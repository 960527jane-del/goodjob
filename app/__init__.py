from flask import Flask, redirect, url_for

def create_app():
    app = Flask(__name__)
    
    # 這裡可以加入其他 app config，例如 SECRET_KEY 等
    
    # 註冊 Blueprint
    from app.routes.pet_routes import pet_bp
    app.register_blueprint(pet_bp)
    
    @app.route('/')
    def index():
        """首頁重導向至寵物頁面"""
        return redirect(url_for('pet.pet_index'))
        
    return app
