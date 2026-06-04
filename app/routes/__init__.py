# 匯入路由實作與藍圖
from . import ingredient
from . import recipe
from .ingredient import ingredient_bp
from .recipe import recipe_bp

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
