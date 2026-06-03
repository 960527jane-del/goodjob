from app.models import db
from datetime import datetime
import logging

class CookingRecord(db.Model):
    """烹飪紀錄資料表模型"""
    __tablename__ = 'cooking_records'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id', ondelete='SET NULL'), nullable=True)
    image_path = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), nullable=False, default='completed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def create(cls, user_id, recipe_id=None, image_path=None, status='completed'):
        """新增一筆烹飪記錄"""
        try:
            record = cls(user_id=user_id, recipe_id=recipe_id, image_path=image_path, status=status)
            db.session.add(record)
            db.session.commit()
            return record
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating cooking record: {e}")
            return None
        
    @classmethod
    def get_by_id(cls, record_id):
        """取得單筆烹飪記錄"""
        try:
            return cls.query.get(record_id)
        except Exception as e:
            logging.error(f"Error getting cooking record by id: {e}")
            return None
        
    @classmethod
    def get_by_user_id(cls, user_id):
        """取得指定使用者的所有烹飪記錄"""
        try:
            return cls.query.filter_by(user_id=user_id).all()
        except Exception as e:
            logging.error(f"Error getting cooking records by user_id: {e}")
            return []
            
    @classmethod
    def get_all(cls):
        """取得所有烹飪記錄"""
        try:
            return cls.query.all()
        except Exception as e:
            logging.error(f"Error getting all cooking records: {e}")
            return []
        
    def update(self, **kwargs):
        """更新烹飪記錄"""
        try:
            for key, value in kwargs.items():
                setattr(self, key, value)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating cooking record: {e}")
            return False
        
    def delete(self):
        """刪除烹飪記錄"""
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error deleting cooking record: {e}")
            return False
