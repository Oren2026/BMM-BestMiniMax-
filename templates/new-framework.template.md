# New Framework — <slug>

> 對應章節：`cognitive-frameworks/README.md`。
> 建立新認知框架時，請複製本檔、補完後存到 `cognitive-frameworks/<slug>/`。

---

## 1. 命名

- **slug**（kebab-case，不可改）：`<framework-slug>`
- **name**（人類可讀）：<framework-name>
- **一句話定義**：<一句話講清楚>

## 2. 初始化檔案

從 `cognitive-frameworks/_template/` 複製三個檔到新目錄：

```bash
cp -r cognitive-frameworks/_template cognitive-frameworks/<slug>
```

接著把 `FRAMEWORK.template.md` / `META.template.md` / `CHECKLIST.template.md` 重新命名為去掉 `.template`：
- `FRAMEWORK.md`
- `META.md`
- `CHECKLIST.md`

## 3. 填寫順序

1. **META.md 先寫**——決定 slug、版本、相容性。
2. **FRAMEWORK.md 寫主體**——核心概念、何時用、何時不用、操作步驟、反模式。
3. **CHECKLIST.md 校稿**——載入前自檢、任務結束覆盤。

## 4. 必填欄位確認

`META.md` 必填：
- [ ] `framework-slug`
- [ ] `framework-name`
- [ ] `framework-version`（首版 `1.0.0`，但若是取代舊框架請見下方「取代流程」）
- [ ] `status`（建議從 `draft` 開始）
- [ ] `compat-with-agent-version`
- [ ] `compat-with-detector-rules`
- [ ] `author` / `created-at` / `last-updated`
- [ ] `tags`

`FRAMEWORK.md` 必填區塊：
- [ ] 一句話定義
- [ ] 核心概念（至少 2 個）
- [ ] 何時用 / 何時不用
- [ ] 操作步驟（每步要有輸入 / 輸出 / 完成判斷）
- [ ] 反模式（至少 3 條）
- [ ] 與其他框架的關係
- [ ] 失敗模式與恢復

## 5. 取代流程（若本框架取代既有框架）

- 舊框架的 `META.md` 改：
  - `status: deprecated`
  - `superseded-by: <本框架 slug>`
  - `migration-from-superseded: <路徑>`
- 本框架的 `META.md` 加 `supersedes: [<舊框架 slug>]`。
- 在 `MIGRATION.md` 增章節說明遷移步驟。
- 在 `CHANGELOG.md` 條目中連結到舊框架的位置。

## 6. 發布前自檢

- [ ] 跑過至少一次完整範例（填在 `FRAMEWORK.md` 的「把框架跑一次」段落）。
- [ ] 給另一位 AI 讀 `FRAMEWORK.md`，請他用自己的話講一遍核心概念——若講不清楚，回去補。
- [ ] 跑 `.framework/VERSION_AWARENESS.md` 決策樹確認 compat 設定正確。
- [ ] 跑 `.framework/DETECTION.md` 規則 D4 確認術語沒漂移。
- [ ] `INDEX.md` 加入新框架的路徑。
