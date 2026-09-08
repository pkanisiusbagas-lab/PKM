"""Tests for the synthetic error hierarchy contracts.

Pins the backward-compat guarantees documented in errors.py and the
picklability of RetryExhaustedError across process boundaries.
"""

from __future__ import annotations

import pickle

import pytest

from src.synthetic.errors import (
    EmptyResponseError,
    LLMResponseError,
    MalformedResponseError,
    RetryExhaustedError,
    SyntheticError,
)


def test_backward_compat_contracts():
    assert issubclass(LLMResponseError, ValueError)
    assert issubclass(EmptyResponseError, SyntheticError)
    assert issubclass(MalformedResponseError, SyntheticError)
    assert issubclass(RetryExhaustedError, RuntimeError)
    assert issubclass(RetryExhaustedError, SyntheticError)


def test_retry_exhausted_carries_context():
    err = RetryExhaustedError("m", 3)
    assert err.model == "m"
    assert err.attempts == 3
    assert "m" in str(err) and "3" in str(err)


def test_retry_exhausted_rejects_bad_args():
    with pytest.raises(ValueError):
        RetryExhaustedError("", 3)
    with pytest.raises(ValueError):
        RetryExhaustedError("m", 0)
    with pytest.raises(ValueError):
        RetryExhaustedError("m", -1)


def test_retry_exhausted_survives_pickle():
    err = pickle.loads(pickle.dumps(RetryExhaustedError("m", 3)))
    assert (err.model, err.attempts) == ("m", 3)
