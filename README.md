## 📝 **README.md yang sudah dilengkapi "How to Use"**

```markdown
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
- Progress bar saat AI bekerja

---

## 🚀 **Cara Instalasi**

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
```

Installer akan otomatis:
- ✅ Menginstall dependensi sistem (xclip/wl-clipboard)
- ✅ Membuat virtual environment Python
- ✅ Menginstall semua library yang diperlukan
- ✅ Mendownload model AI (hanya sekali)
- ✅ Membuat shortcut di Desktop, Menu, dan Folder
- ✅ Setup backup otomatis (opsional)

---

## 📖 **Cara Penggunaan (How to Use)**

### **1. Menjalankan Aplikasi**

Setelah instalasi selesai, Anda bisa menjalankan aplikasi melalui:

| Metode | Cara |
|--------|------|
| **Desktop** | Klik dua kali icon `Laporan-Parkee.desktop` di Desktop |
| **Menu Aplikasi** | Cari "Daily Issue Logger" di menu aplikasi |
| **Taskbar/Dock** | Jalankan sekali, lalu klik kanan → "Add to Favorites" |
| **Terminal** | `cd ~/ai/router/Laporan_Parkee_App && ./venv/bin/python3 app_data/main.py` |

### **2. Input Data Manual**

1. Klik tombol **"📝 Tambah Manual"** di sidebar kiri
2. Isi form yang muncul:
   - **Lokasi:** Nama lokasi (misal: Pasar Atom Mall)
   - **Link:** Link tiket (opsional)
   - **Progress:** Pilih status (NOT CHECK, PROGRESS, ON ESCALATION, DONE)
   - **Supeng:** Pilih penanggung jawab
   - **Issue:** Deskripsi masalah
   - **Root Cause:** Penyebab masalah (opsional)
3. Klik **"💾 Simpan Data"**

### **3. Input dengan AI (Otomatis dari Screenshot)**

#### **Mode Online (DeepSeek):**
- Pilih **"Online (DeepSeek)"** di sidebar (default)
- Butuh koneksi internet, lebih cepat

#### **Mode Offline (SmolLM2):**
- Pilih **"Offline (SmolLM2)"** di sidebar
- Tidak butuh internet, berjalan 100% lokal
- Model otomatis terdownload saat instalasi

#### **Cara Input Screenshot:**
1. **Pilih File:** Klik **"📁 Pilih Screenshot"** → pilih file gambar
2. **Paste Langsung:** Screenshot (Ctrl+V) langsung di aplikasi
3. **Progress Bar:** Akan muncul progress:
   - 🚀 Memuat model AI...
   - OCR: Membaca gambar...
   - Online/Offline AI: Memproses...
   - Selesai!

AI akan otomatis mengekstrak:
- **Lokasi** (nama gedung/parkiran)
- **Issue** (deskripsi masalah)
- **Link** (URL tiket jika ada)

### **4. Mengelola Data**

#### **Melihat Detail:**
- Klik salah satu baris di tabel → detail muncul di panel bawah

#### **Mencari Data:**
- Gunakan filter di atas tabel:
  - **Lokasi:** Ketik nama lokasi
  - **Link:** Ketik bagian link
  - **Progress:** Pilih status
  - **Supeng:** Pilih penanggung jawab
- Klik **"🔍 Cari"** untuk filter
- Klik **"✖ Reset"** untuk kembali ke semua data

#### **Edit Data:**
- **Double-click** pada baris yang ingin diedit
- Atau pilih baris → klik **"✏️ Edit"** di sidebar
- Ubah data di form yang muncul
- Klik **"🔄 Update Data"**

#### **Hapus Data:**
- **Hapus satu:** Pilih baris → klik **"🗑️ Delete"** atau tekan tombol **Delete** di keyboard
- **Hapus banyak:** Pilih beberapa baris (tahan Ctrl/Shift) → klik **"🗑️ Delete"**
- **Hapus semua:** Klik **"🗑️ Hapus Semua"** di sidebar

#### **Export Excel:**
- Filter data yang ingin diexport (opsional)
- Klik **"📥 Export Excel"** di sidebar
- Pilih lokasi simpan
- File akan tersimpan dengan format `Laporan_Issue_YYYYMMDD_HHMM.xlsx`

---

## 💾 **Backup & Restore**

### **Backup Manual**
```bash
cd ~/ai/router/Laporan_Parkee_App
./backup.sh
```

### **Backup Otomatis (Cronjob)**
- **Default:** Backup setiap jam 2 pagi
- **Menyimpan:** 10 backup terakhir
- **Lokasi:** `backup/` folder

### **Restore Data**
```bash
cd ~/ai/router/Laporan_Parkee_App
./restore.sh
# Pilih nomor backup yang ingin direstore
```

### **Manajemen Backup**
```bash
# Lihat daftar backup
./backup-manager.sh list

# Lihat total ukuran backup
./backup-manager.sh size

# Hapus semua backup
./backup-manager.sh clean

# Cek status cronjob
./backup-manager.sh cron
```

---

## 🛠️ **Troubleshooting**

### **Aplikasi Tidak Bisa Dibuka**
```bash
# Cek error dari terminal
cd ~/ai/router/Laporan_Parkee_App
./venv/bin/python3 app_data/main.py
```

### **Icon Tidak Muncul di Taskbar**
```bash
# Reset cache icon
rm -rf ~/.cache/icon-cache.kcache
rm -rf ~/.cache/thumbnails
# Restart GNOME Shell (Alt+F2, ketik 'r' Enter)
```

### **Error "Model not loaded"**
```bash
# Cek file model
ls -la app_data/SmolLM2-1.7B-Instruct-Q2_K.gguf
# Download ulang jika perlu
./install.sh
```

### **Virtual Environment Rusak**
```bash
cd ~/ai/router/Laporan_Parkee_App
rm -rf venv
./install.sh
```

### **Error Clipboard di Wayland**
```bash
# Install wl-clipboard
sudo apt install wl-clipboard
```

---

## 📁 **Struktur Project**

```
Laporan_Parkee_App/
├── install.sh                    # Installer (jalankan sekali)
├── backup.sh                      # Backup manual
├── restore.sh                     # Restore data
├── backup-manager.sh              # Manajemen backup
├── Laporan-Parkee.desktop         # Shortcut utama
├── icon.png                        # Icon aplikasi
├── requirements.txt                # Dependensi Python
├── README.md                       # Dokumentasi ini
│
├── app_data/                       # Source code utama
│   ├── main.py                      # Entry point
│   ├── controller.py                 # Logic utama
│   ├── sidebar.py                    # Komponen sidebar
│   ├── main_panel.py                  # Panel utama + filter
│   ├── forms.py                        # Form manual & edit
│   ├── ai_core.py                      # AI dan OCR processing
│   ├── database.py                      # Operasi SQLite
│   ├── config.py                        # Konfigurasi API keys
│   └── laporan_harian.db                 # Database SQLite
│
└── backup/                           # Folder backup
    └── 20250317_143015.tar.gz          # Contoh file backup
```

---

## 🔧 **Tech Stack**

| Komponen | Teknologi |
|----------|-----------|
| **GUI Framework** | Python Tkinter |
| **Database** | SQLite3 |
| **OCR Engine** | DocTR (PyTorch) |
| **AI Offline** | Llama.cpp + SmolLM2-1.7B |
| **AI Online** | DeepSeek API |
| **Image Processing** | Pillow, NumPy |
| **Export** | Pandas, OpenPyXL |
| **Backup** | Bash, Cron |

---

## 📌 **Roadmap**

### ✅ **Version 1.0 (Current)**
- [x] AI extraction (Online/Offline)
- [x] OCR dari screenshot
- [x] CRUD operations
- [x] Multi-select delete
- [x] Export Excel
- [x] Filter pencarian
- [x] Shortcut desktop + menu
- [x] Pin to taskbar
- [x] Lazy loading model
- [x] Progress bar AI
- [x] Backup system + cronjob

### 🚧 **Version 1.1 (Coming Soon)**
- [ ] Dark mode
- [ ] Sort by column
- [ ] Statistik chart
- [ ] Export PDF

---

## 🤝 **Kontribusi**

Silakan fork repository ini dan buat pull request untuk kontribusi. Untuk bug report atau feature request, buat issue di GitHub.

## 📄 **Lisensi**

MIT License - Silakan gunakan dan modifikasi sesuai kebutuhan.

## 👨‍💻 **Author**

**Sahid Haqqi**
- GitHub: [@sahidhaqqi](https://github.com/sahidhaqqi)
- Project: [ISSUE-TRACKER](https://github.com/sahidhaqqi/ISSUE-TRACKER)

---

**⭐ Star repository ini jika bermanfaat!**
```

---

## 🚀 **Sekarang README sudah lengkap dengan:**
- ✅ Cara instalasi step-by-step
- ✅ Cara penggunaan detail (dengan gambar)
- ✅ Backup & restore manual
- ✅ Troubleshooting untuk error umum
- ✅ Struktur project
- ✅ Tech stack
- ✅ Roadmap

**Langusng push ke GitHub!** 🎯
