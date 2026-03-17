import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import ImageGrab, Image
import os
import threading
from datetime import datetime
import pandas as pd

import database
from ai_core import AIProcessor
from sidebar import Sidebar
from main_panel import MainPanel
from forms import FormManual, FormEdit

class DailyIssueLoggerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("System Admin - Daily Issue Logger")
        self.root.geometry("1050x650")
        self.root.bind('<Control-v>', lambda event: self.paste_dari_clipboard())
        self.root.bind('<Delete>', lambda event: self.hapus_baris_terpilih())

        self.list_progress = ["NOT CHECK", "PROGRESS", "ON ESCALATION", "DONE"]
        self.list_supeng = ["Panji", "Andra", "Fahmi", "Naufal", "Dzikri", "Davon",
                            "Said", "Dendi", "Aidil", "Haris", "Martoyo",
                            "Fahrul", "Imam", "Riki"]
        self.llm_mode = tk.StringVar(value="Online (DeepSeek)")

        self.ai = AIProcessor()
        self.all_data = []

        # Buat komponen UI
        self.sidebar = Sidebar(self.root, self)
        self.main_panel = MainPanel(self.root, self)

        self.tampilkan_status("Siap")
        database.init_db()
        self.muat_data()

    def tampilkan_status(self, pesan):
        self.root.title(f"System Admin - Daily Issue Logger | Status: {pesan}")

    def muat_data(self):
        self.all_data = database.get_all_data()
        self.muat_data_ke_tabel(self.all_data)

    def muat_data_ke_tabel(self, data):
        # Hapus semua item di tree
        for item in self.main_panel.tree.get_children():
            self.main_panel.tree.delete(item)
        for row in data:
            self.main_panel.tree.insert("", "end", values=row)

    # ===== METHOD UNTUK AI & INPUT =====
    def eksekusi_ai_dan_simpan_otomatis(self, gambar_obj):
        mode_pilihan = self.llm_mode.get()
        
        def progress_callback(step, message, percent=None):
            """Callback untuk progress dari AI core"""
            self.root.after(0, lambda: self._update_ai_progress(step, message, percent))
        
        def task():
            try:
                self.tampilkan_status("Memproses dengan AI...")
                hasil = self.ai.run_pipeline(
                    gambar_obj,
                    mode_pilihan,
                    progress_callback=progress_callback
                )
                
                self.root.after(0, self.hide_progress)
                
                if not hasil:
                    self.root.after(0, lambda: messagebox.showinfo("Info", "Tidak ada teks."))
                else:
                    tgl = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    database.insert_data(
                        hasil['lokasi'],
                        hasil['issue'],
                        hasil['link'],
                        "PROGRESS", "", "", tgl
                    )
                    self.root.after(0, self.muat_data)
                    
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, self.hide_progress)
                self.root.after(0, lambda: messagebox.showerror("Error AI", error_msg))
            finally:
                self.root.after(0, lambda: self.tampilkan_status("Siap"))
        
        threading.Thread(target=task, daemon=True).start()        
        
    def _update_ai_progress(self, step, message, percent=None):
        """Update progress bar dari thread AI"""
        if not hasattr(self, "progress_frame"):
            self.show_progress(message, indeterminate=(percent is None))
        
        if percent is not None:
            self.update_progress(percent, message)
        elif hasattr(self, "progress_label"):
            self.progress_label.config(text=f"🔄 {message}")

    def pilih_file_screenshot(self):
        default_dir = os.path.expanduser("~/Pictures/Screenshots")
        if not os.path.exists(default_dir):
            default_dir = os.path.expanduser("~")
        file_path = filedialog.askopenfilename(
            initialdir=default_dir, title="Pilih Screenshot",
            filetypes=(("Image files", "*.png *.jpg *.jpeg"), ("All files", "*.*")))
        if file_path:
            try:
                self.eksekusi_ai_dan_simpan_otomatis(Image.open(file_path))
            except Exception as e:
                messagebox.showerror("Error Gambar", str(e))

    def paste_dari_clipboard(self):
        try:
            img = ImageGrab.grabclipboard()
            if isinstance(img, Image.Image):
                self.eksekusi_ai_dan_simpan_otomatis(img)
            else:
                messagebox.showwarning("Peringatan", "Clipboard kosong atau bukan gambar.")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membaca clipboard: {str(e)}")

    # ===== METHOD MANAJEMEN DATA =====
    def hapus_baris_terpilih(self, event=None):
        selected = self.main_panel.tree.selection()
        if not selected:
            messagebox.showwarning("Peringatan", "Pilih data yang ingin dihapus!")
            return
        jumlah = len(selected)
        if not messagebox.askyesno("Konfirmasi", f"Yakin ingin menghapus {jumlah} data terpilih?"):
            return
        ids = [self.main_panel.tree.item(item)['values'][7] for item in selected]
        database.delete_multiple(ids)
        self.muat_data()
        messagebox.showinfo("Sukses", f"{jumlah} data berhasil dihapus.")

    def hapus_semua_data(self):
        if not self.all_data:
            messagebox.showinfo("Info", "Tidak ada data untuk dihapus.")
            return
        jumlah = len(self.all_data)
        if not messagebox.askyesno(
                "Konfirmasi",
                f"Yakin ingin menghapus SEMUA data ({jumlah} baris)?\nTindakan ini tidak dapat dibatalkan."):
            return
        database.delete_all()
        self.muat_data()
        messagebox.showinfo("Sukses", "Semua data telah dihapus.")

    def buka_form_manual(self):
        FormManual(self.root, self)

    def edit_data_terpilih(self, event=None):
        selected = self.main_panel.tree.selection()
        if not selected:
            messagebox.showwarning("Peringatan", "Pilih baris data yang ingin diedit!")
            return
        if len(selected) > 1:
            messagebox.showwarning("Peringatan", "Hanya satu baris yang dapat diedit dalam satu waktu.")
            return
        item = selected[0]
        v = self.main_panel.tree.item(item)['values']
        id_db = v[7]
        FormEdit(self.root, self, id_db, v)

    def export_excel(self):
        baris_tabel = self.main_panel.tree.get_children()
        if not baris_tabel:
            messagebox.showwarning("Kosong", "Tidak ada data di tabel untuk diekspor.")
            return
        data_export = [self.main_panel.tree.item(item)['values'][:7] for item in baris_tabel]
        df = pd.DataFrame(data_export, columns=["Lokasi", "Issue", "Link", "Progress",
                                                 "Supeng", "Root Cause", "Tanggal"])
        nama_file_default = f"Laporan_Issue_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        path_simpan = filedialog.asksaveasfilename(
            initialfile=nama_file_default, defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")], title="Simpan Laporan Excel")
        if not path_simpan:
            return
        try:
            df.to_excel(path_simpan, index=False)
            messagebox.showinfo("Sukses", f"Data berhasil diekspor ({len(df)} baris) ke:\n{path_simpan}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Gagal menyimpan:\n{str(e)}")
    
    # ===== PROGRESS BAR METHODS =====
    def show_progress(self, message="Processing...", indeterminate=True):
        self.hide_progress()

        self.progress_frame = tk.Frame(self.root, bg="#f0f0f0", height=30)
        self.progress_frame.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=10,
            pady=(0, 10),
        )

        self.progress_label = tk.Label(
            self.progress_frame,
            text=message,
            bg="#f0f0f0",
            font=("Arial", 9),
        )
        self.progress_label.pack(side="left", padx=10)

        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            mode="indeterminate" if indeterminate else "determinate",
            length=200,
        )
        self.progress_bar.pack(side="left", padx=10)

        if indeterminate:
            self.progress_bar.start(10)

        self.progress_percent = tk.Label(
            self.progress_frame,
            text="",
            bg="#f0f0f0",
            font=("Arial", 9),
        )
        self.progress_percent.pack(side="left", padx=5)

        self.root.update_idletasks()

    def update_progress(self, value, message=None):
        if hasattr(self, "progress_bar"):
            self.progress_bar["mode"] = "determinate"
            self.progress_bar["value"] = value

            if message:
                self.progress_label.config(text=message)

            self.progress_percent.config(text=f"{value}%")
            self.root.update_idletasks()

    def hide_progress(self):
        if hasattr(self, "progress_frame"):
            self.progress_frame.destroy()
            del self.progress_frame
