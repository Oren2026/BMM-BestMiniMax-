# Agent Framework — CLI + GUI

> 零依賴的 Python CLI + 自動產生的 HTML 儀表板 + 自動產生的 AI system prompt
> 讓你用 GUI 介面（瀏覽器、AI 工具的 system prompt 欄位）直接駕馭整套框架。

---

## 一句話

```bash
bash install.sh                 # 安裝
agent-fw status                 # 看狀態
agent-fw bootstrap              # 開新 session
agent-fw report --open          # 開瀏覽器看儀表板
agent-fw prompt --for claude    # 產生 AI system prompt
```

---

## 安裝

### 方式 A：一行搞定

```bash
cd /path/to/agent-framework
bash install.sh
```

裝到 `~/.local/bin/agent-fw` 與 `~/.local/share/agent-fw/`。

如果 `~/.local/bin` 不在 PATH，照著提示加：

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### 方式 B：自訂路徑

```bash
bash install.sh --prefix=/opt/agent-fw
```

### 方式 C：不安裝，直接用

```bash
./agent-fw status
```

---

## 命令總覽

```
agent-fw <cmd> [opts]

  init                  在當前目錄初始化 framework
  status                看當前狀態
  read [path]           照協議順序列出要讀的檔案
  bootstrap             跑 session 啟動（產出報告）
  tui                   互動式選單

  bump <type>           bump 版本（major|minor|patch）
  detect                跑多版本混雜偵測
  validate              驗證 framework 完整性

  handoff new           建立新 handoff
  handoff validate <f>  驗證 handoff

  new-framework <slug>  從 _template/ 複製出新認知框架

  prompt [--for TARGET] 產生給 AI 的 system prompt
  report [--open]       產生 HTML 儀表板

  install / uninstall   安裝到 PATH / 移除
```

每個命令都能加 `--root PATH` 指定 framework 根目錄，加 `--no-color` 關色彩。

---

## 與 GUI 工具整合（重點）

### 1. 給 AI 工具（Claude / Cursor / opencode / Claude Code）—— 用 `prompt` 命令

```bash
# 產生給 Claude 的 system prompt
agent-fw prompt --for claude -o prompt.md

# 產生通用版本
agent-fw prompt --for generic -o prompt.md
```

然後在 AI 工具的「System Prompt」欄位貼上 `prompt.md` 的內容。AI 之後就會：
- 開頭先讀 `VERSION`
- 照讀取協議走
- 偵測到版本落差就主動建議重啟

**框架升級時**：再跑一次 `agent-fw prompt`，把新內容貼回去就好。

---

### 2. 瀏覽器儀表板 —— 用 `report` 命令

```bash
agent-fw report --open
```

這會產生 `framework-dashboard.html` 並用瀏覽器開啟。你可以看到：
- 當前 framework 版本
- Detection 健康度（5 條規則的觸發狀態）
- Validation 結果
- 已載入的 cognitive frameworks
- 最近 10 條 CHANGELOG

**沒有任何外部依賴**（純 HTML + CSS，可印表機友善）。

---

### 3. 互動式選單 —— 用 `tui` 命令

```bash
agent-fw tui
```

純文字 GUI，類似 `lazygit` / `htop`。所有命令都能從選單點選。

---

## 典型工作流程

### 情境 A：新 session 開工

```bash
# 1. 跑 bootstrap 拿到啟動報告
agent-fw bootstrap

# 2. （選用）看 HTML 儀表板
agent-fw report --open

# 3. 開始任務
```

### 情境 B：接手別人（或自己之前）的 session

```bash
# 1. 建立 handoff
agent-fw handoff new --task "release-plan" --out handoff.md

# 2. 編輯 handoff.md 把 context 補完

# 3. 下一棒驗證 + bootstrap
agent-fw handoff validate handoff.md
agent-fw bootstrap --handoff handoff.md
```

### 情境 C：框架升級

```bash
# 1. bump
agent-fw bump minor --reason "新增 decision-priority-matrix 框架"

# 2. 驗證
agent-fw validate

# 3. 重新產生 AI system prompt
agent-fw prompt --for claude -o prompt.md

# 4. 把新 prompt.md 內容貼到 AI 工具
```

### 情境 D：發現 AI 行為怪怪的

```bash
# 1. 跑偵測
agent-fw detect

# 2. 跑驗證
agent-fw validate

# 3. 看 HTML 儀表板找問題
agent-fw report --open
```

---

## 為什麼是「CLI + GUI 兩棲」

| 你要什麼 | 工具 |
|----------|------|
| 在終端快速跑 | `agent-fw <cmd>` |
| 在圖形介面看全景 | `agent-fw report --open` |
| 跟 AI 整合 | `agent-fw prompt` 然後貼 system prompt |
| 不熟指令 | `agent-fw tui` 互動選單 |
| 自動化 | `agent-fw <cmd> --format json` 串 API |
| CI / Git hook | 把 `agent-fw validate` 串進 pre-commit |

---

## 跟 opencode / Cursor / Claude Code 整合示意

```
┌─────────────────────────────────┐
│  AI 工具（opencode / Cursor）   │
│                                 │
│  System Prompt:                 │
│  ┌───────────────────────────┐  │
│  │ # Agent Framework v1.0.0 │  │ ←── 從 agent-fw prompt 產出
│  │ ## 讀取協議（嚴格遵守）  │  │
│  │ ## 版本感知決策          │  │
│  │ ## 多版本混雜偵測        │  │
│  └───────────────────────────┘  │
│                                 │
│  每次開新 session：              │
│  1. AI 讀 VERSION               │
│  2. AI 跑 BOOTSTRAP             │
│  3. AI 評估要不要重啟            │
│  4. 開始工作                    │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│  你的 GUI 介面                  │
│  ┌───────────────────────────┐  │
│  │ framework-dashboard.html  │  │ ←── 從 agent-fw report --open 開
│  │ · 版本 v1.0.0             │  │
│  │ · Detection: CLEAN        │  │
│  │ · Validation: 46/46 OK    │  │
│  │ · 3 個 cognitive framework│  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

---

## 環境變數

| 變數 | 作用 |
|------|------|
| `NO_COLOR=1` | 關掉所有色彩 |
| `FORCE_COLOR=1` | 強制啟用色彩（即使不是 TTY） |
| `AGENT_FW_DEBUG=1` | 印出完整 traceback |

---

## 架構

```
agent-fw                       # 可執行檔
agent_fw/                      # 套件
├── cli.py                     # CLI 入口
├── core.py                    # 共用：版本、frontmatter、檔案定位
├── ui.py                      # 純 ANSI 顯示
├── version.py                 # 版本讀寫
├── bootstrap.py               # session 啟動
├── detection.py               # 5 條偵測規則
├── handoff.py                 # 進度交接
├── bump.py                    # 版本 bump
├── changelog_update.py        # CHANGELOG 自動追加
├── framework_new.py           # 從 _template 複製新框架
├── validate.py                # 框架完整性
├── prompt.py                  # 產生 AI system prompt
└── report.py                  # 產生 HTML 儀表板
```

**零外部依賴**。只要 Python 3.8+ 就能跑。

---

## 給開發者

### 加新子命令

1. 在 `agent_fw/` 加新模組
2. 在 `cli.py` 註冊子命令與 handler
3. 跑 `python3 ./agent-fw <new-cmd> --help` 確認

### 改 detection 規則

1. 改 `detection.py` 的規則實作
2. bump `DETECTION_RULES_VERSION`
3. 改 `.framework/DETECTION.md` 的 `detection-rules-version: 1` → 2
4. bump framework 版本（至少 minor）
5. `agent-fw validate` 確認

### 改 framework 結構

1. 改檔案
2. `agent-fw validate` 確認無 broken links
3. `agent-fw bump <type> --reason "..."`
4. `agent-fw prompt` 重新產生 AI prompt

---

## 授權

MIT
