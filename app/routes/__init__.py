from flask import Blueprint

# 初始化 Blueprints
ingredient_bp = Blueprint('ingredient', __name__, url_prefix='/ingredients')
recipe_bp = Blueprint('recipe', __name__, url_prefix='/recipes')

# 匯入各個路由模組以註冊路由
from . import ingredient
from . import recipe
