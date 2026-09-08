"""Tests for the generator CLI exit contract.

Collaborators are stubbed at their defining modules. No network,
no API key, no real files beyond tmp_path.
"""

from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

import src.synthetic.config as config_mod
import src.synthetic.pipeline as pipeline_mod
from src.synthetic import generator


def run(coro):
    return asyncio.run(coro)


def _fake_config(output_path):
    return SimpleNamespace(
        num_samples=2,
        persona_model="p",
        respondent_model="r",
        concurrency=1,
        output_path=str(output_path),
    )


def test_main_async_success_returns_zero_and_exports(monkeypatch, tmp_path):
    out = tmp_path / "d.jsonl"
    sentinel = [object()]
    seen = {}

    async def fake_run_pipeline(config):
        seen["config"] = config
        return sentinel

    def fake_export_csv(samples, csv_path):
        seen["samples"] = samples
        seen["csv_path"] = csv_path

    monkeypatch.setattr(config_mod, "load_config", lambda argv=None: _fake_config(out))
    monkeypatch.setattr(pipeline_mod, "run_pipeline", fake_run_pipeline)
    monkeypatch.setattr(pipeline_mod, "export_csv", fake_export_csv)

    assert run(generator.main_async()) == 0
    assert seen["samples"] is sentinel
    assert str(seen["csv_path"]) == str(out.with_suffix(".csv"))


def test_main_async_total_failure_returns_one(monkeypatch, tmp_path):
    out = tmp_path / "d.jsonl"
    exported = {"n": 0}

    async def fake_run_pipeline(config):
        return []

    def fake_export_csv(samples, csv_path):
        exported["n"] += 1

    monkeypatch.setattr(config_mod, "load_config", lambda argv=None: _fake_config(out))
    monkeypatch.setattr(pipeline_mod, "run_pipeline", fake_run_pipeline)
    monkeypatch.setattr(pipeline_mod, "export_csv", fake_export_csv)

    assert run(generator.main_async()) == 1
    assert exported["n"] == 0


def test_main_maps_config_error_to_exit_one(monkeypatch):
    def raising_load_config(argv=None):
        raise OSError("OPENCODE_API_KEY is not set.")

    monkeypatch.setattr(config_mod, "load_config", raising_load_config)
    with pytest.raises(SystemExit) as exc_info:
        generator.main()
    assert exc_info.value.code == 1


def test_main_maps_keyboard_interrupt_to_exit_one(monkeypatch, tmp_path):
    async def raising_run_pipeline(config):
        raise KeyboardInterrupt

    monkeypatch.setattr(config_mod, "load_config", lambda argv=None: _fake_config(tmp_path / "d.jsonl"))
    monkeypatch.setattr(pipeline_mod, "run_pipeline", raising_run_pipeline)
    with pytest.raises(SystemExit) as exc_info:
        generator.main()
    assert exc_info.value.code == 1


def test_main_success_exits_zero(monkeypatch, tmp_path):
    async def fake_run_pipeline(config):
        return [object()]

    monkeypatch.setattr(config_mod, "load_config", lambda argv=None: _fake_config(tmp_path / "d.jsonl"))
    monkeypatch.setattr(pipeline_mod, "run_pipeline", fake_run_pipeline)
    monkeypatch.setattr(pipeline_mod, "export_csv", lambda samples, path: None)
    with pytest.raises(SystemExit) as exc_info:
        generator.main()
    assert exc_info.value.code == 0


def test_lazy_reexports_match_package_surface():
    from src.synthetic.questionnaire import QUESTIONNAIRE

    assert generator.QUESTIONNAIRE is QUESTIONNAIRE
    assert len(generator.QUESTIONNAIRE) == len(QUESTIONNAIRE) > 0


def test_facade_surface_matches_package():
    import src.synthetic as pkg

    assert set(generator.__all__) == set(pkg.__all__) | {"main", "main_async"}
    assert generator.FailureCategory is not None
    assert generator.JsonObject is not None
    with pytest.raises(AttributeError):
        generator.no_such_name  # noqa: B018
