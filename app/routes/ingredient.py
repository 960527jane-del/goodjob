from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.ingredient import IngredientModel

# 建立 Blueprint
ingredient_bp = Blueprint('ingredient', __name__, url_prefix='/ingredients')

@ingredient_bp.route('/')
def list_ingredients():
    """
    [GET] 顯示所有材料庫內的食材
    對應模板: ingredient/list.html
    呼叫 Model: IngredientModel.get_all()
    """
    ingredients = IngredientModel.get_all()
    return render_template('ingredient/list.html', ingredients=ingredients)

# Register index as an alias endpoint pointing to list_ingredients
ingredient_bp.add_url_rule('/', endpoint='index', view_func=list_ingredients)

@ingredient_bp.route('/new')
def new_ingredient():
    """
    [GET] 顯示新增食材的表單頁面
    對應模板: ingredient/new.html
    """
    return render_template('ingredient/new.html')

@ingredient_bp.route('/', methods=['POST'])
def create_ingredient():
    """
    [POST] 接收表單資料，建立新食材並存入資料庫
    成功後重導向至 /ingredients
    呼叫 Model: IngredientModel.create(...)
    """
    name = request.form.get('name')
    quantity = request.form.get('quantity')
    unit = request.form.get('unit')
    expiry_date = request.form.get('expiry_date')

    # 基本輸入驗證
    if not name or not quantity or not unit:
        flash('「食材名稱」、「數量」與「單位」為必填欄位！', 'error')
        return redirect(url_for('ingredient.new_ingredient'))

    try:
        quantity = float(quantity)
    except ValueError:
        flash('「數量」必須為數字！', 'error')
        return redirect(url_for('ingredient.new_ingredient'))

    # 存入資料庫
    ingredient_id = IngredientModel.create(name, quantity, unit, expiry_date)
    if ingredient_id:
        flash('成功新增食材！', 'success')
    else:
        flash('新增食材失敗，請稍後再試。', 'error')
        
    return redirect(url_for('ingredient.list_ingredients'))

@ingredient_bp.route('/<int:id>/edit')
def edit_ingredient(id):
    """
    [GET] 顯示編輯特定食材的表單頁面
    對應模板: ingredient/edit.html
    呼叫 Model: IngredientModel.get_by_id(id)
    """
    ingredient = IngredientModel.get_by_id(id)
    if not ingredient:
        flash('找不到該食材！', 'error')
        return redirect(url_for('ingredient.list_ingredients'))
        
    return render_template('ingredient/edit.html', ingredient=ingredient)

@ingredient_bp.route('/<int:id>/update', methods=['POST'])
def update_ingredient(id):
    """
    [POST] 接收表單資料，更新特定食材資訊
    成功後重導向至 /ingredients
    呼叫 Model: IngredientModel.update(...)
    """
    name = request.form.get('name')
    quantity = request.form.get('quantity')
    unit = request.form.get('unit')
    expiry_date = request.form.get('expiry_date')

    if not name or not quantity or not unit:
        flash('「食材名稱」、「數量」與「單位」為必填欄位！', 'error')
        return redirect(url_for('ingredient.edit_ingredient', id=id))

    try:
        quantity = float(quantity)
    except ValueError:
        flash('「數量」必須為數字！', 'error')
        return redirect(url_for('ingredient.edit_ingredient', id=id))

    success = IngredientModel.update(id, name, quantity, unit, expiry_date)
    if success:
        flash('食材更新成功！', 'success')
    else:
        flash('更新食材失敗，請稍後再試。', 'error')
        
    return redirect(url_for('ingredient.list_ingredients'))

@ingredient_bp.route('/<int:id>/delete', methods=['POST'])
def delete_ingredient(id):
    """
    [POST] 刪除特定食材
    成功後重導向至 /ingredients
    呼叫 Model: IngredientModel.delete(id)
    """
    success = IngredientModel.delete(id)
    if success:
        flash('食材已刪除！', 'success')
    else:
        flash('刪除食材失敗，請稍後再試。', 'error')
        
    return redirect(url_for('ingredient.list_ingredients'))
