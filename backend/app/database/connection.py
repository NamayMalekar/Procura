import sqlite3
from pathlib import Path


def connect(path=":memory:"):
    if path != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def clone_in_memory(conn):
    """Exact copy of the database in RAM. The validator tests actions on this copy."""
    dst = connect(":memory:")
    conn.backup(dst)
    return dst
