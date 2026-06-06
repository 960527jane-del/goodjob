import sqlite3
import os
from app import create_app
from sql_models import db, User, UserPreference, Achievement, Recipe

os.makedirs('instance', exist_ok=True)
db_path = os.path.join('instance', 'database.db')
schema_path = os.path.join('database', 'schema.sql')

print("Initializing SQLite database via schema.sql...")
with sqlite3.connect(db_path) as conn:
    conn.execute("PRAGMA foreign_keys = ON")
    with open(schema_path, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
print("Database schema loaded successfully at", db_path)

app = create_app()
with app.app_context():
    print("Initializing ORM tables and seeding...")
    db.create_all()
    
    # 1. 檢查並建立預設開發用使用者
    user = db.session.get(User, 1)
    if not user:
        test_user = User(id=1, username='default_user', email='user@example.com')
        test_user.set_password('1234')
        db.session.add(test_user)
        db.session.commit()
        print("Default test user created in ORM!")
    else:
        user.set_password('1234')
        db.session.commit()
        print("Default test user password reset to '1234' in ORM!")

    # 2. 檢查並建立預設偏好設定
    pref = UserPreference.query.filter_by(user_id=1).first()
    if not pref:
        test_pref = UserPreference(user_id=1, diet_type='omnivore', spicy_ok=True, cooking_level='beginner', max_cooking_time=60)
        db.session.add(test_pref)
        db.session.commit()
        print("Default user preferences created!")

    # 3. 檢查並寫入成就種子資料
    achievements = [
        Achievement(id=1, name='新手廚師', description='第一次完成料理回報。', icon='🍳', condition_type='cooking_count', condition_value=1),
        Achievement(id=2, name='家常小炒', description='累計完成 3 次料理回報。', icon='👨‍🍳', condition_type='cooking_count', condition_value=3),
        Achievement(id=3, name='特級廚師', description='累計完成 10 次料理回報。', icon='🏆', condition_type='cooking_count', condition_value=10),
        Achievement(id=4, name='新手訓練家', description='寵物等級達到 5 級。', icon='👾', condition_type='pet_level', condition_value=5),
        Achievement(id=5, name='神奇飼主', description='寵物等級達到 10 級。', icon='💖', condition_type='pet_level', condition_value=10),
        Achievement(id=6, name='幻獸大師', description='寵物等級達到 20 級。', icon='👑', condition_type='pet_level', condition_value=20),
        Achievement(id=7, name='圖鑑初學者', description='圖鑑解鎖數量達到 2 個。', icon='📖', condition_type='unlocked_collection', condition_value=2),
        Achievement(id=8, name='大收集家', description='圖鑑解鎖數量達到 4 個。', icon='📚', condition_type='unlocked_collection', condition_value=4),
    ]
    for ach in achievements:
        existing = db.session.get(Achievement, ach.id)
        if not existing:
            db.session.add(ach)
            print(f"Seeded achievement: {ach.name}")
    db.session.commit()

    # 4. 檢查並寫入食譜種子資料
    recipes = [
        Recipe(
            id=1,
            title='番茄炒蛋',
            description='1. 番茄切塊，雞蛋打散拌勻。\n2. 熱鍋下油，先將蛋液炒熟起鍋。\n3. 鍋中再加點油，炒香番茄塊，加入少許鹽與糖。\n4. 倒入蛋花拌炒均勻，即可上碟。',
            image_url='https://images.unsplash.com/photo-1598103442097-8b74394b95c6?auto=format&fit=crop&w=600&q=80',
            tags='omnivore,vegetarian',
            cooking_time=15,
            difficulty='beginner',
            allergens='蛋',
            required_ingredients='番茄,雞蛋'
        ),
        Recipe(
            id=2,
            title='經典牛肉麵',
            description='1. 牛肉切塊川燙去血水。\n2. 炒香蔥、薑、蒜與八角，加入醬油、米酒、冰糖與水。\n3. 加入牛肉燉煮45分鐘。\n4. 另煮一鍋水，將麵條與青蔥煮熟，撈起放入牛肉湯中即可。',
            image_url='https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?auto=format&fit=crop&w=600&q=80',
            tags='omnivore,beef',
            cooking_time=60,
            difficulty='intermediate',
            allergens='麩質',
            required_ingredients='牛肉,麵條,青蔥'
        ),
        Recipe(
            id=3,
            title='蒜炒高麗菜',
            description='1. 高麗菜洗淨撕成小片，大蒜切碎。\n2. 熱鍋下油，爆香蒜末。\n3. 放入高麗菜大火快炒，加入少許鹽調味。\n4. 炒至稍微變軟且帶有脆度即可起鍋。',
            image_url='https://images.unsplash.com/photo-1608897013039-887f21d8c804?auto=format&fit=crop&w=600&q=80',
            tags='omnivore,vegetarian,vegan',
            cooking_time=10,
            difficulty='beginner',
            allergens='',
            required_ingredients='高麗菜,大蒜'
        ),
        Recipe(
            id=4,
            title='起司歐姆蛋',
            description='1. 雞蛋加入牛奶打散，少許鹽巴調味。\n2. 平底鍋小火熱奶油，倒入蛋液。\n3. 蛋液半熟時，將起司片或起司絲鋪在一側。\n4. 將另一側蛋皮對折，煎至微焦黃，起司融化即可起鍋。',
            image_url='https://images.unsplash.com/photo-1494597564530-871f2b93ac55?auto=format&fit=crop&w=600&q=80',
            tags='omnivore,vegetarian',
            cooking_time=12,
            difficulty='beginner',
            allergens='蛋,牛奶',
            required_ingredients='雞蛋,起司,牛奶'
        ),
        Recipe(
            id=5,
            title='海鮮什錦麵',
            description='1. 蝦子去殼洗淨，蛤蜊吐沙。\n2. 爆香蔥段，加入水煮滾。\n3. 先下麵條煮至半熟，再放入蝦子與蛤蜊。\n4. 蛤蜊全開後加入少許鹽調味即可上桌。',
            image_url='https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=600&q=80',
            tags='omnivore,seafood',
            cooking_time=20,
            difficulty='intermediate',
            allergens='海鮮,麩質',
            required_ingredients='蝦子,蛤蜊,麵條'
        ),
        Recipe(
            id=6,
            title='醬香豆腐',
            description='1. 豆腐切塊，青蔥切段，大蒜切末。\n2. 熱鍋下油將豆腐兩面煎至金黃。\n3. 加入蒜末炒香，倒入少許醬油、糖與水，小火燜煮5分鐘。\n4. 起鍋前撒上青蔥段拌炒即可。',
            image_url='https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=600&q=80',
            tags='omnivore,vegetarian,vegan',
            cooking_time=15,
            difficulty='beginner',
            allergens='',
            required_ingredients='豆腐,青蔥,大蒜'
        ),
        Recipe(
            id=7,
            title='烤堅果燕麥粥',
            description='1. 燕麥片與牛奶倒入小鍋，小火煮滾至濃稠。\n2. 堅果稍微壓碎，撒在燕麥粥表面。\n3. 可依個人喜好加入蜂蜜調味。',
            image_url='https://images.unsplash.com/photo-1517881917431-1355499739c7?auto=format&fit=crop&w=600&q=80',
            tags='omnivore,vegetarian',
            cooking_time=10,
            difficulty='beginner',
            allergens='牛奶,堅果',
            required_ingredients='燕麥,堅果,牛奶'
        ),
        Recipe(
            id=8,
            title='香脆花生香蕉吐司',
            description='1. 吐司烤至微焦香。\n2. 均勻抹上一層厚厚的花生醬。\n3. 香蕉切片鋪在吐司上，即可食用。',
            image_url='https://images.unsplash.com/photo-1541532713592-79a0317b6b77?auto=format&fit=crop&w=600&q=80',
            tags='omnivore,vegetarian,vegan',
            cooking_time=5,
            difficulty='beginner',
            allergens='花生,麩質',
            required_ingredients='吐司,花生醬,香蕉'
        )
    ]
    for rec in recipes:
        existing = db.session.get(Recipe, rec.id)
        if not existing:
            db.session.add(rec)
            print(f"Seeded recipe: {rec.title}")
    db.session.commit()
    print("Database seeding completed!")
