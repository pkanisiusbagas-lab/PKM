from __future__ import annotations

import json
from functools import lru_cache

from .questionnaire import QUESTIONNAIRE
from .types import ChatMessage, PersonaRecord


@lru_cache(maxsize=1)
def render_questionnaire() -> str:
    """Render the questionnaire as plain text for injection into a prompt."""
    lines: list[str] = []
    for q in QUESTIONNAIRE:
        lines.append(f"{q.number}. {q.prompt}")
        if q.kind == "single_choice":
            for opt in q.options:
                lines.append(f"   {opt.key}. {opt.label}")
        elif q.kind == "slider":
            assert q.slider_min is not None and q.slider_max is not None, (
                f"Q{q.number} slider lacks bounds"
            )
            lines.append(
                f"   (Slider {q.slider_min}-{q.slider_max}, "
                f"{q.slider_min}=Masih sangat bingung, {q.slider_max}=Sudah sangat yakin dan mantap)"
            )
        else:
            lines.append("   (Tulis jawaban bebas dengan kata-katamu sendiri)")
        lines.append("")
    return "\n".join(lines)


def _group_runs(numbers: list[int]) -> list[tuple[int, int]]:
    grouped = []
    start = prev = numbers[0]
    for n in numbers[1:]:
        if n == prev + 1:
            prev = n
            continue
        grouped.append((start, prev))
        start = prev = n
    grouped.append((start, prev))
    return grouped


def _compact_range(numbers: list[int]) -> str:
    return ", ".join(
        f"{start}-{end}" if start != end else str(start)
        for start, end in _group_runs(numbers)
    )


def answer_format_hint() -> str:
    """Answer-format instruction derived from QUESTIONNAIRE, never hardcoded."""
    singles = [q.number for q in QUESTIONNAIRE if q.kind == "single_choice"]
    sliders = [q for q in QUESTIONNAIRE if q.kind == "slider"]
    opens = [q.number for q in QUESTIONNAIRE if q.kind == "open_text"]
    parts = [f"HURUF opsi untuk nomor {_compact_range(singles)}"]
    for q in sliders:
        parts.append(f"angka {q.slider_min}-{q.slider_max} untuk nomor {q.number}")
    if opens:
        parts.append(f"jawaban bebas untuk nomor {_compact_range(opens)}")
    if len(parts) == 1:
        return f"Jawab tiap nomor dengan {parts[0]}."
    return "Jawab tiap nomor dengan " + ", ".join(parts[:-1]) + ", dan " + parts[-1] + "."


def _key_hint(keys: list[str]) -> str:
    nums = [int(key[1:]) for key in keys]
    return ", ".join(
        f"q{start} sampai q{end}" if start != end else f"q{start}"
        for start, end in _group_runs(nums)
    )


def key_format_hint() -> str:
    """Key-list instruction derived from QUESTIONNAIRE, never hardcoded."""
    segments = []
    singles = [f"q{q.number}" for q in QUESTIONNAIRE if q.kind == "single_choice"]
    sliders = [f"q{q.number}" for q in QUESTIONNAIRE if q.kind == "slider"]
    opens = [f"q{q.number}" for q in QUESTIONNAIRE if q.kind == "open_text"]
    if singles:
        segments.append(f"{_key_hint(singles)} (huruf kapital)")
    if sliders:
        segments.append(f"{_key_hint(sliders)} (angka)")
    if opens:
        segments.append(f"{_key_hint(opens)} (teks bebas)")
    return "Keluarkan JSON persis dengan key " + ", ".join(segments) + ". "


def example_answers() -> str:
    """Valid example answers derived from QUESTIONNAIRE (passes validation)."""
    example: dict[str, str | int] = {}
    for q in QUESTIONNAIRE:
        key = f"q{q.number}"
        if q.kind == "single_choice":
            example[key] = q.options[0].key if q.options else ""
        elif q.kind == "slider":
            example[key] = q.slider_min if q.slider_min is not None else ""
        else:
            example[key] = "Dokter"
    return json.dumps(example, ensure_ascii=False)


def build_persona_prompt(
    leaning: str, personality: str, confidence: str, city: str, seed: int
) -> list[ChatMessage]:
    """System+user messages instructing the persona agent; JSON-only reply."""
    system = (
        "Kamu adalah generator persona siswa SMA di Indonesia yang sedang "
        "memikirkan pendidikan lanjutan (kuliah/karier). Buat SATU persona fiktif yang terasa "
        "manusiawi, spesifik, dan tidak klise. Balas HANYA dengan JSON valid, tanpa "
        "markdown, tanpa penjelasan tambahan."
    )
    user = (
        f"Kecenderungan minat utama persona ini: {leaning}.\n"
        f"Kepribadian: {personality}.\n"
        f"Tingkat keyakinan terhadap pilihan pendidikan lanjutan: {confidence}.\n"
        f"Kota asal (untuk rasa lokal, opsional dipakai di narasi): {city}.\n"
        f"Kode variasi internal (jangan ditampilkan di output): {seed}.\n\n"
        "Keluarkan JSON dengan struktur persis seperti ini:\n"
        "{\n"
        '  "kecenderungan_sekunder": "<satu kecenderungan minat lain yang juga lumayan kuat>",\n'
        '  "sifat_tambahan": "<1-3 kata sifat lain selain yang sudah diberikan>",\n'
        '  "profil_singkat": "<2-3 kalimat cerita singkat tentang siswa ini, gaya bahasa '
        'natural remaja Indonesia, JANGAN pakai kalimat template>"\n'
        "}"
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def build_respondent_prompt(persona: PersonaRecord) -> list[ChatMessage]:
    """System+user messages instructing the respondent agent; JSON-only reply."""
    system = (
        "Kamu berperan sebagai siswa SMA yang menjawab kuesioner minat, "
        "sesuai persona yang diberikan. Sebagian besar jawaban (kira-kira 70-85%) harus "
        "konsisten dengan persona, tapi sisanya boleh sedikit meleset seperti manusia "
        "asli yang kadang terpengaruh mood, pengalaman kecil, atau rasa penasaran, "
        "supaya data terasa alami dan tidak seragam. Balas HANYA dengan JSON valid, "
        "tanpa markdown, tanpa penjelasan tambahan."
    )
    user = (
        "Persona kamu:\n"
        f"{json.dumps(persona, ensure_ascii=False, indent=2)}\n\n"
        "Berikut kuesionernya. "
        f"{answer_format_hint()}\n\n"
        f"{render_questionnaire()}\n"
        f"{key_format_hint()}"
        "Contoh format:\n"
        f"{example_answers()}"
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]
