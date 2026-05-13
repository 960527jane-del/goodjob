# 系統與使用者流程圖 - 智慧食譜推薦系統 (F-02)

本文件依據 `docs/PRD_F02_智慧食譜推薦系統.md` 與 `docs/ARCHITECTURE.md`，視覺化「智慧食譜推薦系統」的使用者操作路徑與系統內部的資料流動。

## 1. 使用者流程圖（User Flow）

描述使用者從進入系統到查看詳細食譜的完整操作路徑。

```mermaid
flowchart LR
    A([使用者進入系統]) --> B[首頁 / 導覽列]
    B --> C[點擊「智慧食譜推薦」]
    
    C --> D{系統處理中}
    D --> |1. 讀取我的材料庫\n2. 呼叫外部 API| E[食譜推薦列表頁]
    
    E --> F{使用者選擇動作}
    F -->|瀏覽清單| E
    F -->|點擊特定食譜| G[食譜詳細資訊頁]
    
    G --> H{詳細頁操作}
    H -->|查看烹飪步驟| I([準備開始烹飪])
    H -->|檢視缺漏食材| J([將缺漏食材加入採買清單 - 未來擴充])
    H -->|返回列表| E
```

## 2. 系統序列圖（Sequence Diagram）

描述使用者點擊「智慧食譜推薦」時，系統背後與資料庫及外部 API 溝通的完整流程。

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器
    participant Flask as Flask Route (recipe.py)
    participant Model as SQLite DB (我的材料庫)
    participant API as 外部食譜 API
    
    User->>Browser: 點擊「智慧食譜推薦」選單
    Browser->>Flask: GET /recipes
    
    rect rgb(240, 248, 255)
        Note over Flask, Model: 步驟 1: 取得現有食材
        Flask->>Model: 查詢使用者目前庫存的食材
        Model-->>Flask: 回傳食材清單 (例: 雞肉、洋蔥、番茄)
    end
    
    rect rgb(240, 255, 240)
        Note over Flask, API: 步驟 2: 請求推薦食譜
        Flask->>API: HTTP GET 請求 (帶入食材關鍵字)
        API-->>Flask: 回傳推薦食譜 JSON 資料
    end
    
    rect rgb(255, 245, 238)
        Note over Flask, Browser: 步驟 3: 資料處理與渲染
        Flask->>Flask: 解析 JSON，比對現有庫存標示缺漏食材
        Flask-->>Browser: 渲染 recipe/list.html
    end
    
    Browser-->>User: 顯示推薦食譜列表
    
    User->>Browser: 點擊特定食譜查看詳細內容
    Browser->>Flask: GET /recipes/{recipe_id}
    Flask->>API: HTTP GET /recipes/{recipe_id}/information (取得步驟)
    API-->>Flask: 回傳詳細食譜資料與營養資訊
    Flask-->>Browser: 渲染 recipe/detail.html
    Browser-->>User: 顯示完整的食譜圖文教學與配料清單
```

## 3. 功能清單對照表

以下為本功能規劃的頁面與對應的 URL 路徑、HTTP 方法及模板：

| 功能項目 | HTTP 方法 | URL 路徑 | 負責的 View (Template) | 說明 |
| :--- | :---: | :--- | :--- | :--- |
| **推薦食譜列表** | `GET` | `/recipes` | `recipe/list.html` | 讀取「我的材料庫」，呼叫外部食譜 API，顯示推薦清單與烹飪時間 |
| **食譜詳細頁面** | `GET` | `/recipes/<int:recipe_id>` | `recipe/detail.html` | 透過食譜 ID 呼叫 API，顯示詳細烹飪步驟、完整配料表與缺漏食材對比 |
