"""Backward-compatible facade — logic lives in split modules, CLI stays the same."""

from __future__ import annotations

import asyncio
import importlib
import logging
import sys
from pathlib import Path

from .errors import SyntheticError

logger = logging.getLogger(__name__)

_LAZY_EXPORTS = {
    "CONFIDENCE_LEVELS": ".pools",
    "ChatMessage": ".types",
    "Config": ".config",
    "EmptyResponseError": ".errors",
    "FailureBudgetExceededError": ".errors",
    "FailureCategory": ".types",
    "INDONESIAN_CITIES": ".pools",
    "JsonObject": ".types",
    "LEANING_CATEGORIES": ".pools",
    "LLMResponseError": ".errors",
    "MalformedResponseError": ".errors",
    "PERSONALITY_TRAITS": ".pools",
    "PROVIDER_PRESETS": ".providers",
    "PersonaRecord": ".types",
    "ProviderPreset": ".providers",
    "QUESTIONNAIRE": ".questionnaire",
    "Question": ".questionnaire",
    "QuestionOption": ".questionnaire",
    "RetryExhaustedError": ".errors",
    "RetryPolicy": ".client",
    "SurveyResponse": ".response",
    "SyntheticError": ".errors",
    "ZenClient": ".client",
    "ZenClientConfig": ".client",
    "build_persona_prompt": ".prompts",
    "build_persona_record": ".pipeline",
    "build_respondent_prompt": ".prompts",
    "build_stratified_leanings": ".pipeline",
    "export_csv": ".pipeline",
    "generate_one_sample": ".pipeline",
    "generate_one_sample_with_retry": ".pipeline",
    "is_retryable_error": ".client",
    "load_config": ".config",
    "render_questionnaire": ".prompts",
    "resolve_provider": ".providers",
    "run_pipeline": ".pipeline",
    "setup_logging": ".config",
    "validate_answers": ".validation",
}


def __getattr__(name: str):
    if name in _LAZY_EXPORTS:
        module = importlib.import_module(_LAZY_EXPORTS[name], __package__)
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


async def main_async() -> int:
    """Run the generation pipeline. Returns the process exit code."""
    from .config import load_config, setup_logging
    from .pipeline import export_csv, run_pipeline

    setup_logging()
    config = load_config()
    logger.info(
        "Generating %d samples | persona agent=%s | respondent agent=%s | concurrency=%d",
        config.num_samples, config.persona_model, config.respondent_model, config.concurrency,
    )
    samples = await run_pipeline(config)
    if not samples:
        logger.error("No samples were created.")
        return 1
    csv_path = Path(config.output_path).with_suffix(".csv")
    export_csv(samples, csv_path)
    logger.info("Dataset JSONL : %s", config.output_path)
    logger.info("Dataset CSV   : %s", csv_path)
    return 0


def main() -> None:
    """CLI entrypoint: maps interrupts and config errors to exit code 1."""
    try:
        sys.exit(asyncio.run(main_async()))
    except KeyboardInterrupt:
        logger.warning("Cancelled by user.")
        sys.exit(1)
    except SyntheticError as exc:
        logger.error("Run aborted: %s", exc)
        sys.exit(1)
    except OSError as exc:
        logger.error(str(exc))
        sys.exit(1)


__all__ = [
    "CONFIDENCE_LEVELS",
    "INDONESIAN_CITIES",
    "LEANING_CATEGORIES",
    "PERSONALITY_TRAITS",
    "PROVIDER_PRESETS",
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
    "ProviderPreset",
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
    "main",
    "main_async",
    "render_questionnaire",
    "resolve_provider",
    "run_pipeline",
    "setup_logging",
    "validate_answers",
]


if __name__ == "__main__":
    main()
