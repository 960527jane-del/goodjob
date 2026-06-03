# 隨「食」隨地 — 使用者流程圖與系統流程圖 (Flowchart)

本文件使用 Mermaid 流程圖與序列圖，視覺化「隨食隨地」系統中各功能模組（食材管理、食譜推薦、虛擬寵物養成、進化圖鑑）的使用者操作路徑與系統內部資料流。

---

## 1. 全域使用者流程圖 (User Flow)

描述使用者進入網站後，可以在各功能模組之間導覽與操作的完整路徑：

```mermaid
flowchart LR
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
    
    %% 模組 3：虛擬寵物 (F-03)
    Home -->|點擊「虛擬寵物」| F03_Page[寵物互動養成頁面]
    F03_Page -->|點擊「手動餵食」| F03_Feed[發送餵食 API 請求]
    F03_Feed --> F03_Update{是否升級/進化？}
    F03_Update -->|否：僅增加經驗值| F03_Page
    F03_Update -->|是：觸發進化門檻| F06_Evolve[顯示進化特效與動畫彈窗]
    F06_Evolve --> F03_Page
    
    %% 模組 4：寵物圖鑑 (F-06)
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

    User->>Browser: 填寫食材名稱、數量、效期，點擊「新增」
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
展示餵食時，前端發送非同步 AJAX 請求，後端調用 Service 層進行經驗計算與進化圖鑑解鎖的資料流：

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器 (AJAX / JS)
    participant Flask as Flask Route (pet_routes)
    participant Service as Evolution Service
    participant Model as Pet/Collection Model
    participant DB as SQLite (Database)

    User->>Browser: 點擊「手動餵食」按鈕
    Browser->>Flask: POST /pet/feed (AJAX 請求)
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
    Flask-->>Browser: 回傳 JSON 結果
    Note over Browser: 1. 更新經驗值與等級文字<br/>2. 進度條動畫增長<br/>3. 若進化，開啟 modal 展示特效
    Browser-->>User: 取得即時餵食互動與升級/進化之視覺回饋
```

---

## 3. 功能清單對照表 (Feature-to-Route Mapping)

以下為隨食隨地系統各功能模組所對應的 URL 路徑、HTTP 方法與控制器說明：

| 功能編號 | 功能名稱 | HTTP 方法 | URL 路徑 | 對應控制器與方法 | 渲染模板 / 回傳格式 | 說明 |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- |
| **F-01** | 我的材料庫首頁 | `GET` | `/` | `ingredient.index` | `ingredients/index.html` | 列出目前所有食材與新增食材表單 |
| **F-01** | 新增食材 | `POST` | `/ingredient/add` | `ingredient.add` | 重導向至 `/` | 接收新增食材表單，寫入庫存後導回 |
| **F-01** | 編輯食材頁面 | `GET` | `/ingredient/edit/<id>` | `ingredient.edit` | `ingredients/edit.html` | 呈現單一食材修改表單 |
| **F-01** | 更新食材 | `POST` | `/ingredient/update/<id>`| `ingredient.update`| 重導向至 `/` | 接收編輯欄位更新庫存後導回 |
| **F-01** | 刪除食材 | `POST` | `/ingredient/delete/<id>`| `ingredient.delete`| 重導向至 `/` | 刪除指定食材後導回 |
| **F-02** | 推薦食譜 | `GET` | `/recipes/recommend` | `recipe.recommend` | `recipes/recommend.html` | 根據現有材料推薦合適食譜 (Skeleton) |
| **F-03** | 虛擬寵物首頁 | `GET` | `/pet` | `pet.pet_index` | `pet/index.html` | 呈現寵物數據、等級、餵食與進化觸發 |
| **F-03** | 手動餵食互動 | `POST` | `/pet/feed` | `pet.feed_pet` | JSON | 餵食加經驗值，自動升級進化並回傳 |
| **F-06** | 圖鑑主頁面 | `GET` | `/collection` | `collection.collection_index`| `collection/index.html` | 顯示所有寵物圖鑑與解鎖進度 |
| **F-06** | 型態詳情頁面 | `GET` | `/collection/<id>` | `collection.collection_detail`| `collection/detail.html` | 查看單一進化階段型態之風味說明與關係圖 |
| **F-06** | API：寵物狀態 | `GET` | `/api/pet/status` | `collection.api_pet_status`| JSON | 提供非同步輪詢或讀取寵物最新狀態 |
| **F-06** | API：加經驗值 | `POST` | `/api/pet/add-exp` | `collection.api_add_exp` | JSON | 供其他遊戲化功能或開發測試調用加 EXP |
| **F-06** | API：檢查進化 | `POST` | `/api/pet/evolve` | `collection.api_evolve` | JSON | 提供手動觸發進化狀態判定 |
| **F-06** | API：圖鑑資料 | `GET` | `/api/collection` | `collection.api_collection` | JSON | 回傳所有進化階段之解鎖清單與進度 |
| **F-06** | API：型態詳情 | `GET` | `/api/collection/<id>`| `collection.api_collection_detail`| JSON | 取得單一進化階段型態之 API 格式資料 |
