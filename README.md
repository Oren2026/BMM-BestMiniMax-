# Mavis Agent KPI 與新聞追蹤系統

> 讓你一眼掌握 Agent 團隊的工作狀況、協作歷史與系統事件

---

## 🎯 功能特色

- **KPI 儀表板** — API 調用次數、任務完成數、專案數、協作事件
- **Agent 工作負載** — 每個 Agent 的貢獻視覺化
- **新聞牆** — 系統事件即時更新
- **任務追蹤** — 所有任務的狀態、負責人、優先級
- **事件時間軸** — 從系統初始化到現在的所有重要事件

---

## 📁 檔案結構

```
agent-dashboard/
├── index.html          # KPI 儀表板（HTML，視覺化呈現）
├── data.json           # Agent 基本資料
├── api_calls.json      # API 調用記錄
├── tasks.json          # 任務完成記錄
├── news.json           # 新聞 / 事件記錄
├── ARCHITECTURE.md     # 系統架構文檔
├── SYSTEM.md           # 系統維護文檔（SSH Key 等）
└── README.md           # 本文件
```

---

## 🔧 更新流程

### 新增新聞

編輯 `news.json`，添加新事件：

```json
{
  "id": "N006",
  "title": "新事件標題",
  "content": "事件描述",
  "category": "project",
  "agents": ["Mavis"],
  "project": "專案名",
  "timestamp": "2026-06-02T12:00:00Z",
  "priority": "medium"
}
```

### 新增任務

編輯 `tasks.json`，添加新任務：

```json
{
  "id": "T010",
  "name": "任務名稱",
  "description": "任務描述",
  "agent": "Mavis",
  "collaborators": ["General"],
  "project": "專案名",
  "status": "completed",
  "createdAt": "2026-06-02T12:00:00Z",
  "completedAt": "2026-06-02T12:30:00Z",
  "priority": "high"
}
```

### 新增專案

編輯 `tasks.json` 的 `projects` 陣列：

```json
{
  "id": "P005",
  "name": "專案名",
  "description": "專案描述",
  "agents": ["Mavis", "Coder"],
  "taskCount": 1,
  "status": "in-progress"
}
```

---

## 🚀 部署到 GitHub

每次更新後執行：

```bash
eval "$(ssh-agent -s)" && ssh-add ~/.ssh/mavis_deploy
cd /workspace/agent-dashboard
git add .
git commit -m "更新描述"
git push
```

---

## 🔐 SSH Key 設定

- **金鑰位置**: `~/.ssh/mavis_deploy`
- **指紋**: `SHA256:YbB1UQ5i7t2rdOZv/S15cds5SmnKUuaf5rPOLm3ch9A`
- **用途**: `git@github.com:Oren2026/BMM-BestMiniMax-.git`

---

## 📊 資料格式

### news.json categories

| Category | Label | Color |
|----------|-------|-------|
| system | 系統 | #8b5cf6 |
| project | 專案 | #3b82f6 |
| deployment | 部署 | #22c55e |
| collaboration | 協作 | #f97316 |

### task status

| Status | 說明 |
|--------|------|
| completed | 已完成 |
| in-progress | 進行中 |
| pending | 待處理 |

### task priority

| Priority | 說明 |
|----------|------|
| critical | 緊急 |
| high | 高 |
| medium | 中 |
| low | 低 |

---

*本系統由 Mavis Agent 自動維護*
*最後更新：2026-06-02 11:32:00 UTC*