# 🔧 系統維護指南

> 包含 SSH Key 設定、Git 操作、系統維護等重要資訊

---

## 🔐 SSH Key 設定（重要！）

**金鑰位置：** `~/.ssh/mavis_deploy`
**指紋：** `SHA256:YbB1UQ5i7t2rdOZv/S15cds5SmnKUuaf5rPOLm3ch9A`
**公鑰：** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAfhDVw//kYyGWobcXVaZdy96V1oQqjDWEdTfkZytOvE mavis@minimax-agent`
**用途：** `git@github.com:Oren2026/BMM-BestMiniMax-`

### 每次重啟後需要執行的指令：

```bash
eval "$(ssh-agent -s)" && ssh-add ~/.ssh/mavis_deploy
```

---

## 📁 專案結構（更新版）

```
/workspace/
├── INDEX.md                    # 中央入口 ⭐
│
├── agent-dashboard/           # 🤖 Agent KPI 系統
│   ├── docs/                  # 📋 專案文檔
│   │   ├── INDEX.md          # 專案入口
│   │   ├── AGENTS.md         # Agent 角色 ⭐
│   │   ├── WORKFLOW.md       # 協作流程 ⭐
│   │   ├── UPDATE_GUIDE.md   # 更新指南 ⭐
│   │   └── SYSTEM.md         # 本文件
│   │
│   ├── index.html             # KPI 儀表板
│   ├── data.json              # Agent 資料
│   ├── api_calls.json         # API 調用 ⭐
│   ├── tasks.json             # 任務追蹤 ⭐
│   └── news.json              # 新聞事件 ⭐
│
├── portfolio/                  # 🎨 Portfolio 網站
│   ├── docs/
│   │   └── INDEX.md          # 專案入口
│   └── site/                  # 網站程式碼
│
└── shared/                    # 共享資源（預留）
```

---

## 🚀 Git 推送指令

```bash
# 設定 SSH（每次重啟後要做）
eval "$(ssh-agent -s)" && ssh-add ~/.ssh/mavis_deploy

# 切換到 agent-dashboard
cd /workspace/agent-dashboard

# 更新並推送
git add .
git commit -m "更新描述"
GIT_SSH_COMMAND="ssh -i ~/.ssh/mavis_deploy" git push
```

---

## 📊 資料檔案職責

| 檔案 | 職責 | 更新頻率 |
|------|------|---------|
| `api_calls.json` | 記錄 API 調用次數與歷史 | 每次調用 |
| `tasks.json` | 記錄任務狀態與專案 | 每個任務完成 |
| `news.json` | 記錄重要事件與新聞 | 每個重要事件 |
| `data.json` | Agent 基本資料 | 新增 Agent 時 |

---

## ⚙️ 新增專案流程

1. 在 `/workspace/` 下建立新資料夾
2. 建立 `docs/INDEX.md` 作為專案入口
3. 在 `/workspace/INDEX.md` 加入專案連結
4. 如需 Git 同步，在 `agent-dashboard` 的 `tasks.json` 新增任務

---

*最後更新：2026-06-02 11:36*