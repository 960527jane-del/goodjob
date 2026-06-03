# 隨「食」隨地 — 系統流程圖 (Flowchart)

本文件基於 `docs/PRD.md` 與 `docs/ARCHITECTURE.md`，描繪「隨食隨地」系統的核心使用者旅程（User Journey）與系統運作流程，涵蓋食材管理、食譜推薦、虛擬寵物養成、進化圖鑑與烹飪回報。

---

## 1. 全域使用者流程圖 (User Flow)

描述使用者進入網站後，可以在各功能模組之間導覽與操作的完整路徑：

```mermaid
flowchart TD
    Start([使用者開啟網頁]) --> Home[首頁 - 我的材料庫]
    
    %% 模組 1：材料庫 (F-01/F-03)
    Home -->|點擊「新增」| F01_Add[填寫食材表單]
    F01_Add -->|確認新增| Home
    Home -->|點擊「編輯」| F01_Edit[修改食材庫存/效期]
    F01_Edit -->|確認更新| Home
    Home -->|點擊「刪除」| F01_Delete[確認移除食材]
    F01_Delete -->|確認刪除| Home
    Home -->|食材即將過期| F01_Warn[顯示過期警示標籤]:::action
    F01_Warn --> Home
    
    %% 模組 2：找靈感 (F-02)
    Home -->|點擊「找靈感」| F02_Page[食譜推薦頁面]
    F02_Page -->|查看推薦配方| F02_Detail[查看食譜詳情]
    F02_Detail -->|完成料理| F04_Page[上傳照片或直接勾選完成]
    F02_Detail -->|返回材料庫| Home
    
    %% 模組 3：虛擬寵物與餵食 (F-03/F-04)
    Home -->|點擊「虛擬寵物」| F03_Page[寵物互動頁面]
    F03_Page -->|點擊「手動餵食」| F03_FeedCheck{是否有飼料？}
    F03_FeedCheck -->|有| F03_Feed[扣除 1 個飼料並增加 20 EXP]
    F03_FeedCheck -->|無| F03_Warn[提示前往烹飪回報]
    F03_Feed --> F03_Update{是否達標升級/進化？}
    F03_Update -->|否| F03_Page
    F03_Update -->|是| F06_Evolve[解鎖新圖鑑並顯示進化彈窗]
    F06_Evolve --> F03_Page
    F03_Warn --> Home
    
    %% 模組 4：烹飪回報 (F-04)
    Home -->|點擊「烹飪回報」| F04_Page
    F04_Page -->|送出表單| F04_Record[寫入烹飪紀錄]
    F04_Record --> F04_Reward[獲得 1 份虛擬飼料獎勵]
    F04_Reward --> F03_Page
    
    %% 模組 5：寵物圖鑑 (F-06)
    Home -->|點擊「寵物圖鑑」| F06_Page[進化圖鑑主頁]
    F06_Page -->|篩選分類| F06_Filter[篩選屬性: 火/木/水等]
    F06_Filter --> F06_Grid[瀏覽圖鑑網格]
    F06_Grid -->|點擊已解鎖卡片| F06_Detail[查看型態詳情與風味說明]
    F06_Grid -->|點擊未解鎖卡片| F06_Lock[顯示剪影與解鎖條件]
    F06_Detail --> F06_Page
    F06_Lock --> F06_Page
```

---

## 2. 核心系統資料流程圖

此流程圖涵蓋 MVP 階段四大核心功能的系統邏輯：

```mermaid
flowchart TD
    classDef page fill:#f9f,stroke:#333,stroke-width:2px;
    classDef action fill:#bbf,stroke:#333,stroke-width:1px;
    classDef logic fill:#ff9,stroke:#333,stroke-width:1px;
    classDef db fill:#eee,stroke:#333,stroke-width:1px,stroke-dasharray: 5 5;

    Start([啟動 App / 首頁]) --> MainMenu{選擇功能模組}:::logic

    MainMenu -->|進入| InventoryPage[我的材料庫頁面]:::page
    InventoryPage --> CheckExpiry{檢查保存期限 F-03}:::logic
    CheckExpiry -->|即將過期| ShowWarning[顯示過期警示標籤]:::action
    CheckExpiry -->|正常| ShowList[顯示現有食材列表]:::action
    InventoryPage --> ActionInventory{選擇操作}:::logic
    ActionInventory -->|手動新增| AddIng[輸入食材名稱、數量、期限]:::action
    ActionInventory -->|編輯/刪除| EditIng[更新或刪除現有食材]:::action
    AddIng --> DB_Ing[(更新 Ingredient 資料表)]:::db
    EditIng --> DB_Ing

    MainMenu -->|進入| RecipePage[食譜推薦頁面]:::page
    RecipePage --> ReadDB_Ing[(讀取現有庫存)]:::db
    ReadDB_Ing --> MatchRecipe[比對食材與食譜資料]:::action
    MatchRecipe --> ShowRecipes[顯示推薦食譜列表]:::action
    ShowRecipes --> ViewDetail[點擊查看食譜詳細步驟]:::page

    ViewDetail -->|完成料理| CookingReport[進入烹飪回報介面]:::page
    CookingReport --> ChooseReport{選擇回報方式}:::logic
    ChooseReport -->|上傳圖片| UploadPhoto[手機拍照/相簿上傳]:::action
    ChooseReport -->|快速點擊| CheckDone[勾選確認完成]:::action
    UploadPhoto --> VerifyReport[系統發放「虛擬飼料」]:::action
    CheckDone --> VerifyReport
    VerifyReport --> DB_History[(寫入 Cooking_Records F-04)]:::db
    DB_History --> DB_Feed[(更新 FeedInventory 飼料庫存)]:::db

    MainMenu -->|進入| PetPage[虛擬寵物頁面]:::page
    DB_Feed -.->|即時反映庫存| PetPage
    PetPage --> FeedCheck{點擊餵食: 庫存 > 0 ?}:::logic
    FeedCheck -->|否| PromptCook[提示: 去做菜收集飼料吧！]:::action
    PromptCook -.-> RecipePage
    FeedCheck -->|是 AJAX| FeedAction[扣除飼料 增加寵物 EXP]:::action
    FeedAction --> ExpCheck{EXP 是否達升級/進化門檻?}:::logic
    ExpCheck -->|否| ShowExpAnim[播放進食與 +EXP 特效]:::action
    ExpCheck -->|是| ShowLevelUpAnim[播放寵物升級特效]:::action
    ShowLevelUpAnim --> EvoCheck{達到進化等級?}:::logic
    EvoCheck -->|是| EvoModal[顯示進化彈窗並解鎖圖鑑]:::action
    EvoCheck -->|否| ShowExpAnim
    ShowExpAnim --> DB_User_Exp[(更新 user_pets EXP/Level)]:::db
    ShowLevelUpAnim --> DB_User_Exp
    EvoModal --> DB_Collection[(寫入 user_collection)]:::db
```

---

## 3. 系統序列圖 (Sequence Diagrams)

### 3.1 食材管理功能 (F-01) — 手動新增食材

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器 (Frontend)
    participant Flask as Flask Route (Controller)
    participant Model as Ingredient Model
    participant DB as SQLite (Database)

    User->>Browser: 填寫食材名稱、數量、單位、效期，點擊「新增」
    Browser->>Flask: POST /ingredient/add 表單數據
    Flask->>Model: 呼叫 Ingredient.create(user_id, name, qty, unit, date)
    Model->>DB: 執行 INSERT INTO ingredients (...)
    DB-->>Model: 回傳成功
    Model-->>Flask: 回傳新增的 Ingredient 物件
    Flask-->>Browser: 302 重導向至首頁 (/)
    Browser->>Flask: GET /
    Flask->>Model: 查詢最新食材庫存列表 (Ingredient.get_by_user_id)
    Model->>DB: SELECT * FROM ingredients ORDER BY expiry_date
    DB-->>Model: 回傳食材清單
    Model-->>Flask: 傳回 Python List
    Flask-->>Browser: 渲染 HTML 網頁 (index.html)
    Browser-->>User: 看到最新食材庫存清單與有效期限
```

### 3.2 寵物養成與進化功能 (F-03/F-06) — 餵食與進化判定

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器 (AJAX / JS)
    participant Flask as Flask Route (pet_routes)
    participant ORM as FeedInventory Model
    participant Service as Evolution Service
    participant Model as Pet/Collection Model
    participant DB as SQLite (Database)

    User->>Browser: 點擊「手動餵食」按鈕
    Browser->>Flask: POST /pet/feed (AJAX 請求)
    Flask->>ORM: 查詢該使用者飼料庫存 (get_by_user_id)
    ORM-->>Flask: 回傳庫存 (count >= 1)
    
    Flask->>ORM: 呼叫 consume_feed(1) 扣除飼料
    ORM->>DB: UPDATE feed_inventories SET count = count - 1
    DB-->>ORM: 成功
    
    Flask->>Model: 獲取當前使用者的寵物 (Pet.get_by_user_id)
    Model->>DB: SELECT * FROM user_pets WHERE user_id = ?
    DB-->>Model: 回傳當前寵物資料 (Level, EXP, Stage)
    Model-->>Flask: 傳回寵物狀態字典
    
    Flask->>Service: 呼叫增加經驗值邏輯 (add_exp)
    Service->>Model: 更新經驗值與等級 (update_pet_level)
    
    alt Leveled Up (經驗值達標升級且符合進化門檻)
        Service->>Service: 檢查可進化的最高階段 (check_and_evolve)
        Service->>Model: 執行進化並更新當前階段 (update_pet_stage)
        Service->>Model: 解鎖新圖鑑項目 (unlock_stage)
        Model->>DB: INSERT INTO user_collection
        DB-->>Model: 成功
    end
    
    Service-->>Flask: 回傳進化與升級結果 (含新舊型態名稱、Emoji、是否進化)
    Flask-->>Browser: 回傳 JSON 結果 (含 updated_pet 與 remaining_feed)
    Note over Browser: 1. 更新 EXP、等級文字與飼料數量<br/>2. 進度條動畫增長<br/>3. 若進化，開啟 modal 展示特效
    Browser-->>User: 取得即時餵食互動與升級/進化之視覺回饋
```

### 3.3 智慧食譜推薦功能 (F-02)

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器 (Frontend)
    participant Flask as Flask Route (recipe.py)
    participant Model as Ingredient Model
    participant API as 外部食譜 API
    participant Template as Jinja2 Template (list.html)

    User->>Browser: 點擊「智慧食譜推薦」
    Browser->>Flask: GET /recipes
    Flask->>Model: 取得可用食材 (Ingredient.get_by_user_id)
    Model-->>Flask: 回傳食材清單 (例: 雞肉, 洋蔥, 番茄)
    Flask->>API: HTTP GET 請求 (帶入食材參數)
    API-->>Flask: 回傳推薦食譜 JSON 數據
    Flask->>Flask: 比對庫存並標示缺漏食材
    Flask->>Template: 傳入食譜資料渲染
    Template-->>Browser: 回傳 HTML
    Browser-->>User: 看到推薦食譜清單與烹飪資訊
```

### 3.4 烹飪回報與飼料發放 (F-04)

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器 (Frontend)
    participant Flask as Flask Route (cooking.py)
    participant Record as CookingRecord Model
    participant ORM as FeedInventory Model
    participant DB as SQLite (Database)

    User->>Browser: 上傳料理照片並點擊「完成送出」
    Browser->>Flask: POST /cooking/report (multipart/form-data)
    Flask->>Flask: 儲存上傳照片到 static/uploads
    Flask->>Record: 呼叫 CookingRecord.create(user_id, recipe_id, img_path)
    Record->>DB: INSERT INTO cooking_records
    DB-->>Record: 成功
    
    Flask->>ORM: 取得或建立使用者的 FeedInventory
    Flask->>ORM: 呼叫 add_feed(1) 增加 1 份飼料
    ORM->>DB: UPDATE feed_inventories SET count = count + 1
    DB-->>ORM: 成功
    
    Flask-->>Browser: 302 重導向至 /pet
    Browser->>User: 顯示「回報成功！獲得 1 份虛擬飼料！」並渲染最新寵物頁面
```

---

## 4. 功能清單與頁面對照表

| 功能編號 | 功能名稱 | HTTP 方法 | URL 路徑 | 渲染模板 / 回傳格式 | 說明 |
| :--- | :--- | :---: | :--- | :--- | :--- |
| **F-01** | 我的材料庫首頁 | `GET` | `/` | `ingredients/index.html` | 列出目前所有食材與新增食材表單 |
| **F-01** | 新增食材 | `POST` | `/ingredient/add` | 重導向至 `/` | 接收新增食材表單，寫入庫存後導回 |
| **F-01** | 編輯食材頁面 | `GET` | `/ingredient/edit/<id>` | `ingredients/edit.html` | 呈現單一食材修改表單 |
| **F-01** | 更新食材 | `POST` | `/ingredient/update/<id>`| 重導向至 `/` | 接收編輯欄位更新庫存後導回 |
| **F-01** | 刪除食材 | `POST` | `/ingredient/delete/<id>`| 重導向至 `/` | 刪除指定食材後導回 |
| **F-02** | 推薦食譜 | `GET` | `/recipes/recommend` | `recipes/recommend.html` | 根據現有材料推薦合適食譜 |
| **F-03** | 虛擬寵物首頁 | `GET` | `/pet` | `pet/index.html` | 呈現寵物數據、等級、餵食與進化觸發 |
| **F-03** | 手動餵食互動 | `POST` | `/pet/feed` | JSON | 檢查飼料庫存並扣除，加經驗值升級進化並回傳 |
| **F-04** | 烹飪回報頁面 | `GET` | `/cooking` | `cooking/index.html` | 顯示烹飪回報表單 |
| **F-04** | 提交烹飪紀錄 | `POST` | `/cooking/report` | 重導向至 `/pet` | 接收照片、新增紀錄、發放 1 份飼料 |
| **F-06** | 圖鑑主頁面 | `GET` | `/collection` | `collection/index.html` | 顯示所有寵物圖鑑與解鎖進度 |
| **F-06** | 型態詳情頁面 | `GET` | `/collection/<id>` | `collection/detail.html` | 查看單一進化階段型態之風味說明與關係圖 |

---

## 5. 流程設計亮點說明

1. **閉環機制 (Closed Loop)**：使用者從「管理食材」出發，透過「食譜推薦」消化食材，再經由「烹飪回報」獲取獎勵（虛擬飼料），最後至「寵物頁面」消耗獎勵獲得成就感。當飼料不足時，又會引導使用者回到食譜頁面，形成高黏著度的正向循環。
2. **進化圖鑑解鎖 (F-06)**：每當寵物達到進化等級門檻，除了寵物外觀改變外，圖鑑中對應的型態也會自動解鎖，提供使用者收集與探索的動力。
3. **防呆與引導**：在寵物頁面中，若虛擬飼料庫存不足，系統不會只顯示錯誤，而是設計明確的 CTA (Call To Action) 引導使用者去「做菜收集飼料」。
4. **無縫的使用者體驗**：在「餵食」流程中採用 AJAX 異步請求，讓前端特效（如 `+EXP` 動畫、進食動畫、進化 Modal）不會因為頁面重整而中斷。
