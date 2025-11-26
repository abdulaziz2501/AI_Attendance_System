import sqlite3
from datetime import date

def handle_query(query):
    conn = sqlite3.connect("data/attendance.db")
    c = conn.cursor()
    today = date.today()

    if "nechta" in query or "davomat" in query:
        c.execute("SELECT COUNT(*) FROM attendance WHERE date=?", (today,))
        count = c.fetchone()[0]
        return f"Bugun {count} o‘quvchi keldi."
    elif "bugun" in query and "ism" in query:
        c.execute("SELECT name FROM attendance WHERE date=?", (today,))
        names = [row[0] for row in c.fetchall()]
        return f"Bugun kelgan o‘quvchilar: {', '.join(names)}"
    else:
        return "Kechirasiz, savolingizni tushunmadim."
