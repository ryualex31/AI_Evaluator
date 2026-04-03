import sqlite3
import os
import json
from datetime import datetime

# Persistent DB path (important for deployment)
DB_PATH = os.getenv("DB_PATH", "logs.db")


# ---------- INIT DB ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Logs table (stores full interaction as JSON)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            data TEXT
        )
    """)

    # Feedback table (separate for clarity)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            data TEXT
        )
    """)

    conn.commit()
    conn.close()


# ---------- LOG INTERACTION ----------
def log_interaction(data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        **data
    }

    cursor.execute("""
        INSERT INTO logs (timestamp, data)
        VALUES (?, ?)
    """, (
        log_entry["timestamp"],
        json.dumps(log_entry)
    ))

    conn.commit()
    conn.close()


# ---------- LOG FEEDBACK ----------
def log_feedback(data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        **data
    }

    cursor.execute("""
        INSERT INTO feedback (timestamp, data)
        VALUES (?, ?)
    """, (
        log_entry["timestamp"],
        json.dumps(log_entry)
    ))

    conn.commit()
    conn.close()


# ---------- FETCH LOGS ----------
def get_logs(limit=50):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT data FROM logs
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = [json.loads(row[0]) for row in cursor.fetchall()]

    conn.close()
    return rows


# ---------- FETCH FEEDBACK ----------
def get_feedback(limit=50):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT data FROM feedback
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = [json.loads(row[0]) for row in cursor.fetchall()]

    conn.close()
    return rows


# ---------- CLEAR (OPTIONAL) ----------
def clear_logs():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM logs")
    conn.commit()
    conn.close()


def clear_feedback():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM feedback")
    conn.commit()
    conn.close()


# ---------- AUTO INIT ----------
init_db()
