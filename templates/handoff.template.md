# Handoff — <任務名稱>

> 對應章節：`.framework/HANDOFF.md`。
> 必填 `framework-version`，否則接手者可拒絕沿用。
> 參考範例：[`examples/handoff.example.md`](../examples/handoff.example.md)。

---

## 識別（必填）

```yaml
handoff-id: <uuid 或 ISO timestamp>
framework-version: <從 VERSION 抄>
schema-version: <從 VERSION 抄>
from-session: <session id 或描述>
to-session: <留空 / "next" / 接手者描述>
created-at: <ISO-8601>
```

## 背景

### 任務在做什麼
<3-5 句講清楚。比「做一個發表會規劃」更細：給誰、為什麼、deadline、in-scope / out-of-scope。>

### 為什麼會交接到這
<一句話：原本打算自己做嗎？卡在哪？為什麼換人？>

## 目前狀態

### 完成到哪
- [x] <已完成的子任務 1>
- [x] <已完成的子任務 2>
- [ ] <正在做的>
- [ ] <還沒開始的>

### 卡在哪
<具體描述卡點、已經試過什麼、為什麼沒過。>

## 已做決策（與理由）

| 決策 | 選項 | 選了什麼 | 為什麼 |
|------|------|----------|--------|
| <決策 1> | <A vs B vs C> | <選的> | <理由> |
| <決策 2> | <…> | <…> | <…> |

## 開放問題

- <問題 1：confidence: high | medium | low>
- <問題 2>

## 下一棒該做的事

1. <第一步、第二步、第三步⋯⋯ 給出具體動作，不要寫「繼續」。>
2. <…>
3. <…>

## 載入狀態

```yaml
loaded-frameworks:
  - slug: <framework-slug>
    version: <X.Y.Z>
detection-notes: <有沒有觀察到版本混雜跡象？寫「無」或具體描述>
open-files: <目前還開著哪些檔、哪些狀態是 in-memory>
```

## 給接手者的提醒

> 把任何「如果你跟我一樣會卡的地方」寫出來。例如：「使用者偏好先看結論再展開」「不要在驗收層只看自己寫的」。

- <提醒 1>
- <提醒 2>
