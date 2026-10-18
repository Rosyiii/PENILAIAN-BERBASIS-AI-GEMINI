import os
import sys
import time
import re
import io
import base64
import requests
import pandas as pd
from PIL import Image
from dotenv import load_dotenv

# Konfigurasi encoding stdout/stderr agar aman di terminal Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from utils.document_reader import (
    baca_rubrik,
    ambil_rubrik_dari_folder,
    baca_semua_referensi,
)

# ==========================================
# KONFIGURASI PROGRAM (.env)
# ==========================================
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
FOLDER_TUGAS = os.getenv("FOLDER_TUGAS") or os.getenv("FOLDER_JAWABAN") or "./foto_tugas"
FOLDER_REFERENSI = os.getenv("FOLDER_REFERENSI", "./referensi")
FOLDER_PROMPTS = os.getenv("FOLDER_PROMPTS", "./prompts")
OUTPUT_EXCEL = os.getenv("OUTPUT_EXCEL", "rekap_nilai.xlsx")
SISWA_PER_BATCH = int(os.getenv("SISWA_PER_BATCH", "6"))


def perbarui_api_key_di_env(api_key_baru: str, env_path: str = ".env") -> bool:
    """Memperbarui nilai GEMINI_API_KEY pada file .env dan sistem memori."""
    try:
        api_key_baru = api_key_baru.strip()
        lines = []
        key_found = False

        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            new_lines = []
            for line in lines:
                if line.strip().startswith("GEMINI_API_KEY="):
                    new_lines.append(f"GEMINI_API_KEY={api_key_baru}\n")
                    key_found = True
                else:
                    new_lines.append(line)
            lines = new_lines

        if not key_found:
            lines.append(f"\nGEMINI_API_KEY={api_key_baru}\n")

        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        os.environ["GEMINI_API_KEY"] = api_key_baru
        return True
    except Exception as e:
        print(f" [!] Gagal menulis API Key ke berkas .env: {e}")
        return False


def minta_api_key_baru(env_path: str = ".env"):
    """Menjeda proses dan meminta input GEMINI_API_KEY baru via CMD saat kuota/token habis."""
    print("\n" + "=" * 65)
    print("      PERMINTAAN INPUT GEMINI_API_KEY BARU")
    print("=" * 65)
    print(" Kuota / Token Gemini API Anda telah habis atau terkena limit.")
    print(" Masukkan GEMINI_API_KEY baru untuk melanjutkan proses koreksi.")
    print(" (Ketik 'q' atau 'exit' untuk membatalkan dan menyimpan progres yang ada)")
    print("=" * 65)

    while True:
        try:
            kunci_baru = input("\n>> Masukkan GEMINI_API_KEY baru: ").strip()
            if not kunci_baru:
                print(" [!] API Key tidak boleh kosong. Silakan coba lagi.")
                continue
            if kunci_baru.lower() in ("q", "quit", "exit", "batal"):
                print(" [!] Pengguna membatalkan proses pergantian API Key.")
                return None

            sukses = perbarui_api_key_di_env(kunci_baru, env_path=env_path)
            if sukses:
                print(" [OK] GEMINI_API_KEY berhasil diperbarui di berkas .env dan memori sistem.")
            else:
                print(" [!] Peringatan: Gagal memperbarui file .env, namun API Key tetap aktif di memori.")

            return kunci_baru
        except (KeyboardInterrupt, EOFError):
            print("\n [!] Input dibatalkan.")
            return None


# Urutan prioritas model Flash (Generasi terbaru Google Gemini hingga model cadangan)
DAFTAR_PRIORITAS_MODEL = [
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-3.6-flash",
    "gemini-3.7-flash",
    "gemini-3.8-flash",
]


def dapatkan_daftar_model_aktif(api_key: str):
    """Mengecek otomatis dan mengurutkan seluruh model Flash aktif di akun pengguna sesuai prioritas."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    daftar_tersedia = []
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            models = res.json().get('models', [])
            flash_models = [
                m.get('name', '').replace('models/', '') 
                for m in models 
                if 'generateContent' in m.get('supportedGenerationMethods', []) 
                and 'flash' in m.get('name', '').lower()
            ]
            
            # Urutkan model yang tersedia berdasarkan daftar prioritas
            for pref in DAFTAR_PRIORITAS_MODEL:
                if pref in flash_models and pref not in daftar_tersedia:
                    daftar_tersedia.append(pref)

            # Tambahkan model flash lainnya yang ada di akun
            for m in flash_models:
                if m not in daftar_tersedia and not any(x in m for x in ['image', 'tts', 'preview-tts']):
                    daftar_tersedia.append(m)
    except Exception as e:
        print(f" [!] Peringatan: Gagal memuat daftar model dari API ({e}). Menggunakan urutan prioritas standar.")

    if not daftar_tersedia:
        daftar_tersedia = list(DAFTAR_PRIORITAS_MODEL)

    return daftar_tersedia


def dapatkan_model_aktif(api_key: str):
    """Mengambil model Flash utama paling prioritas."""
    models = dapatkan_daftar_model_aktif(api_key)
    return models[0] if models else "gemini-3.8-flash"


def foto_ke_base64(path_foto, max_dim=1024):
    """Kompresi dan konversi foto ke Base64."""
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


def ekstrak_nis_dan_nama(teks: str):
    """Mengekstrak NIS (bila ada) dan Nama Siswa dari string."""
    teks = teks.strip()
    # 1. Format: "12345 - Nama Siswa" atau "12345_Nama Siswa"
    m1 = re.match(r'^(\d+)\s*[-_–]\s*(.+)$', teks)
    if m1:
        return m1.group(1).strip(), m1.group(2).strip()

    # 2. Format: "Nama Siswa (12345)" atau "Nama Siswa [12345]"
    m2 = re.match(r'^(.+?)\s*[\(\[]\s*(\d+)\s*[\)\]]$', teks)
    if m2:
        return m2.group(2).strip(), m2.group(1).strip()

    # 3. Format: "Nama Siswa - 12345"
    m3 = re.match(r'^(.+?)\s*[-_–]\s*(\d+)$', teks)
    if m3:
        return m3.group(2).strip(), m3.group(1).strip()

    return "-", teks


def kelompokkan_foto_per_file(folder_path):
    """Format Opsi 1: File langsung di dalam folder_path dengan pola [NAMA]_[id/keterangan].ext."""
    if not os.path.exists(folder_path):
        return []

    ekstensi_gambar = ('.png', '.jpg', '.jpeg', '.jpe', '.webp')
    kelompok = {}

    for file in sorted(os.listdir(folder_path)):
        full_path = os.path.join(folder_path, file)
        if os.path.isfile(full_path) and file.lower().endswith(ekstensi_gambar) and not file.startswith('.'):
            nama_file_tanpa_ext = os.path.splitext(file)[0]
            tokens = nama_file_tanpa_ext.split('_')
            nama_mentah = tokens[0].strip()

            nis, nama_siswa = ekstrak_nis_dan_nama(nama_mentah)
            # Deteksi ID Moodle bila segmen kedua berupa angka dan NIS belum terisi
            if nis == "-" and len(tokens) > 1 and tokens[1].strip().isdigit():
                nis = tokens[1].strip()

            key = (nama_siswa, nis)
            if key not in kelompok:
                kelompok[key] = []
            kelompok[key].append(full_path)

    hasil = []
    for (nama_siswa, nis), list_foto in kelompok.items():
        hasil.append({
            "kelas": "-",
            "nis": nis,
            "nama": nama_siswa,
            "foto": list_foto
        })
    return hasil


def kelompokkan_foto_per_folder(folder_path):
    """Format Opsi 2: Berjenjang folder_path/Kelas/Nama (NIS)/foto.ext."""
    if not os.path.exists(folder_path):
        return []

    ekstensi_gambar = ('.png', '.jpg', '.jpeg', '.jpe', '.webp')
    hasil = []

    for item in sorted(os.listdir(folder_path)):
        if item.startswith('.'):
            continue
        kelas_path = os.path.join(folder_path, item)
        if not os.path.isdir(kelas_path):
            continue

        nama_kelas = item.strip()
        for sub_item in sorted(os.listdir(kelas_path)):
            if sub_item.startswith('.'):
                continue
            siswa_path = os.path.join(kelas_path, sub_item)
            if not os.path.isdir(siswa_path):
                continue

            nis, nama_siswa = ekstrak_nis_dan_nama(sub_item)
            foto_list = []
            for f in sorted(os.listdir(siswa_path)):
                if f.startswith('.'):
                    continue
                if f.lower().endswith(ekstensi_gambar):
                    foto_list.append(os.path.join(siswa_path, f))

            if foto_list:
                hasil.append({
                    "kelas": nama_kelas,
                    "nis": nis,
                    "nama": nama_siswa,
                    "foto": foto_list
                })

    return hasil


def tentukan_mode_referensi():
    """Menanyakan kepada pengguna apakah ingin menilai dengan atau tanpa bahan referensi."""
    env_mode = os.getenv("GUNAKAN_REFERENSI")
    if env_mode is not None:
        val = env_mode.strip().lower()
        if val in ("false", "0", "no"):
            return False
        elif val in ("true", "1", "yes"):
            return True

    print("\n" + "=" * 55)
    print("           PILIHAN 1: MODE REFERENSI ACUAN")
    print("=" * 55)
    print(" [1] Dengan Referensi (Gunakan bahan acuan di folder referensi/)")
    print(" [2] Tanpa Referensi  (Pengetahuan umum AI, abaikan folder referensi)")
    print("=" * 55)
    
    try:
        pilihan = input("Pilih mode referensi (1/2) [Tekan Enter untuk default: 1]: ").strip()
        if pilihan == "2":
            return False
        return True
    except (EOFError, KeyboardInterrupt):
        return True


def tentukan_format_tugas():
    """Menanyakan kepada pengguna format pengorganisasian lembar jawab siswa."""
    env_format = os.getenv("FORMAT_LEMBAR_JAWAB") or os.getenv("FORMAT_TUGAS")
    if env_format is not None:
        val = env_format.strip().lower()
        if val in ("1", "file", "per_file", "per-file"):
            return "file"
        elif val in ("2", "folder", "per_folder", "per-folder"):
            return "folder"

    print("\n" + "=" * 55)
    print("        PILIHAN 2: FORMAT LEMBAR JAWAB SISWA")
    print("=" * 55)
    print(" [1] Per File   (Semua file di foto_tugas/ berformat NAMA_id.jpg)")
    print(" [2] Per Folder (Struktur: foto_tugas/Kelas/Nama/foto.jpg)")
    print("=" * 55)

    try:
        pilihan = input("Pilih format lembar jawab (1/2) [Tekan Enter untuk default: 1]: ").strip()
        if pilihan == "2":
            return "folder"
        elif pilihan == "1" or pilihan == "":
            return "file"
        else:
            print(f"\n [!] Pilihan '{pilihan}' tidak valid.")
            return None
    except (EOFError, KeyboardInterrupt):
        return None


def proses_penilaian():
    global API_KEY

    print("=" * 65)
    print("      SISTEM PENILAIAN TUGAS SISWA OTOMATIS BERBASIS AI")
    print("                 Karya / Created by: Rosyi")
    print("=" * 65)

    if not API_KEY or API_KEY == "MASUKKAN_API_KEY_ANDA_DI_SINI":
        print("[!] Error: GEMINI_API_KEY belum dikonfigurasi di berkas .env!")
        kunci_awal = minta_api_key_baru()
        if not kunci_awal:
            print("    Proses dibatalkan karena tidak ada GEMINI_API_KEY.")
            return
        API_KEY = kunci_awal

    if not os.path.exists(FOLDER_TUGAS):
        print(f"[!] Error: Folder tugas '{FOLDER_TUGAS}' tidak ditemukan!")
        return

    # 1. Konfirmasi Mode Referensi
    gunakan_referensi = tentukan_mode_referensi()

    # 2. Konfirmasi Format Lembar Jawab Siswa
    format_mode = tentukan_format_tugas()
    if not format_mode:
        print("[!] Penilaian dibatalkan oleh pengguna atau input tidak valid.")
        return

    # Validasi & Muat Data Siswa Berdasarkan Pilihan Format
    if format_mode == "file":
        daftar_siswa = kelompokkan_foto_per_file(FOLDER_TUGAS)
        if not daftar_siswa:
            print("\n" + "=" * 65)
            print(" [!] FORMAT TIDAK SESUAI - PROSES DIBATALKAN")
            print("=" * 65)
            print(" Mode Dipilih : [1] Per File")
            print(f" Lokasi Target: {FOLDER_TUGAS}")
            print("\n KENDALA:")
            print(" Tidak ditemukan file gambar (.jpg, .jpeg, .png, .webp) langsung di folder tugas.")
            print("\n FORMAT YANG DIHARAPKAN:")
            print(f" {FOLDER_TUGAS}/")
            print(" |-- AHMAD PRATAMA_lembar1.jpg")
            print(" |-- AHMAD PRATAMA_lembar2.jpg")
            print(" \\-- BUDI SANTOSO_01.jpg")
            print("=" * 65)
            return

    elif format_mode == "folder":
        daftar_siswa = kelompokkan_foto_per_folder(FOLDER_TUGAS)
        if not daftar_siswa:
            print("\n" + "=" * 65)
            print(" [!] FORMAT TIDAK SESUAI - PROSES DIBATALKAN")
            print("=" * 65)
            print(" Mode Dipilih : [2] Per Folder")
            print(f" Lokasi Target: {FOLDER_TUGAS}")
            print("\n KENDALA:")
            print(" Struktur folder tidak sesuai atau tidak ditemukan foto tugas di dalam folder siswa.")
            print("\n FORMAT YANG DIHARAPKAN:")
            print(f" {FOLDER_TUGAS}/")
            print(" \\-- <Kelas>/")
            print("     \\-- <Nama Siswa (dengan atau tanpa NIS)>/")
            print("         |-- foto1.jpg")
            print("         \\-- foto2.jpg")
            print("\n CONTOH STRUKTUR:")
            print(f" {FOLDER_TUGAS}/")
            print(" |-- Kelas 10-A/")
            print(" |   |-- 12345 - Ahmad Pratama/")
            print(" |   |   |-- lembar1.jpg")
            print(" |   |   \\-- lembar2.jpg")
            print(" |   \\-- Budi Santoso/")
            print(" |       \\-- tugas.jpg")
            print(" \\-- Kelas 10-B/")
            print("     \\-- Citra Lestari (12346)/")
            print("         \\-- jawaban.jpg")
            print("=" * 65)
            return

    total_siswa = len(daftar_siswa)
    print(f"\n[INFO] Format Aktif: PER {'FOLDER' if format_mode == 'folder' else 'FILE'}")
    print(f"[INFO] Berhasil memvalidasi {total_siswa} siswa untuk diproses.")

    # 3. Dapatkan Model Aktif Gemini (Terurut Sesuai Prioritas)
    daftar_model = dapatkan_daftar_model_aktif(API_KEY)
    model_idx = 0
    current_model = daftar_model[model_idx]
    print(f"[INFO] Model utama aktif: {current_model}")
    if len(daftar_model) > 1:
        cadangan = ", ".join(daftar_model[1:4])
        sisa = len(daftar_model) - 4
        tambahan = f" (+{sisa} lainnya)" if sisa > 0 else ""
        print(f"[INFO] Model cadangan fallback: {cadangan}{tambahan}")

    # 4. Muat Dokumen Narasi/Foto Acuan Referensi
    teks_ref = ""
    foto_ref = []
    ada_referensi = False

    if gunakan_referensi:
        data_referensi = baca_semua_referensi(FOLDER_REFERENSI)
        teks_ref = data_referensi.get("teks", "").strip()
        foto_ref = data_referensi.get("gambar", [])
        ada_referensi = bool(teks_ref or foto_ref)

        if not ada_referensi:
            print("[PERINGATAN] Folder referensi kosong. AI akan beralih menilai menggunakan pengetahuan umumnya.")
            nama_rubrik_target = "rubrik_tanpa_referensi.md"
        else:
            info_ref = []
            if teks_ref:
                info_ref.append("dokumen narasi/soal")
            if foto_ref:
                info_ref.append(f"{len(foto_ref)} gambar acuan")
            print(f"[INFO] Mode Acuan: DENGAN REFERENSI ({', '.join(info_ref)}).")
            nama_rubrik_target = "rubrik_dengan_referensi.md"
    else:
        print("[INFO] Mode Acuan: TANPA REFERENSI (AI menilai berdasarkan pemahaman umum).")
        nama_rubrik_target = "rubrik_tanpa_referensi.md"

    # 5. Muat Rubrik Penilaian dari Folder prompts/
    path_rubrik_target = os.path.join(FOLDER_PROMPTS, nama_rubrik_target)
    if os.path.exists(path_rubrik_target):
        try:
            prompt_digunakan = baca_rubrik(path_rubrik_target)
            print(f"[INFO] Rubrik penilaian berhasil dimuat dari: {path_rubrik_target}")
        except Exception as e:
            print(f"[!] Error: Gagal membaca rubrik '{path_rubrik_target}': {e}")
            return
    elif os.path.exists(FOLDER_PROMPTS):
        try:
            prompt_digunakan = ambil_rubrik_dari_folder(FOLDER_PROMPTS)
            print(f"[INFO] Rubrik alternatif berhasil dimuat dari folder: {FOLDER_PROMPTS}")
        except Exception as e:
            print(f"[!] Error: Tidak dapat memuat rubrik dari '{FOLDER_PROMPTS}': {e}")
            return
    else:
        print(f"[!] Error: Folder rubrik '{FOLDER_PROMPTS}' atau file '{nama_rubrik_target}' tidak ditemukan!")
        return

    # 6. Pemrosesan Batch
    hasil_rekap = []
    siswa_chunks = [daftar_siswa[i:i + SISWA_PER_BATCH] for i in range(0, total_siswa, SISWA_PER_BATCH)]
    
    current_api_key = API_KEY

    for idx_batch, chunk in enumerate(siswa_chunks, 1):
        nama_siswa_preview = ", ".join([s["nama"] for s in chunk[:2]])
        print(f"\n[Batch {idx_batch}/{len(siswa_chunks)}] Memproses {len(chunk)} siswa ({nama_siswa_preview}...)...")

        parts = [{"text": prompt_digunakan}]

        # A. Sisipkan Dokumen Acuan jika ada
        if ada_referensi:
            parts.append({"text": "\n\n========================================\n[DOKUMEN ACUAN] BAHAN BACAAN / KUNCI JAWABAN MATERI:\n========================================"})
            if teks_ref:
                parts.append({"text": f"NARASI/SOAL DAN MATERI ACUAN:\n{teks_ref}"})
            for path_ref in foto_ref:
                b64_data = foto_ke_base64(path_ref)
                if b64_data:
                    parts.append({
                        "inlineData": {
                            "mimeType": "image/jpeg",
                            "data": b64_data
                        }
                    })

        # B. Sisipkan Lembar Jawaban Siswa
        for siswa in chunk:
            nama_s = siswa["nama"]
            kelas_s = siswa["kelas"]
            nis_s = siswa["nis"]
            list_foto = siswa["foto"]

            header_siswa = f"LEMBAR JAWABAN SISWA: {nama_s}"
            if kelas_s != "-":
                header_siswa += f" (Kelas: {kelas_s})"
            if nis_s != "-":
                header_siswa += f" (NIS: {nis_s})"
            header_siswa += f" ({len(list_foto)} halaman)"

            parts.append({
                "text": (
                    f"\n\n========================================\n"
                    f"{header_siswa}\n"
                    f"Gunakan format nama persis pada tag output: ---SISWA: {nama_s}---\n"
                    f"========================================"
                )
            })

            for path_foto in list_foto:
                b64_data = foto_ke_base64(path_foto)
                if b64_data:
                    parts.append({
                        "inlineData": {
                            "mimeType": "image/jpeg",
                            "data": b64_data
                        }
                    })

        payload = {"contents": [{"parts": parts}]}
        headers = {"Content-Type": "application/json"}

        # Loop pengiriman request dengan auto-fallback model & penanganan kuota habis
        batch_berhasil = False
        res = None

        while not batch_berhasil:
            current_model = daftar_model[model_idx]
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{current_model}:generateContent?key={current_api_key}"

            try:
                res = requests.post(url, json=payload, headers=headers, timeout=180)
            except requests.exceptions.RequestException as e:
                print(f" [!] Error koneksi ke server Gemini API ({current_model}): {e}")
                if model_idx + 1 < len(daftar_model):
                    model_lama = current_model
                    model_idx += 1
                    current_model = daftar_model[model_idx]
                    print(f" [->] Mencoba model cadangan berikutnya: {current_model}...")
                    time.sleep(2)
                    continue

                print(" [?] Tekan Enter untuk coba lagi, atau ketik 'key' untuk ganti API key, atau 'q' untuk keluar.")
                pilihan_err = input(">> ").strip().lower()
                if pilihan_err == 'q':
                    break
                elif pilihan_err == 'key':
                    kunci_baru = minta_api_key_baru()
                    if kunci_baru:
                        current_api_key = kunci_baru
                        daftar_model = dapatkan_daftar_model_aktif(current_api_key)
                        model_idx = 0
                time.sleep(2)
                continue

            if res is not None and res.status_code == 200:
                batch_berhasil = True
                break

            res_text = res.text if res is not None else ""

            # Evaluasi apakah error dapat diatasi dengan beralih ke model cadangan berikutnya:
            # 1. 404 Not Found / Model no longer available (seperti gemini-2.5-flash)
            # 2. 429 Quota Exceeded / Rate Limit untuk model ini
            # 3. 503 High demand / temporary overload pada model ini
            # 4. 400 Bad Request terkait model deprecated / unsupported
            bisa_fallback = False
            if res is not None:
                if res.status_code in (404, 503, 429):
                    bisa_fallback = True
                elif res.status_code in (400, 403):
                    teks_lower = res_text.lower()
                    if any(k in teks_lower for k in [
                        "resource_exhausted", "quota", "rate limit", 
                        "no longer available", "not found", "deprecated", "high demand"
                    ]):
                        bisa_fallback = True

            # JIKA BISA FALLBACK DAN MASIH ADA MODEL CADANGAN BERIKUTNYA:
            if bisa_fallback and (model_idx + 1 < len(daftar_model)):
                model_lama = current_model
                model_idx += 1
                current_model = daftar_model[model_idx]
                try:
                    pesan_err_singkat = res.json().get('error', {}).get('message', res_text)
                except Exception:
                    pesan_err_singkat = res_text
                print(f"\n [!] Model '{model_lama}' terkendala (HTTP {res.status_code}): {pesan_err_singkat[:100]}...")
                print(f" [->] Otomatis beralih (fallback) ke model prioritas berikutnya: '{current_model}'...")
                time.sleep(1)
                continue  # Ulangi request batch dengan model cadangan tanpa menghentikan sistem

            # JIKA SEMUA MODEL CADANGAN TELAH DICOBA & KUOTA BENAR-BENAR HABIS:
            token_habis = False
            if res is not None:
                if res.status_code == 429:
                    token_habis = True
                elif res.status_code in (400, 401, 403):
                    teks_lower = res_text.lower()
                    if any(k in teks_lower for k in ["resource_exhausted", "quota", "rate limit", "token", "api_key_invalid", "expired"]):
                        token_habis = True

            if token_habis or bisa_fallback:
                print("\n" + "!" * 65)
                print(" [PERHATIAN] Seluruh Model Cadangan Telah Dicoba / Kuota API Habis!")
                try:
                    pesan_err = res.json().get('error', {}).get('message', res_text)
                except Exception:
                    pesan_err = res_text
                print(f" Status Respons: HTTP {res.status_code if res else 'Unknown'} - {pesan_err}")
                print(" Sistem menghentikan sementara proses pengerjaan.")
                print(" Silakan masukkan GEMINI_API_KEY baru untuk melanjutkan proses.")
                print("!" * 65)

                kunci_baru = minta_api_key_baru()
                if not kunci_baru:
                    print(" [!] Melewatkan sisa proses karena tidak ada API key baru.")
                    break

                current_api_key = kunci_baru
                daftar_model = dapatkan_daftar_model_aktif(current_api_key)
                model_idx = 0
                current_model = daftar_model[model_idx]
                print(f" [INFO] Melanjutkan proses koreksi dengan API Key baru dan model: {current_model}...")
                time.sleep(1)
                continue

            else:
                # Error server lainnya (misal error 500)
                print(f" [!] Batch Gagal (HTTP {res.status_code if res else 'Unknown'}): {res_text}")
                print(" [?] Tekan Enter untuk mencoba lagi batch ini, atau 's' untuk lewati batch, atau 'key' ganti API key:")
                pilihan_err = input(">> ").strip().lower()
                if pilihan_err == 's':
                    break
                elif pilihan_err == 'key':
                    kunci_baru = minta_api_key_baru()
                    if kunci_baru:
                        current_api_key = kunci_baru
                        daftar_model = dapatkan_daftar_model_aktif(current_api_key)
                        model_idx = 0
                time.sleep(2)
                continue

        if not batch_berhasil or res is None:
            print(f" [!] Batch {idx_batch} dilewati karena gagal diproses.")
            continue

        # 7. Parsing Hasil Evaluasi AI
        res_json = res.json()
        try:
            teks_hasil = res_json["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            print(f" [!] Format respons AI tidak sesuai pada Batch {idx_batch}: {e}")
            continue

        for siswa in chunk:
            nama_s = siswa["nama"]
            kelas_s = siswa["kelas"]
            nis_s = siswa["nis"]
            list_foto = siswa["foto"]

            # Matching nama siswa dengan regex
            pola_siswa = rf"(?:-|\*)*\s*SISWA:\s*(?:\*|_)*{re.escape(nama_s)}(?:\*|_)*\s*(?:-|\*)*(.*?)(?=(?:-|\*)*\s*SISWA:|$)"
            match_blok = re.search(pola_siswa, teks_hasil, re.DOTALL | re.IGNORECASE)

            if not match_blok:
                nama_depan = nama_s.split()[0]
                pola_depan = rf"(?:-|\*)*\s*SISWA:\s*(?:\*|_)*[^\n]*{re.escape(nama_depan)}[^\n]*(?:\*|_)*\s*(?:-|\*)*(.*?)(?=(?:-|\*)*\s*SISWA:|$)"
                match_blok = re.search(pola_depan, teks_hasil, re.DOTALL | re.IGNORECASE)

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
                "Kelas": kelas_s,
                "NIS": nis_s,
                "Nama Siswa": nama_s,
                "Jumlah Halaman": len(list_foto),
                "Nilai": nilai,
                "Evaluasi Konsep / Catatan": catatan
            })
            tag_kelas = f"[{kelas_s}] " if kelas_s != "-" else ""
            print(f"  |-- {tag_kelas}{nama_s} -> NILAI: {nilai}")

        # Simpan progres berkala ke Excel
        try:
            df_temp = pd.DataFrame(hasil_rekap)
            if format_mode == "file" and all(s["Kelas"] == "-" for s in hasil_rekap) and all(s["NIS"] == "-" for s in hasil_rekap):
                df_temp = df_temp.drop(columns=["Kelas", "NIS"])
            elif format_mode == "file" and all(s["Kelas"] == "-" for s in hasil_rekap):
                df_temp = df_temp.drop(columns=["Kelas"])
            df_temp.to_excel(OUTPUT_EXCEL, index=False)
        except Exception as e_save:
            print(f" [!] Peringatan saat menyimpan progres sementara ke Excel: {e_save}")

        time.sleep(3)

    # 8. Simpan Rekap Akhir ke Excel
    if hasil_rekap:
        df = pd.DataFrame(hasil_rekap)
        if format_mode == "file" and all(s["Kelas"] == "-" for s in hasil_rekap) and all(s["NIS"] == "-" for s in hasil_rekap):
            df = df.drop(columns=["Kelas", "NIS"])
        elif format_mode == "file" and all(s["Kelas"] == "-" for s in hasil_rekap):
            df = df.drop(columns=["Kelas"])
        df.to_excel(OUTPUT_EXCEL, index=False)
        print("\n" + "=" * 65)
        print(f" [SEMUA SELESAI] Rekapitulasi nilai berhasil disimpan di: {OUTPUT_EXCEL}")
        print(f" Total siswa dinilai: {len(hasil_rekap)}")
        print(" Aplikasi dikembangkan oleh: Rosyi")
        print(" Terima kasih telah menggunakan Sistem Penilaian Otomatis!")
        print("=" * 65)
    else:
        print("\n[!] Tidak ada data siswa yang berhasil dinilai.")


if __name__ == "__main__":
    proses_penilaian()