from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import all models here to ensure they are registered with SQLAlchemy metadata
from app.models.user import User
from app.models.pet import Pet
from app.models.feed_inventory import FeedInventory
from app.models.cooking_record import CookingRecord
from app.models.ingredient import Ingredient, IngredientModel
from app.models.recipe import Recipe
from app.models.collection import (
    get_all_stages,
    get_stages_by_species,
    get_stage_by_id,
    get_user_collection,
    unlock_stage,
    is_stage_unlocked,
    get_collection_progress
)

__all__ = [
    'db',
    'User',
    'Pet',
    'FeedInventory',
    'CookingRecord',
    'Ingredient',
    'IngredientModel',
    'Recipe',
    'get_all_stages',
    'get_stages_by_species',
    'get_stage_by_id',
    'get_user_collection',
    'unlock_stage',
    'is_stage_unlocked',
    'get_collection_progress',
]
