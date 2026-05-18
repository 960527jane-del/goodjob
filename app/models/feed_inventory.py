from app.models import db
from datetime import datetime

class FeedInventory(db.Model):
    __tablename__ = 'feed_inventories'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    count = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def create(cls, user_id, count=0):
        inventory = cls(user_id=user_id, count=count)
        db.session.add(inventory)
        db.session.commit()
        return inventory
        
    @classmethod
    def get_by_user_id(cls, user_id):
        return cls.query.filter_by(user_id=user_id).first()
        
    def add_feed(self, amount=1):
        self.count += amount
        db.session.commit()
        
    def consume_feed(self, amount=1):
        if self.count >= amount:
            self.count -= amount
            db.session.commit()
            return True
        return False
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
