#!/bin/bash

APP_PATH="$(cd "$(dirname "$0")" && pwd)"

case "$1" in
    "list")
        echo "📋 Daftar Backup:"
        ls -lh "$APP_PATH/backup"/*.tar.gz 2>/dev/null | awk '{print $9 " (" $5 ")"}'
        ;;
    "clean")
        read -p "Hapus semua backup? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -f "$APP_PATH/backup"/*.tar.gz
            echo "✅ Semua backup dihapus"
        fi
        ;;
    "size")
        du -sh "$APP_PATH/backup"
        ;;
    "cron")
        crontab -l | grep "backup.sh"
        ;;
    *)
        echo "Usage: $0 {list|clean|size|cron}"
        ;;
esac
