"""
Project configuration for the Password Manager.
- App data directory: ~/.amparapass/
- Database path: ~/.amparapass/passwords.db

Notes
-----
- In multi-user mode, the salt is stored per-user inside the database (table `users`).
- Do not store the derived key on disk.
"""
from __future__ import annotations

from pathlib import Path

APP_NAME = "amparapass"
APP_DIR = Path.home() / f".{APP_NAME}"
DB_FILENAME = "passwords.db"

DB_PATH = APP_DIR / DB_FILENAME

# Crypto parameters
PBKDF2_ITERATIONS = 390_000  # Reasonable default as of 2025
KEY_LENGTH = 32  # bytes for Fernet (32-byte key after URL-safe base64)


def ensure_app_dirs() -> None:
    """Ensure the application data directory exists."""
    APP_DIR.mkdir(parents=True, exist_ok=True)


def get_db_path() -> Path:
    ensure_app_dirs()
    return DB_PATH
