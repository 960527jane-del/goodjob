# 隨食隨地 - 路由與 API 設計文件 (API Design)

本文件基於 `docs/PRD.md` 與 `docs/ARCHITECTURE.md`，定義系統各個核心模組的 Flask 路由 (Routes) 設計。這些路由採用 Blueprint 進行模組化管理。

## 1. 食材管理模組 (`inventory.py`)
負責處理「我的材料庫」的增刪改查 (F-01) 與過期提醒 (F-03)。

| Method | Endpoint | Description | Request | Response |
|---|---|---|---|---|
| `GET` | `/inventory` | 取得使用者的食材列表頁面 | N/A | `inventory.html` (包含過期標示) |
| `POST` | `/inventory/add` | 手動新增食材 | FormData: `name`, `quantity`, `expiry_date` | Redirect to `/inventory` |
| `POST` | `/inventory/update/<int:id>` | 修改現有食材數量或資訊 | FormData: `quantity` | Redirect to `/inventory` |
| `POST` | `/inventory/delete/<int:id>` | 刪除特定食材 | N/A | Redirect to `/inventory` |

## 2. 食譜推薦模組 (`recipe.py`)
負責處理食譜的推薦比對與詳細內容顯示 (F-02)。

| Method | Endpoint | Description | Request | Response |
|---|---|---|---|---|
| `GET` | `/recipes/recommend` | 推薦食譜列表 | N/A (系統讀取資料庫庫存比對) | `recipe_list.html` |
| `GET` | `/recipes/<int:id>` | 單一食譜詳細頁面 | N/A | `recipe_detail.html` |

## 3. 烹飪回報模組 (`cooking.py`)
負責處理使用者完成料理後的回報機制 (F-04, F-05)。

| Method | Endpoint | Description | Request | Response |
|---|---|---|---|---|
| `POST` | `/cooking/report` | 回報完成料理並發放飼料 | FormData: `recipe_id`, `photo` (可選) | Redirect / JSON: 成功訊息與發放的飼料數量 |

## 4. 虛擬寵物與餵食模組 (`pet.py`)
負責展示寵物狀態以及處理餵食互動 (F-04)。

| Method | Endpoint | Description | Request | Response |
|---|---|---|---|---|
| `GET` | `/pet` | 取得寵物與飼料庫存狀態頁面 | N/A | `pet.html` |
| `POST` | `/pet/feed` | 餵食寵物 (扣除飼料、增加經驗) | N/A (AJAX 請求) | JSON: `{ "success": true, "pet_level": 2, "pet_exp": 10, "virtual_food": 0 }` |
