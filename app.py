import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, UserPreference, UserAllergen, Recipe, Collection, Achievement, UserAchievement

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key-cute-app'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

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

# ─── 食譜標籤中英文對照 ───
TAG_DISPLAY = {
    'vegetarian': '🥬 素食',
    'vegan': '🌱 全素',
    'spicy': '🌶️ 辣',
    'quick': '⚡ 快速',
    'seafood': '🐟 海鮮',
    'meat': '🥩 肉類',
    'soup': '🍲 湯品',
    'noodle': '🍜 麵食',
    'rice': '🍚 飯類',
    'egg': '🥚 含蛋',
    'milk': '🥛 含奶',
}


def init_db():
    with app.app_context():
        db.create_all()

        # 如果沒有成就，建立預設成就
        if not Achievement.query.first():
            achievements = [
                Achievement(name="踏出新手村的廚師", description="首次將食譜加入收藏", icon="🎓", condition_type="collect", condition_value=1),
                Achievement(name="食譜收集狂", description="收藏 5 篇食譜", icon="📚", condition_type="collect", condition_value=5),
                Achievement(name="開火啦！", description="完成第 1 道料理", icon="🔥", condition_type="cook", condition_value=1),
                Achievement(name="連續開伙小天才", description="完成 5 道料理", icon="🍳", condition_type="cook", condition_value=5),
                Achievement(name="清冰箱大師", description="完成 10 道料理", icon="❄️", condition_type="cook", condition_value=10)
            ]
            db.session.bulk_save_objects(achievements)

        # 如果沒有食譜，建立範例食譜（含 F-07 標籤與過敏原）
        if not Recipe.query.first():
            recipes = [
                Recipe(
                    title="番茄炒蛋",
                    description="經典家常菜，酸甜下飯。只需番茄和雞蛋即可完成。",
                    image_url="https://images.unsplash.com/photo-1596797038530-2c107229654b?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80",
                    tags="quick,egg,rice",
                    cooking_time=15,
                    difficulty="beginner",
                    allergens="蛋"
                ),
                Recipe(
                    title="蒜香義大利麵",
                    description="只要大蒜、橄欖油和義大利麵就能完成的經典風味。",
                    image_url="https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80",
                    tags="quick,noodle,vegan",
                    cooking_time=20,
                    difficulty="beginner",
                    allergens="麩質"
                ),
                Recipe(
                    title="日式咖哩飯",
                    description="濃郁的咖哩塊搭配紅蘿蔔與馬鈴薯，溫暖你的胃。",
                    image_url="https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80",
                    tags="rice,meat",
                    cooking_time=45,
                    difficulty="intermediate",
                    allergens="牛奶,麩質"
                ),
                Recipe(
                    title="香煎雞腿排",
                    description="外酥內嫩的雞腿排，簡單調味就很好吃。",
                    image_url="https://images.unsplash.com/photo-1600891964092-4316c288032e?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80",
                    tags="meat,quick",
                    cooking_time=25,
                    difficulty="beginner",
                    allergens=""
                ),
                Recipe(
                    title="麻婆豆腐",
                    description="麻辣鮮香的四川經典，白飯殺手！",
                    image_url="https://images.unsplash.com/photo-1582452919408-aca4c8de5428?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80",
                    tags="spicy,meat,rice",
                    cooking_time=30,
                    difficulty="intermediate",
                    allergens="大豆"
                ),
                Recipe(
                    title="清炒高麗菜",
                    description="清脆爽口的高麗菜，營養滿分，超簡單素食料理。",
                    image_url="https://images.unsplash.com/photo-1598514982205-f36b96d1e8d4?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80",
                    tags="vegetarian,vegan,quick",
                    cooking_time=10,
                    difficulty="beginner",
                    allergens=""
                ),
                Recipe(
                    title="馬鈴薯燉肉",
                    description="日式家庭料理的經典，甜甜鹹鹹超暖心。",
                    image_url="https://images.unsplash.com/photo-1548943487-a2e4e43b4850?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80",
                    tags="meat,soup",
                    cooking_time=50,
                    difficulty="intermediate",
                    allergens="大豆"
                ),
                Recipe(
                    title="泰式酸辣蝦湯",
                    description="酸酸辣辣的經典泰式湯品，開胃又暖身。",
                    image_url="https://images.unsplash.com/photo-1569058242253-92a9c755a0ec?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80",
                    tags="spicy,seafood,soup",
                    cooking_time=35,
                    difficulty="intermediate",
                    allergens="海鮮"
                ),
                Recipe(
                    title="素食蔬菜咖哩",
                    description="用滿滿蔬菜熬成的咖哩，全素也能超美味。",
                    image_url="https://images.unsplash.com/photo-1585937421612-70a008356fbe?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80",
                    tags="vegetarian,vegan,rice",
                    cooking_time=40,
                    difficulty="beginner",
                    allergens=""
                ),
                Recipe(
                    title="韓式辣炒年糕",
                    description="Q彈年糕搭配甜辣醬，韓劇必備的人氣小吃。",
                    image_url="https://images.unsplash.com/photo-1635363638580-c2809d049eee?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80",
                    tags="spicy,vegetarian,quick",
                    cooking_time=20,
                    difficulty="beginner",
                    allergens="麩質,大豆"
                ),
            ]
            db.session.bulk_save_objects(recipes)
            db.session.commit()


def filter_recipes_by_preference(recipes, user):
    """根據使用者偏好過濾食譜"""
    pref = user.preference
    if not pref:
        return recipes  # 沒有設定偏好，回傳全部

    user_allergens = [a.allergen_name for a in user.allergens]
    filtered = []

    for recipe in recipes:
        recipe_tags = recipe.get_tags_list()
        recipe_allergens = recipe.get_allergens_list()

        # 1. 過敏原過濾：排除含使用者過敏原的食譜
        if user_allergens:
            has_allergen = False
            for allergen in user_allergens:
                if allergen in recipe_allergens:
                    has_allergen = True
                    break
            if has_allergen:
                continue

        # 2. 飲食類型過濾
        if pref.diet_type == 'vegan':
            # 全素：只保留含 vegan 標籤的食譜
            if 'vegan' not in recipe_tags:
                continue
        elif pref.diet_type == 'vegetarian':
            # 素食(蛋奶素)：排除含 meat 或 seafood 標籤的食譜
            if 'meat' in recipe_tags or 'seafood' in recipe_tags:
                continue
        elif pref.diet_type == 'pescatarian':
            # 海鮮素：排除含 meat 標籤（但保留 seafood）
            if 'meat' in recipe_tags:
                continue

        # 3. 辣度過濾
        if not pref.spicy_ok and 'spicy' in recipe_tags:
            continue

        # 4. 烹飪時間過濾
        if pref.max_cooking_time and recipe.cooking_time:
            if recipe.cooking_time > pref.max_cooking_time:
                continue

        filtered.append(recipe)

    return filtered


def check_achievements(user):
    """檢查並解鎖成就"""
    collections_count = len(user.collections)
    cooking_count = user.cooking_count

    all_achievements = Achievement.query.all()
    unlocked_achievement_ids = [ua.achievement_id for ua in user.achievements]

    newly_unlocked = []

    for ach in all_achievements:
        if ach.id not in unlocked_achievement_ids:
            if ach.condition_type == 'collect' and collections_count >= ach.condition_value:
                ua = UserAchievement(user_id=user.id, achievement_id=ach.id)
                db.session.add(ua)
                newly_unlocked.append(ach)
            elif ach.condition_type == 'cook' and cooking_count >= ach.condition_value:
                ua = UserAchievement(user_id=user.id, achievement_id=ach.id)
                db.session.add(ua)
                newly_unlocked.append(ach)

    if newly_unlocked:
        db.session.commit()

    return newly_unlocked


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
        # 更新飲食類型
        pref.diet_type = request.form.get('diet_type', 'omnivore')
        pref.spicy_ok = request.form.get('spicy_ok') == 'on'
        pref.cooking_level = request.form.get('cooking_level', 'beginner')
        max_time = request.form.get('max_cooking_time', '60')
        try:
            pref.max_cooking_time = int(max_time)
        except ValueError:
            pref.max_cooking_time = 60

        # 更新過敏原
        # 先刪除舊的
        UserAllergen.query.filter_by(user_id=user.id).delete()
        # 加入新選的
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
#  主頁面路由
# ════════════════════════════════════════

@app.route('/')
def index():
    recipes = Recipe.query.all()
    collections = []

    # 如果使用者已登入，套用偏好過濾
    if current_user.is_authenticated:
        recipes = filter_recipes_by_preference(recipes, current_user)
        collections = [c.recipe_id for c in current_user.collections]

    all_recipes_count = Recipe.query.count()
    filtered_count = all_recipes_count - len(recipes)

    return render_template('index.html',
                           recipes=recipes,
                           collections=collections,
                           tag_display=TAG_DISPLAY,
                           filtered_count=filtered_count)


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


@app.route('/collection/add/<int:recipe_id>', methods=['POST'])
@login_required
def add_collection(recipe_id):
    user = current_user
    existing = Collection.query.filter_by(user_id=user.id, recipe_id=recipe_id).first()
    if not existing:
        new_col = Collection(user_id=user.id, recipe_id=recipe_id)
        db.session.add(new_col)
        db.session.commit()

        newly_unlocked = check_achievements(user)
        for ach in newly_unlocked:
            flash(f'解鎖成就：{ach.name} {ach.icon}', 'success')

        flash('已加入收藏！', 'success')
    return redirect(request.referrer or url_for('index'))


@app.route('/collection/remove/<int:recipe_id>', methods=['POST'])
@login_required
def remove_collection(recipe_id):
    user = current_user
    existing = Collection.query.filter_by(user_id=user.id, recipe_id=recipe_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        flash('已取消收藏。', 'info')
    return redirect(request.referrer or url_for('index'))


@app.route('/cook/<int:recipe_id>', methods=['POST'])
@login_required
def cook_recipe(recipe_id):
    user = current_user
    recipe = Recipe.query.get_or_404(recipe_id)

    user.cooking_count += 1
    db.session.commit()

    newly_unlocked = check_achievements(user)
    for ach in newly_unlocked:
        flash(f'解鎖成就：{ach.name} {ach.icon}', 'success')

    flash(f'完成料理「{recipe.title}」！累計烹飪次數：{user.cooking_count} 次', 'success')
    return redirect(request.referrer or url_for('index'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
