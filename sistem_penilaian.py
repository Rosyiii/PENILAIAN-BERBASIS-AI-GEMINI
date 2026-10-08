import os
import time
import re
import io
import base64
import requests
import pandas as pd
from PIL import Image

# ==========================================
# KONFIGURASI PROGRAM
# ==========================================
API_KEY = "MASUKKAN_API_KEY_ANDA_DI_SINI"

FOLDER_TUGAS = "./foto_tugas"
FOLDER_REFERENSI = "./referensi"  # Folder tempat menyimpan foto bahan bacaan (maks 5 halaman)
OUTPUT_EXCEL = "rekap_nilai.xlsx"
SISWA_PER_BATCH = 6  # Memproses 6-8 siswa per 1 request API

PROMPT_RUBRIK_BATCH = """
Anda adalah seorang guru penguji yang teliti, adil, dan objektif.

TUGAS UTAMA:
Di awal lampiran, terdapat FOTO BAHAN BACAAN (MATERI ACUAN). Setelah itu terdapat lembar jawaban dari beberapa siswa. Evaluasi setiap jawaban siswa berdasarkan MATERI ACUAN tersebut.

RUBRIK PENILAIAN:
1. Deskripsikan Rubrik Penilaianmu disini

ATURAN OUTPUT (SANGAT PENTING):
- HANYA berikan nilai untuk nama siswa yang lembar jawabannya dilampirkan.
- Dilarang memberikan teks pengantar atau penutup. 
- Output HARUS menggunakan format berikut secara persis untuk setiap siswa tanpa markdown tebal di format struktur:

---SISWA: [Nama Siswa]---
NILAI: [Angka 0-100]
CATATAN: [Berisi alasan kenapa siswa mendapat nilai tersebut secara singkat dan berkaitan dengan rubrik penilaian yang disebutkan]
"""

PROMPT_RUBRIK_BATCH_TANPA_REFERENSI = """
Anda adalah seorang guru penguji yang teliti, adil, dan objektif.

TUGAS UTAMA:
Di bawah ini terdapat lembar jawaban dari beberapa siswa. Evaluasi setiap jawaban siswa berdasarkan kebenaran konsep umum materi.

RUBRIK PENILAIAN:
1. Deskripsikan Rubrik Penilaianmu disini

ATURAN OUTPUT (SANGAT PENTING):
- HANYA berikan nilai untuk nama siswa yang lembar jawabannya dilampirkan.
- Dilarang memberikan teks pengantar atau penutup. 
- Output HARUS menggunakan format berikut secara persis untuk setiap siswa tanpa markdown tebal di format struktur:

---SISWA: [Nama Siswa]---
NILAI: [Angka 0-100]
CATATAN: [Berisi alasan kenapa siswa mendapat nilai tersebut secara singkat dan berkaitan dengan rubrik penilaian yang disebutkan]
"""

def dapatkan_model_aktif(api_key):
    """Mengecek otomatis dan memilih model Flash aktif di akun Anda"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            models = res.json().get('models', [])
            flash_models = [m.get('name', '').replace('models/', '') for m in models 
                            if 'generateContent' in m.get('supportedGenerationMethods', []) and 'flash' in m.get('name', '').lower()]
            
            prioritas = ['gemini-3.5-flash-lite', 'gemini-3.1-flash-lite', 'gemini-2.5-flash-lite', 'gemini-2.5-flash', 'gemini-3-flash', 'gemini-3.5-flash']
            for pref in prioritas:
                if pref in flash_models:
                    return pref
            if flash_models:
                return flash_models[0]
    except Exception:
        pass
    return "gemini-3.5-flash"

def foto_ke_base64(path_foto, max_dim=1024):
    """Kompresi dan konversi foto ke Base64"""
    try:
        img = Image.open(path_foto)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.thumbnail((max_dim, max_dim))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=80)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')
    except Exception as e:
        print(f" [!] Gagal memproses gambar {path_foto}: {e}")
        return None

def kelompokkan_foto_per_siswa(folder_path):
    """Membaca folder tugas dan mengelompokkan file berdasarkan nama siswa sebelum '_' """
    kelompok = {}
    for file in sorted(os.listdir(folder_path)):
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.jpe', '.webp')):
            nama_file_tanpa_ext = os.path.splitext(file)[0]
            if '_' in nama_file_tanpa_ext:
                nama_siswa = nama_file_tanpa_ext.split('_')[0].strip()
            else:
                nama_siswa = nama_file_tanpa_ext.strip()
                
            full_path = os.path.join(folder_path, file)
            
            if nama_siswa not in kelompok:
                kelompok[nama_siswa] = []
            kelompok[nama_siswa].append(full_path)
    return kelompok

def ambil_foto_referensi(folder_ref):
    """Membaca seluruh foto bahan bacaan acuan di folder referensi"""
    if not os.path.exists(folder_ref):
        os.makedirs(folder_ref)
        return []
    
    list_ref = []
    for file in sorted(os.listdir(folder_ref)):
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.jpe', '.webp')):
            list_ref.append(os.path.join(folder_ref, file))
    return list_ref

def proses_penilaian():
    if not os.path.exists(FOLDER_TUGAS):
        print(f"[!] Error: Folder '{FOLDER_TUGAS}' tidak ditemukan!")
        return

    nama_model = dapatkan_model_aktif(API_KEY)
    print(f"[INFO] Menggunakan model aktif: {nama_model}")

    # 1. Muat Bahan Bacaan Referensi
    foto_ref = ambil_foto_referensi(FOLDER_REFERENSI)
    if not foto_ref:
        print("[PERINGATAN] Folder referensi kosong. AI akan menilai menggunakan pengetahuan umumnya.")
        prompt_digunakan = PROMPT_RUBRIK_BATCH_TANPA_REFERENSI
    else:
        print(f"[INFO] Berhasil memuat {len(foto_ref)} halaman BAHAN BACAAN REFERENSI.")
        prompt_digunakan = PROMPT_RUBRIK_BATCH

    # 2. Kelompokkan foto berdasarkan nama siswa
    kelompok_siswa = kelompokkan_foto_per_siswa(FOLDER_TUGAS)
    daftar_nama_siswa = list(kelompok_siswa.keys())
    total_siswa = len(daftar_nama_siswa)

    if total_siswa == 0:
        print("[!] Tidak ada file foto tugas ditemukan di folder 'foto_tugas'.")
        return

    print(f"[INFO] Berhasil mengidentifikasi {total_siswa} siswa secara terpisah.")

    # 3. Bagi siswa ke dalam kelompok Batch
    hasil_rekap = []
    siswa_chunks = [daftar_nama_siswa[i:i + SISWA_PER_BATCH] for i in range(0, total_siswa, SISWA_PER_BATCH)]

    for idx_batch, chunk in enumerate(siswa_chunks, 1):
        print(f"\n[Batch {idx_batch}/{len(siswa_chunks)}] Memproses {len(chunk)} siswa ({', '.join(chunk[:2])}...)...")
        
        parts = [{"text": prompt_digunakan}]
        
        # A. SISIPKAN BAHAN BACAAN / MATERI ACUAN TERLEBIH DAHULU
        if foto_ref:
            parts.append({"text": "\n\n========================================\n[DOKUMEN ACUAN] BAHAN BACAAN / KUNCI JAWABAN MATERI:\n========================================"})
            for path_ref in foto_ref:
                b64_data = foto_ke_base64(path_ref)
                if b64_data:
                    parts.append({
                        "inlineData": {
                            "mimeType": "image/jpeg",
                            "data": b64_data
                        }
                    })

        # B. SISIPKAN LEMBAR JAWABAN SISWA
        for nama_siswa in chunk:
            list_foto = kelompok_siswa[nama_siswa]
            parts.append({"text": f"\n\n========================================\nLEMBAR JAWABAN SISWA: {nama_siswa} ({len(list_foto)} halaman)\n========================================"})
            
            for path_foto in list_foto:
                b64_data = foto_ke_base64(path_foto)
                if b64_data:
                    parts.append({
                        "inlineData": {
                            "mimeType": "image/jpeg",
                            "data": b64_data
                        }
                    })

        # Panggil API Gemini
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{nama_model}:generateContent?key={API_KEY}"
        payload = {"contents": [{"parts": parts}]}
        headers = {"Content-Type": "application/json"}

        try:
            # Mekanisme Retry sederhana (Max 3 kali)
            max_retries = 3
            res = None
            for attempt in range(max_retries):
                res = requests.post(url, json=payload, headers=headers, timeout=180)
                if res.status_code == 200:
                    break
                elif res.status_code == 429:
                    print(f" [!] Terkena limit API (429). Menunggu 10 detik... (Percobaan {attempt+1}/{max_retries})")
                    time.sleep(10)
                else:
                    break
            
            if res is None or res.status_code != 200:
                print(f" [!] Batch Gagal (HTTP {res.status_code if res else 'Unknown'}): {res.text if res else 'No Response'}")
                continue

            res_json = res.json()
            teks_hasil = res_json["candidates"][0]["content"]["parts"][0]["text"]

            # Parsing jawaban AI per siswa
            for nama_siswa in chunk:
                # Regex lebih toleran terhadap markdown bintang (*), spasi, dan jumlah strip (-)
                pola_siswa = rf"(?:-|\*)*\s*SISWA:\s*(?:\*|_)*{re.escape(nama_siswa)}(?:\*|_)*\s*(?:-|\*)*(.*?)(?=(?:-|\*)*\s*SISWA:|$)"
                match_blok = re.search(pola_siswa, teks_hasil, re.DOTALL | re.IGNORECASE)
                
                nilai = 0
                catatan = "Evaluasi tidak ditemukan dalam respon AI."

                if match_blok:
                    isi_blok = match_blok.group(1)
                    
                    match_nilai = re.search(r'NILAI:\s*(\d+)', isi_blok, re.IGNORECASE)
                    if match_nilai:
                        nilai = int(match_nilai.group(1))

                    match_catatan = re.search(r'CATATAN:\s*(.*)', isi_blok, re.IGNORECASE | re.DOTALL)
                    if match_catatan:
                        catatan = match_catatan.group(1).strip()

                hasil_rekap.append({
                    "Nama Siswa": nama_siswa,
                    "Jumlah Halaman": len(kelompok_siswa[nama_siswa]),
                    "Nilai": nilai,
                    "Evaluasi Konsep / Catatan": catatan
                })
                print(f"  ├─ {nama_siswa} -> NILAI: {nilai}")

        except Exception as e:
            print(f" [!] Error pada Batch {idx_batch}: {e}")

        time.sleep(3)

    # 4. Simpan ke file Excel
    df = pd.DataFrame(hasil_rekap)
    df.to_excel(OUTPUT_EXCEL, index=False)
    print("\n" + "=" * 60)
    print(f"[SEMUA SELESAI] Rekap nilai berhasil disimpan di: {OUTPUT_EXCEL}")
    print("=" * 60)

if __name__ == "__main__":
    proses_penilaian()
