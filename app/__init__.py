import os
import sqlite3
from flask import Flask

def create_app():
    # 初始化 Flask 應用程式
    app = Flask(__name__, instance_relative_config=True)
    
    # 載入基礎設定
    app.config.from_object('app.config.Config')
    
    # 設定資料庫路徑
    app.config['DATABASE'] = os.path.join(app.instance_path, 'database.db')

    # 確保 instance 目錄存在 (存放 sqlite 資料庫)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 註冊 Blueprints (路由)
    from .routes import ingredient_bp, recipe_bp
    app.register_blueprint(ingredient_bp)
    app.register_blueprint(recipe_bp)

    return app

def init_db(app=None):
    """
    初始化資料庫。
    可用於獨立腳本執行，或是後續 CLI 指令調用。
    """
    if app is None:
        app = create_app()
        
    db_path = app.config['DATABASE']
    schema_path = os.path.join(os.path.dirname(app.root_path), 'database', 'schema.sql')
    
    with sqlite3.connect(db_path) as conn:
        with open(schema_path, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
    print(f"資料庫已初始化於：{db_path}")
