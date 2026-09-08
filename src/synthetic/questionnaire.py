"""Single source of truth for the survey instrument.

Consumers (prompts.render_questionnaire, validation.validate_answers, and the
derived prompt hints) adapt automatically — keep question numbers unique and
sequential. Indonesian text is intentional survey content, not code.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal

QuestionKind = Literal["single_choice", "slider", "open_text"]


@dataclass(frozen=True)
class QuestionOption:
    key: str
    label: str


@dataclass(frozen=True)
class Question:
    number: int
    prompt: str
    options: tuple[QuestionOption, ...]
    kind: QuestionKind = "single_choice"
    slider_min: int | None = None
    slider_max: int | None = None

    def __post_init__(self) -> None:
        if self.kind == "slider":
            if self.slider_min is None or self.slider_max is None:
                raise ValueError(f"Q{self.number}: slider lacks bounds.")
            if self.slider_min >= self.slider_max:
                raise ValueError(f"Q{self.number}: slider bounds inverted.")
            if self.options:
                raise ValueError(f"Q{self.number}: slider must have empty options.")
        elif self.kind == "open_text":
            if self.options:
                raise ValueError(f"Q{self.number}: open_text must have empty options.")
        else:
            if not self.options:
                raise ValueError(f"Q{self.number}: single_choice needs options.")
            keys = [opt.key for opt in self.options]
            if len(set(keys)) != len(keys):
                raise ValueError(f"Q{self.number}: duplicate option keys {keys}.")

    def valid_keys(self) -> tuple[str, ...]:
        return tuple(opt.key for opt in self.options)


def _opts(*pairs: tuple[str, str]) -> tuple[QuestionOption, ...]:
    return tuple(QuestionOption(key=k, label=v) for k, v in pairs)


QUESTIONNAIRE: Final[tuple[Question, ...]] = (
    Question(
        number=1,
        prompt=(
            "Kalau kamu boleh pilih cara belajar seharian di sekolah, mana yang "
            "paling bikin kamu semangat dan nggak gampang bosan?"
        ),
        options=_opts(
            ("A", "Membaca, berdiskusi, dan menganalisis teori/konsep secara mendalam"),
            ("B", "Langsung praktik (merakit, mengoperasikan alat, mencoba software, atau membuat produk nyata)"),
            ("C", "Seimbang antara dengerin penjelasan guru lalu langsung coba latihannya"),
        ),
    ),
    Question(
        number=2,
        prompt="Mata pelajaran apa yang paling bikin kamu semangat waktu jam pelajarannya tiba?",
        options=_opts(
            ("A", "Matematika / Fisika / Kimia / Biologi"),
            ("B", "Ekonomi / Geografi / Sosiologi / Sejarah"),
            ("C", "Informatika / Komputer / Coding"),
            ("D", "Seni Budaya / Prakarya / Keterampilan tangan"),
            ("E", "Bahasa Indonesia / Bahasa Inggris"),
            ("F", "PJOK / Olahraga"),
        ),
    ),
    Question(
        number=3,
        prompt="Mata pelajaran apa yang paling bikin kamu cepat capek, males, atau energimu terkuras?",
        options=_opts(
            ("A", "Hitungan rumit, rumus, dan kalkulasi angka"),
            ("B", "Hafalan materi panjang, sejarah, dan menulis esai"),
            ("C", "Koding / logika komputer yang detail"),
            ("D", "Menggambar, membuat kerajinan, atau kegiatan seni"),
            ("E", "Praktik fisik / membongkar barang / kegiatan yang kotor"),
        ),
    ),
    Question(
        number=4,
        prompt=(
            "Saat akhir pekan atau libur tanpa tugas sekolah, aktivitas apa yang "
            "paling sering bikin kamu lupa waktu?"
        ),
        options=_opts(
            ("A", "Ngoding, edit video, main game PC/konsol, atau eksplorasi teknologi"),
            ("B", "Nonton dokumenter sains, baca tentang fenomena alam, atau eksperimen kecil"),
            ("C", "Baca berita/isu sosial, ekonomi, hukum, atau novel"),
            ("D", "Ngutak-atik mesin motor/sepeda, elektronik, atau perkakas rumah"),
            ("E", "Jualan online, dropship, hitung untung-rugi, atau mikirin ide bisnis"),
            ("F", "Masak, coba resep baru, atau kegiatan yang berhubungan dengan makanan & kerapihan"),
        ),
    ),
    Question(
        number=5,
        prompt=(
            "Kalau di lingkunganmu ada masalah banjir sampah, cara apa yang paling "
            "pertama muncul di pikiranmu untuk membantu?"
        ),
        options=_opts(
            ("A", "Meneliti cara mengolah sampah secara ilmiah / biologis"),
            ("B", "Membuat kampanye sosial, edukasi warga, atau usul aturan"),
            ("C", "Merancang aplikasi digital untuk penjemputan & pengelolaan sampah"),
            ("D", "Merakit atau memodifikasi alat/mesin untuk mengolah sampah"),
            ("E", "Mengolah sampah jadi produk yang bisa dijual dan dipasarkan"),
        ),
    ),
    Question(
        number=6,
        prompt=(
            "Bayangin kamu sudah lulus sekolah menengah (umur sekitar 18 tahun). "
            "Apa target utamamu saat itu?"
        ),
        options=_opts(
            ("A", "Fokus kuliah penuh di universitas untuk dapat gelar yang tinggi"),
            ("B", "Langsung bekerja atau buka usaha sendiri biar cepat mandiri secara finansial"),
            ("C", "Bekerja sambil kuliah (kelas malam / kuliah jarak jauh)"),
            ("D", "Masih ingin memperkuat teori dulu sebelum menentukan jurusan yang lebih spesifik"),
        ),
    ),
    Question(
        number=7,
        prompt="Lingkungan kerja seperti apa yang paling bikin kamu merasa nyaman dan produktif?",
        options=_opts(
            ("A", "Laboratorium, ruang riset, atau tempat yang berhubungan dengan sains & eksperimen"),
            ("B", "Kantor profesional, lembaga, bank, media, atau tempat yang banyak interaksi & analisis"),
            ("C", "Studio digital / startup teknologi dengan komputer spesifikasi tinggi"),
            ("D", "Bengkel, pabrik, area proyek, atau tempat yang banyak kerja praktik & mesin"),
            ("E", "Kantor administrasi, akuntansi, atau tempat usaha/ritel"),
            ("F", "Dapur, restoran, hotel, atau tempat yang berhubungan dengan pelayanan & kuliner"),
        ),
    ),
    Question(
        number=8,
        prompt="Saat kerja kelompok di sekolah, kamu paling nyaman berperan sebagai apa?",
        options=_opts(
            ("A", "Yang riset data, pecahin masalah logika/rumus, dan cari solusi akurat"),
            ("B", "Yang atur pembagian tugas, catat progress, dan kontrol anggaran"),
            ("C", "Yang bikin presentasi visual, desain, atau tampilan menarik"),
            ("D", "Yang jadi juru bicara / presenter di depan kelas"),
            ("E", "Yang eksekusi teknis (merakit, membuat, atau mewujudkan hasil fisiknya)"),
        ),
    ),
    Question(
        number=9,
        prompt="Kalau kamu wajib pilih salah satu keahlian terapan di bawah ini, mana yang paling ingin kamu kuasai?",
        options=_opts(
            ("A", "Membuat aplikasi, website, atau mengelola jaringan komputer"),
            ("B", "Service motor/mobil, pengelasan, atau kelistrikan"),
            ("C", "Akuntansi, pembukuan, administrasi perkantoran, atau pemasaran"),
            ("D", "Memasak, pastry, atau keterampilan perhotelan"),
            ("E", "Desain grafis, animasi, fotografi, atau konten kreatif"),
            ("F", "Lebih tertarik belajar teori mendalam di SMA daripada keahlian terapan di atas"),
        ),
    ),
    Question(
        number=10,
        prompt="Seberapa yakin kamu dengan pilihan sekolah lanjutanmu saat ini?",
        options=(),
        kind="slider",
        slider_min=1,
        slider_max=10,
    ),
    Question(
        number=11,
        prompt=(
            "Kalau kamu berhasil menyelesaikan sesuatu, mana yang paling bikin kamu puas?"
        ),
        options=_opts(
            ("A", "Hasilnya akurat dan bisa dibuktikan (angka, data, atau eksperimen)"),
            ("B", "Hasilnya bisa memengaruhi atau membantu banyak orang"),
            ("C", "Hasilnya kelihatan keren / kreatif"),
            ("D", "Hasilnya langsung bisa dipakai atau berfungsi"),
            ("E", "Hasilnya bisa menghasilkan uang"),
        ),
    ),
    Question(
        number=12,
        prompt="Kamu lebih nyaman dengan situasi yang seperti apa?",
        options=_opts(
            ("A", "Ada aturan dan langkah yang jelas"),
            ("B", "Bisa eksperimen dan coba-coba meskipun hasilnya belum pasti"),
            ("C", "Banyak interaksi dan diskusi dengan orang"),
            ("D", "Langsung praktik dan lihat hasilnya"),
        ),
    ),
    Question(
        number=13,
        prompt="Kalau mau belajar hal baru, kamu lebih suka yang mana?",
        options=_opts(
            ("A", "Lewat data, grafik, atau penjelasan logis"),
            ("B", "Lewat cerita, kasus nyata, atau pengalaman orang"),
            ("C", "Lewat video tutorial / praktik langsung"),
            ("D", "Lewat diskusi atau tanya-jawab"),
        ),
    ),
    Question(
        number=14,
        prompt="Tantangan seperti apa yang paling menarik buatmu?",
        options=_opts(
            ("A", "Memecahkan masalah yang rumit dan butuh analisis"),
            ("B", "Memahami orang atau fenomena sosial"),
            ("C", "Membuat sesuatu dari nol (produk, desain, sistem)"),
            ("D", "Mengatur dan menjalankan suatu kegiatan/usaha"),
        ),
    ),
    Question(
        number=15,
        prompt="Alasan utama kamu memilih sekolah lanjutan nanti lebih karena…",
        options=_opts(
            ("A", "Ingin mendalami ilmu tertentu secara serius"),
            ("B", "Ingin cepat punya skill yang bisa dipakai kerja"),
            ("C", "Ingin lingkungan yang sesuai sama minat dan kepribadian"),
            ("D", "Masih ikut pertimbangan orang tua / peluang"),
        ),
    ),
    Question(
        number=16,
        prompt="Apa cita-citamu?",
        options=(),
        kind="open_text",
    ),
)


def _validate_questionnaire() -> None:
    numbers = [q.number for q in QUESTIONNAIRE]
    if len(set(numbers)) != len(numbers):
        raise ValueError(f"Duplicate question numbers: {numbers}.")
    if numbers != sorted(numbers):
        raise ValueError(f"Question numbers not sequential: {numbers}.")


_validate_questionnaire()
