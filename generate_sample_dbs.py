#!/usr/bin/env python3
"""Generate sample SQLite DB files: log.db7.db and log.db8.db

Creates a `system_log` table and populates it with synthetic data
representing week 7 and week 8 respectively.

Run: python generate_sample_dbs.py
"""
from datetime import datetime, timedelta
import sqlite3
import random


def make_db(filename: str, start_dt: datetime, rows: int = 200, interval_minutes: int = 60):
    conn = sqlite3.connect(filename)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS system_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            cpu REAL,
            memory REAL,
            disk REAL,
            ping_status TEXT,
            ping_ms REAL
        )
    """)
    conn.commit()

    ts = start_dt
    rows_inserted = 0
    for i in range(rows):
        cpu = round(random.uniform(1.0, 90.0), 2)
        mem = round(random.uniform(5.0, 95.0), 2)
        disk = round(random.uniform(1.0, 90.0), 2)
        ping_up = random.random() > 0.05
        ping_status = "UP" if ping_up else "DOWN"
        ping_ms = round(random.uniform(1.0, 350.0), 2) if ping_up else -1

        cur.execute(
            "INSERT INTO system_log (timestamp, cpu, memory, disk, ping_status, ping_ms) VALUES (?, ?, ?, ?, ?, ?)",
            (ts.strftime("%Y-%m-%d %H:%M:%S"), cpu, mem, disk, ping_status, ping_ms),
        )
        rows_inserted += 1
        ts = ts + timedelta(minutes=interval_minutes)

    conn.commit()
    conn.close()
    print(f"Wrote {rows_inserted} rows to {filename}")


def main():
    # week 7 sample: pick a 7-day window (2025-10-01)
    week7_start = datetime(2025, 10, 1, 0, 0, 0)
    make_db("log.db7.db", week7_start, rows=200, interval_minutes=60)

    # week 8 sample: pick a week after week7 (2025-10-08)
    week8_start = datetime(2025, 10, 8, 0, 0, 0)
    make_db("log.db8.db", week8_start, rows=200, interval_minutes=60)


if __name__ == "__main__":
    main()
