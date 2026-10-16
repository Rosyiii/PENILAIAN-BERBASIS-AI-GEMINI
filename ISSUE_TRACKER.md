# Issue Tracker: Refactoring Arsitektur Sistem Penilaian

**Status:** Resolved / Completed
**Assignee:** Development Team
**Priority:** High
**Epic:** Arsitektur & Modularisasi v2.0

---

## Deskripsi Umum
Dokumen ini berisi panduan teknis dan tugas (issue) terstruktur untuk melakukan refactoring arsitektur pada aplikasi Sistem Penilaian. Refactoring ini bertujuan untuk meningkatkan keamanan (ekstraksi secret key), fleksibilitas input (mendukung berbagai format dokumen untuk rubrik dan referensi soal), serta memperbarui standar dokumentasi proyek.

> [!WARNING]
> **PERINGATAN KERAS:** Jangan mengubah atau merusak logika inti prompt dari proses penilaian AI (`sistem_penilaian.py`). Fokuslah murni pada restrukturisasi file, ekstraksi konfigurasi variabel, dan penambahan utilitas pembaca file (document parsing).

---

## Issue #1: Pemisahan Konfigurasi ke Berkas `.env` `[COMPLETED]`

**Tujuan:** Memindahkan konfigurasi statis seperti `API_KEY`, konfigurasi path folder, dan variabel lingkungan lainnya dari hardcode di dalam kode sumber menuju file `.env`.

**Daftar File Dampak:**
- `sistem_penilaian.py` (Modifikasi)
- `.env` (Buat Baru - Jangan di-commit!)
- `.env.example` (Buat Baru - Masukkan Git)
- `.gitignore` (Modifikasi)

**Step-by-Step Execution:**
1. Instal package `python-dotenv`: Jalankan perintah `pip install python-dotenv` pada terminal.
2. Buat file bernama `.env` di root direktori proyek dan tambahkan variabel berikut (isi dengan nilai dummy atau kosongan untuk saat ini):
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   FOLDER_JAWABAN=data_jawaban
   FOLDER_HASIL=hasil_penilaian
   FOLDER_PROMPTS=prompts
   FOLDER_REFERENSI=referensi
   ```
3. Buat file bernama `.env.example` sebagai template referensi untuk developer lain tanpa memuat nilai rahasia:
   ```env
   GEMINI_API_KEY=
   FOLDER_JAWABAN=data_jawaban
   FOLDER_HASIL=hasil_penilaian
   FOLDER_PROMPTS=prompts
   FOLDER_REFERENSI=referensi
   ```
4. Modifikasi file `.gitignore` dan pastikan terdapat baris `.env` di dalamnya agar file credential tidak bocor ke repository.
5. Modifikasi `sistem_penilaian.py` untuk menginisialisasi `dotenv`:
   ```python
   import os
   from dotenv import load_dotenv

   # Load environment variables dari file .env
   load_dotenv()

   # Akses konfigurasi menggunakan os.getenv
   API_KEY = os.getenv("GEMINI_API_KEY")
   FOLDER_JAWABAN = os.getenv("FOLDER_JAWABAN", "data_jawaban")
   # ... (Ganti semua path folder hardcode lainnya)
   ```

---

## Issue #2: Implementasi Fungsi Pembaca Rubrik Penilaian (`prompts/`) `[COMPLETED]`

**Tujuan:** Membuat fungsi utilitas untuk membaca file rubrik/prompt yang diletakkan di dalam folder `prompts/`. Fungsi ini wajib mendukung ekstraksi teks murni dari file `.docx`, `.txt`, dan `.md`.

**Daftar File Dampak:**
- `sistem_penilaian.py` atau `utils/document_reader.py` (Disarankan membuat file `utils` baru)
- `prompts/` (Buat foldernya jika belum ada)

**Step-by-Step Execution:**
1. Instal dependensi pengolah dokumen word: `pip install python-docx`.
2. Buat modul utilitas untuk fungsi pembaca, atau tulis langsung fungsinya di dalam script utama. Beri nama fungsi `baca_rubrik(filepath)`.
3. Implementasikan percabangan logika (If/Else) berdasarkan ekstensi file:
   ```python
   import os
   from docx import Document

   def baca_rubrik(filepath: str) -> str:
       """Membaca isi file rubrik dari format txt, md, atau docx."""
       if not os.path.exists(filepath):
           raise FileNotFoundError(f"File rubrik {filepath} tidak ditemukan.")
           
       ext = os.path.splitext(filepath)[1].lower()
       
       if ext in ['.txt', '.md']:
           with open(filepath, 'r', encoding='utf-8') as f:
               return f.read()
       elif ext == '.docx':
           doc = Document(filepath)
           return "\n".join([paragraph.text for paragraph in doc.paragraphs])
       else:
           raise ValueError(f"Format file rubrik {ext} belum didukung.")
   ```
4. Ubah variabel teks rubrik yang masih *hardcoded* di alur utama agar memanggil fungsi ini (membaca file rubrik standar yang diletakkan dalam folder `prompts/`).

---

## Issue #3: Implementasi Pembaca Dokumen Narasi & Referensi Soal (`referensi/`) `[COMPLETED]`

**Tujuan:** Membangun fungsionalitas yang membaca dan memuat konteks dari folder `referensi/`. Sistem harus mampu mengekstrak file soal/narasi tugas berbasis teks (PDF, DOCX, TXT, MD) secara bersamaan dengan memisahkan file gambar/foto acuan (JPG, PNG).

**Daftar File Dampak:**
- `sistem_penilaian.py` atau `utils/document_reader.py`
- `referensi/` (Buat foldernya jika belum ada)

**Step-by-Step Execution:**
1. Instal package pembaca PDF tambahan: `pip install PyPDF2`.
2. Kembangkan fungsi bernama `baca_semua_referensi(folder_path)` yang akan mengiterasi seluruh file di dalam folder `referensi/`.
3. Return value dari fungsi ini disarankan dalam bentuk struktur *dictionary* atau tuple yang memisahkan antara teks dan daftar path gambar:
   ```python
   import os
   import PyPDF2
   from docx import Document

   def baca_semua_referensi(folder_path: str) -> dict:
       """Membaca narasi dan foto referensi soal dari suatu folder."""
       referensi_teks = []
       referensi_gambar = []
       
       if not os.path.exists(folder_path):
           return {"teks": "", "gambar": []}
           
       for filename in os.listdir(folder_path):
           filepath = os.path.join(folder_path, filename)
           ext = os.path.splitext(filename)[1].lower()
           
           try:
               if ext in ['.txt', '.md']:
                   with open(filepath, 'r', encoding='utf-8') as f:
                       referensi_teks.append(f.read())
               elif ext == '.docx':
                   doc = Document(filepath)
                   referensi_teks.append("\n".join([p.text for p in doc.paragraphs]))
               elif ext == '.pdf':
                   with open(filepath, 'rb') as f:
                       reader = PyPDF2.PdfReader(f)
                       teks_pdf = "".join([page.extract_text() or "" for page in reader.pages])
                       referensi_teks.append(teks_pdf)
               elif ext in ['.jpg', '.jpeg', '.png', '.webp']:
                   referensi_gambar.append(filepath) # Hanya simpan path, gambar diproses oleh API Gemini nanti
           except Exception as e:
               print(f"Warning: Gagal membaca file referensi {filename}: {e}")
               
       return {
           "teks": "\n\n--- [Batas Referensi] ---\n\n".join(referensi_teks),
           "gambar": referensi_gambar
       }
   ```
4. Injeksi variabel yang berisi `"teks"` dari return fungsi ini ke dalam *prompt input* Gemini. Begitu juga, muat gambar-gambar dari list `"gambar"` agar dikirim sebagai part payload ke Gemini AI (mendampingi foto jawaban siswa).

---

## Issue #4: Pembaruan Dependensi & Restrukturisasi `README.md` `[COMPLETED]`

**Tujuan:** Memperbarui _environment_ list (`requirements.txt`) dengan module tambahan dan membakukan dokumentasi proyek.

**Daftar File Dampak:**
- `requirements.txt` (Modifikasi/Buat Baru)
- `README.md` (Modifikasi)

**Step-by-Step Execution:**
1. Jalankan kembali pencatatan library via `pip freeze > requirements.txt` ATAU secara manual pastikan package berikut ada dalam `requirements.txt`:
   ```text
   google-generativeai
   python-dotenv
   python-docx
   PyPDF2
   ```
2. Buka `README.md` dan strukturkan ulang menjadi format standar profesional berikut:
   - **Judul Proyek & Deskripsi Singkat:** Penjelasan Sistem Penilaian Jawaban Otomatis menggunakan Gemini AI.
   - **Fitur Utama:** Sebutkan dukungan multi-format (TXT, MD, DOCX, PDF) serta kemampuan memisahkan rubrik dan soal referensi.
   - **Prerequisites (Prasyarat):** Versi Python yang digunakan (misal: Python 3.9+) & Akun Google AI Studio untuk API Key.
   - **Instalasi:**
     ```bash
     git clone <url-repo>
     cd <nama-folder>
     pip install -r requirements.txt
     ```
   - **Konfigurasi Lingkungan (.env):** Panduan agar *user* menyalin `.env.example` menjadi `.env` dan mengisi API Key-nya.
   - **Struktur Direktori:** Visualisasikan arsitektur folder terbaru (berdasarkan Issue 1-3). Contoh:
     ```text
     ├── data_jawaban/   # Tempat meletakkan foto/file jawaban siswa
     ├── hasil_penilaian/# Output hasil dari proses penilaian AI
     ├── prompts/        # Tempat menyimpan file rubrik kriteria (.txt/.md/.docx)
     ├── referensi/      # Tempat menyimpan narasi soal & gambar acuan
     ├── .env            # Konfigurasi kredensial (Local Only)
     └── sistem_penilaian.py
     ```
   - **Cara Penggunaan:** Step-by-step menaruh dokumen input di masing-masing folder lalu mengeksekusi `python sistem_penilaian.py`.
3. Lakukan **Commit & Push** keseluruhan perubahan arsitektur ini ke remote repository dengan deskripsi PR yang representatif.
