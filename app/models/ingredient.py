from app.models import db
from datetime import datetime
import logging

class Ingredient(db.Model):
    """F-01: 我的材料庫 (使用者擁有的食材)"""
    __tablename__ = 'ingredients'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, default=1.0)
    unit = db.Column(db.String(20), nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)  # F-03: 過期提醒
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def create(cls, user_id, name, quantity=1.0, unit=None, expiry_date=None):
        """新增一筆食材記錄"""
        try:
            ingredient = cls(user_id=user_id, name=name, quantity=quantity, unit=unit, expiry_date=expiry_date)
            db.session.add(ingredient)
            db.session.commit()
            return ingredient
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating ingredient: {e}")
            return None

    @classmethod
    def get_by_user_id(cls, user_id):
        """取得指定使用者的食材記錄，依過期日排序"""
        try:
            return cls.query.filter_by(user_id=user_id).order_by(cls.expiry_date.asc()).all()
        except Exception as e:
            logging.error(f"Error getting ingredients for user {user_id}: {e}")
            return []

    @classmethod
    def get_by_id(cls, ingredient_id):
        """根據 ID 取得單筆食材記錄"""
        try:
            return cls.query.get(ingredient_id)
        except Exception as e:
            logging.error(f"Error getting ingredient by id: {e}")
            return None

    def update(self, **kwargs):
        """更新特定食材記錄"""
        try:
            for key, value in kwargs.items():
                setattr(self, key, value)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating ingredient: {e}")
            return False

    def delete(self):
        """刪除特定食材記錄"""
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error deleting ingredient: {e}")
            return False

# Alias for backward compatibility
IngredientModel = Ingredient
