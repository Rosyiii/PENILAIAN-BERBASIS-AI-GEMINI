# Sistem Penilaian Tugas Siswa Otomatis (Gemini AI)

Aplikasi berbasis Python untuk melakukan penilaian otomatis pada tugas tulisan tangan siswa (berupa foto/gambar) menggunakan Google Gemini AI. Hasil penilaian berupa skor angka dan evaluasi catatan akan diekstrak secara otomatis ke dalam berkas Microsoft Excel (`rekap_nilai.xlsx`).

---

## 📂 Struktur Repositori

```text
.
├── foto_tugas/               # Folder tempat menyimpan foto tugas siswa (kosong di repo)
├── README.md                 # Dokumentasi dan petunjuk penggunaan
└── sistem_penilaian.py       # Skrip utama penilaian otomatis
```

## 🛠️ Prasyarat & Instalasi

Sebelum menjalankan program, pastikan komputer Anda telah terpasang Python versi 3.10 atau yang lebih baru.

**Clone Repositori**
```bash
git clone https://github.com/Rosyiii/PENILAIAN-BERBASIS-AI-GEMINI.git
cd NAMA_REPO
```

**Instal Library Python**
Jalankan perintah berikut pada Terminal / Command Prompt:
```bash
pip install requests pandas pillow openpyxl
```

## ⚙️ Konfigurasi API Key (Wajib)

Demi keamanan, API Key tidak disertakan di dalam repositori ini.
1. Dapatkan API Key gratis di Google AI Studio.
2. Buka berkas `sistem_penilaian.py` menggunakan text editor (VS Code, Notepad, dll.).
3. Masukkan API Key Anda pada variabel `API_KEY` di baris atas program:

```python
# Masukkan API Key Google AI Studio Anda di sini
API_KEY = "MASUKKAN_API_KEY_ANDA_DI_SINI"
```

## 📁 Format Penamaan File & Folder Foto Tugas

Foto tugas siswa disimpan di dalam folder `foto_tugas/`. Sistem mendukung 2 skema penataan berkas:

### 1. Metode Penamaan Berkas Langsung (Direkomendasikan)
Jika foto tugas siswa diletakkan langsung di dalam folder `foto_tugas/`, **WAJIB** mengikuti format penamaan berikut:

```plaintext
[NAMA siswa] - [id Dokumen] - [Nama dokumen asli].jpg
```

**Format:** Terdapat tanda pemisah jelas berupa strip/garis bawah antarelemen.

**Contoh Penamaan File:**
* `ALEANDRA MIKRAJ SUSANTO - 10293 - lembar_jawaban.jpg`
* `AMABEL LATHISYA PUTRI - 10294 - tugas_manajemen_data.jpeg`
* `ARKA RIZAL MAULANA - 10295 - halaman_1.png`

> Sistem akan membaca bagian paling depan sebelum karakter pemisah sebagai Nama Siswa.

### 2. Metode Sub-Folder (Khusus Multi-Halaman)
Jika 1 siswa mengumpulkan beberapa foto/halaman tugas, buat folder menggunakan nama siswa di dalam `foto_tugas/`:

```plaintext
foto_tugas/
├── ALEANDRA MIKRAJ SUSANTO/
│   ├── lembar1.jpg
│   └── lembar2.jpg
└── AMABEL LATHISYA PUTRI/
    └── tugas.jpg
```

## 🚀 Panduan Penggunaan untuk Admin

1. **Input Foto Tugas:** Masukkan berkas foto tugas siswa ke dalam folder `foto_tugas/` sesuai format penamaan di atas.
2. **Ganti Prompt Perintah AI:** Buka berkas `sistem_penilaian.py` cari `PROMPT_RUBRIK = """` -> ubah semua teks hingga `"""` sesuaikan dengan kriteria penilaian Anda. deskripsikan perintah tugas Anda sedetail mungkin mulai dari **KONSEP, GIMANA CARA MENILAI, BERAPA POIN NILAI YANG MAU DIHASILKAN**. Perlu diingat untuk **TIDAK MERUBAH** narasi berikut: **Berikan output WAJIB dengan format persis seperti ini:**
3. **Jalankan Skrip:** Buka Terminal / CMD di lokasi folder proyek, lalu jalankan:
   ```bash
   python sistem_penilaian.py
   ```
4. **Proses Penilaian:** Sistem akan mendeteksi model Gemini AI aktif, mengompresi gambar, dan menganalisis tugas siswa satu per satu.
5. **Unduh Hasil:** Setelah muncul pesan [SEMUA SELESAI], buka berkas `rekap_nilai.xlsx` yang dibuat otomatis di folder utama.

## 📊 Hasil Rekapitulasi Excel

Hasil luaran `rekap_nilai.xlsx` memiliki struktur tabel berikut:

| Nama Siswa / Folder | Jumlah Halaman | Nilai | Evaluasi Konsep / Catatan |
| :--- | :---: | :---: | :--- |
| ALEANDRA MIKRAJ SUSANTO | 1 | 80 | Penjelasan ringkas, estimasi 210 kata... |
| AMABEL LATHISYA PUTRI | 2 | 100 | Pemahaman konsep tepat, estimasi 250 kata... |

## 🚨 Kendala Umum (Troubleshooting)

* **Error HTTP 429: Quota exceeded:** Kuota panggillan API gratis (Free Tier) pada akun Google Anda telah habis. Dapatkan API Key baru menggunakan akun Gmail lain melalui Google AI Studio.
* **Error Folder './foto_tugas' tidak ditemukan:** Pastikan folder `foto_tugas/` berada di direktori yang sama dengan berkas `sistem_penilaian.py`.
