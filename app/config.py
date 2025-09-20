"""
Project configuration for the Password Manager.
- Defines app data directory under the user's home: ~/.amparapass/
- Default database path: ~/.amparapass/passwords.db
- Salt file path for key derivation: ~/.amparapass/salt.bin

Keep secrets (like the master password) out of source control.
"""
from __future__ import annotations

from pathlib import Path

APP_NAME = "amparapass"
APP_DIR = Path.home() / f".{APP_NAME}"
DB_FILENAME = "passwords.db"
SALT_FILENAME = "salt.bin"

DB_PATH = APP_DIR / DB_FILENAME
SALT_PATH = APP_DIR / SALT_FILENAME

# Crypto parameters
PBKDF2_ITERATIONS = 390_000  # Reasonable default as of 2025
KEY_LENGTH = 32  # bytes for Fernet (32-byte key after URL-safe base64)


def ensure_app_dirs() -> None:
    """Ensure the application data directory exists."""
    APP_DIR.mkdir(parents=True, exist_ok=True)


def get_db_path() -> Path:
    ensure_app_dirs()
    return DB_PATH


def get_salt_path() -> Path:
    ensure_app_dirs()
    return SALT_PATH
