# 📋 System Admin - Daily Issue Logger

Aplikasi Desktop (GUI) berbasis Python Tkinter untuk mencatat, mengelola, dan mengekstrak laporan *issue* operasional secara otomatis menggunakan kecerdasan buatan (AI) dan Optical Character Recognition (OCR).

Aplikasi ini menggunakan arsitektur **Thin Client**. Installer hanya berukuran beberapa Kilobyte, dan sistem akan secara cerdas mengunduh environment (PyTorch, DocTR) dan Model AI (GGUF) secara otomatis pada saat pertama kali dijalankan.

## ✨ Fitur Utama
* **🤖 AI Auto-Extraction:** * **Offline Mode:** Menggunakan model `SmolLM2-1.7B-Instruct` (Berjalan 100% lokal di CPU tanpa internet).
    * **Online Mode:** Terintegrasi dengan API DeepSeek untuk pemrosesan super cepat.
* **👁️ Smart OCR:** Otomatis membaca teks dari *screenshot* (mendukung X11 dan Wayland clipboard) menggunakan `doctr`.
* **💾 Local Database:** Semua log tersimpan aman di SQLite (`laporan_harian.db`).
* **📊 Excel Export:** Export data langsung ke format `.xlsx` berdasarkan filter pencarian yang aktif.
* **🎛️ Full CRUD:** Tambah, Edit, Hapus, dan Filter laporan dengan UI yang intuitif.

## 🚀 Cara Instalasi & Menjalankan

Anda tidak perlu menginstal Python, pip, atau dependensi secara manual. Semua sudah diotomatisasi.

1. Buka terminal dan *clone* repository ini:
   ```bash
   git clone [https://github.com/USERNAME_KAMU/Laporan_Parkee_App.git](https://github.com/USERNAME_KAMU/Laporan_Parkee_App.git)
   cd Laporan_Parkee_App
