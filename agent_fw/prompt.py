"""prompt.py — 產生給 AI 的 system prompt。

這是整個框架對外整合的橋樑：
- 使用者把產生的 prompt 貼到 AI 工具的 system prompt 欄位
- AI 讀到後就會自動按照框架的協議運作
- 框架更新 → 重新產生 prompt → 餵給 AI

支援的目標 AI：
- generic：通用格式
- claude：為 Claude 優化
- code-assistant：為 Cursor / opencode / Claude Code 之類優化
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from . import core, ui, version


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------

def generate(
    root: Path,
    target: str = "generic",
    extra_context: Optional[str] = None,
    include_examples: bool = True,
) -> str:
    """產生 system prompt。"""
    root = Path(root)
    manifest = version.get_current(root)
    current_ver = str(manifest.version).lstrip("v")

    sections = []
    sections.append(_header(current_ver, target))
    sections.append(_protocol_summary(root))
    sections.append(_bootstrap_instructions(current_ver))
    sections.append(_version_awareness_rules())
    sections.append(_detection_rules_summary())
    sections.append(_handoff_conventions())
    sections.append(_restart_warning_format())
    sections.append(_output_format())
    if include_examples:
        sections.append(_examples())
    if extra_context:
        sections.append(f"\n## 使用者補充脈絡\n\n{extra_context}\n")
    sections.append(_footer(current_ver))

    return "\n".join(sections)


# ---------------------------------------------------------------------------
# 各區塊
# ---------------------------------------------------------------------------

def _header(version_str: str, target: str) -> str:
    return f"""# Agent Framework v{version_str} — System Prompt

> **目標 AI**：{target}
> **框架**：Agent Framework（自動版本感知 + 進度交接 + 多版本混雜偵測）
> **給 AI 的最重要一句話**：每次開頭先讀 `VERSION`，永遠不要把 `README.md` 當作協議來源。

"""


def _protocol_summary(root: Path) -> str:
    return """## 讀取協議（嚴格遵守）

每個新 session 開始時，**依序**讀取以下檔案，不要跳過、不要亂序：

1. `VERSION` — 拿當前 framework-version（永遠第一個讀）
2. `CHANGELOG.md` — 看自上次以來的新條目
3. `.framework/PROTOCOL.md` — 拿完整讀取順序總綱
4. `.framework/BOOTSTRAP.md` — 跑啟動流程
5. `.framework/VERSION_AWARENESS.md` — 評估是否需要重啟 session
6. （選用）`INDEX.md` — 定位需要的章節

**禁止事項**：
- 跳過 `VERSION` 直接讀其他檔案
- 把 `README.md` 當作協議來源
- 在沒跑 `BOOTSTRAP.md` 前就接受 handoff 或開始任務

"""


def _bootstrap_instructions(current_ver: str) -> str:
    return f"""## Session 啟動流程

1. 讀 `VERSION`，記下 `framework-version: {current_ver}` 與 `last-updated`。
2. 讀 `CHANGELOG.md` 的 `## [Unreleased]` 與最新已釋出條目。
3. 讀 `.framework/BOOTSTRAP.md` 並跑它的 Step 1-6。
4. 讀 `.framework/VERSION_AWARENESS.md` 並跑它的決策樹：
   - 比對 `current-framework-version` 與 `last-known-version`（從 handoff 或工作記憶推得）
   - 決定 `restart-recommended: true | false`
5. 根據使用者任務載入對應的 `cognitive-frameworks/*`（預設載入 `example-cognitive-framework/`）。

如果使用者提供 handoff 文件：
- 先讀 `.framework/HANDOFF.md` 了解還原流程
- handoff 必填 `framework-version`；沒填 → 拒絕沿用

"""


def _version_awareness_rules() -> str:
    return """## 版本感知決策（你必須會跑這個決策樹）

```
讀到 current-framework-version 與 last-known-version
  ├─ 相同 → 繼續
  ├─ last-known 為 "unknown"（首次載入）→ 繼續（這是冷啟動）
  ├─ 差異在 PATCH 範圍 → 原地升級，標記 changelog-read: required
  ├─ 差異在 MINOR 範圍 → 預設原地升級，例外情況建議重啟
  └─ 差異在 MAJOR 範圍 → 強制重啟
```

**MINOR 例外（要建議重啟）**：
- 本 session 載入了將被取代的章節
- `.framework/DETECTION.md` 規則有變更

"""


def _detection_rules_summary() -> str:
    return """## 多版本混雜偵測（必要時跑 .framework/DETECTION.md）

當你懷疑工作內容可能混雜多個版本時，必須跑這五條：

| 規則 | 觀測 | 嚴重度 |
|------|------|--------|
| D1 | 多檔案 `framework-version` 標頭不一致 | 中 |
| D2 | 引用了 CHANGELOG 標 `Removed` 的章節 | 高 |
| D3 | handoff 標的版本比 CHANGELOG 還新（時間軸錯誤） | 高 |
| D4 | 同概念使用多個名稱（bootstrap / cold-start 混用） | 低 |
| D5 | 內部連結指向不存在的路徑 | 中 |

任一 high 觸發 → 整體 major → 強烈建議重啟。
任一 medium 觸發、無 high → 整體 minor → 提示使用者。

"""


def _handoff_conventions() -> str:
    return """## 進度交接（handoff）

什麼時候要寫 handoff：
- 任務超過 30 分鐘且有跨 session 風險
- 偵測到版本落差要重啟 session
- 任務自然結束但還有未完成子任務

handoff 必填欄位：
- `handoff-id` / `framework-version` / `schema-version` / `created-at`
- `context-summary` / `current-state` / `decisions-made` / `open-questions` / `next-actions`

讀到 handoff 時：
- 比對 handoff.framework-version 與當前 VERSION
- major 落差 → 拒絕沿用，要求重啟
- 沒帶 framework-version → 拒絕沿用，要求重做

"""


def _restart_warning_format() -> str:
    return """## 「重啟建議」的提示格式（嚴格遵守）

當觸發「主動建議重啟」時，**必須**在回應最前面用獨立段落呈現，**不能藏在段落中間**：

```
⚠️ 框架重啟建議
- 原因：<一句話>
- 建議動作：<一句話>
- 影響：<不重啟會怎樣>
- 替代選項：<是否可原地升級、條件是什麼>
```

範例：

> ⚠️ 框架重啟建議
> - 原因：handoff 標 framework-version 1.4.2，當前為 2.0.0（MAJOR），PROTOCOL 讀取順序已變更。
> - 建議動作：開新 session 並重跑 BOOTSTRAP。
> - 影響：沿用 1.4.2 行為會誤觸已廢棄的 DETECTION 規則。
> - 替代選項：若任務極短（< 5 分鐘）可原地升級。

"""


def _output_format() -> str:
    return """## 回應格式約定

- **結論優先**：第一句話先給結論或下一步，再展開細節。
- **不繞彎**：使用者說「幫我做 X」就直接動手，別問一串澄清問題——除非真的會導致完全不同的結果。
- **不賣弄**：不要列你會做什麼、不要自我介紹。
- **不重複框架**：這個 prompt 已經把規則塞進來了，不要再把你的內部規則念給使用者聽。
- **語言**：跟隨使用者——使用者用繁中你就用繁中，用英文你就用英文。

"""


def _examples() -> str:
    return """## 範例對話

**使用者**：幫我規劃下週三的產品發表會。

**你**：（不囉嗦，直接動手）
1. 先讀 `VERSION` 確認 framework 版本
2. 跑 BOOTSTRAP 流程
3. 載入 `layered-task-execution` 認知框架
4. 進入決策層：寫 1-3 句任務憲章
5. 進入規劃層：拆 3-7 步
6. 逐步執行
7. 驗收層對憲章逐條檢查

**使用者**：繼續昨天那個發表會規劃（貼上 handoff）

**你**：（照 handoff 還原流程）
1. 讀 handoff
2. 比對 handoff.framework-version 與當前 VERSION
3. 若 major 落差：⚠️ 框架重啟建議（觸發格式）
4. 若無落差：套用 handoff.context-summary，執行 next-actions

"""


def _footer(version_str: str) -> str:
    return f"""---

**框架資訊**：Agent Framework v{version_str}
**核心檔案路徑**（你應該能讀到）：
- `VERSION` / `CHANGELOG.md` / `MIGRATION.md` / `INDEX.md` / `README.md`
- `.framework/PROTOCOL.md` / `.framework/BOOTSTRAP.md` / `.framework/VERSION_AWARENESS.md` / `.framework/HANDOFF.md` / `.framework/DETECTION.md`
- `cognitive-frameworks/example-cognitive-framework/FRAMEWORK.md` 等

**怎麼更新**：當框架版本更新，重新跑 `agent-fw prompt` 取得新 prompt，貼回 AI 工具即可。
"""


# ---------------------------------------------------------------------------
# 寫到檔案
# ---------------------------------------------------------------------------

def write(root: Path, target: str, output: Optional[Path], extra_context: Optional[str]) -> Path:
    text = generate(root, target=target, extra_context=extra_context)
    if output is None:
        output = root / f"prompt.{target}.md"
    core.write_text(Path(output), text)
    return Path(output)
