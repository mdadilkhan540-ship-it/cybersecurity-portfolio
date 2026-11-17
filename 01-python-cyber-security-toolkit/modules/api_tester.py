"""
modules/api_tester.py
Tool #4: API Tester.
- Send GET/POST requests with optional headers and JSON body
- Pretty-print the JSON response, show status code and timing
"""

import json
import threading
import time
import tkinter as tk
from tkinter import messagebox, scrolledtext

import requests

from utils.logger import get_logger

logger = get_logger(__name__)


class ApiTesterFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#1e1e1e")

        tk.Label(
            self, text="API Tester", fg="#00ff9c", bg="#1e1e1e",
            font=("Consolas", 16, "bold")
        ).pack(pady=10)

        # --- URL + method row ---
        top = tk.Frame(self, bg="#1e1e1e")
        top.pack(fill="x", padx=15, pady=5)

        self.method_var = tk.StringVar(value="GET")
        tk.OptionMenu(top, self.method_var, "GET", "POST", "PUT", "DELETE").pack(side="left", padx=5)

        self.url_entry = tk.Entry(top, width=60)
        self.url_entry.insert(0, "https://httpbin.org/get")
        self.url_entry.pack(side="left", padx=5, fill="x", expand=True)

        self.send_btn = tk.Button(top, text="Send", width=10, command=self._send_async)
        self.send_btn.pack(side="left", padx=5)

        # --- Headers ---
        tk.Label(self, text="Headers (JSON, optional)", fg="white", bg="#1e1e1e").pack(anchor="w", padx=15)
        self.headers_box = scrolledtext.ScrolledText(self, height=3, width=90)
        self.headers_box.insert(tk.END, '{"Content-Type": "application/json"}')
        self.headers_box.pack(padx=15, pady=2)

        # --- Body ---
        tk.Label(self, text="Body (JSON, for POST/PUT)", fg="white", bg="#1e1e1e").pack(anchor="w", padx=15)
        self.body_box = scrolledtext.ScrolledText(self, height=5, width=90)
        self.body_box.pack(padx=15, pady=2)

        # --- Status line ---
        self.status_label = tk.Label(self, text="", fg="orange", bg="#1e1e1e")
        self.status_label.pack(anchor="w", padx=15, pady=5)

        # --- Response ---
        tk.Label(self, text="Response", fg="white", bg="#1e1e1e").pack(anchor="w", padx=15)
        self.response_box = scrolledtext.ScrolledText(self, height=14, width=90)
        self.response_box.pack(padx=15, pady=2)

    def _send_async(self):
        # Run the request off the GUI thread so the window doesn't freeze.
        self.send_btn.config(state="disabled")
        self.status_label.config(text="Sending...", fg="orange")
        threading.Thread(target=self._send, daemon=True).start()

    def _send(self):
        url = self.url_entry.get().strip()
        method = self.method_var.get()

        headers = {}
        raw_headers = self.headers_box.get("1.0", tk.END).strip()
        if raw_headers:
            try:
                headers = json.loads(raw_headers)
            except json.JSONDecodeError as e:
                self._finish(error=f"Invalid headers JSON: {e}")
                return

        body = None
        raw_body = self.body_box.get("1.0", tk.END).strip()
        if raw_body:
            try:
                body = json.loads(raw_body)
            except json.JSONDecodeError as e:
                self._finish(error=f"Invalid body JSON: {e}")
                return

        if not url:
            self._finish(error="URL is required")
            return

        try:
            start = time.time()
            resp = requests.request(method, url, headers=headers or None, json=body, timeout=10)
            elapsed = (time.time() - start) * 1000

            try:
                pretty = json.dumps(resp.json(), indent=2)
            except ValueError:
                pretty = resp.text

            logger.info(f"{method} {url} -> {resp.status_code} ({elapsed:.0f} ms)")
            self._finish(status=resp.status_code, elapsed=elapsed, body=pretty)

        except requests.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            self._finish(error=str(e))

    def _finish(self, status=None, elapsed=None, body=None, error=None):
        def update():
            self.send_btn.config(state="normal")
            self.response_box.delete("1.0", tk.END)
            if error:
                self.status_label.config(text=f"Error: {error}", fg="#ff5555")
                self.response_box.insert(tk.END, error)
            else:
                self.status_label.config(
                    text=f"Status: {status}   |   {elapsed:.0f} ms", fg="#00ff9c"
                )
                self.response_box.insert(tk.END, body)
        self.after(0, update)
