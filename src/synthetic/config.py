"""Synthetic generation configuration: CLI flags, environment, defaults.

Precedence (highest first): CLI flag > environment variable > built-in default.
Requires the active provider's key (see ProviderPreset.key_env) in the
environment (or a .env file).
"""

from __future__ import annotations

import argparse
import logging
import math
import os
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from .providers import resolve_provider

# Cost/operational guardrails: typos here bill real money or hammer the API.
MAX_SAMPLES = 100_000
MAX_CONCURRENCY = 64


@dataclass(frozen=True)
class Config:
    """Resolved, validated settings for one generation run."""

    api_key: str
    base_url: str
    persona_model: str
    respondent_model: str
    num_samples: int
    concurrency: int
    temperature: float
    output_path: str
    seed: int | None = None
    resume: bool = True
    max_failure_rate: float = 0.5
    gate_warmup: int = 10
    provider: str = "zen"

    def __post_init__(self) -> None:
        if not self.api_key:
            raise ValueError("api_key must not be empty.")
        if not self.base_url:
            raise ValueError("base_url must not be empty.")
        if not self.persona_model:
            raise ValueError("persona_model must not be empty.")
        if not self.respondent_model:
            raise ValueError("respondent_model must not be empty.")
        if self.num_samples < 1 or self.num_samples > MAX_SAMPLES:
            raise ValueError(f"num_samples must be between 1 and {MAX_SAMPLES}.")
        if self.concurrency < 1 or self.concurrency > MAX_CONCURRENCY:
            raise ValueError(f"concurrency must be between 1 and {MAX_CONCURRENCY}.")
        if not math.isfinite(self.temperature):
            raise ValueError("temperature must be finite.")
        if not self.output_path:
            raise ValueError("output_path must not be empty.")
        if not isinstance(self.provider, str) or not self.provider.strip():
            raise ValueError("provider must be a non-empty string.")
        resolve_provider(self.provider)
        if not 0 <= self.max_failure_rate <= 1:
            raise ValueError("max_failure_rate must be between 0 and 1.")
        if self.gate_warmup < 1:
            raise ValueError("gate_warmup must be at least 1.")


def _cli_or_env[T](
    cli_value: T | None,
    env_name: str,
    parse: Callable[[str], T],
    default: T,
) -> T:
    """Resolve one setting: CLI value, else parsed env var, else default."""
    if cli_value is not None:
        return cli_value
    raw = os.getenv(env_name)
    if raw is None or raw == "":
        return default
    try:
        return parse(raw)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"{env_name} is invalid: {raw!r}") from exc


def _parse_bool(raw: str) -> bool:
    normalized = raw.strip().lower()
    if normalized in ("1", "true", "yes", "on"):
        return True
    if normalized in ("0", "false", "no", "off"):
        return False
    raise ValueError(f"Cannot parse boolean: {raw!r}")


def load_config(argv: Sequence[str] | None = None) -> Config:
    """Load configuration from CLI flags, environment, and defaults.

    `argv` is injectable for tests; pass None to read sys.argv.
    Raises OSError if the provider key env var is missing.
    """
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="Generate the Peta Arah Minat synthetic questionnaire dataset via OpenCode Zen."
    )
    parser.add_argument("--samples", type=int, default=None, help="Number of samples to generate")
    parser.add_argument("--output", type=str, default=None, help="Output JSONL file path")
    parser.add_argument("--concurrency", type=int, default=None, help="Number of parallel requests")
    parser.add_argument("--temperature", type=float, default=None, help="Base LLM sampling temperature")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducible runs")
    parser.add_argument("--resume", action=argparse.BooleanOptionalAction, default=None,
                        help="Resume from existing output rows")
    parser.add_argument("--max-failure-rate", type=float, default=None,
                        help="Abort when failure rate exceeds this (0-1)")
    parser.add_argument("--gate-warmup", type=int, default=None,
                        help="Samples completed before the failure gate arms")
    parser.add_argument("--provider", type=str, default=None,
                        help="LLM provider: zen, gemini, groq, huggingface, tokenrouter")
    args = parser.parse_args(argv)

    preset = resolve_provider(_cli_or_env(args.provider, "PROVIDER", str, "zen"))
    prefix = preset.env_prefix
    api_key = os.getenv(preset.key_env)
    if not api_key:
        raise OSError(
            f"{preset.key_env} is not set. {preset.where_to_get_key} "
            "Copy .env.example to .env and fill it in."
        )

    return Config(
        api_key=api_key,
        base_url=_cli_or_env(
            None, f"{prefix}_BASE_URL", str,
            _cli_or_env(None, "ZEN_BASE_URL", str, preset.base_url),
        ),
        persona_model=_cli_or_env(
            None, f"{prefix}_PERSONA_MODEL", str,
            _cli_or_env(None, "ZEN_MODEL_PERSONA", str, preset.persona_model),
        ),
        respondent_model=_cli_or_env(
            None, f"{prefix}_RESPONDENT_MODEL", str,
            _cli_or_env(None, "ZEN_MODEL_RESPONDENT", str, preset.respondent_model),
        ),
        num_samples=_cli_or_env(args.samples, "NUM_SAMPLES", int, 2000),
        concurrency=_cli_or_env(args.concurrency, "CONCURRENCY", int, 8),
        temperature=_cli_or_env(args.temperature, "TEMPERATURE", float, 1.1),
        output_path=_cli_or_env(args.output, "OUTPUT_PATH", str, "dataset/peta_arah_minat.jsonl"),
        seed=_cli_or_env(args.seed, "SEED", int, None),
        provider=preset.name,
        resume=_cli_or_env(args.resume, "RESUME", _parse_bool, True),
        max_failure_rate=_cli_or_env(args.max_failure_rate, "MAX_FAILURE_RATE", float, 0.5),
        gate_warmup=_cli_or_env(args.gate_warmup, "GATE_WARMUP", int, 10),
    )


def setup_logging() -> None:
    """Configure root logging. Safe to call multiple times.

    Set LOG_FILE to also tee logs to a file (parent dirs auto-created).
    """
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    log_file = os.getenv("LOG_FILE")
    if log_file:
        path = Path(log_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(path, encoding="utf-8"))
    logging.basicConfig(
        level=getattr(logging, level_name, logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S",
        handlers=handlers,
        force=True,
    )
