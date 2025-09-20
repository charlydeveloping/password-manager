import os
import pytest

from app import crypto


def test_generate_salt_length():
    salt = crypto.generate_salt(16)
    assert isinstance(salt, bytes)
    assert len(salt) == 16


def test_derive_key_and_roundtrip():
    salt = crypto.generate_salt(16)
    key = crypto.derive_key("master123", salt)
    token = crypto.encrypt("secret", key)
    plain = crypto.decrypt(token, key)
    assert plain == "secret"


def test_decrypt_invalid_token():
    salt = crypto.generate_salt(16)
    k1 = crypto.derive_key("pw1", salt)
    k2 = crypto.derive_key("pw2", salt)
    token = crypto.encrypt("abc", k1)
    with pytest.raises(Exception):
        crypto.decrypt(token, k2)
