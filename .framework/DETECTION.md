# DETECTION — 多版本混雜偵測

> **對象**：正在運行中的 AI session。
> **角色**：把「我懷疑內容混雜了多個版本」這個直覺，變成可觀測、可決策的規則。

---

## 為什麼需要這個

人寫的內容、handoff 裡的引用、不同時間建立的 `cognitive-frameworks/*`——它們的 `framework-version` 標頭可能不一致。當 AI 用一份過期的章節搭配新版協議運行，就會出現「規則對、結論錯」的幽靈錯。

這個檔案定義**如何觀測**這個現象。

---

## 規則版本

```
detection-rules-version: 1
applies-to-framework-version: ">=1.0.0"
```

> bump detection rules 時請同步更新本標頭與 `VERSION_AWARENESS.md` 的契約。

---

## 規則 D1：標頭一致性

**觀測**：每個 markdown 檔案應有 `framework-version` 標頭（位於檔案最上方 frontmatter 或前 5 行內）。

**觸發**：當 session 內同時載入兩個以上檔案，且它們的 `framework-version` 不一致時，標記 `mixed-headers: true`。

**嚴重度**：中。
**建議動作**：用 `VERSION_AWARENESS.md` 的 MINOR/MAJOR 處理流程。

---

## 規則 D2：章節廢棄引用

**觀測**：當前 `INDEX.md` 與 `CHANGELOG.md` 共同定義了「已廢棄章節清單」。若 session 引用了其中任何章節，標記 `deprecated-reference: true`。

**觸發來源**：
- 引用檔案路徑出現在 `CHANGELOG.md` 的 `### Removed` 區段
- 引用檔案路徑出現在 `MIGRATION.md` 的「跨版本注意事項」中被標記 `replaced-by: <新路徑>`

**嚴重度**：高。
**建議動作**：建議重啟 session；提示使用者用新章節。

---

## 規則 D3：時間軸衝突

**觀測**：handoff 文件帶有 `created-at` 與 `framework-version`。當 `framework-version` 比 `CHANGELOG.md` 中對應時間點的版本**還新**時，標記 `timeline-anomaly: true`。

**範例**：handoff 標記 `framework-version: 1.1.0`、`created-at: 2026-05-01`，但 CHANGELOG 中 1.1.0 是在 2026-06-15 才釋出——這份 handoff 來自未來或被竄改。

**嚴重度**：高。
**建議動作**：拒絕套用 handoff，要求重新確認。

---

## 規則 D4：術語漂移

**觀測**：當 session 內出現多份文件，且同一概念使用了**多個不同名稱**——例如一份說「bootstrap」、另一份說「cold-start」——標記 `terminology-drift: true`。

**判斷依據**：
- INDEX.md 中定義的核心術語表（見下方）為基準
- 任何與基準不一致且非「歷史引用」的出現都算漂移

**嚴重度**：低到中。
**建議動作**：提示使用者術語不一致，請其決定要不要重啟或加 gloss。

---

## 規則 D5：路徑失效

**觀測**：任何 session 內引用（包含 handoff、cognitive-frameworks/ 內部交叉引用、CHANGELOG 中的 replaced-by）若指向不存在的路徑，標記 `broken-reference: true`。

**嚴重度**：中。
**建議動作**：列出所有失效路徑，要求使用者確認是否要修復或刪除。

---

## 核心術語表（給 D4 用）

| 基準術語 | 別名（視為漂移） | 範本歸屬 |
|----------|------------------|----------|
| bootstrap | cold-start, init, startup | BOOTSTRAP |
| handoff | handover, transfer, pass-down | HANDOFF |
| framework-version | schema-version（不同概念！） | VERSION |
| mixed-version | version-drift, multi-version | DETECTION |
| restart-recommended | reload-required, session-reset | VERSION_AWARENESS |

> `schema-version` 與 `framework-version` 是**不同**的東西：前者描述 `VERSION` 檔案本身的格式，後者描述框架內容的語義。混淆視為漂移。

---

## 偵測輸出格式

當任一規則觸發，AI 必須在內部狀態中標記，並在合適時機（下一句回應、建議重啟時）報告：

```yaml
mixed-version-detection:
  rules-version: 1
  triggered: [<D1 | D2 | D3 | D4 | D5>]
  findings:
    - rule: D2
      severity: high
      evidence: "<引述的內容>"
      recommendation: "<具體建議>"
  overall: clean | minor | major
```

`overall` 計算：
- 任一 high → major
- 任一中、無 high → minor
- 全低或無觸發 → clean

---

## 與其他檔案的契約

- `VERSION_AWARENESS.md` 拿到本檔的 `findings` 後，決定是否觸發「主動建議重啟」。
- `MIGRATION.md` 是 `D2` 的權威來源。
- `INDEX.md` 提供路徑地圖，是 `D5` 的檢查基準。
