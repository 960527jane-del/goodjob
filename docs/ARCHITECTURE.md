# 隨食隨地 - 系統架構設計

本文件根據功能需求 (包含虛擬寵物養成系統 F-03) 規劃了專案的技術架構與資料夾結構。

## 1. 技術架構說明

本專案採用輕量級的後端渲染架構，不採取前後端分離，以求快速開發與迭代。

- **後端框架：Python + Flask**
  - **原因**：Flask 輕量且極具彈性，非常適合用來快速建立如「隨食隨地」這樣的中小型應用程式。
  - **Controller 職責**：Flask 路由負責接收來自使用者的 HTTP 請求 (如：餵食請求、查看頁面)，並進行商業邏輯計算 (例如計算新的經驗值)。
- **模板引擎：Jinja2**
  - **原因**：內建於 Flask 中，能夠直接將後端資料 (如寵物等級、經驗值) 注入到 HTML 頁面中一起渲染給使用者。
  - **View 職責**：負責定義與渲染使用者看到的介面結構。
- **資料庫：SQLite**
  - **原因**：無需額外架設資料庫伺服器，資料直接儲存在本機檔案 (`.db`) 中，十分輕巧，適合 MVP 開發階段。
  - **Model 職責**：負責與 SQLite 溝通，進行資料的寫入 (如更新經驗值) 與讀取 (如取得當前等級)。

## 2. 專案資料夾結構

建議的資料夾樹狀圖如下：

```text
goodjob/
│
├── app/                  # 主要的應用程式邏輯
│   ├── __init__.py       # 初始化 Flask 應用程式與設定
│   ├── models/           # 資料庫模型 (與 SQLite 溝通)
│   │   └── pet.py        # 寵物相關的資料表結構與操作函數
│   ├── routes/           # Flask 路由控制器 (Controller)
│   │   └── pet_routes.py # 處理 `/pet` 與 `/api/pet/feed` 相關請求
│   ├── templates/        # Jinja2 HTML 模板 (View)
│   │   └── pet/
│   │       └── index.html# 寵物專屬頁面
│   └── static/           # CSS、JS 與圖片等靜態資源
│       ├── css/
│       │   └── style.css # 網頁樣式 (包含進度條與微動畫)
│       ├── js/
│       │   └── pet.js    # 處理前端餵食按鈕事件與動畫
│       └── images/       # 寵物不同等級的圖片素材
│
├── instance/             # 存放不應加入版控的本機資料
│   └── database.db       # SQLite 實體資料庫檔案
│
├── docs/                 # 專案文件 (PRD, 架構圖, 流程圖)
│
├── app.py                # 應用程式啟動入口
└── requirements.txt      # Python 套件相依清單
```

## 3. 元件關係圖

以下是整個系統在處理使用者請求時，各個元件如何互動的架構圖：

```mermaid
graph TD
    User([使用者瀏覽器])
    
    subgraph 隨食隨地 Flask 應用程式
        Controller[Flask Route\n(Controller)]
        Template[Jinja2 Template\n(View)]
        Model[Database Model\n(Model)]
    end
    
    DB[(SQLite 資料庫)]

    %% 讀取頁面流程
    User -- "1. 發送 GET /pet" --> Controller
    Controller -- "2. 查詢當前狀態" --> Model
    Model -- "3. SELECT pet" --> DB
    DB -- "4. 回傳資料" --> Model
    Model -- "5. 狀態資料" --> Controller
    Controller -- "6. 注入資料並渲染" --> Template
    Template -- "7. 回傳完整 HTML" --> User
    
    %% 餵食互動流程
    User -- "A. 發送 POST /api/pet/feed" -.-> Controller
    Controller -- "B. 更新經驗值" -.-> Model
    Model -- "C. UPDATE pet" -.-> DB
    DB -.-> Model
    Model -.-> Controller
    Controller -- "D. 回傳 JSON 結果" -.-> User
```

## 4. 關鍵設計決策

1. **採用 SSR (伺服器端渲染) 搭配部分前端 Ajax**
   - **原因**：主要頁面使用 Jinja2 渲染，降低初期開發複雜度；但針對「餵食」按鈕這種需要即時互動且不重新整理頁面的操作，使用前端 JS 呼叫 API 並動態更新進度條，以確保流暢的「遊戲體驗」。
2. **輕量化資料庫選擇 (SQLite)**
   - **原因**：目前為 MVP 階段，不需要複雜的權限或大型併發連線，使用 SQLite 可大幅減少團隊設定環境的時間，且未來若需升級至 PostgreSQL 或 MySQL 也相對容易。
3. **資料夾依職責切割 (MVC)**
   - **原因**：將 `models`, `routes`, `templates` 拆分在不同的資料夾中，能讓負責前端與後端的組員互不干擾，方便後續擴充其他功能（如新增食譜功能）。
