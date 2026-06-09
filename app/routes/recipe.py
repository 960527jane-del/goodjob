from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
from sql_models import db, Recipe, Collection, UserPreference, UserAllergen, UserAchievement, Achievement, Pet as SqlPet
from app.models.ingredient import IngredientModel
from app.models.feed_inventory import FeedInventory
from app.models.pet import Pet
from app.services import evolution_service
from datetime import datetime, date

recipe_bp = Blueprint('recipe', __name__, url_prefix='/recipes')


def is_expiring_soon(expiry_date_str):
    """判斷食材是否在 3 天內過期"""
    if not expiry_date_str:
        return False
    try:
        # 轉為 date 物件比對
        expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
        today = date.today()
        days_left = (expiry_date - today).days
        return 0 <= days_left <= 3
    except Exception:
        return False


@recipe_bp.route('/recommend', methods=['GET'])
@login_required
def recommend():
    """
    智慧食譜推薦系統 (F-02)
    - 取得使用者偏好與過敏原
    - 比對冰箱現有食材
    - 惜食優先排序 (即將過期食材加權)
    - 回傳符合設定的食譜列表
    """
    # 1. 取得使用者偏好設定
    pref = UserPreference.query.filter_by(user_id=current_user.id).first()
    if not pref:
        pref = UserPreference(user_id=current_user.id)
        db.session.add(pref)
        db.session.commit()

    # 2. 取得使用者過敏原
    allergens = [a.allergen_name for a in current_user.allergens]

    # 3. 取得我的材料庫食材
    pantry_items = IngredientModel.get_all(current_user.id)
    pantry_dict = {item['name'].strip(): item for item in pantry_items}

    # 4. 取得所有食譜並進行篩選與匹配
    all_recipes = Recipe.query.all()
    recommended_list = []

    for recipe in all_recipes:
        # A. 飲食類型過濾
        # 食譜標籤包含飲食類型，如 "omnivore, vegetarian, vegan"
        recipe_tags = [t.strip() for t in recipe.tags.split(',') if t.strip()]
        if pref.diet_type == 'vegan' and 'vegan' not in recipe_tags:
            continue
        if pref.diet_type == 'vegetarian' and 'vegetarian' not in recipe_tags and 'vegan' not in recipe_tags:
            continue
        if pref.diet_type == 'seafood' and 'seafood' not in recipe_tags and 'vegetarian' not in recipe_tags and 'vegan' not in recipe_tags:
            continue

        # B. 辣度過濾
        if not pref.spicy_ok and 'spicy' in recipe_tags:
            continue

        # C. 烹飪時間過濾
        if recipe.cooking_time and recipe.cooking_time > pref.max_cooking_time:
            continue

        # D. 過敏原過濾
        # 檢查食譜過敏原是否包含使用者過敏原
        recipe_allergens = [a.strip() for a in recipe.allergens.split(',') if a.strip()]
        has_allergen_clash = False
        for user_allergen in allergens:
            if user_allergen in recipe_allergens:
                has_allergen_clash = True
                break
        if has_allergen_clash:
            continue

        # E. 食材匹配度計算
        required_list = [i.strip() for i in recipe.required_ingredients.split(',') if i.strip()]
        if not required_list:
            continue

        matching_ingredients = []
        missing_ingredients = []
        has_expiring_soon_item = False

        for req in required_list:
            if req in pantry_dict:
                item = pantry_dict[req]
                matching_ingredients.append(item)
                # 檢查是否即將過期
                if is_expiring_soon(item.get('expiry_date')):
                    has_expiring_soon_item = True
            else:
                missing_ingredients.append(req)

        match_count = len(matching_ingredients)
        total_count = len(required_list)
        match_percentage = round((match_count / total_count) * 100)

        # F. 惜食推薦引擎加權評分
        # 基本分等於匹配百分比，如果包含即將過期食材則加 20 分加權分，促使用戶優先消耗即將過期食材
        sorting_score = match_percentage
        if has_expiring_soon_item:
            sorting_score += 20

        recommended_list.append({
            'recipe': recipe,
            'match_percentage': match_percentage,
            'matching_ingredients': matching_ingredients,
            'missing_ingredients': missing_ingredients,
            'sorting_score': sorting_score,
            'has_expiring': has_expiring_soon_item
        })

    # 5. 依據評分進行排序 (高分在前)
    recommended_list.sort(key=lambda x: x['sorting_score'], reverse=True)

    return render_template(
        'recipes/recommend.html',
        recipes=recommended_list,
        pref=pref
    )


@recipe_bp.route('/<int:recipe_id>', methods=['GET'])
@login_required
def detail(recipe_id):
    """食譜詳細頁面 (F-02)"""
    recipe = Recipe.query.get_or_404(recipe_id)

    # 取得材料庫做比對
    pantry_items = IngredientModel.get_all(current_user.id)
    pantry_dict = {item['name'].strip(): item for item in pantry_items}

    required_list = [i.strip() for i in recipe.required_ingredients.split(',') if i.strip()]
    matching_ingredients = []
    missing_ingredients = []

    for req in required_list:
        if req in pantry_dict:
            matching_ingredients.append(pantry_dict[req])
        else:
            missing_ingredients.append(req)

    # 檢查是否已收藏
    is_favorited = Collection.query.filter_by(user_id=current_user.id, recipe_id=recipe.id).first() is not None

    return render_template(
        'recipes/detail.html',
        recipe=recipe,
        matching_ingredients=matching_ingredients,
        missing_ingredients=missing_ingredients,
        is_favorited=is_favorited
    )


@recipe_bp.route('/favorite/<int:recipe_id>', methods=['POST'])
@login_required
def favorite(recipe_id):
    """切換收藏/取消收藏食譜 (F-05)"""
    fav = Collection.query.filter_by(user_id=current_user.id, recipe_id=recipe_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
        return jsonify({'success': True, 'favorited': False, 'message': '已取消收藏食譜 ⭐'})
    else:
        new_fav = Collection(user_id=current_user.id, recipe_id=recipe_id)
        db.session.add(new_fav)
        db.session.commit()
        return jsonify({'success': True, 'favorited': True, 'message': '已成功收藏食譜 💖'})


@recipe_bp.route('/cook/<int:recipe_id>', methods=['POST'])
@login_required
def cook(recipe_id):
    """
    完成烹飪回報 (與食譜推薦結合)：
    1. 扣除冰箱中的配料數量 (若數量變為 0 則刪除食材)
    2. 使用者烹飪次數 +1
    3. 發放 1 個虛擬飼料給使用者庫存
    4. 寵物 EXP +20 點
    5. 觸發成就檢查與解鎖
    """
    recipe = Recipe.query.get_or_404(recipe_id)
    required_list = [i.strip() for i in recipe.required_ingredients.split(',') if i.strip()]

    # 取得材料庫
    pantry_items = IngredientModel.get_all(current_user.id)
    pantry_dict = {item['name'].strip(): item for item in pantry_items}

    # 扣減食材庫存
    for req in required_list:
        if req in pantry_dict:
            item = pantry_dict[req]
            new_qty = item['quantity'] - 1.0
            if new_qty <= 0:
                # 數量用盡，刪除食材
                IngredientModel.delete(item['id'], current_user.id)
            else:
                # 扣減數量
                IngredientModel.update(item['id'], item['name'], new_qty, item['unit'], item['expiry_date'], current_user.id)

    # 1. 使用者烹飪次數 +1
    current_user.cooking_count += 1
    db.session.commit()

    # 2. 寵物加經驗 +20 EXP 並判定進化 (F-06 服務層)
    # 先取得當前使用者的寵物
    pet_status = SqlPet.query.filter_by(user_id=current_user.id).first()
    pet_updated = None
    if pet_status:
        # 調用 pet 模組的 add_exp，它內部整合了 evolution_service 與 level up / evolution 判定
        from app.models.pet import Pet as RawPet
        pet_updated = RawPet.add_exp(pet_status.id, 20)

    # 3. 發放 1 個虛擬飼料 (F-04)
    inventory = FeedInventory.get_by_user_id(current_user.id)
    if not inventory:
        inventory = FeedInventory.create(current_user.id, count=0)
    inventory.add_feed(1)

    # 4. 檢查成就解鎖
    newly_unlocked = current_user.check_achievements()
    unlocked_achievements = [{
        "name": ach.name,
        "icon": ach.icon,
        "description": ach.description
    } for ach in newly_unlocked]

    # 回傳 JSON 供前端 AJAX 呈現
    return jsonify({
        'success': True,
        'message': f'烹飪完成！扣除食材，並成功發放 1 個飼料！寵物獲得了 20 點 EXP ⭐',
        'remaining_feed': inventory.count,
        'pet': pet_updated,
        'unlocked_achievements': unlocked_achievements
    })
