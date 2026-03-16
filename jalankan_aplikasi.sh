#!/bin/bash
cd "$(dirname "$0")"

echo "=== System Admin Daily Logger Setup ==="

# 1. Cek Clipboard Handler
if [ "$XDG_SESSION_TYPE" = "wayland" ]; then
    if ! command -v wl-paste &> /dev/null; then
        echo "[+] Menginstal wl-clipboard..."
        sudo apt-get update && sudo apt-get install -y wl-clipboard
    fi
else
    if ! command -v xclip &> /dev/null; then
        echo "[+] Menginstal xclip..."
        sudo apt-get update && sudo apt-get install -y xclip
    fi
fi

# 2. Cek Virtual Environment (VENV)
if ! command -v python3-venv &> /dev/null; then
    echo "[+] Menginstal dependensi python venv..."
    sudo apt-get install -y python3-venv python3-pip
fi

# 3. Setup Lingkungan Isolasi Python
if [ ! -d "venv" ]; then
    echo "[+] Membuat Virtual Environment..."
    python3 -m venv venv
fi

# Aktifkan VENV
source venv/bin/activate

# 4. Install Library (Hanya jalan sekali kalau belum diinstall)
echo "[+] Memeriksa dependensi AI (Bisa memakan waktu saat pertama kali...)"
pip install -r requirements.txt 

# 5. Cek Model GGUF
MODEL_PATH="app_data/SmolLM2-1.7B-Instruct-Q2_K.gguf"
MODEL_URL="https://huggingface.co/bartowski/SmolLM2-1.7B-Instruct-GGUF/resolve/main/SmolLM2-1.7B-Instruct-Q2_K.gguf"

if [ ! -f "$MODEL_PATH" ]; then
    echo "=================================================="
    echo "Mendownload Model Offline SmolLM2 (644MB)..."
    echo "Pastikan internet kencang."
    echo "=================================================="
    wget --show-progress -O "$MODEL_PATH" "$MODEL_URL"
fi

# 6. Jalankan Aplikasi Murni (Tanpa PyInstaller)
echo "Memulai Aplikasi..."
python app_data/main.py
