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

## 2. 核心路由處理邏輯

### 2.1 虛擬寵物首頁 (`GET /pet`)
- **業務邏輯**：
  1. 呼叫 `Pet.get_by_user_id(DEV_USER_ID)` 獲取當前使用者的寵物。
  2. 若資料庫無記錄，則自動調用 `Pet.create(DEV_USER_ID, "小食怪")` 建立一隻初始寵物。
  3. 將包含 species 與 stages 關聯欄位的 `pet` 字典傳入 `pet/index.html` 進行渲染。

### 2.2 手動餵食 (`POST /pet/feed`)
- **業務邏輯**：
  1. 呼叫 `Pet.add_exp(pet_id, 10)` (每次手動餵食增加 10 經驗值)。
  2. 控制器內部的 `Pet.add_exp` 會將流程委託至 `evolution_service.add_exp` 處理。
  3. `evolution_service` 執行總經驗值加總，並呼叫 `calculate_level_from_exp` 計算新等級。
  4. 若等級上升，自動檢查並調用 `check_and_evolve` 判定進化並解鎖對應圖鑑。
  5. 最終回傳包含最新 EXP、進度條比率、等級、升級旗標、進化型態等資訊之 JSON。

### 2.3 圖鑑篩選與展示 (`GET /collection`)
- **業務邏輯**：
  1. 呼叫 `collection_model.get_all_stages()` 取得所有種族與進化階段。
  2. 呼叫 `collection_model.get_user_collection(DEV_USER_ID)` 取得已解鎖的階段 ID 集合 (Set)。
  3. 透過 `in` 運算子於 HTML 中判定特定卡片是否顯示為彩色解鎖狀態或灰色鎖定狀態。
