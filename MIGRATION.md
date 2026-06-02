# Migration Guide

本檔說明框架版本之間的遷移步驟。**任何 MAJOR bump 都必須新增對應章節**，MINOR 變更僅在下方「跨版本注意事項」補一條。

> **給 AI 讀者**：當 `VERSION` 與既有工作記憶中的版本不同時，請讀本檔；若本檔未涵蓋新舊版本組合，請主動提示使用者「需要手動遷移決策」並列出已知差異。

---

## 升級決策樹

```
讀取到新 VERSION
  │
  ├─ MAJOR 變更？
  │     ├─ 是 → 必須在乾淨 session 中重讀 PROTOCOL
  │     │        並重跑 .framework/BOOTSTRAP.md
  │     └─ 否 ─┐
  │            │
  │   既有工作記憶有沒有依賴已廢棄的章節？
  │     ├─ 是 → 建議重啟 session（沿用舊章節語義會出錯）
  │     └─ 否 → 可原地升級
  │
  └─ 觸發 .framework/DETECTION.md 規則 → 多版本混雜？
        ├─ 是 → 強烈建議重啟 session
        └─ 否 → 提示使用者後繼續
```

---

## 跨版本注意事項

### v1.0.x → v1.1.x
- 預期為 `MINOR` 變更：新增 `.framework/*.md` 區段、`templates/` 範本、`cognitive-frameworks/` 示範。
- 動作：增量讀取新增章節，原有 session 可沿用。
- 例外：若新增的章節取代了既有章節，視為 MAJOR，請回到上一層決策樹。

### v1.x → v2.0.0
- 預期為 `MAJOR` 變更：協議順序變更、偵測規則語義改變、`schema-version` 推進。
- 動作：**必須重啟 session**。在新 session 中完整重跑 `BOOTSTRAP.md`。
- 建議在升級前先用 `examples/handoff.example.md` 將目前進度封存。

---

## 給維護者的檢查清單（每次 bump）

- [ ] `VERSION` 已更新
- [ ] `CHANGELOG.md` 已新增條目
- [ ] 本檔有對應章節（若為 MAJOR）
- [ ] `.framework/VERSION_AWARENESS.md` 的偵測規則仍可運作
- [ ] `INDEX.md` 的檔案清單仍正確
- [ ] 受影響的 `cognitive-frameworks/*` 已標註 `framework-version` 影響
