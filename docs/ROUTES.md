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
