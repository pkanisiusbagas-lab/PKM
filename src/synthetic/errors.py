"""Failure domains for the synthetic survey pipeline.

Hierarchy:
- SyntheticError: base of all pipeline errors in this package.
- LLMResponseError (also a ValueError): the model returned something
  unusable. Subclassing ValueError keeps existing `except ValueError`
  handlers working.
- RetryExhaustedError (also a RuntimeError): every attempt failed.
  Existing `except RuntimeError` handlers keep working.
"""

from __future__ import annotations


class SyntheticError(Exception):
    """Base class for all synthetic-pipeline errors."""


class LLMResponseError(SyntheticError, ValueError):
    """Model returned something unusable (empty or malformed)."""


class EmptyResponseError(LLMResponseError):
    """Model returned no choices or empty message content."""


class MalformedResponseError(LLMResponseError):
    """Model content held no parseable JSON object."""


class RetryExhaustedError(SyntheticError, RuntimeError):
    """All attempts failed.

    Attributes:
        model: Model identifier from the failed call.
        attempts: Total attempts made, including the first.
        The original error is available as __cause__.
    """

    model: str
    attempts: int

    def __init__(self, model: str, attempts: int) -> None:
        if not isinstance(model, str) or not model:
            raise ValueError("model must be a non-empty string.")
        if not isinstance(attempts, int) or isinstance(attempts, bool) or attempts < 1:
            raise ValueError("attempts must be a positive int.")
        super().__init__(f"Model call '{model}' failed after {attempts} attempts")
        self.model = model
        self.attempts = attempts

    def __reduce__(self):  # keep the exception picklable across process boundaries.
        return (RetryExhaustedError, (self.model, self.attempts))


class FailureBudgetExceededError(SyntheticError, RuntimeError):
    """Failure rate exceeded the configured budget mid-run."""

    rate: float
    limit: float
    failures: int
    completed: int

    def __init__(self, rate: float, limit: float, failures: int, completed: int) -> None:
        super().__init__(
            f"Failure rate {rate:.0%} exceeded budget {limit:.0%} "
            f"({failures}/{completed} failed)"
        )
        self.rate = rate
        self.limit = limit
        self.failures = failures
        self.completed = completed

    def __reduce__(self):  # keep the exception picklable across process boundaries.
        return (FailureBudgetExceededError, (self.rate, self.limit, self.failures, self.completed))
