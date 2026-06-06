from flask import Blueprint, redirect, url_for, render_template, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from sql_models import db, User, UserPreference, UserAllergen, Achievement, UserAchievement
from app.models.pet import Pet
from app.models.feed_inventory import FeedInventory

main_bp = Blueprint('main', __name__)


@main_bp.route('/', methods=['GET'])
def index():
    """首頁重定向至虛擬寵物頁面"""
    if current_user.is_authenticated:
        return redirect(url_for('pet.pet_index'))
    return render_template('index.html')


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('pet.pet_index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('請檢查電子信箱或密碼是否正確。', 'error')
            return render_template('login.html', email=email)
            
        login_user(user, remember=remember)
        flash('登入成功，歡迎回來！', 'success')
        return redirect(url_for('pet.pet_index'))
        
    return render_template('login.html')


@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('pet.pet_index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        display_name = request.form.get('display_name') or username
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        if password != password_confirm:
            flash('兩次輸入的密碼不一致！', 'error')
            return render_template('register.html', email=email, username=username, display_name=display_name)
            
        if User.query.filter_by(email=email).first():
            flash('該 Email 已被註冊！', 'error')
            return render_template('register.html', username=username, display_name=display_name)
            
        if User.query.filter_by(username=username).first():
            flash('該帳號名稱已被使用！', 'error')
            return render_template('register.html', email=email, display_name=display_name)
            
        # 建立使用者
        new_user = User(email=email, username=username, display_name=display_name)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        # 初始化寵物 (F-03)
        try:
            # 建立預設寵物，這會自動寫入 user_pets 表並解鎖圖鑑第一階段
            Pet.create(new_user.id, f"{display_name}的寵物")
        except Exception as e:
            print(f"Error creating pet for new user: {e}")
            
        # 初始化飼料庫存 (F-04) - 贈送 5 個初始飼料
        try:
            FeedInventory.create(new_user.id, count=5)
        except Exception as e:
            print(f"Error creating feed inventory for new user: {e}")
            
        # 初始化使用者偏好設定 (F-02)
        try:
            default_pref = UserPreference(user_id=new_user.id, diet_type='omnivore', spicy_ok=True, cooking_level='beginner', max_cooking_time=60)
            db.session.add(default_pref)
            db.session.commit()
        except Exception as e:
            print(f"Error creating user preference: {e}")
            
        login_user(new_user)
        flash('註冊成功！已為您登入並建立初始寵物與偏好設定！', 'success')
        return redirect(url_for('main.preferences'))
        
    return render_template('register.html')


@main_bp.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    flash('您已成功登出。', 'info')
    return redirect(url_for('main.login'))


@main_bp.route('/preferences', methods=['GET', 'POST'])
@login_required
def preferences():
    # 取得當前偏好設定
    pref = UserPreference.query.filter_by(user_id=current_user.id).first()
    if not pref:
        pref = UserPreference(user_id=current_user.id)
        db.session.add(pref)
        db.session.commit()
        
    # 取得過敏原
    user_allergens = [a.allergen_name for a in current_user.allergens]
    
    diet_type_options = {
        'omnivore': '葷食',
        'vegetarian': '蛋奶素',
        'vegan': '全素',
        'seafood': '海鮮素'
    }
    
    allergen_options = ['蛋', '牛奶', '麩質', '海鮮', '堅果', '花生']
    
    cooking_level_options = {
        'beginner': '新手',
        'intermediate': '家常',
        'advanced': '大師'
    }
    
    if request.method == 'POST':
        diet_type = request.form.get('diet_type')
        spicy_ok = True if request.form.get('spicy_ok') else False
        cooking_level = request.form.get('cooking_level')
        max_cooking_time = int(request.form.get('max_cooking_time', 60))
        
        pref.diet_type = diet_type
        pref.spicy_ok = spicy_ok
        pref.cooking_level = cooking_level
        pref.max_cooking_time = max_cooking_time
        
        # 處理過敏原變更
        # 1. 刪除原有過敏原
        UserAllergen.query.filter_by(user_id=current_user.id).delete()
        
        # 2. 新增勾選的過敏原
        selected_allergens = request.form.getlist('allergens')
        for allergen in selected_allergens:
            ua = UserAllergen(user_id=current_user.id, allergen_name=allergen)
            db.session.add(ua)
            
        db.session.commit()
        flash('偏好設定已更新！', 'success')
        return redirect(url_for('pet.pet_index'))
        
    return render_template(
        'preferences.html',
        pref=pref,
        user_allergens=user_allergens,
        diet_type_options=diet_type_options,
        allergen_options=allergen_options,
        cooking_level_options=cooking_level_options
    )


@main_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    # 取得使用者成就解鎖紀錄 (帶有解鎖時間)
    unlocked_achievements = db.session.query(Achievement, UserAchievement.unlocked_at)\
        .join(UserAchievement, Achievement.id == UserAchievement.achievement_id)\
        .filter(UserAchievement.user_id == current_user.id)\
        .order_by(UserAchievement.unlocked_at.desc()).all()
        
    # 取得使用者收藏食譜
    from sql_models import Recipe, Collection
    saved_recipes = db.session.query(Recipe)\
        .join(Collection, Recipe.id == Collection.recipe_id)\
        .filter(Collection.user_id == current_user.id)\
        .all()
        
    # 取得寵物資訊
    pet = Pet.get_by_user_id(current_user.id)
    
    return render_template(
        'profile.html',
        unlocked_achievements=unlocked_achievements,
        saved_recipes=saved_recipes,
        pet=pet
    )
