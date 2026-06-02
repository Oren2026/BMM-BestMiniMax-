# Changelog

本檔記錄本框架本身的版本演進。採 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.1.0/) 格式，版本編號採 [Semantic Versioning](https://semver.org/lang/zh-TW/)。

> **給 AI 讀者**：每次 `bump version` 後，請同步更新本檔、新增 MIGRATION 條目（如有破壞性變更），並重新評估 `.framework/VERSION_AWARENESS.md` 中的偵測規則是否仍有效。

---

## [Unreleased]

### Planned
- `cognitive-frameworks/` 增補第二份示範（任務拆解型）
- `.framework/DETECTION.md` 增加跨語言前綴偵測
- `templates/` 補上 `decision-tree.template.md`

---

## [1.0.0] - 2026-06-01

### Added
- 初始框架釋出。
- 根目錄：`README.md` / `INDEX.md` / `VERSION` / `CHANGELOG.md` / `MIGRATION.md`。
- `.framework/` 系統協議區：`PROTOCOL.md` / `BOOTSTRAP.md` / `VERSION_AWARENESS.md` / `HANDOFF.md` / `DETECTION.md`。
- `cognitive-frameworks/`：總覽檔 + `_template/`（`FRAMEWORK` / `META` / `CHECKLIST`）+ `example-cognitive-framework/` 示範。
- `templates/`：`session-bootstrap` / `handoff` / `version-bump` / `new-framework` / `changelog-entry`。
- `examples/`：對應三份主要範本的具體填寫範例。
- `agent-fw` CLI 工具（agent_fw/ 套件）：status / read / bootstrap / bump / detect / validate / handoff / new-framework / prompt / report / tui。
- HTML 儀表板（`agent-fw report`）。
- AI system prompt 產生器（`agent-fw prompt`）。

### Notes
- `schema-version: 1` 鎖定，未來 MAJOR 變動才會 bump。
- 預設 `recommended-restart-on-bump: true`。
