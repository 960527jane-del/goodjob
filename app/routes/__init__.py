from flask import Blueprint

# 1. 宣告材料庫藍圖 (供後續實作檔案 import)
ingredient_bp = Blueprint('ingredient', __name__, url_prefix='/ingredients')

# 2. 匯入路由實作，確保其中的裝飾器被執行
from . import ingredient

# 3. 匯入其他模組已宣告的藍圖
from app.routes.main import main_bp
from app.routes.cooking import cooking_bp
from app.routes.pet_routes import pet_bp
from app.routes.collection_routes import collection_bp

def register_blueprints(app):
    """
    註冊全站所有 Blueprint
    """
    app.register_blueprint(main_bp)
    app.register_blueprint(cooking_bp)
    app.register_blueprint(pet_bp)
    app.register_blueprint(collection_bp)
    app.register_blueprint(ingredient_bp)
