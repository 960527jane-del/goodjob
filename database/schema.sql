-- ============================================================
-- 隨食隨地 — 統一資料庫 Schema (Virtual Pet System Only)
-- ============================================================

-- 1. 使用者基礎資料表
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    display_name  TEXT,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. 寵物狀態表
CREATE TABLE IF NOT EXISTS pets (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL UNIQUE,
    name          TEXT NOT NULL,
    hunger        INTEGER DEFAULT 100, -- 飢餓度 (預設 100)
    growth        INTEGER DEFAULT 0,   -- 成長值 (預設 0)
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================
-- 種子資料
-- ============================================================

-- 建立預設開發用使用者 (ID = 1, 預設密碼為 1234)
INSERT OR IGNORE INTO users (id, username, email, password_hash, display_name)
VALUES (1, 'default_user', 'user@example.com', 'scrypt:32768:8:1$K3h8j6c3$ef36a5bfa4a6e87d7bca87b003a8d9a2ffb3846e4544d6db875ad2b419b48cde', '預設使用者');

-- 建立預設寵物
INSERT OR IGNORE INTO pets (user_id, name, hunger, growth)
VALUES (1, '小食怪', 100, 0);
