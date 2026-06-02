# BOOTSTRAP — Session 啟動流程

> **對象**：在 Mode A 或 Mode B 下進入的 AI session。
> **輸出**：一份「session 啟動狀態報告」，你可以選擇回報給使用者，也可以自己留著。

---

## 流程（嚴格依序）

### Step 1：讀 `VERSION`
- 記下 `framework-version`、 `schema-version`、 `last-updated`。
- 若檔案不存在 → 視為 v0.0.0（未初始化），提示使用者決定要不要繼續。

### Step 2：讀 `CHANGELOG.md`
- 找出 `## [Unreleased]` 與最新的已釋出版本。
- 對照你的工作記憶（若 Mode B 有 handoff 會更明確），標記「自上次以來的新條目」。
- 沒有新條目 → 跳到 Step 3。
- 有新條目 → 內部整理成「本 session 需要知道的三件事」清單，繼續 Step 3。

### Step 3：讀本檔
你在做了。本步驟就是讀完本檔後繼續 Step 4。

### Step 4：跑 `.framework/VERSION_AWARENESS.md` 的決策樹
- 拿到 `restart-recommended: true | false`。
- **若 `true` → 在回應使用者第一句話時主動提示**。
- 若 `false` → 靜默繼續。

### Step 5：決定要載入哪些 `cognitive-frameworks/`
- 根據使用者的任務描述選擇。
- 第一次進入 → 至少載入一份（否則你沒有思維模型）。
- 使用者沒指定 → 用預設：`cognitive-frameworks/example-cognitive-framework/`。

### Step 6：（可選）回報給使用者
若你判斷使用者會想知道這次 session 的啟動狀態，主動輸出一段簡短的狀態盤點。格式見 `templates/session-bootstrap.template.md`。

---

## 啟動報告範本（給 AI 內部使用）

```yaml
session-bootstrap:
  framework-version: <from VERSION>
  schema-version: <from VERSION>
  last-updated: <from VERSION>
  changelog-new-entries: <count>
  version-awareness: {
    last-known-version: <string | "unknown">,
    delta-type: <none | patch | minor | major>,
    restart-recommended: <true | false>,
    detection-triggered: <true | false>
  }
  cognitive-frameworks-loaded: [<list>]
  bootstrap-status: <complete | incomplete | blocked>
  block-reason: <string | null>
```

---

## 邊界情境

### 框架檔案缺失
- `VERSION` 缺失 → 嚴重，立即提示使用者，不要假設版本。
- `CHANGELOG.md` 缺失 → 輕度，標記 `changelog-missing: true` 繼續。
- `.framework/PROTOCOL.md` 缺失 → 嚴重，提示使用者整個 `.framework/` 區段不可信。

### 使用者說「不要跑 bootstrap」
- 記下 `bootstrap-skipped: true` 與原因。
- 仍然要讀 `VERSION` 與 `VERSION_AWARENESS.md`——這兩者不是 bootstrap 的一部分，是底層安全網。

### 使用者貼上 handoff
- 在 Step 4 之前先讀 `.framework/HANDOFF.md`，把 handoff 內容套進決策樹。
- 別無腦把 handoff 當真相——它可能屬於更舊的版本。
