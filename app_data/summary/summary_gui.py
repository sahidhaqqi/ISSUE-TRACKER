import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import pandas as pd
from .summary_logic import SummaryLogic

class SummaryWindow:
    def __init__(self, parent, data, list_progress, list_supeng):
        self.parent = parent
        self.data = data
        self.list_progress = list_progress
        self.list_supeng = list_supeng
        self.logic = SummaryLogic()
        self.filtered_data = data.copy()
        
        self.window = tk.Toplevel(parent)
        self.window.title("Generate Laporan Harian")
        self.window.geometry("900x700")
        self.window.grab_set()
        
        self._build_ui()
        self._update_preview()
        
    def _build_ui(self):
        # ==================== PREVIEW FRAME ====================
        preview_frame = tk.LabelFrame(self.window, text="Preview Data", padx=10, pady=10)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Treeview dengan scrollbar
        tree_frame = tk.Frame(preview_frame)
        tree_frame.pack(fill="both", expand=True)
        
        columns = ("Lokasi", "Issue", "Progress", "Supeng", "Tanggal")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8)
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Set column widths
        col_widths = [200, 300, 100, 100, 120]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
        
        # Info jumlah data
        self.info_label = tk.Label(
            preview_frame,
            text="Total data: 0 | Menampilkan preview",
            font=("Arial", 9),
            fg="gray"
        )
        self.info_label.pack(anchor="w", pady=5)
        
        # ==================== FILTER FRAME ====================
        filter_frame = tk.LabelFrame(self.window, text="Filter Data", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        # Row 0: Filter Progress (MULTI-SELECT)
        tk.Label(filter_frame, text="Progress:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w", padx=5)
        
        self.progress_vars = {}
        progress_frame = tk.Frame(filter_frame)
        progress_frame.grid(row=0, column=1, columnspan=3, sticky="w", padx=5, pady=2)
        
        # Tambah checkbox untuk setiap progress
        for i, prog in enumerate(["SEMUA"] + self.list_progress):
            var = tk.BooleanVar(value=(prog == "SEMUA"))
            cb = tk.Checkbutton(
                progress_frame, 
                text=prog, 
                variable=var,
                command=self._on_filter_change
            )
            cb.grid(row=0, column=i, padx=5)
            self.progress_vars[prog] = var
        
        # Row 1: Filter Supeng (MULTI-SELECT)
        tk.Label(filter_frame, text="Supeng:", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        self.supeng_vars = {}
        supeng_frame = tk.Frame(filter_frame)
        supeng_frame.grid(row=1, column=1, columnspan=3, sticky="w", padx=5)
        
        # Tambah checkbox untuk setiap supeng
        supeng_list = ["SEMUA"] + self.list_supeng
        for i in range(0, len(supeng_list), 4):  # 4 kolom
            row_frame = tk.Frame(supeng_frame)
            row_frame.pack(anchor="w")
            for j in range(4):
                if i+j < len(supeng_list):
                    sup = supeng_list[i+j]
                    var = tk.BooleanVar(value=(sup == "SEMUA"))
                    cb = tk.Checkbutton(
                        row_frame, 
                        text=sup, 
                        variable=var,
                        command=self._on_filter_change
                    )
                    cb.pack(side="left", padx=5)
                    self.supeng_vars[sup] = var
        
        # Row 2: Filter Lokasi (SEARCH)
        tk.Label(filter_frame, text="Lokasi:", font=("Arial", 9, "bold")).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        
        self.lokasi_entry = ttk.Entry(filter_frame, width=30)
        self.lokasi_entry.grid(row=2, column=1, sticky="w", padx=5)
        self.lokasi_entry.bind("<KeyRelease>", self._on_filter_change)
        
        tk.Label(filter_frame, text="(ketik untuk filter)", font=("Arial", 8), fg="gray").grid(row=2, column=2, sticky="w")
        
        # Row 3: Filter Tanggal
        tk.Label(filter_frame, text="Rentang Tanggal:", font=("Arial", 9, "bold")).grid(row=3, column=0, sticky="w", padx=5, pady=5)
        
        tk.Label(filter_frame, text="Dari:").grid(row=3, column=1, sticky="w", padx=5)
        self.start_date = ttk.Entry(filter_frame, width=15)
        self.start_date.insert(0, (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"))
        self.start_date.grid(row=3, column=2, sticky="w", padx=5)
        self.start_date.bind("<KeyRelease>", self._on_filter_change)
        
        tk.Label(filter_frame, text="Sampai:").grid(row=3, column=3, sticky="w", padx=5)
        self.end_date = ttk.Entry(filter_frame, width=15)
        self.end_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.end_date.grid(row=3, column=4, sticky="w", padx=5)
        self.end_date.bind("<KeyRelease>", self._on_filter_change)
        
        # Row 4: Tombol Reset
        btn_frame = tk.Frame(filter_frame)
        btn_frame.grid(row=4, column=0, columnspan=5, pady=10)
        
        tk.Button(
            btn_frame,
            text="🔄 Reset Semua Filter",
            command=self._reset_filters,
            bg="#607D8B",
            fg="white"
        ).pack(side="left", padx=5)
        
        tk.Button(
            btn_frame,
            text="📊 Hitung Data",
            command=self._update_preview,
            bg="#4CAF50",
            fg="white"
        ).pack(side="left", padx=5)
        
        # Info ringkasan filter
        self.filter_summary = tk.Label(
            filter_frame,
            text="",
            font=("Arial", 9),
            fg="blue"
        )
        self.filter_summary.grid(row=5, column=0, columnspan=5, pady=5)
        
        # ==================== RESULT FRAME ====================
        result_frame = tk.LabelFrame(self.window, text="Hasil Generate", padx=10, pady=10)
        result_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Text area + scrollbar
        text_frame = tk.Frame(result_frame)
        text_frame.pack(fill="both", expand=True)
        
        self.result_text = tk.Text(text_frame, wrap="word", height=12, font=("Courier", 10))
        self.result_text.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(text_frame, command=self.result_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.result_text.config(yscrollcommand=scrollbar.set)
        
        # ==================== BUTTON FRAME ====================
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Button(
            btn_frame,
            text="🚀 Generate Laporan",
            command=self._generate,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20
        ).pack(side="left", padx=5)
        
        tk.Button(
            btn_frame,
            text="💾 Simpan ke File",
            command=self._save,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20
        ).pack(side="left", padx=5)
        
        tk.Button(
            btn_frame,
            text="📋 Copy",
            command=self._copy,
            bg="#FF9800",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20
        ).pack(side="left", padx=5)
        
        tk.Button(
            btn_frame,
            text="❌ Tutup",
            command=self.window.destroy,
            bg="#f44336",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20
        ).pack(side="right", padx=5)
    
    def _on_filter_change(self, event=None):
        """Auto update preview saat filter berubah"""
        self._update_preview()
    
    def _update_preview(self):
        """Update preview berdasarkan filter"""
        filtered = []
        
        # Kumpulkan progress yang dipilih
        selected_progress = []
        for prog, var in self.progress_vars.items():
            if var.get():
                if prog == "SEMUA":
                    selected_progress = self.list_progress.copy()
                    break
                else:
                    selected_progress.append(prog)
        
        # Kumpulkan supeng yang dipilih
        selected_supeng = []
        for sup, var in self.supeng_vars.items():
            if var.get():
                if sup == "SEMUA":
                    selected_supeng = self.list_supeng.copy()
                    break
                else:
                    selected_supeng.append(sup)
        
        # Filter lokasi (case insensitive)
        lokasi_filter = self.lokasi_entry.get().lower().strip()
        
        # Filter tanggal
        start = self.start_date.get()
        end = self.end_date.get()
        
        # Apply semua filter
        for row in self.data:
            # Filter progress
            if selected_progress and row[3] not in selected_progress:
                continue
            
            # Filter supeng
            if selected_supeng and row[4] not in selected_supeng:
                continue
            
            # Filter lokasi
            if lokasi_filter and lokasi_filter not in row[0].lower():
                continue
            
            # Filter tanggal
            tgl = row[6][:10]
            if tgl < start or tgl > end:
                continue
            
            filtered.append(row)
        
        self.filtered_data = filtered
        
        # Update treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for row in filtered[:50]:  # max preview 50 data
            self.tree.insert("", "end", values=(
                row[0],
                row[1][:80],
                row[3],
                row[4],
                row[6][:10]
            ))
        
        # Update info
        total = len(self.data)
        filtered_count = len(filtered)
        self.info_label.config(
            text=f"Total data: {total} | Setelah filter: {filtered_count} | Menampilkan {min(50, filtered_count)} data"
        )
        
        # Update summary filter
        filter_text = f"Progress: {len(selected_progress)}/{len(self.list_progress)} | Supeng: {len(selected_supeng)}/{len(self.list_supeng)}"
        if lokasi_filter:
            filter_text += f" | Lokasi: '{lokasi_filter}'"
        self.filter_summary.config(text=filter_text)
    
    def _reset_filters(self):
        """Reset semua filter ke default"""
        # Reset progress (SEMUA)
        for prog, var in self.progress_vars.items():
            var.set(prog == "SEMUA")
        
        # Reset supeng (SEMUA)
        for sup, var in self.supeng_vars.items():
            var.set(sup == "SEMUA")
        
        # Reset lokasi
        self.lokasi_entry.delete(0, tk.END)
        
        # Reset tanggal (7 hari terakhir)
        self.start_date.delete(0, tk.END)
        self.start_date.insert(0, (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"))
        self.end_date.delete(0, tk.END)
        self.end_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        self._update_preview()
    
    def _generate(self):
        """Generate summary dari data yang difilter"""
        if not self.filtered_data:
            messagebox.showwarning("Peringatan", "Tidak ada data dengan filter tersebut!")
            return
        
        # Tampilkan loading
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "⏳ Menggenerate laporan...")
        self.window.update()
        
        # Generate dengan AI
        result = self.logic.generate(self.filtered_data)
        
        # Tampilkan hasil
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result)
    
    def _save(self):
        """Simpan hasil ke file"""
        result = self.result_text.get(1.0, tk.END).strip()
        if not result or result == "⏳ Menggenerate laporan...":
            messagebox.showwarning("Peringatan", "Tidak ada hasil untuk disimpan!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"laporan_harian_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        )
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(result)
            messagebox.showinfo("Sukses", f"Laporan disimpan di:\n{filename}")
    
    def _copy(self):
        """Copy hasil ke clipboard"""
        result = self.result_text.get(1.0, tk.END).strip()
        if not result or result == "⏳ Menggenerate laporan...":
            messagebox.showwarning("Peringatan", "Tidak ada hasil untuk dicopy!")
            return
        
        self.window.clipboard_clear()
        self.window.clipboard_append(result)
        messagebox.showinfo("Sukses", "Laporan dicopy ke clipboard!")
