#!/bin/bash

# Warna untuk output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

APP_PATH="$(cd "$(dirname "$0")" && pwd)"
APP_NAME="Daily Issue Logger"
DESKTOP_FILE="daily-issue-logger.desktop"

echo -e "${GREEN}=== $APP_NAME - INSTALLATION ===${NC}"
echo -e "Path: $APP_PATH"
echo ""

# 1. Cek & Install Dependensi Sistem (Clipboard)
echo -e "${YELLOW}[1/9] Memeriksa dependensi sistem...${NC}"
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
echo -e "${YELLOW}[2/9] Memeriksa Python virtual environment...${NC}"
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
echo -e "${YELLOW}[3/9] Menginstall dependensi Python...${NC}"
source "$APP_PATH/venv/bin/activate"
pip install --upgrade pip -q
pip install -r "$APP_PATH/requirements.txt" -q
echo "   ✅ Semua library terinstall"

# 5. Download Model AI (jika belum ada)
echo -e "${YELLOW}[4/9] Memeriksa model AI...${NC}"
MODEL_FILE="$APP_PATH/app_data/SmolLM2-1.7B-Instruct-Q2_K.gguf"
if [ ! -f "$MODEL_FILE" ]; then
    echo "   ⬇️  Mendownload model offline (sekitar 700MB)..."
    wget -q --show-progress -O "$MODEL_FILE" "https://huggingface.co/bartowski/SmolLM2-1.7B-Instruct-GGUF/resolve/main/SmolLM2-1.7B-Instruct-Q2_K.gguf"
else
    echo "   ✅ Model AI sudah ada"
fi

# 6. Buat Icon (jika belum ada)
echo -e "${YELLOW}[5/9] Memeriksa icon aplikasi...${NC}"
if [ ! -f "$APP_PATH/icon.png" ]; then
    echo "   🖼️  Membuat icon placeholder..."
    # Buat icon sederhana (kotak biru dengan tulisan "LOG")
    convert -size 64x64 xc:navy -font Helvetica -pointsize 20 -fill white -gravity center -draw "text 0,0 'LOG'" "$APP_PATH/icon.png" 2>/dev/null || touch "$APP_PATH/icon.png"
else
    echo "   ✅ Icon sudah ada"
fi

# 7. Buat Shortcut .desktop dengan WMClass yang benar
echo -e "${YELLOW}[6/9] Membuat shortcut aplikasi...${NC}"

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

# 8. Copy shortcut ke semua lokasi
echo -e "${YELLOW}[7/9] Memasang shortcut ke berbagai lokasi...${NC}"

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

# ===== FITUR BACKUP OTOMATIS =====
echo -e "${YELLOW}[8/9] Mengkonfigurasi backup otomatis...${NC}"

# Buat folder backup
mkdir -p "$APP_PATH/backup"

# Buat script backup jika belum ada
if [ ! -f "$APP_PATH/backup.sh" ]; then
    echo "   📝 Membuat script backup..."
    cat > "$APP_PATH/backup.sh" << 'EOF'
#!/bin/bash

# ============================================
# BACKUP SCRIPT - Daily Issue Logger
# ============================================

# Warna output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Ambil lokasi script ini berada
APP_PATH="$(cd "$(dirname "$0")" && pwd)"
BACKUP_ROOT="$APP_PATH/backup"
DB_PATH="$APP_PATH/app_data/laporan_harian.db"
ICON_PATH="$APP_PATH/icon.png"
MAX_BACKUPS=10

# Format tanggal
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$BACKUP_ROOT/$DATE"

# Header
echo -e "${BLUE}================================${NC}"
echo -e "${GREEN}📦 BACKUP DAILY ISSUE LOGGER${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Buat folder backup
mkdir -p "$BACKUP_DIR"

# 1. Backup Database
echo -e "${YELLOW}💾 Backup database...${NC}"
if [ -f "$DB_PATH" ]; then
    cp "$DB_PATH" "$BACKUP_DIR/"
    DB_SIZE=$(du -h "$DB_PATH" | cut -f1)
    echo -e "   ✅ Database: ${GREEN}laporan_harian.db${NC} ($DB_SIZE)"
else
    echo -e "   ⚠️  Database tidak ditemukan (masih kosong)"
fi

# 2. Backup Icon
echo -e "${YELLOW}🖼️  Backup icon...${NC}"
if [ -f "$ICON_PATH" ]; then
    cp "$ICON_PATH" "$BACKUP_DIR/"
    echo -e "   ✅ Icon: ${GREEN}icon.png${NC}"
else
    echo -e "   ⚠️  Icon tidak ditemukan"
fi

# 3. Compress backup
echo -e "${YELLOW}📦 Mengcompress backup...${NC}"
cd "$BACKUP_ROOT"
tar -czf "$DATE.tar.gz" "$DATE" 2>/dev/null
rm -rf "$DATE"
echo -e "   ✅ Compressed: ${GREEN}$DATE.tar.gz${NC}"

# 4. Hapus backup lama
echo -e "${YELLOW}🧹 Membersihkan backup lama...${NC}"
cd "$BACKUP_ROOT"
BACKUP_COUNT=$(ls -1 *.tar.gz 2>/dev/null | wc -l)
if [ "$BACKUP_COUNT" -gt "$MAX_BACKUPS" ]; then
    ls -t *.tar.gz | tail -n +$((MAX_BACKUPS+1)) | xargs -r rm
    echo -e "   ✅ Menyimpan $MAX_BACKUPS backup terakhir"
fi

# 5. Hitung total size
TOTAL_SIZE=$(du -sh "$BACKUP_ROOT" 2>/dev/null | cut -f1)
echo ""
echo -e "${GREEN}✅ BACKUP SELESAI!${NC}"
echo -e "   📁 Lokasi: $BACKUP_ROOT"
echo -e "   💿 Total size: $TOTAL_SIZE"
EOF
    echo "   ✅ Script backup.sh dibuat"
fi

# Buat script restore
if [ ! -f "$APP_PATH/restore.sh" ]; then
    echo "   📝 Membuat script restore..."
    cat > "$APP_PATH/restore.sh" << 'EOF'
#!/bin/bash

# ============================================
# RESTORE SCRIPT - Daily Issue Logger
# ============================================

APP_PATH="$(cd "$(dirname "$0")" && pwd)"
BACKUP_ROOT="$APP_PATH/backup"

echo -e "${BLUE}================================${NC}"
echo -e "${GREEN}📦 RESTORE DAILY ISSUE LOGGER${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Cek apakah ada backup
if [ ! -d "$BACKUP_ROOT" ] || [ -z "$(ls -A "$BACKUP_ROOT"/*.tar.gz 2>/dev/null)" ]; then
    echo -e "${RED}❌ Tidak ada backup ditemukan!${NC}"
    exit 1
fi

# Tampilkan daftar backup
echo "📂 Daftar Backup Tersedia:"
echo "=========================="
ls -1 "$BACKUP_ROOT"/*.tar.gz 2>/dev/null | nl
echo ""

read -p "Pilih nomor backup yang akan direstore: " CHOICE

BACKUP_FILE=$(ls -1 "$BACKUP_ROOT"/*.tar.gz 2>/dev/null | sed -n "${CHOICE}p")

if [ -z "$BACKUP_FILE" ]; then
    echo -e "${RED}❌ Pilihan tidak valid!${NC}"
    exit 1
fi

echo -e "${YELLOW}🔄 Merestore $BACKUP_FILE ...${NC}"

# Extract ke temporary folder
TMP_DIR="/tmp/daily-logger-restore"
mkdir -p "$TMP_DIR"
tar -xzf "$BACKUP_FILE" -C "$TMP_DIR"

# Cari folder hasil extract
EXTRACTED_DIR=$(find "$TMP_DIR" -type d -name "2*" | head -1)

RESTORE_COUNT=0
if [ -n "$EXTRACTED_DIR" ]; then
    # Restore database
    if [ -f "$EXTRACTED_DIR/laporan_harian.db" ]; then
        cp "$EXTRACTED_DIR/laporan_harian.db" "$APP_PATH/app_data/"
        echo -e "   ✅ Database direstore"
        RESTORE_COUNT=$((RESTORE_COUNT + 1))
    fi
    
    # Restore icon
    if [ -f "$EXTRACTED_DIR/icon.png" ]; then
        cp "$EXTRACTED_DIR/icon.png" "$APP_PATH/"
        echo -e "   ✅ Icon direstore"
        RESTORE_COUNT=$((RESTORE_COUNT + 1))
    fi
fi

# Bersihkan temporary
rm -rf "$TMP_DIR"

if [ $RESTORE_COUNT -gt 0 ]; then
    echo ""
    echo -e "${GREEN}✅ RESTORE SELESAI!${NC}"
    echo -e "   📦 $RESTORE_COUNT file direstore"
else
    echo -e "${RED}❌ Tidak ada file yang direstore${NC}"
fi
EOF
    echo "   ✅ Script restore.sh dibuat"
fi

# Buat script backup manager
if [ ! -f "$APP_PATH/backup-manager.sh" ]; then
    echo "   📝 Membuat script backup manager..."
    cat > "$APP_PATH/backup-manager.sh" << 'EOF'
#!/bin/bash

# ============================================
# BACKUP MANAGER - Daily Issue Logger
# ============================================

APP_PATH="$(cd "$(dirname "$0")" && pwd)"
BACKUP_ROOT="$APP_PATH/backup"

case "$1" in
    "list")
        echo -e "${BLUE}📋 DAFTAR BACKUP${NC}"
        echo "=================="
        if [ -d "$BACKUP_ROOT" ] && [ "$(ls -A "$BACKUP_ROOT"/*.tar.gz 2>/dev/null)" ]; then
            ls -lh "$BACKUP_ROOT"/*.tar.gz 2>/dev/null | awk '{print "   " $9 " (" $5 ")"}'
        else
            echo "   Tidak ada backup"
        fi
        ;;
    "clean")
        echo -e "${YELLOW}🧹 Membersihkan backup...${NC}"
        if [ -d "$BACKUP_ROOT" ]; then
            COUNT=$(ls -1 "$BACKUP_ROOT"/*.tar.gz 2>/dev/null | wc -l)
            if [ "$COUNT" -gt 0 ]; then
                read -p "Hapus semua backup ($COUNT file)? (y/n): " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    rm -f "$BACKUP_ROOT"/*.tar.gz
                    echo -e "${GREEN}✅ Semua backup dihapus${NC}"
                fi
            else
                echo "   Tidak ada backup untuk dihapus"
            fi
        else
            echo "   Folder backup tidak ditemukan"
        fi
        ;;
    "size")
        echo -e "${BLUE}💿 TOTAL SIZE BACKUP${NC}"
        echo "======================"
        if [ -d "$BACKUP_ROOT" ]; then
            du -sh "$BACKUP_ROOT"
        else
            echo "   0B"
        fi
        ;;
    "cron")
        echo -e "${BLUE}⏰ CRONJOB STATUS${NC}"
        echo "=================="
        CRON=$(crontab -l 2>/dev/null | grep "backup.sh")
        if [ -n "$CRON" ]; then
            echo "   ✅ $CRON"
        else
            echo "   ❌ Tidak ada cronjob backup"
        fi
        ;;
    *)
        echo "📌 Backup Manager - Daily Issue Logger"
        echo ""
        echo "Usage: $0 {command}"
        echo ""
        echo "Commands:"
        echo "   list    - Lihat daftar backup"
        echo "   clean   - Hapus semua backup"
        echo "   size    - Lihat total ukuran backup"
        echo "   cron    - Cek status cronjob"
        ;;
esac
EOF
    echo "   ✅ Script backup-manager.sh dibuat"
fi

# BERI IZIN EXECUTE KE SEMUA SCRIPT BACKUP
echo -e "${YELLOW}[9/9] Memberi izin execute ke semua script...${NC}"
chmod +x "$APP_PATH/backup.sh" 2>/dev/null && echo "   ✅ backup.sh"
chmod +x "$APP_PATH/restore.sh" 2>/dev/null && echo "   ✅ restore.sh"
chmod +x "$APP_PATH/backup-manager.sh" 2>/dev/null && echo "   ✅ backup-manager.sh"
chmod +x "$APP_PATH"/*.sh 2>/dev/null
echo "   ✅ Semua script backup sudah executable"

# Tanya apakah mau setup cronjob
echo ""
read -p "🕒 Setup backup otomatis harian? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Cek apakah cron sudah ada
    CRON_JOB="0 2 * * * $APP_PATH/backup.sh > /dev/null 2>&1"
    
    if ! crontab -l 2>/dev/null | grep -F "$CRON_JOB" > /dev/null; then
        # Tambah ke crontab
        (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
        echo "   ✅ Cronjob ditambahkan: Backup setiap jam 2 pagi"
    else
        echo "   ⚠️  Cronjob sudah ada"
    fi
    
    # CEK DULU APAKAH ADA DATA SEBELUM MINTA BACKUP
    if [ -f "$APP_PATH/app_data/laporan_harian.db" ] && [ -s "$APP_PATH/app_data/laporan_harian.db" ]; then
        # Database ada dan tidak kosong
        DB_SIZE=$(du -h "$APP_PATH/app_data/laporan_harian.db" | cut -f1)
        echo -e "   📊 Database terdeteksi: $DB_SIZE"
        read -p "📦 Jalankan backup pertama sekarang? (y/n): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            "$APP_PATH/backup.sh"
        fi
    else
        echo -e "   📊 Database masih kosong (belum ada data)"
        echo -e "   ⏭️  Lewati backup pertama"
    fi
fi

echo ""
echo -e "${GREEN}✅ INSTALASI SELESAI!${NC}"
echo ""
echo "📌 Cara menjalankan aplikasi:"
echo "   1. Klik dua kali shortcut di DESKTOP"
echo "   atau"
echo "   2. Cari '$APP_NAME' di MENU APLIKASI"
echo ""
echo "📌 Manajemen Backup:"
echo "   ./backup.sh              - Backup manual"
echo "   ./restore.sh             - Restore data"
echo "   ./backup-manager.sh list - Lihat backup"
echo "   ./backup-manager.sh size - Lihat ukuran backup"
echo "   ./backup-manager.sh cron - Cek cronjob"
echo ""

# Tanya apakah mau langsung jalankan
read -p "🚀 Jalankan aplikasi sekarang? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Menjalankan aplikasi..."
    "$APP_PATH/venv/bin/python3" "$APP_PATH/app_data/main.py"
fi





echo ""
echo -e "${GREEN}✅ INSTALASI SELESAI!${NC}"
echo ""
echo "📌 Cara menjalankan aplikasi:"
echo "   1. Klik dua kali shortcut di DESKTOP"
echo "   atau"
echo "   2. Cari '$APP_NAME' di MENU APLIKASI"
echo ""
echo "📌 Manajemen Backup:"
echo "   ./backup.sh        - Backup manual"
echo "   ./restore.sh       - Restore data"
echo "   ./backup-manager.sh list  - Lihat backup"
echo ""

# Tanya apakah mau langsung jalankan
read -p "🚀 Jalankan aplikasi sekarang? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Menjalankan aplikasi..."
    "$APP_PATH/venv/bin/python3" "$APP_PATH/app_data/main.py"
fi
