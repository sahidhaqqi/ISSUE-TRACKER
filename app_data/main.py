import tkinter as tk
from tkinter import ttk
from controller import DailyIssueLoggerUI  # tanpa app_data.

if __name__ == "__main__":
    root = tk.Tk()
    ttk.Style().theme_use('clam')
    app = DailyIssueLoggerUI(root)
    root.mainloop()
