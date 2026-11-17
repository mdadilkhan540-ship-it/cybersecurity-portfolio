"""
utils/logger.py
Central logging utility for the toolkit. Every module imports get_logger()
so all activity (tool launches, scans, errors) lands in one timestamped
log file under logs/.
"""

import logging
import os
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

_LOG_FILE = os.path.join(LOG_DIR, f"toolkit_{datetime.now().strftime('%Y%m%d')}.log")

_configured = False


def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger that writes to both the daily log file and the console.
    Call this at the top of every module: logger = get_logger(__name__)
    """
    global _configured
    root = logging.getLogger("cyber_toolkit")

    if not _configured:
        root.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        fmt = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(fmt)
        console_handler.setFormatter(fmt)

        root.addHandler(file_handler)
        root.addHandler(console_handler)
        _configured = True

    return logging.getLogger(f"cyber_toolkit.{name}")
