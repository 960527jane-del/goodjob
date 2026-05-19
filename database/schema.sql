-- 隨食隨地 SQLite 資料庫建表語法

-- 建立食材庫存表
CREATE TABLE IF NOT EXISTS ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    quantity REAL NOT NULL,
    unit TEXT,
    expiry_date TEXT,
    created_at TEXT NOT NULL
);
