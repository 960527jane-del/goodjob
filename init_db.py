import sqlite3
import os
from app import create_app
from app.models import db
from app.models.user import User

os.makedirs('instance', exist_ok=True)
db_path = os.path.join('instance', 'database.db')
schema_path = os.path.join('database', 'schema.sql')

print("Initializing SQLite database via schema.sql...")
with sqlite3.connect(db_path) as conn:
    conn.execute("PRAGMA foreign_keys = ON")
    with open(schema_path, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
print("Database schema loaded successfully at", db_path)

app = create_app()
with app.app_context():
    print("Initializing SQLAlchemy ORM tables...")
    db.create_all()
    
    # 檢查是否有預設使用者，如果沒有則建立一個
    user = db.session.get(User, 1)
    if not user:
        test_user = User(id=1, username='default_user', email='user@example.com')
        test_user.set_password('1234')
        db.session.add(test_user)
        db.session.commit()
        print("Default test user created in ORM!")
    else:
        # 確保密碼也是雜湊妥當的 (如果 schema.sql 插入的是文字或舊雜湊)
        if not user.password_hash or not user.password_hash.startswith(('scrypt:', 'pbkdf2:')):
            user.set_password('1234')
            db.session.commit()
            print("Default test user password updated in ORM!")
        else:
            print("Default test user already exists and is configured.")
