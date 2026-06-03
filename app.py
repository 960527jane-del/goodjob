import os
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sql_models import db, User, Pet
from app import create_app

app = create_app()

# ─── Flask-Login 初始化 ───
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = '請先登入才能使用此功能 🔒'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


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
#  首頁儀表板 (寵物養成系統)
# ════════════════════════════════════════

@app.route('/')
@login_required
def index():
    user = current_user
    pet = Pet.query.filter_by(user_id=user.id).first()
    if not pet:
        # 如果使用者沒有寵物，自動建立一隻
        pet = Pet(user_id=user.id, name="小寶貝", hunger=100, growth=0)
        db.session.add(pet)
        db.session.commit()
    return render_template('pet_dashboard.html', pet=pet)


# ════════════════════════════════════════
#  餵食 API
# ════════════════════════════════════════

@app.route('/feed', methods=['POST'])
@login_required
def feed():
    user = current_user
    pet = Pet.query.filter_by(user_id=user.id).first()
    if not pet:
        return jsonify({"success": False, "message": "找不到寵物 😢"}), 404
        
    if pet.hunger <= 0:
        return jsonify({"success": False, "message": "寵物已經吃得太飽了，不需要再餵食了 💖"}), 400
        
    # 餵食減少飢餓度 (hunger)，增加成長值 (growth)
    pet.hunger = max(0, pet.hunger - 10)
    pet.growth += 10
    db.session.commit()
    
    return jsonify({
        "success": True,
        "hunger": pet.hunger,
        "growth": pet.growth,
        "message": "餵食成功！成長值 +10，飢餓度 -10 ✨"
    })


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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=bool(remember))
            flash(f'歡迎回來，{user.display_name}！👋', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Email 或密碼錯誤，請重試', 'danger')
            return render_template('login.html', email=email)

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已成功登出，下次見！👋', 'info')
    return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
