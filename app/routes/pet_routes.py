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
    pass

@pet_bp.route('/feed', methods=['POST'])
def feed_pet():
    """
    處理手動餵食請求
    
    - 取得預設使用者的寵物 (MVP hardcode user_id=1)
    - 呼叫 Pet.add_exp 增加經驗值 (假設固定增加 10)
    - 回傳 JSON 格式的最新寵物狀態
    """
    pass
