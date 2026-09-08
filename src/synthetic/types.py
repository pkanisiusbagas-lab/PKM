"""Shared type aliases for the synthetic pipeline.

Static contracts only — no runtime validation; enforcement lives in validation.py.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence
from typing import Literal, TypedDict


class ChatMessage(TypedDict):
    """One chat message: role + content, matching the OpenAI-compatible format."""

    role: Literal["system", "user", "assistant", "tool"]
    content: str


class PersonaRecord(TypedDict):
    """Merged persona: sampled traits plus the LLM persona fragment."""

    kecenderungan_dominan: str
    kecenderungan_sekunder: str
    sifat_kepribadian: str
    level_keyakinan: str
    kota_asal: str
    profil_singkat: str


type JsonValue = str | int | float | bool | None | list[JsonValue] | dict[str, JsonValue]
type JsonObject = dict[str, JsonValue]

type MessageSequence = Sequence[ChatMessage]

type SleepFn = Callable[[float], Awaitable[None]]

type FailureCategory = Literal[
    "rate_limit", "connection", "server", "client", "unknown", "invalid_response"
]
