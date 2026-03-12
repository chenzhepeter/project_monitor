import sqlite3
import os
from config import DB_PATH

def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                company      TEXT    NOT NULL,
                title        TEXT    NOT NULL,
                url          TEXT    UNIQUE NOT NULL,
                source       TEXT,
                snippet      TEXT,
                summary      TEXT,
                published_at TEXT,
                created_at   TEXT    DEFAULT (datetime('now','localtime'))
            )
        """)
        conn.commit()

def is_seen(url: str) -> bool:
    """已存在的 URL 返回 True（去重用）"""
    with get_conn() as conn:
        row = conn.execute("SELECT 1 FROM articles WHERE url = ?", (url,)).fetchone()
        return row is not None

def save_article(company, title, url, source, snippet, summary, published_at):
    with get_conn() as conn:
        try:
            conn.execute(
                """INSERT INTO articles (company, title, url, source, snippet, summary, published_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (company, title, url, source, snippet, summary, published_at),
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # 重复 URL，忽略

def get_recent_articles(company: str, limit: int = 10):
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT * FROM articles WHERE company = ?
               ORDER BY created_at DESC LIMIT ?""",
            (company, limit),
        ).fetchall()
        return [dict(r) for r in rows]
