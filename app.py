import os
from flask import render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sql_models import db, User, UserPreference, UserAllergen, Achievement, UserAchievement
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


# ─── 可用的過敏原與飲食類型選項 ───
ALLERGEN_OPTIONS = ['花生', '牛奶', '蛋', '麩質', '海鮮', '堅果', '大豆']
DIET_TYPE_OPTIONS = {
    'omnivore': '葷食（不限制）',
    'vegetarian': '素食（蛋奶素）',
    'vegan': '全素（純植物）',
    'pescatarian': '海鮮素'
}
COOKING_LEVEL_OPTIONS = {
    'beginner': '新手入門',
    'intermediate': '有點基礎',
    'advanced': '廚房老手'
}

def init_db():
    with app.app_context():
        db.create_all()

        # 如果沒有成就，建立預設成就
        if not Achievement.query.first():
            achievements = [
                Achievement(name="初次踏入廚房", description="解鎖 1 個進化圖鑑", icon="🎓", condition_type="collect", condition_value=1),
                Achievement(name="圖鑑收集狂", description="解鎖 5 個進化圖鑑", icon="📚", condition_type="collect", condition_value=5),
                Achievement(name="開火啦！", description="完成第 1 次烹飪", icon="🔥", condition_type="cook", condition_value=1),
                Achievement(name="連續開伙小天才", description="完成 5 次烹飪", icon="🍳", condition_type="cook", condition_value=5),
                Achievement(name="清冰箱大師", description="完成 10 次烹飪", icon="❄️", condition_type="cook", condition_value=10)
            ]
            db.session.bulk_save_objects(achievements)
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

        # 建立使用者
        user = User(
            email=email,
            username=username,
            display_name=display_name or username
        )
        user.set_password(password)
        db.session.add(user)

        # 建立預設偏好
        pref = UserPreference(user=user)
        db.session.add(pref)

        db.session.commit()

        login_user(user)
        flash(f'歡迎加入隨「食」隨地，{user.display_name}！🎉 請先設定你的飲食偏好', 'success')
        return redirect(url_for('preferences'))

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
            flash(f'歡迎回來，{user.display_name}！🍳', 'success')
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


# ════════════════════════════════════════
#  偏好設定路由
# ════════════════════════════════════════

@app.route('/preferences', methods=['GET', 'POST'])
@login_required
def preferences():
    user = current_user
    pref = user.preference

    # 確保有偏好記錄
    if not pref:
        pref = UserPreference(user_id=user.id)
        db.session.add(pref)
        db.session.commit()

    if request.method == 'POST':
        pref.diet_type = request.form.get('diet_type', 'omnivore')
        pref.spicy_ok = request.form.get('spicy_ok') == 'on'
        pref.cooking_level = request.form.get('cooking_level', 'beginner')
        max_time = request.form.get('max_cooking_time', '60')
        try:
            pref.max_cooking_time = int(max_time)
        except ValueError:
            pref.max_cooking_time = 60

        # 更新過敏原
        UserAllergen.query.filter_by(user_id=user.id).delete()
        selected_allergens = request.form.getlist('allergens')
        for allergen_name in selected_allergens:
            if allergen_name in ALLERGEN_OPTIONS:
                ua = UserAllergen(user_id=user.id, allergen_name=allergen_name)
                db.session.add(ua)

        db.session.commit()
        flash('偏好設定已儲存！食譜推薦會根據你的偏好調整 ✨', 'success')
        return redirect(url_for('preferences'))

    user_allergens = [a.allergen_name for a in user.allergens]
    return render_template('preferences.html',
                           pref=pref,
                           user_allergens=user_allergens,
                           allergen_options=ALLERGEN_OPTIONS,
                           diet_type_options=DIET_TYPE_OPTIONS,
                           cooking_level_options=COOKING_LEVEL_OPTIONS)


# ════════════════════════════════════════
#  主頁面與收藏、烹飪路由
# ════════════════════════════════════════


@app.route('/profile')
@login_required
def profile():
    user = current_user
    all_achievements = Achievement.query.all()

    unlocked_ids = [ua.achievement_id for ua in user.achievements]

    achievements_status = []
    for ach in all_achievements:
        achievements_status.append({
            'achievement': ach,
            'unlocked': ach.id in unlocked_ids
        })

    return render_template('profile.html', user=user, achievements_status=achievements_status)



if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
