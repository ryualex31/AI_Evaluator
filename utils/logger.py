import sqlite3
import os
import json
from datetime import datetime

# Persistent DB path
DB_PATH = os.getenv("DB_PATH", "logs.db")


if os.getenv("RESET_DB") == "true":
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

# ---------- INIT DB ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Logs table (structured + raw JSON)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,

            -- User
            user_email TEXT,

            -- Query
            query TEXT,
            intent TEXT,

            -- SQL
            sql_query TEXT,

            -- Output
            response TEXT,

            -- Evaluation metrics
            accuracy INTEGER,
            coverage INTEGER,
            faithfulness INTEGER,
            clarity INTEGER,
            overall_score INTEGER,

            -- System
            retries INTEGER,

            -- Raw payload
            data TEXT
        )
    """)

    # Feedback table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            user_email TEXT,
            query TEXT,
            response TEXT,
            feedback TEXT,
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

    evaluation = data.get("evaluation", {})

    cursor.execute("""
        INSERT INTO logs (
            timestamp, user_email, query, intent,
            sql_query, response,
            accuracy, coverage, faithfulness, clarity, overall_score,
            retries, data
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        log_entry["timestamp"],
        data.get("user_email"),
        data.get("query"),
        data.get("intent"),
        data.get("sql_query"),
        data.get("summary") or data.get("response"),

        evaluation.get("accuracy"),
        evaluation.get("coverage"),
        evaluation.get("faithfulness"),
        evaluation.get("clarity"),
        evaluation.get("overall"),

        data.get("retries"),
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
        INSERT INTO feedback (
            timestamp, user_email, query, response, feedback, data
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        log_entry["timestamp"],
        data.get("user_email"),
        data.get("query"),
        data.get("response"),
        data.get("feedback"),
        json.dumps(log_entry)
    ))

    conn.commit()
    conn.close()


# ---------- FETCH LOGS ----------
def get_logs(limit=50):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            timestamp, user_email, query, intent,
            sql_query, response,
            accuracy, coverage, faithfulness, clarity, overall_score,
            retries
        FROM logs
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    columns = [col[0] for col in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

    conn.close()
    return rows


# ---------- FETCH FEEDBACK ----------
def get_feedback(limit=50):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT timestamp, user_email, query, response, feedback
        FROM feedback
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    columns = [col[0] for col in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

    conn.close()
    return rows


# ---------- CLEAR ----------
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