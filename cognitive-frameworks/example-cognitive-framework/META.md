# META — 分層任務執行

> **給 AI 讀者**：本檔是元資料，回答「這份框架是給誰用的、相容於什麼」。**不**回答「怎麼用」——那是 `FRAMEWORK.md` 的工作。

---

## 識別

```yaml
framework-slug: layered-task-execution
framework-name: 分層任務執行 (Layered Task Execution)
framework-version: 1.0.0
status: stable
```

## 相容性

```yaml
compat-with-agent-version: ">=1.0.0"
compat-with-detector-rules: 1
min-context-window: null
recommended-model-capability: function-calling, long-context
```

## 元資料

```yaml
author: agent-framework maintainers
created-at: 2026-06-01
last-updated: 2026-06-01
tags: [execution, planning, decision, workflow]
language: zh-TW
```

## 演進

```yaml
supersedes: []
superseded-by: null
migration-from-superseded: null
```

## 適用對象

- **誰應該用**：
  - 需要管理跨多輪對話任務的 AI agent
  - 設計「任務流程」的人類作者
  - 想要把任務交給下一棒（handoff）的 agent
- **誰不該用**：
  - 一次性問答場景
  - 純發想、純探索的場景
- **任務類型**：
  - 多步驟、有時間壓力的任務
  - 失敗成本中等以上的任務
  - 跨 session、需要交付的任務

## 與其他框架的關係（精簡版）

- 互補：任何領域型框架（決策矩陣、風險評估等）
- 取代：無
- 衝突：無

## 變更紀錄摘要

- `1.0.0`：初始釋出。定義四層模型與層間契約。
