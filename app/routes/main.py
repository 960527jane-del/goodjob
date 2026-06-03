from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def index():
    """
    處理首頁請求
    
    輸入: 無
    處理邏輯: 處理基本顯示，檢查狀態。
    輸出: 渲染 templates/index.html
    """
    return render_template('index.html')
