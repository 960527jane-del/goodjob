# 此檔案可作為 Blueprint 的註冊點，供 app.py 載入
from app.routes.main import main_bp
from app.routes.cooking import cooking_bp
from app.routes.pet import pet_bp

def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(cooking_bp)
    app.register_blueprint(pet_bp)
