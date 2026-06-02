# Version Bump — 從 1.0.0 升到 1.1.0（MINOR）

> 對應章節：`MIGRATION.md`、`.framework/VERSION_AWARENESS.md`、`.framework/DETECTION.md`。
> 情境：新增第二份認知框架「決策優先矩陣」，且新增 `templates/decision-tree.template.md`。

---

## 1. 確認 bump 類型

```yaml
from: 1.0.0
to: 1.1.0
type: minor
reason: "新增 cognitive-frameworks/decision-priority-matrix/ 與 templates/decision-tree.template.md，無破壞性變更"
breaking-changes: none
```

## 2. 影響評估

- [x] `INDEX.md` 的檔案清單需更新——新增兩條目
- [x] `.framework/VERSION_AWARENESS.md` 決策樹仍適用——MINOR 例外條件沒觸發
- [x] `.framework/DETECTION.md` 規則版本不需 bump——規則未變
- [x] `cognitive-frameworks/example-cognitive-framework/META.md` 的 `compat-with-agent-version` 仍為 `>=1.0.0`——不需更新
- [x] `MIGRATION.md` 補一條「v1.0.x → v1.1.x 注意事項」即可
- [x] 沒有「已廢棄但仍被引用」的章節

## 3. 執行更新

- [x] 改 `VERSION`：`v1.0.0` → `v1.1.0`、`last-updated: 2026-06-15`
- [x] `CHANGELOG.md` 新增條目：

  ```markdown
  ## [1.1.0] - 2026-06-15

  ### Added
  - `cognitive-frameworks/decision-priority-matrix/`：第二份示範框架
  - `templates/decision-tree.template.md`：決策樹型任務的工作範本
  - `INDEX.md`：新增上述兩條目

  ### Notes
  - MINOR bump，無破壞性變更。原地升級即可。
  ```

- [x] `MIGRATION.md` 在「v1.0.x → v1.1.x」段落補：
  > v1.1.0 開始，`INDEX.md` 列出更多 templates。MINOR 變更，原地升級即可，**不需要**重啟 session。

- [x] `INDEX.md` 加入：
  > - `templates/decision-tree.template.md`
  > - `cognitive-frameworks/decision-priority-matrix/`

- [x] 新框架的 `META.md` 標 `compat-with-agent-version: ">=1.1.0"`（**新框架**才能這樣標；既有框架仍可標 `>=1.0.0` 表示向後相容）

## 4. 驗證

- [x] `INDEX.md` 所有內部連結仍可達（手動點過 `decision-priority-matrix/FRAMEWORK.md`）
- [x] `.framework/VERSION_AWARENESS.md` 決策樹跑一次：拿「假 session 載入 v1.0.0 範例 + v1.1.0 新章節」當輸入，預期 `version-delta: minor` + `restart-recommended: false`
- [x] BOOTSTRAP 模擬：拿「使用者說『用 decision-priority-matrix』」當輸入，新框架成功載入、無 detection 觸發
- [x] 既有 `examples/handoff.example.md` 的 `framework-version: 1.0.0` 仍視為相容（MINOR 不破壞向後相容）

## 5. 通知 / 公告

- [x] `CHANGELOG.md` 最新條目可讀
- [x] 對仍在使用 v1.0.0 的 session：發送「提示 bump」訊息——「框架已釋出 v1.1.0，建議下次 session 開頭重跑 BOOTSTRAP」

## 6. 後續監控

- 觀察期結束於：2026-06-22
- 觀察記錄位置：本檔副本（已 commit）
- 預期觀察重點：
  - 是否有 session 引用 `decision-priority-matrix` 但 framework-version 仍標 1.0.0（觸發 D1）
  - 是否有術語漂移（觸發 D4）：「優先矩陣」vs「優先級矩陣」vs「priority matrix」

---

## 對照：如果這是 MAJOR bump 會多什麼

- 必填：MIGRATION.md 完整章節（含決策樹路徑變更、章節廢棄清單）
- 必填：CHANGELOG.md 標 `### Migration` 區塊並指向 MIGRATION.md
- 必填：主動 ping 所有運行中 session「請重啟並重跑 BOOTSTRAP」
- 必填：把 `recommended-restart-on-bump: true` 改為 `required-restart-on-bump: true`（**未來**版本考慮）

---

## 對照：如果這是 PATCH bump 會少什麼

- 不需更新 MIGRATION.md
- 不需發公告
- CHANGELOG 條目精簡為「Fixed: <具體 bug>」
- 觀察期可縮短為 3 天
