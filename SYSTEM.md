# Agent KPI 與新聞追蹤系統

> 最後更新：2026-06-02 11:32:00 UTC

---

## 📊 KPI 儀表板

### 系統使用統計

| 指標 | 數值 |
|------|------|
| 總 API 調用次數 | 47 |
| 任務完成數 | 15 |
| 專案數 | 4 |
| Agent 協作事件 | 23 |

### Agent 工作負載

| Agent | 調用次數 | 處理專案數 | 協作次數 |
|-------|---------|-----------|---------|
| Mavis (Root) | 32 | 4 | 18 |
| General | 8 | 2 | 5 |
| Coder | 4 | 1 | 2 |
| Verifier | 3 | 1 | 2 |

---

## 📰 新聞 / 任務記錄

### 2026-06-02

| 時間 | 事件 | 負責 Agent | 相關專案 |
|------|------|-----------|---------|
| 02:43 | Agent 團隊初始化 | Mavis | 系統架構 |
| 03:10 | Portfolio 網站建置完成 | Mavis + General | Portfolio 專案 |
| 11:13 | Agent 架構儀表板上線 | Mavis | Dashboard |
| 11:28 | Agent Dashboard 部署到 GitHub | Mavis | Dashboard |
| 11:32 | KPI 新聞系統建立 | Mavis | KPI System |

---

## 🔧 系統架構

```
用戶請求
    │
    ▼
Mavis (Root) ── 接收並分配任務
    │
    ├── 記錄 API 調用到 api_calls.json
    │
    ├── General ── 執行一般任務 ── 記錄到 tasks.json
    │
    ├── Coder ── 軟體開發 ── 記錄到 tasks.json
    │
    └── Verifier ── 品質驗證 ── 記錄到 tasks.json
    │
    ▼
所有結果同步到 GitHub (agent-dashboard 專案)
```

---

## 📁 資料檔案結構

```
agent-dashboard/
├── index.html              # KPI 儀表板 (HTML)
├── ARCHITECTURE.md         # 架構文檔
├── data.json               # Agent 資料
├── api_calls.json          # API 調用記錄 (新增)
├── tasks.json              # 任務完成記錄 (新增)
├── news.json               # 新聞 / 事件記錄 (新增)
└── README.md               # 系統說明 (新增)
```

---

## 🚀 使用方式

### 新增新聞/事件

1. 編輯 `news.json`，添加新事件
2. 執行 `git push` 同步到 GitHub

### 追蹤任務

1. 編輯 `tasks.json`，記錄新任務
2. 執行 `git push` 同步到 GitHub

### 查看統計

直接開啟 `index.html` 查看即時 KPI 儀表板

---

## 🔐 SSH Key 提醒（重要！）

金鑰位置：`~/.ssh/mavis_deploy`

每次重啟後需要重新設定：
```bash
eval "$(ssh-agent -s)" && ssh-add ~/.ssh/mavis_deploy
```

---

*本系統由 Mavis Agent 自動維護*