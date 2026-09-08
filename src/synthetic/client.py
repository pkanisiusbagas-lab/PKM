"""Async LLM chat client with explicit, testable retry policy.

Retry semantics:
- `max_attempts` is the total number of attempts, including the first.
- Transient API errors (connection/timeout, 408/409/429, 5xx) and
  malformed model responses are retried.
- Permanent client errors (400/401/403/404/422, ...) propagate immediately.
- No sleep happens after the final attempt.
"""

from __future__ import annotations

import asyncio
import logging
import math
import random
import uuid
from dataclasses import dataclass, field
from types import TracebackType
from typing import Self

from openai import (
    APIConnectionError,
    APIError,
    APIStatusError,
    AsyncOpenAI,
    RateLimitError,
)

from .errors import (
    EmptyResponseError,
    LLMResponseError,
    RetryExhaustedError,
)
from .types import FailureCategory, JsonObject, MessageSequence, SleepFn
from .validation import _extract_json

logger = logging.getLogger(__name__)

_SDK_MAX_RETRIES = 0  # Custom RetryPolicy owns retries; SDK-level retries disabled.

_RETRYABLE_STATUS_CODES: frozenset[int] = frozenset({408, 409, 429, 500, 502, 503, 504})

_MAX_ERROR_PREVIEW_CHARS = 200


@dataclass(frozen=True)
class RetryPolicy:
    """Centralized retry tuning."""

    max_attempts: int = 5
    backoff_base: float = 2.0
    backoff_cap_seconds: float = 30.0
    jitter_seconds: float = 1.0
    invalid_response_delay_seconds: float = 1.0

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1.")
        if self.backoff_base <= 0:
            raise ValueError("backoff_base must be positive.")
        if self.backoff_cap_seconds < 0:
            raise ValueError("backoff_cap_seconds must not be negative.")
        if self.jitter_seconds < 0:
            raise ValueError("jitter_seconds must not be negative.")
        if self.invalid_response_delay_seconds < 0:
            raise ValueError("invalid_response_delay_seconds must not be negative.")

    def delay_for(self, *, attempt: int, jitter_seconds: float) -> float:
        """Deterministic backoff delay for the Nth attempt."""
        if attempt < 1:
            raise ValueError("attempt must be at least 1.")
        if jitter_seconds < 0:
            raise ValueError("jitter_seconds must not be negative.")
        grown = self.backoff_base**attempt
        return min(grown, self.backoff_cap_seconds) + jitter_seconds


@dataclass(frozen=True)
class ZenClientConfig:
    """Immutable configuration for ZenClient."""

    api_key: str
    base_url: str
    timeout_seconds: float = 60.0
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    max_tokens: int | None = 1024
    session_id: str | None = None

    def __post_init__(self) -> None:
        if not self.api_key:
            raise ValueError("api_key must not be empty.")
        if not self.base_url:
            raise ValueError("base_url must not be empty.")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive.")
        if self.max_tokens is not None and self.max_tokens < 1:
            raise ValueError("max_tokens must be positive.")


def is_retryable_error(exc: BaseException) -> bool:
    """Return True only for transient errors."""
    if isinstance(exc, APIStatusError):
        return exc.status_code in _RETRYABLE_STATUS_CODES
    return isinstance(exc, APIConnectionError)


def _failure_category(exc: APIError) -> FailureCategory:
    if isinstance(exc, RateLimitError):
        return "rate_limit"
    if isinstance(exc, APIConnectionError):
        return "connection"
    if isinstance(exc, APIStatusError):
        return "server" if exc.status_code >= 500 else "client"
    return "unknown"


def _extract_message_content(response: object) -> str:
    choices = getattr(response, "choices", None)
    if not choices:
        raise EmptyResponseError("Model returned a response without choices.")
    message = getattr(choices[0], "message", None)
    content = getattr(message, "content", None)
    if not isinstance(content, str) or not content:
        raise EmptyResponseError("Model returned empty content.")
    return content


class ZenClient:
    """Async chat client for OpenAI-compatible endpoints.

    Use as `async with ZenClient(config) as client:` so the connection
    is always closed. `close()` is idempotent.
    """

    def __init__(
        self,
        config: ZenClientConfig,
        *,
        sleep: SleepFn = asyncio.sleep,
        rng: random.Random | None = None,
    ) -> None:
        self._policy = config.retry_policy
        self._max_tokens = config.max_tokens
        self._sleep = sleep
        self._rng = rng if rng is not None else random.Random()
        # Free-tier gateway recognizes calls by session; one stable id per
        # client keeps all retries of a run on the same identity.
        self.session_id = config.session_id or f"ses_{uuid.uuid4().hex[:16]}"
        self._client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
            max_retries=_SDK_MAX_RETRIES,
            timeout=config.timeout_seconds,
            default_headers={"x-opencode-session": self.session_id},
        )
        self._closed = False

    async def chat_json(
        self,
        *,
        model: str,
        messages: MessageSequence,
        temperature: float,
        max_attempts: int | None = None,
    ) -> JsonObject:
        """Send one chat request and return the parsed JSON object.

        Retries transient errors and malformed responses up to
        `max_attempts`. Raises RetryExhaustedError when all attempts fail.
        `messages` must be a Sequence (list/tuple), not a one-shot iterator.
        """
        if not model:
            raise ValueError("model must be a non-empty string.")
        if len(messages) == 0:
            raise ValueError("messages must not be empty.")
        if any(not m.get("role") or not m.get("content") for m in messages):
            raise ValueError("Every message must have non-empty 'role' and 'content'.")
        if not math.isfinite(temperature):
            raise ValueError("temperature must be finite.")

        attempts = max_attempts if max_attempts is not None else self._policy.max_attempts
        if attempts < 1:
            raise ValueError("max_attempts must be at least 1.")

        last_error: Exception | None = None
        delay = 0.0
        category: FailureCategory = "invalid_response"

        for attempt in range(1, attempts + 1):
            try:
                content = await self._request_content(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                )
                return _extract_json(content)
            except LLMResponseError as exc:
                last_error = exc
                delay = self._policy.invalid_response_delay_seconds
                category = "invalid_response"
            except APIError as exc:
                retry_plan = self._retry_plan(exc, attempt)
                if retry_plan is None:
                    raise
                last_error = exc
                delay, category = retry_plan

            if attempt >= attempts:
                break

            logger.warning(
                "chat_json retry attempt=%d/%d model=%s category=%s delay=%.1fs err=%s: %s",
                attempt,
                attempts,
                model,
                category,
                delay,
                type(last_error).__name__,
                str(last_error)[:_MAX_ERROR_PREVIEW_CHARS],
            )
            await self._sleep(delay)

        assert last_error is not None  # Guaranteed: the loop runs at least once.
        raise RetryExhaustedError(model, attempts) from last_error

    async def close(self) -> None:
        """Close the connection. Safe to call multiple times."""
        if self._closed:
            return
        self._closed = True
        await self._client.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.close()

    async def _request_content(
        self,
        *,
        model: str,
        messages: MessageSequence,
        temperature: float,
    ) -> str:
        response = await self._client.chat.completions.create(
            model=model,
            messages=list(messages),
            temperature=temperature,
            max_tokens=self._max_tokens,
        )
        return _extract_message_content(response)

    def _retry_plan(
        self, exc: APIError, attempt: int
    ) -> tuple[float, FailureCategory] | None:
        """Return (delay, category) for retryable errors, None for permanent ones."""
        if not is_retryable_error(exc):
            return None
        return self._sample_backoff(attempt), _failure_category(exc)

    def _sample_backoff(self, attempt: int) -> float:
        jitter = self._rng.uniform(0, self._policy.jitter_seconds)
        return self._policy.delay_for(attempt=attempt, jitter_seconds=jitter)
