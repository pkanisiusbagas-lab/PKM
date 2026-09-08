"""Unit tests for ZenClient retry behavior and backoff calculation.

No network, no API key, no sleeping: the SDK transport is stubbed and
a SleepRecorder stands in for asyncio.sleep.
"""

from __future__ import annotations

import asyncio
import random
from types import SimpleNamespace

import httpx
import pytest
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    InternalServerError,
    RateLimitError,
)

from src.synthetic.client import (
    RetryPolicy,
    ZenClient,
    ZenClientConfig,
    _extract_message_content,
    is_retryable_error,
)
from src.synthetic.errors import (
    EmptyResponseError,
    MalformedResponseError,
    RetryExhaustedError,
)


def run(coro):
    return asyncio.run(coro)


def _request():
    return httpx.Request("POST", "http://localhost/v1/chat/completions")


def _status_error(cls, status_code):
    return cls(
        "boom",
        response=httpx.Response(status_code, request=_request()),
        body={},
    )


class SleepRecorder:
    """Stand-in for asyncio.sleep that records delays instead of waiting."""

    def __init__(self):
        self.delays: list[float] = []

    async def __call__(self, delay: float) -> None:
        self.delays.append(delay)


def make_client(sleep, *, attempts=3, seed=0):
    policy = RetryPolicy(max_attempts=attempts)
    config = ZenClientConfig(
        api_key="test-key", base_url="http://localhost", retry_policy=policy
    )
    return ZenClient(config, sleep=sleep, rng=random.Random(seed))


def stub_request_content(client, script):
    """Replace _request_content with a scripted sequence.

    Each item is either a string to return or an exception to raise.
    Returns the call counter dict.
    """
    calls = {"n": 0}
    items = list(script)

    async def fake(*, model, messages, temperature):
        calls["n"] += 1
        item = items.pop(0) if items else items[-1]
        if isinstance(item, Exception):
            raise item
        return item

    client._request_content = fake
    return calls


# --- backoff: pure calculation, no client needed ---


def test_backoff_grows_then_caps():
    policy = RetryPolicy(backoff_base=2.0, backoff_cap_seconds=30.0)
    delays = [policy.delay_for(attempt=n, jitter_seconds=0.0) for n in range(1, 7)]
    assert delays == [2.0, 4.0, 8.0, 16.0, 30.0, 30.0]


def test_backoff_never_negative():
    policy = RetryPolicy()
    assert policy.delay_for(attempt=1, jitter_seconds=0.0) >= 0


def test_backoff_rejects_bad_attempt():
    with pytest.raises(ValueError):
        RetryPolicy().delay_for(attempt=0, jitter_seconds=0.0)


def test_policy_rejects_bad_config():
    with pytest.raises(ValueError):
        RetryPolicy(max_attempts=0)
    with pytest.raises(ValueError):
        RetryPolicy(jitter_seconds=-1.0)
    with pytest.raises(ValueError):
        ZenClientConfig(api_key="", base_url="http://x")
    with pytest.raises(ValueError):
        ZenClientConfig(api_key="k", base_url="http://x", timeout_seconds=0)
    with pytest.raises(ValueError):
        ZenClientConfig(api_key="k", base_url="http://x", max_tokens=0)
    assert ZenClientConfig(api_key="k", base_url="http://x").max_tokens == 1024


# --- retryable classification ---


def test_retryable_transient_errors():
    assert is_retryable_error(_status_error(RateLimitError, 429)) is True
    assert is_retryable_error(APIConnectionError(request=_request())) is True
    assert is_retryable_error(APITimeoutError(request=_request())) is True
    assert is_retryable_error(_status_error(InternalServerError, 500)) is True


def test_permanent_errors_not_retryable():
    assert is_retryable_error(_status_error(AuthenticationError, 401)) is False
    assert is_retryable_error(_status_error(BadRequestError, 400)) is False


@pytest.mark.parametrize("status", [408, 409, 429, 500, 502, 503, 504])
def test_all_retryable_status_codes(status):
    assert is_retryable_error(_status_error(APIStatusError, status)) is True


@pytest.mark.parametrize("status", [400, 401, 403, 404, 422])
def test_all_permanent_status_codes(status):
    assert is_retryable_error(_status_error(APIStatusError, status)) is False


def test_sdk_error_hierarchy_assumption():
    # is_retryable_error relies on this MRO: fail fast if the SDK reshapes it.
    assert issubclass(RateLimitError, APIStatusError)
    assert issubclass(APITimeoutError, APIConnectionError)


def test_jitter_stays_within_bounds():
    sleep = SleepRecorder()
    client = make_client(sleep, seed=1)
    policy = client._policy
    for attempt in (1, 2, 5):
        delay = client._sample_backoff(attempt)
        grown = min(policy.backoff_base**attempt, policy.backoff_cap_seconds)
        assert grown <= delay <= grown + policy.jitter_seconds


def test_chat_json_rejects_bad_input():
    sleep = SleepRecorder()
    client = make_client(sleep)
    messages = [{"role": "user", "content": "hi"}]
    with pytest.raises(ValueError):
        run(client.chat_json(model="", messages=messages, temperature=0.0))
    with pytest.raises(ValueError):
        run(client.chat_json(model="m", messages=[], temperature=0.0))
    with pytest.raises(ValueError):
        run(
            client.chat_json(model="m", messages=messages, temperature=float("nan"))
        )
    with pytest.raises(ValueError):
        run(
            client.chat_json(
                model="m", messages=messages, temperature=0.0, max_attempts=0
            )
        )


@pytest.mark.parametrize(
    "messages",
    [
        [{"role": "", "content": "hi"}],
        [{"role": "user", "content": ""}],
        [{"role": "user"}],
    ],
)
def test_chat_json_rejects_empty_message_fields(messages):
    sleep = SleepRecorder()
    client = make_client(sleep)
    calls = stub_request_content(client, ['{"ok": true}'])
    with pytest.raises(ValueError):
        run(client.chat_json(model="m", messages=messages, temperature=0.0))
    assert calls["n"] == 0  # rejected before any network call.
    assert sleep.delays == []


# --- chat_json behavior ---


def test_success_first_attempt_no_sleep():
    sleep = SleepRecorder()
    client = make_client(sleep)
    calls = stub_request_content(client, ['{"q1": "A"}'])
    result = run(
        client.chat_json(model="m", messages=[{"role": "user", "content": "hi"}], temperature=0.0)
    )
    assert result == {"q1": "A"}
    assert calls["n"] == 1
    assert sleep.delays == []


def test_retry_then_success():
    sleep = SleepRecorder()
    client = make_client(sleep)
    calls = stub_request_content(
        client, [APIConnectionError(request=_request()), '{"ok": true}']
    )
    result = run(
        client.chat_json(model="m", messages=[{"role": "user", "content": "hi"}], temperature=0.0)
    )
    assert result == {"ok": True}
    assert calls["n"] == 2
    assert len(sleep.delays) == 1  # 1 retry -> 1 sleep.


def test_exhaustion_raises_with_cause_and_no_final_sleep():
    sleep = SleepRecorder()
    client = make_client(sleep, attempts=3)
    calls = stub_request_content(
        client, [APIConnectionError(request=_request())] * 3
    )
    with pytest.raises(RetryExhaustedError) as exc_info:
        run(
            client.chat_json(
                model="m", messages=[{"role": "user", "content": "hi"}], temperature=0.0
            )
        )
    assert exc_info.value.model == "m"
    assert exc_info.value.attempts == 3
    assert isinstance(exc_info.value.__cause__, APIConnectionError)
    assert calls["n"] == 3
    assert len(sleep.delays) == 2  # no sleep after final attempt.


def test_malformed_response_retried_then_success():
    sleep = SleepRecorder()
    client = make_client(sleep)
    calls = stub_request_content(client, ["bukan json sama sekali", '{"q1": "B"}'])
    result = run(
        client.chat_json(model="m", messages=[{"role": "user", "content": "hi"}], temperature=0.0)
    )
    assert result == {"q1": "B"}
    assert calls["n"] == 2
    assert sleep.delays == [client._policy.invalid_response_delay_seconds]


def test_empty_response_raises_malformed():
    from src.synthetic.validation import _extract_json

    with pytest.raises(MalformedResponseError):
        _extract_json("   ")


def test_permanent_error_propagates_without_retry():
    sleep = SleepRecorder()
    client = make_client(sleep)
    calls = stub_request_content(
        client, [_status_error(AuthenticationError, 401)]
    )
    with pytest.raises(AuthenticationError):
        run(
            client.chat_json(
                model="m", messages=[{"role": "user", "content": "hi"}], temperature=0.0
            )
        )
    assert calls["n"] == 1
    assert sleep.delays == []


def test_extract_message_content_rejects_empty_choices():
    with pytest.raises(EmptyResponseError):
        _extract_message_content(SimpleNamespace(choices=[]))
    with pytest.raises(EmptyResponseError):
        _extract_message_content(
            SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=""))])
        )


def test_request_content_forwards_max_tokens():
    seen = {}

    async def fake_create(**kwargs):
        seen.update(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content='{"a": 1}'))]
        )

    sleep = SleepRecorder()
    client = make_client(sleep)
    client._client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=fake_create))
    )
    assert (
        run(
            client.chat_json(
                model="m", messages=[{"role": "user", "content": "hi"}], temperature=0.0
            )
        )
        == {"a": 1}
    )
    assert seen["model"] == "m"
    assert seen["max_tokens"] == 1024


def test_session_id_defaults_to_stable_ses():
    client = make_client(SleepRecorder())
    assert client.session_id.startswith("ses_")
    assert len(client.session_id) == 20


def test_custom_session_id_respected():
    config = ZenClientConfig(api_key="k", base_url="http://x", session_id="ses_custom")
    client = ZenClient(config, sleep=SleepRecorder(), rng=random.Random(0))
    assert client.session_id == "ses_custom"


def test_lifecycle_close_idempotent_and_context_manager():
    sleep = SleepRecorder()
    client = make_client(sleep)
    closed = {"n": 0}

    async def fake_close():
        closed["n"] += 1

    client._client.close = fake_close
    run(client.close())
    run(client.close())
    assert closed["n"] == 1  # second close is a no-op.

    client2 = make_client(sleep)
    client2._client.close = fake_close

    async def use_with():
        async with client2 as entered:
            assert entered is client2

    run(use_with())
    assert closed["n"] == 2
