from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import all models here to ensure they are registered with SQLAlchemy metadata
from app.models.user import User
from app.models.pet import Pet
from app.models.feed_inventory import FeedInventory
from app.models.cooking_record import CookingRecord

__all__ = [
    'db',
    'User',
    'Pet',
    'FeedInventory',
    'CookingRecord',
    'IngredientModel'
]
