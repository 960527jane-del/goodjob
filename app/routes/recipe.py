from flask import render_template, request
from . import recipe_bp

@recipe_bp.route('/')
def list_recipes():
    """
    [GET] 讀取使用者庫存食材，向外部 API 請求並顯示推薦食譜清單
    對應模板: recipe/list.html
    """
    pass

@recipe_bp.route('/<int:id>')
def recipe_detail(id):
    """
    [GET] 根據食譜 ID 向外部 API 請求詳細步驟與配料，並與現有庫存比對
    對應模板: recipe/detail.html
    """
    pass
