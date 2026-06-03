from flask import Blueprint, redirect, url_for

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def index():
    """
    將首頁請求重定向至虛擬寵物主頁面
    """
    return redirect(url_for('pet.pet_index'))
