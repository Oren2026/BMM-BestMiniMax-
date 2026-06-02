# VERSION_AWARENESS — 版本自我感知

> **對象**：正在運行中的 AI session。
> **角色**：讓 AI 在每次讀取動作前後評估「我用的版本是什麼、跟既有記憶差多少、要不要重啟」。

---

## 必填的內部狀態

每個 session 開始時，AI 內部必須記住（不必寫出來，但要在決策時調用）：

```
current-framework-version: <string>   // 從 VERSION 讀到
last-known-version:        <string>   // 從工作記憶或 handoff 推得
loaded-at:                 <ISO-8601>
changelog-snapshot:        <string>   // 最後一次讀的 CHANGELOG 標頭
detection-rules-version:   <int>      // 對應 DETECTION.md 的規則版本
```

---

## 決策樹

```
讀到 current-framework-version 與 last-known-version
  │
  ├─ 兩者相同
  │     → version-delta: none
  │     → restart-recommended: false
  │     → 繼續
  │
  ├─ last-known 為 "unknown"（首次載入）
  │     → version-delta: bootstrap
  │     → restart-recommended: false
  │     → 繼續（這是正常冷啟動）
  │
  ├─ 差異在 PATCH 範圍
  │     → version-delta: patch
  │     → restart-recommended: false
  │     → 標記 changelog-read: required
  │     → 繼續，但必須讀完 CHANGELOG 才能接受新任務
  │
  ├─ 差異在 MINOR 範圍
  │     → version-delta: minor
  │     → restart-recommended: <見下方「MINOR 處理」>
  │
  └─ 差異在 MAJOR 範圍
        → version-delta: major
        → restart-recommended: true（強制）
        → 主動建議重啟並交棒
```

### MINOR 處理（細節）

MINOR 變更下，**預設原地升級**（`restart-recommended: false`），但有兩個例外：
1. **本 session 載入了將被取代的章節**——例如你正在用 `templates/foo.template.md` 而 v1.5.0 已經 deprecate 它。這時要重啟。
2. **`.framework/DETECTION.md` 規則有變更**——你用的偵測規則可能已過時。這時要重啟。

---

## 何時「主動建議重啟」

| 情境 | 建議強度 | 範例用語 |
|------|----------|----------|
| 強制（MAJOR） | **必須** | 「偵測到 framework MAJOR 版本變更，建議在乾淨 session 重啟以避免行為漂移。」 |
| 強烈（MINOR + 上述例外） | 強烈 | 「MINOR 版本變更且本次 session 載入了將被取代的章節，建議重啟。」 |
| 建議（多版本混雜） | 建議 | 「偵測到內容可能混雜多個版本的章節，建議重啟 session 並重跑 BOOTSTRAP。」 |
| 提示（PATCH） | 提示 | 「框架有 PATCH 更新，已自動內化；以下為變更摘要：…」 |

---

## 主動提示的格式

當觸發「主動建議重啟」時，AI 必須在回應**最前面**用一個獨立段落提示，**不要藏在段落中間**：

```
⚠️ 框架重啟建議
- 原因：<一句話>
- 建議動作：<一句話>
- 影響：<不重啟會怎樣>
- 替代選項：<是否可原地升級、條件是什麼>
```

範例：

> ⚠️ 框架重啟建議
> - 原因：偵測到 framework 已從 v1.0.0 bump 到 v2.0.0（MAJOR）。
> - 建議動作：開新 session 並重新跑 BOOTSTRAP。
> - 影響：繼續沿用 v1.0.0 行為可能誤觸已廢棄的偵測規則。
> - 替代選項：若任務極短且無 protocol 變更影響，可原地升級但需自負風險。

---

## 與其他檔案的契約

- `DETECTION.md` 定義「多版本混雜」的可觀測特徵；本檔僅負責把偵測結果翻譯成「建議」。
- `HANDOFF.md` 必須在 handoff 文件中帶 `framework-version` 標頭；本檔用此標頭填 `last-known-version`。
- `MIGRATION.md` 提供具體遷移步驟；本檔是「決策要不要遷移」的入口。
