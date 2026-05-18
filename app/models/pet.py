from app.models import db
from datetime import datetime

class Pet(db.Model):
    __tablename__ = 'pets'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    level = db.Column(db.Integer, default=1)
    exp = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def create(cls, user_id, name):
        pet = cls(user_id=user_id, name=name)
        db.session.add(pet)
        db.session.commit()
        return pet
        
    @classmethod
    def get_by_id(cls, pet_id):
        return cls.query.get(pet_id)
        
    @classmethod
    def get_by_user_id(cls, user_id):
        return cls.query.filter_by(user_id=user_id).first()
        
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        
    def add_exp(self, amount, level_up_threshold=100):
        self.exp += amount
        if self.exp >= level_up_threshold:
            self.level += 1
            self.exp -= level_up_threshold
        db.session.commit()
