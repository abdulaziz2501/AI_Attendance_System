import sqlite3

def init_db():
    conn = sqlite3.connect("data/attendance.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        date TEXT,
        time TEXT
    )
    """)
    conn.commit()
    conn.close()
