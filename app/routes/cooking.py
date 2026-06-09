import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models.cooking_record import CookingRecord
from app.models.feed_inventory import FeedInventory
from sql_models import db, User

cooking_bp = Blueprint('cooking', __name__, url_prefix='/cooking')

# 允許的圖片副檔名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@cooking_bp.route('/', methods=['GET'])
@login_required
def report_page():
    """
    顯示烹飪回報表單頁面
    """
    recipe_id = request.args.get('recipe_id')
    recipe = None
    if recipe_id:
        from sql_models import Recipe
        recipe = Recipe.query.get(recipe_id)
    return render_template('cooking/index.html', recipe=recipe)


@cooking_bp.route('/report', methods=['POST'])
@login_required
def submit_report():
    """
    處理送出烹飪紀錄的表單
    """
    user_id = current_user.id
    recipe_id = request.form.get('recipe_id')
    
    # 取得圖片或狀態
    file = request.files.get('image')
    is_completed = request.form.get('completed')
    
    if not file and not is_completed:
        flash("請上傳圖片或勾選完成狀態！", "error")
        return redirect(url_for('cooking.report_page', recipe_id=recipe_id))
        
    image_path = None
    if file and file.filename != '':
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # 確保有 uploads 資料夾
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            # 儲存相對路徑以便前端讀取
            image_path = f"uploads/{filename}"
        else:
            flash("不支援的檔案格式！", "error")
            return redirect(url_for('cooking.report_page', recipe_id=recipe_id))
            
    # 1. 如果有指定食譜，自動扣除材料庫中的所需配料
    if recipe_id:
        from sql_models import Recipe
        recipe = Recipe.query.get(recipe_id)
        if recipe:
            required_list = [i.strip() for i in recipe.required_ingredients.split(',') if i.strip()]
            from app.models.ingredient import IngredientModel
            pantry_items = IngredientModel.get_all(user_id)
            pantry_dict = {item['name'].strip(): item for item in pantry_items}
            
            for req in required_list:
                if req in pantry_dict:
                    item = pantry_dict[req]
                    new_qty = item['quantity'] - 1.0
                    if new_qty <= 0:
                        # 數量用盡，刪除食材
                        IngredientModel.delete(item['id'], user_id)
                    else:
                        # 扣減數量
                        IngredientModel.update(item['id'], item['name'], new_qty, item['unit'], item['expiry_date'], user_id)

    # 新增烹飪紀錄
    record = CookingRecord.create(user_id=user_id, image_path=image_path, status='completed')
    if not record:
        flash("紀錄儲存失敗，請稍後再試。", "error")
        return redirect(url_for('cooking.report_page', recipe_id=recipe_id))
        
    # 2. 更新使用者烹飪次數
    user = db.session.get(User, user_id)
    if user:
        user.cooking_count += 1
        db.session.commit()
        
    # 3. 寵物加經驗 +20 EXP 並判定升級與進化
    from sql_models import Pet as SqlPet
    pet_status = SqlPet.query.filter_by(user_id=user_id).first()
    if pet_status:
        from app.models.pet import Pet as RawPet
        pet_updated = RawPet.add_exp(pet_status.id, 20)
        if pet_updated and pet_updated.get('is_level_up'):
            flash(f"🎉 寵物升級了！目前等級：{pet_updated['level']}！", "success")
        if pet_updated and pet_updated.get('evolution'):
            flash(f"✨ 寵物進化成了 {pet_updated['evolution']}！", "success")
            
    # 4. 檢查是否有解鎖成就
    if user:
        newly_unlocked = user.check_achievements()
        for ach in newly_unlocked:
            flash(f'🏆 解鎖新成就：{ach.name} {ach.icon}！ ({ach.description})', 'success')
        
    # 5. 增加 1 個飼料庫存
    inventory = FeedInventory.get_by_user_id(user_id)
    if not inventory:
        inventory = FeedInventory.create(user_id=user_id, count=0)
        
    if inventory.add_feed(1):
        flash("烹飪回報成功！獲得 1 份虛擬飼料！ 🥩", "success")
    else:
        flash("紀錄已建立，但飼料發放失敗。", "warning")
        
    return redirect(url_for('pet.pet_index'))
