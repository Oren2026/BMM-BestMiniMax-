#!/usr/bin/env bash
# restore.sh — 在新的 Mavis/MaxHermes pod 上恢復 SSH key
#
# 用法：
#   1. 先到 1Password / Bitwarden / 你的密碼管理器取出 private key
#   2. bash keys/restore.sh
#   3. 貼上 private key，Ctrl+D 結束
#   4. script 會自動設好 ~/.ssh/ 並測試連線

set -e

# 顏色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

KEY_DIR="${HOME}/.ssh"
KEY_FILE="${KEY_DIR}/mavis_github_deploy"
KNOWN_HOSTS="${KEY_DIR}/known_hosts"
CONFIG="${KEY_DIR}/config"
EXPECTED_FP="SHA256:VyTFuZxzjjkhhP4gS4rGsq1BmJml6d0SYMf1X2xEAB4"

echo -e "${YELLOW}=== Mavis Agent SSH Key Restore ===${NC}"
echo ""
echo "這個 script 會幫你在新的 pod 恢復 SSH key，讓你可以 git push 到"
echo "  git@github.com:Oren2026/BMM-BestMiniMax-.git"
echo ""
echo "準備好你的 private key 內容（在密碼管理器裡找 'mavis_github_deploy'）"
echo ""

# 確認 ~/.ssh 存在
mkdir -p "${KEY_DIR}"
chmod 700 "${KEY_DIR}"

# 如果已經有 key，問要不要覆蓋
if [ -f "${KEY_FILE}" ]; then
    echo -e "${YELLOW}⚠ ${KEY_FILE} 已存在${NC}"
    read -p "  要覆蓋嗎？[y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "已取消"
        exit 0
    fi
fi

# 讀取 private key
echo "請貼上 private key 內容（以 -----BEGIN 開頭、-----END 結尾）"
echo "貼完按 Ctrl+D："
echo ""
KEY_CONTENT=$(cat)
echo ""

# 簡單驗證格式
if ! echo "${KEY_CONTENT}" | grep -q "BEGIN OPENSSH PRIVATE KEY" \
   && ! echo "${KEY_CONTENT}" | grep -q "BEGIN RSA PRIVATE KEY" \
   && ! echo "${KEY_CONTENT}" | grep -q "BEGIN EC PRIVATE KEY"; then
    echo -e "${RED}✗ 這看起來不像合法的 private key（找不到 BEGIN 標記）${NC}"
    echo "  請確認你複製的是 private key（.pub 是 public key，不能用）"
    exit 1
fi

# 寫入
echo "${KEY_CONTENT}" > "${KEY_FILE}"
chmod 600 "${KEY_FILE}"

# 設定 SSH config
cat > "${CONFIG}" <<'EOF'
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/mavis_github_deploy
    IdentitiesOnly yes
    StrictHostKeyChecking accept-new
EOF
chmod 600 "${CONFIG}"

# 設定 git config
git config --global user.name "Mavis Agent" 2>/dev/null || true
git config --global user.email "mavis-agent@minimax.io" 2>/dev/null || true
git config --global core.sshCommand "ssh -i ~/.ssh/mavis_github_deploy -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new" 2>/dev/null || true

# 驗證指紋
ACTUAL_FP=$(ssh-keygen -lf "${KEY_FILE}" 2>/dev/null | awk '{print $2}')
if [ "${ACTUAL_FP}" != "${EXPECTED_FP}" ]; then
    echo -e "${YELLOW}⚠ Key 指紋不匹配${NC}"
    echo "  預期：${EXPECTED_FP}"
    echo "  實際：${ACTUAL_FP}"
    echo "  這不一定有問題（可能是新的 key pair），但請確認你用的是正確的 key"
else
    echo -e "${GREEN}✓ Key 指紋匹配${NC}"
fi

# 測試連線
echo ""
echo "測試 SSH 連線到 GitHub..."
if ssh -T -o ConnectTimeout=10 git@github.com 2>&1 | grep -q "successfully authenticated"; then
    echo -e "${GREEN}✓ 認證成功${NC}"
elif ssh -T -o ConnectTimeout=10 git@github.com 2>&1 | grep -q "Permission denied"; then
    echo -e "${RED}✗ Permission denied${NC}"
    echo "  請確認 public key 已在 GitHub 帳號的 SSH keys 裡："
    echo "  https://github.com/settings/keys"
    exit 1
else
    echo -e "${YELLOW}⚠ 連線結果不明確，請手動確認：ssh -T git@github.com${NC}"
fi

echo ""
echo -e "${GREEN}=== 完成 ===${NC}"
echo ""
echo "之後你可以："
echo "  git clone git@github.com:Oren2026/BMM-BestMiniMax-.git"
echo "  cd framework && bash install.sh"
echo "  agent-fw status"
