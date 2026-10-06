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
OUTPUT_EXCEL = "rekap_nilai.xlsx"

# Rubrik Penilaian Manajemen Data
PROMPT_RUBRIK = """
Anda adalah seorang guru penguji yang teliti dan adil.
Kali ini anda akan menilai tugas siswa untuk materi manajemen data.
Tugas Anda adalah membaca foto tulisan tangan siswa dan menilai dengan kriteria penilaian sebagai berikut:

Petunjuk Penilaian:
1. Bacalah tulisan tangan pada foto (walaupun tulisan kurang rapi). Jika ada beberapa foto, baca secara berurutan sebagai satu kesatuan tugas.
2. Hitunglah ada berapa kata yang sudah ditulis oleh peserta didik. Kalau peserta didik membuat lebih dari 200 kata maka nilainya 80, bila kurang dari 200 maka 60.
3. Essai yang dibuat peserta didik sesuai dengan judul dan materi akan dapat tambahan 20, kalau tidak nanti menyesuaikan seberapa mirip dengan materi yang kita sampaikan.
4. Berikan output WAJIB dengan format persis seperti ini:

NILAI: [Isi angka 0-100]
CATATAN: [Penjelasan singkat pemahaman konsep siswa, jumlah estimasi kata, dan alasan pemberian nilai]
"""

def dapatkan_model_aktif(api_key):
    """Mengecek otomatis dan memilih model Flash terstabil yang aktif di akun Anda"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            models = res.json().get('models', [])
            flash_models = []
            for m in models:
                name = m.get('name', '').replace('models/', '')
                methods = m.get('supportedGenerationMethods', [])
                if 'generateContent' in methods and 'flash' in name.lower():
                    flash_models.append(name)
            
            # Prioritas model aktif, stabil, dan berkuota memadai
            prioritas = [
                'gemini-3.5-flash', 
                'gemini-flash-latest', 
                'gemini-3.6-flash', 
                'gemini-3.1-flash-lite', 
                'gemini-3.7-flash'
            ]
            
            for pref in prioritas:
                if pref in flash_models:
                    return pref
            
            if flash_models:
                return flash_models[0]
    except Exception as e:
        print(f"[AUTO-DETECT WARNING] Gagal cek model: {e}")
    
    return "gemini-3.5-flash"

def foto_ke_base64(path_foto, max_dim=800):
    """Membaca foto, memperkecil ukurannya, dan mengubah ke format Base64 ringan"""
    img = Image.open(path_foto)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    
    img.thumbnail((max_dim, max_dim))
    
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=80)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def panggil_gemini_direct(prompt, list_path_foto, api_key, model_name, max_retry=3):
    """Memanggil API Google secara langsung via HTTP POST"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    parts = [{"text": prompt}]
    for path_foto in list_path_foto:
        b64_data = foto_ke_base64(path_foto)
        parts.append({
            "inlineData": {
                "mimeType": "image/jpeg",
                "data": b64_data
            }
        })
    
    payload = {"contents": [{"parts": parts}]}
    headers = {"Content-Type": "application/json"}
    
    for attempt in range(1, max_retry + 1):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=120)
            
            if response.status_code != 200:
                res_err = response.json()
                err_msg = res_err.get('error', {}).get('message', response.text)
                raise Exception(f"HTTP {response.status_code}: {err_msg}")

            res_json = response.json()
            if "candidates" in res_json and len(res_json["candidates"]) > 0:
                parts_resp = res_json["candidates"][0].get("content", {}).get("parts", [])
                teks_hasil = "".join([p.get("text", "") for p in parts_resp])
                if teks_hasil:
                    return teks_hasil
                    
            raise Exception("Respon dari server kosong.")

        except Exception as e:
            if attempt == max_retry:
                raise Exception(f"{e}")
            print(f" [Mencoba ulang ({attempt}/{max_retry})...]", end="", flush=True)
            time.sleep(3)

def proses_penilaian():
    if not os.path.exists(FOLDER_TUGAS):
        print(f"Error: Folder '{FOLDER_TUGAS}' tidak ditemukan!")
        return

    # Mendapatkan model aktif yang valid
    nama_model_aktif = dapatkan_model_aktif(API_KEY)
    print(f"[INFO] Menggunakan model aktif: {nama_model_aktif}\n")

    kelompok_siswa = {}
    for root, dirs, files in os.walk(FOLDER_TUGAS):
        for file in sorted(files):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.jpe', '.webp')):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, FOLDER_TUGAS)
                bagian = rel_path.split(os.sep)
                
                nama_siswa = bagian[0] if len(bagian) > 1 else file.split('_')[0]

                if nama_siswa not in kelompok_siswa:
                    kelompok_siswa[nama_siswa] = []
                kelompok_siswa[nama_siswa].append(full_path)

    hasil_rekap = []
    total_siswa = len(kelompok_siswa)
    print(f"Berhasil menemukan {total_siswa} siswa. Memulai penilaian otomatis...\n")

    idx = 1
    for nama_siswa, list_foto in kelompok_siswa.items():
        print(f"[{idx}/{total_siswa}] Memproses: {nama_siswa} ({len(list_foto)} halaman)...", end="", flush=True)
        
        try:
            teks_hasil = panggil_gemini_direct(PROMPT_RUBRIK, list_foto, API_KEY, nama_model_aktif)

            nilai = 0
            catatan = teks_hasil
            
            match_nilai = re.search(r'NILAI:\s*(\d+)', teks_hasil, re.IGNORECASE)
            if match_nilai:
                nilai = int(match_nilai.group(1))

            match_catatan = re.search(r'CATATAN:\s*(.*)', teks_hasil, re.IGNORECASE | re.DOTALL)
            if match_catatan:
                catatan = match_catatan.group(1).strip()

            hasil_rekap.append({
                "Nama Siswa / Folder": nama_siswa,
                "Jumlah Halaman": len(list_foto),
                "Nilai": nilai,
                "Evaluasi Konsep / Catatan": catatan
            })
            print(" [SELESAI]")

        except Exception as e:
            print(f" [GAGAL: {e}]")
            hasil_rekap.append({
                "Nama Siswa / Folder": nama_siswa,
                "Jumlah Halaman": len(list_foto),
                "Nilai": 0,
                "Evaluasi Konsep / Catatan": f"Error: {e}"
            })

        idx += 1
        time.sleep(3)

    df = pd.DataFrame(hasil_rekap)
    df.to_excel(OUTPUT_EXCEL, index=False)
    print(f"\n[SEMUA SELESAI] Rekap nilai berhasil disimpan di: {OUTPUT_EXCEL}")

if __name__ == "__main__":
    proses_penilaian()