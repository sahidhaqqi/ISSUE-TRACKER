import tkinter as tk
from tkinter import ttk

class MainPanel:
    def __init__(self, master, controller):
        self.master = master
        self.controller = controller
        self.frame = tk.Frame(master, padx=15, pady=15)
        self.frame.grid(row=0, column=1, sticky="nsew")
        master.columnconfigure(1, weight=1)
        master.rowconfigure(0, weight=1)

        self.filter_lokasi = None
        self.filter_link = None
        self.filter_progress = None
        self.filter_supeng = None
        self.tree = None
        self.detail_text = None
        self.status_label = None

        self._build_filter()
        self._build_tree()
        self._build_detail()

    # ==================== FILTER ====================
    def _build_filter(self):
        filter_frame = tk.LabelFrame(
            self.frame,
            text="Filter Pencarian",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10,
        )
        filter_frame.pack(fill="x", pady=(0, 15))

        tk.Label(filter_frame, text="Lokasi:").grid(
            row=0, column=0, sticky="w", pady=2
        )
        self.filter_lokasi = ttk.Entry(filter_frame, width=20)
        self.filter_lokasi.grid(row=1, column=0, padx=(0, 10))

        tk.Label(filter_frame, text="Link:").grid(
            row=0, column=1, sticky="w", pady=2
        )
        self.filter_link = ttk.Entry(filter_frame, width=15)
        self.filter_link.grid(row=1, column=1, padx=(0, 10))

        tk.Label(filter_frame, text="Progress:").grid(
            row=0, column=2, sticky="w", pady=2
        )
        self.filter_progress = ttk.Combobox(
            filter_frame,
            values=["SEMUA"] + self.controller.list_progress,
            state="readonly",
            width=15,
        )
        self.filter_progress.grid(row=1, column=2, padx=(0, 10))
        self.filter_progress.current(0)

        tk.Label(filter_frame, text="Supeng:").grid(
            row=0, column=3, sticky="w", pady=2
        )
        self.filter_supeng = ttk.Combobox(
            filter_frame,
            values=["SEMUA"] + self.controller.list_supeng,
            state="readonly",
            width=15,
        )
        self.filter_supeng.grid(row=1, column=3, padx=(0, 10))
        self.filter_supeng.current(0)

        btn_frame = tk.Frame(filter_frame)
        btn_frame.grid(row=1, column=4, padx=10)

        tk.Button(
            btn_frame, text="🔍 Cari", command=self._terapkan_filter, width=8
        ).pack(side="left", padx=2)
        tk.Button(
            btn_frame, text="✖ Reset", command=self._reset_filter, width=8
        ).pack(side="left", padx=2)

    def _terapkan_filter(self):
        f_lokasi = self.filter_lokasi.get().lower()
        f_link = self.filter_link.get().lower()
        f_progress = self.filter_progress.get()
        f_supeng = self.filter_supeng.get()

        data_tersaring = [
            row
            for row in self.controller.all_data
            if f_lokasi in row[0].lower()
            and f_link in row[2].lower()
            and (f_progress == "SEMUA" or f_progress == row[3])
            and (f_supeng == "SEMUA" or f_supeng == row[4])
        ]
        self.controller.muat_data_ke_tabel(data_tersaring)

    def _reset_filter(self):
        self.filter_lokasi.delete(0, tk.END)
        self.filter_link.delete(0, tk.END)
        self.filter_progress.current(0)
        self.filter_supeng.current(0)
        self.controller.muat_data_ke_tabel(self.controller.all_data)

    # ==================== TREEVIEW ====================
    def _build_tree(self):
        tk.Label(
            self.frame, text="Log Laporan Hari Ini", font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=(10, 5))

        columns = (
            "lokasi",
            "issue",
            "link",
            "progress",
            "supeng",
            "root_cause",
            "tanggal",
            "hidden_id",
        )

        self.tree = ttk.Treeview(
            self.frame,
            columns=columns,
            show="headings",
            height=8,
            selectmode="extended",
        )

        col_widths = [
            ("lokasi", 120),
            ("issue", 220),
            ("link", 100),
            ("progress", 100),
            ("supeng", 80),
            ("root_cause", 150),
            ("tanggal", 130),
        ]

        for col, w in col_widths:
            self.tree.heading(col, text=col.replace("_", " ").title())
            anchor = "center" if col in ("progress", "supeng", "tanggal") else "w"
            self.tree.column(col, width=w, anchor=anchor)

        self.tree.column("hidden_id", width=0, stretch=tk.NO)
        self.tree.pack(fill="both", expand=True, pady=(0, 15))
        
        # Bindings
        self.tree.bind("<<TreeviewSelect>>", self._on_row_select)
        self.tree.bind("<Double-1>", lambda e: self.controller.edit_data_terpilih())
        self.tree.bind("<Button-3>", self._show_tree_menu)  # KLIK KANAN

    def _on_row_select(self, event):
        selected = self.tree.selection()
        if not selected:
            self.detail_text.config(state="normal")
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.config(state="disabled")
            return

        v = self.tree.item(selected[0])["values"]
        self.detail_text.config(state="normal")
        self.detail_text.delete(1.0, tk.END)
        self.detail_text.insert(
            tk.END,
            f"Tanggal  : {v[6]}\n"
            f"Lokasi   : {v[0]}\n"
            f"Progress : {v[3]}\n"
            f"Supeng   : {v[4]}\n"
            f"Link     : {v[2] if v[2] else '-'}\n\n"
            f"Issue      :\n{v[1]}\n\n"
            f"Root Cause :\n{v[5] if v[5] else 'Belum dianalisis.'}",
        )
        self.detail_text.config(state="disabled")

    # ==================== DETAIL TEXT ====================
    def _build_detail(self):
        tk.Label(
            self.frame,
            text="Detail Lengkap:",
            font=("Arial", 10, "bold")
        ).pack(anchor="w")

        self.detail_text = tk.Text(
            self.frame, height=8, wrap="word", bg="#f4f6f7"
        )
        self.detail_text.pack(fill="both", expand=True, pady=5)
        
        # Binding klik kanan untuk detail text
        self.detail_text.bind("<Button-3>", self._show_detail_menu)

    # ==================== STATUS MESSAGE ====================
    def show_status_message(self, message, duration=3000):
        """Tampilkan pesan status sementara di main panel"""
        if hasattr(self, 'status_label') and self.status_label:
            self.status_label.destroy()

        self.status_label = tk.Label(
            self.frame,
            text=message,
            bg="#f0f0f0",
            fg="#666",
            font=("Arial", 9)
        )
        self.status_label.pack(side="bottom", fill="x", pady=5)

        # Auto hide setelah duration ms
        self.frame.after(
            duration,
            lambda: self.status_label.destroy() if hasattr(self, 'status_label') else None
        )

    # ==================== FITUR COPY (BARU) ====================
    def _copy_tree_selection(self):
        """Copy selected rows dari treeview ke clipboard"""
        selected = self.tree.selection()
        if not selected:
            return
        
        # Header kolom
        headers = ["Lokasi", "Issue", "Link", "Progress", "Supeng", "Root Cause", "Tanggal"]
        
        # Ambil data dari baris yang dipilih
        rows = []
        for item in selected:
            values = self.tree.item(item)['values'][:7]
            rows.append("\t".join(str(v) for v in values))
        
        # Gabungkan header + data
        result = "\t".join(headers) + "\n" + "\n".join(rows)
        
        # Copy ke clipboard
        self.master.clipboard_clear()
        self.master.clipboard_append(result)
        
        # Tampilkan notifikasi kecil
        self.show_status_message(f"✅ {len(selected)} baris dicopy", 1500)

    def _copy_detail_text(self):
        """Copy text dari detail panel ke clipboard"""
        if hasattr(self, 'detail_text'):
            try:
                text = self.detail_text.get("1.0", tk.END).strip()
                if text:
                    self.master.clipboard_clear()
                    self.master.clipboard_append(text)
                    self.show_status_message("✅ Detail dicopy", 1500)
            except:
                pass

    def _copy_selection(self):
        """Copy teks yang dipilih di detail text"""
        try:
            text = self.detail_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            if text:
                self.master.clipboard_clear()
                self.master.clipboard_append(text)
                self.show_status_message("✅ Teks dicopy", 1500)
        except tk.TclError:
            # Tidak ada teks yang dipilih
            pass

    def _show_tree_menu(self, event):
        """Tampilkan menu klik kanan untuk treeview"""
        # Pilih baris yang diklik
        item = self.tree.identify_row(event.y)
        if item:
            # Kalau belum terseleksi, seleksi dulu
            if item not in self.tree.selection():
                self.tree.selection_set(item)
        
        # Buat menu popup
        menu = tk.Menu(self.master, tearoff=0)
        
        selected_count = len(self.tree.selection())
        if selected_count > 0:
            menu.add_command(
                label=f"📋 Copy {selected_count} baris",
                command=self._copy_tree_selection
            )
            menu.add_separator()
        
        menu.add_command(label="✏️ Edit", command=self.controller.edit_data_terpilih)
        menu.add_command(label="🗑️ Delete", command=self.controller.hapus_baris_terpilih)
        
        # Tampilkan menu di posisi klik
        menu.tk_popup(event.x_root, event.y_root)

    def _show_detail_menu(self, event):
        """Tampilkan menu klik kanan untuk detail text"""
        menu = tk.Menu(self.master, tearoff=0)
        menu.add_command(label="📋 Copy All", command=self._copy_detail_text)
        menu.add_command(label="📋 Copy Selection", command=self._copy_selection)
        menu.tk_popup(event.x_root, event.y_root)
