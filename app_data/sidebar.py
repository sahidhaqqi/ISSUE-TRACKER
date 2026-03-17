import tkinter as tk
from tkinter import ttk

class Sidebar:
    def __init__(self, master, controller):
        self.master = master
        self.controller = controller
        self.frame = tk.Frame(master, width=200, bg="#2c3e50", pady=20, padx=15)
        self.frame.grid(row=0, column=0, sticky="ns")
        self.frame.grid_propagate(False)
        self._build()

    def _build(self):
        # Input Data
        tk.Label(self.frame, text="Input Data", bg="#2c3e50", fg="white",
                 font=("Arial", 11, "bold")).pack(pady=(0, 10))
        tk.Button(self.frame, text="📝 Tambah Manual",
                  command=self.controller.buka_form_manual, width=18).pack(pady=5)

        ttk.Separator(self.frame, orient='horizontal').pack(fill='x', pady=10)

        # Auto Input (AI)
        tk.Label(self.frame, text="Auto Input (AI)", bg="#2c3e50", fg="white",
                 font=("Arial", 10)).pack(pady=(0, 5))
        tk.Button(self.frame, text="📁 Pilih Screenshot",
                  command=self.controller.pilih_file_screenshot, width=18).pack(pady=5)
        tk.Button(self.frame, text="📋 Paste (Ctrl+V)",
                  command=self.controller.paste_dari_clipboard, width=18).pack(pady=5)

        ttk.Separator(self.frame, orient='horizontal').pack(fill='x', pady=10)

        # Mode LLM
        tk.Label(self.frame, text="Mode LLM:", bg="#2c3e50", fg="white",
                 font=("Arial", 10)).pack(pady=(0, 3))
        ttk.Combobox(self.frame, textvariable=self.controller.llm_mode,
                     values=["Online (DeepSeek)", "Offline (SmolLM2)"],
                     state="readonly", width=16).pack(pady=(0, 5))

        ttk.Separator(self.frame, orient='horizontal').pack(fill='x', pady=15)

        # Manajemen Data
        tk.Label(self.frame, text="Manajemen Data", bg="#2c3e50", fg="white",
                 font=("Arial", 11, "bold")).pack(pady=(0, 10))
        tk.Button(self.frame, text="✏️ Edit",
                  command=self.controller.edit_data_terpilih, width=18).pack(pady=5)
        tk.Button(self.frame, text="🗑️ Delete",
                  command=self.controller.hapus_baris_terpilih, width=18).pack(pady=5)
        tk.Button(self.frame, text="🗑️ Hapus Semua",
                  command=self.controller.hapus_semua_data, width=18).pack(pady=5)

        ttk.Separator(self.frame, orient='horizontal').pack(fill='x', pady=15)
        tk.Button(self.frame, text="📥 Export Excel",
                  command=self.controller.export_excel, width=18).pack(pady=5)
        tk.Button(self.frame, text="Keluar",
                  command=self.controller.root.quit, width=18, fg="red").pack(side="bottom", pady=20)
