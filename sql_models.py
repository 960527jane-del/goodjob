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
    cooking_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 關聯
    collections = db.relationship('Collection', backref='user', lazy=True, cascade="all, delete-orphan")
    achievements = db.relationship('UserAchievement', backref='user', lazy=True, cascade="all, delete-orphan")
    preference = db.relationship('UserPreference', backref='user', uselist=False, cascade="all, delete-orphan")
    allergens = db.relationship('UserAllergen', backref='user', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        """設定密碼（自動 hash）"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """驗證密碼"""
        return check_password_hash(self.password_hash, password)


class UserPreference(db.Model):
    """使用者飲食偏好"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    diet_type = db.Column(db.String(20), default='omnivore')       # omnivore, vegetarian, vegan, pescatarian
    spicy_ok = db.Column(db.Boolean, default=True)                 # 是否接受辣
    cooking_level = db.Column(db.String(20), default='beginner')   # beginner, intermediate, advanced
    max_cooking_time = db.Column(db.Integer, default=60)           # 最長烹飪時間(分鐘)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserAllergen(db.Model):
    """使用者過敏原"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    allergen_name = db.Column(db.String(50), nullable=False)  # 花生, 牛奶, 蛋, 麩質, 海鮮, 堅果, 大豆

    __table_args__ = (
        db.UniqueConstraint('user_id', 'allergen_name', name='uq_user_allergen'),
    )


class Recipe(db.Model):
    """食譜"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    # F-07 新增欄位：用於偏好過濾
    tags = db.Column(db.String(200), default='')           # 逗號分隔標籤，如 'vegetarian,spicy,quick'
    cooking_time = db.Column(db.Integer, default=30)       # 烹飪時間(分鐘)
    difficulty = db.Column(db.String(20), default='beginner')  # beginner, intermediate, advanced
    allergens = db.Column(db.String(200), default='')      # 逗號分隔過敏原，如 'egg,milk'

    def get_tags_list(self):
        """取得標籤列表"""
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    def get_allergens_list(self):
        """取得過敏原列表"""
        if not self.allergens:
            return []
        return [a.strip() for a in self.allergens.split(',') if a.strip()]


class Collection(db.Model):
    """食譜收藏"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
    recipe = db.relationship('Recipe')


class Achievement(db.Model):
    """成就"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    icon = db.Column(db.String(50), nullable=False)  # emoji or icon class
    condition_type = db.Column(db.String(50), nullable=False)  # 'cook', 'collect'
    condition_value = db.Column(db.Integer, nullable=False)


class UserAchievement(db.Model):
    """使用者成就解鎖記錄"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievement.id'), nullable=False)
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)
    achievement = db.relationship('Achievement')


class Ingredient(db.Model):
    """庫存食材"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.Float, default=0.0)
    unit = db.Column(db.String(50), default='')
    expiry_date = db.Column(db.String(10), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def create(name, quantity, unit, expiry_date):
        ingredient = Ingredient(
            name=name,
            quantity=quantity,
            unit=unit,
            expiry_date=expiry_date or None
        )
        db.session.add(ingredient)
        db.session.commit()
        return ingredient.id

    @staticmethod
    def get_all():
        return Ingredient.query.order_by(Ingredient.created_at.desc()).all()

    @staticmethod
    def get_by_id(ingredient_id):
        return Ingredient.query.get(ingredient_id)

    @staticmethod
    def update(ingredient_id, name, quantity, unit, expiry_date):
        ingredient = Ingredient.query.get(ingredient_id)
        if not ingredient:
            return False
        ingredient.name = name
        ingredient.quantity = quantity
        ingredient.unit = unit
        ingredient.expiry_date = expiry_date or None
        db.session.commit()
        return True

    @staticmethod
    def delete(ingredient_id):
        ingredient = Ingredient.query.get(ingredient_id)
        if not ingredient:
            return False
        db.session.delete(ingredient)
        db.session.commit()
        return True
