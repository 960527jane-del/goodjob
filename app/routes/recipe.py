from flask import render_template, current_app, flash, redirect, url_for
import requests
from . import recipe_bp
from app.models.ingredient import Ingredient

def get_mock_recipes():
    """提供測試用的食譜清單假資料"""
    return [
        {
            "id": 1,
            "title": "番茄炒蛋 (開發模式示範)",
            "image": "https://via.placeholder.com/312x231.png?text=Tomato+Eggs",
            "missedIngredientCount": 0,
            "usedIngredientCount": 2,
        },
        {
            "id": 2,
            "title": "洋蔥炒雞肉 (開發模式示範)",
            "image": "https://via.placeholder.com/312x231.png?text=Onion+Chicken",
            "missedIngredientCount": 1,
            "usedIngredientCount": 1,
        }
    ]

def get_mock_recipe_detail(recipe_id):
    """提供測試用的單一食譜詳細假資料"""
    return {
        "id": recipe_id,
        "title": "番茄炒蛋 (開發模式示範)",
        "image": "https://via.placeholder.com/556x370.png?text=Tomato+Eggs",
        "readyInMinutes": 15,
        "extendedIngredients": [
            {"original": "2 顆 番茄"},
            {"original": "3 顆 雞蛋"},
            {"original": "少許 鹽與油"}
        ],
        "instructions": "1. 番茄洗淨切塊。<br>2. 雞蛋打散備用。<br>3. 熱鍋下油，先將雞蛋炒熟後撈起。<br>4. 原鍋再加少許油，下番茄拌炒至軟爛出汁。<br>5. 將炒好的雞蛋倒回鍋中，加入鹽調味，翻炒均勻即可起鍋。"
    }

@recipe_bp.route('/recommend')
def recommend():
    """
    [GET] 導向智慧食譜推薦頁面，取代舊的推薦說明頁面。
    """
    return redirect(url_for('recipe.list_recipes'))


@recipe_bp.route('/')
def list_recipes():
    """
    [GET] 讀取使用者庫存食材，向外部 API 請求並顯示推薦食譜清單
    """
    user_id = 1 # MVP assumed user
    ingredients = Ingredient.get_by_user_id(user_id)
    if not ingredients:
        flash('您的材料庫目前是空的，無法為您推薦食譜。請先新增食材！', 'warning')
        return render_template('recipe/list.html', recipes=[])

    # 將現有食材串接為字串 (如: "番茄,雞蛋")
    ingredient_names = [item.name for item in ingredients]
    ingredients_str = ','.join(ingredient_names)

    api_key = current_app.config.get('RECIPE_API_KEY')
    # 若沒有設定有效的 API Key，自動降級使用假資料測試
    if not api_key or api_key == 'your_external_recipe_api_key_here':
        flash('目前尚未設定有效的 RECIPE_API_KEY，將顯示開發測試用的食譜資料。', 'info')
        recipes = get_mock_recipes()
    else:
        # 呼叫 Spoonacular API 搜尋符合現有食材的食譜
        url = "https://api.spoonacular.com/recipes/findByIngredients"
        params = {
            "ingredients": ingredients_str,
            "number": 5,          # 推薦 5 道食譜
            "ranking": 2,         # 最小化缺少的食材
            "apiKey": api_key
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            recipes = response.json()
        except Exception as e:
            flash(f'無法從外部 API 取得食譜資料，發生錯誤：{e}。目前顯示測試資料。', 'error')
            recipes = get_mock_recipes()

    return render_template('recipe/list.html', recipes=recipes)

@recipe_bp.route('/<int:id>')
def recipe_detail(id):
    """
    [GET] 根據食譜 ID 向外部 API 請求詳細步驟與配料，並與現有庫存比對
    """
    api_key = current_app.config.get('RECIPE_API_KEY')
    
    if not api_key or api_key == 'your_external_recipe_api_key_here':
        recipe = get_mock_recipe_detail(id)
    else:
        # 呼叫 Spoonacular API 取得食譜詳細教學與配料
        url = f"https://api.spoonacular.com/recipes/{id}/information"
        params = {
            "apiKey": api_key
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            recipe = response.json()
        except Exception as e:
            flash(f'無法取得食譜詳細資料，發生錯誤：{e}。目前顯示測試資料。', 'error')
            recipe = get_mock_recipe_detail(id)

    return render_template('recipe/detail.html', recipe=recipe)
