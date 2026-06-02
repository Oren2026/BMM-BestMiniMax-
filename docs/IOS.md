# iOS 整合指南

把 Agent Framework 帶到 iPhone / iPad 的三條路徑——由淺到深。

---

## 路徑 A：在 Mavis 網頁介面用（最簡單，30 秒）

你已經在做這件事了——直接用 iOS Safari 開：

```
https://agent.minimax.io/mavis?id=404585416609955
```

**iOS 怎麼操作**：
1. Safari 開啟後，點底部分享按鈕（向上箭頭）
2. 選「加入主畫面」→ 命名「Mavis」→ 完成
3. 之後從主畫面點就像 App 一樣，全螢幕、無網址列

**能做什麼**：
- 跟 AI 對話（貼上 `prompt.claude.md` 的內容到對話開頭當 system prompt）
- 看 `framework-dashboard.html`（Mavis 通常有檔案預覽，點開就看到 GUI 儀表板）
- 跑 `agent-fw <cmd>`（Mavis 介面有命令列工具支援的話）

**優點**：零安裝、零設定、隨時同步。
**缺點**：iOS Safari 不能跑 Python CLI（要看 `framework-dashboard.html` 的 GUI 才看得到）。

---

## 路徑 B：用 iOS 內建檔案 App 看框架（1 分鐘）

iOS 16+ 的「檔案」App 可以看雲端資料夾。

**步驟**：
1. 下載 `agent-framework-v1.0.0.tar.gz`（從 Mavis 介面下載到 iPhone）
2. 用「檔案」App 開啟 → 點 `.tar.gz` 會跳出「解壓縮」選項
3. 解壓後得到 `agent-framework-v1.0.0/` 資料夾

**能做什麼**：
- 用「檔案」App 直接看所有 md 檔（iOS 內建 md 預覽器）
- 把 `framework-dashboard.html` 用 Safari 開（漂亮的 GUI 介面）
- 複製 `prompt.claude.md` 內容貼到 Claude iOS App 的「Custom Instructions」

**優點**：離線可用、不用一直連線。
**缺點**：不能跑 Python CLI（要看命令輸出要回到 Mavis 介面）。

---

## 路徑 C：在 iOS 跑 Python CLI（進階）

兩個 App 選一個：

### C-1：a-Shell（推薦，便宜好用）
- App Store 搜尋「a-Shell」
- 支援 Python 3、pip、git
- 開啟後直接：
  ```bash
  cd /path/to/agent-framework-v1.0.0
  python3 agent-fw status
  python3 agent-fw bootstrap
  ```

### C-2：iSH（模擬 Alpine Linux，更完整）
- App Store 搜尋「iSH」
- 模擬完整 Linux 環境
- 可裝 pip、git、甚至 vim
- 操作跟 Mac terminal 一模一樣

**優點**：完整功能、能跑 `agent-fw` 所有命令。
**缺點**：iOS 上打字慢、螢幕小；命令列體驗不如 Mac。

---

## 跟 iOS 上的 AI App 整合

不管走哪條路，**iOS 上的 AI App 都能內化這套框架**：

| App | 設定位置 | 怎麼貼 |
|-----|---------|--------|
| **Claude iOS** | Settings → Custom Instructions | 貼 `prompt.claude.md` 內容 |
| **ChatGPT iOS** | Settings → Personalization → Custom Instructions | 貼 `prompt.generic.md` 內容 |
| **Copilot iOS** | 對話開頭貼（每次都要） | 貼 `prompt.claude.md` 內容 |
| **Perplexity iOS** | 對話開頭貼 | 貼 `prompt.generic.md` 內容 |

**做法**：
1. 在 Mavis 介面（或下載到 iPhone）打開 `prompt.claude.md`
2. 全選（Cmd+A / 長按 → 全選）→ 複製
3. 開 Claude iOS App → Settings → Custom Instructions
4. 貼上 → 儲存

從此以後，你在 iPhone 跟 Claude 對話，它就會自動照 framework 協議走：
- 開頭讀 VERSION
- 跑 BOOTSTRAP
- 偵測到版本落差主動建議重啟

---

## 三條路徑對照

| | A: Mavis 網頁 | B: 檔案 App | C: Python CLI |
|---|---|---|---|
| **設定時間** | 30 秒 | 1 分鐘 | 5-10 分鐘 |
| **能不能跑 agent-fw** | ✅（在 Mavis 內） | ❌ | ✅ |
| **能不能看 dashboard** | ✅ | ✅（用 Safari） | ❌（要再寫 TUI） |
| **能不能看 md 檔** | ✅ | ✅ | ⚠（要 `cat`） |
| **離線能用** | ❌ | ✅ | ✅ |
| **適合情境** | 主力使用 | 備用 / 查資料 | 開發 / 進階操作 |

**建議**：用 A 為主，必要時下載到 B 看檔案，C 留給真的要在 iOS 改框架的時候。
