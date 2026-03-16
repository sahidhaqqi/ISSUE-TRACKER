#!/bin/bash

# Ambil lokasi absolut dari folder aplikasi ini
APP_PATH="$(cd "$(dirname "$0")" && pwd)"
ICON_PATH="accessories-text-editor" # Bisa diganti path icon custom .png

echo "=== System Admin Daily Logger Setup ==="

# 1. Cek & Install Dependensi Sistem (Clipboard)
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

# 2. Cek Python Venv
if ! command -v python3-venv &> /dev/null; then
    sudo apt-get install -y python3-venv python3-pip
fi

if [ ! -d "$APP_PATH/venv" ]; then
    echo "[+] Membuat Virtual Environment..."
    python3 -m venv "$APP_PATH/venv"
fi

# 3. Otomatis Membuat Shortcut (Desktop Entry)
SHORTCUT_PATH="$HOME/.local/share/applications/laporan-parkee.desktop"
if [ ! -f "$SHORTCUT_PATH" ]; then
    echo "[+] Membuat shortcut di App Menu..."
    cat << EOM > "$SHORTCUT_PATH"
[Desktop Entry]
Version=1.0
Name=Daily Issue Logger
Comment=Aplikasi Laporan Harian Parkee (AI & OCR)
Exec=$APP_PATH/jalankan_aplikasi.sh
Path=$APP_PATH
Icon=$ICON_PATH
Terminal=false
Type=Application
Categories=Utility;Office;
EOM
    chmod +x "$SHORTCUT_PATH"
fi

# 4. Install Library & Model
source "$APP_PATH/venv/bin/activate"
echo "[+] Memeriksa dependensi AI..."
pip install -r "$APP_PATH/requirements.txt" -q

MODEL_FILE="$APP_PATH/app_data/SmolLM2-1.7B-Instruct-Q2_K.gguf"
if [ ! -f "$MODEL_FILE" ]; then
    echo "[+] Mendownload Model Offline..."
    wget -q --show-progress -O "$MODEL_FILE" "https://huggingface.co/bartowski/SmolLM2-1.7B-Instruct-GGUF/resolve/main/SmolLM2-1.7B-Instruct-Q2_K.gguf"
fi

# 5. Jalankan Aplikasi
echo "Memulai Aplikasi..."
python3 "$APP_PATH/app_data/main.py"
