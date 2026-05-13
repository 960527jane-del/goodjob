"""
隨「食」隨地 — Flask 應用程式入口
"""
import os
import sqlite3
from flask import Flask
from config import DATABASE, SECRET_KEY
from models.db import close_db
from routes.collection_routes import collection_bp


def create_app():
    app = Flask(__name__)
    app.config['DATABASE'] = DATABASE
    app.config['SECRET_KEY'] = SECRET_KEY

    # 確保 instance 資料夾存在
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)

    # 註冊 teardown
    app.teardown_appcontext(close_db)

    # 註冊 Blueprint
    app.register_blueprint(collection_bp)

    # 初始化資料庫
    init_db(app)

    # 首頁導向圖鑑（開發用）
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('collection.collection_index'))

    return app


def init_db(app):
    """執行 SQL Schema 並插入種子資料"""
    schema_path = os.path.join(os.path.dirname(__file__), 'schema', 'pet_collection.sql')

    with app.app_context():
        conn = sqlite3.connect(app.config['DATABASE'])
        conn.execute("PRAGMA foreign_keys = ON")

        with open(schema_path, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())

        conn.close()


# 開發模式啟動
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
