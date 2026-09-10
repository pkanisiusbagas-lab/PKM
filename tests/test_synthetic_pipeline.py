"""Tests for the synthetic generation pipeline.

Network is stubbed at module seams: pure helpers run directly,
generate_one_sample is monkeypatched for retry/run tests, and
run_pipeline uses a real (non-connecting) ZenClient.
"""

from __future__ import annotations

import asyncio
import json
import random

import pytest

import src.synthetic.pipeline as pipeline_mod
from src.synthetic.config import Config
from src.synthetic.errors import FailureBudgetExceededError, RetryExhaustedError
from src.synthetic.pipeline import (
    build_persona_record,
    export_csv,
    generate_one_sample_with_retry,
    run_pipeline,
)
from src.synthetic.pools import build_stratified_leanings
from src.synthetic.response import SurveyResponse


def run(coro):
    return asyncio.run(coro)


def _config(output_path, **overrides):
    kwargs = {
        "api_key": "k",
        "base_url": "http://localhost",
        "persona_model": "p",
        "respondent_model": "r",
        "num_samples": 3,
        "concurrency": 2,
        "temperature": 1.0,
        "output_path": str(output_path),
    }
    kwargs.update(overrides)
    return Config(**kwargs)


def _response(idx):
    return SurveyResponse(
        respondent_id=f"R{idx:05d}-abc123",
        kecenderungan_dominan="X",
        kecenderungan_sekunder="Y",
        sifat_kepribadian="rajin",
        level_keyakinan_persona="yakin",
        kota_asal="Jakarta",
        profil_singkat="test",
        answers={"q1": "A", "q10": 7},
        generated_at="2026-01-01T00:00:00+00:00",
    )


def test_build_persona_record_merges_fragment():
    record = build_persona_record(
        leaning="Tekno",
        personality="rajin",
        confidence="yakin",
        city="Bandung",
        persona_raw={
            "kecenderungan_sekunder": "Sains",
            "sifat_tambahan": "teliti",
            "profil_singkat": "halo",
        },
    )
    assert record == {
        "kecenderungan_dominan": "Tekno",
        "kecenderungan_sekunder": "Sains",
        "sifat_kepribadian": "rajin, teliti",
        "level_keyakinan": "yakin",
        "kota_asal": "Bandung",
        "profil_singkat": "halo",
    }


def test_build_persona_record_defaults():
    record = build_persona_record(
        leaning="X", personality="rajin", confidence="c", city="K", persona_raw={}
    )
    assert record["kecenderungan_sekunder"] == "Tidak spesifik"
    assert record["sifat_kepribadian"] == "rajin"
    assert record["profil_singkat"] == ""


def test_with_retry_succeeds_after_failures(monkeypatch):
    calls = {"n": 0}

    async def flaky(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] < 3:
            raise ValueError("boom")
        return _response(1)

    monkeypatch.setattr(pipeline_mod, "generate_one_sample", flaky)
    result = run(generate_one_sample_with_retry(None, 1, "X", "p", "r", 1.0))
    assert result.respondent_id == "R00001-abc123"
    assert calls["n"] == 3


def test_with_retry_gives_up(monkeypatch):
    calls = {"n": 0}

    async def always_fails(*args, **kwargs):
        calls["n"] += 1
        raise ValueError("boom")

    monkeypatch.setattr(pipeline_mod, "generate_one_sample", always_fails)
    assert run(generate_one_sample_with_retry(None, 1, "X", "p", "r", 1.0)) is None
    assert calls["n"] == 3


def test_with_retry_skips_exhausted_without_retry(monkeypatch):
    calls = {"n": 0}

    async def exhausted(*args, **kwargs):
        calls["n"] += 1
        raise RetryExhaustedError("m", 5)

    monkeypatch.setattr(pipeline_mod, "generate_one_sample", exhausted)
    assert run(generate_one_sample_with_retry(None, 1, "X", "p", "r", 1.0)) is None
    assert calls["n"] == 1


def test_export_csv_round_trip(tmp_path):
    path = tmp_path / "out.csv"
    export_csv([_response(1), _response(2)], path)
    with path.open(encoding="utf-8") as f:
        rows = list(f.read().splitlines())
    assert len(rows) == 3  # header + 2 rows.
    assert rows[0].startswith("respondent_id,")


def test_export_csv_empty_is_noop(tmp_path):
    path = tmp_path / "out.csv"
    export_csv([], path)
    assert not path.exists()


def test_stratified_leanings_deterministic_with_seed():
    first = build_stratified_leanings(16, rng=random.Random(7))
    second = build_stratified_leanings(16, rng=random.Random(7))
    assert first == second


def test_run_pipeline_resumes_existing_rows(monkeypatch, tmp_path):
    out = tmp_path / "d.jsonl"
    out.write_text(json.dumps({"respondent_id": "old"}) + "\n", encoding="utf-8")
    calls = {"n": 0}

    async def fake_with_retry(client, idx, leaning, *args, **kwargs):
        calls["n"] += 1
        return _response(idx)

    monkeypatch.setattr(pipeline_mod, "generate_one_sample_with_retry", fake_with_retry)
    results = run(run_pipeline(_config(out, seed=7, gate_warmup=100)))
    assert calls["n"] == 2  # 1 pre-existing row skipped.
    assert [r.respondent_id for r in results] == ["R00002-abc123", "R00003-abc123"]
    assert len(out.read_text(encoding="utf-8").splitlines()) == 3


def test_resume_ignores_blank_lines(monkeypatch, tmp_path):
    out = tmp_path / "d.jsonl"
    out.write_text(json.dumps({"respondent_id": "old"}) + "\n\n", encoding="utf-8")
    calls = {"n": 0}

    async def fake_with_retry(client, idx, leaning, *args, **kwargs):
        calls["n"] += 1
        return _response(idx)

    monkeypatch.setattr(pipeline_mod, "generate_one_sample_with_retry", fake_with_retry)
    results = run(run_pipeline(_config(out, seed=7, gate_warmup=100)))
    assert calls["n"] == 2  # trailing blank line is not a completed row.
    assert len(results) == 2


def test_run_pipeline_failure_gate_aborts(monkeypatch, tmp_path):
    out = tmp_path / "d.jsonl"

    async def fake_with_retry(client, idx, leaning, *args, **kwargs):
        return None

    monkeypatch.setattr(pipeline_mod, "generate_one_sample_with_retry", fake_with_retry)
    with pytest.raises(FailureBudgetExceededError) as exc_info:
        run(run_pipeline(_config(out, num_samples=5, max_failure_rate=0.4, gate_warmup=2)))
    assert exc_info.value.failures == 2
    assert exc_info.value.completed == 2


def test_resume_without_seed_refuses(monkeypatch, tmp_path):
    out = tmp_path / "d.jsonl"
    out.write_text(json.dumps({"respondent_id": "old"}) + "\n", encoding="utf-8")

    async def fake_with_retry(client, idx, leaning, *args, **kwargs):
        return _response(idx)

    monkeypatch.setattr(pipeline_mod, "generate_one_sample_with_retry", fake_with_retry)
    with pytest.raises(ValueError, match="seed"):
        run(run_pipeline(_config(out, num_samples=3)))


def test_export_csv_neutralizes_formula_injection(tmp_path):
    import csv as csv_mod

    path = tmp_path / "out.csv"
    export_csv([_response(1)], path)
    with path.open(encoding="utf-8") as f:
        rows = list(csv_mod.DictReader(f))
    assert rows[0]["respondent_id"] == "R00001-abc123"

    evil = _response(1)
    import dataclasses

    evil = dataclasses.replace(evil, profil_singkat="=HYPERLINK(1)")
    export_csv([evil], path)
    with path.open(encoding="utf-8") as f:
        rows = list(csv_mod.DictReader(f))
    assert rows[0]["profil_singkat"] == "'=HYPERLINK(1)"
