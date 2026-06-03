from flask import Blueprint, request, render_template, redirect, url_for, flash
# from models import db, Ingredient

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')

@inventory_bp.route('/', methods=['GET'])
def list_inventory():
    """取得使用者的食材列表 (F-01, F-03)"""
    # TODO: 查詢資料庫，並傳遞過期狀態給前端
    return render_template('inventory.html')

@inventory_bp.route('/add', methods=['POST'])
def add_ingredient():
    """手動新增食材 (F-01)"""
    # TODO: 解析 request.form，新增 Ingredient，寫入 DB
    return redirect(url_for('inventory.list_inventory'))

@inventory_bp.route('/update/<int:id>', methods=['POST'])
def update_ingredient(id):
    """修改食材數量或資訊 (F-01)"""
    # TODO: 更新資料庫中的該筆食材
    return redirect(url_for('inventory.list_inventory'))

@inventory_bp.route('/delete/<int:id>', methods=['POST'])
def delete_ingredient(id):
    """刪除特定食材 (F-01)"""
    # TODO: 刪除資料庫中的該筆食材
    return redirect(url_for('inventory.list_inventory'))
