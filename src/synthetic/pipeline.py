"""Batch generation pipeline: stratify → fan out → stream → export.

Retry budget (worst case per sample): up to `max_attempts` outer tries of
`generate_one_sample`, each performing 2 chat calls of up to 5 inner
attempts. `RetryExhaustedError` short-circuits the outer retry since its
inner budget is already spent.
"""

from __future__ import annotations

import asyncio
import csv
import json
import logging
import random
import uuid
from datetime import UTC, datetime
from pathlib import Path

from tqdm import tqdm

from .client import ZenClient, ZenClientConfig
from .config import Config
from .errors import FailureBudgetExceededError, RetryExhaustedError
from .pools import (
    CONFIDENCE_LEVELS,
    INDONESIAN_CITIES,
    PERSONALITY_TRAITS,
    build_stratified_leanings,
)
from .prompts import build_persona_prompt, build_respondent_prompt
from .response import SurveyResponse
from .types import JsonObject, PersonaRecord
from .validation import validate_answers

logger = logging.getLogger("peta_arah_minat")

# Cell prefixes that turn CSV text into live spreadsheet formulas.
_CSV_UNSAFE_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def _sanitize_csv_value(value: str | int) -> str | int:
    """Neutralize spreadsheet formula injection in free-text fields."""
    if isinstance(value, str) and value.startswith(_CSV_UNSAFE_PREFIXES):
        return f"'{value}"
    return value


def build_persona_record(
    *,
    leaning: str,
    personality: str,
    confidence: str,
    city: str,
    persona_raw: JsonObject,
) -> PersonaRecord:
    """Merge an LLM persona fragment with sampled traits. Pure, no I/O."""
    extra = persona_raw.get("sifat_tambahan", "")
    traits = f"{personality}, {extra}".strip(", ") if extra else personality
    return {
        "kecenderungan_dominan": leaning,
        "kecenderungan_sekunder": str(
            persona_raw.get("kecenderungan_sekunder", "Tidak spesifik")
        ),
        "sifat_kepribadian": traits,
        "level_keyakinan": confidence,
        "kota_asal": city,
        "profil_singkat": str(persona_raw.get("profil_singkat", "")),
    }


async def generate_one_sample(
    client: ZenClient,
    index: int,
    leaning: str,
    persona_model: str,
    respondent_model: str,
    base_temperature: float,
    rng: random.Random | None = None,
) -> SurveyResponse:
    """Generate one survey response via persona + respondent agent calls."""
    r = rng if rng is not None else random
    personality = r.choice(PERSONALITY_TRAITS)
    confidence = r.choice(CONFIDENCE_LEVELS)
    city = r.choice(INDONESIAN_CITIES)
    seed = r.randint(100_000, 999_999)
    temperature = max(0.1, min(2.0, base_temperature + r.uniform(-0.15, 0.15)))

    persona_raw = await client.chat_json(
        model=persona_model,
        messages=build_persona_prompt(leaning, personality, confidence, city, seed),
        temperature=temperature,
    )
    persona = build_persona_record(
        leaning=leaning,
        personality=personality,
        confidence=confidence,
        city=city,
        persona_raw=persona_raw,
    )

    answers_raw = await client.chat_json(
        model=respondent_model,
        messages=build_respondent_prompt(persona),
        temperature=temperature,
    )
    answers = validate_answers(answers_raw)

    return SurveyResponse(
        respondent_id=f"R{index:05d}-{uuid.uuid4().hex[:6]}",
        kecenderungan_dominan=leaning,
        kecenderungan_sekunder=persona["kecenderungan_sekunder"],
        sifat_kepribadian=persona["sifat_kepribadian"],
        level_keyakinan_persona=confidence,
        kota_asal=city,
        profil_singkat=persona["profil_singkat"],
        answers=answers,
        generated_at=datetime.now(UTC).isoformat(),
    )


async def generate_one_sample_with_retry(
    client: ZenClient,
    index: int,
    leaning: str,
    persona_model: str,
    respondent_model: str,
    base_temperature: float,
    max_attempts: int = 3,
    rng: random.Random | None = None,
) -> SurveyResponse | None:
    """Try a sample up to max_attempts; return None if it keeps failing.

    Never re-retries RetryExhaustedError: its inner budget is already spent.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            return await generate_one_sample(
                client, index, leaning, persona_model, respondent_model, base_temperature, rng
            )
        except RetryExhaustedError:
            logger.warning("Sample #%d hit the exhausted retry budget; skipping.", index)
            return None
        except Exception as exc:  # noqa: BLE001 — sample boundary must not crash the run
            logger.warning("Sample #%d failed (attempt %d/%d): %s", index, attempt, max_attempts, exc)
    logger.error("Sample #%d failed permanently after %d attempts", index, max_attempts)
    return None


def export_csv(samples: list[SurveyResponse], csv_path: Path) -> None:
    """Write samples to CSV. No-op with a warning when empty."""
    if not samples:
        logger.warning("No data to export to CSV.")
        return
    fieldnames = list(samples[0].to_flat_dict().keys())
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for sample in samples:
            writer.writerow(
                {k: _sanitize_csv_value(v) for k, v in sample.to_flat_dict().items()}
            )


def _count_jsonl_lines(path: Path) -> int:
    with path.open("r", encoding="utf-8") as f:
        return sum(1 for _ in f)


async def run_pipeline(config: Config) -> list[SurveyResponse]:
    """Run the full generation batch, streaming JSONL rows as they complete.

    Resume: with config.resume, existing output rows are kept and only the
    remainder is generated (requires config.seed for exact order).
    Failure gate: raises FailureBudgetExceededError once `gate_warmup`
    samples completed and the failure rate exceeds `max_failure_rate`.
    """
    output_path = Path(config.output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    existing = _count_jsonl_lines(output_path) if config.resume and output_path.exists() else 0
    remaining = config.num_samples - min(existing, config.num_samples)
    if existing and remaining > 0 and config.seed is None:
        raise ValueError(
            f"Cannot resume '{output_path}' ({existing} rows) without config.seed: "
            "leaning order would be non-deterministic. Set --seed or re-run with resume=False."
        )
    completed_before = config.num_samples - remaining

    rng = random.Random(config.seed) if config.seed is not None else random.Random()
    leanings = build_stratified_leanings(config.num_samples, rng=rng)[completed_before:]

    client_config = ZenClientConfig(api_key=config.api_key, base_url=config.base_url)
    async with ZenClient(client_config) as client:
        semaphore = asyncio.Semaphore(config.concurrency)
        results: list[SurveyResponse] = []
        failures = 0

        async def worker(idx: int, leaning: str) -> SurveyResponse | None:
            async with semaphore:
                return await generate_one_sample_with_retry(
                    client, idx, leaning, config.persona_model,
                    config.respondent_model, config.temperature, rng=rng,
                )

        tasks = [
            asyncio.create_task(worker(i, leaning))
            for i, leaning in enumerate(leanings, start=completed_before + 1)
        ]

        with output_path.open(  # noqa: ASYNC230 -- streaming JSONL writes; async file IO deferred.
            "a" if completed_before else "w", encoding="utf-8"
        ) as f, tqdm(
            total=config.num_samples, initial=completed_before, desc="Generating", unit="sampel"
        ) as pbar:
            for coro in asyncio.as_completed(tasks):
                sample = await coro
                if sample is not None:
                    results.append(sample)
                    f.write(json.dumps(sample.to_flat_dict(), ensure_ascii=False) + "\n")
                    f.flush()
                else:
                    failures += 1
                pbar.update(1)

                completed = completed_before + len(results) + failures
                if (
                    completed >= config.gate_warmup
                    and failures / completed > config.max_failure_rate
                ):
                    for task in tasks:
                        task.cancel()
                    await asyncio.gather(*tasks, return_exceptions=True)
                    raise FailureBudgetExceededError(
                        failures / completed, config.max_failure_rate, failures, completed
                    )

        logger.info("Done. Succeeded: %d | Failed: %d", len(results), failures)
        return results
