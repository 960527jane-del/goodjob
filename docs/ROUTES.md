# 隨「食」隨地 — 路由與 API 設計文件 (Routes)

本文件詳細列出系統中所有路由與 API 端點、其對應的控制器(Blueprint), HTTP 方法、輸入輸出以及渲染的模板，以作為前後端協作之核心指引。

---

## 1. 路由規劃總覽表

| 功能模組 | HTTP 方法 | URL 路徑 | 對應控制器與方法 | 渲染模板 / 回傳格式 | 說明 |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **我的材料庫** | `GET` | `/` | `ingredient.index` | `ingredients/index.html` | 列出目前所有食材與新增食材表單 |
| **新增食材** | `POST` | `/ingredient/add` | `ingredient.add` | 重導向至 `/` | 接收新增表單，寫入庫存後導回 |
| **編輯食材頁面**| `GET` | `/ingredient/edit/<id>`| `ingredient.edit` | `ingredients/edit.html` | 呈現單一食材修改表單 |
| **更新食材** | `POST` | `/ingredient/update/<id>`| `ingredient.update`| 重導向至 `/` | 接收編輯欄位更新庫存後導回 |
| **刪除食材** | `POST` | `/ingredient/delete/<id>`| `ingredient.delete`| 重導向至 `/` | 刪除指定食材後導回 |
| **推薦食譜** | `GET` | `/recipes/recommend` | `recipe.recommend` | `recipes/recommend.html` | 根據現有材料推薦合適食譜 |
| **虛擬寵物主頁**| `GET` | `/pet` | `pet.pet_index` | `pet/index.html` | 呈現寵物數據、等級、餵食與進化觸發 |
| **手動餵食互動**| `POST` | `/pet/feed` | `pet.feed_pet` | JSON | 檢查飼料庫存並扣減，增加寵物經驗值升級進化並回傳 |
| **烹飪回報頁面**| `GET` | `/cooking` | `cooking.report_page` | `cooking/index.html` | 顯示烹飪回報照片上傳與完成勾選頁面 |
| **提交烹飪紀錄**| `POST` | `/cooking/report` | `cooking.submit_report`| 重導向至 `/pet` | 儲存料理照片、新增紀錄、加 1 個飼料庫存並重導向 |
| **圖鑑主頁面** | `GET` | `/collection` | `collection.collection_index`| `collection/index.html` | 顯示所有寵物圖鑑與解鎖進度 |
| **型態詳情頁面**| `GET` | `/collection/<id>` | `collection.collection_detail`| `collection/detail.html` | 查看單一進化階段型態之風味說明與關係圖 |
| **用戶註冊** | `GET`/`POST` | `/register` | `register` (app.py) | `register.html` / 重導向至 `/preferences` | 接收表單註冊使用者並自動登入 |
| **用戶登入** | `GET`/`POST` | `/login` | `login` (app.py) | `login.html` / 重導向至首頁 | 接收表單並登入使用者 |
| **用戶登出** | `GET` | `/logout` | `logout` (app.py) | 重導向至首頁 | 清除使用者 Session |
| **偏好設定** | `GET`/`POST` | `/preferences` | `preferences` (app.py) | `preferences.html` | 修改過敏原與飲食類型 (全素/五辛素/烹飪程度) |
| **成就與個人資料**| `GET` | `/profile` | `profile` (app.py) | `profile.html` | 顯示個人累積烹飪次數與解鎖的成就列表 |

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

### 2.3 編輯食材頁面 (`GET /ingredient/edit/<int:id>`)
*   **輸入**：URL 參數 `id` (INTEGER)
*   **處理邏輯**：調用 `Ingredient.get_by_id(id)`。
*   **輸出**：渲染 `ingredients/edit.html`。

### 2.4 更新食材 (`POST /ingredient/update/<int:id>`)
*   **輸入**：URL 參數 `id` (INTEGER)，表單欄位 `name`, `quantity`, `unit`, `expiry_date`
*   **處理邏輯**：驗證欄位合法性後，調用 `Ingredient.update()`。
*   **輸出**：重導向至 `/`。

### 2.5 刪除食材 (`POST /ingredient/delete/<int:id>`)
*   **輸入**：URL 參數 `id` (INTEGER)
*   **處理邏輯**：調用 `Ingredient.delete(id)`。
*   **輸出**：重導向至 `/`。

### 2.6 推薦食譜 (`GET /recipes/recommend`)
*   **輸入**：無
*   **處理邏輯**：目前為靜態展示，未來將讀取 `Ingredient.get_all()` 進行食材匹配。
*   **輸出**：渲染 `recipes/recommend.html`。

### 2.7 虛擬寵物主頁 (`GET /pet`)
*   **輸入**：無
*   **處理邏輯**：調用 `Pet.get_by_user_id(DEV_USER_ID)`，若寵物不存在則自動調用 `Pet.create()` 建立預設寵物；同時載入 `FeedInventory.get_by_user_id(DEV_USER_ID)`。
*   **輸出**：渲染 `pet/index.html`。

### 2.8 手動餵食互動 (`POST /pet/feed`)
*   **輸入**：無
*   **處理邏輯**：
    1. 取得使用者的 `FeedInventory`，檢查 `count >= 1`。
    2. 調用 `consume_feed(1)` 扣除 1 個飼料。
    3. 取得寵物 ID，調用 `Pet.add_exp(pet_id, 20)` 增加 20 點經驗值。
    4. 自動觸發進化與升級檢查。
*   **輸出**：回傳最新寵物狀態與剩餘飼料庫存的 JSON 數據：
    ```json
    {
       "success": true,
       "pet": { ... },
       "remaining_feed": 4
    }
    ```

### 2.9 烹飪回報頁面 (`GET /cooking`)
*   **輸入**：無
*   **處理邏輯**：無特殊邏輯，僅顯示回報頁面。
*   **輸出**：渲染 `cooking/index.html`。

### 2.10 提交烹飪紀錄 (`POST /cooking/report`)
*   **輸入**：表單中的圖片檔案 `image`，完成狀態勾選。
*   **處理邏輯**：
    1. 將圖片儲存於 `static/uploads/` 中。
    2. 新增 `CookingRecord` 紀錄。
    3. 取得使用者 `FeedInventory`，呼叫 `add_feed(1)` 增加 1 份飼料。
*   **輸出**：重導向至 `/pet` 並 Flash 提示獲得飼料。

---

## 3. Jinja2 模板清單

專案所使用的 HTML 模板均繼承共用模板並進行局部區塊（Block）覆寫：

*   **共用基礎版型**：[base.html](file:///c:/Users/linpi/Desktop/程式設計/goodjob/app/templates/base.html)
*   **我的材料庫首頁**：[ingredients/index.html](file:///c:/Users/linpi/Desktop/程式設計/goodjob/app/templates/ingredients/index.html)
*   **編輯食材頁面**：[ingredients/edit.html](file:///c:/Users/linpi/Desktop/程式設計/goodjob/app/templates/ingredients/edit.html)
*   **食譜推薦頁面**：[recipes/recommend.html](file:///c:/Users/linpi/Desktop/程式設計/goodjob/app/templates/recipes/recommend.html)
*   **虛擬寵物主頁**：[pet/index.html](file:///c:/Users/linpi/Desktop/程式設計/goodjob/app/templates/pet/index.html)
*   **圖鑑主頁面**：[collection/index.html](file:///c:/Users/linpi/Desktop/程式設計/goodjob/app/templates/collection/index.html)
*   **型態詳情頁面**：[collection/detail.html](file:///c:/Users/linpi/Desktop/程式設計/goodjob/app/templates/collection/detail.html)
*   **烹飪回報頁面**：[cooking/index.html](file:///c:/Users/linpi/Desktop/程式設計/goodjob/app/templates/cooking/index.html)
