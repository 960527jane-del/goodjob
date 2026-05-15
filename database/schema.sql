-- 刪除已存在的資料表以避免衝突 (適用於重置資料庫)
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS pets;

-- 建立使用者資料表
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 建立寵物資料表
CREATE TABLE pets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    level INTEGER DEFAULT 1,
    exp INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- 插入測試資料 (Seeding)
INSERT INTO users (username) VALUES ('test_user_1');
-- 測試使用者 1 擁有一隻名叫「貪吃小雞」的 1 級寵物
INSERT INTO pets (user_id, name, level, exp) VALUES (1, '貪吃小雞', 1, 0);
