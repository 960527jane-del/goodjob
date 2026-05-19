import os
import sqlite3
from flask import Flask
from app.routes.ingredient import ingredient_bp
from app.routes.recipe import recipe_bp

def create_app():
    app = Flask(__name__)
    # 設定一個開發用的 SECRET_KEY，實際部署應該從環境變數讀取
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key')

    # 確保 instance 資料夾存在以存放 SQLite 資料庫
    os.makedirs(app.instance_path, exist_ok=True)

    # 註冊 Blueprints
    app.register_blueprint(ingredient_bp)
    app.register_blueprint(recipe_bp)

    return app
