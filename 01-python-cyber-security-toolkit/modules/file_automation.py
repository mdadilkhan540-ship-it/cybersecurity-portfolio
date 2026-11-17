"""
modules/file_automation.py
Tool #2: File & Folder Automation.
- Create / read / write text files
- Organize a folder by moving files into subfolders based on extension
"""

import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

from utils.logger import get_logger

logger = get_logger(__name__)


class FileAutomationFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#1e1e1e")
        self.target_dir = tk.StringVar()

        tk.Label(
            self, text="File & Folder Automation", fg="#00ff9c", bg="#1e1e1e",
            font=("Consolas", 16, "bold")
        ).pack(pady=10)

        # --- Quick file write/read ---
        write_frame = tk.LabelFrame(self, text="Write / Read File", fg="white", bg="#1e1e1e")
        write_frame.pack(fill="x", padx=15, pady=5)

        self.path_entry = tk.Entry(write_frame, width=50)
        self.path_entry.pack(side="left", padx=5, pady=5)
        tk.Button(write_frame, text="Browse", command=self._browse_file).pack(side="left", padx=5)

        self.content_box = scrolledtext.ScrolledText(self, height=8, width=70)
        self.content_box.pack(padx=15, pady=5)

        btn_frame = tk.Frame(self, bg="#1e1e1e")
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Write File", width=15, command=self._write_file).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Read File", width=15, command=self._read_file).grid(row=0, column=1, padx=5)

        # --- Folder organizer ---
        org_frame = tk.LabelFrame(self, text="Organize Folder by File Type", fg="white", bg="#1e1e1e")
        org_frame.pack(fill="x", padx=15, pady=15)

        tk.Entry(org_frame, textvariable=self.target_dir, width=50).pack(side="left", padx=5, pady=5)
        tk.Button(org_frame, text="Browse Folder", command=self._browse_folder).pack(side="left", padx=5)
        tk.Button(org_frame, text="Organize", command=self._organize_folder).pack(side="left", padx=5)

        self.status = tk.Label(self, text="", fg="#00ff9c", bg="#1e1e1e")
        self.status.pack(pady=5)

    # ---------- file write/read ----------
    def _browse_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)

    def _write_file(self):
        path = self.path_entry.get().strip()
        if not path:
            messagebox.showwarning("Missing path", "Enter or browse to a file path first.")
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.content_box.get("1.0", tk.END))
            logger.info(f"Wrote file: {path}")
            self.status.config(text=f"Saved: {path}")
        except OSError as e:
            logger.error(f"Write failed for {path}: {e}")
            messagebox.showerror("Write failed", str(e))

    def _read_file(self):
        path = self.path_entry.get().strip()
        if not path or not os.path.isfile(path):
            messagebox.showwarning("Not found", "That file path doesn't exist.")
            return
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                data = f.read()
            self.content_box.delete("1.0", tk.END)
            self.content_box.insert(tk.END, data)
            logger.info(f"Read file: {path}")
            self.status.config(text=f"Loaded: {path}")
        except OSError as e:
            logger.error(f"Read failed for {path}: {e}")
            messagebox.showerror("Read failed", str(e))

    # ---------- folder organizer ----------
    def _browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.target_dir.set(folder)

    def _organize_folder(self):
        folder = self.target_dir.get().strip()
        if not folder or not os.path.isdir(folder):
            messagebox.showwarning("Invalid folder", "Pick a valid folder to organize.")
            return

        moved = 0
        for name in os.listdir(folder):
            full_path = os.path.join(folder, name)
            if os.path.isfile(full_path):
                ext = os.path.splitext(name)[1].lstrip(".").lower() or "no_extension"
                dest_dir = os.path.join(folder, ext.upper() + "_files")
                os.makedirs(dest_dir, exist_ok=True)
                try:
                    shutil.move(full_path, os.path.join(dest_dir, name))
                    moved += 1
                except shutil.Error as e:
                    logger.warning(f"Could not move {name}: {e}")

        logger.info(f"Organized {moved} files in {folder}")
        self.status.config(text=f"Organized {moved} file(s) in {folder}")
        messagebox.showinfo("Done", f"Organized {moved} file(s).")
