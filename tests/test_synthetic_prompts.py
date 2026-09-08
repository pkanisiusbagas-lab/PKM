"""Tests for prompt builders. Pure functions, no network.

Also pins the respondent change: prompts address SMA students.
"""

from __future__ import annotations

import json

from src.synthetic.prompts import (
    answer_format_hint,
    build_persona_prompt,
    build_respondent_prompt,
    example_answers,
    key_format_hint,
    render_questionnaire,
)
from src.synthetic.questionnaire import QUESTIONNAIRE
from src.synthetic.validation import validate_answers


def test_render_covers_all_questions():
    text = render_questionnaire()
    for q in QUESTIONNAIRE:
        assert f"{q.number}." in text
    assert "Slider 1-10" in text


def test_builders_return_system_user_pair():
    persona_msgs = build_persona_prompt("Tekno", "rajin", "yakin", "Jakarta", 1)
    assert [m["role"] for m in persona_msgs] == ["system", "user"]
    assert "Jakarta" in persona_msgs[1]["content"]
    assert "Tekno" in persona_msgs[1]["content"]


def test_respondent_embeds_persona():
    persona = {
        "kecenderungan_dominan": "X",
        "kecenderungan_sekunder": "Y",
        "sifat_kepribadian": "rajin",
        "level_keyakinan": "yakin",
        "kota_asal": "Jakarta",
        "profil_singkat": "halo",
    }
    msgs = build_respondent_prompt(persona)
    assert [m["role"] for m in msgs] == ["system", "user"]
    assert "halo" in msgs[1]["content"]
    assert "Slider 1-10" in msgs[1]["content"]


def test_prompts_address_sma_students():
    persona_text = build_persona_prompt("X", "y", "z", "K", 1)[0]["content"]
    respondent_text = build_respondent_prompt(
        {
            "kecenderungan_dominan": "X",
            "kecenderungan_sekunder": "Y",
            "sifat_kepribadian": "y",
            "level_keyakinan": "z",
            "kota_asal": "K",
            "profil_singkat": "p",
        }
    )[0]["content"]
    for text in (persona_text, respondent_text):
        assert "SMA" in text
        assert "SMP" not in text


def test_format_hints_derive_from_questionnaire():
    assert "1-9" in answer_format_hint()
    assert "q1 sampai q9" in key_format_hint()
    assert "q10" in key_format_hint()


def test_example_answers_pass_validation():
    example = json.loads(example_answers())
    validated = validate_answers(example)
    assert set(validated) == {f"q{q.number}" for q in QUESTIONNAIRE}
