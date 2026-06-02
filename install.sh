#!/usr/bin/env bash
# install.sh — 把 agent-fw 安裝到 ~/.local/bin
# 用法：bash install.sh [--prefix=/path]

set -e

# 解析參數
PREFIX="${HOME}/.local"
while [[ $# -gt 0 ]]; do
    case "$1" in
        --prefix=*) PREFIX="${1#*=}"; shift ;;
        --prefix)   PREFIX="$2"; shift 2 ;;
        -h|--help)
            echo "用法：bash install.sh [--prefix=PATH]"
            echo "預設安裝到 ~/.local"
            exit 0 ;;
        *) echo "未知參數：$1" >&2; exit 1 ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${PREFIX}/bin"
LIB_ROOT="${PREFIX}/share/agent-fw"

echo "→ 安裝前綴：${PREFIX}"
echo "→ 來源目錄：${SCRIPT_DIR}"

mkdir -p "${BIN_DIR}" "${LIB_ROOT}/agent_fw"

# 複製套件
echo "→ 複製 agent_fw/ → ${LIB_ROOT}/agent_fw/"
rm -rf "${LIB_ROOT}/agent_fw"
cp -r "${SCRIPT_DIR}/agent_fw" "${LIB_ROOT}/"

# 複製可執行檔
echo "→ 複製 agent-fw → ${BIN_DIR}/agent-fw"
cp "${SCRIPT_DIR}/agent-fw" "${BIN_DIR}/agent-fw"
chmod +x "${BIN_DIR}/agent-fw"

# 修 shebang 與路徑
echo "→ 修補路徑"
python3 -c "
import re
from pathlib import Path
script = Path('${BIN_DIR}/agent-fw')
text = script.read_text()
text = text.replace(
    'HERE = Path(__file__).resolve().parent\nROOT = HERE.parent',
    'HERE = Path(__file__).resolve().parent\nROOT = Path(\"${LIB_ROOT}\")'
)
script.write_text(text)
"

# 提示 PATH
echo ""
echo "✓ 安裝完成"
echo ""
echo "可執行檔：${BIN_DIR}/agent-fw"
echo "套件路徑：${LIB_ROOT}/agent_fw"
echo ""

# 檢查 PATH
if [[ ":${PATH}:" != *":${BIN_DIR}:"* ]]; then
    echo "⚠ ${BIN_DIR} 不在 PATH 中"
    echo "  請把這行加到你的 ~/.bashrc 或 ~/.zshrc："
    echo ""
    echo "      export PATH=\"\${HOME}/.local/bin:\${PATH}\""
    echo ""
    echo "  然後：source ~/.bashrc（或重開終端）"
fi

echo ""
echo "驗證安裝："
"${BIN_DIR}/agent-fw" --version
