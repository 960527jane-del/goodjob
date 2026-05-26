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
