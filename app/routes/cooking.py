from flask import Blueprint, render_template, request, redirect, url_for, flash

cooking_bp = Blueprint('cooking', __name__, url_prefix='/cooking')

@cooking_bp.route('/', methods=['GET'])
def report_page():
    """
    顯示烹飪回報表單頁面
    
    輸入: 無
    處理邏輯: 檢查使用者狀態。
    輸出: 渲染 templates/cooking/index.html
    """
    pass

@cooking_bp.route('/report', methods=['POST'])
def submit_report():
    """
    處理送出烹飪紀錄的表單
    
    輸入: POST 帶上 'image' 檔案 或 完成狀態
    處理邏輯:
        1. 驗證並儲存上傳的檔案到 static/uploads/
        2. 建立 CookingRecord
        3. 透過 FeedInventory.add_feed() 增加飼料
    輸出: 重導向到 /pet 頁面，並帶有成功 flash 訊息
    """
    pass
