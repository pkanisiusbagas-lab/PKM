"""Provider presets: base URLs, key env vars, and default models.

The client layer stays provider-agnostic (any OpenAI-compatible endpoint);
this module only maps names to connection defaults. No logic, no I/O.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class ProviderPreset:
    """Connection defaults for one LLM provider."""

    name: str
    base_url: str
    key_env: str
    persona_model: str
    respondent_model: str
    where_to_get_key: str

    @property
    def env_prefix(self) -> str:
        """Derive the override prefix: TOKENROUTER_API_KEY -> TOKENROUTER."""
        return self.key_env.removesuffix("_API_KEY").removesuffix("_TOKEN")


PROVIDER_PRESETS: Final[dict[str, ProviderPreset]] = {
    "zen": ProviderPreset(
        name="zen",
        base_url="https://opencode.ai/zen/v1",
        key_env="OPENCODE_API_KEY",
        persona_model="big-pickle",
        respondent_model="big-pickle",
        where_to_get_key="OpenCode Zen dashboard (/connect in the TUI).",
    ),
    "gemini": ProviderPreset(
        name="gemini",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        key_env="GEMINI_API_KEY",
        persona_model="gemini-2.0-flash",
        respondent_model="gemini-2.0-flash",
        where_to_get_key="Google AI Studio, free tier available.",
    ),
    "groq": ProviderPreset(
        name="groq",
        base_url="https://api.groq.com/openai/v1",
        key_env="GROQ_API_KEY",
        persona_model="openai/gpt-oss-20b",
        respondent_model="openai/gpt-oss-20b",
        where_to_get_key="GroqCloud console, free tier 30 RPM.",
    ),
    "huggingface": ProviderPreset(
        name="huggingface",
        base_url="https://router.huggingface.co/v1",
        key_env="HF_TOKEN",
        persona_model="openai/gpt-oss-20b:fastest",
        respondent_model="openai/gpt-oss-20b:fastest",
        where_to_get_key="Hugging Face settings, token with Inference Providers permission.",
    ),
    "tokenrouter": ProviderPreset(
        name="tokenrouter",
        base_url="https://api.tokenrouter.com/v1",
        key_env="TOKENROUTER_API_KEY",
        persona_model="z-ai/glm-5.3-free",
        respondent_model="z-ai/glm-5.3-free",
        where_to_get_key="TokenRouter console (tokenrouter.com/console/token).",
    ),
}


def resolve_provider(name: str) -> ProviderPreset:
    """Return the preset for name (case-insensitive). Raises ValueError."""
    key = name.strip().lower()
    try:
        return PROVIDER_PRESETS[key]
    except KeyError:
        known = ", ".join(sorted(PROVIDER_PRESETS))
        raise ValueError(f"Unknown provider {name!r}; expected one of: {known}.") from None
