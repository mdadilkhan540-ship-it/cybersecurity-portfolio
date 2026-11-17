"""
modules/screenshot_tool.py
Tool #8 (part 1): Screenshot capture, with a view of recent activity log lines.
"""

import os
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, scrolledtext

from utils.logger import get_logger, LOG_DIR

logger = get_logger(__name__)

SHOT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "screenshots")


class ScreenshotFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#1e1e1e")
        os.makedirs(SHOT_DIR, exist_ok=True)

        tk.Label(
            self, text="Screenshot Capture & Activity Log", fg="#00ff9c", bg="#1e1e1e",
            font=("Consolas", 16, "bold")
        ).pack(pady=10)

        tk.Button(self, text="Take Screenshot", width=20, command=self._take_screenshot).pack(pady=10)
        self.status = tk.Label(self, text="", fg="#00ff9c", bg="#1e1e1e")
        self.status.pack()

        tk.Label(self, text=f"Saved to: {SHOT_DIR}", fg="#888888", bg="#1e1e1e").pack(pady=(0, 10))

        tk.Label(self, text="Recent log activity", fg="white", bg="#1e1e1e").pack(anchor="w", padx=15)
        self.log_view = scrolledtext.ScrolledText(self, height=16, width=90)
        self.log_view.pack(padx=15, pady=5)
        tk.Button(self, text="Refresh Log", command=self._load_log).pack(pady=5)

        self._load_log()

    def _take_screenshot(self):
        try:
            import pyautogui
        except ImportError:
            messagebox.showerror(
                "Missing dependency",
                "pyautogui isn't installed, or there's no display available in this environment.\n"
                "Install with: pip install pyautogui"
            )
            return

        filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        path = os.path.join(SHOT_DIR, filename)
        try:
            img = pyautogui.screenshot()
            img.save(path)
            self.status.config(text=f"Saved: {path}")
            logger.info(f"Screenshot saved: {path}")
        except Exception as e:  # pyautogui can raise several platform-specific errors
            logger.error(f"Screenshot failed: {e}")
            messagebox.showerror("Screenshot failed", str(e))

    def _load_log(self):
        today_log = os.path.join(LOG_DIR, f"toolkit_{datetime.now().strftime('%Y%m%d')}.log")
        self.log_view.delete("1.0", tk.END)
        if not os.path.isfile(today_log):
            self.log_view.insert(tk.END, "No log entries yet today.")
            return
        with open(today_log, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        self.log_view.insert(tk.END, "".join(lines[-200:]))  # last 200 lines
        self.log_view.see(tk.END)
