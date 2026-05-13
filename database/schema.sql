-- schema.sql
-- 智慧食譜推薦系統：資料庫建表語法

-- 建立 ingredients (我的材料庫) 資料表
CREATE TABLE IF NOT EXISTS ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    quantity REAL NOT NULL,
    unit TEXT NOT NULL,
    expiry_date TEXT, -- 儲存格式為 YYYY-MM-DD
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
