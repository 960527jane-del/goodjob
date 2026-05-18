from app.models import db
from datetime import datetime
import logging

class FeedInventory(db.Model):
    """飼料庫存資料表模型"""
    __tablename__ = 'feed_inventories'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    count = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def create(cls, user_id, count=0):
        """新增一筆飼料庫存記錄"""
        try:
            inventory = cls(user_id=user_id, count=count)
            db.session.add(inventory)
            db.session.commit()
            return inventory
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating feed inventory: {e}")
            return None
        
    @classmethod
    def get_by_id(cls, inventory_id):
        """取得單筆庫存記錄"""
        try:
            return cls.query.get(inventory_id)
        except Exception as e:
            logging.error(f"Error getting feed inventory by id: {e}")
            return None
            
    @classmethod
    def get_by_user_id(cls, user_id):
        """取得指定使用者的庫存記錄"""
        try:
            return cls.query.filter_by(user_id=user_id).first()
        except Exception as e:
            logging.error(f"Error getting feed inventory by user_id: {e}")
            return None
            
    @classmethod
    def get_all(cls):
        """取得所有庫存記錄"""
        try:
            return cls.query.all()
        except Exception as e:
            logging.error(f"Error getting all feed inventories: {e}")
            return []
            
    def update(self, **kwargs):
        """更新庫存記錄"""
        try:
            for key, value in kwargs.items():
                setattr(self, key, value)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating feed inventory: {e}")
            return False
        
    def add_feed(self, amount=1):
        """增加飼料數量"""
        try:
            self.count += amount
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error adding feed: {e}")
            return False
        
    def consume_feed(self, amount=1):
        """扣除飼料數量，若不足則回傳 False"""
        try:
            if self.count >= amount:
                self.count -= amount
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error consuming feed: {e}")
            return False
        
    def delete(self):
        """刪除庫存記錄"""
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error deleting feed inventory: {e}")
            return False
