from flask import Blueprint, render_template, jsonify

pet_bp = Blueprint('pet', __name__, url_prefix='/pet')

@pet_bp.route('/', methods=['GET'])
def pet_status():
    """取得寵物與飼料庫存狀態頁面 (F-04)"""
    # TODO: 讀取 User 的 pet_level, pet_exp, virtual_food
    return render_template('pet.html')

@pet_bp.route('/feed', methods=['POST'])
def feed_pet():
    """餵食寵物 (扣除飼料、增加經驗) (F-04)"""
    # TODO: 
    # 1. 檢查 virtual_food > 0
    # 2. virtual_food -= 1, pet_exp += N
    # 3. 檢查是否升級，若 pet_exp >= threshold: pet_level += 1
    # 4. db.session.commit()
    return jsonify({
        "success": True,
        "pet_level": 1,
        "pet_exp": 10,
        "virtual_food": 0
    })
