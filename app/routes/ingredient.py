from flask import Blueprint, render_template, request, redirect, url_for, flash

ingredient_bp = Blueprint('ingredient', __name__)

@ingredient_bp.route('/')
def index():
    """
    我的材料庫 (首頁)
    取得所有食材，並渲染食材列表頁面。
    對應模板：ingredients/index.html
    """
    pass

@ingredient_bp.route('/ingredient/add', methods=['POST'])
def add():
    """
    新增食材
    接收表單資料，建立新紀錄後，重導向回首頁。
    """
    pass

@ingredient_bp.route('/ingredient/edit/<int:id>')
def edit(id):
    """
    編輯食材頁面
    取得單一食材資料，渲染編輯表單。
    對應模板：ingredients/edit.html
    """
    pass

@ingredient_bp.route('/ingredient/update/<int:id>', methods=['POST'])
def update(id):
    """
    更新食材
    接收編輯表單的資料，更新資料庫後，重導向回首頁。
    """
    pass

@ingredient_bp.route('/ingredient/delete/<int:id>', methods=['POST'])
def delete(id):
    """
    刪除食材
    刪除指定 ID 的食材，完成後重導向回首頁。
    """
    pass
