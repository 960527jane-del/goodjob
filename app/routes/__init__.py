from flask import Blueprint

# 1. 宣告你原本的藍圖
ingredient_bp = Blueprint('ingredient', __name__, url_prefix='/ingredients')
recipe_bp = Blueprint('recipe', __name__, url_prefix='/recipes')

# 2. 匯入你原本的路由實作（確保裡面的裝飾器如 @ingredient_bp.route 有被執行）
from . import ingredient
from . import recipe

# 此檔案可作為 Blueprint 的註冊點，供 app.py 載入
from app.routes.main import main_bp
from app.routes.cooking import cooking_bp
from app.routes.pet import pet_bp

def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(cooking_bp)
    app.register_blueprint(pet_bp)
# 註冊你原本的藍圖
    app.register_blueprint(ingredient_bp)
    app.register_blueprint(recipe_bp)