import sqlite3
import os

ROOT = os.path.dirname(__file__) + os.sep + '..'
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

DB7 = os.path.join(ROOT, 'log.db7.db')
DB8 = os.path.join(ROOT, 'log.db8.db')


def test_db7_exists_and_has_rows():
    assert os.path.exists(DB7), f"{DB7} should exist"
    conn = sqlite3.connect(DB7)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='system_log'")
    assert cur.fetchone() is not None, "system_log table should exist in DB7"
    cur.execute("SELECT COUNT(*) FROM system_log")
    count = cur.fetchone()[0]
    conn.close()
    assert count > 0, "DB7 should have at least one row"


def test_db8_exists_and_has_rows():
    assert os.path.exists(DB8), f"{DB8} should exist"
    conn = sqlite3.connect(DB8)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='system_log'")
    assert cur.fetchone() is not None, "system_log table should exist in DB8"
    cur.execute("SELECT COUNT(*) FROM system_log")
    count = cur.fetchone()[0]
    conn.close()
    assert count > 0, "DB8 should have at least one row"
