# Version Bump — <從 X.Y.Z 升到 A.B.C>

> 對應章節：`MIGRATION.md`、`.framework/VERSION_AWARENESS.md`、`.framework/DETECTION.md`。
> 參考範例：[`examples/version-bump.example.md`](../examples/version-bump.example.md)。
> **每次 bump 都要留紀錄在本檔副本裡**——這是審計痕跡。

---

## 1. 確認 bump 類型

```yaml
from: <X.Y.Z>
to: <A.B.C>
type: <major | minor | patch>
reason: <一句話講為什麼要 bump>
breaking-changes:
  - <列出具體破壞性變更；type=patch 時填 none>
```

## 2. 影響評估

- [ ] `INDEX.md` 的檔案清單仍正確
- [ ] `.framework/VERSION_AWARENESS.md` 的決策樹仍適用
- [ ] `.framework/DETECTION.md` 的規則版本是否需 bump
- [ ] `cognitive-frameworks/*/META.md` 的 `compat-with-agent-version` 是否需更新
- [ ] `MIGRATION.md` 是否需新增章節（type=major 時必填）
- [ ] 是否有任何「已廢棄但仍被引用」的章節

## 3. 執行更新

- [ ] 改 `VERSION` 檔
- [ ] 新增 `CHANGELOG.md` 條目（用 [`changelog-entry.template.md`](changelog-entry.template.md)）
- [ ] 若 major：新增 `MIGRATION.md` 章節
- [ ] 若 detection rules 有變：bump `detection-rules-version`
- [ ] 若 cognitive frameworks 受影響：在對應 `META.md` 加 compat 註記

## 4. 驗證

- [ ] `INDEX.md` 所有內部連結仍可達
- [ ] `VERSION_AWARENESS.md` 的決策樹在新版本上能跑
- [ ] 跑一次 BOOTSTRAP 模擬：拿「假使用者提示」看會不會觸發重啟建議
- [ ] 若有 handoff 範例，更新對應的 `framework-version` 標頭

## 5. 通知 / 公告（可選）

- [ ] 在 `CHANGELOG.md` 的最新條目確認可讀
- [ ] 若有對外發布管道，準備 announcement
- [ ] 通知所有正在使用舊版的 session：重啟並重跑 BOOTSTRAP

## 6. 後續監控

> bump 後 7 天內觀察 `.framework/DETECTION.md` 是否觸發異常；若連續觸發 D2/D3，考慮 patch 修補。

- 觀察期結束於：<日期>
- 觀察記錄位置：<本檔副本或外部 issue tracker>
