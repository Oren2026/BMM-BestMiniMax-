# Session Bootstrap — 2026-06-01 接手 release-plan 任務

> 對應章節：`.framework/BOOTSTRAP.md` Step 6。
> 情境：使用者說「繼續昨天那個發表會規劃」，AI 接手既有 handoff。

---

## 框架狀態

```yaml
framework-version: 1.0.0
schema-version: 1
last-updated: 2026-06-01
changelog-new-entries: 0
changelog-key-points: []
```

## 版本感知

```yaml
version-awareness:
  last-known-version: "1.0.0"
  delta-type: none
  restart-recommended: false
  detection-triggered: false
  reason: "handoff 與當前 VERSION 一致，無落差"
```

## 已載入資源

```yaml
cognitive-frameworks-loaded:
  - slug: layered-task-execution
    version: 1.0.0
handoffs-received: 1
handoffs-source:
  - "examples/handoff.example.md（由昨天 session 寫出）"
```

## 啟動結果

```yaml
bootstrap-status: complete
block-reason: null
ready-for-task: true
```

---

## 一句話給使用者

> ✅ 框架就緒（v1.0.0）、handoff 已套用、載入 LTE 框架中。昨天已完成的子任務見下表，要不要我先摘要再繼續？

---

## 邊界範例：偵測到 major 落差

```yaml
framework-version: 2.0.0
schema-version: 2
changelog-new-entries: 3

version-awareness:
  last-known-version: "1.4.2"
  delta-type: major
  restart-recommended: true
  detection-triggered: true
  reason: "CHANGELOG 顯示 PROTOCOL.md 讀取順序變更，舊決策樹失效"

bootstrap-status: blocked
block-reason: "major version mismatch，建議重啟 session"
ready-for-task: false
```

### 對應給使用者的提示

> ⚠️ 框架重啟建議
> - 原因：handoff 標記 framework-version 1.4.2，當前為 2.0.0（MAJOR），PROTOCOL 讀取順序已變更。
> - 建議動作：開新 session 並重跑 BOOTSTRAP。
> - 影響：沿用 1.4.2 行為會誤觸已廢棄的 DETECTION 規則。
> - 替代選項：若任務極短（< 5 分鐘）且不涉及 PROTOCOL，可原地升級。
