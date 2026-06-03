# 隨「食」隨地 — 系統架構文件 (System Architecture)

本文件詳細規劃並描述「隨「食」隨地」系統（特別是針對 F-06 寵物進化圖鑑功能）的軟體架構、目錄結構、元件職責與關鍵設計決策。

---

## 1. 技術架構說明

本系統採用經典的 **MVC (Model-View-Controller)** 設計模式，配合服務層（Service Layer）來處理複雜的業務邏輯。此架構能有效解耦資料、呈現與控制邏輯，提升系統的擴充性與可維護性。

### 1.1 技術選型與原因

*   **後端框架：Python + Flask**
    *   *選用原因*：Flask 是一款輕量級且高度靈活的微型框架（Micro-framework），非常適合 MVP 階段快速開發與迭代，且能輕易融入模組化設計。
*   **前端渲染：Jinja2 模板引擎**
    *   *選用原因*：Jinja2 是 Flask 預設的模板引擎，支持在 HTML 中動態插入後端數據與渲染邏輯。採用「伺服器端渲染 (SSR)」免去了維護繁雜的前後端分離專案的成本，極適合小規模協作與快速成型。
*   **資料庫：SQLite**
    *   *選用原因*：SQLite 是無伺服器（Serverless）的輕量級關聯式資料庫，所有數據均存在本地單一檔案中，無需額外安裝與設定資料庫服務，非常便於協作開發與快速部署。
*   **前端邏輯：HTML5 + CSS3 + JavaScript (Vanilla JS)**
    *   *選用原因*：不依賴大型前端框架（如 React/Vue），使用原生 CSS 與 JavaScript 實作 Glassmorphism（毛玻璃效果）的 UI 風格與進化動畫，降低系統複雜度並提高載入效能。

### 1.2 Flask MVC 模式說明

*   **Model (資料模型層)**：
    *   位於 `app/models/`，負責直接存取 SQLite 資料庫，定義資料表存取邏輯（如 `Ingredient`、`Pet`、`Collection` 的 CRUD 運作），並封裝資料校驗規則。
*   **View (視圖呈現層)**：
    *   位於 `app/templates/` 與 `app/static/`，使用 HTML5/Jinja2 模板與 CSS 決定使用者的視覺界面，配合 JavaScript 處理前端互動與動畫（如圖鑑卡片翻面、進化光效）。
*   **Controller (控制器/路由層)**：
    *   位於 `app/routes/`，定義系統的所有 HTTP 路由與 API端點，負責接收使用者請求、調用對應的 Model 或 Service 處理資料，最後決定要渲染哪個 Jinja2 模板或返回 JSON 數據。
*   **Service (服務層 - 額外擴充)**：
    *   位於 `app/services/`，當業務邏輯過於複雜（例如進化條件判定與經驗值跳級計算）不適合寫在 Controller 或 Model 中時，將其提取至 Service 層（如 `EvolutionService`）進行統一封裝，保持 Controller 的簡潔度。

---

## 2. 專案資料夾結構

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
│       ├── js/
│       │   └── collection.js   # 圖鑑與進化互動 JS 腳本
│       └── images/
│           └── pets/           # 儲存寵物進化各階段的圖片
│
├── database/
│   └── schema.sql              # 統一 SQLite 建表語法與種子資料
│
├── instance/
│   └── database.db             # 運行時生成的 SQLite 資料庫檔案
│
├── docs/                       # 系統說明文件
│   ├── PRD.md                  # 專案需求文件
│   ├── ARCHITECTURE.md         # 本系統架構文件
│   ├── DB_DESIGN.md            # 資料庫設計文件
│   ├── FLOWCHART.md            # 使用者與系統流程圖
│   └── ROUTES.md               # 路由與 API 設計文件
│
├── app.py                      # Flask 專案唯一啟動入口
├── config.py                   # 專案全局設定檔
├── init_db.py                  # 資料庫初始化腳本
└── requirements.txt            # Python 套件依賴清單
```

---

## 3. 元件關係與資料流向

以下展示使用者在瀏覽器操作系統時，前後端與資料庫的關鍵資料流向：

### 3.1 頁面渲染資料流 (SSR)
當使用者要求瀏覽圖鑑頁面時：

```mermaid
sequenceDiagram
    participant Browser as 瀏覽器 (Frontend)
    participant Route as Flask Route (Controller)
    participant Model as Collection Model
    participant DB as SQLite Database
    participant Template as Jinja2 Template (View)

    Browser->>Route: GET /collection 請求
    Route->>Model: 查詢使用者已解鎖的圖鑑 (get_unlocked_stages)
    Model->>DB: SELECT user_collection JOIN pet_stages
    DB-->>Model: 回傳資料庫記錄
    Model-->>Route: 傳回 Python Dict 列表
    Route->>Template: 傳入圖鑑清單資料進行渲染
    Template-->>Route: 生成包含動態數據的 HTML 原始碼
    Route-->>Browser: 回傳 200 OK 網頁內容
    Note over Browser: 渲染 Glassmorphism 卡片網格
```

### 3.2 異步 API 資料流 (AJAX)
當使用者在寵物養成頁面點擊「手動餵食」觸發經驗值變更並判定進化時：

```mermaid
sequenceDiagram
    participant Browser as 瀏覽器 (Frontend JS)
    participant Route as Flask Route (Controller)
    participant Service as Evolution Service (Logic)
    participant Model as Pet Model
    participant DB as SQLite Database

    Browser->>Route: POST /api/pet/evolve (或 /pet/feed) 請求 (AJAX)
    Route->>Model: 取得當前寵物狀態 (get_pet_by_user)
    Model->>DB: SELECT * FROM user_pets
    DB-->>Model: 回傳寵物原始數據
    Model-->>Route: 傳回寵物 Dict
    
    Route->>Service: 呼叫進化判定與計算 (check_and_evolve)
    Note over Service: 1. 累加經驗值並判定是否升級<br/>2. 判斷是否達到進化等級門檻<br/>3. 計算出新的進化階段 ID
    
    alt 觸發升級/進化
        Service->>Model: 更新等級與進化階段 (update_pet_stage)
        Service->>Model: 寫入圖鑑解鎖紀錄 (unlock_stage)
        Model->>DB: INSERT INTO user_collection
        DB-->>Model: 成功
    end
    
    Service-->>Route: 回傳進化計算結果 (含新舊外觀、Emoji、是否進化標記)
    Route-->>Browser: 回傳 JSON 結果
    Note over Browser: 1. 動態更新進度條與數值<br/>2. 若進化標記為真，播放進化光效 Modal
```

---

## 4. 關鍵設計決策

1.  **模組化 Package 架構 (`app/` 目錄)**
    *   *原因*：相較於將所有代碼塞在單一 `app.py` 中，將專案預先進行模組化規劃（分為 `models`、`routes`、`templates` 等）能有效防止程式碼隨功能增加而失控，確保食材管理、食譜推薦、虛擬寵物與圖鑑系統能各自獨立開發、測試，不互相干擾。
2.  **核心邏輯抽離至服務層 (Service Layer)**
    *   *原因*：寵物進化判定與經驗值（EXP）跳級更新屬於複雜的業務邏輯，將其獨立封裝於 `app/services/evolution_service.py` 中。這能讓控制器（Routes）保持簡潔，僅負責處理請求與響應，且服務層邏輯可以被不同的 Route（如餵食、烹飪完成、日常登入等）重複調用，提高程式碼重用性。
3.  **無 ORM 的輕量化資料庫存取層**
    *   *原因*：在 MVP 階段，為了維持系統的高效與輕量，不使用大型 ORM（如 SQLAlchemy），而是透過 Python 原生 `sqlite3`。搭配設定 `conn.row_factory = sqlite3.Row` 使查詢結果能以類字典（Dict）方式存取，既保留了寫原生 SQL 的靈活性，又極大方便了 Jinja2 模板直接調用屬性。
4.  **連線生命週期管理 (Request-Scoped Connection)**
    *   *原因*：在 `app/database.py` 中使用 Flask 的 `g` 全局變數管理資料庫連線，並利用 `teardown_appcontext` 在每次 HTTP 請求結束時自動關閉連線。這能確保資料庫連線不洩漏，有效防範併發寫入時可能引發的 SQLite `database is locked` 異常。
5.  **前台非同步互動 (AJAX + JSON)**
    *   *原因*：傳統 SSR 在每次使用者餵食寵物時都需要重新載入整個頁面，會造成糟糕的遊戲體驗。透過前台發送 AJAX 請求，後端返回輕量的 JSON 格式數據，前台 JavaScript 接收後進行局部 UI 更新（如進度條增加、文字變更、進化 Modal 彈出），在保持 SSR 開發便利的同時，獲得極佳的 SPA（單頁應用）流暢互動感。
