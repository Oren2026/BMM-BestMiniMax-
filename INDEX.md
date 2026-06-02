# Framework Index

> **給 AI 讀者**：本檔是框架地圖，僅供「快速定位」。真實的讀取協議請見 [`.framework/PROTOCOL.md`](.framework/PROTOCOL.md)。**不要**把本檔當作啟動流程的一部分。

---

## 一、根目錄

| 檔案 | 角色 | 何時讀 |
|------|------|--------|
| [README.md](README.md) | 框架入口、人類導讀 | 第一次接觸框架時 |
| [INDEX.md](INDEX.md) | 本檔，檔案地圖 | 需要定位時 |
| [VERSION](VERSION) | 當前版本、自我描述 | **永遠第一個讀** |
| [CHANGELOG.md](CHANGELOG.md) | 演進歷史 | 確認有什麼變動時 |
| [MIGRATION.md](MIGRATION.md) | 跨版本遷移 | 偵測到版本落差時 |

## 二、`.framework/` 系統協議

> AI 行為準則、AI 之間如何交接、如何偵測多版本混雜——全部住這裡。

| 檔案 | 角色 | 何時讀 |
|------|------|--------|
| [`.framework/PROTOCOL.md`](.framework/PROTOCOL.md) | 讀取順序總綱 | session 啟動時 |
| [`.framework/BOOTSTRAP.md`](.framework/BOOTSTRAP.md) | session 啟動流程 | 新 session 第一步 |
| [`.framework/VERSION_AWARENESS.md`](.framework/VERSION_AWARENESS.md) | 版本自我感知 | 任何讀取動作前後 |
| [`.framework/HANDOFF.md`](.framework/HANDOFF.md) | 進度交接規範 | 切換 session / 交付前 |
| [`.framework/DETECTION.md`](.framework/DETECTION.md) | 多版本混雜偵測 | 懷疑內容來源不一致時 |

## 三、`cognitive-frameworks/` 認知框架本體

> 你想讓 AI 內化的「思維模型」。每個子資料夾是一份獨立的認知框架。

| 檔案 | 角色 |
|------|------|
| [`cognitive-frameworks/README.md`](cognitive-frameworks/README.md) | 認知框架總覽、命名與版本約定 |
| [`cognitive-frameworks/_template/`](cognitive-frameworks/_template/) | 建立新框架時的空白範本 |
| [`cognitive-frameworks/example-cognitive-framework/`](cognitive-frameworks/example-cognitive-framework/) | 一份完整示範 |

## 四、`templates/` 範本套件

> 可直接複製貼上的工作模板。

| 範本 | 用途 |
|------|------|
| [`templates/session-bootstrap.template.md`](templates/session-bootstrap.template.md) | 每次新 session 開頭的狀態盤點 |
| [`templates/handoff.template.md`](templates/handoff.template.md) | 跨 session 交棒時的進度封存 |
| [`templates/version-bump.template.md`](templates/version-bump.template.md) | bump 框架版本時的檢查流程 |
| [`templates/new-framework.template.md`](templates/new-framework.template.md) | 新增一份認知框架時的骨架 |
| [`templates/changelog-entry.template.md`](templates/changelog-entry.template.md) | CHANGELOG 條目草稿 |

## 五、`examples/` 範例

> 對應主要範本的具體填寫範例。

| 範例 | 對應範本 |
|------|----------|
| [`examples/session-bootstrap.example.md`](examples/session-bootstrap.example.md) | session-bootstrap |
| [`examples/handoff.example.md`](examples/handoff.example.md) | handoff |
| [`examples/version-bump.example.md`](examples/version-bump.example.md) | version-bump |

---

## 快速指令

**AI 接到任務時**（依序）：
1. `read VERSION` → 拿當前版本
2. `read .framework/PROTOCOL.md` → 拿讀取順序
3. `read .framework/BOOTSTRAP.md` → 跑啟動流程
4. `read .framework/VERSION_AWARENESS.md` → 評估是否需要重啟

**AI 交付前**：
1. `read .framework/HANDOFF.md` → 決定是否要寫 handoff
2. 若 bump → `read .framework/DETECTION.md` → 評估多版本混雜風險
