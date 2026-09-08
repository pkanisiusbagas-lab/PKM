from __future__ import annotations

import random
from typing import Final

LEANING_CATEGORIES: Final[tuple[str, ...]] = (
    "Sains & Riset (MIPA)",
    "Sosial & Humaniora (IPS/Bahasa)",
    "Teknologi & Rekayasa Perangkat Lunak",
    "Vokasi Teknik & Otomotif/Elektronika",
    "Bisnis, Ekonomi & Kewirausahaan",
    "Seni, Desain & Industri Kreatif",
    "Kuliner & Perhotelan",
    "Belum Yakin / Minat Campuran",
)

PERSONALITY_TRAITS: Final[tuple[str, ...]] = (
    "pemalu tapi observatif",
    "percaya diri dan ekspresif",
    "kompetitif",
    "santai dan easy going",
    "perfeksionis",
    "spontan dan suka coba hal baru",
    "pendiam tapi keras kepala soal minatnya",
    "ambisius",
    "gampang bosan kalau materinya monoton",
    "sangat rajin dan terencana",
    "humoris dan suka jadi pusat perhatian",
    "penuh rasa ingin tahu",
)

CONFIDENCE_LEVELS: Final[tuple[str, ...]] = (
    "masih sangat bingung",
    "sedikit condong tapi belum yakin",
    "cukup yakin",
    "sangat yakin dan mantap",
)

INDONESIAN_CITIES: Final[tuple[str, ...]] = (
    "Jakarta", "Surabaya", "Bandung", "Medan", "Makassar", "Yogyakarta",
    "Semarang", "Palembang", "Denpasar", "Balikpapan", "Malang", "Pekanbaru",
)


def build_stratified_leanings(n: int, rng: random.Random | None = None) -> list[str]:
    """Evenly distribute n samples across LEANING_CATEGORIES, then shuffle order.

    Each category appears n // 8 or n // 8 + 1 times. n == 0 returns [].
    Pass rng for reproducible ordering.
    """
    if n < 0:
        raise ValueError(f"n must not be negative, got {n}.")
    r = rng if rng is not None else random
    categories = list(LEANING_CATEGORIES)
    base = categories * (n // len(categories))
    remainder = n - len(base)
    if remainder:
        # Invariant: remainder == n % len(categories), so sample() never
        # needs replacement draws here.
        base.extend(r.sample(categories, remainder))
    r.shuffle(base)
    return base
