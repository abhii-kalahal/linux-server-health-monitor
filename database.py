import sqlite3
import os

DB_PATH = "data/monitor.db"

def get_connection():
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect(DB_PATH)

def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            cpu REAL,
            memory REAL,
            disk REAL,
            uptime REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS security_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            event_type TEXT,
            details TEXT
        )
    """)

    conn.commit()
    conn.close()

def save_metrics(data):
    conn = get_connection()
    conn.execute("""
        INSERT INTO metrics (timestamp, cpu, memory, disk, uptime)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data["timestamp"],
        data["cpu"],
        data["memory"],
        data["disk"],
        data["uptime"]
    ))
    conn.commit()
    conn.close()

def get_metrics_history(limit=50):
    conn = get_connection()
    rows = conn.execute("""
        SELECT timestamp, cpu, memory, disk, uptime
        FROM metrics ORDER BY id DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return rows[::-1]

def save_security_event(timestamp, event_type, details):
    conn = get_connection()
    conn.execute("""
        INSERT INTO security_events (timestamp, event_type, details)
        VALUES (?, ?, ?)
    """, (timestamp, event_type, details))
    conn.commit()
    conn.close()

def get_security_events(limit=100):
    conn = get_connection()
    rows = conn.execute("""
        SELECT timestamp, event_type, details
        FROM security_events ORDER BY id DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return rows
