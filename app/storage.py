"""SQLite storage layer for the password vault.

Schema (table: vault):
- id INTEGER PRIMARY KEY AUTOINCREMENT
- site TEXT NOT NULL
- username TEXT NOT NULL
- secret TEXT NOT NULL  # encrypted password token (Fernet)

This layer is intentionally simple; callers pass already-encrypted secrets.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from .config import get_db_path


@dataclass
class VaultItem:
    id: int
    site: str
    username: str
    secret: str  # Fernet token


def _connect(db_path: Optional[Path] = None) -> sqlite3.Connection:
    path = db_path or get_db_path()
    return sqlite3.connect(path)


def init_db(db_path: Optional[Path] = None) -> None:
    """Create tables if not exist."""
    with _connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site TEXT NOT NULL,
                username TEXT NOT NULL,
                secret TEXT NOT NULL
            )
            """
        )
        conn.commit()


def add_entry(site: str, username: str, secret: str, db_path: Optional[Path] = None) -> int:
    """Insert a new entry and return new row id."""
    if not site or not username or not secret:
        raise ValueError("site, username and secret are required")
    with _connect(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO vault (site, username, secret) VALUES (?, ?, ?)",
            (site, username, secret),
        )
        conn.commit()
        return int(cur.lastrowid)


def list_entries(db_path: Optional[Path] = None) -> List[VaultItem]:
    with _connect(db_path) as conn:
        cur = conn.execute("SELECT id, site, username, secret FROM vault ORDER BY id DESC")
        rows = cur.fetchall()
        return [VaultItem(id=row[0], site=row[1], username=row[2], secret=row[3]) for row in rows]


def delete_entry(entry_id: int, db_path: Optional[Path] = None) -> bool:
    with _connect(db_path) as conn:
        cur = conn.execute("DELETE FROM vault WHERE id = ?", (entry_id,))
        conn.commit()
        return cur.rowcount > 0
