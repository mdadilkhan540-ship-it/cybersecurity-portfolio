"""
modules/hash_crypto.py
Tool #3: Hashing & Encryption Utilities.
- MD5 / SHA256 hashing of text or files
- Fernet (symmetric) encryption & decryption with key generation/save/load
"""

import hashlib
import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

from cryptography.fernet import Fernet, InvalidToken

from utils.logger import get_logger

logger = get_logger(__name__)

KEY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(KEY_DIR, exist_ok=True)
DEFAULT_KEY_PATH = os.path.join(KEY_DIR, "fernet.key")


class HashCryptoFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#1e1e1e")
        self.fernet_key = None

        tk.Label(
            self, text="Hashing & Encryption", fg="#00ff9c", bg="#1e1e1e",
            font=("Consolas", 16, "bold")
        ).pack(pady=10)

        # ---------- Hashing ----------
        hash_frame = tk.LabelFrame(self, text="Hashing", fg="white", bg="#1e1e1e")
        hash_frame.pack(fill="x", padx=15, pady=5)

        self.hash_input = tk.Entry(hash_frame, width=55)
        self.hash_input.pack(side="left", padx=5, pady=5)

        self.algo_var = tk.StringVar(value="sha256")
        tk.OptionMenu(hash_frame, self.algo_var, "md5", "sha256").pack(side="left", padx=5)

        tk.Button(hash_frame, text="Hash Text", command=self._hash_text).pack(side="left", padx=5)
        tk.Button(hash_frame, text="Hash File", command=self._hash_file).pack(side="left", padx=5)

        self.hash_output = tk.Entry(self, width=80)
        self.hash_output.pack(padx=15, pady=5)

        # ---------- Encryption ----------
        enc_frame = tk.LabelFrame(self, text="Fernet Encryption", fg="white", bg="#1e1e1e")
        enc_frame.pack(fill="both", padx=15, pady=15, expand=True)

        key_btns = tk.Frame(enc_frame, bg="#1e1e1e")
        key_btns.pack(pady=5)
        tk.Button(key_btns, text="Generate Key", command=self._generate_key).grid(row=0, column=0, padx=5)
        tk.Button(key_btns, text="Load Key", command=self._load_key).grid(row=0, column=1, padx=5)
        self.key_label = tk.Label(enc_frame, text="No key loaded", fg="orange", bg="#1e1e1e")
        self.key_label.pack()

        self.enc_text = scrolledtext.ScrolledText(enc_frame, height=6, width=70)
        self.enc_text.pack(padx=5, pady=5)

        action_btns = tk.Frame(enc_frame, bg="#1e1e1e")
        action_btns.pack(pady=5)
        tk.Button(action_btns, text="Encrypt", width=15, command=self._encrypt).grid(row=0, column=0, padx=5)
        tk.Button(action_btns, text="Decrypt", width=15, command=self._decrypt).grid(row=0, column=1, padx=5)

    # ---------- hashing ----------
    def _hash_text(self):
        text = self.hash_input.get()
        algo = self.algo_var.get()
        digest = hashlib.new(algo, text.encode("utf-8")).hexdigest()
        self._set_output(digest)
        logger.info(f"Hashed text input with {algo}")

    def _hash_file(self):
        path = filedialog.askopenfilename()
        if not path:
            return
        algo = self.algo_var.get()
        h = hashlib.new(algo)
        try:
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
            self._set_output(h.hexdigest())
            logger.info(f"Hashed file {path} with {algo}")
        except OSError as e:
            messagebox.showerror("Error", str(e))

    def _set_output(self, value):
        self.hash_output.delete(0, tk.END)
        self.hash_output.insert(0, value)

    # ---------- encryption ----------
    def _generate_key(self):
        self.fernet_key = Fernet.generate_key()
        with open(DEFAULT_KEY_PATH, "wb") as f:
            f.write(self.fernet_key)
        self.key_label.config(text=f"Key generated & saved: {DEFAULT_KEY_PATH}", fg="#00ff9c")
        logger.info("Generated new Fernet key")

    def _load_key(self):
        path = filedialog.askopenfilename(initialdir=KEY_DIR)
        if not path:
            return
        with open(path, "rb") as f:
            self.fernet_key = f.read()
        self.key_label.config(text=f"Key loaded: {path}", fg="#00ff9c")
        logger.info(f"Loaded Fernet key from {path}")

    def _require_key(self):
        if not self.fernet_key:
            messagebox.showwarning("No key", "Generate or load a Fernet key first.")
            return False
        return True

    def _encrypt(self):
        if not self._require_key():
            return
        f = Fernet(self.fernet_key)
        plaintext = self.enc_text.get("1.0", tk.END).rstrip("\n")
        token = f.encrypt(plaintext.encode("utf-8"))
        self.enc_text.delete("1.0", tk.END)
        self.enc_text.insert(tk.END, token.decode("utf-8"))
        logger.info("Encrypted text block")

    def _decrypt(self):
        if not self._require_key():
            return
        f = Fernet(self.fernet_key)
        token = self.enc_text.get("1.0", tk.END).strip()
        try:
            plaintext = f.decrypt(token.encode("utf-8"))
            self.enc_text.delete("1.0", tk.END)
            self.enc_text.insert(tk.END, plaintext.decode("utf-8"))
            logger.info("Decrypted text block")
        except InvalidToken:
            messagebox.showerror("Decrypt failed", "Invalid token or wrong key.")
            logger.warning("Decryption failed: invalid token")
