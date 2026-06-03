from flask import Blueprint, render_template, request, jsonify
from app.models.pet import Pet
from app.models.feed_inventory import FeedInventory
from app.models.user import User

pet_bp = Blueprint('pet', __name__, url_prefix='/pet')

@pet_bp.route('/', methods=['GET'])
def pet_page():
    """
    顯示虛擬寵物狀態頁面
    """
    # 假設 MVP 開發階段，固定 user_id = 1
    user_id = 1
    user = User.get_by_id(user_id)
    if not user:
        user = User.create(username='demo_user', email='demo@example.com')
        if not user:
            users = User.get_all()
            user = users[0] if users else None
        if user:
            user_id = user.id

    # 取得寵物與庫存
    pet = Pet.get_by_user_id(user_id)
    if not pet:
        # 如果沒有寵物，自動建立一隻預設寵物
        pet = Pet.create(user_id=user_id, name="我的寶貝")
        
    inventory = FeedInventory.get_by_user_id(user_id)
    if not inventory:
        # 如果沒有庫存紀錄，自動建立一筆
        inventory = FeedInventory.create(user_id=user_id, count=0)
        
    return render_template('pet/index.html', pet=pet, inventory=inventory)

@pet_bp.route('/feed', methods=['POST'])
def feed_pet():
    """
    處理餵食寵物的 AJAX 請求
    """
    user_id = 1
    
    inventory = FeedInventory.get_by_user_id(user_id)
    if not inventory or inventory.count < 1:
        return jsonify({"success": False, "error": "飼料不足，快去煮飯吧！"}), 400
        
    pet = Pet.get_by_user_id(user_id)
    if not pet:
        return jsonify({"success": False, "error": "找不到您的寵物！"}), 404
        
    # 扣除飼料
    if inventory.consume_feed(1):
        # 增加經驗值 (假設每次餵食固定增加 20 EXP)
        old_level = pet.level
        if pet.add_exp(20):
            level_up = pet.level > old_level
            return jsonify({
                "success": True,
                "new_exp": pet.exp,
                "new_level": pet.level,
                "level_up": level_up,
                "remaining_feed": inventory.count
            })
            
    return jsonify({"success": False, "error": "餵食處理失敗，請稍後再試。"}), 500
