from flask import render_template, request, redirect, url_for, flash
from . import ingredient_bp
from app.models.ingredient import Ingredient

@ingredient_bp.route('/')
def list_ingredients():
    """
    [GET] 顯示所有材料庫內的食材
    對應模板: ingredient/list.html
    """
    user_id = 1 # MVP assumed user
    ingredients = Ingredient.get_by_user_id(user_id)
    return render_template('ingredient/list.html', ingredients=ingredients)

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
    """
    user_id = 1
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
        
    if expiry_date:
        from datetime import datetime
        try:
            expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date()
        except:
            expiry_date = None
    else:
        expiry_date = None

    # 存入資料庫
    ingredient = Ingredient.create(user_id, name, quantity, unit, expiry_date)
    if ingredient:
        flash('成功新增食材！', 'success')
    else:
        flash('新增食材失敗，請稍後再試。', 'error')
        
    return redirect(url_for('ingredient.list_ingredients'))

@ingredient_bp.route('/<int:id>/edit')
def edit_ingredient(id):
    """
    [GET] 顯示編輯特定食材的表單頁面
    """
    ingredient = Ingredient.get_by_id(id)
    if not ingredient:
        flash('找不到該食材！', 'error')
        return redirect(url_for('ingredient.list_ingredients'))
        
    return render_template('ingredient/edit.html', ingredient=ingredient)

@ingredient_bp.route('/<int:id>/update', methods=['POST'])
def update_ingredient(id):
    """
    [POST] 接收表單資料，更新特定食材資訊
    """
    ingredient = Ingredient.get_by_id(id)
    if not ingredient:
        flash('找不到該食材！', 'error')
        return redirect(url_for('ingredient.list_ingredients'))

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

    if expiry_date:
        from datetime import datetime
        try:
            expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date()
        except:
            expiry_date = None
    else:
        expiry_date = None

    success = ingredient.update(name=name, quantity=quantity, unit=unit, expiry_date=expiry_date)
    if success:
        flash('食材更新成功！', 'success')
    else:
        flash('更新食材失敗，請稍後再試。', 'error')
        
    return redirect(url_for('ingredient.list_ingredients'))

@ingredient_bp.route('/<int:id>/delete', methods=['POST'])
def delete_ingredient(id):
    """
    [POST] 刪除特定食材
    """
    ingredient = Ingredient.get_by_id(id)
    if ingredient:
        success = ingredient.delete()
        if success:
            flash('食材已刪除！', 'success')
        else:
            flash('刪除食材失敗，請稍後再試。', 'error')
    else:
        flash('找不到該食材！', 'error')
        
    return redirect(url_for('ingredient.list_ingredients'))
