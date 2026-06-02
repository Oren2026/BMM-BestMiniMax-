# HANDOFF — 進度交接規範

> **對象**：要把目前 session 的進度交給下一棒（自己未來的 session / 別的 AI / 別的模型版本）的 agent。
> **角色**：定義 handoff 該怎麼寫、怎麼讀、怎麼驗證。

---

## 什麼時候要寫 handoff

強制時機：
1. **任務超過 30 分鐘**且**有跨 session 風險**——主動在切換前提議。
2. **偵測到版本落差**——依照 `VERSION_AWARENESS.md` 觸發「主動建議重啟」時，先寫 handoff 再交棒。
3. **任務自然結束**——交付前若還有未完成子任務，必須寫。

非強制：
- 短任務、一次性問答。

---

## handoff 必填欄位

最低限度（缺一就視為不可交接）：

```yaml
handoff-id: <uuid 或時間戳>
framework-version: <從 VERSION 抄過來>     # 必填！這是版本感知的錨點
schema-version: <從 VERSION 抄過來>
from-session: <session id 或描述>
to-session: <留空 / "next" / 接手者描述>
created-at: <ISO-8601>

context-summary: <3-5 句話講清楚任務在做什麼>
current-state: <目前完成到哪、卡在哪>
decisions-made: <已做的關鍵決策、為什麼>
open-questions: <還沒解決的問題>
next-actions: <下一棒第一件該做的事、第二件、…>
loaded-frameworks: <列出 cognitive-frameworks/* 的清單>
detection-notes: <有沒有觀察到版本混雜的跡象>
```

完整範本見 [`templates/handoff.template.md`](../templates/handoff.template.md)。
填寫範例見 [`examples/handoff.example.md`](../examples/handoff.example.md)。

---

## 寫 handoff 的紀律

### 對未來的自己好：寫得像給陌生人
接手者**沒有**你現在的脈絡。把背景寫清楚、把術語展開、把相對時間換成絕對時間（「昨天」→ 「2026-05-31」）。

### 對接手者好：把不確定的事標出來
任何「我覺得是這樣但沒驗證」的東西都要用 `confidence: low` 標記。

### 對自己好：留決策痕跡
不只寫「決定做 X」，要寫「為什麼不是 Y 與 Z」。接手者會感謝你。

---

## 還原流程（接手者該做什麼）

```
1. 讀 handoff
2. 讀 .framework/VERSION_AWARENESS.md
3. 比對 handoff.framework-version 與當前 VERSION
4. 比對結果：
     ├─ 相同 → 套用 handoff.context-summary，繼續 next-actions
     ├─ 不同（PATCH/MINOR）→ 套用 handoff 但讀 CHANGELOG 補齊差異
     ├─ 不同（MAJOR）→ 拒絕沿用，要求重啟
     └─ handoff 沒帶 framework-version → 視為不可信，要求重做
```

---

## handoff 過期規則

- **同版本**：handoff 在 7 天內可視為新鮮；超過請接手者重新確認。
- **跨版本**：即使時間未過，只要 `framework-version` 落差存在就視為過期。

---

## 常見錯誤

| 錯誤 | 後果 | 修正 |
|------|------|------|
| 沒填 `framework-version` | 接手者無法判斷是否過期 | 補上 |
| 寫「昨天做…」 | 接手者無從對齊時間軸 | 改成 ISO-8601 |
| 把整段對話貼進去 | 雜訊淹沒重點 | 用 context-summary 摘要 |
| 漏寫 open-questions | 接手者重踩同個坑 | 補上 |
| 沒指定 next-actions | 接手者不知從哪開始 | 補上 |
