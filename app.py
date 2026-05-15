from flask import Flask, redirect, url_for
import os

def create_app():
    # 建立與設定 app
    app = Flask(__name__)
    
    # 設定 SECRET_KEY (用於 session 等安全機制)
    # 這裡預設會去讀環境變數，如果沒有就給一個開發用的預設值
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
    )

    # 註冊藍圖 (Blueprints)
    from app.routes.pet_routes import pet_bp
    app.register_blueprint(pet_bp)

    # 設定首頁重導向至寵物頁面
    @app.route('/')
    def index():
        return redirect(url_for('pet.index'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
