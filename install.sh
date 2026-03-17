#!/bin/bash

# Warna untuk output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

APP_PATH="$(cd "$(dirname "$0")" && pwd)"
APP_NAME="Daily Issue Logger"
DESKTOP_FILE="Laporan-Parkee.desktop"

echo -e "${GREEN}=== $APP_NAME - INSTALLATION ===${NC}"
echo -e "Path: $APP_PATH"
echo ""

# 1. Cek & Install Dependensi Sistem (Clipboard)
echo -e "${YELLOW}[1/7] Memeriksa dependensi sistem...${NC}"
if [ "$XDG_SESSION_TYPE" = "wayland" ]; then
    if ! command -v wl-paste &> /dev/null; then
        echo "   ⚠️  wl-clipboard tidak ditemukan, menginstal..."
        sudo apt-get update && sudo apt-get install -y wl-clipboard
    fi
else
    if ! command -v xclip &> /dev/null; then
        echo "   ⚠️  xclip tidak ditemukan, menginstal..."
        sudo apt-get update && sudo apt-get install -y xclip
    fi
fi

# 2. Cek Python Virtual Environment
echo -e "${YELLOW}[2/7] Memeriksa Python virtual environment...${NC}"
if ! command -v python3-venv &> /dev/null; then
    echo "   ⚠️  python3-venv tidak ditemukan, menginstal..."
    sudo apt-get install -y python3-venv python3-pip
fi

# 3. Buat Virtual Environment
if [ ! -d "$APP_PATH/venv" ]; then
    echo "   📦 Membuat virtual environment..."
    python3 -m venv "$APP_PATH/venv"
else
    echo "   ✅ Virtual environment sudah ada"
fi

# 4. Install Library Python
echo -e "${YELLOW}[3/7] Menginstall dependensi Python...${NC}"
source "$APP_PATH/venv/bin/activate"
pip install --upgrade pip -q
pip install -r "$APP_PATH/requirements.txt" -q
echo "   ✅ Semua library terinstall"

# 5. Download Model AI (jika belum ada)
echo -e "${YELLOW}[4/7] Memeriksa model AI...${NC}"
MODEL_FILE="$APP_PATH/app_data/SmolLM2-1.7B-Instruct-Q2_K.gguf"
if [ ! -f "$MODEL_FILE" ]; then
    echo "   ⬇️  Mendownload model offline (sekitar 700MB)..."
    wget -q --show-progress -O "$MODEL_FILE" "https://huggingface.co/bartowski/SmolLM2-1.7B-Instruct-GGUF/resolve/main/SmolLM2-1.7B-Instruct-Q2_K.gguf"
else
    echo "   ✅ Model AI sudah ada"
fi

# 6. Buat Icon (jika belum ada)
echo -e "${YELLOW}[5/7] Memeriksa icon aplikasi...${NC}"
if [ ! -f "$APP_PATH/icon.png" ]; then
    echo "   🖼️  Membuat icon placeholder..."
    # Buat icon sederhana (kotak biru dengan tulisan "LOG")
    convert -size 64x64 xc:navy -font Helvetica -pointsize 20 -fill white -gravity center -draw "text 0,0 'LOG'" "$APP_PATH/icon.png" 2>/dev/null || touch "$APP_PATH/icon.png"
else
    echo "   ✅ Icon sudah ada"
fi

# 7. Buat Shortcut .desktop dengan WMClass yang benar
echo -e "${YELLOW}[6/7] Membuat shortcut aplikasi...${NC}"

# Deteksi WMClass (default Tk untuk aplikasi Tkinter)
WMCLASS="Tk"
echo "   🖥️  Menggunakan WMClass: $WMCLASS"

cat > "$APP_PATH/$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Name=$APP_NAME
Comment=Aplikasi Laporan Harian Parkee (AI & OCR)
Exec=$APP_PATH/venv/bin/python3 $APP_PATH/app_data/main.py
Path=$APP_PATH
Icon=$APP_PATH/icon.png
Terminal=false
Type=Application
Categories=Utility;Office;
StartupNotify=true
StartupWMClass=$WMCLASS
EOF

chmod +x "$APP_PATH/$DESKTOP_FILE"
echo "   ✅ Shortcut dibuat di: $APP_PATH/$DESKTOP_FILE"

# 8. Copy ke semua lokasi
echo -e "${YELLOW}[7/7] Memasang shortcut ke berbagai lokasi...${NC}"

# Ke folder aplikasi lokal (muncul di menu)
mkdir -p "$HOME/.local/share/applications"
cp "$APP_PATH/$DESKTOP_FILE" "$HOME/.local/share/applications/"
chmod +x "$HOME/.local/share/applications/$DESKTOP_FILE"
echo "   📋 → Menu Aplikasi"

# Ke Desktop (jika ada)
if [ -d "$HOME/Desktop" ]; then
    cp "$APP_PATH/$DESKTOP_FILE" "$HOME/Desktop/"
    chmod +x "$HOME/Desktop/$DESKTOP_FILE"
    echo "   🖥️ → Desktop"
    
    # Di GNOME, file .desktop di desktop perlu di-trust
    gio set "$HOME/Desktop/$DESKTOP_FILE" metadata::trusted true 2>/dev/null || true
fi

# Update database aplikasi
update-desktop-database "$HOME/.local/share/applications/" 2>/dev/null || true

echo ""
echo -e "${GREEN}✅ INSTALASI SELESAI!${NC}"
echo ""
echo "📌 Cara menjalankan aplikasi:"
echo "   1. Klik dua kali shortcut di DESKTOP"
echo "   atau"
echo "   2. Cari '$APP_NAME' di MENU APLIKASI"
echo ""
echo "📌 Cara pin ke taskbar/dock:"
echo "   1. Jalankan aplikasi (klik shortcut)"
echo "   2. Klik kanan ikon yang muncul di dock"
echo "   3. Pilih 'Add to Favorites'"
echo ""
echo "📌 Jika icon tidak muncul di dock dengan benar:"
echo "   1. Jalankan: xprop WM_CLASS"
echo "   2. Klik window aplikasi"
echo "   3. Edit StartupWMClass di file .desktop sesuai hasil"
echo ""

# Tanya apakah mau langsung jalankan
read -p "🚀 Jalankan aplikasi sekarang? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Menjalankan aplikasi..."
    "$APP_PATH/venv/bin/python3" "$APP_PATH/app_data/main.py"
fi
