# 📁 Agent Dashboard - KPI 與新聞追蹤系統

> Agent 團隊工作負載監控與新聞事件記錄

---

## 🎯 專案概覽

| 項目 | 內容 |
|------|------|
| **類型** | 監控儀表板 |
| **技術** | HTML + JavaScript (無需後端) |
| **目錄** | `/workspace/agent-dashboard/` |
| **文檔** | `/workspace/agent-dashboard/docs/` |
| **GitHub** | `Oren2026/BMM-BestMiniMax-` |

---

## 📂 目錄結構

```
agent-dashboard/
├── docs/                   # 📋 專案文檔
│   ├── INDEX.md           # 本文件
│   ├── AGENTS.md          # Agent 角色與職責
│   ├── WORKFLOW.md        # 協作流程
│   └── UPDATE_GUIDE.md    # 更新指南
│
├── index.html              # 🎯 KPI 儀表板（直接用瀏覽器開）
├── data.json              # Agent 基本資料
├── api_calls.json         # API 調用記錄
├── tasks.json             # 任務追蹤
├── news.json              # 新聞事件
├── ARCHITECTURE.md        # 系統架構
├── SYSTEM.md             # 維護指南（含 SSH Key）
└── README.md             # 使用說明
```

---

## 🎯 主要功能

- [x] KPI 儀表板（API 調用、任務、專案、協作）
- [x] Agent 工作負載視覺化
- [x] 新聞牆（系統事件即時更新）
- [x] 任務追蹤表（狀態、優先級、負責人）
- [x] 事件時間軸
- [x] 組織架構圖

---

## 🚀 查看方式

直接用瀏覽器開啟 `index.html`：
```bash
# 方式1：直接開
open /workspace/agent-dashboard/index.html

# 方式2：用 python 跑簡易伺服器
cd /workspace/agent-dashboard && python3 -m http.server 8080
# 然後開 http://localhost:8080
```

---

## 🔧 更新流程

### 新增新聞
編輯 `news.json`，添加新事件後 push 到 GitHub

### 新增任務
編輯 `tasks.json`，添加新任務後 push 到 GitHub

詳細指南請看 `/workspace/agent-dashboard/docs/UPDATE_GUIDE.md`

---

## 📊 當前統計

| 指標 | 數值 |
|------|------|
| API 調用 | 47 次 |
| 任務完成 | 15 項 |
| 專案數 | 4 個 |
| 協作事件 | 23 次 |

---

*最後更新：2026-06-02 11:36*