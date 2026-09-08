"""Structural tests for the questionnaire instrument."""

from __future__ import annotations

import pytest

from src.synthetic.questionnaire import QUESTIONNAIRE


def test_numbers_unique_and_sequential():
    assert [q.number for q in QUESTIONNAIRE] == list(range(1, 17))


def test_single_choice_options_well_formed():
    singles = [q for q in QUESTIONNAIRE if q.kind == "single_choice"]
    assert len(singles) == 14
    for q in singles:
        assert len(q.options) >= 2
        keys = [o.key for o in q.options]
        assert keys == [chr(ord("A") + i) for i in range(len(keys))]
        assert all(o.label for o in q.options)


def test_slider_sane():
    sliders = [q for q in QUESTIONNAIRE if q.kind == "slider"]
    assert len(sliders) == 1
    q = sliders[0]
    assert q.slider_min is not None and q.slider_max is not None
    assert q.slider_min < q.slider_max
    assert q.options == ()


def test_open_text_present_and_empty_options():
    opens = [q for q in QUESTIONNAIRE if q.kind == "open_text"]
    assert [q.number for q in opens] == [16]
    assert opens[0].options == ()


def test_kinds_valid():
    assert {q.kind for q in QUESTIONNAIRE} == {"single_choice", "slider", "open_text"}


def test_invalid_questions_rejected():
    from src.synthetic.questionnaire import Question

    with pytest.raises(ValueError):
        Question(number=99, prompt="x", options=(), kind="slider")
    with pytest.raises(ValueError):
        Question(number=99, prompt="x", options=())
