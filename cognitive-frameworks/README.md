# Cognitive Frameworks

> **對象**：想要讓 AI 內化某種思維模型的人 / 想要載入某種思維模型的 AI。
> **角色**：本目錄是「思維模型庫」，每個子資料夾是一份獨立的認知框架。
> **契約**：每份框架都有自己的 `framework-version` 與 `compat-with-agent-version`。

---

## 目錄約定

```
cognitive-frameworks/
├── README.md                          # 本檔
├── _template/                         # 空白範本——複製此目錄開始新框架
│   ├── FRAMEWORK.template.md
│   ├── META.template.md
│   └── CHECKLIST.template.md
└── <framework-slug>/                  # 實際框架
    ├── FRAMEWORK.md                   # 框架本體
    ├── META.md                        # 元資料：版本、相容性、作者
    └── CHECKLIST.md                   # 使用前自檢 / 使用後覆盤
```

### 命名規則
- 目錄名用 kebab-case：`layered-task-execution` / `decision-priority-matrix`。
- 框架對外名稱用人類可讀：「分層任務執行」/「決策優先矩陣」。
- slug 不可改——一旦發布就成了穩定 ID；要改名 = 視為新框架（見 `templates/new-framework.template.md`）。

---

## 三件檔案各自的工作

### FRAMEWORK.md
框架本體。回答：「這是什麼、什麼時候用、怎麼用、怎麼知道用對了」。
- 必須包含：核心概念、何時用 / 何時不用、操作步驟、反模式、與其他框架的關係。

### META.md
元資料。回答：「這份框架是給誰用的、相容於什麼、不相容於什麼」。
- 必填欄位：`framework-slug` / `framework-name` / `framework-version` / `compat-with-agent-version` / `compat-with-detector-rules` / `author` / `created-at` / `last-updated` / `status` / `tags` / `supersedes` / `superseded-by`。

### CHECKLIST.md
使用前自檢 + 使用後覆盤。回答：「我真的準備好用這份框架了嗎？我用對了嗎？」
- 分兩半：`## 載入前自檢` 與 `## 任務結束覆盤`。

---

## 框架版本管理

每份框架**獨立**於 agent framework 本身的版本。它有自己的 `framework-version`（採 SemVer）。

- `MAJOR`：核心概念變更、與其他框架的關係改變
- `MINOR`：新增步驟、新增反模式
- `PATCH`：錯字、範例潤稿

當 `framework-version` 變動時，AI 必須：
1. 重讀 `META.md`
2. 跑 `CHECKLIST.md` 的「載入前自檢」
3. 評估是否觸發 `.framework/VERSION_AWARENESS.md` 的重啟建議

---

## 與 agent framework 的關係

```
agent framework (本倉庫的 .framework/*)
  └─ 是合約層——「AI 該怎麼讀、怎麼接、怎麼升級」
      └─ cognitive-frameworks/* 是內容層——「AI 該怎麼想」
```

合約層不應該硬編碼任何特定思維模型；它只定義「思維模型該長什麼形狀」（透過 META / CHECKLIST 的欄位約定）。
內容層不應該改寫合約層的讀取協議；它只貢獻「在協議允許的範圍內，怎麼思考任務」。

兩者耦合點只有兩個：
- `compat-with-agent-version`：META 必填
- `compat-with-detector-rules`：META 必填
