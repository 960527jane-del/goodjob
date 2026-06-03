from app.models import db
import logging

class Recipe(db.Model):
    """F-02: 食譜資料表模型"""
    __tablename__ = 'recipes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    required_ingredients = db.Column(db.Text, nullable=True) # JSON 或文字格式的食材清單
    image_url = db.Column(db.String(500), nullable=True)

    @classmethod
    def create(cls, title, description=None, required_ingredients=None, image_url=None):
        try:
            recipe = cls(title=title, description=description, required_ingredients=required_ingredients, image_url=image_url)
            db.session.add(recipe)
            db.session.commit()
            return recipe
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating recipe: {e}")
            return None

    @classmethod
    def get_all(cls):
        try:
            return cls.query.all()
        except Exception as e:
            logging.error(f"Error getting all recipes: {e}")
            return []

    @classmethod
    def get_by_id(cls, recipe_id):
        try:
            return cls.query.get(recipe_id)
        except Exception as e:
            logging.error(f"Error getting recipe by id: {e}")
            return None
