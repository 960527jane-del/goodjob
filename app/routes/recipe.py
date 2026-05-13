from flask import Blueprint, render_template

recipe_bp = Blueprint('recipe', __name__)

@recipe_bp.route('/recipes/recommend')
def recommend():
    """
    推薦食譜
    根據現有的材料庫資料，推薦可用的食譜。
    對應模板：recipes/recommend.html
    """
    pass
