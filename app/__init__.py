"""
隨「食」隨地 — Flask 應用程式初始化與 Blueprint 註冊 (F-01, F-02, F-03, F-06)
"""
import os
from flask import Flask
from app.database import close_db


def create_app():
    app = Flask(__name__)
    
    # 讀取專案設定
    from config import DATABASE, SECRET_KEY
    app.config['DATABASE'] = DATABASE
    app.config['SECRET_KEY'] = SECRET_KEY
    
    # 確保 instance 資料夾存在，以存放 SQLite 資料庫
    os.makedirs(app.instance_path, exist_ok=True)
    
    # 註冊資料庫 teardown context，在請求結束時關閉連線
    app.teardown_appcontext(close_db)
    
    # 註冊 Blueprints
    from app.routes.ingredient import ingredient_bp
    from app.routes.recipe import recipe_bp
    from app.routes.pet_routes import pet_bp
    from app.routes.collection_routes import collection_bp
    
    app.register_blueprint(ingredient_bp)
    app.register_blueprint(recipe_bp)
    app.register_blueprint(pet_bp)
    app.register_blueprint(collection_bp)
    
    return app
