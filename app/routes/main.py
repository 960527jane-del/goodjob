from flask import Blueprint, redirect, url_for, render_template, request, flash

main_bp = Blueprint('main', __name__)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    簡化登入頁面 (臨時實現)
    """
    if request.method == 'POST':
        # 預設使用 user_id=1
        flash('登入成功！', 'success')
        return redirect(url_for('pet.pet_index'))
    return render_template('login.html')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    簡化註冊頁面 (臨時實現)
    """
    if request.method == 'POST':
        flash('註冊成功！', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@main_bp.route('/logout', methods=['GET'])
def logout():
    """
    簡化登出 (臨時實現)
    """
    flash('已登出！', 'info')
    return redirect(url_for('index'))
