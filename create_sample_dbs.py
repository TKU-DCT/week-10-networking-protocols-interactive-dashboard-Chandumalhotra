"""Generate two sample SQLite databases for Week 7 and Week 8.

Generated files will be created in the current working directory as:
- log.db7.db  (Week 7 schema)
- log.db8.db  (Week 8 schema)

Run with: python create_sample_dbs.py
"""

import sqlite3
from datetime import datetime, timedelta
import random

NUM_ROWS = 30

now = datetime.now()

# Week 7 schema
def make_db7(path="log.db7.db"):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS system_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            cpu REAL,
            memory REAL,
            disk REAL,
            ping_status TEXT,
            ping_ms REAL
        )
    ''')
    conn.commit()

    # Insert sample rows
    for i in range(NUM_ROWS):
        ts = (now - timedelta(minutes=5 * (NUM_ROWS - i))).strftime("%Y-%m-%d %H:%M:%S")
        cpu = round(random.uniform(0, 95), 1)
        memory = round(random.uniform(0, 95), 1)
        disk = round(random.uniform(5, 95), 1)
        if random.random() < 0.1:
            ping_status = "DOWN"
            ping_ms = -1
        else:
            ping_status = "UP"
            ping_ms = round(random.uniform(1, 200), 1)
        cur.execute('INSERT INTO system_log (timestamp, cpu, memory, disk, ping_status, ping_ms) VALUES (?, ?, ?, ?, ?, ?)',
                    (ts, cpu, memory, disk, ping_status, ping_ms))

    conn.commit()
    conn.close()
    print("Created:", path)

# Week 8 schema
def make_db8(path="log.db8.db"):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS system_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            cpu_usage REAL,
            memory_usage REAL,
            disk_usage REAL,
            ping_status TEXT,
            ping_time REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()

    # Insert sample rows
    for i in range(NUM_ROWS):
        ts = (now - timedelta(minutes=5 * (NUM_ROWS - i))).strftime("%Y-%m-%d %H:%M:%S")
        cpu = round(random.uniform(0, 95), 1)
        memory = round(random.uniform(0, 95), 1)
        disk = round(random.uniform(5, 95), 1)
        if random.random() < 0.1:
            ping_status = "DOWN"
            ping_time = -1
        else:
            ping_status = "UP"
            ping_time = round(random.uniform(1, 200), 1)
        cur.execute('INSERT INTO system_log (timestamp, cpu_usage, memory_usage, disk_usage, ping_status, ping_time) VALUES (?, ?, ?, ?, ?, ?)',
                    (ts, cpu, memory, disk, ping_status, ping_time))

    conn.commit()
    conn.close()
    print("Created:", path)

if __name__ == '__main__':
    make_db7()
    make_db8()
