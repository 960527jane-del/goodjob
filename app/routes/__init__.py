from flask import Blueprint

# 定義藍圖
ingredient_bp = Blueprint('ingredient', __name__, url_prefix='/ingredients')
recipe_bp = Blueprint('recipe', __name__, url_prefix='/recipes')

# 匯入路由實作
from . import ingredient
from . import recipe

# 從其他模組匯入藍圖
from app.routes.main import main_bp
from app.routes.cooking import cooking_bp
from app.routes.pet_routes import pet_bp
from app.routes.collection_routes import collection_bp

def register_blueprints(app):
    """
    註冊所有 Blueprint 到 Flask 應用程式
    """
    app.register_blueprint(main_bp)
    app.register_blueprint(pet_bp)
    app.register_blueprint(collection_bp)
    app.register_blueprint(cooking_bp)
    app.register_blueprint(ingredient_bp)
    app.register_blueprint(recipe_bp)
