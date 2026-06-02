# 📝 更新指南

> 如何更新 KPI、新聞、任務等資料

---

## 🎯 更新原則

1. **每次有重要事件就更新** — 不要累積
2. **一次只更新相關檔案** — 不要碰無關的
3. **保持格式一致** — 參考現有範例
4. **commit message 要清楚** — 讓別人知道改了什麼

---

## 📂 各檔案更新方式

### 1. 更新 API 調用次數

編輯 `api_calls.json`：

```json
{
  "summary": {
    "totalApiCalls": 48,  // ← 記得 +1
    ...
  },
  "apiCallHistory": [
    {
      "id": "AC006",           // ← 新 ID
      "agent": "mavis",
      "endpoint": "/api/xxx",
      "timestamp": "2026-06-02T12:00:00Z",
      "status": "success"
    }
  ]
}
```

---

### 2. 新增新聞事件

編輯 `news.json`：

```json
{
  "news": [
    {
      "id": "N006",              // ← 新 ID（N+1）
      "title": "新聞標題",
      "content": "詳細描述",
      "category": "project",     // system / project / deployment / collaboration
      "agents": ["Mavis", "Coder"],
      "project": "專案名",
      "timestamp": "2026-06-02T12:00:00Z",
      "priority": "medium"        // high / medium / low
    }
  ]
}
```

---

### 3. 新增任務

編輯 `tasks.json`：

```json
{
  "tasks": [
    {
      "id": "T010",               // ← 新 ID（T+1）
      "name": "任務名稱",
      "description": "任務描述",
      "agent": "Mavis",
      "collaborators": ["Coder"], // 沒有就 []
      "project": "專案名",
      "status": "completed",      // completed / in-progress / pending
      "createdAt": "2026-06-02T12:00:00Z",
      "completedAt": "2026-06-02T12:30:00Z",
      "priority": "high"           // critical / high / medium / low
    }
  ],
  "projects": [
    {
      "id": "P006",
      "name": "專案名",
      "description": "專案描述",
      "agents": ["Mavis", "Coder"],
      "taskCount": 1,              // 記得 +1
      "status": "completed"        // completed / in-progress
    }
  ]
}
```

---

### 4. 更新 Agent 統計

編輯 `api_calls.json` 的 `agentStats`：

```json
{
  "agentStats": [
    {
      "agentId": "mavis",
      "name": "Mavis",
      "apiCalls": 33,           // ← +1
      "projectsHandled": 4,
      "collaborations": 19,     // ← +1
      "tasks": [
        {
          "id": "T010",
          "name": "新任務",
          "status": "completed",
          "date": "2026-06-02T12:30:00Z"
        }
      ]
    }
  ]
}
```

---

## 🔧 Git 推送流程

```bash
# 1. 確保 SSH 已設定（如還沒設）
eval "$(ssh-agent -s)" && ssh-add ~/.ssh/mavis_deploy

# 2. 進入專案目錄
cd /workspace/agent-dashboard

# 3. 查看更動
git status

# 4. 加入暫存區
git add .

# 5. 提交（message 要清楚）
git commit -m "feat: 新增 N006 新聞 / 更新 API 統計至 48"

# 6. 推送
git push
```

---

## ⚠️ 注意事項

### 不要做的

- ❌ 不要刪除歷史資料
- ❌ 不要修改其他 Agent 的記錄（除非有充分理由）
- ❌ 不要留空值或 null（要用有意義的預設）
- ❌ 不要一次 commit 太多不相關的更動

### 建議做的

- ✅ 更新時順便檢查數字是否合理
- ✅ 保持 timestamp 格式一致（ISO 8601）
- ✅ 讓 commit message 描述性強
- ✅ 定時同步 GitHub（每天至少一次）

---

## 📋 快速檢查清單

更新前確認：

- [ ] 新聞 ID 是否為 N+1？
- [ ] 任務 ID 是否為 T+1？
- [ ] 專案 ID 是否為 P+1？
- [ ] API 總數是否已更新？
- [ ] timestamp 格式是否正確？
- [ ] status 值是否合法？
- [ ] priority 值是否合法？

---

*最後更新：2026-06-02 11:36*