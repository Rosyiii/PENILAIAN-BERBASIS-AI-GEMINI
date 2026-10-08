# Sistem Penilaian Tugas Siswa Otomatis Berbasis Gemini AI

Aplikasi Python berbasis kecerdasan buatan (Google Gemini API) yang berfungsi untuk melakukan penilaian otomatis pada tugas atau ujian tulisan tangan siswa. Sistem membaca hasil pindaian foto lembar jawaban siswa dan mengevaluasinya berdasarkan acuan materi yang telah disediakan oleh guru.

## 1. Fitur Utama
- **Pemuatan Referensi Otomatis:** Sistem mampu membaca bahan acuan/materi kunci jawaban (maksimal 5 halaman) dari folder `./referensi` untuk dijadikan standar koreksi oleh AI. Sistem juga memiliki mekanisme penanganan (*fallback*) jika folder ini dibiarkan kosong.
- **Pengelompokan Multihalaman:** Menggabungkan lembar jawaban yang terdiri dari banyak foto secara otomatis untuk masing-masing siswa (dikelompokkan berdasarkan nama file di karakter awal sebelum `_`).
- **Batch Processing Cerdas:** Memproses 6–8 siswa sekaligus per satu kali panggilan (request) API. Strategi ini sangat menghemat kuota harian (Request Per Day / RPD) untuk pengguna Gemini API *free-tier*.
- **Ekspor Otomatis ke Excel:** Mengekstrak hasil penilaian dan catatan evaluasi dari AI secara andal menggunakan Regex fleksibel, lalu menyimpannya ke dalam file rekapitulasi `rekap_nilai.xlsx`.

## 2. Alur Program (Workflow)
1. **Inisiasi & Pemuatan Referensi:** Program pertama-tama memuat seluruh gambar di folder `./referensi`, merangkumnya menjadi format Base64, dan mempersiapkannya sebagai landasan penilaian.
2. **Pengelompokan Siswa:** Program memindai folder `./foto_tugas`. Setiap file diekstrak nama siswanya (teks sebelum karakter `_` pertama, contoh: `Budi_1.jpg` dibaca `Budi`). Foto-foto dengan nama siswa yang sama digabungkan ke dalam satu entri penilaian utuh.
3. **Kompresi Gambar:** Setiap gambar di-resize (maksimal dimensi 1024px) dan dikompresi agar pembacaan OCR optimal namun tetap mencegah *error* atau batas maksimal beban memori (*bandwidth*).
4. **Eksekusi API (Batching):** Siswa-siswa dibagi menjadi *batch* (standar: 6 siswa per *batch*). Pada setiap *batch*, program menyatukan dan mengirimkan:
   - *Prompt* Rubrik Penilaian
   - Gambar Bahan Bacaan Acuan (jika ada)
   - Gambar-Gambar Lembar Jawaban Siswa
5. **Parsing & Ekspor Data:** AI mengembalikan teks hasil evaluasi. Program secara pintar mencari potongan teks untuk tiap-tiap siswa lalu merangkumnya menjadi DataFrame yang disimpan ke `rekap_nilai.xlsx`.

## 3. Cara Penggunaan / Cara Menjalankan Kode

### Prasyarat Instalasi
Sebelum menjalankan program, pastikan Python sudah terinstal di komputer Anda (versi 3.8 ke atas direkomendasikan). Cek dengan perintah di Terminal/CMD:
```bash
python --version
```
Jika Anda belum memiliki Python, silakan unduh dan instal dari [python.org](https://www.python.org/).

Selanjutnya, instal pustaka (*library*) pendukung yang dibutuhkan (`requests`, `pandas`, `Pillow`, `openpyxl`). Buka Terminal atau Command Prompt lalu jalankan:
```bash
pip install requests pandas Pillow openpyxl
```

### Konfigurasi API Key
1. Dapatkan API Key secara gratis melalui Google AI Studio: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey).
2. Buka file `sistem_penilaian.py` menggunakan teks editor (misalnya VS Code atau Notepad).
3. Cari baris konfigurasi `API_KEY` (biasanya di bagian atas) dan ubah nilainya menjadi API Key milik Anda:
   ```python
   API_KEY = "MASUKKAN_API_KEY_ANDA_DI_SINI"
   ```

### Aturan Format Nama File Tugas
Masukkan semua foto lembar jawaban siswa ke dalam folder `./foto_tugas`.
Gunakan format penamaan file dengan karakter pemisah *underscore* (`_`) antara "Nama Siswa" dan "Kode Tambahan".
**Contoh yang Benar:**
- `Budi Santoso_lembar1.jpg`
- `Budi Santoso_lembar2.jpg`
- `Siti Aminah_01.jpg`

Sistem akan otomatis mengenali `Budi Santoso` sebagai satu kesatuan siswa yang mengumpulkan 2 lembar jawaban.

### Direktori Bahan Bacaan
Jika Anda memiliki acuan materi atau kunci jawaban, letakkan fotonya ke dalam folder `./referensi` (direkomendasikan tidak lebih dari 5 foto). Jika direktori ini dibiarkan kosong, AI akan merubah metode *prompt*-nya dan menilai esai/jawaban siswa berdasarkan pengetahuan dasar secara umum.

### Menyesuaikan Prompt / Rubrik Penilaian
Guru dapat menyesuaikan standar perolehan skor, kriteria minimal kata, hingga ketegasan penilaian (rubrik).
Buka `sistem_penilaian.py` menggunakan notepad, lalu ubah teks pada variabel `PROMPT_RUBRIK_BATCH` (untuk penilaian dengan acuan) dan `PROMPT_RUBRIK_BATCH_TANPA_REFERENSI` (untuk penilaian tanpa acuan) sesuai dengan kebutuhan pengujian Anda, jangan lupa disimpan filenya kalau sudah selesai mengubah isi file.

### Menjalankan Program
Setelah semua file siap di tempatnya, jalankan program melalui Terminal/Command Prompt di dalam *directory* proyek Anda dengan perintah:
```bash
python sistem_penilaian.py
```
Tunggu hingga semua *batch* selesai dievaluasi, dan hasilnya akan langsung tercetak ke *spreadsheet* Excel.

### Troubleshooting (Pesan Error Umum)
* **Error HTTP 429: Quota exceeded:** Kuota panggilan API gratis (Free Tier) pada akun Google Anda telah habis. Dapatkan API Key baru menggunakan akun Gmail lain melalui Google AI Studio.
* **Error Folder './foto_tugas' tidak ditemukan:** Pastikan folder `foto_tugas/` berada di direktori yang sama dengan berkas `sistem_penilaian.py`.

## 4. Struktur File & Input/Output Data

**Pohon Direktori:**
```text
📦 Proyek Penilaian AI
 ┣ 📂 foto_tugas/           # (Input) Berisi pindaian foto tugas/jawaban siswa (.jpg / .png)
 ┣ 📂 referensi/            # (Input) Berisi acuan materi kunci dari guru (.jpg / .png)
 ┣ 📜 .gitignore            # Pengabaian file yang tidak perlu di-upload (misal: env/excel)
 ┣ 📜 sistem_penilaian.py   # Script / Kode Utama Program
 ┣ 📜 README.md             # Dokumentasi dan panduan ini
 ┗ 📊 rekap_nilai.xlsx      # (Output) File hasil penilaian yang dibuat oleh sistem
```

**Input Data:** 
- Program membaca file gambar dengan format `.jpg`, `.jpeg`, `.png`, atau `.webp`.
- **Catatan Penting:** Pastikan tulisan pada gambar siswa dapat terbaca oleh mata manusia agar AI (Fitur OCR) juga sanggup mendeteksi tulisannya dengan baik.

**Output Data:**
Sistem menghasilkan file `rekap_nilai.xlsx` yang terdiri dari kolom (Header):
1. **Nama Siswa:** Diambil dari ekstraksi otomatis awalan nama file.
2. **Jumlah Halaman:** Banyaknya lampiran lembar jawaban yang diserahkan.
3. **Nilai:** Angka bulat berskala 0 hingga 100.
4. **Evaluasi Konsep / Catatan:** Alasan komprehensif, evaluasi jumlah kata, dan analisis AI perihal pemberian nilai tersebut.
