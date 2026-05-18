import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from app.models.cooking_record import CookingRecord
from app.models.feed_inventory import FeedInventory

cooking_bp = Blueprint('cooking', __name__, url_prefix='/cooking')

# 允許的圖片副檔名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@cooking_bp.route('/', methods=['GET'])
def report_page():
    """
    顯示烹飪回報表單頁面
    """
    return render_template('cooking/index.html')

@cooking_bp.route('/report', methods=['POST'])
def submit_report():
    """
    處理送出烹飪紀錄的表單
    """
    # 假設 MVP 開發階段，固定 user_id = 1
    user_id = 1
    
    # 取得圖片或狀態
    file = request.files.get('image')
    is_completed = request.form.get('completed')
    
    if not file and not is_completed:
        flash("請上傳圖片或勾選完成狀態！", "danger")
        return redirect(url_for('cooking.report_page'))
        
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
            flash("不支援的檔案格式！", "danger")
            return redirect(url_for('cooking.report_page'))
            
    # 新增烹飪紀錄
    record = CookingRecord.create(user_id=user_id, image_path=image_path, status='completed')
    if not record:
        flash("紀錄儲存失敗，請稍後再試。", "danger")
        return redirect(url_for('cooking.report_page'))
        
    # 增加飼料
    inventory = FeedInventory.get_by_user_id(user_id)
    if not inventory:
        inventory = FeedInventory.create(user_id=user_id, count=0)
        
    if inventory.add_feed(1):
        flash("回報成功！獲得 1 份虛擬飼料！", "success")
    else:
        flash("紀錄已建立，但飼料發放失敗。", "warning")
        
    return redirect(url_for('pet.pet_page'))
