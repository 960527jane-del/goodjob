# 路由設計文件 (Routes) - 隨食隨地

本文件詳細規劃了「隨食隨地」系統後端的路由與前端頁面的對應關係，確保前端行為與資料庫操作能正確串接。

## 1. 路由總覽表格

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
| :--- | :--- | :--- | :--- | :--- |
| 我的材料庫 (首頁) | GET | `/` | `ingredients/index.html` | 列出目前所有食材，並包含新增表單 |
| 新增食材 | POST | `/ingredient/add` | — | 接收新增表單，寫入資料庫後重導向至 `/` |
| 編輯食材頁面 | GET | `/ingredient/edit/<id>` | `ingredients/edit.html` | 顯示單一食材的修改表單 |
| 更新食材 | POST | `/ingredient/update/<id>` | — | 接收修改表單，更新資料庫後重導向至 `/` |
| 刪除食材 | POST | `/ingredient/delete/<id>` | — | 刪除指定食材，完成後重導向至 `/` |
| 推薦食譜 | GET | `/recipes/recommend` | `recipes/recommend.html` | 根據現有食材推薦食譜 |

## 2. 每個路由的詳細說明

### `GET /` (首頁 / 我的材料庫)
- **輸入**：無。
- **處理邏輯**：呼叫 `Ingredient.get_all()` 取得所有依建立時間反序排列的食材紀錄。
- **輸出**：渲染 `ingredients/index.html`，傳遞 `ingredients` 變數。
- **錯誤處理**：若資料庫為空，顯示「目前沒有食材，請新增！」的空狀態畫面。

### `POST /ingredient/add` (新增食材)
- **輸入**：表單欄位 `name`, `quantity`, `unit`, `expiry_date`。
- **處理邏輯**：接收欄位值，進行簡單空值檢查，呼叫 `Ingredient.create(...)` 寫入資料庫。
- **輸出**：重導向至 `GET /`。
- **錯誤處理**：若 `name` 或 `quantity` 為空，使用 `flash()` 提示錯誤，然後重導向回首頁。

### `GET /ingredient/edit/<id>` (編輯食材頁面)
- **輸入**：URL 參數 `id`。
- **處理邏輯**：呼叫 `Ingredient.get_by_id(id)` 取得該筆食材的原始資料。
- **輸出**：渲染 `ingredients/edit.html`，傳遞 `ingredient` 變數。
- **錯誤處理**：若找不到該 ID，回傳 404 錯誤，或 `flash()` 並重導向回首頁。

### `POST /ingredient/update/<id>` (更新食材)
- **輸入**：URL 參數 `id` 以及表單欄位 `name`, `quantity`, `unit`, `expiry_date`。
- **處理邏輯**：接收更新的資料，呼叫 `Ingredient.update(...)` 修改資料庫內容。
- **輸出**：重導向至 `GET /`。
- **錯誤處理**：若資料驗證失敗，`flash()` 錯誤訊息並重導向回該編輯頁面。

### `POST /ingredient/delete/<id>` (刪除食材)
- **輸入**：URL 參數 `id`。
- **處理邏輯**：呼叫 `Ingredient.delete(id)` 刪除該筆資料。
- **輸出**：重導向至 `GET /`。
- **錯誤處理**：若該 ID 不存在，則忽略操作或 `flash()` 錯誤訊息。

### `GET /recipes/recommend` (推薦食譜)
- **輸入**：無。
- **處理邏輯**：取得現有食材，呼叫簡易演算法或外部 API 取回推薦食譜 (MVP 初期可使用測試資料)。
- **輸出**：渲染 `recipes/recommend.html`。
- **錯誤處理**：如果無食材可推薦，提示使用者先新增食材。

## 3. Jinja2 模板清單

所有的模板檔案預期將建立在 `app/templates/` 目錄下：

1. `base.html`：共用版型，包含導覽列 (Navbar)、主體結構與 Footer、以及統一引入 CSS 樣式。
2. `ingredients/index.html`：繼承自 `base.html`。首頁，負責呈現食材清單、操作按鈕 (編輯/刪除)，以及新增食材的表單區塊。
3. `ingredients/edit.html`：繼承自 `base.html`。獨立的修改頁面，用於編輯特定食材的數量與有效期限。
4. `recipes/recommend.html`：繼承自 `base.html`。顯示系統推薦的食譜清單。

## 4. 路由骨架程式碼

路由的骨架已經建立在 `app/routes/` 之下，採用 Flask Blueprint 進行模組化規劃：
- `app/routes/ingredient.py`：處理食材管理的增刪改查路由。
- `app/routes/recipe.py`：處理食譜推薦相關路由。
