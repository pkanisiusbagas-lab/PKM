"""Pins for the static type contracts in types.py.

These fail loudly the moment someone edits a contract that
downstream code silently depends on.
"""

from __future__ import annotations

from typing import get_args

from src.synthetic.types import ChatMessage, FailureCategory, PersonaRecord


def test_message_contract():
    assert ChatMessage.__required_keys__ == {"role", "content"}


def test_persona_record_contract():
    assert PersonaRecord.__required_keys__ == {
        "kecenderungan_dominan",
        "kecenderungan_sekunder",
        "sifat_kepribadian",
        "level_keyakinan",
        "kota_asal",
        "profil_singkat",
    }


def test_failure_category_values():
    # FailureCategory is a PEP 695 alias; unwrap via __value__ first.
    assert set(get_args(FailureCategory.__value__)) == {
        "rate_limit",
        "connection",
        "server",
        "client",
        "unknown",
        "invalid_response",
    }
