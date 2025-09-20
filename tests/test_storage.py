from pathlib import Path
import sqlite3

from app import storage


def test_init_and_crud(tmp_path: Path):
    db = tmp_path / "test.db"
    storage.init_db(db)

    # Add entries
    rid = storage.add_entry("example.com", "alice", "TOKEN1", db)
    assert isinstance(rid, int)

    rid2 = storage.add_entry("example.com", "bob", "TOKEN2", db)

    # List
    items = storage.list_entries(db)
    assert len(items) == 2
    assert items[0].secret in {"TOKEN1", "TOKEN2"}

    # Delete
    ok = storage.delete_entry(rid, db)
    assert ok is True

    # Delete non-existing
    ok2 = storage.delete_entry(9999, db)
    assert ok2 is False
