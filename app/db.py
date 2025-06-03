import sqlite3
from pathlib import Path
import os

DB_PATH = Path(os.environ.get("DATA_DIR", "./data")) / "crawl_status.db"

conn = sqlite3.connect(DB_PATH)
conn.execute("""
CREATE TABLE IF NOT EXISTS crawl_status (
    crawl_id TEXT PRIMARY KEY,
    status TEXT NOT NULL
);
""")
conn.commit()

def set_status(crawl_id: str, status: str):
    with conn:
        conn.execute("REPLACE INTO crawl_status (crawl_id, status) VALUES (?, ?)", (crawl_id, status))

def get_status(crawl_id: str):
    row = conn.execute("SELECT status FROM crawl_status WHERE crawl_id = ?", (crawl_id,)).fetchone()
    return row[0] if row else None
