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
CONFIG_PATH="$APP_PATH/app_data/config.py"
MAX_BACKUPS=10  # Maksimal backup yang disimpan

# Format tanggal
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$BACKUP_ROOT/$DATE"

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

# 3. Backup Config (opsional - hapus API key dulu)
echo -e "${YELLOW}🔧 Backup config (tanpa API key)...${NC}"
if [ -f "$CONFIG_PATH" ]; then
    # Backup config tapi hapus API key
    grep -v "DEEPSEEK_API_KEY" "$CONFIG_PATH" > "$BACKUP_DIR/config.py"
    echo -e "   ✅ Config: ${GREEN}config.py${NC} (API key dihapus)"
fi

# 4. Buat info file
cat > "$BACKUP_DIR/backup_info.txt" << EOF
Backup Date: $(date)
App Path: $APP_PATH
Database: $(basename "$DB_PATH")
Size: $(du -h "$DB_PATH" 2>/dev/null | cut -f1 || echo "N/A")
EOF

# 5. Compress backup (opsional)
echo -e "${YELLOW}📦 Mengcompress backup...${NC}"
cd "$BACKUP_ROOT"
tar -czf "$DATE.tar.gz" "$DATE" 2>/dev/null
rm -rf "$DATE"  # Hapus folder setelah di-compress
echo -e "   ✅ Compressed: ${GREEN}$DATE.tar.gz${NC}"

# 6. Hapus backup lama (lebih dari MAX_BACKUPS)
echo -e "${YELLOW}🧹 Membersihkan backup lama...${NC}"
cd "$BACKUP_ROOT"
BACKUP_COUNT=$(ls -1 *.tar.gz 2>/dev/null | wc -l)
if [ "$BACKUP_COUNT" -gt "$MAX_BACKUPS" ]; then
    ls -t *.tar.gz | tail -n +$((MAX_BACKUPS+1)) | xargs -r rm
    echo -e "   ✅ Menyimpan $MAX_BACKUPS backup terakhir"
fi

# 7. Hitung total size backup
TOTAL_SIZE=$(du -sh "$BACKUP_ROOT" 2>/dev/null | cut -f1)
echo ""
echo -e "${GREEN}✅ BACKUP SELESAI!${NC}"
echo -e "   📁 Lokasi: $BACKUP_ROOT"
echo -e "   💿 Total size: $TOTAL_SIZE"
echo -e "   📊 Total backup: $(ls -1 "$BACKUP_ROOT"/*.tar.gz 2>/dev/null | wc -l)"
