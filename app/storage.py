"""SQLite storage layer for the password vault.

Tables:
- users: id INTEGER PRIMARY KEY AUTOINCREMENT,
         username TEXT UNIQUE NOT NULL,
         full_name TEXT,
         email TEXT,
         salt BLOB NOT NULL,
         verifier TEXT NOT NULL
- vault: id INTEGER PRIMARY KEY AUTOINCREMENT,
         user_id INTEGER NOT NULL,
         site TEXT NOT NULL,
         username TEXT NOT NULL,
         secret TEXT NOT NULL

Notes
-----
- Multi-user model; each user has their own salt. Vault rows scoped by user_id.
- `verifier` is an encrypted token used to validate the master password.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple, Dict, Any

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
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                full_name TEXT,
                email TEXT,
                salt BLOB NOT NULL,
                verifier TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                site TEXT NOT NULL,
                username TEXT NOT NULL,
                secret TEXT NOT NULL
            )
            """
        )
        # Best-effort migration: ensure vault has user_id column
        try:
            cur = conn.execute("PRAGMA table_info(vault)")
            cols = [r[1] for r in cur.fetchall()]
            if "user_id" not in cols:
                conn.execute("ALTER TABLE vault ADD COLUMN user_id INTEGER")
                conn.execute("UPDATE vault SET user_id = 1 WHERE user_id IS NULL")
        except Exception:
            pass
        conn.commit()


def add_entry(site: str, username: str, secret: str, user_id: int, db_path: Optional[Path] = None) -> int:
    """Insert a new entry and return new row id."""
    if not site or not username or not secret:
        raise ValueError("site, username and secret are required")
    with _connect(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO vault (user_id, site, username, secret) VALUES (?, ?, ?, ?)",
            (user_id, site, username, secret),
        )
        conn.commit()
        return int(cur.lastrowid)


def list_entries(user_id: int, db_path: Optional[Path] = None) -> List[VaultItem]:
    with _connect(db_path) as conn:
        cur = conn.execute(
            "SELECT id, site, username, secret FROM vault WHERE user_id = ? ORDER BY id DESC",
            (user_id,),
        )
        rows = cur.fetchall()
        return [VaultItem(id=row[0], site=row[1], username=row[2], secret=row[3]) for row in rows]


def delete_entry(entry_id: int, user_id: int, db_path: Optional[Path] = None) -> bool:
    with _connect(db_path) as conn:
        cur = conn.execute("DELETE FROM vault WHERE id = ? AND user_id = ?", (entry_id, user_id))
        conn.commit()
        return cur.rowcount > 0


# User management (single-user)

def get_user_by_username(username: str, db_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    with _connect(db_path) as conn:
        cur = conn.execute(
            "SELECT id, username, full_name, email, salt, verifier FROM users WHERE username = ?",
            (username,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "username": row[1],
            "full_name": row[2],
            "email": row[3],
            "salt": row[4],
            "verifier": row[5],
        }


def get_user_by_id(user_id: int, db_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    with _connect(db_path) as conn:
        cur = conn.execute(
            "SELECT id, username, full_name, email, salt, verifier FROM users WHERE id = ?",
            (user_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "username": row[1],
            "full_name": row[2],
            "email": row[3],
            "salt": row[4],
            "verifier": row[5],
        }


def create_user(username: str, full_name: str, email: str, salt: bytes, verifier: str, db_path: Optional[Path] = None) -> int:
    with _connect(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO users (username, full_name, email, salt, verifier) VALUES (?, ?, ?, ?, ?)",
            (username, full_name, email, salt, verifier),
        )
        conn.commit()
        return int(cur.lastrowid)


def update_user_verifier(user_id: int, verifier: str, db_path: Optional[Path] = None) -> None:
    with _connect(db_path) as conn:
        conn.execute("UPDATE users SET verifier = ? WHERE id = ?", (verifier, user_id))
        conn.commit()


def update_entry_secret(entry_id: int, secret: str, user_id: int, db_path: Optional[Path] = None) -> None:
    with _connect(db_path) as conn:
        conn.execute("UPDATE vault SET secret = ? WHERE id = ? AND user_id = ?", (secret, entry_id, user_id))
        conn.commit()
