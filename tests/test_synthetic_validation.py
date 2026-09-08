"""Direct tests for JSON extraction and answer normalization edges."""

from __future__ import annotations

import json

import pytest

import src.synthetic.validation as validation_mod
from src.synthetic.errors import MalformedResponseError
from src.synthetic.questionnaire import QUESTIONNAIRE, Question, _opts
from src.synthetic.validation import _extract_json, validate_answers


def _valid_raw():
    raw = {}
    for q in QUESTIONNAIRE:
        key = f"q{q.number}"
        if q.kind == "single_choice":
            raw[key] = q.options[0].key
        elif q.kind == "slider":
            raw[key] = q.slider_min
        else:
            raw[key] = "Dokter"
    return raw


def test_extract_strips_fences_and_prose():
    assert _extract_json('```json\n{"q1": "A"}\n```') == {"q1": "A"}
    assert _extract_json('Here you go: {"q1": "A"} enjoy!') == {"q1": "A"}
    assert _extract_json('{"q1": "A"}') == {"q1": "A"}


def test_extract_rejects_non_objects():
    with pytest.raises(MalformedResponseError):
        _extract_json("[1, 2, 3]")
    with pytest.raises(MalformedResponseError):
        _extract_json("no json here")
    with pytest.raises(MalformedResponseError):
        _extract_json('{"q1": }')


def test_normalization_edges():
    assert validate_answers({**_valid_raw(), "q1": "b."})["q1"] == "B"
    assert validate_answers({**_valid_raw(), "q10": "7.9"})["q10"] == 7
    assert validate_answers({**_valid_raw(), "q16": None})["q16"] == ""
    assert validate_answers({**_valid_raw(), "q16": "Pilot"})["q16"] == "Pilot"


def test_missing_and_invalid_keys():
    raw = _valid_raw()
    del raw["q2"]
    with pytest.raises(ValueError, match="q2"):
        validate_answers(raw)
    with pytest.raises(ValueError, match="q3"):
        validate_answers({**_valid_raw(), "q3": "Z"})
    with pytest.raises(ValueError, match="q10"):
        validate_answers({**_valid_raw(), "q10": 99})


def test_unknown_kind_raises(monkeypatch):
    weird = Question(number=1, prompt="x", options=_opts(("A", "a")), kind="mystery")
    monkeypatch.setattr(validation_mod, "QUESTIONNAIRE", (weird,))
    with pytest.raises(ValueError, match="Unknown question kind"):
        validate_answers({"q1": "A"})


def test_example_from_prompts_still_valid():
    from src.synthetic.prompts import example_answers

    validated = validate_answers(json.loads(example_answers()))
    assert set(validated) == {f"q{q.number}" for q in QUESTIONNAIRE}
