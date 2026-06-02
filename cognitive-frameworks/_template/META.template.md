# META — <Framework Name>

> **給 AI 讀者**：本檔是元資料，回答「這份框架是給誰用的、相容於什麼」。**不**回答「怎麼用」——那是 `FRAMEWORK.md` 的工作。

---

## 識別

```yaml
framework-slug: <kebab-case-id>            # 穩定 ID，發布後不可改
framework-name: <人類可讀名稱>
framework-version: <X.Y.Z>                 # 採 SemVer
status: <draft | stable | deprecated>
```

## 相容性

```yaml
compat-with-agent-version: >=<X.Y.Z>       # 與哪個版本以後的 agent framework 相容
compat-with-detector-rules: <int>          # 對應 .framework/DETECTION.md 的規則版本
min-context-window: <tokens | null>         # 執行本框架至少需要的 context 大小（可選）
recommended-model-capability: <string>     # 例：「function-calling」「long-context」
```

## 元資料

```yaml
author: <人 / 組織 / AI 代理>
created-at: <YYYY-MM-DD>
last-updated: <YYYY-MM-DD>
tags: [<標籤 1>, <標籤 2>]
language: <zh-TW | en | …>
```

## 演進

```yaml
supersedes: [<被本框架取代的 slug>]        # 若 status: deprecated，留空
superseded-by: <取代本框架的 slug>          # 若 status: deprecated 才填
migration-from-superseded: <path>          # 從舊版遷移的指引
```

## 適用對象

- **誰應該用**：<角色 1>、<角色 2>
- **誰不該用**：<角色 1>、<角色 2>
- **任務類型**：<任務類型 1>、<任務類型 2>

## 與其他框架的關係（精簡版）

- 互補：<slug 清單>
- 取代：<slug 清單>
- 衝突：<slug 清單>

## 變更紀錄摘要

> 完整紀錄在 `FRAMEWORK.md` 末或外部 changelog；本欄只放與「相容性 / 語義」有關的關鍵節點。

- <framework-version>：<一句話講清楚這版變了什麼、為什麼需要 bump>
- <framework-version>：<...>
