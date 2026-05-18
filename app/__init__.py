import os
from flask import Flask
from app.models import db
from app.routes import register_blueprints

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'database.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
        
    # Ensure uploads folder exists
    try:
        os.makedirs(os.path.join(app.root_path, 'static', 'uploads'))
    except OSError:
        pass

    # Initialize extensions
    db.init_app(app)

    with app.app_context():
        # Create all tables using SQLAlchemy (matches schema.sql design)
        db.create_all()

    # Register blueprints
    register_blueprints(app)

    return app
