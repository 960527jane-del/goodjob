from flask import Blueprint, render_template
# 如果未來推薦食譜需要用到食材資料，可取消下方註解：
# from app.models.ingredient import Ingredient

recipe_bp = Blueprint('recipe', __name__)

@recipe_bp.route('/recipes/recommend')
def recommend():
    """
    推薦食譜
    根據現有的材料庫資料，推薦可用的食譜。
    對應模板：recipes/recommend.html
    """
    # 這裡未來可實作演算法或串接 AI
    # 目前僅作靜態畫面展示與串接準備
    return render_template('recipes/recommend.html')
