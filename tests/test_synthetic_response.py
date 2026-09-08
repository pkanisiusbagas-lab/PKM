"""Tests for the SurveyResponse DTO contract."""

from __future__ import annotations

import dataclasses

import pytest

from src.synthetic.response import SurveyResponse


def _response(**overrides):
    kwargs = {
        "respondent_id": "R00001-abc123",
        "kecenderungan_dominan": "X",
        "kecenderungan_sekunder": "Y",
        "sifat_kepribadian": "rajin",
        "level_keyakinan_persona": "yakin",
        "kota_asal": "Jakarta",
        "profil_singkat": "halo",
        "answers": {"q1": "A", "q10": 7},
        "generated_at": "2026-01-01T00:00:00+00:00",
    }
    kwargs.update(overrides)
    return SurveyResponse(**kwargs)


def test_to_flat_dict_layout():
    flat = _response().to_flat_dict()
    assert list(flat) == [
        "respondent_id",
        "kecenderungan_dominan",
        "kecenderungan_sekunder",
        "sifat_kepribadian",
        "level_keyakinan_persona",
        "kota_asal",
        "profil_singkat",
        "q1",
        "q10",
        "generated_at",
    ]
    assert flat["q1"] == "A" and flat["q10"] == 7


def test_answers_colliding_with_fixed_fields_rejected():
    with pytest.raises(ValueError, match="collide"):
        _response(answers={"kota_asal": "X"})


def test_empty_respondent_id_rejected():
    with pytest.raises(ValueError, match="respondent_id"):
        _response(respondent_id="")


def test_frozen():
    with pytest.raises(dataclasses.FrozenInstanceError):
        _response().kota_asal = "X"
