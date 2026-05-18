# 流程圖設計 - 虛擬寵物養成系統 (F-03)

本文件根據產品需求文件（PRD）與系統架構文件（ARCHITECTURE），視覺化「虛擬寵物養成系統」的使用者操作路徑與系統內部的資料流動。

---

## 1. 使用者流程圖（User Flow）

描述使用者在系統中如何操作與互動的路徑。

```mermaid
flowchart LR
    A([使用者登入系統]) --> B[進入虛擬寵物頁面]
    B --> C{查看寵物狀態}
    
    C -->|觀察外觀與數值| D[顯示當前等級與經驗值進度條]
    C -->|點擊互動| E[點擊「手動餵食」按鈕]
    
    E --> F{系統處理餵食請求}
    F -->|成功獲得經驗值| G[更新經驗值與進度條動畫]
    F -->|經驗值達標| H[觸發升級動畫與外觀改變]
    
    G --> B
    H --> B
```

---

## 2. 系統序列圖（Sequence Diagram）

描述使用者點擊「手動餵食」後，前端與後端及資料庫之間完整的互動過程。

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器 (JS/Jinja2)
    participant Flask as Flask 路由 (Controller)
    participant Model as Pet Model (邏輯層)
    participant DB as SQLite 資料庫
    
    User->>Browser: 點擊「手動餵食」按鈕
    Browser->>Flask: AJAX POST /pet/feed
    
    Flask->>Model: 呼叫 feed_pet(user_id)
    Model->>DB: SELECT * FROM pets WHERE user_id = ?
    DB-->>Model: 回傳當前 EXP 與 Level
    
    Note over Model: 計算新 EXP：<br/>若 EXP >= 升級門檻，則 Level + 1
    
    Model->>DB: UPDATE pets SET exp = ?, level = ?
    DB-->>Model: 更新成功
    Model-->>Flask: 回傳最新的寵物狀態
    
    Flask-->>Browser: 回傳 JSON (包含新 EXP, Level, 升級狀態)
    
    Note over Browser: 根據回傳的 JSON 更新畫面：<br/>1. 增長進度條<br/>2. 更新等級文字<br/>3. 若有升級，顯示特效或新外觀
    Browser-->>User: 看到寵物獲得經驗值或升級的視覺回饋
```

---

## 3. 功能清單對照表

以下為 F-03 系統對應的路由與 HTTP 方法設計，作為實作時的參考依據。

| 功能項目 | HTTP 方法 | URL 路徑 | 說明 |
| :--- | :---: | :--- | :--- |
| **寵物專屬展示頁面** | `GET` | `/pet` | 載入包含寵物圖片、等級、經驗值進度條的 HTML 頁面。 |
| **手動觸發餵食 (互動)** | `POST` | `/pet/feed` | 透過 AJAX 呼叫，增加經驗值並處理升級邏輯，回傳更新後的 JSON 狀態。 |
| **獲取最新寵物狀態** | `GET` | `/api/pet/status` | (Nice to Have) 若未來需要非同步輪詢狀態，可提供此 API 回傳 JSON。 |
