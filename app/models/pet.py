from app.models import db
from datetime import datetime
import logging

class Pet(db.Model):
    """虛擬寵物資料表模型"""
    __tablename__ = 'pets'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    level = db.Column(db.Integer, default=1)
    exp = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def create(cls, user_id, name):
        """新增一筆寵物記錄"""
        try:
            pet = cls(user_id=user_id, name=name)
            db.session.add(pet)
            db.session.commit()
            return pet
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating pet: {e}")
            return None
        
    @classmethod
    def get_by_id(cls, pet_id):
        """取得單筆寵物記錄"""
        try:
            return cls.query.get(pet_id)
        except Exception as e:
            logging.error(f"Error getting pet by id: {e}")
            return None
        
    @classmethod
    def get_by_user_id(cls, user_id):
        """取得指定使用者的寵物記錄"""
        try:
            return cls.query.filter_by(user_id=user_id).first()
        except Exception as e:
            logging.error(f"Error getting pet by user_id: {e}")
            return None
            
    @classmethod
    def get_all(cls):
        """取得所有寵物記錄"""
        try:
            return cls.query.all()
        except Exception as e:
            logging.error(f"Error getting all pets: {e}")
            return []
        
    def update(self, **kwargs):
        """更新寵物記錄"""
        try:
            for key, value in kwargs.items():
                setattr(self, key, value)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating pet: {e}")
            return False
        
    def delete(self):
        """刪除寵物記錄"""
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error deleting pet: {e}")
            return False
        
    def add_exp(self, amount, level_up_threshold=100):
        """增加寵物經驗值，若達標則升級"""
        try:
            self.exp += amount
            while self.exp >= level_up_threshold:
                self.level += 1
                self.exp -= level_up_threshold
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error adding exp to pet: {e}")
            return False
