# 📋 LAPORAN ANALISIS & CETAK BIRU REVISI INSTRUMEN ASESMEN
## Platform "Peta Arah Minat" untuk Penjurusan Siswa SMP ke SMA & SMK
**Dokumen:** Analisis Validitas Konten & Penyesuaian Taksonomi Peminatan  
**Target Pengguna:** Siswa Sekolah Menengah Pertama (SMP) Usia 12–15 Tahun  
**Konteks Kurikulum:** Transisi Menuju SMA (Peminatan MIPA / IPS) & SMK (Program Keahlian Umum di Indonesia)

---

## 1. Ringkasan Eksekutif (Executive Summary)

Instrumen awal kuis "Peta Arah Minat" dirancang dengan pendekatan gamifikasi yang sangat ramah siswa (*friendly, non-intimidating*). Namun, dari sudut pandang **psikometri dan bimbingan karier (BK)**, instrumen 11 soal awal **belum cukup representatif** jika ditujukan secara spesifik untuk membedakan kelayakan siswa masuk ke **SMA (MIPA vs. IPS)** atau **SMK (Rumpun Vokasi Nasional)**.

### Temuan Utama:
1. **Defisit Bobot Penjurusan:** Dari 11 pertanyaan awal, hanya 4–5 soal yang menyumbang skor determinatif terhadap bidang minat. Sisanya bersifat refleksi konseling kualitatif yang netral terhadap pilihan jurusan.
2. **Ketiadaan Pembeda Karakter Belajar SMA vs. SMK:** Pilihan SMA vs. SMK bukan sekadar perbedaan mata pelajaran, melainkan perbedaan **orientasi masa depan (akademis jangka panjang vs. kesiapan kerja/vokasi)** dan **gaya belajar (konseptual-analitis vs. aplikatif-kinestetik)**.
3. **Bias Rumpun Teknologi & Kreatif Digital:** Rumpun jurusan SMK terbesar di Indonesia seperti **Teknik Otomotif, Teknik Pengelasan/Mesin, Bisnis Daring & Akuntansi, serta Tata Boga/Perhotelan** belum terwakili secara adil dalam opsi pilihan.

---

## 2. Audit Kritis 11 Pertanyaan Awal

Berikut adalah evaluasi per butir soal awal terhadap daya pembeda (*discriminating power*) penjurusan:

| No | Pertanyaan Eksisting | Tipe Output | Kontribusi Skor Penjurusan | Evaluasi & Kelemahan |
| :---: | :--- | :---: | :---: | :--- |
| **Q1** | Kondisi kesiapan jurusan saat ini | Diagnostik | Rendah (0%) | Bagus untuk konseling awal, tetapi tidak menentukan kecocokan jurusan. |
| **Q2** | Mapel yang paling disukai | Skoring | **Sangat Tinggi (25%)** | Sangat efektif memetakan dasar MIPA, IPS, atau Seni. |
| **Q3** | Mapel yang paling tidak disukai | Eliminasi | **Tinggi (15%)** | Efektif sebagai filter negatif (*negative weighting*). |
| **Q4** | Aktivitas waktu luang | Skoring | **Tinggi (15%)** | Membantu, tetapi opsinya terlalu condong ke koding, sains, dan konten medsos. |
| **Q5** | Preferensi jenis pekerjaan | Skoring | **Tinggi (15%)** | Bagus untuk membedakan kepemimpinan, riset, kreasi, dan teknologi. |
| **Q6** | Esai cita-cita karier | Kualitatif | Rendah (0% otomatis) | Membutuhkan model NLP/AI terpisah untuk diubah menjadi skor angka. |
| **Q7** | Faktor kebingungan memilih | Reflektif | Rendah (0%) | Analisis hambatan mental/sosial siswa, bukan alat ukur kompetensi. |
| **Q8** | Minat lain di luar mapel | Skoring | **Sedang (10%)** | Terlalu banyak tumpang tindih (*redundant*) dengan Q4 dan Q5. |
| **Q9** | Pengalaman salah jurusan/ekskul | Reflektif | Rendah (0%) | Tidak menyumbang arah jurusan baru. |
| **Q10** | Slider keyakinan (1–10) | Metrik | Rendah (0%) | Hanya mengukur tingkat *self-efficacy* (kepercayaan diri siswa). |
| **Q11** | Pengaruh lingkungan keputusan | Sosial | Rendah (0%) | Mengukur locus of control (pengaruh orang tua vs internal). |

> **Kesimpulan Audit:** Hanya **~65% instrumen** yang bekerja sebagai penentu minat, dan **0% instrumen** yang mengukur kesiapan mentalitas belajar vokasi (SMK) vs akademis murni (SMA).

---

## 3. Formulasi Baru: 10 Pertanyaan Emas Penjurusan SMA / SMK

Untuk menjaga agar kuis tetap ringkas (maksimal 10 soal), seru, dan dapat dihitung otomatis secara presisi oleh sistem scoring, berikut adalah restrukturisasi 10 soal yang telah disesuaikan dengan spektrum pendidikan menengah di Indonesia:

### 🧩 [Pertanyaan 1] Gaya Belajar Dominan *(Pemilah Utama: SMA vs. SMK)*
* **Teks Soal:** "Kalau disuruh memilih cara belajar seharian penuh di sekolah, mana yang paling bikin kamu bersemangat dan tidak cepat bosan?"
* **Pilihan Jawaban:**
  * `A` Membaca literatur, berdiskusi teori/ide, dan menganalisis konsep mendalam. $\rightarrow$ `[SMA: +3, SMK: +0]`
  * `B` Praktik langsung merakit, mengoperasikan alat, mencoba software, atau memasak produk nyata. $\rightarrow$ `[SMA: +0, SMK: +3]`
  * `C` Seimbang antara mendengarkan penjelasan guru lalu mencoba latihannya secara mandiri. $\rightarrow$ `[SMA: +2, SMK: +2]`

---

### 🧩 [Pertanyaan 2] Mata Pelajaran Favorit *(Rumpun Dasar Akademis)*
* **Teks Soal:** "Mata pelajaran sekolah apa yang paling membuatmu bersemangat saat jam pelajarannya tiba?"
* **Pilihan Jawaban:**
  * `A` Matematika atau IPA (Fisika/Biologi) $\rightarrow$ `[SMA MIPA: +3, SMK Teknik/TI: +2]`
  * `B` IPS (Ekonomi/Geografi/Sosiologi) atau Bahasa $\rightarrow$ `[SMA IPS: +3, SMK Bisnis: +2]`
  * `C` Informatika / Komputer $\rightarrow$ `[SMK TI: +3, SMA MIPA: +2]`
  * `D` Prakarya, Seni Rupa, atau Keterampilan Tangan $\rightarrow$ `[SMK Industri Kreatif/Boga: +3]`
  * `E` Pendidikan Jasmani & Olahraga (PJOK) $\rightarrow$ `[SMA IPS: +1, SMK Lapangan: +2]`

---

### 🧩 [Pertanyaan 3] Mata Pelajaran yang Paling Dihindari *(Filter Eliminasi)*
* **Teks Soal:** "Mata pelajaran apa yang paling sering membuat energimu terkuras atau cepat merasa jenuh?"
* **Pilihan Jawaban:**
  * `A` Hitungan rumit, rumus hafalan, dan kalkulasi angka $\rightarrow$ `[MIPA: -3, Teknik: -2]`
  * `B` Hafalan materi bacaan panjang, sejarah, dan esai teks $\rightarrow$ `[IPS: -3, Bisnis: -1]`
  * `C` Koding logika atau instruksi komputer detail $\rightarrow$ `[TI: -3]`
  * `D` Menggambar manual, membuat kerajinan, atau kegiatan artistik $\rightarrow$ `[Desain/Seni: -3]`
  * `E` Praktik fisik atau membongkar barang kotor $\rightarrow$ `[Teknik Otomotif/Mesin: -3]`

---

### 🧩 [Pertanyaan 4] Eksplorasi Waktu Luang *(Minat Otentik / Hobi)*
* **Teks Soal:** "Saat akhir pekan atau hari libur tanpa tugas sekolah, aktivitas apa yang paling sering membuatmu lupa waktu?"
* **Pilihan Jawaban:**
  * `A` Mencoba koding software, mengedit video, bermain game PC/konsol $\rightarrow$ `[SMK TI / DKV: +3]`
  * `B` Menonton dokumenter sains, membaca ensiklopedia, eksplorasi fenomena alam $\rightarrow$ `[SMA MIPA: +3]`
  * `C` Menonton konten analisis kasus sosial, isu ekonomi, hukum, atau membaca novel $\rightarrow$ `[SMA IPS: +3]`
  * `D` Mengutak-atik mesin motor/sepeda, merakit kabel, atau memperbaiki perkakas rumah $\rightarrow$ `[SMK Otomotif/Mesin/Elektro: +3]`
  * `E` Menjual barang, dropship, memikirkan ide jualan, merapikan catatan uang saku $\rightarrow$ `[SMK Bisnis & Pemasaran/Akuntansi: +3]`
  * `F` Memasak di dapur, mencoba resep kue baru, menata ruangan atau fashion $\rightarrow$ `[SMK Tata Boga/Perhotelan/Tata Busana: +3]`

---

### 🧩 [Pertanyaan 5] Problem-Solving Challenge *(Pendekatan Solusi Masalah)*
* **Teks Soal:** "Jika di lingkunganmu ada masalah banjir sampah, cara mana yang paling terlintas pertama kali di pikiranmu untuk membantunya?"
* **Pilihan Jawaban:**
  * `A` Meneliti komposisi kimia sampah dan mencari solusi daur ulang biologis. $\rightarrow$ `[SMA MIPA: +3]`
  * `B` Mengedukasi warga, membuat kampanye sosial, dan merancang aturan hukumnya. $\rightarrow$ `[SMA IPS: +3]`
  * `C` Merancang aplikasi penjemputan sampah digital berbasis GPS & IoT. $\rightarrow$ `[SMK TI: +3]`
  * `D` Merakit mesin pencacah plastik otomatis menggunakan dinamo dan motor penggerak. $\rightarrow$ `[SMK Teknik Mesin/Listrik: +3]`
  * `E` Mengolah sampah menjadi produk bernilai jual tinggi dan memasarkannya ke marketplace. $\rightarrow$ `[SMK Bisnis/Kreatif: +3]`

---

### 🧩 [Pertanyaan 6] Rencana Pasca Kelulusan *(Orientasi Masa Depan)*
* **Teks Soal:** "Saat membayangkan dirimu di usia 18 tahun (setelah lulus sekolah menengah nanti), apa target utamamu?"
* **Pilihan Jawaban:**
  * `A` Fokus kuliah penuh (S1/D4) di universitas impian untuk mengejar gelar akademis tinggi. $\rightarrow$ `[SMA: +3, SMK: +0]`
  * `B` Langsung bekerja atau membuka usaha sendiri karena ingin mandiri secara finansial. $\rightarrow$ `[SMK: +3, SMA: +0]`
  * `C` Ingin bekerja sambil kuliah malam/jarak jauh dengan uang penghasilan sendiri. $\rightarrow$ `[SMK: +2, SMA: +1]`
  * `D` Masih fleksibel, ingin memperkuat teori sains/sosial sebelum menentukan spesialisasi. $\rightarrow$ `[SMA: +3, SMK: +0]`

---

### 🧩 [Pertanyaan 7] Preferensi Lingkungan Kerja Masa Depan
* **Teks Soal:** "Lingkungan kerja seperti apa yang paling membuatmu merasa nyaman dan produktif?"
* **Pilihan Jawaban:**
  * `A` Laboratorium riset, rumah sakit klinis, atau ruang observasi sains $\rightarrow$ `[SMA MIPA: +3]`
  * `B` Ruang sidang hukum, lembaga riset kebijakan publik, media massa, perbankan $\rightarrow$ `[SMA IPS: +3]`
  * `C` Studio software, tech startup, ruang kerja digital dengan komputer spesifikasi tinggi $\rightarrow$ `[SMK TI: +3]`
  * `D` Bengkel modern, area konstruksi proyek, pabrik industri perakitan $\rightarrow$ `[SMK Teknik Rekayasa: +3]`
  * `E` Kantor administrasi perusahaan, perbankan akuntansi, atau ritel bisnis $\rightarrow$ `[SMK Manajemen Bisnis: +3]`
  * `F` Restoran, hotel berbintang, dapur *bakery*, atau industri pariwisata $\rightarrow$ `[SMK Pariwisata/Boga: +3]`

---

### 🧩 [Pertanyaan 8] Peran dalam Tim Kerja Kolaboratif
* **Teks Soal:** "Saat mengerjakan tugas kelompok di sekolah, kamu paling nyaman memegang peran sebagai apa?"
* **Pilihan Jawaban:**
  * `A` Penemu data akurat, perancang logika, dan pemecah kebuntuan rumus $\rightarrow$ `[MIPA / Teknik: +2]`
  * `B` Pengatur pembagian tugas, pencatat alur kerja, dan pengontrol anggaran $\rightarrow$ `[IPS / Bisnis: +2]`
  * `C` Pembuat presentasi visual, desainer poster materi, atau pembuat slide estetis $\rightarrow$ `[TI / DKV / Seni: +2]`
  * `D` Juru bicara/presenter yang menyampaikan ide dengan percaya diri di depan kelas $\rightarrow$ `[IPS / Pariwisata: +2]`
  * `E` Eksekutor teknis perakitan bahan dan pencetak output fisik tugas $\rightarrow$ `[SMK Vokasi: +2]`

---

### 🧩 [Pertanyaan 9] Minat Spesifik Terapan Vokasional *(Saringan Khusus SMK)*
* **Teks Soal:** "Jika kamu diwajibkan memilih salah satu keahlian terapan di bawah ini, mana yang paling ingin kamu kuasai?"
* **Pilihan Jawaban:**
  * `A` Membangun aplikasi smartphone, mengelola jaringan server, atau membuat website $\rightarrow$ `[SMK TI (RPL/TKJ)]`
  * `B` Memperbaiki kelistrikan kendaraan, servis mesin motor/mobil, atau pengelasan presisi $\rightarrow$ `[SMK Teknik Mesin/Otomotif]`
  * `C` Menyusun laporan keuangan pembukuan, perpajakan, dan administrasi perkantoran digital $\rightarrow$ `[SMK Akuntansi/MPLB]`
  * `D` Seni meracik kuliner nusantara/internasional, pastry cake, dan hospitality perhotelan $\rightarrow$ `[SMK Tata Boga/Perhotelan]`
  * `E` Ilustrasi karakter 2D/3D, fotografi, sinematografi, dan desain grafis periklanan $\rightarrow$ `[SMK DKV / Animasi]`
  * `F` Lebih tertarik teori ilmu murni daripada spesialisasi keahlian terapan di atas $\rightarrow$ `[Fokus SMA MIPA/IPS]`

---

### 🧩 [Pertanyaan 10] Tingkat Keyakinan Diri *(Slider Gamifikasi 1–10)*
* **Teks Soal:** "Seberapa yakin kamu bahwa kamu sudah siap mengambil keputusan sekolah lanjutanmu?"
* **Format:** Slider interaktif dari 1 (*Sangat Ragu*) sampai 10 (*Sangat Mantap*).
* **Fungsi Sistem:** Mengukur *decision readiness score* untuk ditampilkan pada ringkasan konseling di dashboard hasil.

---

## 4. Matriks Pemetaan Jurusan di Indonesia

Berdasarkan 10 pertanyaan di atas, sistem akan mengelompokkan siswa ke dalam **7 Klaster Pendidikan Lanjutan Nasional**:



                                   HASIL SKOR SISWA
                                         │
               ┌─────────────────────────┴─────────────────────────┐
               ▼                                                   ▼
        JALUR SMA (AKADEMIK)                                JALUR SMK (VOKASI)
(Fokus Teori, Konsep, & Riset S1)                   (Fokus Skill Kerja, Praktik, & Portofolio)
               │                                                   │
     ┌─────────┴─────────┐                  ┌──────────────┬───────┴──────┬──────────────┐
     ▼                   ▼                  ▼              ▼              ▼              ▼
 SMA MIPA             SMA IPS             SMK TI         SMK TEKNIK    SMK BISNIS    SMK PARIWISATA


### Panduan Karakteristik 7 Klaster:

1. **SMA Rumpun MIPA (Matematika & Ilmu Pengetahuan Alam)**
   * *Profil:* Menyukai abstraksi rumus, logika matematis, cara kerja alam dan teknologi ilmiah.
   * *Prospek Studi Lanjutan:* Kedokteran, Ilmu Komputer, Farmasi, Teknik Sipil/Elektro/Mesin (S1), Statistika, Bioteknologi.
2. **SMA Rumpun IPS (Ilmu Pengetahuan Sosial)**
   * *Profil:* Menyukai interaksi sosial, dinamika pasar/uang, sejarah peradaban, bahasa, komunikasi, dan hukum.
   * *Prospek Studi Lanjutan:* Manajemen Bisnis, Ilmu Hukum, Psikologi, Hubungan Internasional, Ilmu Komunikasi, Akuntansi (S1).
3. **SMK Rumpun Teknologi Informasi (TI / DKV)**
   * *Konsentrasi Populer:* Rekayasa Perangkat Lunak (RPL), Teknik Komputer & Jaringan (TKJ), Desain Komunikasi Visual (DKV).
   * *Karakter:* Tertarik logika digital, software, desain visual modern, dan ekosistem internet.
4. **SMK Rumpun Teknik & Rekayasa**
   * *Konsentrasi Populer:* Teknik Kendaraan Ringan (TKR), Teknik Sepeda Motor (TSM), Teknik Pengelasan, Teknik Instalasi Tenaga Listrik (TITL).
   * *Karakter:* Kinestetik tinggi, senang perkakas mesin, perbaikan otomotif, dan rekayasa fisik.
5. **SMK Rumpun Bisnis & Manajemen**
   * *Konsentrasi Populer:* Akuntansi & Keuangan Lembaga (AKL), Manajemen Perkantoran & Layanan Bisnis (MPLB), Pemasaran Retail.
   * *Karakter:* Rapi, terorganisir, teliti dengan uang/catatan, senang melayani pelanggan, dan tertarik wirausaha.
6. **SMK Rumpun Pariwisata & Kuliner**
   * *Konsentrasi Populer:* Kuliner (Tata Boga), Perhotelan, Tata Kecantikan, Tata Busana.
   * *Karakter:* Kreatif aplikatif, hospitality tinggi, gemar meracik produk pangan/layanan keramahan tamu.
7. **SMK Rumpun Seni & Industri Kreatif**
   * *Konsentrasi Populer:* Seni Kriya, Animasi 3D, Desain Interior.
   * *Karakter:* Ekspresif, imajinasi visual kuat, dan tekun menciptakan karya otentik.

---

## 5. Algoritma Perhitungan Skor (Pseudocode Logic)

Berikut adalah logika pemrograman sederhana yang dapat langsung diterapkan pada modul kalkulasi frontend (React / Next.js):

```javascript
// Struktur awal skor penampung
const scores = {
  sma_mipa: 0,
  sma_ips: 0,
  smk_ti: 0,
  smk_teknik: 0,
  smk_bisnis: 0,
  smk_pariwisata: 0,
  smk_seni: 0
};

// Parameter Bobot Utama:
// Q1: Gaya Belajar (SMA vs SMK Weighting)
// Q2: Mapel Favorit
// Q3: Mapel Dihindari (Negative Deduction)
// Q4: Hobi Luang
// Q5: Problem Solving
// Q6: Orientasi Pasca Lulus (SMA vs SMK Weighting)
// Q7: Lingkungan Kerja Idaman
// Q8: Peran Tim
// Q9: Spesialisasi Terapan Vokasi

function calculateRecommendation(answers) {
  // 1. Akumulasi Skor dari Jawaban Siswa
  answers.forEach((ans) => {
    Object.keys(ans.weights).forEach((key) => {
      scores[key] += ans.weights[key];
    });
  });

  // 2. Normalisasi Skor Tertinggi
  const sortedClusters = Object.entries(scores).sort((a, b) => b[1] - a[1]);
  const primaryMatch = sortedClusters[0];   // Rekomendasi No. 1
  const secondaryMatch = sortedClusters[1]; // Rekomendasi No. 2

  // 3. Klasifikasi Induk Jalur (SMA vs SMK Index)
  const smaTotal = scores.sma_mipa + scores.sma_ips;
  const smkTotal = scores.smk_ti + scores.smk_teknik + scores.smk_bisnis + scores.smk_pariwisata + scores.smk_seni;
  
  const recommendedTrack = smaTotal >= smkTotal ? "SMA (Jalur Akademik)" : "SMK (Jalur Vokasi Terapan)";

  return {
    recommendedTrack,
    primaryCluster: primaryMatch[0],
    primaryScore: primaryMatch[1],
    secondaryCluster: secondaryMatch[0],
    secondaryScore: secondaryMatch[1]
  };
}