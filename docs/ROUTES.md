# 隨「食」隨地 — 路由與 API 設計文件 (Routes)

本文件詳細列出系統中所有路由與 API 端點、其對應的控制器(Blueprint)、HTTP 方法、輸入輸出以及渲染的模板，以作為前後端協作之核心指引。

---

## 1. 路由規劃總覽表

| 功能模組 | HTTP 方法 | URL 路徑 | 對應控制器與方法 | 渲染模板 / 回傳格式 | 說明 |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **我的材料庫** | `GET` | `/` | `ingredient.index` | `ingredients/index.html` | 列出目前所有食材與新增食材表單 |
| **新增食材** | `POST` | `/ingredient/add` | `ingredient.add` | 重導向至 `/` | 接收新增表單，寫入庫存後導回 |
| **編輯食材頁面**| `GET` | `/ingredient/edit/<id>`| `ingredient.edit` | `ingredients/edit.html` | 呈現單一食材修改表單 |
| **更新食材** | `POST` | `/ingredient/update/<id>`| `ingredient.update`| 重導向至 `/` | 接收編輯欄位更新庫存後導回 |
| **刪除食材** | `POST` | `/ingredient/delete/<id>`| `ingredient.delete`| 重導向至 `/` | 刪除指定食材後導回 |
| **推薦食譜** | `GET` | `/recipes/recommend` | `recipe.recommend` | `recipes/recommend.html` | 根據現有材料推薦合適食譜 (Skeleton) |
| **虛擬寵物主頁**| `GET` | `/pet` | `pet.pet_index` | `pet/index.html` | 呈現寵物數據、等級、餵食與進化觸發 |
| **手動餵食互動**| `POST` | `/pet/feed` | `pet.feed_pet` | JSON | 餵食加經驗值，自動升級進化並回傳 |
| **圖鑑主頁面** | `GET` | `/collection` | `collection.collection_index`| `collection/index.html` | 顯示所有寵物圖鑑與解鎖進度 |
| **型態詳情頁面**| `GET` | `/collection/<id>` | `collection.collection_detail`| `collection/detail.html` | 查看單一進化階段型態之風味說明與關係圖 |
| **API：寵物狀態** | `GET` | `/api/pet/status` | `collection.api_pet_status`| JSON | 提供非同步輪詢或讀取寵物最新狀態 |
| **API：加經驗值** | `POST` | `/api/pet/add-exp` | `collection.api_add_exp` | JSON | 供其他遊戲化功能或開發測試調用加 EXP |
| **API：檢查進化** | `POST` | `/api/pet/evolve` | `collection.api_evolve` | JSON | 提供手動觸發進化狀態判定 |
| **API：圖鑑資料** | `GET` | `/api/collection` | `collection.api_collection` | JSON | 回傳所有進化階段之解鎖清單與進度 |
| **API：型態詳情** | `GET` | `/api/collection/<id>`| `collection.api_collection_detail`| JSON | 取得單一進化階段型態之 API 格式資料 |

---

## 2. 每個路由的詳細說明

### 2.1 我的材料庫 (首頁) (`GET /`)
*   **輸入**：無
*   **處理邏輯**：調用 `Ingredient.get_all()` 獲取所有材料清單。
*   **輸出**：渲染 `ingredients/index.html`。
*   **錯誤處理**：若資料庫連線失敗，返回空食材清單並在網頁提示。

### 2.2 新增食材 (`POST /ingredient/add`)
*   **輸入**：表單欄位 `name` (TEXT), `quantity` (REAL), `unit` (TEXT), `expiry_date` (TEXT)
*   **處理邏輯**：
    1. 驗證 `name` 與 `quantity` 是否填寫。
    2. 將 `quantity` 轉為 float。
    3. 調用 `Ingredient.create()` 插入資料庫。
*   **輸出**：重導向至 `/`，並透過 Flash 顯示成功或失敗訊息。
*   **錯誤處理**：欄位未填或數量不為數字時，Flash 提示錯誤並重導向回首頁。

### 2.3 編輯食材頁面 (`GET /ingredient/edit/<int:id>`)
*   **輸入**：URL 參數 `id` (INTEGER)
*   **處理邏輯**：調用 `Ingredient.get_by_id(id)`。
*   **輸出**：渲染 `ingredients/edit.html`。
*   **錯誤處理**：若找不到該食材，Flash 提示「找不到該食材！」並重導向回首頁。

### 2.4 更新食材 (`POST /ingredient/update/<int:id>`)
*   **輸入**：URL 參數 `id` (INTEGER)，表單欄位 `name`, `quantity`, `unit`, `expiry_date`
*   **處理邏輯**：驗證欄位合法性後，調用 `Ingredient.update()`。
*   **輸出**：重導向至 `/`。
*   **錯誤處理**：驗證失敗時，重導向回編輯頁面並 Flash 錯誤。

### 2.5 刪除食材 (`POST /ingredient/delete/<int:id>`)
*   **輸入**：URL 參數 `id` (INTEGER)
*   **處理邏輯**：調用 `Ingredient.delete(id)`。
*   **輸出**：重導向至 `/`。
*   **錯誤處理**：刪除失敗時，Flash 顯示錯誤訊息。

### 2.6 推薦食譜 (`GET /recipes/recommend`)
*   **輸入**：無
*   **處理邏輯**：目前為靜態展示，未來將讀取 `Ingredient.get_all()` 進行食材匹配。
*   **輸出**：渲染 `recipes/recommend.html`。

### 2.7 虛擬寵物主頁 (`GET /pet`)
*   **輸入**：無
*   **處理邏輯**：調用 `Pet.get_by_user_id(DEV_USER_ID)`，若寵物不存在則自動調用 `Pet.create()` 建立預設寵物。
*   **輸出**：渲染 `pet/index.html`。

### 2.8 手動餵食互動 (`POST /pet/feed`)
*   **輸入**：無
*   **處理邏輯**：
    1. 取得寵物 ID，調用 `Pet.add_exp(pet_id, 10)` 增加 10 點經驗值。
    2. 自動觸發進化與升級檢查。
*   **輸出**：回傳最新寵物狀態的 JSON 數據。

---

## 3. Jinja2 模板清單

專案所使用的 HTML 模板均繼承共用模板並進行局部區塊（Block）覆寫：

*   **共用基礎版型**：[base.html](file:///c:/Users/linpi/Desktop/程式設計/goodjob/app/templates/base.html)
    *   *說明*：包含 Glassmorphism 的全站導覽列、頁尾、背景粒子樣式與共用 CSS/JS 引用。
*   **我的材料庫首頁**：[ingredients/index.html](file:///c:/Users/linpi/Desktop/程式設計/goodjob/app/templates/ingredients/index.html)
    *   *繼承*：`base.html`
    *   *用途*：顯示目前的食材列表網格與快捷新增食材表單。
*   **編輯食材頁面**：[ingredients/edit.html](file:///c:/Users/linpi/Desktop/程式設計/goodjob/app/templates/ingredients/edit.html)
    *   *繼承*：`base.html`
    *   *用途*：顯示單一食材的修改表單。
*   **食譜推薦頁面**：[recipes/recommend.html](file:///c:/Users/linpi/Desktop/程式設計/goodjob/app/templates/recipes/recommend.html)
    *   *繼承*：`base.html`
    *   *用途*：呈現食譜推薦列表與匹配進度。
*   **虛擬寵物主頁**：[pet/index.html](file:///c:/Users/linpi/Desktop/程式設計/goodjob/app/templates/pet/index.html)
    *   *繼承*：`base.html`
    *   *用途*：呈現寵物外觀、Level、EXP 視覺化進度條與餵食互動按鈕。
*   **圖鑑主頁面**：[collection/index.html](file:///c:/Users/linpi/Desktop/程式設計/goodjob/app/templates/collection/index.html)
    *   *繼承*：`base.html`
    *   *用途*：以卡片網格展示所有寵物階段的解鎖與遮罩狀態。
*   **型態詳情頁面**：[collection/detail.html](file:///c:/Users/linpi/Desktop/程式設計/goodjob/app/templates/collection/detail.html)
    *   *繼承*：`base.html`
    *   *用途*：呈現特定寵物形態的詳細故事與進化樹。

---

## 4. 路由骨架程式碼實作狀態

目前專案的各路由模組程式碼已在 `app/routes/` 目錄下完成實作（相較於空骨架，已寫入完整的處理邏輯與資料庫互動）：
- 食材管理路由：[ingredient.py](file:///c:/Users/linpi/Desktop/程式設計/goodjob/app/routes/ingredient.py)
- 食譜推薦路由：[recipe.py](file:///c:/Users/linpi/Desktop/程式設計/goodjob/app/routes/recipe.py)
- 寵物養成路由：[pet_routes.py](file:///c:/Users/linpi/Desktop/程式設計/goodjob/app/routes/pet_routes.py)
- 進化與圖鑑 API 路由：[collection_routes.py](file:///c:/Users/linpi/Desktop/程式設計/goodjob/app/routes/collection_routes.py)
