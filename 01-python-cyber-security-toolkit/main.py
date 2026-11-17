"""
main.py
Central Tkinter GUI Dashboard for the Python Cyber Toolkit.

Run with:  python main.py
(from inside the cyber_toolkit/ folder, or `python -m cyber_toolkit.main`
 if you move this package somewhere else — adjust the imports below if so)
"""

import tkinter as tk

from utils.logger import get_logger
from modules.file_automation import FileAutomationFrame
from modules.hash_crypto import HashCryptoFrame
from modules.api_tester import ApiTesterFrame
from modules.network_tools import NetworkToolsFrame
from modules.bruteforce import BruteForceFrame
from modules.sql_tester import SqlTesterFrame
from modules.screenshot_tool import ScreenshotFrame

logger = get_logger("main")

BG = "#121212"
ACCENT = "#00ff9c"


class CyberToolkitApp(tk.Tk):
    TOOLS = {
        "File & Folder Automation": FileAutomationFrame,
        "Hashing & Encryption": HashCryptoFrame,
        "API Tester": ApiTesterFrame,
        "Networking Tools": NetworkToolsFrame,
        "Brute-Force Simulator": BruteForceFrame,
        "SQL Injection Tester": SqlTesterFrame,
        "Screenshot & Logs": ScreenshotFrame,
    }

    def __init__(self):
        super().__init__()
        self.title("Python Cyber Toolkit")
        self.geometry("900x650")
        self.configure(bg=BG)

        self.container = tk.Frame(self, bg=BG)
        self.container.pack(fill="both", expand=True)

        self._build_menu()
        self._show_home()

        logger.info("Application started")

    def _build_menu(self):
        sidebar = tk.Frame(self.container, bg="#1a1a1a", width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar, text="TOOLKIT", fg=ACCENT, bg="#1a1a1a",
            font=("Consolas", 18, "bold")
        ).pack(pady=20)

        tk.Button(
            sidebar, text="Home", command=self._show_home,
            bg="#262626", fg="white", relief="flat", anchor="w", padx=15
        ).pack(fill="x", pady=2, padx=10)

        for name in self.TOOLS:
            tk.Button(
                sidebar, text=name, command=lambda n=name: self._show_tool(n),
                bg="#262626", fg="white", relief="flat", anchor="w", padx=15,
                wraplength=190, justify="left"
            ).pack(fill="x", pady=2, padx=10)

        self.content = tk.Frame(self.container, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)

    def _clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def _show_home(self):
        self._clear_content()
        tk.Label(
            self.content, text="Python Cyber Toolkit",
            fg=ACCENT, bg=BG, font=("Consolas", 24, "bold")
        ).pack(pady=40)
        tk.Label(
            self.content,
            text="Select a tool from the left menu.\n\n"
                 "Reminder: networking, brute-force, and SQLi tools are for\n"
                 "systems you own or have explicit permission to test.\n"
                 "A local practice target for the SQLi tester is included in\n"
                 "test_server/vulnerable_app.py (run it, then point the tester\n"
                 "at http://127.0.0.1:5050/user?id=1).",
            fg="#aaaaaa", bg=BG, font=("Consolas", 11), justify="center"
        ).pack(pady=10)
        logger.info("Navigated to Home")

    def _show_tool(self, name):
        self._clear_content()
        frame_cls = self.TOOLS[name]
        frame = frame_cls(self.content)
        frame.pack(fill="both", expand=True)
        logger.info(f"Opened tool: {name}")


if __name__ == "__main__":
    app = CyberToolkitApp()
    app.mainloop()
