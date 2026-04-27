import sqlite3
import json
from datetime import datetime

DB_PATH = "aide_memory.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fix_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            error_type TEXT,
            root_cause TEXT,
            fix_command TEXT,
            success INTEGER,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_fix(error_type, root_cause, fix_command, success: bool, error_key=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO fix_history (error_type, root_cause, fix_command, success, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (
        error_key or error_type,  # use specific key if provided
        root_cause,
        fix_command,
        int(success),
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

def lookup_past_fix(error_type: str, error_key=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT fix_command, success FROM fix_history
        WHERE error_type = ? AND success = 1
        ORDER BY timestamp DESC LIMIT 1
    """, (error_key or error_type,))
    row = cursor.fetchone()
    conn.close()
    return {"fix_command": row[0], "success": bool(row[1])} if row else None

def get_all_history():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fix_history ORDER BY timestamp DESC LIMIT 20")
    rows = cursor.fetchall()
    conn.close()
    return rows