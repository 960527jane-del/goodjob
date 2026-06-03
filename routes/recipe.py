from flask import Blueprint, request, render_template

recipe_bp = Blueprint('recipe', __name__, url_prefix='/recipes')

@recipe_bp.route('/recommend', methods=['GET'])
def recommend_recipes():
    """推薦食譜列表 (F-02)"""
    # TODO: 讀取使用者庫存，比對食譜 required_ingredients
    return render_template('recipe_list.html')

@recipe_bp.route('/<int:id>', methods=['GET'])
def recipe_detail(id):
    """單一食譜詳細頁面"""
    # TODO: 查詢並顯示食譜詳細步驟與所需食材
    return render_template('recipe_detail.html')
