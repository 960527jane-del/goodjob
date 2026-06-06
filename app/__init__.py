"""
隨「食」隨地 — Flask 應用程式初始化與 Blueprint 註冊 (F-01, F-02, F-03, F-06)
"""
import os
from flask import Flask
from app.database import close_db
from sql_models import db

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration
    from config import DATABASE, SECRET_KEY
    app.config['DATABASE'] = DATABASE
    app.config['SECRET_KEY'] = SECRET_KEY
    
    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Ensure instance directory exists
    os.makedirs(app.instance_path, exist_ok=True)
    
    # Register raw db teardown
    app.teardown_appcontext(close_db)
    
    # Initialize SQLAlchemy
    db.init_app(app)
    
    # Initialize Flask-Login
    from flask_login import LoginManager
    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    login_manager.login_message = '請先登入系統！'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)
    
    from sql_models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()
        
        
    # Register Blueprints
    from app.routes import register_blueprints
    register_blueprints(app)
    
    return app
