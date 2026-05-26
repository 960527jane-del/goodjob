# 路由設計 - 智慧食譜推薦系統 (F-02)

本文件依據 PRD 與架構設計，規劃 Flask 應用程式的路由 (Routes) 與 Jinja2 模板對應關係。除了核心的「智慧食譜推薦 (F-02)」功能外，也一併規劃了「我的材料庫」的基礎 CRUD 路由，以利後續的完整測試。

## 1. 路由總覽表格

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
| :--- | :---: | :--- | :--- | :--- |
| **我的材料庫列表** | `GET` | `/ingredients` | `ingredient/list.html` | 顯示所有現有食材 |
| **新增食材頁面** | `GET` | `/ingredients/new` | `ingredient/new.html` | 顯示新增食材表單 |
| **建立食材** | `POST` | `/ingredients` | — | 接收表單，存入 DB，重導向列表 |
| **編輯食材頁面** | `GET` | `/ingredients/<id>/edit` | `ingredient/edit.html` | 顯示編輯特定食材的表單 |
| **更新食材** | `POST` | `/ingredients/<id>/update` | — | 接收表單，更新 DB，重導向列表 |
| **刪除食材** | `POST` | `/ingredients/<id>/delete` | — | 刪除指定食材，重導向列表 |
| **推薦食譜列表** | `GET` | `/recipes` | `recipe/list.html` | 讀取食材庫，呼叫外部 API，顯示推薦清單 |
| **食譜詳細頁面** | `GET` | `/recipes/<id>` | `recipe/detail.html` | 顯示特定食譜的烹飪教學與缺漏配料 |

## 2. 每個路由的詳細說明

### 我的材料庫 (Ingredients)
- **`GET /ingredients`**
  - **處理邏輯**：呼叫 `IngredientModel.get_all()` 取得所有食材。
  - **輸出**：渲染 `ingredient/list.html` 並傳入 `ingredients` 資料。
- **`GET /ingredients/new`**
  - **處理邏輯**：無特殊邏輯，僅顯示表單。
  - **輸出**：渲染 `ingredient/new.html`。
- **`POST /ingredients`**
  - **輸入**：表單欄位 `name`, `quantity`, `unit`, `expiry_date`。
  - **處理邏輯**：驗證資料後呼叫 `IngredientModel.create(...)` 存入。
  - **輸出**：重導向至 `/ingredients`。
- **`GET /ingredients/<id>/edit`**
  - **處理邏輯**：呼叫 `IngredientModel.get_by_id(id)` 取得該筆食材資料。
  - **輸出**：渲染 `ingredient/edit.html`，若查無資料則回傳 404。
- **`POST /ingredients/<id>/update`**
  - **輸入**：表單欄位 `name`, `quantity`, `unit`, `expiry_date`。
  - **處理邏輯**：驗證資料後呼叫 `IngredientModel.update(...)` 更新。
  - **輸出**：重導向至 `/ingredients`。
- **`POST /ingredients/<id>/delete`**
  - **處理邏輯**：呼叫 `IngredientModel.delete(id)` 刪除該筆資料。
  - **輸出**：重導向至 `/ingredients`。

### 智慧食譜推薦 (Recipes)
- **`GET /recipes`**
  - **處理邏輯**：
    1. 呼叫 `IngredientModel.get_all()` 取得可用食材。
    2. 將食材轉換為關鍵字，呼叫外部食譜 API 尋找匹配食譜。
    3. 解析 API 回傳資料。
  - **輸出**：渲染 `recipe/list.html` 並傳入推薦清單。
  - **錯誤處理**：若外部 API 失敗，可回傳友善錯誤提示。
- **`GET /recipes/<id>`**
  - **輸入**：URL 參數 `<id>` (外部食譜的 ID)。
  - **處理邏輯**：
    1. 使用 ID 向外部 API 請求詳細食譜資訊（步驟、完整配料表）。
    2. 將食譜所需配料與本地 `IngredientModel.get_all()` 進行比對，標示出現有與缺漏的食材。
  - **輸出**：渲染 `recipe/detail.html` 並傳入詳細資訊。

## 3. Jinja2 模板清單

所有模板皆繼承自 `templates/base.html`，確保全站包含導覽列 (Navbar) 與共用外觀。

- `templates/base.html`: 網站共用版型 (Base Layout)。
- `templates/ingredient/list.html`: 我的材料庫列表頁。
- `templates/ingredient/new.html`: 新增食材表單頁面。
- `templates/ingredient/edit.html`: 編輯食材表單頁面。
- `templates/recipe/list.html`: 智慧食譜推薦結果頁面。
- `templates/recipe/detail.html`: 單一食譜詳細教學頁面。

## 4. 路由骨架程式碼

相關的 Flask 路由骨架 (Blueprint) 已建立於 `app/routes/ingredient.py` 與 `app/routes/recipe.py` 中。
# 隨食隨地 - 路由與頁面設計文件 (Routes)

## 1. 路由總覽表格

| 功能模組 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
| :--- | :--- | :--- | :--- | :--- |
| **首頁** | GET | `/` | `templates/index.html` | 顯示歡迎畫面、系統介紹與功能入口 |
| **烹飪回報** | GET | `/cooking` | `templates/cooking/index.html` | 顯示烹飪照片上傳與回報表單 |
| **送出回報** | POST | `/cooking/report` | — | 接收表單資料、儲存相片、增加飼料，完成後重導向 |
| **寵物養成** | GET | `/pet` | `templates/pet/index.html` | 顯示寵物等級、經驗值與當前擁有的飼料數 |
| **餵食寵物** | POST | `/pet/feed` | — | 接收 AJAX 請求，扣除飼料並增加經驗值，回傳 JSON |

## 2. 每個路由的詳細說明

### 2.1 `GET /` (首頁)
- **輸入**：無
- **處理邏輯**：簡單取得系統狀態或首頁介紹文案。
- **輸出**：渲染 `index.html`
- **錯誤處理**：無特殊錯誤，正常回傳 200。

### 2.2 `GET /cooking` (顯示回報表單)
- **輸入**：無
- **處理邏輯**：確認使用者身分（可預設為 `user_id = 1` 進行 MVP 開發）。
- **輸出**：渲染 `cooking/index.html`
- **錯誤處理**：若未登入則導回首頁或登入頁。

### 2.3 `POST /cooking/report` (送出回報)
- **輸入**：表單中的圖片檔案 `image` 或勾選狀態欄位。
- **處理邏輯**：
  1. 驗證是否有上傳檔案。
  2. 將檔案儲存至 `static/uploads/`，並取得路徑。
  3. 呼叫 `CookingRecord.create()` 儲存紀錄。
  4. 取得該使用者的 `FeedInventory`，呼叫 `add_feed(1)` 增加飼料。
- **輸出**：重導向至 `/pet`，並透過 flash 訊息提示「成功獲得飼料」。
- **錯誤處理**：
  - 若檔案格式錯誤或驗證失敗：重導向回 `/cooking` 並帶錯誤提示。

### 2.4 `GET /pet` (顯示寵物狀態)
- **輸入**：無
- **處理邏輯**：
  1. 取得當前登入使用者的 `Pet` 資料 (經驗值、等級)。
  2. 取得當前登入使用者的 `FeedInventory` 資料 (剩餘飼料數量)。
- **輸出**：渲染 `pet/index.html`，並將寵物與庫存資料傳入。
- **錯誤處理**：若找不到該使用者的寵物或庫存，則自動幫其建立預設資料再渲染。

### 2.5 `POST /pet/feed` (餵食寵物)
- **輸入**：無（透過 POST 請求觸發即可）
- **處理邏輯**：
  1. 取得使用者的 `FeedInventory`。
  2. 若 `count >= 1`，呼叫 `consume_feed(1)` 扣除飼料。
  3. 若扣除成功，取得 `Pet` 並呼叫 `add_exp(10)` 增加經驗值。
- **輸出**：回傳 JSON，格式如 `{ "success": true, "new_exp": 10, "new_level": 1, "remaining_feed": 5 }`
- **錯誤處理**：
  - 若飼料不足：回傳 400 JSON `{ "success": false, "error": "飼料不足" }`。

## 3. Jinja2 模板清單

所有模板皆會繼承共用的基礎佈局檔案 `base.html`。

- `templates/base.html`：包含 HTML 骨架、全站共用的 Header/導覽列、Footer 以及引入共用的 CSS/JS 檔案。
- `templates/index.html`：首頁內容，繼承 `base.html`。
- `templates/cooking/index.html`：烹飪回報表單與相片預覽介面，繼承 `base.html`。
- `templates/pet/index.html`：虛擬寵物顯示畫面、經驗進度條、剩餘飼料數量與餵食按鈕，繼承 `base.html`。
