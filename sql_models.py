from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """使用者帳號"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    display_name = db.Column(db.String(80))
    cooking_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 關聯
    pet = db.relationship('Pet', backref='user', uselist=False, cascade="all, delete-orphan")
    preference = db.relationship('UserPreference', backref='user', uselist=False, cascade="all, delete-orphan")
    allergens = db.relationship('UserAllergen', backref='user', cascade="all, delete-orphan")
    favorites = db.relationship('Collection', backref='user', cascade="all, delete-orphan")
    achievements = db.relationship('UserAchievement', backref='user', cascade="all, delete-orphan")

    def set_password(self, password):
        """設定密碼（自動 hash）"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """驗證密碼"""
        return check_password_hash(self.password_hash, password)

    def check_achievements(self):
        """
        檢查使用者是否滿足任何尚未解鎖的成就。
        若滿足，則新增至 user_achievement，並回傳新解鎖的成就清單。
        """
        # 1. 查詢所有已解鎖的成就 ID
        unlocked_ids = [ua.achievement_id for ua in self.achievements]
        
        # 2. 查詢所有未解鎖的成就
        achievements_to_check = Achievement.query.filter(~Achievement.id.in_(unlocked_ids)).all() if unlocked_ids else Achievement.query.all()
        
        newly_unlocked = []
        
        # 3. 取得寵物等級
        pet_level = 1
        if self.pet:
            pet_level = self.pet.current_level
        else:
            # 原有的 raw SQL 寵物查詢
            from app.models.pet import Pet as RawPet
            pet = RawPet.get_by_user_id(self.id)
            if pet:
                pet_level = pet.get('level', 1)
                
        # 4. 取得圖鑑解鎖數量
        from app.models.collection import get_collection_progress
        try:
            progress = get_collection_progress(self.id)
            collection_count = progress.get('unlocked', 0)
        except Exception:
            collection_count = 0
        
        for ach in achievements_to_check:
            is_satisfied = False
            if ach.condition_type == 'cooking_count':
                is_satisfied = self.cooking_count >= ach.condition_value
            elif ach.condition_type == 'pet_level':
                is_satisfied = pet_level >= ach.condition_value
            elif ach.condition_type == 'unlocked_collection':
                is_satisfied = collection_count >= ach.condition_value
                
            if is_satisfied:
                ua = UserAchievement(user_id=self.id, achievement_id=ach.id)
                db.session.add(ua)
                newly_unlocked.append(ach)
                
        if newly_unlocked:
            db.session.commit()
            
        return newly_unlocked


class Pet(db.Model):
    """寵物狀態"""
    __tablename__ = 'user_pets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    species_id = db.Column(db.Integer, nullable=True)
    pet_name = db.Column(db.String(100), nullable=False)
    current_level = db.Column(db.Integer, default=1)
    current_exp = db.Column(db.Integer, default=0)
    current_stage_id = db.Column(db.Integer, nullable=True)
    hunger = db.Column(db.Integer, default=50)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserPreference(db.Model):
    """使用者偏好設定"""
    __tablename__ = 'user_preference'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    diet_type = db.Column(db.String(50), default='omnivore')
    spicy_ok = db.Column(db.Boolean, default=True)
    cooking_level = db.Column(db.String(50), default='beginner')
    max_cooking_time = db.Column(db.Integer, default=60)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserAllergen(db.Model):
    """使用者過敏原"""
    __tablename__ = 'user_allergen'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    allergen_name = db.Column(db.String(50), nullable=False)


class Recipe(db.Model):
    """食譜資料"""
    __tablename__ = 'recipe'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    tags = db.Column(db.String(255))          # 逗號分隔的標籤，如 "omnivore, spicy"
    cooking_time = db.Column(db.Integer)      # 分鐘
    difficulty = db.Column(db.String(50))     # beginner, intermediate, advanced
    allergens = db.Column(db.String(255))      # 逗號分隔的過敏原，如 "egg, milk"
    required_ingredients = db.Column(db.Text)  # 逗號分隔的食材，如 "番茄,雞蛋"



class Collection(db.Model):
    """使用者食譜收藏 (最愛食譜)"""
    __tablename__ = 'collection'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id', ondelete='CASCADE'), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)


class Achievement(db.Model):
    """成就定義"""
    __tablename__ = 'achievement'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    condition_type = db.Column(db.String(50), nullable=False) # cooking_count, pet_level, unlocked_collection
    condition_value = db.Column(db.Integer, nullable=False)


class UserAchievement(db.Model):
    """使用者成就解鎖紀錄"""
    __tablename__ = 'user_achievement'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievement.id', ondelete='CASCADE'), nullable=False)
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)
