#!/bin/bash

# ============================================
# RESTORE SCRIPT - Daily Issue Logger
# ============================================

APP_PATH="$(cd "$(dirname "$0")" && pwd)"
BACKUP_ROOT="$APP_PATH/backup"

echo "📂 Daftar Backup Tersedia:"
echo "=========================="
ls -1 "$BACKUP_ROOT"/*.tar.gz 2>/dev/null | nl

if [ $? -ne 0 ]; then
    echo "❌ Tidak ada backup ditemukan!"
    exit 1
fi

echo ""
read -p "Pilih nomor backup yang akan direstore: " CHOICE

BACKUP_FILE=$(ls -1 "$BACKUP_ROOT"/*.tar.gz 2>/dev/null | sed -n "${CHOICE}p")

if [ -z "$BACKUP_FILE" ]; then
    echo "❌ Pilihan tidak valid!"
    exit 1
fi

echo "🔄 Merestore $BACKUP_FILE ..."

# Extract ke temporary folder
TMP_DIR="/tmp/daily-logger-restore"
mkdir -p "$TMP_DIR"
tar -xzf "$BACKUP_FILE" -C "$TMP_DIR"

# Cari folder hasil extract
EXTRACTED_DIR=$(find "$TMP_DIR" -type d -name "2*" | head -1)

if [ -n "$EXTRACTED_DIR" ]; then
    # Restore database
    if [ -f "$EXTRACTED_DIR/laporan_harian.db" ]; then
        cp "$EXTRACTED_DIR/laporan_harian.db" "$APP_PATH/app_data/"
        echo "✅ Database direstore"
    fi
    
    # Restore icon
    if [ -f "$EXTRACTED_DIR/icon.png" ]; then
        cp "$EXTRACTED_DIR/icon.png" "$APP_PATH/"
        echo "✅ Icon direstore"
    fi
fi

# Bersihkan
rm -rf "$TMP_DIR"
echo "✅ RESTORE SELESAI!"
