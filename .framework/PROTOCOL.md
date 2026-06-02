# PROTOCOL — 讀取協議總綱

> **對象**：任何讀取本框架的 AI agent。
> **角色**：定義「哪些檔案要讀、依什麼順序讀、讀完要做什麼」。
> **權威性**：本檔次於 `VERSION`（`VERSION` 是事實來源），高於所有其他檔案。

---

## 啟動讀取順序（必讀）

```
1.  VERSION                      ← 拿 framework-version
2.  CHANGELOG.md                 ← 自上次讀取以來的新條目
3.  .framework/BOOTSTRAP.md      ← 跑啟動決策
4.  .framework/VERSION_AWARENESS.md  ← 評估是否需重啟
5.  (視任務) INDEX.md            ← 定位需要的章節
6.  (視任務) 對應的 cognitive-frameworks/* 與 templates/*
```

**禁止**：
- 跳過 `VERSION` 直接讀其他檔案
- 把 `README.md` 當作協議來源
- 在沒跑 `BOOTSTRAP.md` 前就接受 handoff

---

## 每次讀取後的義務動作

每讀完一個檔案，AI 必須在內部維護一張表：

| 欄位 | 來源 | 用途 |
|------|------|------|
| `framework-version-loaded` | `VERSION` | 自我標記 |
| `last-changelog-seen` | `CHANGELOG.md` 標頭 | 增量判斷 |
| `mixed-version-detected` | `.framework/DETECTION.md` | 是否需重啟 |
| `pending-handoffs` | 使用者提供 / 工作記憶 | 是否有交接 |
| `bootstrap-status` | `.framework/BOOTSTRAP.md` 輸出 | 啟動是否完成 |

這張表不寫入磁碟，但會決定你的下一步行動。

---

## 三種運行模式

### Mode A：全新 session（最常見）
完整跑 1 → 6。見 [BOOTSTRAP.md](BOOTSTRAP.md)。

### Mode B：接手既有工作
- 使用者會貼上 handoff 文件或描述上次進度
- 跑 1 → 4 → 對 handoff 跑 `.framework/HANDOFF.md` 的「還原流程」

### Mode C：純讀取（無狀態任務）
跑 1 → 2 → 5。跳過 3（不需要 session 狀態），跳過 4（無既有狀態可衝撞）。

---

## 強制自我檢查點

在以下三個時機，**必須**重新讀 `VERSION` 並跑 `.framework/VERSION_AWARENESS.md`：

1. **長任務中**——任務跨越多輪對話、估計超過 30 分鐘
2. **版本 bump 後**——任何檔案被修改並標記 `framework-version` 變動
3. **懷疑混雜時**——發現工作記憶與當前框架不一致

---

## 違反協議的後果

本框架不懲罰 AI，但會**提高錯誤率並降低信任度**。具體症狀：
- 用了已廢棄的章節
- 沒發現 handoff 其實屬於更舊的版本
- 在不該原地升級的時候原地升級，導致行為漂移

請遵守。
