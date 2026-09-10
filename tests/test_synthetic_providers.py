"""Tests for provider presets and provider-aware config loading."""

from __future__ import annotations

import pytest

import src.synthetic.config as config_mod
from src.synthetic.config import load_config
from src.synthetic.providers import PROVIDER_PRESETS, resolve_provider


def test_known_providers_resolve():
    assert set(PROVIDER_PRESETS) == {"zen", "gemini", "groq", "huggingface", "tokenrouter"}
    assert resolve_provider("Groq").name == "groq"
    assert resolve_provider("  HUGGINGFACE  ").name == "huggingface"


def test_unknown_provider_rejected():
    with pytest.raises(ValueError, match="Unknown provider"):
        resolve_provider("openai")
    with pytest.raises(ValueError, match="Unknown provider"):
        resolve_provider("")


def test_presets_sane():
    for preset in PROVIDER_PRESETS.values():
        assert preset.base_url.startswith("https://")
        assert preset.key_env and preset.persona_model and preset.respondent_model
        assert preset.where_to_get_key
        assert preset.env_prefix and "_" not in preset.env_prefix
        assert preset.key_env.startswith(preset.env_prefix)


def test_provider_wiring(monkeypatch):
    for var in ("PROVIDER", "ZEN_BASE_URL", "ZEN_MODEL_PERSONA", "ZEN_MODEL_RESPONDENT",
                "GEMINI_API_KEY", "GROQ_API_KEY", "HF_TOKEN", "OPENCODE_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setattr(config_mod, "load_dotenv", lambda *args, **kwargs: False)

    monkeypatch.setenv("GROQ_API_KEY", "gsk-test")
    monkeypatch.setenv("PROVIDER", "groq")
    config = load_config([])
    assert config.provider == "groq"
    assert config.base_url == "https://api.groq.com/openai/v1"
    assert config.api_key == "gsk-test"

    # Explicit model env beats preset defaults.
    monkeypatch.setenv("ZEN_MODEL_PERSONA", "custom-model")
    assert load_config([]).persona_model == "custom-model"

    # Wrong key env for the provider is a clear error.
    monkeypatch.delenv("GROQ_API_KEY")
    with pytest.raises(OSError, match="GROQ_API_KEY"):
        load_config([])

    # Unknown provider is a clear error.
    monkeypatch.setenv("PROVIDER", "openai")
    with pytest.raises(ValueError, match="Unknown provider"):
        load_config([])


def test_provider_specific_env_beats_generic(monkeypatch):
    for var in ("PROVIDER", "ZEN_BASE_URL", "ZEN_MODEL_PERSONA", "ZEN_MODEL_RESPONDENT",
                "TOKENROUTER_BASE_URL", "TOKENROUTER_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setattr(config_mod, "load_dotenv", lambda *args, **kwargs: False)

    monkeypatch.setenv("TOKENROUTER_API_KEY", "tr-test")
    monkeypatch.setenv("PROVIDER", "tokenrouter")
    monkeypatch.setenv("ZEN_BASE_URL", "https://generic.example/v1")
    monkeypatch.setenv("TOKENROUTER_BASE_URL", "https://specific.example/v1")
    config = load_config([])
    assert config.base_url == "https://specific.example/v1"
    assert config.persona_model == "z-ai/glm-5.3-free"
