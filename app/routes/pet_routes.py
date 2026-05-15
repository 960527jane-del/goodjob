from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from app.models.pet import Pet

# 建立寵物功能的 Blueprint
pet_bp = Blueprint('pet', __name__)

# 測試用：因為尚未實作登入系統，預設使用 ID 為 1 的測試使用者
CURRENT_USER_ID = 1

@pet_bp.route('/pet', methods=['GET'])
def index():
    """
    寵物專屬首頁
    - 輸入：無 (從 session 獲取 user_id，目前寫死為 1)
    - 邏輯：查詢資料庫中該使用者的寵物資料
    - 輸出：渲染 templates/pet/index.html，將資料帶入模板
    """
    pet = Pet.get_by_user_id(CURRENT_USER_ID)
    
    # 防呆機制：如果這個使用者還沒有寵物，自動幫他建立一隻，確保畫面能正常顯示
    if not pet:
        Pet.create(CURRENT_USER_ID, "貪吃小雞")
        pet = Pet.get_by_user_id(CURRENT_USER_ID)
        flash("歡迎！我們已經為你準備了一隻可愛的虛擬寵物！", "success")

    return render_template('pet/index.html', pet=pet)

@pet_bp.route('/api/pet/feed', methods=['POST'])
def feed():
    """
    餵食寵物 API
    - 輸入：JSON 格式 (可選，包含 exp_gained 欄位)
    - 邏輯：呼叫 Pet.feed 增加經驗值，若滿 100 則升級
    - 輸出：回傳 JSON 結果
    """
    # 嘗試從前端取得 JSON 資料，若無則預設每次餵食給予 25 EXP
    data = request.get_json() or {}
    exp_gained = data.get('exp_gained', 25)
    
    updated_pet, is_level_up = Pet.feed(CURRENT_USER_ID, exp_gained)
    
    if not updated_pet:
        return jsonify({"success": False, "error": "找不到該使用者的寵物資料"}), 404
        
    return jsonify({
        "success": True,
        "pet": updated_pet,
        "is_level_up": is_level_up
    }), 200

@pet_bp.route('/api/pet/status', methods=['GET'])
def status():
    """
    取得寵物狀態 API
    - 輸入：無
    - 邏輯：查詢該使用者的寵物最新狀態
    - 輸出：回傳 JSON 結果
    """
    pet = Pet.get_by_user_id(CURRENT_USER_ID)
    
    if not pet:
        return jsonify({"success": False, "error": "找不到該使用者的寵物資料"}), 404
        
    return jsonify({
        "success": True,
        "pet": pet
    }), 200
