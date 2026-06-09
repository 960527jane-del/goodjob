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
            image_url='/static/images/recipes/tomato_scrambled_eggs.png',
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
            image_url='/static/images/recipes/beef_noodles.png',
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
            image_url='/static/images/recipes/garlic_cabbage.png',
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
            image_url='/static/images/recipes/cheese_omelette.png',
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
            image_url='/static/images/recipes/seafood_noodles.png',
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
            image_url='/static/images/recipes/braised_tofu.png',
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
            image_url='/static/images/recipes/nut_oatmeal.png',
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
            image_url='/static/images/recipes/banana_toast.png',
            tags='omnivore,vegetarian,vegan',
            cooking_time=5,
            difficulty='beginner',
            allergens='花生,麩質',
            required_ingredients='吐司,花生醬,香蕉'
        ),
        Recipe(
            id=9,
            title='咖哩雞肉飯',
            description='1. 雞肉切一口大小，馬鈴薯、紅蘿蔔切塊。\n2. 熱鍋下油炒香雞肉，再放入馬鈴薯、紅蘿蔔拌炒。\n3. 加水蓋過食材，大火煮滾後轉小火煮15分鐘。\n4. 關火加入咖哩塊攪拌至融化，小火燉煮5分鐘至濃稠，淋在白飯上即可。',
            image_url='/static/images/recipes/curry_chicken_rice.png',
            tags='omnivore',
            cooking_time=30,
            difficulty='intermediate',
            allergens='',
            required_ingredients='雞肉,馬鈴薯,紅蘿蔔,洋蔥'
        ),
        Recipe(
            id=10,
            title='清蒸鱸魚',
            description='1. 鱸魚洗淨擦乾，魚身兩面劃幾刀，抹少許鹽巴與米酒。\n2. 鋪上薑絲與青蔥段，水滾後大火蒸10分鐘。\n3. 倒掉蒸出的水，拿掉青蔥段，重新鋪上新鮮的薑絲與蔥絲。\n4. 淋上蒸魚醬油，最後燒熱大匙油淋在魚身上激發香氣即可。',
            image_url='/static/images/recipes/steamed_bass.png',
            tags='omnivore,seafood',
            cooking_time=25,
            difficulty='intermediate',
            allergens='海鮮',
            required_ingredients='鱸魚,青蔥,生薑'
        ),
        Recipe(
            id=11,
            title='麻婆豆腐',
            description='1. 嫩豆腐切小塊，蒜頭、生薑切末，青蔥切花。\n2. 熱鍋下油爆香薑蒜末與辣豆瓣醬，放入絞肉炒散至變色。\n3. 加入適量醬油、糖與高湯煮滾，輕輕放入豆腐燜煮3分鐘。\n4. 太白粉水勾芡收汁，起鍋撒上花椒粉與蔥花即可。',
            image_url='/static/images/recipes/mapo_tofu.png',
            tags='omnivore,spicy',
            cooking_time=20,
            difficulty='intermediate',
            allergens='',
            required_ingredients='豆腐,絞肉,青蔥'
        ),
        Recipe(
            id=12,
            title='鳳梨蝦球',
            description='1. 蝦仁去腸泥，背部劃刀，用紙巾吸乾水分，用少許鹽巴和米酒醃製。\n2. 蝦仁沾裹地瓜粉或蛋黃液，熱油鍋下油炸至金黃酥脆後撈出瀝乾。\n3. 罐頭鳳梨切片鋪在盤底，放上炸好的蝦球。\n4. 均勻淋上美乃滋即可享用。',
            image_url='/static/images/recipes/pineapple_shrimp.png',
            tags='omnivore,seafood',
            cooking_time=25,
            difficulty='advanced',
            allergens='海鮮,蛋',
            required_ingredients='蝦仁,鳳梨,蛋'
        ),
        Recipe(
            id=13,
            title='三杯雞',
            description='1. 雞肉切塊川燙，蒜頭剝皮，生薑切片，九層塔洗淨。\n2. 鍋中倒入麻油，小火煸香薑片與蒜頭至微焦黃。\n3. 放入雞肉炒至表面微焦，加入黑麻油、醬油、米酒、冰糖，大火煮滾轉小火收汁。\n4. 湯汁快收乾時，加入九層塔大火快速翻炒均勻即可起鍋。',
            image_url='/static/images/recipes/three_cup_chicken.png',
            tags='omnivore',
            cooking_time=30,
            difficulty='intermediate',
            allergens='',
            required_ingredients='雞肉,九層塔,生薑,大蒜'
        ),
        Recipe(
            id=14,
            title='奶油蘑菇濃湯',
            description='1. 蘑菇切片，洋蔥切末，大蒜切碎。\n2. 鍋中融化奶油，炒香洋蔥、大蒜與蘑菇，直到蘑菇出水並炒至微焦。\n3. 加入麵粉炒勻，分次緩慢加入高湯攪拌均勻避免結塊，小火煮滾。\n4. 倒入牛奶或鮮奶油再煮5分鐘，最後以鹽與黑胡椒調味即可。',
            image_url='/static/images/recipes/mushroom_soup.png',
            tags='omnivore,vegetarian',
            cooking_time=20,
            difficulty='beginner',
            allergens='牛奶',
            required_ingredients='蘑菇,牛奶,洋蔥'
        ),
        Recipe(
            id=15,
            title='涼拌小黃瓜',
            description='1. 小黃瓜洗淨，用刀背拍碎後切成段，加入少許鹽抓勻醃製10分鐘，瀝乾出水。\n2. 大蒜切碎，辣椒切片。\n3. 在小黃瓜中加入蒜末、辣椒、糖、白醋、香油，攪拌均勻。\n4. 放入冰箱冷藏醃製30分鐘以上，風味更佳。',
            image_url='/static/images/recipes/cucumber_salad.png',
            tags='omnivore,vegetarian,vegan',
            cooking_time=10,
            difficulty='beginner',
            allergens='',
            required_ingredients='小黃瓜,大蒜,辣椒'
        ),
        Recipe(
            id=16,
            title='紅油抄手',
            description='1. 餛飩放入滾水中煮熟後撈出。\n2. 將醬油、醋、糖、花椒粉、紅油與蒜末調成醬汁。\n3. 將醬汁淋在餛飩上，撒上花生碎與蔥花即可。',
            image_url='/static/images/recipes/spicy_wontons.png',
            tags='omnivore,spicy',
            cooking_time=15,
            difficulty='beginner',
            allergens='麩質,花生',
            required_ingredients='餛飩,大蒜,青蔥'
        ),
        Recipe(
            id=17,
            title='奶油培根義大利麵',
            description='1. 義大利麵煮熟備用，培根切條。\n2. 蛋黃、鮮奶油、帕瑪森起司與黑胡椒拌勻成醬汁。\n3. 炒香培根，倒入義大利麵與煮麵水拌勻，關火後倒入醬汁快速拌勻至濃稠即可。',
            image_url='/static/images/recipes/carbonara.png',
            tags='omnivore',
            cooking_time=20,
            difficulty='intermediate',
            allergens='麩質,蛋,牛奶',
            required_ingredients='義大利麵,培根,雞蛋,起司'
        ),
        Recipe(
            id=18,
            title='鮮脆什錦沙拉',
            description='1. 生菜、小黃瓜、小番茄洗淨切妥。\n2. 加入堅果與起司碎。\n3. 淋上橄欖油與油醋汁拌勻即可。',
            image_url='/static/images/recipes/garden_salad.png',
            tags='omnivore,vegetarian,vegan',
            cooking_time=8,
            difficulty='beginner',
            allergens='堅果',
            required_ingredients='生菜,小黃瓜,番茄,堅果'
        ),
        Recipe(
            id=19,
            title='薑絲蛤蜊湯',
            description='1. 蛤蜊吐沙洗淨，生薑切絲，青蔥切花。\n2. 鍋中加水燒開，放入薑絲與蛤蜊。\n3. 蛤蜊煮至全開，加入少許鹽巴與米酒，撒上蔥花即可。',
            image_url='/static/images/recipes/clam_soup.png',
            tags='omnivore,seafood',
            cooking_time=12,
            difficulty='beginner',
            allergens='海鮮',
            required_ingredients='蛤蜊,生薑,青蔥'
        ),
        Recipe(
            id=20,
            title='青椒炒肉絲',
            description='1. 肉絲用醬油、米酒、太白粉醃製。\n2. 青椒洗淨切絲。\n3. 熱鍋下油爆香蒜末，放入肉絲炒至變色撈出，再下青椒炒熟，最後合炒均勻即可。',
            image_url='/static/images/recipes/pork_pepper.png',
            tags='omnivore',
            cooking_time=15,
            difficulty='beginner',
            allergens='',
            required_ingredients='豬肉,青椒,大蒜'
        ),
        Recipe(
            id=21,
            title='糖醋排骨',
            description='1. 排骨醃製後沾地瓜粉炸至金黃。\n2. 鍋中留底油，加入糖、醋、醬油、水調成糖醋汁煮滾。\n3. 放入排骨翻炒，讓糖醋汁均勻裹在排骨上，撒上芝麻即可。',
            image_url='/static/images/recipes/sugar_ribs.png',
            tags='omnivore',
            cooking_time=35,
            difficulty='advanced',
            allergens='',
            required_ingredients='排骨,芝麻'
        ),
        Recipe(
            id=22,
            title='照燒雞腿排',
            description='1. 雞腿排皮朝下煎至金黃出油，翻面煎熟。\n2. 倒入醬油、味醂、米酒與糖調成的照照醬汁。\n3. 大火收汁至醬汁濃稠，切塊後灑上白芝麻即可。',
            image_url='/static/images/recipes/teriyaki_chicken.png',
            tags='omnivore',
            cooking_time=25,
            difficulty='intermediate',
            allergens='',
            required_ingredients='雞肉,芝麻'
        ),
        Recipe(
            id=23,
            title='紅燒茄子',
            description='1. 茄子切段切條，過油炸軟撈出。\n2. 爆香蒜末、薑末與蔥白，加入醬油、糖、醋與水煮滾。\n3. 倒入茄子燜煮入味，最後勾芡收汁，撒上蔥花即可。',
            image_url='/static/images/recipes/braised_eggplant.png',
            tags='omnivore,vegetarian,vegan',
            cooking_time=20,
            difficulty='intermediate',
            allergens='',
            required_ingredients='茄子,大蒜,青蔥,生薑'
        ),
        Recipe(
            id=24,
            title='宮保雞丁',
            description='1. 雞丁用醬油、米酒、太白粉醃製。\n2. 熱鍋下油爆香乾辣椒、花椒粒與薑蒜片。\n3. 下雞丁大火快炒至熟，倒入醬汁與花生米快速翻炒均勻即可。',
            image_url='/static/images/recipes/kung_pao_chicken.png',
            tags='omnivore,spicy',
            cooking_time=20,
            difficulty='intermediate',
            allergens='花生',
            required_ingredients='雞肉,花生,大蒜,生薑'
        ),
        Recipe(
            id=25,
            title='乾煎鮭魚排',
            description='1. 鮭魚排兩面抹上少許鹽巴與黑胡椒。\n2. 熱鍋不放油（鮭魚富含油脂），皮朝下入鍋中火煎至酥脆。\n3. 翻面煎熟，起鍋前可淋上檸檬汁。',
            image_url='/static/images/recipes/seared_salmon.png',
            tags='omnivore,seafood',
            cooking_time=15,
            difficulty='beginner',
            allergens='海鮮',
            required_ingredients='鮭魚,檸檬'
        ),
        Recipe(
            id=26,
            title='香煎蘿蔔糕',
            description='1. 蘿蔔糕切成適當厚度的片狀。\n2. 平底鍋熱油，放入蘿蔔糕小火慢煎。\n3. 煎至兩面金黃酥脆即可起鍋，搭配蒜蓉醬油食用。',
            image_url='/static/images/recipes/radish_cake.png',
            tags='omnivore,vegetarian',
            cooking_time=10,
            difficulty='beginner',
            allergens='',
            required_ingredients='蘿蔔糕'
        ),
        Recipe(
            id=27,
            title='經典馬鈴薯燉肉',
            description='1. 肉片切段，馬鈴薯、紅蘿蔔、洋蔥切塊。\n2. 炒香洋蔥與肉片，放入馬鈴薯與紅蘿蔔拌炒。\n3. 加入水、醬油、味醂與糖，大火煮滾後轉小火燉煮20分鐘至入味。',
            image_url='/static/images/recipes/nikujaga.png',
            tags='omnivore',
            cooking_time=35,
            difficulty='intermediate',
            allergens='',
            required_ingredients='豬肉,馬鈴薯,紅蘿蔔,洋蔥'
        ),
        Recipe(
            id=28,
            title='泰式打拋豬',
            description='1. 熱鍋下油，爆香蒜末與辣椒末。\n2. 放入豬絞肉炒散至變色，加入醬油、蠔油與糖調味。\n3. 起鍋前加入九層塔大火翻炒，淋上檸檬汁即可。',
            image_url='/static/images/recipes/pad_kra_prow.png',
            tags='omnivore,spicy',
            cooking_time=15,
            difficulty='beginner',
            allergens='',
            required_ingredients='豬肉,九層塔,大蒜,辣椒,檸檬'
        ),
        Recipe(
            id=29,
            title='銀耳紅棗蓮子湯',
            description='1. 白木耳湯泡軟剪碎，紅棗、蓮子洗淨。\n2. 鍋中加水，放入白木耳大火煮滾後轉小火慢燉1小時至出膠。\n3. 放入紅棗、蓮子與冰糖，再燉煮20分鐘即可。',
            image_url='/static/images/recipes/white_fungus_soup.png',
            tags='omnivore,vegetarian,vegan',
            cooking_time=80,
            difficulty='intermediate',
            allergens='',
            required_ingredients='白木耳,紅棗,蓮子'
        ),
        Recipe(
            id=30,
            title='味噌豆腐湯',
            description='1. 豆腐切丁，海帶芽泡水展開，青蔥切末。\n2. 鍋中加水煮滾，放入豆腐與海帶芽煮2分鐘。\n3. 關火，將味噌融化入湯中攪拌均勻，撒上蔥花即可。',
            image_url='/static/images/recipes/miso_soup.png',
            tags='omnivore,vegetarian,vegan',
            cooking_time=10,
            difficulty='beginner',
            allergens='',
            required_ingredients='豆腐,青蔥,海帶芽'
        )
    ]
    for rec in recipes:
        existing = db.session.get(Recipe, rec.id)
        if not existing:
            db.session.add(rec)
            print(f"Seeded recipe: {rec.title}")
        else:
            # Update fields if already exists
            existing.title = rec.title
            existing.description = rec.description
            existing.image_url = rec.image_url
            existing.tags = rec.tags
            existing.cooking_time = rec.cooking_time
            existing.difficulty = rec.difficulty
            existing.allergens = rec.allergens
            existing.required_ingredients = rec.required_ingredients
            print(f"Updated recipe: {rec.title}")
    db.session.commit()
    print("Database seeding completed!")
