from flask import Blueprint, render_template, request, jsonify

pet_bp = Blueprint('pet', __name__, url_prefix='/pet')

@pet_bp.route('/', methods=['GET'])
def pet_page():
    """
    顯示虛擬寵物狀態頁面
    
    輸入: 無
    處理邏輯: 查詢該使用者的 Pet 與 FeedInventory 資料。
    輸出: 渲染 templates/pet/index.html，並帶入寵物與庫存資訊
    """
    pass

@pet_bp.route('/feed', methods=['POST'])
def feed_pet():
    """
    處理餵食寵物的 AJAX 請求
    
    輸入: 無 (POST request)
    處理邏輯:
        1. 檢查 FeedInventory 數量是否大於等於 1
        2. 扣除 1 個飼料
        3. 增加 Pet 經驗值並檢查是否升級
    輸出: JSON 格式包含 success, new_exp, new_level, remaining_feed
    錯誤處理: 若飼料不足回傳 400 及錯誤 JSON
    """
    pass
