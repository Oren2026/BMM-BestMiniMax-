# SSH Key 管理

這份 framework 的 GitHub 同步靠 SSH key。Pod 是 ephemeral 的，所以 key 管理有兩條路徑：

---

## 設計目標

- **一次 approve，永久可用**：把 public key 加到 GitHub **帳號**的 SSH keys，未來所有 pod 共用同一把 key
- **新 pod 自動恢復**：未來新 pod 開起來時，跑 `bash keys/restore.sh` 即可

---

## 目前的 key

| 屬性 | 值 |
|------|-----|
| 類型 | ed25519 |
| 指紋 | `SHA256:VyTFuZxzjjkhhP4gS4rGsq1BmJml6d0SYMf1X2xEAB4` |
| Comment | `mavis-agent-20260602-maxhermes-ndwfd` |
| 產生日期 | 2026-06-02 |
| 產生環境 | MaxHermes pod `maxhermes-ndwfd` (172.26.26.100) |
| 用途 | 推 `system` branch 到 `Oren2026/BMM-BestMiniMax-.git` |

`mavis_agent.pub` 是 public key（已 commit，可公開）。
Private key 不進 git，請用密碼管理器保管（1Password / Bitwarden / macOS Keychain）。

---

## 一次性設定（5 分鐘，做完之後永久不用再動）

### 步驟 1：把 public key 加到你的 GitHub 帳號

1. 開 https://github.com/settings/keys
2. 點「New SSH key」
3. Title: `Mavis Agent (maxhermes)` 之類
4. Key type: **Authentication Key**（不是 Signing Key）
5. Key: 貼上 `mavis_agent.pub` 的完整內容
6. 點「Add SSH key」

> 為什麼加到「帳號」而不是 repo 的「Deploy keys」？
> - 帳號層級的 key 對**所有**你有權限的 repo 都有效
> - Deploy keys 是 per-repo 的，未來加新 repo 還要再來一次
> - 帳號層級的 key 自動信任你已有的所有 repo，不用再 approve

### 步驟 2：把 private key 存到密碼管理器

把 `~/.ssh/mavis_github_deploy`（**private** key）整份內容存到你的密碼管理器。命名建議：
- 名稱：`mavis-github-deploy`
- 類型：SSH Key
- 備註：推到 `Oren2026/BMM-BestMiniMax-` 的 system branch

---

## 之後每次新 pod（30 秒）

1. 新 Mavis session 開起來後，跟 AI 講：
   > 請跑 `bash keys/restore.sh`
2. AI 會問你貼 private key，從密碼管理器複製貼上、Ctrl+D
3. AI 回報「認證成功」→ 完成

未來這個 pod 推什麼都會被 GitHub 認得。

---

## 為什麼不把 private key 進 git

- 即使加密，加密檔進 public repo 等於公開（密碼學界共識：don't roll your own crypto）
- 進 private repo 也只是把單一祕密變成兩層祕密（passphrase + repo access）
- 1Password 之類的工具是專門設計來保護 secrets 的，比 git 強很多

---

## 緊急 rotate（key 洩漏時）

如果你懷疑 key 洩漏：

1. 從 https://github.com/settings/keys 刪掉那把 key
2. 開新 Mavis session，重新跑：
   ```bash
   ssh-keygen -t ed25519 -C "mavis-agent-$(date +%Y%m%d)" -f ~/.ssh/mavis_github_deploy -N ""
   ```
3. 把新 public key 加到 GitHub
4. 更新這個 README 的「目前的 key」區段
5. commit + push

---

## 為什麼是 SSH 不是 HTTPS / Token

- SSH key 不用每次 push 都輸入（token 要）
- SSH key 可以限制用途（Authentication Key 不能讀 issues 等敏感操作）
- 1Password CLI 對 SSH key 整合較好

如果你偏好 HTTPS + Personal Access Token（PAT），流程類似，只是把 key 換成 token 罷了。
