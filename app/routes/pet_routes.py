from flask import Blueprint, render_template, request, jsonify

# 建立寵物功能的 Blueprint
pet_bp = Blueprint('pet', __name__)

@pet_bp.route('/pet', methods=['GET'])
def index():
    """
    寵物專屬首頁
    - 輸入：無 (可從 session 獲取 user_id)
    - 邏輯：查詢資料庫中該使用者的寵物資料
    - 輸出：渲染 templates/pet/index.html，將資料帶入模板
    """
    pass

@pet_bp.route('/api/pet/feed', methods=['POST'])
def feed():
    """
    餵食寵物 API
    - 輸入：JSON 或 POST data (可選，例如指定增加的經驗值)
    - 邏輯：呼叫 Pet.feed 增加經驗值，若達標則升級
    - 輸出：回傳 JSON 結果 (包含新經驗值、等級與是否升級)
    """
    pass

@pet_bp.route('/api/pet/status', methods=['GET'])
def status():
    """
    取得寵物狀態 API
    - 輸入：無
    - 邏輯：查詢該使用者的寵物最新狀態
    - 輸出：回傳 JSON 結果
    """
    pass
