# 隨「食」隨地 — 系統架構文件 (System Architecture)

本文件詳細規劃並描述「隨「食」隨地」系統的軟體架構、目錄結構與各模組元件之職責分工。

---

## 1. 系統架構設計

本系統採用經典的 **MVC (Model-View-Controller)** 設計模式，並透過模組化（Modular Package）架構將不同功能單元解耦，以提升系統的擴充性與可維護性。

- **Model (資料庫模型)**：集中於 `app/models/`，負責處理食材與寵物的資料庫讀寫及 CRUD 邏輯。
- **View (視圖與呈現)**：集中於 `app/templates/`，使用 Flask Jinja2 模板，搭配 `app/static/` 中的 CSS/JS，呈現使用者介面。
- **Controller (控制器/路由)**：集中於 `app/routes/`，定義 API 與頁面路由，負責接收請求並協調 Model 與 View。
- **Service (服務層)**：集中於 `app/services/`，處理複雜的核心業務邏輯（如：寵物升級與進化的邏輯計算）。

---

## 2. 目錄結構規劃

以下為整個專案的整合目錄結構，所有主要邏輯皆集中於 `app/` 套件目錄下：

```text
goodjob/
├── app/                        # 應用程式主要套件目錄
│   ├── database.py             # 資料庫連線管理與初始化工具
│   │
│   ├── models/                 # [Model] 資料庫存取與邏輯層
│   │   ├── __init__.py
│   │   ├── ingredient.py       # 食材管理 Model (F-01)
│   │   ├── pet.py              # 寵物狀態與 CRUD Model (F-03/F-06)
│   │   └── collection.py       # 寵物圖鑑資料 CRUD Model (F-06)
│   │
│   ├── routes/                 # [Controller] 路由與 API 端點
│   │   ├── __init__.py
│   │   ├── ingredient.py       # 食材管理路由 (F-01)
│   │   ├── recipe.py           # 食譜推薦路由 (F-02)
│   │   ├── pet_routes.py       # 虛擬寵物養成路由 (F-03)
│   │   └── collection_routes.py# 寵物圖鑑與進化 API 路由 (F-06)
│   │
│   ├── services/               # [Service] 核心業務邏輯服務層
│   │   └── evolution_service.py# 寵物經驗值計算與進化引擎 (F-06)
│   │
│   ├── templates/              # [View] Jinja2 HTML 模板
│   │   ├── base.html           # 全站統一的 Glassmorphism 共用版型
│   │   ├── ingredients/
│   │   │   ├── index.html      # 我的材料庫首頁 (F-01)
│   │   │   └── edit.html       # 食材編輯頁面 (F-01)
│   │   ├── recipes/
│   │   │   └── recommend.html  # 食譜推薦展示頁 (F-02)
│   │   ├── pet/
│   │   │   └── index.html      # 虛擬寵物互動頁面 (F-03)
│   │   ├── collection/
│   │   │   ├── index.html      # 寵物圖鑑展示頁面 (F-06)
│   │   │   └── detail.html     # 寵物階段詳情頁面 (F-06)
│   │   └── components/
│   │       └── evolution_modal.html # 進化動畫彈窗組件
│   │
│   └── static/                 # 靜態資源 (CSS, JS, 圖片)
│       ├── css/
│       │   ├── style.css       # 共用樣式表
│       │   └── collection.css  # 圖鑑專屬樣式表
│       └── js/
│           └── collection.js   # 圖鑑與進化互動 JS 腳本
│
├── database/
│   └── schema.sql              # 統一 SQLite 建表語法與種子資料
│
├── instance/
│   └── database.db             # 運行時生成的 SQLite 資料庫檔案
│
├── docs/                       # 系統說明文件
│   ├── PRD.md
│   ├── ARCHITECTURE.md         # 本文件
│   ├── DB_DESIGN.md
│   ├── FLOWCHART.md
│   └── ROUTES.md
│
├── app.py                      # Flask 專案唯一啟動入口
├── config.py                   # 專案全局設定檔
├── init_db.py                  # 資料庫初始化腳本
└── requirements.txt            # Python 套件依賴清單
```

---

## 3. 元件關係與資料流向

以下 sequence diagram 展示了以「手動餵食寵物並觸發進化」為例的系統資料流向：

```mermaid
sequenceDiagram
    participant Browser as 瀏覽器 (Frontend)
    participant Route as Flask Route (Controller)
    participant Service as Evolution Service (Logic)
    participant Model as Pet Model (Data layer)
    participant DB as SQLite Database

    Browser->>Route: POST /pet/feed 請求
    Route->>Model: 查詢當前寵物狀態 (get_pet_by_user)
    Model->>DB: 查詢 user_pets
    DB-->>Model: 回傳寵物數據
    Model-->>Route: 傳回寵物狀態字典
    
    Route->>Service: 呼叫增加經驗值邏輯 (add_exp)
    Note over Service: 計算新等級與餘額<br/>判斷是否升級
    Service->>Model: 更新資料庫 (update_pet_level)
    
    optLeveled Up (觸發升級與進化)
        Service->>Service: 檢查並進化 (check_and_evolve)
        Service->>Model: 更新當前進化階段 (update_pet_stage)
        Service->>Model: 解鎖新階段圖鑑 (unlock_stage)
    end
    
    Service-->>Route: 傳回包含升級與進化結果的字典
    Route-->>Browser: 回傳 JSON 結果
    Note over Browser: 增長進度條與更新文字<br/>若有進化，展示進化彈窗動畫
```

---

## 4. 關鍵架構決策

1. **模組化 Package 架構 (`app/` 目錄)**
   - **優勢**：相較於單一檔案結構，預先進行模組化規劃可以防止程式碼隨功能增加而失控，確保食材管理、食譜推薦、虛擬寵物與圖鑑系統能各自獨立開發、測試，不互相干擾。

2. **統一的資料庫存取層 (SQLite + `sqlite3.Row`)**
   - **優勢**：在 MVP 階段不使用複雜的 ORM (如 SQLAlchemy)，保持連線輕量；透過設定 `conn.row_factory = sqlite3.Row` 讓查詢結果能以 Dict 方式存取，既保留了 SQL 的靈活性，又方便前端模板直接調用。

3. **統一的 Request-Scoped 連線生命週期管理**
   - **優勢**：使用 Flask 的 `g` 物件管理資料庫連線生命週期，搭配 `teardown_appcontext` 在每次 HTTP 請求結束時自動關閉連線，能徹底防止資料庫連線洩漏 (Connection Leak) 與併發鎖定問題。
