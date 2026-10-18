# TEMPLATE PROMPT UNTUK DI-COPY KE GEMINI WEB (GOOGLE)
# [Mode: Tanpa Bahan Referensi / Penilaian Mandiri Berdasarkan Soal di Lembar Tugas]
#
# CARA PENGGUNAAN (TRIK PRAKTIS 5 DETIK):
# 1. Buka Gemini di browser Anda: https://gemini.google.com
# 2. Salin (copy) SELURUH TEKS DI BAWAH INI (dari baris 'Halo Gemini...' sampai akhir).
# 3. Tempel (paste) ke kolom chat Gemini Web.
# 4. Lampirkan / upload foto berkas tugas siswa atau foto lembar soal di chat tersebut.
# 5. Tekan Enter / Kirim!
# 6. Salin (copy) seluruh hasil balasan yang dibuatkan oleh Gemini Web.
# 7. Buka berkas 'prompts/rubrik_tanpa_referensi.md', timpa / paste seluruh isinya dengan hasil tadi.
# 8. Selesai! Jalankan sistem di terminal: python sistem_penilaian.py

===================== [SALIN DARI SINI SAMPAI PALING BAWAH] =====================

Halo Gemini, saya adalah seorang guru yang sedang menyusun rubrik penilaian otomatis untuk tugas tulisan tangan siswa.
Pada penilaian ini, TIDAK ADA berkas acuan/kunci jawaban terpisah di folder referensi. AI diharapkan menilai langsung lembar kerja siswa berdasarkan foto lembar tugas/soal yang saya lampirkan dan kaidah keilmuan yang benar.

Tolong buatkan dokumen rubrik penilaian lengkap berdasarkan foto lembar tugas yang saya lampirkan dengan MENGIKUTI FORMAT TEMPLATE SISTEM berikut secara persis:

```markdown
# PANDUAN DAN RUBRIK PENILAIAN AI (TANPA BAHAN REFERENSI / PENGETAHUAN UMUM)
Peran: Anda adalah seorang guru penilai yang teliti, adil, profesional, dan objektif.

================================================================================
BAGIAN 1: DESKRIPSI TUGAS SISWA
================================================================================
- Rincikan tugas apa saja yang dikerjakan siswa berdasarkan foto yang saya lampirkan (sebutkan mata pelajaran, topik materi, jumlah nomor soal, bentuk pengerjaan, dan apa yang harus ditulis siswa).
- Nyatakan bahwa AI harus mengoreksi kebenaran jawaban langsung dari tulisan tangan lembar siswa secara objektif.

================================================================================
BAGIAN 2: RUBRIK DAN PEDOMAN NILAI (SKALA TOTAL 0 - 100)
================================================================================
Bagi bobot nilai per nomor/komponen secara terukur dan adil sehingga totalnya persis 100 poin:
- Sebutkan kriteria poin per nomor (misal: penulisan langkah/metode pengerjaan X poin, ketepatan rumus/konsep Y poin, hasil akhir benar Z poin).
- Berikan kriteria nilai parsial jika jawaban siswa ada langkah yang benar namun perhitungan akhir keliru.
- Nilai 0 jika nomor tersebut tidak dikerjakan atau salah konsep total.

================================================================================
BAGIAN 3: FORMAT OUTPUT SISTEM [WAJIB! JANGAN PERNAH DIUBAH BAGIAN INI]
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
CATATAN: [Tuliskan evaluasi pemahaman siswa: nomor mana yang benar/lengkap, nomor mana yang kurang, serta rincian poin]
```

Tolong buatkan rincian Bagian 1 dan Bagian 2 secara spesifik dan mendalam sesuai foto tugas yang saya lampirkan, serta pertahankan Bagian 3 persis seperti template di atas tanpa diubah sedikitpun. Terima kasih!
