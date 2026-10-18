# TEMPLATE PROMPT UNTUK DI-COPY KE GEMINI WEB (GOOGLE)
# [Mode: Dengan Bahan Referensi / Kunci Jawaban / Lembar Soal]
#
# CARA PENGGUNAAN (TRIK PRAKTIS 5 DETIK):
# 1. Buka Gemini di browser Anda: https://gemini.google.com
# 2. Salin (copy) SELURUH TEKS DI BAWAH INI (dari baris 'Halo Gemini...' sampai akhir).
# 3. Tempel (paste) ke kolom chat Gemini Web.
# 4. Lampirkan / upload foto berkas tugas, lembar soal, atau kunci jawaban Anda di chat tersebut.
# 5. Tekan Enter / Kirim!
# 6. Salin (copy) seluruh hasil balasan yang dibuatkan oleh Gemini Web.
# 7. Buka berkas 'prompts/rubrik_dengan_referensi.md', timpa / paste hasilnya ke situ.
# 8. Selesai! Jalankan sistem di terminal: python sistem_penilaian.py

===================== [SALIN DARI SINI SAMPAI PALING BAWAH] =====================

Halo Gemini, saya adalah seorang guru yang sedang menyusun rubrik penilaian otomatis untuk tugas tulisan tangan siswa.
Saya telah melampirkan foto lembar tugas / lembar soal / bahan acuan tugas murid saya.

Tolong buatkan dokumen rubrik penilaian lengkap berdasarkan foto tugas yang saya lampirkan dengan MENGIKUTI FORMAT TEMPLATE SISTEM berikut secara persis:

```markdown
# PANDUAN DAN RUBRIK PENILAIAN AI (DENGAN BAHAN REFERENSI/ACUAN)
Peran: Anda adalah seorang guru penilai yang teliti, adil, profesional, dan objektif.

================================================================================
BAGIAN 1: DESKRIPSI TUGAS SISWA
================================================================================
- Rincikan tugas apa saja yang dikerjakan siswa berdasarkan foto yang saya lampirkan (sebutkan nama materi/aktivitas, nomor soal/problem, apa input dan output yang diharapkan, serta bentuk jawaban yang diperbolehkan).
- Evaluasi setiap lembar jawaban siswa secara teliti berdasarkan bahan acuan/kunci pada folder 'referensi/' serta pedoman nilai di bawah ini.

================================================================================
BAGIAN 2: PERAN BAHAN DI FOLDER REFERENSI
================================================================================
Jelaskan bahwa bahan yang ada di folder referensi berfungsi sebagai:
- Berkas referensi berfungsi sebagai [sebutkan fungsinya: KUNCI JAWABAN RESMI / LEMBAR SOAL / MATERI BACAAN TEORI].

================================================================================
BAGIAN 3: RUBRIK DAN PEDOMAN NILAI (SKALA TOTAL 0 - 100)
================================================================================
Bagi bobot nilai per nomor/problem secara adil dan terukur hingga totalnya persis 100 poin:
- Sebutkan kriteria poin per nomor (misal: logika algoritma X poin, ketepatan rumus Y poin, jawaban akhir benar Z poin).
- Berikan kriteria nilai parsial jika jawaban siswa setengah benar atau ada kesalahan hitung kecil tapi langkah benar.
- Nilai 0 jika salah konsep total atau tidak dikerjakan.

================================================================================
BAGIAN 4: FORMAT OUTPUT SISTEM [WAJIB! JANGAN PERNAH DIUBAH BAGIAN INI]
================================================================================
PERINGATAN KERAS: Bagian di bawah ini WAJIB persis seperti ini karena dibaca otomatis
oleh sistem program untuk dimasukkan ke Excel rekap_nilai.xlsx.
Dilarang mengubah atau menghapus kata '---SISWA:', 'NILAI:', dan 'CATATAN:'.

ATURAN OUTPUT:
- HANYA berikan nilai untuk siswa yang lembar tugasnya dilampirkan.
- Dilarang memberikan teks pengantar pembuka (seperti "Berikut hasil penilaian:") atau penutup.
- Format output untuk SETIAP siswa HARUS persis seperti berikut:

---SISWA: [Nama Siswa]---
NILAI: [Angka bulat 0-100]
CATATAN: [Tuliskan evaluasi pemahaman siswa: nomor/bagian mana yang benar, nomor mana yang salah, dan alasan perolehan poin]
```

Tolong buatkan rincian Bagian 1, Bagian 2, dan Bagian 3 secara spesifik dan mendalam sesuai foto yang saya lampirkan, serta pertahankan Bagian 4 persis seperti template di atas tanpa diubah sedikitpun. Terima kasih!
