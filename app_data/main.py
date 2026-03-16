import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import ImageGrab, Image
import os
import threading
from datetime import datetime
import pandas as pd

import database
from ai_core import AIProcessor

class DailyIssueLoggerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("System Admin - Daily Issue Logger")
        self.root.geometry("1050x650")
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.bind('<Control-v>', lambda event: self.paste_dari_clipboard())

        self.list_progress = ["NOT CHECK", "PROGRESS", "ON ESCALATION", "DONE"]
        self.list_supeng = ["Panji", "Andra", "Fahmi", "Naufal", "Dzikri", "Davon", "Said", "Dendi", "Aidil", "Haris", "Martoyo", "Fahrul", "Imam", "Riki"]
        self.llm_mode = tk.StringVar(value="Online (DeepSeek)")
        
        self.ai = AIProcessor()

        self.setup_sidebar()
        self.setup_main_panel()

        self.tampilkan_status("Memuat Model AI...")
        threading.Thread(target=self.load_models_bg, daemon=True).start()
        
        database.init_db()
        self.muat_data()

    def load_models_bg(self):
        try:
            self.ai.load_models()
            self.root.after(0, lambda: self.tampilkan_status("Siap"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Gagal muat model: {e}"))
            self.root.after(0, lambda: self.tampilkan_status("Error Model"))

    def tampilkan_status(self, pesan):
        self.root.title(f"System Admin - Daily Issue Logger | Status: {pesan}")

    def muat_data(self):
        self.all_data = database.get_all_data()
        self.muat_data_ke_tabel(self.all_data)

    def eksekusi_ai_dan_simpan_otomatis(self, gambar_obj):
        mode_pilihan = self.llm_mode.get()
        def task():
            try:
                self.tampilkan_status("Memproses dengan AI...")
                hasil = self.ai.run_pipeline(gambar_obj, mode_pilihan)
                if not hasil:
                    self.root.after(0, lambda: messagebox.showinfo("Info", "Tidak ada teks."))
                else:
                    tgl = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    database.insert_data(hasil['lokasi'], hasil['issue'], hasil['link'], "PROGRESS", "", "", tgl)
                    self.root.after(0, self.muat_data)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error AI", str(e)))
            finally:
                self.root.after(0, lambda: self.tampilkan_status("Siap"))
                
        threading.Thread(target=task, daemon=True).start()

    def pilih_file_screenshot(self):
        default_dir = os.path.expanduser("~/Pictures/Screenshots")
        if not os.path.exists(default_dir):
            default_dir = os.path.expanduser("~")
        file_path = filedialog.askopenfilename(initialdir=default_dir, title="Pilih Screenshot",
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

    def hapus_baris_terpilih(self):
        selected_item = self.tree.selection()
        if selected_item:
            if messagebox.askyesno("Hapus", "Yakin ingin menghapus data ini?"):
                id_db = self.tree.item(selected_item[0])['values'][7]
                database.delete_data(id_db)
                self.muat_data()

    def buka_form_manual(self):
        top = tk.Toplevel(self.root)
        top.title("Input Log Manual")
        top.geometry("450x550")
        top.grab_set()

        tk.Label(top, text="Input Data Manual", font=("Arial", 11, "bold")).pack(pady=10)
        form_frame = tk.Frame(top, padx=20)
        form_frame.pack(fill="both", expand=True)

        fields = [("Lokasi:", ttk.Entry), ("Link:", ttk.Entry)]
        entries = {}
        for i, (label, widget) in enumerate(fields):
            tk.Label(form_frame, text=label).grid(row=i, column=0, sticky="nw", pady=5)
            e = widget(form_frame, width=35)
            e.grid(row=i, column=1, pady=5)
            entries[label] = e

        tk.Label(form_frame, text="Progress:").grid(row=2, column=0, sticky="nw", pady=5)
        combo_progress = ttk.Combobox(form_frame, values=["", "NOT CHECK", "PROGRESS", "ON ESCALATION", "DONE"], state="readonly", width=32)
        combo_progress.grid(row=2, column=1, pady=5)
        combo_progress.current(0)

        tk.Label(form_frame, text="Supeng:").grid(row=3, column=0, sticky="nw", pady=5)
        combo_supeng = ttk.Combobox(form_frame, values=self.list_supeng, width=32)
        combo_supeng.grid(row=3, column=1, pady=5)

        tk.Label(form_frame, text="Issue:").grid(row=4, column=0, sticky="nw", pady=5)
        text_issue = tk.Text(form_frame, width=35, height=4)
        text_issue.grid(row=4, column=1, pady=5)

        tk.Label(form_frame, text="Root Cause:").grid(row=5, column=0, sticky="nw", pady=5)
        text_rc = tk.Text(form_frame, width=35, height=4)
        text_rc.grid(row=5, column=1, pady=5)

        def simpan_manual():
            database.insert_data(
                entries["Lokasi:"].get(),
                text_issue.get("1.0", tk.END).strip(),
                entries["Link:"].get(),
                combo_progress.get(),
                combo_supeng.get(),
                text_rc.get("1.0", tk.END).strip(),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            top.destroy()
            self.muat_data()
            messagebox.showinfo("Sukses", "Data manual berhasil ditambahkan.")

        tk.Button(top, text="💾 Simpan Data", command=simpan_manual, bg="#2ecc71", fg="white", font=("Arial", 10, "bold")).pack(pady=20)

    def edit_data_terpilih(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Pilih baris data yang ingin diedit!")
            return

        v = self.tree.item(selected_item[0])['values']
        id_db = v[7]

        top = tk.Toplevel(self.root)
        top.title("Edit Log Data")
        top.geometry("450x550")
        top.grab_set()

        tk.Label(top, text="Edit Data Issue", font=("Arial", 11, "bold")).pack(pady=10)
        form_frame = tk.Frame(top, padx=20)
        form_frame.pack(fill="both", expand=True)

        tk.Label(form_frame, text="Lokasi:").grid(row=0, column=0, sticky="nw", pady=5)
        entry_lokasi = ttk.Entry(form_frame, width=35)
        entry_lokasi.grid(row=0, column=1, pady=5)
        entry_lokasi.insert(0, v[0])

        tk.Label(form_frame, text="Link:").grid(row=1, column=0, sticky="nw", pady=5)
        entry_link = ttk.Entry(form_frame, width=35)
        entry_link.grid(row=1, column=1, pady=5)
        entry_link.insert(0, v[2] if v[2] != '-' else "")

        tk.Label(form_frame, text="Progress:").grid(row=2, column=0, sticky="nw", pady=5)
        combo_progress = ttk.Combobox(form_frame, values=["", "NOT CHECK", "PROGRESS", "ON ESCALATION", "DONE"], state="readonly", width=32)
        combo_progress.grid(row=2, column=1, pady=5)
        combo_progress.set(v[3])

        tk.Label(form_frame, text="Supeng:").grid(row=3, column=0, sticky="nw", pady=5)
        combo_supeng = ttk.Combobox(form_frame, values=self.list_supeng, width=32)
        combo_supeng.grid(row=3, column=1, pady=5)
        combo_supeng.set(v[4])

        tk.Label(form_frame, text="Issue:").grid(row=4, column=0, sticky="nw", pady=5)
        text_issue = tk.Text(form_frame, width=35, height=4)
        text_issue.grid(row=4, column=1, pady=5)
        text_issue.insert("1.0", v[1])

        tk.Label(form_frame, text="Root Cause:").grid(row=5, column=0, sticky="nw", pady=5)
        text_rc = tk.Text(form_frame, width=35, height=4)
        text_rc.grid(row=5, column=1, pady=5)
        rc = v[5] if v[5] else ""
        if rc and rc != "Belum dianalisis.":
            text_rc.insert("1.0", rc)

        def update_ke_db():
            database.update_data(
                id_db,
                entry_lokasi.get(),
                text_issue.get("1.0", tk.END).strip(),
                entry_link.get(),
                combo_progress.get(),
                combo_supeng.get(),
                text_rc.get("1.0", tk.END).strip()
            )
            self.muat_data()
            top.destroy()
            messagebox.showinfo("Sukses", "Data berhasil diupdate.")

        tk.Button(top, text="🔄 Update Data", command=update_ke_db, bg="#f39c12", fg="white", font=("Arial", 10, "bold")).pack(pady=20)

    def export_excel(self):
        baris_tabel = self.tree.get_children()
        if not baris_tabel:
            messagebox.showwarning("Kosong", "Tidak ada data di tabel untuk diekspor.")
            return
        data_export = [self.tree.item(item)['values'][:7] for item in baris_tabel]
        df = pd.DataFrame(data_export, columns=["Lokasi", "Issue", "Link", "Progress", "Supeng", "Root Cause", "Tanggal"])
        nama_file_default = f"Laporan_Issue_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        path_simpan = filedialog.asksaveasfilename(initialfile=nama_file_default, defaultextension=".xlsx",
                                                    filetypes=[("Excel Files", "*.xlsx")], title="Simpan Laporan Excel")
        if not path_simpan:
            return
        try:
            df.to_excel(path_simpan, index=False)
            messagebox.showinfo("Sukses", f"Data berhasil diekspor ({len(df)} baris) ke:\n{path_simpan}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Gagal menyimpan:\n{str(e)}")

    def setup_sidebar(self):
        sidebar = tk.Frame(self.root, width=200, bg="#2c3e50", pady=20, padx=15)
        sidebar.grid(row=0, column=0, sticky="ns")

        tk.Label(sidebar, text="Input Data", bg="#2c3e50", fg="white", font=("Arial", 11, "bold")).pack(pady=(0, 10))
        tk.Button(sidebar, text="📝 Tambah Manual", command=self.buka_form_manual, width=18).pack(pady=5)

        ttk.Separator(sidebar, orient='horizontal').pack(fill='x', pady=10)

        tk.Label(sidebar, text="Auto Input (AI)", bg="#2c3e50", fg="white", font=("Arial", 10)).pack(pady=(0, 5))
        tk.Button(sidebar, text="📁 Pilih Screenshot", command=self.pilih_file_screenshot, width=18).pack(pady=5)
        tk.Button(sidebar, text="📋 Paste (Ctrl+V)", command=self.paste_dari_clipboard, width=18).pack(pady=5)

        ttk.Separator(sidebar, orient='horizontal').pack(fill='x', pady=10)

        tk.Label(sidebar, text="Mode LLM:", bg="#2c3e50", fg="white", font=("Arial", 10)).pack(pady=(0, 3))
        ttk.Combobox(sidebar, textvariable=self.llm_mode,
                     values=["Online (DeepSeek)", "Offline (SmolLM2)"],
                     state="readonly", width=16).pack(pady=(0, 5))

        ttk.Separator(sidebar, orient='horizontal').pack(fill='x', pady=15)

        tk.Label(sidebar, text="Manajemen Data", bg="#2c3e50", fg="white", font=("Arial", 11, "bold")).pack(pady=(0, 10))
        tk.Button(sidebar, text="✏️ Edit", command=self.edit_data_terpilih, width=18).pack(pady=5)
        tk.Button(sidebar, text="🗑️ Delete", command=self.hapus_baris_terpilih, width=18).pack(pady=5)

        ttk.Separator(sidebar, orient='horizontal').pack(fill='x', pady=15)
        tk.Button(sidebar, text="📥 Export Excel", command=self.export_excel, width=18).pack(pady=5)
        tk.Button(sidebar, text="Keluar", command=self.root.quit, width=18, fg="red").pack(side="bottom", pady=20)

    def setup_main_panel(self):
        main_panel = tk.Frame(self.root, padx=15, pady=15)
        main_panel.grid(row=0, column=1, sticky="nsew")

        filter_frame = tk.LabelFrame(main_panel, text="Filter Pencarian", font=("Arial", 10, "bold"), padx=10, pady=10)
        filter_frame.pack(fill="x", pady=(0, 15))

        tk.Label(filter_frame, text="Lokasi:").grid(row=0, column=0, sticky="w", pady=2)
        self.filter_lokasi = ttk.Entry(filter_frame, width=20)
        self.filter_lokasi.grid(row=1, column=0, padx=(0, 10))

        tk.Label(filter_frame, text="Link:").grid(row=0, column=1, sticky="w", pady=2)
        self.filter_link = ttk.Entry(filter_frame, width=15)
        self.filter_link.grid(row=1, column=1, padx=(0, 10))

        tk.Label(filter_frame, text="Progress:").grid(row=0, column=2, sticky="w", pady=2)
        self.filter_progress = ttk.Combobox(filter_frame, values=["SEMUA"] + self.list_progress, state="readonly", width=15)
        self.filter_progress.grid(row=1, column=2, padx=(0, 10))
        self.filter_progress.current(0)

        tk.Label(filter_frame, text="Supeng:").grid(row=0, column=3, sticky="w", pady=2)
        self.filter_supeng = ttk.Combobox(filter_frame, values=["SEMUA"] + self.list_supeng, state="readonly", width=15)
        self.filter_supeng.grid(row=1, column=3, padx=(0, 10))
        self.filter_supeng.current(0)

        btn_frame = tk.Frame(filter_frame)
        btn_frame.grid(row=1, column=4, padx=10)
        tk.Button(btn_frame, text="🔍 Cari", command=self.terapkan_filter, width=8).pack(side="left", padx=2)
        tk.Button(btn_frame, text="✖ Reset", command=self.reset_filter, width=8).pack(side="left", padx=2)

        tk.Label(main_panel, text="Log Laporan Hari Ini", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))

        columns = ("lokasi", "issue", "link", "progress", "supeng", "root_cause", "tanggal", "hidden_id")
        self.tree = ttk.Treeview(main_panel, columns=columns, show="headings", height=8)

        for col, w in [("lokasi", 120), ("issue", 220), ("link", 100), ("progress", 100),
                       ("supeng", 80), ("root_cause", 150), ("tanggal", 130)]:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=w, anchor="center" if col in ("progress", "supeng", "tanggal") else "w")
        self.tree.column("hidden_id", width=0, stretch=tk.NO)

        self.tree.pack(fill="both", expand=True, pady=(0, 15))
        self.tree.bind('<<TreeviewSelect>>', self.on_row_select)

        tk.Label(main_panel, text="Detail Lengkap:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.detail_text = tk.Text(main_panel, height=8, wrap="word", bg="#f4f6f7")
        self.detail_text.pack(fill="both", expand=True, pady=5)

    def terapkan_filter(self):
        f_lokasi = self.filter_lokasi.get().lower()
        f_link = self.filter_link.get().lower()
        f_progress = self.filter_progress.get()
        f_supeng = self.filter_supeng.get()
        data_tersaring = [row for row in self.all_data
                          if f_lokasi in row[0].lower() and f_link in row[2].lower()
                          and (f_progress == "SEMUA" or f_progress == row[3])
                          and (f_supeng == "SEMUA" or f_supeng == row[4])]
        self.muat_data_ke_tabel(data_tersaring)

    def reset_filter(self):
        self.filter_lokasi.delete(0, tk.END)
        self.filter_link.delete(0, tk.END)
        self.filter_progress.current(0)
        self.filter_supeng.current(0)
        self.muat_data_ke_tabel(self.all_data)

    def muat_data_ke_tabel(self, data):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in data:
            self.tree.insert("", "end", values=row)

    def on_row_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            v = self.tree.item(selected_item[0])['values']
            self.detail_text.config(state="normal")
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.insert(tk.END,
                f"Tanggal  : {v[6]}\nLokasi   : {v[0]}\nProgress : {v[3]}\nSupeng   : {v[4]}\n"
                f"Link     : {v[2] if v[2] else '-'}\n\nIssue      :\n{v[1]}\n\n"
                f"Root Cause :\n{v[5] if v[5] else 'Belum dianalisis.'}")
            self.detail_text.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    ttk.Style().theme_use('clam')
    app = DailyIssueLoggerUI(root)
    root.mainloop()
