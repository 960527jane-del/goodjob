from flask import render_template, request, redirect, url_for
from . import ingredient_bp

@ingredient_bp.route('/')
def list_ingredients():
    """
    [GET] 顯示所有材料庫內的食材
    對應模板: ingredient/list.html
    呼叫 Model: IngredientModel.get_all()
    """
    pass

@ingredient_bp.route('/new')
def new_ingredient():
    """
    [GET] 顯示新增食材的表單頁面
    對應模板: ingredient/new.html
    """
    pass

@ingredient_bp.route('/', methods=['POST'])
def create_ingredient():
    """
    [POST] 接收表單資料，建立新食材並存入資料庫
    成功後重導向至 /ingredients
    呼叫 Model: IngredientModel.create(...)
    """
    pass

@ingredient_bp.route('/<int:id>/edit')
def edit_ingredient(id):
    """
    [GET] 顯示編輯特定食材的表單頁面
    對應模板: ingredient/edit.html
    呼叫 Model: IngredientModel.get_by_id(id)
    """
    pass

@ingredient_bp.route('/<int:id>/update', methods=['POST'])
def update_ingredient(id):
    """
    [POST] 接收表單資料，更新特定食材資訊
    成功後重導向至 /ingredients
    呼叫 Model: IngredientModel.update(...)
    """
    pass

@ingredient_bp.route('/<int:id>/delete', methods=['POST'])
def delete_ingredient(id):
    """
    [POST] 刪除特定食材
    成功後重導向至 /ingredients
    呼叫 Model: IngredientModel.delete(id)
    """
    pass
