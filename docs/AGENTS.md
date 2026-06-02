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

---

## 🎯 各角色詳細職責

### Mavis (Root/Leader)

**核心職責：**
- 接收用戶所有請求
- 任務分析與分解
- 派遣適當的 Worker Agent
- 最終品質把關與交付
- 維護系統文檔

**不做的事：**
- 不寫實際程式碼（除非簡單任務）
- 不執行需要多個 Worker 的複雜任務（交給團隊）

**Session ID:** `404585416609955`
**模型:** MiniMax-M2.7

---

### General (Worker - 通用工作者)

**核心職責：**
- 執行多樣化的一般任務
- 資料研究與分析
- 非專業領域的簡單處理
- 協助文書與文件生成

**不做的事：**
- 不處理高風險決定
- 不做複雜的系統架構設計

**Session ID:** `404585416609956`
**模型:** MiniMax-M2.7

---

### Coder (Worker - 軟體工程師)

**核心職責：**
- 程式碼開發
- 功能實現
- 架構設計建議
- 代碼質量優化

**不做的事：**
- 不做產品決策
- 不處理非技術問題

**Session ID:** `404585416609957`
**模型:** MiniMax-M2.7

---

### Verifier (Worker - 驗證專家)

**核心職責：**
- 品質驗證
- 發現問題與漏洞
- 極限測試
- 安全審查

**不做的事：**
- 不寫新功能代碼
- 不做架構決策

**Session ID:** `404585416609958`
**模型:** MiniMax-M2.7

---

## 📊 KPI 計算方式

### API 調用次數
- 每個獨立的 API 請求算 1 次
- 記錄在 `/workspace/agent-dashboard/api_calls.json`

### 任務完成數
- 每個 completed 狀態的任務算 1 次
- 記錄在 `/workspace/agent-dashboard/tasks.json`

### 專案處理數
- 每個 Agent 參與的專案數
- 從 `tasks.json` 的 `project` 欄位統計

### 協作次數
- 有 `collaborators` 的任務才算協作
- 記錄在 `api_calls.json` 的 `collaborationEvents`

---

## 🔄 新增 Agent 流程

當需要新增 Agent 時：

1. 在 `data.json` 的 `agents` 陣列新增
2. 在 `api_calls.json` 的 `agentStats` 新增統計資料
3. 更新 `ARCHITECTURE.md` 的組織圖
4. 更新本文檔的 Agent 列表
5. Push 到 GitHub

---

*最後更新：2026-06-02 11:36*