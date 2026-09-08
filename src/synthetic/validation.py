from __future__ import annotations

import json
import re
from typing import cast

from .errors import MalformedResponseError
from .questionnaire import QUESTIONNAIRE
from .types import JsonObject


def _extract_json(text: str) -> JsonObject:
    """Best-effort JSON extraction, tolerant of markdown fences or stray prose."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.MULTILINE).strip()
    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if not match:
        raise MalformedResponseError(
            f"No JSON object found in model response: {text[:200]!r}"
        )
    try:
        parsed = json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        raise MalformedResponseError(
            f"Model response is not valid JSON: {text[:200]!r}"
        ) from exc
    if not isinstance(parsed, dict):
        raise MalformedResponseError("Model response is not a JSON object.")
    return cast(JsonObject, parsed)


def validate_answers(raw: JsonObject) -> dict[str, str | int]:
    """Validate and normalize a raw answer dict against the questionnaire schema.

    Leniency contract (deliberate, for sloppy model output): single letters
    are extracted via strip/upper/first-char; sliders truncate floats toward
    zero; open text maps None to "". Unknown question kinds raise.
    """
    validated: dict[str, str | int] = {}
    for q in QUESTIONNAIRE:
        key = f"q{q.number}"
        if key not in raw:
            raise ValueError(f"Key '{key}' is missing from model output")
        value = raw[key]
        if q.kind == "single_choice":
            keys = q.valid_keys()
            letter = str(value).strip().upper()[:1]
            if letter not in keys:
                raise ValueError(
                    f"Option '{value}' is invalid for {key}; expected one of {keys}"
                )
            validated[key] = letter
        elif q.kind == "slider":
            try:
                number = int(float(value))
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid slider value '{value}' for {key}") from exc
            assert q.slider_min is not None and q.slider_max is not None
            if not (q.slider_min <= number <= q.slider_max):
                raise ValueError(f"Slider value {number} is out of range for {key}")
            validated[key] = number
        elif q.kind == "open_text":
            validated[key] = "" if value is None else str(value)
        else:
            raise ValueError(f"Unknown question kind {q.kind!r} for {key}.")
    return validated
