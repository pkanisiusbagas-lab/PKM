# Synthetic Survey Pipeline

Generator dataset sintetis kuesioner minat (16 soal: 14 pilihan ganda, 1 slider, 1 isian cita-cita) memakai dua agen LLM: agen persona (bikin profil siswa SMA fiktif) lalu agen responden (menjawab kuesioner sesuai persona).

## Prasyarat

1. Install dependencies: `uv sync`
2. Salin `.env.example` menjadi `.env` lalu isi `OPENCODE_API_KEY`.
3. **Pastikan model yang dipakai bisa diakses key-mu.** Model free-tier (`*-free`, `big-pickle`) diblokir untuk pemanggilan API mentah (`400 MissingSessionID`). Kalau kena error itu, ganti `ZEN_MODEL_PERSONA` / `ZEN_MODEL_RESPONDENT` di `.env` ke model yang accessible.

## Cara Run

```powershell
# Test kecil dulu (5 sampel)
uv run python -m src.synthetic.generator --samples 5 --seed 7 --output data/synthetic/generated/dataset.jsonl

# Run penuh (default 2000 sampel)
uv run python -m src.synthetic.generator --seed 7 --output data/synthetic/generated/dataset.jsonl
```

`--output` menunjuk file JSONL. File CSV turunan dibuat otomatis dengan nama sama (`dataset.csv`). Daftar flag lengkap: `uv run python -m src.synthetic.generator --help`.

## Progress Saat Run

- Bar `Generating: x/y [...]` — persen, estimasi sisa waktu, kecepatan per sampel.
- Baris INFO di awal: jumlah sampel, model persona/responden, concurrency.
- Ringkasan akhir: `Done. Succeeded: N | Failed: M`.

## Kalau Error

- **Key hilang** → pesan jelas + exit `1`, tanpa traceback.
- **Error transient** (koneksi/timeout, 429, 5xx) → retry otomatis dengan backoff, tiap percobaan tercatat (attempt, model, kategori, delay).
- **Error permanen** (misal 400/401) → langsung gagal per sampel, di-retry maksimal 3x di level sampel, sampel lain tetap jalan.
- **Respons model rusak** (bukan JSON / jawaban tidak valid) → retry dengan delay tetap.
- **Gagal total** (nol sampel jadi) → `No samples were created.`, exit `1`.
- **Failure gate** → run diabort kalau tingkat kegagalan melewati `MAX_FAILURE_RATE` setelah `GATE_WARMUP` sampel (lindungi quota).

## Resume

Run yang putus bisa dilanjut dengan perintah yang **sama persis (termasuk `--seed`)** — baris yang sudah jadi dipertahankan, hanya sisanya yang di-generate. Tanpa `--seed` + file output sudah ada = ditolak eksplisit supaya distribusi tidak skew diam-diam. Matikan dengan `--no-resume`.

## Variabel .env

| Variabel | Default | Keterangan |
|---|---|---|
| `OPENCODE_API_KEY` | wajib | API key |
| `ZEN_BASE_URL` | `https://opencode.ai/zen/v1` | Endpoint OpenAI-compatible |
| `ZEN_MODEL_PERSONA` | `big-pickle` | Model agen persona |
| `ZEN_MODEL_RESPONDENT` | `deepseek-v4-flash-free` | Model agen responden |
| `NUM_SAMPLES` | `2000` | Jumlah sampel (maks 100.000) |
| `CONCURRENCY` | `8` | Request paralel (maks 64) |
| `TEMPERATURE` | `1.1` | Temperature sampling |
| `OUTPUT_PATH` | `dataset/peta_arah_minat.jsonl` | Path JSONL (disarankan `--output`) |
| `SEED` | kosong | Seed reproduksibilitas + syarat resume |
| `RESUME` | `true` | Lanjut dari baris existing |
| `MAX_FAILURE_RATE` | `0.5` | Batas abort (0–1) |
| `GATE_WARMUP` | `10` | Sampel sebelum gate aktif |
| `LOG_LEVEL` | `INFO` | Level log |

## Output

- `data/synthetic/generated/dataset.jsonl` — mentahan streaming (1 baris = 1 JSON), basis resume.
- `data/synthetic/generated/dataset.csv` — tabel flat siap modeling (`pd.read_csv` langsung jalan). Field teks bebas sudah disanitasi dari formula-injection spreadsheet.
