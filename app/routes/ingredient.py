from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.ingredient import Ingredient

ingredient_bp = Blueprint('ingredient', __name__)

@ingredient_bp.route('/')
def index():
    """
    我的材料庫 (首頁)
    取得所有食材，並渲染食材列表頁面。
    對應模板：ingredients/index.html
    """
    ingredients = Ingredient.get_all()
    return render_template('ingredients/index.html', ingredients=ingredients)

@ingredient_bp.route('/ingredient/add', methods=['POST'])
def add():
    """
    新增食材
    接收表單資料，建立新紀錄後，重導向回首頁。
    """
    name = request.form.get('name')
    quantity = request.form.get('quantity')
    unit = request.form.get('unit')
    expiry_date = request.form.get('expiry_date')

    # 基本輸入驗證
    if not name or not quantity:
        flash('食材名稱與數量為必填欄位！', 'error')
        return redirect(url_for('ingredient.index'))

    try:
        quantity = float(quantity)
    except ValueError:
        flash('數量必須是數字！', 'error')
        return redirect(url_for('ingredient.index'))

    result_id = Ingredient.create(name, quantity, unit, expiry_date)
    if result_id:
        flash('食材新增成功！', 'success')
    else:
        flash('食材新增失敗，請稍後再試。', 'error')
        
    return redirect(url_for('ingredient.index'))

@ingredient_bp.route('/ingredient/edit/<int:id>')
def edit(id):
    """
    編輯食材頁面
    取得單一食材資料，渲染編輯表單。
    對應模板：ingredients/edit.html
    """
    ingredient = Ingredient.get_by_id(id)
    if not ingredient:
        flash('找不到該食材！', 'error')
        return redirect(url_for('ingredient.index'))
        
    return render_template('ingredients/edit.html', ingredient=ingredient)

@ingredient_bp.route('/ingredient/update/<int:id>', methods=['POST'])
def update(id):
    """
    更新食材
    接收編輯表單的資料，更新資料庫後，重導向回首頁。
    """
    name = request.form.get('name')
    quantity = request.form.get('quantity')
    unit = request.form.get('unit')
    expiry_date = request.form.get('expiry_date')

    # 基本輸入驗證
    if not name or not quantity:
        flash('食材名稱與數量為必填欄位！', 'error')
        return redirect(url_for('ingredient.edit', id=id))

    try:
        quantity = float(quantity)
    except ValueError:
        flash('數量必須是數字！', 'error')
        return redirect(url_for('ingredient.edit', id=id))

    success = Ingredient.update(id, name, quantity, unit, expiry_date)
    if success:
        flash('食材更新成功！', 'success')
    else:
        flash('食材更新失敗，請稍後再試。', 'error')

    return redirect(url_for('ingredient.index'))

@ingredient_bp.route('/ingredient/delete/<int:id>', methods=['POST'])
def delete(id):
    """
    刪除食材
    刪除指定 ID 的食材，完成後重導向回首頁。
    """
    success = Ingredient.delete(id)
    if success:
        flash('食材已刪除！', 'success')
    else:
        flash('刪除失敗，請稍後再試。', 'error')
        
    return redirect(url_for('ingredient.index'))
