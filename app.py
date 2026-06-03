import os
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sql_models import db, User, Pet
from app import create_app

app = create_app()

def init_db():
    with app.app_context():
        db.create_all()
        
        # 確保有預設使用者 (ID=1)
        user = db.session.get(User, 1)
        if not user:
            default_user = User(id=1, username='default_user', email='user@example.com')
            default_user.set_password('1234')
            db.session.add(default_user)
            db.session.commit()
            
            # 為預設使用者建立一隻寵物
            default_pet = Pet(user_id=1, name='小食怪', hunger=100, growth=0)
            db.session.add(default_pet)
            db.session.commit()

# ════════════════════════════════════════
#  認證路由：註冊 / 登入 / 登出
# ════════════════════════════════════════

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        username = request.form.get('username', '').strip()
        display_name = request.form.get('display_name', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')

        # 驗證
        errors = []
        if not email:
            errors.append('請輸入 Email')
        if not username:
            errors.append('請輸入帳號名稱')
        if not password:
            errors.append('請輸入密碼')
        if len(password) < 4:
            errors.append('密碼至少 4 個字元')
        if password != password_confirm:
            errors.append('兩次密碼不一致')
        if User.query.filter_by(email=email).first():
            errors.append('此 Email 已被註冊')
        if User.query.filter_by(username=username).first():
            errors.append('此帳號名稱已被使用')

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('register.html', email=email, username=username, display_name=display_name)

        # 建立使用者與其寵物
        user = User(
            email=email,
            username=username,
            display_name=display_name or username
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush() # 取得 user.id

        pet = Pet(user_id=user.id, name="小寶貝", hunger=100, growth=0)
        db.session.add(pet)
        db.session.commit()

        login_user(user)
        flash(f'註冊成功！歡迎，{user.display_name}！🎉', 'success')
        return redirect(url_for('index'))

    return render_template('register.html')
