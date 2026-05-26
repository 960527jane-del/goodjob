# 隨「食」隨地 — 使用者流程圖與系統流程圖 (Flowchart)

本文件使用 Mermaid 流程圖，視覺化隨食隨地系統中各功能模組（食材管理、虛擬寵物養成、進化圖鑑）的使用者操作路徑與系統內部資料流。

---

## 1. 全域使用者流程圖 (User Flow)

描述使用者登入網站後，可在各模組之間切換與操作的路徑：

```mermaid
flowchart TD
    Start([使用者登入系統]) --> Home[首頁 - 我的材料庫]
    
    %% 模組 1：材料庫
    Home --> F01_Action{選擇食材操作？}
    F01_Action -->|新增/編輯/刪除| F01_Process[新增食材、調整數量、設定過期日]
    F01_Process --> Home
    
    %% 模組 2：找靈感
    Home -->|點擊「找靈感」| F02_Page[食譜推薦頁面]
    F02_Page -->|查看配方| Home
    
    %% 模組 3：虛擬寵物
    Home -->|點擊「虛擬寵物」| F03_Page[寵物互動養成頁面]
    F03_Page --> F03_Action{選擇互動？}
    F03_Action -->|手動餵食| F03_Feed[發送餵食請求，增加經驗值]
    F03_Feed --> F03_LevelUp{是否升級？}
    F03_LevelUp -->|否| F03_Page
    F03_LevelUp -->|是| F03_Evolve{是否達到進化門檻？}
    F03_Evolve -->|否| F03_Page
    F03_Evolve -->|是| F06_Evolve[觸發進化動畫，解鎖圖鑑型態]
    F06_Evolve --> F03_Page
    
    %% 模組 4：寵物圖鑑
    Home -->|點擊「寵物圖鑑」| F06_Page[進化圖鑑主頁面]
    F06_Page -->|篩選種族| F06_Grid[篩選顯示全部、小食怪、焰靈龍、鮮綠兔]
    F06_Grid -->|點擊卡片| F06_Detail[查看已解鎖或未解鎖階段詳情與進化樹]
    F06_Detail --> F06_Page
```

---

## 2. 系統互動序列圖 (Sequence Diagrams)

### 2.1 食材管理功能 (F-01) — 手動新增食材
展示瀏覽器前端與 Flask 後端、資料庫的模型交互：

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器 (Frontend)
    participant Flask as Flask Route (Controller)
    participant Model as Ingredient Model
    participant DB as SQLite (Database)

    User->>Browser: 填寫食材名稱、數量、效期，點擊「新增」
    Browser->>Flask: POST /ingredient/add 表單數據
    Flask->>Model: 呼叫 Ingredient.create(name, qty, unit, date)
    Model->>DB: 執行 INSERT INTO ingredients (...)
    DB-->>Model: 回傳成功
    Model-->>Flask: 回傳 lastrowid
    Flask-->>Browser: 302 重導向至首頁 (/)
    Browser->>Flask: GET /
    Flask->>Model: 查詢所有食材 (Ingredient.get_all)
    Model->>DB: SELECT * FROM ingredients
    DB-->>Model: 回傳食材清單
    Model-->>Flask: 傳回 Python Dict 列表
    Flask-->>Browser: 渲染 HTML 網頁
    Browser-->>User: 看到最新食材庫存清單
```

---

### 2.2 寵物養成與進化功能 (F-03/F-06) — 手動餵食與自動進化
展示餵食時，前端非同步 AJAX 與後端自動經驗計算、進化解鎖的關聯：

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器 (AJAX / JS)
    participant Flask as Flask Route (pet_routes)
    participant Service as Evolution Service
    participant Model as Pet/Collection Model
    participant DB as SQLite (Database)

    User->>Browser: 點擊「手動餵食」按鈕
    Browser->>Flask: POST /pet/feed (AJAX)
    Flask->>Model: 獲取當前寵物 (Pet.get_by_user_id)
    Model->>DB: SELECT * FROM user_pets WHERE user_id = 1
    DB-->>Model: 回傳當前寵物資料 (Level, EXP, Stage)
    Model-->>Flask: 傳回寵物 Dict
    
    Flask->>Service: 呼叫增加經驗值 (add_exp)
    Service->>Model: 更新經驗值與等級 (update_pet_level)
    
    alt Leveled Up (經驗值達標升級)
        Service->>Service: 檢查可進化的最高階段 (check_and_evolve)
        Service->>Model: 執行進化並更新階段 (update_pet_stage)
        Service->>Model: 解鎖新圖鑑項目 (unlock_stage)
        Model->>DB: INSERT INTO user_collection
        DB-->>Model: 成功
    end
    
    Service-->>Flask: 回傳進化與升級結果 (含新舊型態名稱、Emoji、圖鑑描述)
    Flask-->>Browser: 回傳 JSON 結果
    Note over Browser: 1. 更新經驗值與等級文字<br/>2. 進度條動畫增長<br/>3. 若進化，開啟 modal 展示特效
    Browser-->>User: 取得即時餵食互動與升級/進化之視覺回饋
```
