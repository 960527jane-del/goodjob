from app.models import db
from datetime import datetime

class User(db.Model):
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
        user = cls(username=username, email=email)
        db.session.add(user)
        db.session.commit()
        return user
        
    @classmethod
    def get_by_id(cls, user_id):
        return cls.query.get(user_id)
        
    @classmethod
    def get_all(cls):
        return cls.query.all()
        
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
