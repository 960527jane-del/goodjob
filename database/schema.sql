-- ============================================================
-- 隨食隨地 — 統一資料庫 Schema
-- ============================================================

-- 1. 使用者基礎資料表
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    display_name  TEXT,
    cooking_count INTEGER DEFAULT 0,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. 寵物種族表 (F-06)
CREATE TABLE IF NOT EXISTS pet_species (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    name              TEXT NOT NULL,
    element           TEXT,
    emoji             TEXT,
    description       TEXT,
    color_primary     TEXT,
    color_secondary   TEXT
);

-- 3. 寵物進化階段表 (F-06)
CREATE TABLE IF NOT EXISTS pet_stages (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    species_id       INTEGER NOT NULL,
    stage_order      INTEGER,
    name             TEXT NOT NULL,
    level_required   INTEGER,
    image_path       TEXT,
    emoji            TEXT,
    description      TEXT,
    FOREIGN KEY (species_id) REFERENCES pet_species(id) ON DELETE CASCADE
);

-- 4. 使用者寵物狀態表 (F-03/F-06)
CREATE TABLE IF NOT EXISTS user_pets (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id           INTEGER NOT NULL,
    species_id        INTEGER,
    pet_name          TEXT NOT NULL,
    current_level     INTEGER DEFAULT 1,
    current_exp       INTEGER DEFAULT 0,
    current_stage_id  INTEGER,
    hunger            INTEGER DEFAULT 50,
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (species_id) REFERENCES pet_species(id),
    FOREIGN KEY (current_stage_id) REFERENCES pet_stages(id)
);

-- 5. 飼料庫存表 (F-03)
CREATE TABLE IF NOT EXISTS feed_inventories (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL UNIQUE,
    count        INTEGER DEFAULT 0,
    updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 6. 寵物圖鑑解鎖表 (F-06)
CREATE TABLE IF NOT EXISTS user_collection (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL,
    pet_stage_id INTEGER NOT NULL,
    unlocked_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (pet_stage_id) REFERENCES pet_stages(id) ON DELETE CASCADE,
    UNIQUE(user_id, pet_stage_id)
);

-- 7. 食材表 (F-02)
CREATE TABLE IF NOT EXISTS ingredients (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    quantity    REAL NOT NULL,
    unit        TEXT NOT NULL,
    expiry_date TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 8. 烹飪紀錄表 (F-02)
CREATE TABLE IF NOT EXISTS cooking_records (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    image_path TEXT,
    status     TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 9. 食譜表 (F-02)
CREATE TABLE IF NOT EXISTS recipe (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    title         TEXT NOT NULL,
    description   TEXT,
    image_url     TEXT,
    tags          TEXT,
    cooking_time  INTEGER,
    difficulty    TEXT,
    allergens     TEXT,
    required_ingredients TEXT
);

-- 10. 使用者食譜收藏表 (F-02)
CREATE TABLE IF NOT EXISTS collection (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    recipe_id  INTEGER NOT NULL,
    saved_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (recipe_id) REFERENCES recipe(id) ON DELETE CASCADE,
    UNIQUE(user_id, recipe_id)
);

-- 11. 使用者偏好設定表 (F-02)
CREATE TABLE IF NOT EXISTS user_preference (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id           INTEGER NOT NULL UNIQUE,
    diet_type         TEXT,
    spicy_ok          BOOLEAN DEFAULT 1,
    cooking_level     TEXT,
    max_cooking_time  INTEGER,
    updated_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 12. 使用者過敏原表 (F-02)
CREATE TABLE IF NOT EXISTS user_allergen (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL,
    allergen_name TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 13. 成就表 (F-06)
CREATE TABLE IF NOT EXISTS achievement (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    description     TEXT,
    icon            TEXT,
    condition_type  TEXT,
    condition_value INTEGER
);

-- 14. 使用者成就達成表 (F-06)
CREATE TABLE IF NOT EXISTS user_achievement (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    achievement_id  INTEGER NOT NULL,
    unlocked_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (achievement_id) REFERENCES achievement(id) ON DELETE CASCADE,
    UNIQUE(user_id, achievement_id)
);

-- ============================================================
-- 種子資料
-- ============================================================

-- 建立預設開發用使用者 (ID = 1, 預設密碼為 1234)
INSERT OR IGNORE INTO users (id, username, email, password_hash, display_name)
VALUES (1, 'default_user', 'user@example.com', 'scrypt:32768:8:1$K3h8j6c3$ef36a5bfa4a6e87d7bca87b003a8d9a2ffb3846e4544d6db875ad2b419b48cde', '預設使用者');

-- 建立預設寵物種族
INSERT OR IGNORE INTO pet_species (id, name, element, emoji, description, color_primary, color_secondary)
VALUES 
    (1, '火焰小怪', 'Fire', '🔥', '熱愛美食的火焰型寵物', '#FF6B6B', '#FFA500'),
    (2, '水滴小寶', 'Water', '💧', '溫柔療癒的水系型寵物', '#4ECDC4', '#45B7D1');

-- 建立預設寵物進化階段
INSERT OR IGNORE INTO pet_stages (id, species_id, stage_order, name, level_required, emoji, description)
VALUES 
    (1, 1, 1, '幼火焰', 1, '🔥', '剛孵化的小火焰'),
    (2, 1, 2, '熱血火焰', 10, '🔥🔥', '成長期的火焰'),
    (3, 1, 3, '烈火戰士', 20, '🔥🔥🔥', '進化完全的火焰戰士'),
    (4, 2, 1, '小水滴', 1, '💧', '剛孵化的小水滴'),
    (5, 2, 2, '波浪水精', 10, '💧💧', '成長期的水精靈'),
    (6, 2, 3, '海洋水神', 20, '💧💧💧', '進化完全的水神');

-- 建立預設使用者寵物
INSERT OR IGNORE INTO user_pets (id, user_id, species_id, pet_name, current_level, current_exp, current_stage_id, hunger)
VALUES (1, 1, 1, '小食怪', 1, 0, 1, 50);

-- 建立預設飼料庫存
INSERT OR IGNORE INTO feed_inventories (user_id, count)
VALUES (1, 100);

