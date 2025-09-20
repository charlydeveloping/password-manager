"""Crypto utilities: key derivation and symmetric encryption.

This module exposes minimal, testable functions:
- derive_key(master_password: str, salt: bytes) -> bytes
- generate_salt(length: int = 16) -> bytes
- encrypt(plaintext: str, key: bytes) -> str  # returns Fernet token (base64 str)
- decrypt(token: str, key: bytes) -> str

Notes
-----
- We use PBKDF2HMAC with SHA256 and a high iteration count.
- For storage, callers should persist the salt separately (e.g., in config SALT_PATH).
- We use Fernet (cryptography.fernet) for authenticated encryption.
"""
from __future__ import annotations

from base64 import urlsafe_b64encode
import os
from typing import Final

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet, InvalidToken

from . import config


def generate_salt(length: int = 16) -> bytes:
    """Generate a random salt of given length in bytes."""
    if length <= 0:
        raise ValueError("salt length must be positive")
    return os.urandom(length)


def derive_key(master_password: str, salt: bytes) -> bytes:
    """Derive a Fernet-compatible key from the master password and salt.

    Returns the urlsafe base64-encoded key bytes accepted by Fernet.
    """
    if not isinstance(master_password, str) or master_password == "":
        raise ValueError("master_password must be a non-empty string")
    if not isinstance(salt, (bytes, bytearray)) or len(salt) == 0:
        raise ValueError("salt must be non-empty bytes")

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=config.KEY_LENGTH,
        salt=bytes(salt),
        iterations=config.PBKDF2_ITERATIONS,
    )
    key = kdf.derive(master_password.encode("utf-8"))
    # Fernet requires a base64-encoded 32-byte key
    return urlsafe_b64encode(key)


def encrypt(plaintext: str, key: bytes) -> str:
    """Encrypt a plaintext string and return a Fernet token (str)."""
    if not isinstance(plaintext, str):
        raise TypeError("plaintext must be a string")
    f = Fernet(key)
    token = f.encrypt(plaintext.encode("utf-8"))
    return token.decode("utf-8")


def decrypt(token: str, key: bytes) -> str:
    """Decrypt a Fernet token and return the plaintext string.

    Raises InvalidToken if the key is wrong or token is corrupted.
    """
    if not isinstance(token, str):
        raise TypeError("token must be a string")
    f = Fernet(key)
    try:
        plaintext = f.decrypt(token.encode("utf-8"))
    except InvalidToken:
        raise
    return plaintext.decode("utf-8")
