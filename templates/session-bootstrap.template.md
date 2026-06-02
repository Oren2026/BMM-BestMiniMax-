# Session Bootstrap — <session name / date>

> 對應章節：`.framework/BOOTSTRAP.md` 的 Step 6。
> 使用時機：新 session 第一句話、接手既有工作前。
> 刪掉所有 `<…>` 佔位符再送出。

---

## 框架狀態

```yaml
framework-version: <從 VERSION 抄>
schema-version: <從 VERSION 抄>
last-updated: <從 VERSION 抄>
changelog-new-entries: <數量>
changelog-key-points:
  - <本 session 需要知道的第一件事>
  - <第二件事>
  - <第三件事>
```

## 版本感知

```yaml
version-awareness:
  last-known-version: <"unknown" | 之前的版本>
  delta-type: <none | patch | minor | major | bootstrap>
  restart-recommended: <true | false>
  detection-triggered: <true | false>
  reason: <一句話>
```

## 已載入資源

```yaml
cognitive-frameworks-loaded:
  - slug: <framework-slug>
    version: <X.Y.Z>
  - slug: <…>
    version: <…>
handoffs-received: <0 | 1 | …>
handoffs-source: <列出來源描述>
```

## 啟動結果

```yaml
bootstrap-status: <complete | incomplete | blocked>
block-reason: <string | null>
ready-for-task: <true | false>
```

---

## 一句話給使用者（可選）

> 若 `restart-recommended: true`，**必須**在這裡主動提示，並引用 [`.framework/VERSION_AWARENESS.md`](../.framework/VERSION_AWARENESS.md) 的「主動提示格式」。

<例如：「框架已從 v1.0.0 bump 到 v2.0.0（MAJOR），建議在新 session 重啟以避免行為漂移。」>
