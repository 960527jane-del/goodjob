from app import create_app
from app.models import db
from app.models.user import User

app = create_app()

with app.app_context():
    db.create_all()
    if not User.query.get(1):
        test_user = User(username='Test User', email='test@example.com')
        db.session.add(test_user)
        db.session.commit()
        print("Test user created!")
    else:
        print("Database already initialized.")
