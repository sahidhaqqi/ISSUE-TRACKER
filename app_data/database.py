import sqlite3
from config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS daily_issues
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  lokasi TEXT, issue TEXT, link TEXT, progress TEXT,
                  supeng TEXT, root_cause TEXT, tanggal TEXT)''')
    conn.commit()
    conn.close()

def get_all_data():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, lokasi, issue, link, progress, supeng, root_cause, tanggal FROM daily_issues ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return [(r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[0]) for r in rows]

def insert_data(lokasi, issue, link, progress, supeng, root_cause, tanggal):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO daily_issues (lokasi, issue, link, progress, supeng, root_cause, tanggal) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (lokasi, issue, link, progress, supeng, root_cause, tanggal))
    conn.commit()
    conn.close()

def update_data(id_db, lokasi, issue, link, progress, supeng, root_cause):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE daily_issues SET lokasi=?, issue=?, link=?, progress=?, supeng=?, root_cause=? WHERE id=?",
              (lokasi, issue, link, progress, supeng, root_cause, id_db))
    conn.commit()
    conn.close()

def delete_data(id_db):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM daily_issues WHERE id = ?", (id_db,))
    conn.commit()
    conn.close()
