# 📋 System Admin - Daily Issue Logger

Aplikasi Desktop (GUI) berbasis Python Tkinter untuk mencatat, mengelola, dan mengekstrak laporan *issue* operasional secara otomatis menggunakan kecerdasan buatan (AI) dan Optical Character Recognition (OCR).

![Aplikasi Screenshot](screenshot.png)

## ✨ Fitur Utama

### 🤖 **AI Auto-Extraction**
- **Online Mode:** Terintegrasi dengan API DeepSeek untuk pemrosesan super cepat
- **Offline Mode:** Menggunakan model `SmolLM2-1.7B-Instruct` (Berjalan 100% lokal di CPU tanpa internet)
- **Lazy Loading:** Model AI hanya dimuat saat dibutuhkan, hemat RAM

### 👁️ **Smart OCR**
- Otomatis membaca teks dari screenshot
- Mendukung X11 dan Wayland clipboard
- Menggunakan `python-doctr` untuk akurasi tinggi

### 💾 **Local Database**
- Semua log tersimpan aman di SQLite (`laporan_harian.db`)
- Tidak perlu koneksi internet
- Backup dan restore mudah

### 📊 **Export & Reporting**
- Export data ke format `.xlsx` (Excel)
- Filter berdasarkan tanggal, progress, lokasi
- Export hanya data yang tampil di layar

### 🎛️ **Full CRUD Operations**
- **Tambah:** Input manual atau auto dari AI
- **Edit:** Double-click pada baris untuk edit
- **Hapus:** Single delete, multi-select delete, atau hapus semua
- **Filter:** Filter real-time berdasarkan kolom

### 🖥️ **User Experience**
- Shortcut di Desktop, Menu Aplikasi, dan Taskbar
- Pin ke dock/taskbar dengan icon kustom
- Keyboard shortcut (Ctrl+V untuk paste screenshot)
- Detail panel untuk melihat data lengkap

## 💾 **Backup & Restore**

### Backup Manual
```bash
cd ~/ai/router/Laporan_Parkee_App
./backup.sh

Backup Otomatis (Cronjob)
Default: Setiap jam 2 pagi

Menyimpan: 10 backup terakhir

Lokasi: backup/ folder


## 🚀 **Cara Instalasi & Menjalankan**

### Persyaratan Sistem
- **OS:** Linux (Pop!_OS, Ubuntu, Debian, dll)
- **RAM:** Minimal 4GB (8GB direkomendasikan)
- **Storage:** 2GB free space (untuk model AI)
- **Internet:** Koneksi stabil (hanya untuk installasi pertama)

### Instalasi (Sekali Saja)

```bash
# Clone repository
git clone https://github.com/sahidhaqqi/ISSUE-TRACKER.git
cd ISSUE-TRACKER

# Jalankan installer
chmod +x install.sh
./install.sh


