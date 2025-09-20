"""Business logic connecting crypto and storage.

High-level contract:
- initialize(master_password: str) -> bytes: ensures app dirs, db, and salt; returns derived key
- add_password(key: bytes, site: str, username: str, password: str) -> int
- list_passwords(key: bytes) -> list[dict]: returns decrypted items [{id, site, username, password}]
- delete_password(entry_id: int) -> bool

Notes
-----
- Salt is stored in a file at SALT_PATH.
- If salt file doesn't exist, it's created. Changing salt later will break existing records.
- For simplicity we decrypt on listing; for large datasets, consider lazy decrypt on demand.
"""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import List, Dict

from . import config, crypto, storage


def _load_or_create_salt() -> bytes:
    path = config.get_salt_path()
    if path.exists():
        return path.read_bytes()
    salt = crypto.generate_salt()
    path.write_bytes(salt)
    return salt


def initialize(master_password: str) -> bytes:
    """Initialize app data and return derived key for this session."""
    config.ensure_app_dirs()
    storage.init_db()
    salt = _load_or_create_salt()
    key = crypto.derive_key(master_password, salt)
    return key


def add_password(key: bytes, site: str, username: str, password: str) -> int:
    token = crypto.encrypt(password, key)
    return storage.add_entry(site=site, username=username, secret=token)


def list_passwords(key: bytes) -> List[Dict[str, str]]:
    items = storage.list_entries()
    result: List[Dict[str, str]] = []
    for it in items:
        try:
            pwd = crypto.decrypt(it.secret, key)
        except Exception:
            pwd = "<unable to decrypt>"
        result.append({"id": it.id, "site": it.site, "username": it.username, "password": pwd})
    return result


def delete_password(entry_id: int) -> bool:
    return storage.delete_entry(entry_id)
