"""
modules/sql_tester.py
Tool #7: SQL Injection Tester.

Sends a set of standard SQLi probe payloads to a target URL (appended to a
query-string parameter), compares each response against a baseline request,
and flags responses that look abnormal (different length, SQL error
strings, different status code). This is a detection aid, not an
exploitation tool — it does not extract data or chain injections.

Intended target: the included test_server/vulnerable_app.py running on
localhost, or any system you own/are authorized to test.
"""

import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

import requests

from utils.logger import get_logger

logger = get_logger(__name__)

PAYLOADS = [
    "'",
    "''",
    "' OR '1'='1",
    "' OR '1'='1' -- ",
    "1 OR 1=1",
    "1; DROP TABLE users",
    "' AND 1=CONVERT(int, (SELECT @@version)) -- ",
    "1' UNION SELECT NULL--",
]

SQL_ERROR_SIGNATURES = [
    "sql syntax", "sqlite3.", "unclosed quotation", "odbc", "ora-",
    "mysql_fetch", "pg_query", "sqlstate", "syntax error",
]


class SqlTesterFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#1e1e1e")

        tk.Label(
            self, text="SQL Injection Tester", fg="#00ff9c", bg="#1e1e1e",
            font=("Consolas", 16, "bold")
        ).pack(pady=10)
        tk.Label(
            self,
            text="Detection aid only — compares responses to common payloads against a baseline.\n"
                 "Test the included practice server (test_server/vulnerable_app.py) or systems you own.",
            fg="orange", bg="#1e1e1e", font=("Consolas", 9, "italic"), justify="center"
        ).pack()

        row = tk.Frame(self, bg="#1e1e1e")
        row.pack(fill="x", padx=15, pady=10)
        tk.Label(row, text="Target URL (with param, e.g. .../user?id=1):", fg="white", bg="#1e1e1e").pack(anchor="w")
        self.url_entry = tk.Entry(row, width=70)
        self.url_entry.insert(0, "http://127.0.0.1:5050/user?id=1")
        self.url_entry.pack(side="left", padx=5, fill="x", expand=True)

        row2 = tk.Frame(self, bg="#1e1e1e")
        row2.pack(fill="x", padx=15, pady=5)
        tk.Label(row2, text="Parameter to inject:", fg="white", bg="#1e1e1e").pack(side="left")
        self.param_entry = tk.Entry(row2, width=20)
        self.param_entry.insert(0, "id")
        self.param_entry.pack(side="left", padx=5)

        self.run_btn = tk.Button(row2, text="Run Tests", width=14, command=self._run_async)
        self.run_btn.pack(side="left", padx=10)

        self.output = scrolledtext.ScrolledText(self, height=18, width=90)
        self.output.pack(padx=15, pady=5)

    def _run_async(self):
        url = self.url_entry.get().strip()
        param = self.param_entry.get().strip()
        if not url or not param:
            messagebox.showwarning("Missing input", "Provide a URL and the parameter name.")
            return
        self.output.delete("1.0", tk.END)
        self.run_btn.config(state="disabled")
        threading.Thread(target=self._run, args=(url, param), daemon=True).start()

    def _build_url(self, base_url, param, value):
        parsed = urlparse(base_url)
        query = parse_qs(parsed.query)
        query[param] = value
        new_query = urlencode(query, doseq=True)
        return urlunparse(parsed._replace(query=new_query))

    def _run(self, base_url, param):
        try:
            baseline_resp = requests.get(base_url, timeout=8)
        except requests.RequestException as e:
            self._log(f"Could not reach baseline URL: {e}")
            self.after(0, lambda: self.run_btn.config(state="normal"))
            return

        baseline_len = len(baseline_resp.text)
        baseline_status = baseline_resp.status_code
        self._log(f"Baseline: status={baseline_status}, length={baseline_len} chars\n")

        flagged = 0
        for payload in PAYLOADS:
            test_url = self._build_url(base_url, param, payload)
            try:
                resp = requests.get(test_url, timeout=8)
            except requests.RequestException as e:
                self._log(f"[ERROR]  payload={payload!r} -> request failed: {e}")
                continue

            body_lower = resp.text.lower()
            has_error_sig = any(sig in body_lower for sig in SQL_ERROR_SIGNATURES)
            len_diff = abs(len(resp.text) - baseline_len)
            status_changed = resp.status_code != baseline_status

            anomaly = has_error_sig or status_changed or len_diff > max(50, baseline_len * 0.2)

            tag = "[FLAGGED]" if anomaly else "[ok]     "
            self._log(
                f"{tag} payload={payload!r:35} status={resp.status_code} "
                f"len_diff={len_diff} error_signature={has_error_sig}"
            )
            if anomaly:
                flagged += 1

        self._log(f"\nDone. {flagged}/{len(PAYLOADS)} payload(s) flagged as anomalous.")
        if flagged:
            self._log("Anomalies suggest the parameter may be unsafely concatenated into SQL. "
                       "Investigate further manually before drawing conclusions.")
        logger.info(f"SQLi test of {base_url} param={param}: {flagged} flagged")
        self.after(0, lambda: self.run_btn.config(state="normal"))

    def _log(self, text):
        self.after(0, lambda: (self.output.insert(tk.END, text + "\n"), self.output.see(tk.END)))
