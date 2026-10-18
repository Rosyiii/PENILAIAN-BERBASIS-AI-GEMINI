# Panduan Praktis Menulis Rubrik Penilaian untuk Guru & Pengguna

Dokumen ini disusun untuk memudahkan guru dan pengguna awam dalam menyesuaikan kriteria penilaian AI agar hasilnya **100% akurat sesuai harapan** tanpa membuat sistem error.

---

## 🌟 TRIK PRAKTIS 5 DETIK: Bikin Rubrik Tanpa Pusing (Pakai Gemini Web)

Banyak guru atau pengguna merasa bingung dan ragu ketika harus merangkai kata-kata prompt sendiri. **Anda TIDAK PERLU menulis prompt dari nol!** Kami telah menyiapkan trik 2-file yang sangat mudah:

### Konsep 2 Jenis File:
1. **File Template Copas Gemini Web** (Untuk bikin prompt otomatis):
   - [TEMPLATE_COPAS_GEMINI_WEB_DENGAN_REFERENSI.md](file:///c:/Users/aster/Downloads/Penilaian%20Test/prompts/TEMPLATE_COPAS_GEMINI_WEB_DENGAN_REFERENSI.md)
   - [TEMPLATE_COPAS_GEMINI_WEB_TANPA_REFERENSI.md](file:///c:/Users/aster/Downloads/Penilaian%20Test/prompts/TEMPLATE_COPAS_GEMINI_WEB_TANPA_REFERENSI.md)
2. **Berkas Running Sistem** (Yang dibaca oleh program saat penilaian berjalan):
   - [rubrik_dengan_referensi.md](file:///c:/Users/aster/Downloads/Penilaian%20Test/prompts/rubrik_dengan_referensi.md)
   - [rubrik_tanpa_referensi.md](file:///c:/Users/aster/Downloads/Penilaian%20Test/prompts/rubrik_tanpa_referensi.md)

### Alur Langkah Praktis (Hanya 4 Langkah):
1. **Buka File Template Copas:**  
   Pilih salah satu file template copas di atas sesuai kebutuhan Anda (apakah ada bahan referensi/kunci jawaban di folder `referensi/` atau tidak). Salin (*copy*) seluruh teks yang ada di dalamnya.
2. **Buka Gemini di Browser:**  
   Buka Google Gemini di browser Anda: [https://gemini.google.com](https://gemini.google.com).
3. **Tempel Prompt & Lampirkan Foto:**  
   Tempel (*paste*) teks yang sudah Anda salin ke kolom chat Gemini, lalu lampirkan foto lembar soal / tugas / kunci jawaban Anda, lalu tekan **Kirim / Enter**.
4. **Salin Balasan & Timpa ke Berkas Running:**  
   Gemini Web akan membuatkan rubrik terstruktur rapi yang sudah disesuaikan persis dengan foto soal Anda. Salin teks balasan tersebut, lalu buka berkas running yang sesuai (`rubrik_dengan_referensi.md` atau `rubrik_tanpa_referensi.md`), lalu timpa (*paste*) isinya.
5. **Jalankan Program:**  
   Tinggal ketik perintah di terminal: `python sistem_penilaian.py` ("oiii jalankan programnya!"). Sistem akan mengeksekusi penilaian dengan presisi tinggi!

---

## 1. Aturan Dasar: Mana yang Boleh Diubah & Mana yang DILARANG?

| Bagian Prompt | Boleh Diubah? | Penjelasan |
| :--- | :---: | :--- |
| **Deskripsi Tugas Siswa** | **YA (Bebas)** | Jelaskan kepada AI apa yang dikerjakan murid (latihan 10 soal, esai 200 kata, rangkuman, dll.). |
| **Peran Folder Referensi** | **YA (Bebas)** | Beritahu AI apa isi folder `referensi/` (apakah kunci jawaban, lembar soal, atau bahan bacaan materi). |
| **Rubrik & Bobot Nilai** | **YA (Bebas)** | Tentukan pembagian poin sesuka hati Anda. Pastikan total nilai maksimal adalah **100**. |
| **Petunjuk Khusus AI** | **YA (Bebas)** | Tambahkan instruksi seperti toleransi tulisan tangan, rumus yang diperbolehkan, dsb. |
| **Format Output Sistem** | ⛔ **DILARANG DIUBAH** | **JANGAN UBAH** format `---SISWA: [Nama Siswa]---`, `NILAI: [Angka]`, dan `CATATAN: [Teks]`. Format ini wajib persis karena dibaca oleh kode Python untuk dimasukkan ke file Excel `rekap_nilai.xlsx`. |

---

## 2. Cara Kerja Folder `referensi/`

Folder `referensi/` sangat fleksibel dan dapat digunakan untuk berbagai keperluan:

1. **Sebagai Kunci Jawaban Resmi / Pembahasan:**
   * Masukkan foto atau PDF kunci jawaban ke folder `referensi/`.
   * Di dalam file `prompts/rubrik_dengan_referensi.md`, tuliskan:  
     *"Berkas di folder referensi adalah kunci jawaban resmi. Cocokkan jawaban siswa dengan kunci tersebut."*

2. **Sebagai Lembar Soal Resmi:**
   * Jika pada lembar tugas siswa hanya tertulis nomor dan jawaban tanpa teks soal, masukkan file soal ke `referensi/`.
   * Di prompt tuliskan:  
     *"Berkas di folder referensi adalah lembar soal ulangan. Periksa apakah jawaban siswa menjawab pertanyaan pada soal tersebut."*

3. **Sebagai Materi Bacaan / Buku Acuan:**
   * Masukkan materi teori atau bahan ajar ke `referensi/`.
   * Di prompt tuliskan:  
     *"Bahan di folder referensi adalah materi acuan. Nilai apakah siswa memahami dan menerapkan konsep dari materi tersebut."*

---

## 3. Contoh Template Rubrik untuk Berbagai Tipe Tugas

### Contoh A: Tugas Hitungan Eksakta (Matematika / Fisika / Kimia)
```markdown
BAGIAN 1: DESKRIPSI TUGAS SISWA
Siswa mengerjakan 5 soal hitungan fisika pada lembar tugas masing-masing.

BAGIAN 2: RUBRIK DAN PEDOMAN NILAI
Total skor maksimal: 100 poin (Tiap soal berbobot 20 poin).
Untuk setiap nomor soal:
1. Menuliskan Diketahui dan Ditanya: 5 poin
2. Menuliskan Rumus yang benar: 5 poin
3. Langkah perhitungan runtut: 5 poin
4. Hasil akhir dan satuan benar: 5 poin
Jika salah hitung tapi rumus benar: berikan 10 poin.
```

### Contoh B: Tugas Esai / Karangan (Bahasa Indonesia / Sejarah / PKn)
```markdown
BAGIAN 1: DESKRIPSI TUGAS SISWA
Siswa membuat esai minimal 200 kata dengan tema "Pentingnya Menjaga Privasi Data Digital".

BAGIAN 2: RUBRIK DAN PEDOMAN NILAI
Total skor maksimal: 100 poin:
1. Panjang Tulisan: Minimal 200 kata mendapatkan 40 poin dasar (kurang dari 200 kata dapat 25 poin).
2. Kesesuaian dengan Tema: Hingga 30 poin jika membahas perlindungan data pribadi dan dampaknya.
3. Struktur & Bahasa: Hingga 20 poin untuk kerapian alur kalimat dan penggunaan bahasa yang baik.
4. Nama Terang: 10 poin jika menuliskan nama jelas di bagian atas lembar kertas.
```

### Contoh C: Tugas Tanya-Jawab Uraian Pendek (Informatika / Biologi / Teori)
```markdown
BAGIAN 1: DESKRIPSI TUGAS SISWA
Siswa menjawab 10 pertanyaan uraian singkat bab Struktur Jaringan Komputer.

BAGIAN 2: PERAN BAHAN REFERENSI
Berkas di folder referensi adalah Kunci Jawaban Soal 1-10.

BAGIAN 3: RUBRIK DAN PEDOMAN NILAI
Total nilai maksimal: 100 poin (10 poin per nomor).
- Jawaban sesuai kata kunci di kunci jawaban: 10 poin per nomor.
- Jawaban mendekati atau menggunakan bahasa sendiri tapi maknanya benar: 7-8 poin.
- Jawaban tidak tepat atau kosong: 0 poin.
```

---

## 4. Bagaimana Urutan Halaman Ditentukan oleh Sistem? (Penting!)

Banyak pengguna bertanya: *"Bagaimana sistem tahu foto mana yang menjadi Halaman 1, Halaman 2, dst?"*

### Prinsip Pengurutan: Alfabetis / Nomor Nama Berkas (Alphabetical Sorting)
Sistem membaca dan mengurutkan berkas secara otomatis **berdasarkan nama file secara berurutan (abjad & angka)**:

1. **Pada Mode Per Folder (`foto_tugas/Kelas/Nama/`):**
   Beri nama foto di dalam folder siswa dengan angka atau nomor halaman yang jelas:
   * `1.jpg` atau `hal1.jpg` $\rightarrow$ **Otomatis menjadi Halaman 1**
   * `2.jpg` atau `hal2.jpg` $\rightarrow$ **Otomatis menjadi Halaman 2**
   * `3.jpg` atau `hal3.jpg` $\rightarrow$ **Otomatis menjadi Halaman 3**  
   *(Tips: Jika halaman mencapai belasan, gunakan format 2 digit seperti `01.jpg`, `02.jpg`, dst).*

2. **Pada Mode Per File (`foto_tugas/` langsung):**
   Sertakan urutan halaman setelah nama siswa:
   * `Ahmad Pratama_01.jpg` $\rightarrow$ **Halaman 1**
   * `Ahmad Pratama_02.jpg` $\rightarrow$ **Halaman 2**

3. **Urutan Berkas di Folder `referensi/`:**
   Sama halnya dengan lembar tugas siswa, berkas di folder referensi dibaca sesuai abjad nama file:
   * `01_lembar_soal.pdf` $\rightarrow$ dibaca pertama
   * `02_kunci_hal1.jpg` $\rightarrow$ dibaca kedua
   * `03_kunci_hal2.jpg` $\rightarrow$ dibaca ketiga

### Urutan Kronologis Bundel yang Diterima AI:
Ketika sistem mengirimkan data ke Google Gemini, susunan yang diterima AI adalah layaknya membuka map jilid:
1. **Urutan 1:** Seluruh Teks Rubrik Penilaian (Aturan & bobot nilai Anda).
2. **Urutan 2:** Bahan Acuan di Folder `referensi/` (Kunci jawaban / soal resmi, jika ada).
3. **Urutan 3:** Lembar Tugas Siswa Pertama (Header Identitas $\rightarrow$ Foto Halaman 1 $\rightarrow$ Foto Halaman 2).
4. **Urutan 4:** Lembar Tugas Siswa Kedua (Header Identitas $\rightarrow$ Foto Halaman 1 $\rightarrow$ Foto Halaman 2).
*(dan seterusnya hingga siswa terakhir dalam batch).*

---

## 5. Bagian yang Wajib Selalu Dipertahankan (Di Bagian Paling Bawah Prompt)

Pastikan 5 baris ini **selalu ada di akhir file prompt Anda tanpa diubah**:

```text
---SISWA: [Nama Siswa]---
NILAI: [Angka 0-100]
CATATAN: [Evaluasi pemahaman konsep, estimasi kata, dan justifikasi poin]
```
Dengan menjaga baris ini tetap utuh, AI akan menghasilkan nilai yang langsung dapat diekspor secara rapi ke `rekap_nilai.xlsx`!
