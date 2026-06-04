# 🔬 Lab Board - 實驗室共享行事曆

## 專案概述

實驗室共享行事曆系統，讓15位同學可以：
- 看到彼此的行程與可用時段
- 雙前端：個人儀表板 + 白板大螢幕（月曆視圖）

## 架構

```
lab-board/
├── server/          # Node.js + Express + SQLite
├── public/
│   ├── board/       # 白板（月曆視圖）
│   └── personal/    # 個人儀表板
├── data/            # SQLite 資料庫
└── docs/            # 文件
```

## 功能

### 個人儀表板
- 新增/編輯/刪除行程
- 設定可用時段（空閒/忙碌）
- 頭像設定

### 白板大螢幕
- 月曆視圖顯示所有人行程
- 每人用不同顏色區分
- 自動輪播月份
- 適合投影到實驗室電視

## API

| Method | Endpoint | 說明 |
|--------|----------|------|
| GET | `/api/users` | 取得所有成員 |
| POST | `/api/users` | 新增成員 |
| GET | `/api/events` | 取得所有行程 |
| POST | `/api/events` | 新增行程 |
| PUT | `/api/events/:id` | 更新行程 |
| DELETE | `/api/events/:id` | 刪除行程 |
| GET | `/api/calendar/:year/:month` | 取得指定月行事 |

## 技術棧

- **後端**: Node.js + Express + better-sqlite3
- **前端**: 原生 HTML/CSS/JS（無框架）
- **資料庫**: SQLite
- **部署**: 本地 server（實驗室電腦）