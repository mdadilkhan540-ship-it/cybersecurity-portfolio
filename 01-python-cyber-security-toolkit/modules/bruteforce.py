"""
modules/bruteforce.py
Tool #6: Wordlist Brute-Force Simulator.

Purely offline/local: you supply a hash and a wordlist file, and it checks
which word (if any) produces that hash. This is the same technique used to
audit password strength (e.g. checking your own hashed passwords against
known-weak wordlists) — it never contacts a network service or live login.
"""

import hashlib
import os
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

from utils.logger import get_logger

logger = get_logger(__name__)

SAMPLE_WORDLIST = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sample_wordlist.txt"
)


class BruteForceFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#1e1e1e")
        self._stop_flag = False

        tk.Label(
            self, text="Wordlist Brute-Force Simulator", fg="#00ff9c", bg="#1e1e1e",
            font=("Consolas", 16, "bold")
        ).pack(pady=10)
        tk.Label(
            self,
            text="Offline only: checks a wordlist against a hash you provide.\n"
                 "Use this to audit your own password hashes — not against live accounts.",
            fg="orange", bg="#1e1e1e", font=("Consolas", 9, "italic"), justify="center"
        ).pack()

        row1 = tk.Frame(self, bg="#1e1e1e")
        row1.pack(fill="x", padx=15, pady=10)
        tk.Label(row1, text="Target hash:", fg="white", bg="#1e1e1e").pack(side="left")
        self.hash_entry = tk.Entry(row1, width=50)
        self.hash_entry.pack(side="left", padx=5)

        self.algo_var = tk.StringVar(value="sha256")
        tk.OptionMenu(row1, self.algo_var, "md5", "sha1", "sha256").pack(side="left", padx=5)

        row2 = tk.Frame(self, bg="#1e1e1e")
        row2.pack(fill="x", padx=15, pady=5)
        tk.Label(row2, text="Wordlist file:", fg="white", bg="#1e1e1e").pack(side="left")
        self.wordlist_entry = tk.Entry(row2, width=50)
        self.wordlist_entry.insert(0, SAMPLE_WORDLIST)
        self.wordlist_entry.pack(side="left", padx=5)
        tk.Button(row2, text="Browse", command=self._browse).pack(side="left", padx=5)

        row3 = tk.Frame(self, bg="#1e1e1e")
        row3.pack(pady=10)
        self.run_btn = tk.Button(row3, text="Start", width=12, command=self._run_async)
        self.run_btn.pack(side="left", padx=5)
        tk.Button(row3, text="Stop", width=12, command=self._stop).pack(side="left", padx=5)
        tk.Button(row3, text="Generate sample wordlist", command=self._generate_sample).pack(side="left", padx=5)

        self.output = scrolledtext.ScrolledText(self, height=14, width=85)
        self.output.pack(padx=15, pady=5)

    def _browse(self):
        path = filedialog.askopenfilename()
        if path:
            self.wordlist_entry.delete(0, tk.END)
            self.wordlist_entry.insert(0, path)

    def _generate_sample(self):
        common = [
            "123456", "password", "qwerty", "letmein", "admin", "welcome",
            "monkey", "dragon", "football", "iloveyou", "trustno1", "sunshine",
        ]
        os.makedirs(os.path.dirname(SAMPLE_WORDLIST), exist_ok=True)
        with open(SAMPLE_WORDLIST, "w", encoding="utf-8") as f:
            f.write("\n".join(common))
        messagebox.showinfo("Done", f"Sample wordlist written to:\n{SAMPLE_WORDLIST}")
        logger.info("Generated sample wordlist")

    def _stop(self):
        self._stop_flag = True

    def _run_async(self):
        target_hash = self.hash_entry.get().strip().lower()
        wordlist_path = self.wordlist_entry.get().strip()

        if not target_hash:
            messagebox.showwarning("Missing hash", "Enter the target hash first.")
            return
        if not os.path.isfile(wordlist_path):
            messagebox.showwarning("Missing wordlist", "Pick a valid wordlist file.")
            return

        self._stop_flag = False
        self.output.delete("1.0", tk.END)
        self.run_btn.config(state="disabled")
        threading.Thread(target=self._run, args=(target_hash, wordlist_path), daemon=True).start()

    def _run(self, target_hash, wordlist_path):
        algo = self.algo_var.get()
        start = time.time()
        tried = 0
        found = None

        with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if self._stop_flag:
                    self._log("Stopped by user.")
                    break
                word = line.strip()
                if not word:
                    continue
                tried += 1
                digest = hashlib.new(algo, word.encode("utf-8")).hexdigest()
                if digest == target_hash:
                    found = word
                    break

        elapsed = time.time() - start
        if found:
            self._log(f"\nMATCH FOUND: '{found}'  (tried {tried} words in {elapsed:.2f}s)")
            logger.info(f"Brute-force match found after {tried} attempts")
        elif not self._stop_flag:
            self._log(f"\nNo match in wordlist. (tried {tried} words in {elapsed:.2f}s)")
            logger.info(f"Brute-force exhausted {tried} attempts with no match")

        self.after(0, lambda: self.run_btn.config(state="normal"))

    def _log(self, text):
        self.after(0, lambda: (self.output.insert(tk.END, text + "\n"), self.output.see(tk.END)))
