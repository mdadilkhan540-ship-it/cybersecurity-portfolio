"""
modules/network_tools.py
Tool #5: Networking Tools.
- Port scanner: checks TCP connect() on a port range against a target
- Subdomain finder: DNS-resolves a wordlist of common subdomains

Both tools default to a safe target (127.0.0.1) and only perform passive
TCP-connect / DNS-resolution checks — no exploitation. Only point these
at hosts you own or are explicitly authorized to test.
"""

import socket
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext

from utils.logger import get_logger

logger = get_logger(__name__)

COMMON_SUBDOMAINS = [
    "www", "mail", "ftp", "api", "dev", "test", "staging", "admin",
    "blog", "shop", "vpn", "ns1", "ns2", "cdn", "portal", "app",
    "docs", "status", "support", "beta",
]


class NetworkToolsFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#1e1e1e")
        self._stop_scan = False

        tk.Label(
            self, text="Networking Tools", fg="#00ff9c", bg="#1e1e1e",
            font=("Consolas", 16, "bold")
        ).pack(pady=10)

        tk.Label(
            self,
            text="Only scan hosts you own or have explicit permission to test.",
            fg="orange", bg="#1e1e1e", font=("Consolas", 9, "italic")
        ).pack()

        # ---------- Port Scanner ----------
        scan_frame = tk.LabelFrame(self, text="Port Scanner", fg="white", bg="#1e1e1e")
        scan_frame.pack(fill="x", padx=15, pady=10)

        row1 = tk.Frame(scan_frame, bg="#1e1e1e")
        row1.pack(fill="x", padx=5, pady=5)
        tk.Label(row1, text="Target:", fg="white", bg="#1e1e1e").pack(side="left")
        self.target_entry = tk.Entry(row1, width=25)
        self.target_entry.insert(0, "127.0.0.1")
        self.target_entry.pack(side="left", padx=5)

        tk.Label(row1, text="Port range:", fg="white", bg="#1e1e1e").pack(side="left", padx=(15, 0))
        self.start_port = tk.Entry(row1, width=6)
        self.start_port.insert(0, "1")
        self.start_port.pack(side="left", padx=2)
        tk.Label(row1, text="-", fg="white", bg="#1e1e1e").pack(side="left")
        self.end_port = tk.Entry(row1, width=6)
        self.end_port.insert(0, "1024")
        self.end_port.pack(side="left", padx=2)

        self.scan_btn = tk.Button(row1, text="Scan", width=10, command=self._scan_async)
        self.scan_btn.pack(side="left", padx=10)
        tk.Button(row1, text="Stop", width=8, command=self._stop).pack(side="left")

        self.scan_output = scrolledtext.ScrolledText(scan_frame, height=10, width=85)
        self.scan_output.pack(padx=5, pady=5)

        # ---------- Subdomain Finder ----------
        sub_frame = tk.LabelFrame(self, text="Subdomain Finder", fg="white", bg="#1e1e1e")
        sub_frame.pack(fill="x", padx=15, pady=10)

        row2 = tk.Frame(sub_frame, bg="#1e1e1e")
        row2.pack(fill="x", padx=5, pady=5)
        tk.Label(row2, text="Domain:", fg="white", bg="#1e1e1e").pack(side="left")
        self.domain_entry = tk.Entry(row2, width=30)
        self.domain_entry.insert(0, "example.com")
        self.domain_entry.pack(side="left", padx=5)
        tk.Button(row2, text="Find Subdomains", command=self._find_subdomains_async).pack(side="left", padx=10)

        self.sub_output = scrolledtext.ScrolledText(sub_frame, height=8, width=85)
        self.sub_output.pack(padx=5, pady=5)

    # ---------- port scanner ----------
    def _stop(self):
        self._stop_scan = True

    def _scan_async(self):
        target = self.target_entry.get().strip()
        try:
            start = int(self.start_port.get())
            end = int(self.end_port.get())
        except ValueError:
            messagebox.showerror("Invalid input", "Port range must be integers.")
            return
        if not (0 < start <= end <= 65535):
            messagebox.showerror("Invalid range", "Ports must be between 1 and 65535.")
            return
        if end - start > 5000:
            messagebox.showwarning("Range too large", "Limit scans to 5000 ports at a time.")
            return

        self._stop_scan = False
        self.scan_output.delete("1.0", tk.END)
        self.scan_btn.config(state="disabled")
        threading.Thread(target=self._scan, args=(target, start, end), daemon=True).start()

    def _scan(self, target, start, end):
        try:
            resolved = socket.gethostbyname(target)
        except socket.gaierror:
            self._log_scan(f"Could not resolve host: {target}")
            self.after(0, lambda: self.scan_btn.config(state="normal"))
            return

        self._log_scan(f"Scanning {target} ({resolved}) ports {start}-{end}...\n")
        open_ports = []

        for port in range(start, end + 1):
            if self._stop_scan:
                self._log_scan("Scan stopped by user.")
                break
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.3)
                result = s.connect_ex((resolved, port))
                if result == 0:
                    try:
                        service = socket.getservbyport(port)
                    except OSError:
                        service = "unknown"
                    open_ports.append(port)
                    self._log_scan(f"  [OPEN] {port}/tcp  ({service})")

        self._log_scan(f"\nDone. {len(open_ports)} open port(s) found.")
        logger.info(f"Port scan of {target} ({start}-{end}) found {len(open_ports)} open ports")
        self.after(0, lambda: self.scan_btn.config(state="normal"))

    def _log_scan(self, text):
        self.after(0, lambda: (self.scan_output.insert(tk.END, text + "\n"), self.scan_output.see(tk.END)))

    # ---------- subdomain finder ----------
    def _find_subdomains_async(self):
        domain = self.domain_entry.get().strip()
        if not domain:
            messagebox.showwarning("Missing domain", "Enter a domain first.")
            return
        self.sub_output.delete("1.0", tk.END)
        threading.Thread(target=self._find_subdomains, args=(domain,), daemon=True).start()

    def _find_subdomains(self, domain):
        self._log_sub(f"Checking {len(COMMON_SUBDOMAINS)} common subdomains for {domain}...\n")
        found = []
        for sub in COMMON_SUBDOMAINS:
            fqdn = f"{sub}.{domain}"
            try:
                ip = socket.gethostbyname(fqdn)
                found.append((fqdn, ip))
                self._log_sub(f"  [FOUND] {fqdn} -> {ip}")
            except socket.gaierror:
                pass
        self._log_sub(f"\nDone. {len(found)} subdomain(s) resolved.")
        logger.info(f"Subdomain scan of {domain} found {len(found)} results")

    def _log_sub(self, text):
        self.after(0, lambda: (self.sub_output.insert(tk.END, text + "\n"), self.sub_output.see(tk.END)))
