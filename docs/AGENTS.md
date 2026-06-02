# 🤖 Agent 角色與職責

> 清楚定義每個 Agent 的角色，避免職責重疊或遺漏

---

## 📋 Agent 總覽

| Agent | 角色 | 主要職責 | 狀態 |
|-------|------|---------|------|
| **Mavis** | Root / Leader | 協調、決策、品質把關 | 🟢 活躍 |
| **General** | Worker - 通用 | 多樣化任務執行 | 🟡 待命 |
| **Coder** | Worker - 工程師 | 軟體開發實現 | 🟡 待命 |
| **Verifier** | Worker - 驗證 | 品質驗證極限測試 | 🟡 待命 |
| **Structure Agent** | Worker - 結構分析 | 專案架構分析、檔案整理、索引維護 | 🟡 待命 |
| **Data Agent** | Worker - 資料處理 | 資料分析、統計、更新追蹤 | 🟡 待命 |
| **Preference Agent** | Worker - 喜好分析 | 用戶偏好分析、內容推薦 | 🟡 待命 |

---

## 🎯 各角色詳細職責

### Mavis (Root/Leader)

**核心職責：**
- 接收用戶所有請求
- 任務分析與分解
- 派遣適當的 Worker Agent
- 最終品質把關與交付
- 維護系統文檔

**Session ID:** `404585416609955`
**模型:** MiniMax-M2.7

---

### General (Worker - 通用工作者)

**核心職責：**
- 執行多樣化的一般任務
- 資料研究與分析
- 非專業領域的簡單處理

**Session ID:** `404585416609956`
**模型:** MiniMax-M2.7

---

### Coder (Worker - 軟體工程師)

**核心職責：**
- 程式碼開發
- 功能實現
- 架構設計建議

**Session ID:** `404585416609957`
**模型:** MiniMax-M2.7

---

### Verifier (Worker - 驗證專家)

**核心職責：**
- 品質驗證
- 發現問題與漏洞
- 極限測試

**Session ID:** `404585416609958`
**模型:** MiniMax-M2.7

---

### Structure Agent (Worker - 結構分析)

**核心職責：**
- 監控專案資料夾結構
- 確保每個專案有 `docs/INDEX.md`
- 維護 `/workspace/INDEX.md` 中央入口
- 確保檔案命名一致性
- 發現重複或過時的檔案

**不做的事：**
- 不寫實際內容
- 不執行分析任務

---

### Data Agent (Worker - 資料處理)

**核心職責：**
- 維護 `api_calls.json`、`tasks.json`、`news.json` 等資料檔案
- 更新統計數字（API 調用次數、任務完成數等）
- 驗證資料格式一致性
- 定期同步資料到 GitHub

**不做的事：**
- 不做複雜的數據分析
- 不做決策

---

### Preference Agent (Worker - 喜好分析)

**核心職責：**
- 分析用戶感興趣的主題（AI、能源、NVIDIA 等）
- 根據用戶偏好推薦新聞
- 記錄用戶互動模式
- 幫助 Mavis 更好地路由任務

**不做的事：**
- 不做技術分析
- 不直接回覆用戶

---

## 🔄 新增 Agent 流程

當需要新增 Agent 時：

1. 在 `data.json` 的 `agents` 陣列新增
2. 在 `api_calls.json` 的 `agentStats` 新增統計資料
3. 更新 `ARCHITECTURE.md` 的組織圖
4. 更新本文檔的 Agent 列表
5. Push 到 GitHub

---

*最後更新：2026-06-02 11:46*