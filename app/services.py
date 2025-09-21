"""Business logic connecting crypto and storage.

High-level contract:
- initialize(master_password: str) -> bytes: legacy initializer (kept but not used in multi-user flows)
- register_user(username: str, full_name: str, email: str, master_password: str) -> tuple[int, bytes]
- login(username: str, master_password: str) -> tuple[int, bytes]
- get_user_profile(user_id: int) -> dict | None
- change_master_password(user_id: int, old_password: str, new_password: str) -> None
- add_password(user_id: int, key: bytes, site: str, username: str, password: str) -> int
- list_passwords(user_id: int, key: bytes) -> list[dict]
- delete_password(user_id: int, entry_id: int) -> bool

Notes
-----
- Salt is stored in a file at SALT_PATH.
- The `users.verifier` stores an encrypted constant using the derived key to validate the master password.
- Changing salt breaks decryption; salt is created once and reused.
"""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from . import config, crypto, storage


def _load_or_create_salt() -> bytes:
    # Legacy helper no longer used; kept for compatibility if initialize() is called
    return crypto.generate_salt()


def initialize(master_password: str) -> bytes:
    """Deprecated: kept for compatibility. Use register_user/login instead."""
    config.ensure_app_dirs()
    storage.init_db()
    salt = _load_or_create_salt()
    key = crypto.derive_key(master_password, salt)
    return key

def is_registered() -> bool:
    storage.init_db()
    # Not meaningful in multi-user; return True if any user exists
    return storage.get_user_by_id(1) is not None


def _derive_user_key(master_password: str, salt: bytes) -> bytes:
    return crypto.derive_key(master_password, salt)


def register_user(username: str, full_name: str, email: str, master_password: str) -> Tuple[int, bytes]:
    config.ensure_app_dirs()
    storage.init_db()
    if not username or len(username) < 3:
        raise ValueError("Username must be at least 3 characters")
    if storage.get_user_by_username(username) is not None:
        raise ValueError("Username already exists")
    # Password policy: min length 12, must include upper, lower, digit
    if len(master_password) < 12 or not any(c.islower() for c in master_password) or not any(c.isupper() for c in master_password) or not any(c.isdigit() for c in master_password):
        raise ValueError("Password must be 12+ chars with upper, lower, digit")
    salt = crypto.generate_salt(16)
    key = _derive_user_key(master_password, salt)
    verifier = crypto.encrypt("verification", key)
    user_id = storage.create_user(username=username, full_name=full_name, email=email, salt=salt, verifier=verifier)
    return user_id, key

def login(username: str, master_password: str) -> Tuple[int, bytes]:
    config.ensure_app_dirs()
    storage.init_db()
    user = storage.get_user_by_username(username)
    if user is None:
        raise ValueError("User not found")
    salt = user["salt"]
    key = _derive_user_key(master_password, salt)
    # verify
    try:
        val = crypto.decrypt(user["verifier"], key)
        if val != "verification":
            raise ValueError("Invalid master password")
    except Exception as ex:
        raise ValueError("Invalid master password") from ex
    return int(user["id"]), key


def get_user_profile(user_id: int) -> Optional[Dict[str, str]]:
    user = storage.get_user_by_id(user_id)
    if user is None:
        return None
    return {"username": user.get("username") or "", "full_name": user.get("full_name") or "", "email": user.get("email") or ""}


def add_password(user_id: int, key: bytes, site: str, username: str, password: str) -> int:
    token = crypto.encrypt(password, key)
    return storage.add_entry(site=site, username=username, secret=token, user_id=user_id)


def list_passwords(user_id: int, key: bytes) -> List[Dict[str, str]]:
    items = storage.list_entries(user_id)
    result: List[Dict[str, str]] = []
    for it in items:
        try:
            pwd = crypto.decrypt(it.secret, key)
        except Exception:
            pwd = "<unable to decrypt>"
        result.append({"id": it.id, "site": it.site, "username": it.username, "password": pwd})
    return result

def delete_password(user_id: int, entry_id: int) -> bool:
    return storage.delete_entry(entry_id, user_id)


def change_master_password(user_id: int, old_password: str, new_password: str) -> None:
    """Change master password by re-encrypting all secrets with new key and updating verifier.

    Steps:
    - derive old and new keys
    - decrypt each vault item with old key and re-encrypt with new key
    - update user verifier
    """
    storage.init_db()
    user = storage.get_user_by_id(user_id)
    if user is None:
        raise ValueError("No user registered")
    salt = user["salt"]
    old_key = _derive_user_key(old_password, salt)
    # verify old
    try:
        if crypto.decrypt(user["verifier"], old_key) != "verification":
            raise ValueError("Invalid old password")
    except Exception as ex:
        raise ValueError("Invalid old password") from ex

    # Password policy for new master password
    if len(new_password) < 12 or not any(c.islower() for c in new_password) or not any(c.isupper() for c in new_password) or not any(c.isdigit() for c in new_password):
        raise ValueError("Password must be 12+ chars with upper, lower, digit")
    new_key = _derive_user_key(new_password, salt)

    # re-encrypt vault
    items = storage.list_entries(user_id)
    for it in items:
        plaintext = crypto.decrypt(it.secret, old_key)
        new_token = crypto.encrypt(plaintext, new_key)
        storage.update_entry_secret(it.id, new_token, user_id)

    # update verifier
    new_verifier = crypto.encrypt("verification", new_key)
    storage.update_user_verifier(user_id, new_verifier)


def update_password(user_id: int, key: bytes, entry_id: int, new_password: str) -> None:
    """Update a single vault entry's password by re-encrypting its secret."""
    token = crypto.encrypt(new_password, key)
    storage.update_entry_secret(entry_id, token, user_id)
