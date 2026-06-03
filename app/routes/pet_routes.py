from flask import Blueprint, render_template, jsonify, request
from app.models.pet import Pet
from app.models.feed_inventory import FeedInventory

# 建立 Blueprint
pet_bp = Blueprint('pet', __name__, url_prefix='/pet')

@pet_bp.route('/', methods=['GET'])
def pet_index():
    """
    顯示寵物專屬頁面
    
    - 取得預設使用者的寵物資料 (MVP hardcode user_id=1)
    - 若寵物不存在則自動建立一隻
    - 取得或建立使用者的飼料庫存 (F-04 整合)
    - 將寵物與庫存資料傳入 templates/pet/index.html 進行渲染
    """
    # MVP 階段預設使用 user_id = 1
    user_id = 1
    
    try:
        # 嘗試取得寵物
        pet = Pet.get_by_user_id(user_id)
        
        # 若無寵物，則建立預設寵物
        if not pet:
            Pet.create(user_id, "我的預設寵物")
            pet = Pet.get_by_user_id(user_id)
            
        # 取得或建立飼料庫存 (F-04 整合)
        inventory = FeedInventory.get_by_user_id(user_id)
        if not inventory:
            inventory = FeedInventory.create(user_id, count=0)
            
        return render_template('pet/index.html', pet=pet, inventory=inventory)
    except Exception as e:
        return f"發生錯誤: {str(e)}", 500

@pet_bp.route('/feed', methods=['POST'])
def feed_pet():
    """
    處理手動餵食請求
    
    - 取得預設使用者的寵物 (MVP hardcode user_id=1)
    - 檢查並扣除 1 個飼料庫存 (F-04 整合)
    - 呼叫 Pet.add_exp 增加經驗值並處理升級與進化
    - 回傳 JSON 格式的最新寵物狀態與剩餘飼料數
    """
    # MVP 階段預設使用 user_id = 1
    user_id = 1
    
    try:
        pet = Pet.get_by_user_id(user_id)
        if not pet:
            return jsonify({"success": False, "message": "找不到寵物，請先進入寵物頁面建立"}), 404
            
        # 檢查與扣除飼料庫存 (F-04 整合)
        inventory = FeedInventory.get_by_user_id(user_id)
        if not inventory:
            inventory = FeedInventory.create(user_id, count=0)
            
        if inventory.count < 1:
            return jsonify({"success": False, "message": "飼料不足，快去烹飪回報獲得飼料吧！"}), 400
            
        if not inventory.consume_feed(1):
            return jsonify({"success": False, "message": "扣除飼料失敗，請重試"}), 500
            
        # 增加 20 經驗值並觸發升級/進化邏輯
        updated_pet = Pet.add_exp(pet['id'], 20)
        
        return jsonify({
            "success": True,
            "pet": updated_pet,
            "remaining_feed": inventory.count
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
