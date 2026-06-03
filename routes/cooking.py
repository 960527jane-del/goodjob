from flask import Blueprint, request, jsonify, redirect, url_for

cooking_bp = Blueprint('cooking', __name__, url_prefix='/cooking')

@cooking_bp.route('/report', methods=['POST'])
def report_cooking():
    """回報完成料理並發放虛擬飼料 (F-04, F-05)"""
    # TODO:
    # 1. 建立 CookingHistory 紀錄
    # 2. 處理可能上傳的照片
    # 3. 給予 User 虛擬飼料 (virtual_food += N)
    # 4. db.session.commit()
    return jsonify({"success": True, "message": "回報成功，獲得虛擬飼料！"})
