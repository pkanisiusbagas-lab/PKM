"""One generated respondent: structured record plus its flat artifact layout."""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass

from .types import JsonObject


@dataclass(frozen=True)
class SurveyResponse:
    """One generated survey response with validated answers."""

    respondent_id: str
    kecenderungan_dominan: str
    kecenderungan_sekunder: str
    sifat_kepribadian: str
    level_keyakinan_persona: str
    kota_asal: str
    profil_singkat: str
    answers: dict[str, str | int]
    generated_at: str

    def __post_init__(self) -> None:
        if not self.respondent_id:
            raise ValueError("respondent_id must not be empty.")
        reserved = {f.name for f in dataclasses.fields(self)} - {"answers"}
        collision = set(self.answers) & reserved
        if collision:
            raise ValueError(f"answers collide with fixed fields: {sorted(collision)}.")

    def to_flat_dict(self) -> JsonObject:
        """Flat layout for JSONL/CSV: fixed fields, answers spread, timestamp."""
        return {
            "respondent_id": self.respondent_id,
            "kecenderungan_dominan": self.kecenderungan_dominan,
            "kecenderungan_sekunder": self.kecenderungan_sekunder,
            "sifat_kepribadian": self.sifat_kepribadian,
            "level_keyakinan_persona": self.level_keyakinan_persona,
            "kota_asal": self.kota_asal,
            "profil_singkat": self.profil_singkat,
            **self.answers,
            "generated_at": self.generated_at,
        }
