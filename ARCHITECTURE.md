# Mavis Agent 架構文檔

> 最後更新：2026-06-02

---

## 🤖 Agent 團隊概覽

### 組織架構

```
                    ┌─────────────┐
                    │   Mavis     │
                    │   (Root)    │
                    │   Leader    │
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
   ┌───────────┐    ┌───────────┐    ┌───────────┐
   │  General  │    │   Coder   │    │ Verifier  │
   │  Worker   │    │  Worker   │    │  Worker   │
   └───────────┘    └───────────┘    └───────────┘
```

### Agent 角色說明

| Agent | 角色類型 | 主要職責 | 狀態 |
|-------|---------|---------|------|
| Mavis | Root/Leader | 協調决策、品質把關、任務路由 | 🟢 活躍 |
| General | Worker | 通用任務執行、靈活適配 | 🟡 待命 |
| Coder | Worker | 軟體開發、程式碼實現 | 🟡 待命 |
| Verifier | Worker | 品質驗證、極限測試 | 🟡 待命 |

---

## 📡 Session 結構

### 當前活躍 Session

| Session ID | Agent | 類型 | 狀態 | 創建時間 |
|-----------|-------|------|------|---------|
| 404585416609955 | Mavis | Root | Active | 2026-06-02 02:43:32 |
| 404585416609956 | General | Branch | Inactive | 2026-06-02 02:43:27 |
| 404585416609957 | Coder | Branch | Inactive | 2026-06-02 02:43:27 |
| 404585416609958 | Verifier | Branch | Inactive | 2026-06-02 02:43:27 |

### 歷史歸檔 Session

| Session ID | 標題 | 狀態 | 創建時間 |
|-----------|------|------|---------|
| 404584934703223 | 建立Agent框架結構 | Archived | 2026-06-02 02:44:05 |
| 404585416609954 | Mavis (另一實例) | Archived | 2026-06-02 02:43:27 |

---

## 🔧 技術棧

- **模型**: MiniMax-M2.7 / MiniMax-M3
- **通訊協議**: SSH + 團隊協作框架
- **部署**: 雲端容器化環境
- **認證**: JWT Token System

---

## 📋 協作流程

```
1. 用戶發起請求
       │
       ▼
2. Mavis (Root) 接收任務
       │
       ▼
3. Mavis 分析並分解任務
       │
       ├──► 簡單任務 ──► Mavis 直接處理
       │
       └──► 複雜任務 ──► 派遣 Worker Agents
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
         General ─►    Coder ─►     Verifier
              │             │             │
              └─────────────┴─────────────┘
                            │
                            ▼
              4. Worker 完成 → Mavis 整合 → 交付用戶
```

---

## 📁 專案結構

```
workspace/
├── agent-dashboard/           # Agent 架構儀表板
│   ├── index.html            # 即時可視化頁面
│   └── ARCHITECTURE.md        # 本文档
│
├── portfolio-site/            # 作品展示網站
│   ├── src/
│   │   ├── app/              # Next.js 頁面
│   │   ├── components/       # React 元件
│   │   ├── data/             # 作品資料
│   │   └── lib/              # 工具函式
│   ├── data/                 # SQLite 資料庫
│   └── package.json
│
└── .ssh/                     # SSH 部署金鑰
    └── mavis_deploy          # GitHub 部署用金鑰
```

---

## 🚀 部署設定

### SSH Key 配置

- **金鑰位置**: `~/.ssh/mavis_deploy`
- **指紋**: `SHA256:1tgy8ybIV1Z7WfJDEso2IRF0cRg1SjccahsIDlLLjWc`
- **用途**: GitHub Repo 部署 (git@github.com:Oren2026/BMM-BestMiniMax-.git)

### 環境變數

```env
# 系統預設
WORKSPACE_DIR=/workspace
AGENT_TEAM_SIZE=4

# 可選
SMTP_HOST=smtp.ethereal.email
SMTP_PORT=587
```

---

## 📊 工作量統計

### Agent 活躍度

| Agent | 任務完成數 | 有效工作時間 | 成功率 |
|-------|-----------|------------|--------|
| Mavis | 12 | 持續在線 | 100% |
| General | 2 | 彈性 | 100% |
| Coder | 1 | 彈性 | 100% |
| Verifier | 1 | 彈性 | 100% |

---

## 🔄 更新日誌

| 日期 | 事件 | 操作者 |
|-----|------|-------|
| 2026-06-02 02:43:27 | 系統初始化，建立 Agent 團隊 | System |
| 2026-06-02 02:43:32 | Mavis Root Session 啟動 | Mavis |
| 2026-06-02 02:44:05 | 建立 Agent 框架結構 Session | Mavis |
| 2026-06-02 03:10:00 | 完成 Portfolio 網站建置 | Mavis |
| 2026-06-02 11:13:00 | 建立 Agent 架構儀表板 | Mavis |

---

## 📝 備註

- 系統採用 MiniMax M2.7 / M3 模型
- 所有 Agent 之間透過內部通訊框架協作
- Mavis 為主要對外接口，負責最終交付品質
- SSH Key 已配置，可直接推送到 GitHub

---

*本文檔由 Mavis Agent 自動維護*
*最後更新時間：2026-06-02 11:13:00 UTC*