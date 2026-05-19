import os
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, User, Recipe, Collection, Achievement, UserAchievement

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key-cute-app'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def init_db():
    with app.app_context():
        db.create_all()
        # Create a test user if not exists
        if not User.query.filter_by(username='Test User').first():
            test_user = User(username='Test User')
            db.session.add(test_user)
            db.session.commit()
            
            # Add cute achievements
            achievements = [
                Achievement(name="踏出新手村的廚師", description="首次將食譜加入收藏", icon="🎓", condition_type="collect", condition_value=1),
                Achievement(name="食譜收集狂", description="收藏 5 篇食譜", icon="📚", condition_type="collect", condition_value=5),
                Achievement(name="開火啦！", description="完成第 1 道料理", icon="🔥", condition_type="cook", condition_value=1),
                Achievement(name="連續開伙小天才", description="完成 5 道料理", icon="🍳", condition_type="cook", condition_value=5),
                Achievement(name="清冰箱大師", description="完成 10 道料理", icon="❄️", condition_type="cook", condition_value=10)
            ]
            db.session.bulk_save_objects(achievements)
            
            # Add some fake recipes
            recipes = [
                Recipe(title="番茄炒蛋", description="經典家常菜，酸甜下飯。", image_url="https://images.unsplash.com/photo-1596797038530-2c107229654b?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80"),
                Recipe(title="蒜香義大利麵", description="只要大蒜、橄欖油和義大利麵就能完成。", image_url="https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80"),
                Recipe(title="日式咖哩飯", description="濃郁的咖哩塊搭配紅蘿蔔與馬鈴薯。", image_url="https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80"),
                Recipe(title="香煎雞腿排", description="外酥內嫩的雞腿排，簡單調味就很好吃。", image_url="https://images.unsplash.com/photo-1600891964092-4316c288032e?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80"),
                Recipe(title="清炒高麗菜", description="清脆爽口的高麗菜，營養滿分。", image_url="https://images.unsplash.com/photo-1598514982205-f36b96d1e8d4?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80"),
                Recipe(title="馬鈴薯燉肉", description="日式家庭料理的經典，溫暖你的胃。", image_url="https://images.unsplash.com/photo-1548943487-a2e4e43b4850?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80")
            ]
            db.session.bulk_save_objects(recipes)
            db.session.commit()

def check_achievements(user):
    collections_count = len(user.collections)
    cooking_count = user.cooking_count
    
    # Get all achievements
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

@app.route('/')
def index():
    user = User.query.filter_by(username='Test User').first()
    recipes = Recipe.query.all()
    collections = [c.recipe_id for c in user.collections]
    return render_template('index.html', recipes=recipes, collections=collections)

@app.route('/profile')
def profile():
    user = User.query.filter_by(username='Test User').first()
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
def add_collection(recipe_id):
    user = User.query.filter_by(username='Test User').first()
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
def remove_collection(recipe_id):
    user = User.query.filter_by(username='Test User').first()
    existing = Collection.query.filter_by(user_id=user.id, recipe_id=recipe_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        flash('已取消收藏。', 'info')
    return redirect(request.referrer or url_for('index'))

@app.route('/cook/<int:recipe_id>', methods=['POST'])
def cook_recipe(recipe_id):
    user = User.query.filter_by(username='Test User').first()
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
