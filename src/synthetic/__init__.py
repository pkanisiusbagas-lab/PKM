"""Synthetic survey generation package (facade-friendly)."""

from .client import RetryPolicy, ZenClient, ZenClientConfig, is_retryable_error
from .config import Config, load_config, setup_logging
from .errors import (
    EmptyResponseError,
    FailureBudgetExceededError,
    LLMResponseError,
    MalformedResponseError,
    RetryExhaustedError,
    SyntheticError,
)
from .pipeline import (
    build_persona_record,
    export_csv,
    generate_one_sample,
    generate_one_sample_with_retry,
    run_pipeline,
)
from .pools import (
    CONFIDENCE_LEVELS,
    INDONESIAN_CITIES,
    LEANING_CATEGORIES,
    PERSONALITY_TRAITS,
    build_stratified_leanings,
)
from .prompts import (
    build_persona_prompt,
    build_respondent_prompt,
    render_questionnaire,
)
from .questionnaire import QUESTIONNAIRE, Question, QuestionOption
from .response import SurveyResponse
from .types import ChatMessage, FailureCategory, JsonObject, PersonaRecord
from .validation import validate_answers

__all__ = [
    "CONFIDENCE_LEVELS",
    "INDONESIAN_CITIES",
    "LEANING_CATEGORIES",
    "PERSONALITY_TRAITS",
    "QUESTIONNAIRE",
    "ChatMessage",
    "Config",
    "EmptyResponseError",
    "FailureBudgetExceededError",
    "FailureCategory",
    "JsonObject",
    "LLMResponseError",
    "MalformedResponseError",
    "PersonaRecord",
    "Question",
    "QuestionOption",
    "RetryExhaustedError",
    "RetryPolicy",
    "SurveyResponse",
    "SyntheticError",
    "ZenClient",
    "ZenClientConfig",
    "build_persona_prompt",
    "build_persona_record",
    "build_respondent_prompt",
    "build_stratified_leanings",
    "export_csv",
    "generate_one_sample",
    "generate_one_sample_with_retry",
    "is_retryable_error",
    "load_config",
    "render_questionnaire",
    "run_pipeline",
    "setup_logging",
    "validate_answers",
]
