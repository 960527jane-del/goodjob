"""
隨「食」隨地 — 資料庫連線工具模組 (F-01, F-03, F-06)
"""
import sqlite3
import os
from flask import g, current_app

# 取得目前檔案所在的絕對路徑的上一層 (goodjob/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
DB_PATH = os.path.join(INSTANCE_DIR, 'database.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'database', 'schema.sql')


def get_db_connection():
    """取得獨立資料庫連線並設定 row_factory，適合非 request 生命週期的操作"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_db():
    """取得 Request 範疇內的資料庫連線（每次 request 共用同一連線）"""
    if 'db' not in g:
        db_file = current_app.config.get('DATABASE', DB_PATH)
        g.db = sqlite3.connect(db_file)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    """關閉資料庫連線（由 Flask teardown_appcontext 自動呼叫）"""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """初始化資料庫與資料表"""
    # 確保 instance 資料夾存在
    if not os.path.exists(INSTANCE_DIR):
        os.makedirs(INSTANCE_DIR)
        
    conn = get_db_connection()
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("Database initialized successfully.")


if __name__ == '__main__':
    init_db()
