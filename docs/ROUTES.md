# 隨食隨地 - 路由與頁面設計 (F-03 虛擬寵物養成系統)

本文件根據 `PRD_F-03.md`、`ARCHITECTURE.md` 與 `DB_DESIGN.md`，規劃了虛擬寵物養成系統的 URL 路由、HTTP 方法與對應的 Jinja2 模板。

## 1. 路由總覽表格

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
| --- | --- | --- | --- | --- |
| 寵物專屬首頁 | GET | `/pet` | `templates/pet/index.html` | 顯示寵物目前的狀態、等級與經驗值進度條 |
| 餵食寵物 API | POST | `/api/pet/feed` | — (回傳 JSON) | 接收前端點擊餵食的非同步請求，計算經驗值並存入 DB |
| 取得寵物狀態 | GET | `/api/pet/status` | — (回傳 JSON) | 供前端非同步獲取最新等級與經驗值 |

## 2. 每個路由的詳細說明

### 2.1 寵物專屬首頁
- **URL**: `/pet`
- **Method**: `GET`
- **輸入**: 無（從 session 中取得 user_id）
- **處理邏輯**: 
  - 呼叫 `Pet.get_by_user_id(user_id)` 取得該使用者的寵物資料。
  - 若無寵物資料，可導向「建立寵物」頁面或顯示預設畫面。
- **輸出**: 渲染 `templates/pet/index.html`，並將寵物物件 (包含 name, level, exp) 傳入模板中。
- **錯誤處理**: 若 user_id 無效或未登入，重導向至登入頁面 (未來擴充)。

### 2.2 餵食寵物 API
- **URL**: `/api/pet/feed`
- **Method**: `POST`
- **輸入**: JSON 格式 `{"exp_gained": 25}` 或依後端設定給予固定值。
- **處理邏輯**:
  - 驗證使用者身份。
  - 呼叫 `Pet.feed(user_id, exp_gained)` 更新經驗值與計算是否升級。
- **輸出**: 回傳 JSON 格式結果，例如：`{"success": true, "pet": {"level": 2, "exp": 10}, "is_level_up": true}`。
- **錯誤處理**: 
  - 若找不到寵物，回傳 404 `{"error": "Pet not found"}`。
  - 若未登入，回傳 401。

### 2.3 取得寵物狀態 API
- **URL**: `/api/pet/status`
- **Method**: `GET`
- **輸入**: 無
- **處理邏輯**:
  - 呼叫 `Pet.get_by_user_id(user_id)` 查詢最新資料。
- **輸出**: 回傳 JSON，例如：`{"level": 2, "exp": 10}`。
- **錯誤處理**: 若找不到寵物，回傳 404。

## 3. Jinja2 模板清單

以下為本功能需建立的 HTML 模板檔案：

- `templates/base.html`：**所有頁面共用的母版**，包含 `<header>` (導覽列)、`<head>` (匯入 CSS/JS) 等。
- `templates/pet/index.html`：**寵物專屬首頁**，繼承自 `base.html`。包含顯示寵物外觀的區塊、進度條以及餵食按鈕。

## 4. 路由骨架程式碼
已於 `app/routes/pet_routes.py` 建立路由控制器骨架。
