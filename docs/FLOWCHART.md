# 隨「食」隨地 — 使用者流程圖與系統流程圖 (Flowchart)

本文件使用 Mermaid 流程圖與序列圖，視覺化「隨食隨地」系統中各功能模組（食材管理、食譜推薦、虛擬寵物養成、進化圖鑑、烹飪回報）的使用者操作路徑與系統內部資料流。

---

## 1. 全域使用者流程圖 (User Flow)

描述使用者進入網站後，可以在各功能模組之間導覽與操作的完整路徑：

```mermaid
flowchart TD
    Start([使用者開啟網頁]) --> Home[首頁 - 我的材料庫]
    
    %% 模組 1：材料庫 (F-01)
    Home -->|點擊「新增」| F01_Add[填寫食材表單]
    F01_Add -->|確認新增| Home
    Home -->|點擊「編輯」| F01_Edit[修改食材庫存/效期]
    F01_Edit -->|確認更新| Home
    Home -->|點擊「刪除」| F01_Delete[確認移除食材]
    F01_Delete -->|確認刪除| Home
    
    %% 模組 2：找靈感 (F-02)
    Home -->|點擊「找靈感」| F02_Page[食譜推薦頁面]
    F02_Page -->|查看推薦配方| F02_Detail[查看食譜詳情]
    F02_Detail -->|返回材料庫| Home
    
    %% 模組 3：虛擬寵物與餵食 (F-03, F-04)
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
    Home -->|點擊「烹飪回報」| F04_Page[上傳照片或直接勾選完成]
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

## 2. 系統序列圖 (Sequence Diagrams)

### 2.1 食材管理功能 (F-01) — 手動新增食材
展示使用者新增食材時，前端瀏覽器與後端 Flask、資料庫 Model 的典型交互：

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器 (Frontend)
    participant Flask as Flask Route (Controller)
    participant Model as Ingredient Model
    participant DB as SQLite (Database)

    User->>Browser: 填寫食材名稱、數量、單位、效期，點擊「新增」
    Browser->>Flask: POST /ingredient/add 表單數據
    Flask->>Model: 呼叫 Ingredient.create(name, qty, unit, date)
    Model->>DB: 執行 INSERT INTO ingredients (...)
    DB-->>Model: 回傳成功
    Model-->>Flask: 回傳最後一筆插入的 id
    Flask-->>Browser: 302 重導向至首頁 (/)
    Browser->>Flask: GET /
    Flask->>Model: 查詢最新食材庫存列表 (Ingredient.get_all)
    Model->>DB: SELECT * FROM ingredients ORDER BY expiry_date
    DB-->>Model: 回傳食材清單
    Model-->>Flask: 傳回 Python Dict 列表
    Flask-->>Browser: 渲染 HTML 網頁 (index.html)
    Browser-->>User: 看到最新食材庫存清單與有效期限
```

### 2.2 寵物養成與進化功能 (F-03/F-06) — 餵食與進化判定
展示餵食時，前端發送非同步 AJAX 請求，後端檢查/扣除飼料庫存，並調用 Service 層進行經驗計算與進化圖鑑解鎖的資料流：

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
    Model->>DB: SELECT * FROM user_pets WHERE user_id = 1
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
    
    Service-->>Flask: 回傳進化與升級結果 (含新舊型態名稱、圖片、是否進化)
    Flask-->>Browser: 回傳 JSON 結果 (含 updated_pet 與 remaining_feed)
    Note over Browser: 1. 更新經驗值、等級文字與飼料數量<br/>2. 進度條動畫增長<br/>3. 若進化，開啟 modal 展示特效
    Browser-->>User: 取得即時餵食互動與升級/進化之視覺回饋
```

### 2.3 智慧食譜推薦功能 (F-02)
展示使用者點擊推薦食譜時，系統如何讀取食材庫存並呼叫外部 API 的流向：

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
    Flask->>Model: 取得可用食材 (Ingredient.get_all)
    Model-->>Flask: 回傳食材清單 (例: 雞肉, 洋蔥, 番茄)
    Flask->>API: HTTP GET 請求 (帶入食材參數)
    API-->>Flask: 回傳推薦食譜 JSON 數據
    Flask->>Flask: 比對庫存並標示缺漏食材
    Flask->>Template: 傳入食譜資料渲染
    Template-->>Browser: 回傳 HTML
    Browser-->>User: 看到推薦食譜清單與烹飪資訊
```

### 2.4 烹飪回報與飼料發放 (F-04)
展示使用者回報烹飪完成時，系統建立烹飪紀錄並發放飼料的流向：

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
    Flask->>Record: 呼叫 CookingRecord.create(user_id, img_path)
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

## 3. 功能清單與頁面對照表

| 功能編號 | 功能名稱 | HTTP 方法 | URL 路徑 | 渲染模板 / 回傳格式 | 說明 |
| :--- | :--- | :---: | :--- | :--- | :--- |
| **F-01** | 我的材料庫首頁 | `GET` | `/` | `ingredients/index.html` | 列出目前所有食材與新增食材表單 |
| **F-01** | 新增食材 | `POST` | `/ingredient/add` | 重導向至 `/` | 接收新增食材表單，寫入庫存後導回 |
| **F-01** | 編輯食材頁面 | `GET` | `/ingredient/edit/<id>` | `ingredients/edit.html` | 呈現單一食材修改表單 |
| **F-01** | 更新食材 | `POST` | `/ingredient/update/<id>`| 重導向至 `/` | 接收編輯欄位更新庫存後導回 |
| **F-01** | 刪除食材 | `POST` | `/ingredient/delete/<id>`| 重導向至 `/` | 刪除指定食材後導回 |
| **F-02** | 推薦食譜 | `GET` | `/recipes/recommend` | `recipes/recommend.html` | 根據現有材料推薦合適食譜 (Skeleton) |
| **F-03** | 虛擬寵物首頁 | `GET` | `/pet` | `pet/index.html` | 呈現寵物數據、等級、餵食與進化觸發 |
| **F-03** | 手動餵食互動 | `POST` | `/pet/feed` | JSON | 檢查飼料庫存並扣除，加經驗值升級進化並回傳 |
| **F-04** | 烹飪回報頁面 | `GET` | `/cooking` | `cooking/index.html` | 顯示烹飪回報表單 |
| **F-04** | 提交烹飪紀錄 | `POST` | `/cooking/report` | 重導向至 `/pet` | 接收照片、新增紀錄、發放 1 份飼料 |
| **F-06** | 圖鑑主頁面 | `GET` | `/collection` | `collection/index.html` | 顯示所有寵物圖鑑與解鎖進度 |
| **F-06** | 型態詳情頁面 | `GET` | `/collection/<id>` | `collection/detail.html` | 查看單一進化階段型態之風味說明與關係圖 |
