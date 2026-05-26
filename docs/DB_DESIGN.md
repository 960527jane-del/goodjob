# 資料庫設計 - 智慧食譜推薦系統 (F-02)

本文件依據前期的設計規劃，定義了「我的材料庫」底層資料庫的結構與關聯，並提供對應的建表語法。

## 1. ER 圖（實體關係圖）

本系統的核心在於管理使用者的可用食材，作為向外部 API 請求食譜推薦的基礎。由於目前為 MVP 版本，主要設計 `ingredients` 資料表。

```mermaid
erDiagram
  INGREDIENTS {
    integer id PK "主鍵"
    string name "食材名稱"
    real quantity "數量"
    string unit "單位 (如: g, 顆)"
    date expiry_date "有效期限 (YYYY-MM-DD)"
    datetime created_at "建立時間"
  }
```

## 2. 資料表詳細說明

### `ingredients` (我的材料庫)
儲存使用者目前擁有的食材清單，作為食譜推薦系統的查詢基準。

| 欄位名稱 | 型別 | 必填 | 說明 |
| :--- | :--- | :---: | :--- |
| `id` | INTEGER | ✅ | 主鍵 (Primary Key)，自動遞增 |
| `name` | TEXT | ✅ | 食材名稱（例如：雞肉、洋蔥、番茄） |
| `quantity` | REAL | ✅ | 剩餘數量 |
| `unit` | TEXT | ✅ | 數量單位（例如：g, kg, 顆, 把） |
| `expiry_date` | TEXT | ❌ | 有效期限，ISO 格式 `YYYY-MM-DD`，用於優先推薦即期食材 |
| `created_at` | DATETIME | ✅ | 建立時間，預設為 `CURRENT_TIMESTAMP` |

## 3. SQL 建表語法

SQLite 建表語法已儲存於 `database/schema.sql`，可用於初始化系統資料庫。

## 4. Python Model 程式碼

處理對 SQLite 資料庫的 CRUD (建立、讀取、更新、刪除) 操作邏輯，已實作於 `app/models/ingredient.py`，使用 Python 內建的 `sqlite3` 模組，保持系統輕量化。
# 隨食隨地 - 資料庫設計文件 (DB Design)

## 1. ER 圖（實體關係圖）

```mermaid
erDiagram
  USER ||--o{ PET : owns
  USER ||--o{ FEED_INVENTORY : has
  USER ||--o{ COOKING_RECORD : creates

  USER {
    int id PK
    string username
    string email
    datetime created_at
  }

  PET {
    int id PK
    int user_id FK
    string name
    int level
    int exp
    datetime updated_at
  }

  FEED_INVENTORY {
    int id PK
    int user_id FK
    int count
    datetime updated_at
  }

  COOKING_RECORD {
    int id PK
    int user_id FK
    string image_path
    string status
    datetime created_at
  }
```

## 2. 資料表詳細說明

### 2.1 USER (使用者表)
儲存系統使用者的基本資訊。
- `id` (INTEGER, PK): 使用者唯一識別碼
- `username` (VARCHAR, 必填): 使用者名稱
- `email` (VARCHAR, 必填, 唯一): 電子郵件
- `created_at` (DATETIME): 帳號建立時間

### 2.2 PET (虛擬寵物表)
儲存每位使用者的虛擬寵物狀態 (F-03)。
- `id` (INTEGER, PK): 寵物唯一識別碼
- `user_id` (INTEGER, FK): 關聯的使用者 ID
- `name` (VARCHAR, 必填): 寵物名稱
- `level` (INTEGER, 必填): 當前等級，預設 1
- `exp` (INTEGER, 必填): 當前經驗值，預設 0
- `updated_at` (DATETIME): 最後狀態更新時間

### 2.3 FEED_INVENTORY (飼料庫存表)
管理使用者透過回報料理獲得的虛擬飼料數量 (F-04)。
- `id` (INTEGER, PK): 庫存紀錄識別碼
- `user_id` (INTEGER, FK): 關聯的使用者 ID
- `count` (INTEGER, 必填): 飼料數量，預設 0
- `updated_at` (DATETIME): 庫存最後變動時間

### 2.4 COOKING_RECORD (烹飪紀錄表)
紀錄使用者回報的料理紀錄，用作發放飼料的依據 (F-04)。
- `id` (INTEGER, PK): 紀錄唯一識別碼
- `user_id` (INTEGER, FK): 關聯的使用者 ID
- `image_path` (VARCHAR, 可空): 上傳的料理圖片路徑
- `status` (VARCHAR, 必填): 紀錄狀態（如 'completed'）
- `created_at` (DATETIME): 紀錄提交時間
