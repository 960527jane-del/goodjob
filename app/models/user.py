from app.models import db
from datetime import datetime
import logging

class User(db.Model):
    """使用者資料表模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    pets = db.relationship('Pet', backref='owner', lazy=True, cascade="all, delete-orphan")
    feed_inventory = db.relationship('FeedInventory', backref='owner', uselist=False, cascade="all, delete-orphan")
    cooking_records = db.relationship('CookingRecord', backref='cook', lazy=True, cascade="all, delete-orphan")

    @classmethod
    def create(cls, username, email):
        """新增一筆使用者記錄"""
        try:
            user = cls(username=username, email=email)
            db.session.add(user)
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating user: {e}")
            return None
        
    @classmethod
    def get_by_id(cls, user_id):
        """取得單筆使用者記錄"""
        try:
            return cls.query.get(user_id)
        except Exception as e:
            logging.error(f"Error getting user by id: {e}")
            return None
        
    @classmethod
    def get_all(cls):
        """取得所有使用者記錄"""
        try:
            return cls.query.all()
        except Exception as e:
            logging.error(f"Error getting all users: {e}")
            return []
        
    def update(self, **kwargs):
        """更新使用者記錄"""
        try:
            for key, value in kwargs.items():
                setattr(self, key, value)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating user: {e}")
            return False
        
    def delete(self):
        """刪除使用者記錄"""
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error deleting user: {e}")
            return False
