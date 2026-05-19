"""
資料庫連線工具模組
使用 Flask 的 g 物件管理連線生命週期
"""
import sqlite3
from flask import g, current_app


def get_db():
    """取得資料庫連線（每次 request 共用同一連線）"""
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    """關閉資料庫連線（由 teardown_appcontext 自動呼叫）"""
    db = g.pop('db', None)
    if db is not None:
        db.close()
