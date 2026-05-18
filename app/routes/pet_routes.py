from flask import Blueprint, render_template, jsonify, request
from app.models.pet import Pet

# 建立 Blueprint
pet_bp = Blueprint('pet', __name__, url_prefix='/pet')

@pet_bp.route('/', methods=['GET'])
def pet_index():
    """
    顯示寵物專屬頁面
    
    - 取得預設使用者的寵物資料 (MVP hardcode user_id=1)
    - 若寵物不存在則自動建立一隻
    - 將寵物資料傳入 templates/pet/index.html 進行渲染
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
            
        return render_template('pet/index.html', pet=pet)
    except Exception as e:
        # 若發生錯誤，可考慮紀錄 log，此處暫時回傳 500
        return f"發生錯誤: {str(e)}", 500

@pet_bp.route('/feed', methods=['POST'])
def feed_pet():
    """
    處理手動餵食請求
    
    - 取得預設使用者的寵物 (MVP hardcode user_id=1)
    - 呼叫 Pet.add_exp 增加經驗值 (假設固定增加 10)
    - 回傳 JSON 格式的最新寵物狀態
    """
    # MVP 階段預設使用 user_id = 1
    user_id = 1
    
    try:
        pet = Pet.get_by_user_id(user_id)
        
        if not pet:
            return jsonify({"success": False, "message": "找不到寵物，請先進入寵物頁面建立"}), 404
            
        # 增加 10 經驗值
        updated_pet = Pet.add_exp(pet['id'], 10)
        
        return jsonify({
            "success": True,
            "pet": updated_pet
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
