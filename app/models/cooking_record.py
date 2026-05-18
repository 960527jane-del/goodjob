from app.models import db
from datetime import datetime

class CookingRecord(db.Model):
    __tablename__ = 'cooking_records'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    image_path = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), nullable=False, default='completed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def create(cls, user_id, image_path=None, status='completed'):
        record = cls(user_id=user_id, image_path=image_path, status=status)
        db.session.add(record)
        db.session.commit()
        return record
        
    @classmethod
    def get_by_id(cls, record_id):
        return cls.query.get(record_id)
        
    @classmethod
    def get_by_user_id(cls, user_id):
        return cls.query.filter_by(user_id=user_id).all()
        
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
