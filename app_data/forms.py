import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import database

class FormManual:
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.top = tk.Toplevel(parent)
        self.top.title("Input Log Manual")
        self.top.geometry("450x550")
        self.top.update_idletasks()
        self.top.grab_set()

        self._build_ui()

    def _build_ui(self):
        tk.Label(self.top, text="Input Data Manual", font=("Arial", 11, "bold")).pack(
            pady=10
        )
        form_frame = tk.Frame(self.top, padx=20)
        form_frame.pack(fill="both", expand=True)

        fields = [("Lokasi:", ttk.Entry), ("Link:", ttk.Entry)]
        self.entries = {}
        for i, (label, widget) in enumerate(fields):
            tk.Label(form_frame, text=label).grid(row=i, column=0, sticky="nw", pady=5)
            e = widget(form_frame, width=35)
            e.grid(row=i, column=1, pady=5)
            self.entries[label] = e

        tk.Label(form_frame, text="Progress:").grid(
            row=2, column=0, sticky="nw", pady=5
        )
        self.combo_progress = ttk.Combobox(
            form_frame,
            values=["", "NOT CHECK", "PROGRESS", "ON ESCALATION", "DONE"],
            state="readonly",
            width=32,
        )
        self.combo_progress.grid(row=2, column=1, pady=5)
        self.combo_progress.current(0)

        tk.Label(form_frame, text="Supeng:").grid(row=3, column=0, sticky="nw", pady=5)
        self.combo_supeng = ttk.Combobox(
            form_frame, values=self.controller.list_supeng, width=32
        )
        self.combo_supeng.grid(row=3, column=1, pady=5)

        tk.Label(form_frame, text="Issue:").grid(row=4, column=0, sticky="nw", pady=5)
        self.text_issue = tk.Text(form_frame, width=35, height=4)
        self.text_issue.grid(row=4, column=1, pady=5)

        tk.Label(form_frame, text="Root Cause:").grid(
            row=5, column=0, sticky="nw", pady=5
        )
        self.text_rc = tk.Text(form_frame, width=35, height=4)
        self.text_rc.grid(row=5, column=1, pady=5)

        tk.Button(
            self.top,
            text="💾 Simpan Data",
            command=self._simpan,
            bg="#2ecc71",
            fg="white",
            font=("Arial", 10, "bold"),
        ).pack(pady=20)

    def _simpan(self):
        database.insert_data(
            self.entries["Lokasi:"].get(),
            self.text_issue.get("1.0", tk.END).strip(),
            self.entries["Link:"].get(),
            self.combo_progress.get(),
            self.combo_supeng.get(),
            self.text_rc.get("1.0", tk.END).strip(),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        self.top.destroy()
        self.controller.muat_data()
        messagebox.showinfo("Sukses", "Data manual berhasil ditambahkan.")


class FormEdit:
    def __init__(self, parent, controller, id_db, values):
        self.parent = parent
        self.controller = controller
        self.id_db = id_db
        self.values = values
        self.top = tk.Toplevel(parent)
        self.top.title("Edit Log Data")
        self.top.geometry("450x550")
        self.top.update_idletasks()
        self.top.grab_set()

        self._build_ui()

    def _build_ui(self):
        tk.Label(self.top, text="Edit Data Issue", font=("Arial", 11, "bold")).pack(
            pady=10
        )
        form_frame = tk.Frame(self.top, padx=20)
        form_frame.pack(fill="both", expand=True)

        # Lokasi
        tk.Label(form_frame, text="Lokasi:").grid(row=0, column=0, sticky="nw", pady=5)
        self.entry_lokasi = ttk.Entry(form_frame, width=35)
        self.entry_lokasi.grid(row=0, column=1, pady=5)
        self.entry_lokasi.insert(0, self.values[0])

        # Link
        tk.Label(form_frame, text="Link:").grid(row=1, column=0, sticky="nw", pady=5)
        self.entry_link = ttk.Entry(form_frame, width=35)
        self.entry_link.grid(row=1, column=1, pady=5)
        self.entry_link.insert(0, self.values[2] if self.values[2] != "-" else "")

        # Progress
        tk.Label(form_frame, text="Progress:").grid(
            row=2, column=0, sticky="nw", pady=5
        )
        self.combo_progress = ttk.Combobox(
            form_frame,
            values=["", "NOT CHECK", "PROGRESS", "ON ESCALATION", "DONE"],
            state="readonly",
            width=32,
        )
        self.combo_progress.grid(row=2, column=1, pady=5)
        self.combo_progress.set(self.values[3])

        # Supeng
        tk.Label(form_frame, text="Supeng:").grid(row=3, column=0, sticky="nw", pady=5)
        self.combo_supeng = ttk.Combobox(
            form_frame, values=self.controller.list_supeng, width=32
        )
        self.combo_supeng.grid(row=3, column=1, pady=5)
        self.combo_supeng.set(self.values[4])

        # Issue
        tk.Label(form_frame, text="Issue:").grid(row=4, column=0, sticky="nw", pady=5)
        self.text_issue = tk.Text(form_frame, width=35, height=4)
        self.text_issue.grid(row=4, column=1, pady=5)
        self.text_issue.insert("1.0", self.values[1])

        # Root Cause
        tk.Label(form_frame, text="Root Cause:").grid(
            row=5, column=0, sticky="nw", pady=5
        )
        self.text_rc = tk.Text(form_frame, width=35, height=4)
        self.text_rc.grid(row=5, column=1, pady=5)
        rc = self.values[5] if self.values[5] else ""
        if rc and rc != "Belum dianalisis.":
            self.text_rc.insert("1.0", rc)

        tk.Button(
            self.top,
            text="🔄 Update Data",
            command=self._update,
            bg="#f39c12",
            fg="white",
            font=("Arial", 10, "bold"),
        ).pack(pady=20)

    def _update(self):
        database.update_data(
            self.id_db,
            self.entry_lokasi.get(),
            self.text_issue.get("1.0", tk.END).strip(),
            self.entry_link.get(),
            self.combo_progress.get(),
            self.combo_supeng.get(),
            self.text_rc.get("1.0", tk.END).strip(),
        )
        self.top.destroy()
        self.controller.muat_data()
        messagebox.showinfo("Sukses", "Data berhasil diupdate.")
