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
