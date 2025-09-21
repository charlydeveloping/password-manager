from pathlib import Path
import sqlite3

from app import storage
from app import crypto


def test_init_and_crud(tmp_path: Path):
    db = tmp_path / "test.db"
    storage.init_db(db)
    # Create user
    salt = crypto.generate_salt(16)
    uid = storage.create_user("user1", "Alice", "alice@example.com", salt, "VERIFIER")

    # Add entries
    rid = storage.add_entry("example.com", "alice", "TOKEN1", uid, db)
    assert isinstance(rid, int)

    rid2 = storage.add_entry("example.com", "bob", "TOKEN2", uid, db)

    # List
    items = storage.list_entries(uid, db)
    assert len(items) == 2
    assert items[0].secret in {"TOKEN1", "TOKEN2"}

    # Delete
    ok = storage.delete_entry(rid, uid, db)
    assert ok is True

    # Delete non-existing
    ok2 = storage.delete_entry(9999, uid, db)
    assert ok2 is False
