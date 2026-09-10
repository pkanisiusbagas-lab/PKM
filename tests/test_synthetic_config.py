"""Tests for synthetic generation config loading.

load_config takes argv directly, so no sys.argv patching is needed.
Environment is fully isolated per test via the clean_env fixture.
"""

from __future__ import annotations

import logging

import pytest

import src.synthetic.config as config_mod
from src.synthetic.config import (
    MAX_CONCURRENCY,
    MAX_SAMPLES,
    Config,
    load_config,
    setup_logging,
)

_MANAGED_VARS = (
    "OPENCODE_API_KEY",
    "ZEN_BASE_URL",
    "ZEN_MODEL_PERSONA",
    "ZEN_MODEL_RESPONDENT",
    "NUM_SAMPLES",
    "CONCURRENCY",
    "TEMPERATURE",
    "OUTPUT_PATH",
    "LOG_LEVEL",
    "RESUME",
    "MAX_FAILURE_RATE",
    "GATE_WARMUP",
    "LOG_FILE",
    "PROVIDER",
)


@pytest.fixture
def clean_env(monkeypatch):
    for var in _MANAGED_VARS:
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("OPENCODE_API_KEY", "test-key")
    # Neutralize dotenv: a real .env on disk must not leak into tests.
    monkeypatch.setattr(config_mod, "load_dotenv", lambda *args, **kwargs: False)
    return monkeypatch


def _valid_kwargs(**overrides):
    kwargs = {
        "api_key": "k",
        "base_url": "http://x",
        "persona_model": "p",
        "respondent_model": "r",
        "num_samples": 10,
        "concurrency": 2,
        "temperature": 1.0,
        "output_path": "out.jsonl",
    }
    kwargs.update(overrides)
    return kwargs


def test_config_rejects_bad_values():
    for kwargs in (
        _valid_kwargs(num_samples=0),
        _valid_kwargs(num_samples=-5),
        _valid_kwargs(num_samples=MAX_SAMPLES + 1),
        _valid_kwargs(concurrency=0),
        _valid_kwargs(concurrency=MAX_CONCURRENCY + 1),
        _valid_kwargs(temperature=float("nan")),
        _valid_kwargs(temperature=float("inf")),
        _valid_kwargs(output_path=""),
        _valid_kwargs(api_key=""),
        _valid_kwargs(persona_model=""),
    ):
        with pytest.raises(ValueError):
            Config(**kwargs)


def test_load_config_defaults(clean_env):
    config = load_config([])
    assert config.num_samples == 2000
    assert config.concurrency == 8
    assert config.temperature == 1.1
    assert config.output_path == "dataset/peta_arah_minat.jsonl"
    assert config.base_url == "https://opencode.ai/zen/v1"


def test_cli_beats_env(clean_env):
    clean_env.setenv("NUM_SAMPLES", "5")
    config = load_config(["--samples", "10"])
    assert config.num_samples == 10


def test_env_beats_default(clean_env):
    clean_env.setenv("NUM_SAMPLES", "5")
    assert load_config([]).num_samples == 5


def test_falsy_cli_values_are_respected(clean_env):
    # Regression: `args.x or default` used to swallow 0 / 0.0.
    assert load_config(["--temperature", "0"]).temperature == 0.0


def test_invalid_env_names_the_variable(clean_env):
    clean_env.setenv("NUM_SAMPLES", "abc")
    with pytest.raises(ValueError, match="NUM_SAMPLES"):
        load_config([])


def test_empty_env_falls_back_to_default(clean_env):
    clean_env.setenv("NUM_SAMPLES", "")
    assert load_config([]).num_samples == 2000


def test_invalid_temperature_names_the_variable(clean_env):
    clean_env.setenv("TEMPERATURE", "panas")
    with pytest.raises(ValueError, match="TEMPERATURE"):
        load_config([])


def test_missing_api_key_raises(clean_env, monkeypatch):
    monkeypatch.delenv("OPENCODE_API_KEY")
    with pytest.raises(OSError, match="OPENCODE_API_KEY"):
        load_config([])


def test_setup_logging_is_repeatable():
    setup_logging()
    setup_logging()


def test_setup_logging_writes_file(clean_env, tmp_path):
    log_file = tmp_path / "nested" / "run.log"
    clean_env.setenv("LOG_FILE", str(log_file))
    setup_logging()
    logging.getLogger("test-log-file").warning("hello-file")
    for handler in logging.root.handlers:
        handler.flush()
    assert "hello-file" in log_file.read_text(encoding="utf-8")


def test_setup_logging_without_file(clean_env):
    setup_logging()
    assert not any(isinstance(h, logging.FileHandler) for h in logging.root.handlers)


def test_seed_defaults_to_none(clean_env):
    assert load_config([]).seed is None

def test_seed_from_cli_and_env(clean_env):
    assert load_config(["--seed", "7"]).seed == 7
    clean_env.setenv("SEED", "9")
    assert load_config([]).seed == 9


def test_run_knob_defaults(clean_env):
    config = load_config([])
    assert config.resume is True
    assert config.max_failure_rate == 0.5
    assert config.gate_warmup == 10


def test_run_knobs_from_cli(clean_env):
    config = load_config(["--no-resume", "--max-failure-rate", "0.2", "--gate-warmup", "5"])
    assert config.resume is False
    assert config.max_failure_rate == 0.2
    assert config.gate_warmup == 5


def test_run_knobs_from_env(clean_env):
    clean_env.setenv("RESUME", "false")
    clean_env.setenv("MAX_FAILURE_RATE", "0.2")
    clean_env.setenv("GATE_WARMUP", "5")
    config = load_config([])
    assert config.resume is False
    assert config.max_failure_rate == 0.2
    assert config.gate_warmup == 5


def test_invalid_run_knobs_rejected(clean_env):
    clean_env.setenv("RESUME", "maybe")
    with pytest.raises(ValueError, match="RESUME"):
        load_config([])
    with pytest.raises(ValueError):
        load_config(["--max-failure-rate", "2"])
    with pytest.raises(ValueError):
        load_config(["--gate-warmup", "0"])
