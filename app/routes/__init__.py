def register_blueprints(app):
    """
    註冊所有 Blueprint 到 Flask 應用程式
    """
    from app.routes.main import main_bp
    from app.routes.pet_routes import pet_bp
    from app.routes.collection_routes import collection_bp
    from app.routes.cooking import cooking_bp
    from app.routes.ingredient import ingredient_bp
    from app.routes.recipe import recipe_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(pet_bp)
    app.register_blueprint(collection_bp)
    app.register_blueprint(cooking_bp)
    app.register_blueprint(ingredient_bp)
    app.register_blueprint(recipe_bp)

