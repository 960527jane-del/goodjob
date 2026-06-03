# 隨食隨地 - 系統流程圖 (Flowchart)

本文件基於 `docs/PRD.md` 與 `docs/ARCHITECTURE.md`，描繪「隨食隨地」系統的核心使用者旅程（User Journey）與系統運作流程。

## 1. 核心系統使用流程圖

此流程圖涵蓋了 MVP 階段的四大核心功能：
- **F-01 / F-03**: 食材管理與過期提醒
- **F-02**: 智慧食譜推薦
- **F-04**: 烹飪回報與餵食機制
- **F-05**: 烹飪歷史紀錄

```mermaid
flowchart TD
    %% 定義節點樣式
    classDef page fill:#f9f,stroke:#333,stroke-width:2px;
    classDef action fill:#bbf,stroke:#333,stroke-width:1px;
    classDef logic fill:#ff9,stroke:#333,stroke-width:1px;
    classDef db fill:#eee,stroke:#333,stroke-width:1px,stroke-dasharray: 5 5;

    Start([啟動 App / 首頁]) --> MainMenu{選擇功能模組}:::logic

    %% -------------------------
    %% 模組 1: 食材管理 (F-01, F-03)
    %% -------------------------
    MainMenu -->|進入| InventoryPage[我的材料庫頁面]:::page
    InventoryPage --> CheckExpiry{檢查保存期限 (F-03)}:::logic
    CheckExpiry -->|即將過期| ShowWarning[顯示過期警示標籤]:::action
    CheckExpiry -->|正常| ShowList[顯示現有食材列表]:::action
    
    InventoryPage --> ActionInventory{選擇操作}:::logic
    ActionInventory -->|手動新增| AddIng[輸入食材名稱、數量、期限]:::action
    ActionInventory -->|編輯/刪除| EditIng[更新或刪除現有食材]:::action
    AddIng --> DB_Ing[(更新 Ingredient 資料表)]:::db
    EditIng --> DB_Ing

    %% -------------------------
    %% 模組 2: 食譜推薦 (F-02)
    %% -------------------------
    MainMenu -->|進入| RecipePage[食譜推薦頁面]:::page
    RecipePage --> ReadDB_Ing[(讀取現有庫存)]:::db
    ReadDB_Ing --> MatchRecipe[比對食材與食譜資料]:::action
    MatchRecipe --> ShowRecipes[顯示推薦食譜列表]:::action
    ShowRecipes --> ViewDetail[點擊查看食譜詳細步驟]:::page

    %% -------------------------
    %% 模組 3: 烹飪回報 (F-04, F-05)
    %% -------------------------
    ViewDetail -->|完成料理| CookingReport[進入烹飪回報介面]:::page
    CookingReport --> ChooseReport{選擇回報方式}:::logic
    ChooseReport -->|上傳圖片| UploadPhoto[手機拍照/相簿上傳]:::action
    ChooseReport -->|快速點擊| CheckDone[勾選確認完成]:::action
    
    UploadPhoto --> VerifyReport[系統發放「虛擬飼料」]:::action
    CheckDone --> VerifyReport
    
    VerifyReport --> DB_History[(寫入 Cooking_History F-05)]:::db
    DB_History --> DB_User_Food[(更新 User 虛擬飼料庫存)]:::db

    %% -------------------------
    %% 模組 4: 寵物養成與餵食 (F-04)
    %% -------------------------
    MainMenu -->|進入| PetPage[虛擬寵物頁面]:::page
    DB_User_Food -.->|即時反映庫存| PetPage
    
    PetPage --> FeedCheck{點擊餵食: \n庫存 > 0 ?}:::logic
    FeedCheck -->|否| PromptCook[提示: 去做菜收集飼料吧！]:::action
    PromptCook -.-> RecipePage
    
    FeedCheck -->|是 (AJAX)| FeedAction[扣除飼料, 增加寵物 EXP]:::action
    FeedAction --> ExpCheck{EXP 是否達升級門檻?}:::logic
    
    ExpCheck -->|否| ShowExpAnim[播放進食與 +EXP 特效]:::action
    ExpCheck -->|是| ShowLevelUpAnim[播放寵物升級特效與外觀變更]:::action
    
    ShowExpAnim --> DB_User_Exp[(更新 User EXP)]:::db
    ShowLevelUpAnim --> DB_User_Exp
```

---

## 2. 流程設計亮點說明
1. **閉環機制 (Closed Loop)**：使用者從「管理食材」出發，透過「食譜推薦」消化食材，再經由「烹飪回報」獲取獎勵（虛擬飼料），最後至「寵物頁面」消耗獎勵獲得成就感。當飼料不足時，又會引導使用者回到食譜頁面，形成高黏著度的正向循環。
2. **防呆與引導**：在寵物頁面中，若虛擬飼料庫存不足，系統不會只顯示錯誤，而是設計明確的 CTA (Call To Action) 引導使用者去「做菜收集飼料」。
3. **無縫的使用者體驗**：如 `ARCHITECTURE.md` 所述，在「餵食」流程中採用了 AJAX 異步請求更新資料庫，讓前端特效（如 `+EXP` 動畫、進食動畫）不會因為頁面重整而中斷。
