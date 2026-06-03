from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """使用者帳號"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    display_name = db.Column(db.String(80))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 關聯
    pet = db.relationship('Pet', backref='user', uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        """設定密碼（自動 hash）"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """驗證密碼"""
        return check_password_hash(self.password_hash, password)


class Pet(db.Model):
    """寵物狀態"""
    __tablename__ = 'pets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    hunger = db.Column(db.Integer, default=100)  # 飢餓度 (預設 100)
    growth = db.Column(db.Integer, default=0)    # 成長值 (預設 0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
