-- ============================================================
-- 隨食隨地 — 統一資料庫 Schema (F-01, F-03, F-04, F-06)
-- ============================================================

-- 1. 食材庫存表 (F-01)
CREATE TABLE IF NOT EXISTS ingredients (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    quantity    REAL NOT NULL,
    unit        TEXT NOT NULL,
    expiry_date TEXT, -- 儲存格式為 YYYY-MM-DD
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. 使用者基礎資料表 (F-03/F-06/User Authentication)
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    display_name  TEXT,
    cooking_count INTEGER DEFAULT 0,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. 寵物種族定義表 (F-06)
CREATE TABLE IF NOT EXISTS pet_species (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL UNIQUE,       -- 種族名稱（如：小食怪、焰靈龍、鮮綠兔）
    element         TEXT NOT NULL,              -- 元素屬性（cooking, fire, nature）
    emoji           TEXT NOT NULL,              -- 代表 Emoji
    description     TEXT,                       -- 種族描述
    color_primary   TEXT DEFAULT '#ff9f43',    -- 主題色
    color_secondary TEXT DEFAULT '#ffeaa7'     -- 次要色
);

-- 4. 寵物進化階段定義表 (F-06)
CREATE TABLE IF NOT EXISTS pet_stages (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    species_id     INTEGER NOT NULL,            -- 所屬種族 (FK)
    stage_order    INTEGER NOT NULL,            -- 進化順序 (1, 2, 3, 4)
    name           TEXT NOT NULL,               -- 階段名稱
    level_required INTEGER NOT NULL,            -- 進化所需等級
    image_path     TEXT NOT NULL,               -- 圖片路徑
    emoji          TEXT NOT NULL,               -- 階段代表 Emoji
    description    TEXT,                        -- 風味描述
    FOREIGN KEY (species_id) REFERENCES pet_species(id),
    UNIQUE(species_id, stage_order)
);

-- 5. 使用者寵物狀態表 (F-03/F-06)
CREATE TABLE IF NOT EXISTS user_pets (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER NOT NULL,           -- 使用者 ID (FK)
    species_id       INTEGER NOT NULL,           -- 選擇的種族 (FK)
    pet_name         TEXT,                       -- 寵物暱稱
    current_level    INTEGER DEFAULT 1,          -- 當前等級
    current_exp      INTEGER DEFAULT 0,          -- 當前經驗值
    current_stage_id INTEGER NOT NULL,           -- 當前進化階段 (FK)
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (species_id) REFERENCES pet_species(id),
    FOREIGN KEY (current_stage_id) REFERENCES pet_stages(id),
    UNIQUE(user_id)
);

-- 6. 使用者圖鑑解鎖記錄表 (F-06)
CREATE TABLE IF NOT EXISTS user_collection (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL,
    pet_stage_id INTEGER NOT NULL,               -- 已解鎖的階段 (FK)
    unlocked_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (pet_stage_id) REFERENCES pet_stages(id),
    UNIQUE(user_id, pet_stage_id)
);

-- 7. 飼料庫存表 (F-04)
CREATE TABLE IF NOT EXISTS feed_inventories (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    count      INTEGER DEFAULT 0,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 8. 烹飪紀錄表 (F-04)
CREATE TABLE IF NOT EXISTS cooking_records (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    image_path VARCHAR(255),
    status     VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================
-- 種子資料：預設使用者與 3 種寵物 × 4 進化階段 = 12 筆圖鑑項目
-- ============================================================

-- 建立預設開發用使用者 (ID = 1, 預設密碼為 1234)
INSERT OR IGNORE INTO users (id, username, email, password_hash, display_name, cooking_count)
VALUES (1, 'default_user', 'user@example.com', 'scrypt:32768:8:1$K3h8j6c3$ef36a5bfa4a6e87d7bca87b003a8d9a2ffb3846e4544d6db875ad2b419b48cde', '預設使用者', 0);

-- 種族 1：小食怪（料理系）
INSERT OR IGNORE INTO pet_species (id, name, element, emoji, description, color_primary, color_secondary)
VALUES (1, '小食怪', 'cooking', '🍳', '熱愛料理的可愛小怪獸，隨著烹飪技巧提升而不斷進化！', '#ff9f43', '#ffeaa7');

-- 種族 2：焰靈龍（火焰系）
INSERT OR IGNORE INTO pet_species (id, name, element, emoji, description, color_primary, color_secondary)
VALUES (2, '焰靈龍', 'fire', '🔥', '體內蘊含烈焰之力的神秘龍族，用火焰烹調出最美味的料理。', '#ee5a24', '#ff7979');

-- 種族 3：鮮綠兔（自然系）
INSERT OR IGNORE INTO pet_species (id, name, element, emoji, description, color_primary, color_secondary)
VALUES (3, '鮮綠兔', 'nature', '🌿', '與大自然共生的溫柔兔族，擅長運用新鮮蔬果製作健康料理。', '#00b894', '#55efc4');

-- 小食怪 進化階段
INSERT OR IGNORE INTO pet_stages (id, species_id, stage_order, name, level_required, image_path, emoji, description)
VALUES
(1,  1, 1, '食怪蛋',   1,  '/static/images/pets/foodie_stage1.png', '🥚', '一顆散發著香氣的神秘蛋，似乎隨時都會孵化...'),
(2,  1, 2, '小食怪',   5,  '/static/images/pets/foodie_stage2.png', '🍳', '剛孵化的小食怪，對所有食材都充滿好奇心！'),
(3,  1, 3, '美食精靈', 15, '/static/images/pets/foodie_stage3.png', '🍲', '已經能獨立烹飪的美食精靈，料理技巧日漸精湛。'),
(4,  1, 4, '廚神大師', 30, '/static/images/pets/foodie_stage4.png', '👨‍🍳', '傳說中的廚神大師，任何食材在他手中都能化為絕世佳餚！');

-- 焰靈龍 進化階段
INSERT OR IGNORE INTO pet_stages (id, species_id, stage_order, name, level_required, image_path, emoji, description)
VALUES
(5,  2, 1, '火種蛋',   1,  '/static/images/pets/flame_stage1.png', '🔴', '溫度極高的龍蛋，表面不斷閃爍著火光。'),
(6,  2, 2, '小焰龍',   5,  '/static/images/pets/flame_stage2.png', '🦎', '破殼而出的小焰龍，能噴出小小的火苗。'),
(7,  2, 3, '烈火龍',   15, '/static/images/pets/flame_stage3.png', '🐉', '掌握了烈焰之力的火龍，炙烤料理無人能敵。'),
(8,  2, 4, '神焰龍王', 30, '/static/images/pets/flame_stage4.png', '🐲', '覺醒神焰的龍王，傳說牠的火焰能烹出天界美食！');

-- 鮮綠兔 進化階段
INSERT OR IGNORE INTO pet_stages (id, species_id, stage_order, name, level_required, image_path, emoji, description)
VALUES
(9,  3, 1, '種子莢',   1,  '/static/images/pets/green_stage1.png', '🌱', '埋在沃土中的種子莢，蘊含著自然的生命力。'),
(10, 3, 2, '萌芽兔',   5,  '/static/images/pets/green_stage2.png', '🐰', '破土而出的萌芽兔，頭頂的嫩芽隨風搖曳。'),
(11, 3, 3, '花冠兔',   15, '/static/images/pets/green_stage3.png', '🌸', '頭戴花冠的優雅兔子，能讓蔬果瞬間成熟。'),
(12, 3, 4, '森靈兔神', 30, '/static/images/pets/green_stage4.png', '🌳', '守護森林的古老兔神，掌管世間一切鮮蔬果物。');

-- 開發用：為 user_id=1 建立預設寵物（小食怪）
INSERT OR IGNORE INTO user_pets (user_id, species_id, pet_name, current_level, current_exp, current_stage_id)
VALUES (1, 1, '小食怪', 1, 0, 1);

-- 預設解鎖第一階段圖鑑
INSERT OR IGNORE INTO user_collection (user_id, pet_stage_id)
VALUES (1, 1);

-- 預設飼料庫存初始化 (給予 5 個，以便初始餵食測試)
INSERT OR IGNORE INTO feed_inventories (id, user_id, count)
VALUES (1, 1, 5);
