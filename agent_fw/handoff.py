"""handoff.py — 進度交接管理。

對應 .framework/HANDOFF.md 與 templates/handoff.template.md。
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from . import core, ui, version


# 簡化版 YAML 解析：只支援 key: value 與列表
def _simple_yaml_load(text: str) -> dict:
    out: dict = {}
    current_list_key: Optional[str] = None
    for line in text.splitlines():
        if not line.strip():
            continue
        if line.startswith("  - ") or line.startswith("    - "):
            if current_list_key is not None:
                v = line.strip().lstrip("-").strip()
                if isinstance(out.get(current_list_key), list):
                    out[current_list_key].append(v)
            continue
        if ":" in line:
            k, _, v = line.partition(":")
            k = k.strip()
            v = v.strip()
            if not v:
                # 後面是列表
                current_list_key = k
                out[k] = []
            else:
                current_list_key = None
                out[k] = v
    return out


@dataclass
class HandoffValidation:
    valid: bool
    issues: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    framework_version: str = ""
    last_known_version: str = ""
    is_compatible: bool = True
    delta_type: str = "none"


# ---------------------------------------------------------------------------
# 建立
# ---------------------------------------------------------------------------

TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "templates" / "handoff.template.md"


def create(
    out_path: Path,
    framework_root: Path,
    task_name: str,
    context_summary: str,
    current_state: str = "",
    decisions: str = "",
    open_questions: str = "",
    next_actions: str = "",
    loaded_frameworks: str = "",
    detection_notes: str = "",
    from_session: str = "",
) -> Path:
    """從範本建立新 handoff。"""
    if not TEMPLATE_PATH.is_file():
        raise FileNotFoundError(f"找不到 handoff 範本：{TEMPLATE_PATH}")

    manifest = version.get_current(framework_root)
    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    handoff_id = f"{datetime.now().strftime('%Y%m%dT%H%M%S')}-{task_name[:30]}"

    text = core.read_text(TEMPLATE_PATH)
    # 替換標題
    text = text.replace("<任務名稱>", task_name, 1)

    # 在 frontmatter 區段填入識別資訊
    fill = (
        f"handoff-id: {handoff_id}\n"
        f"framework-version: {manifest.version}\n"
        f"schema-version: {manifest.schema_version}\n"
        f"from-session: \"{from_session or 'current'}\"\n"
        f"to-session: next\n"
        f"created-at: {now}\n"
    )
    text = re.sub(
        r"## 識別（必填\）\n\n```yaml\n([\s\S]*?)\n```",
        lambda m: f"## 識別（必填）\n\n```yaml\n{fill}```",
        text,
        count=1,
    )

    # 替換其他常見佔位符
    text = text.replace("<context-summary>", context_summary)
    text = text.replace("<current-state>", current_state or "（待補）")
    text = text.replace("<decisions>", decisions or "（待補）")
    text = text.replace("<open-questions>", open_questions or "（待補）")
    text = text.replace("<next-actions>", next_actions or "（待補）")
    text = text.replace("<loaded-frameworks>", loaded_frameworks or "layered-task-execution (1.0.0)")
    text = text.replace("<detection-notes>", detection_notes or "無觀察到版本混雜跡象")

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    return out_path


# ---------------------------------------------------------------------------
# 驗證
# ---------------------------------------------------------------------------

FRONTMATTER_YAML_RE = re.compile(r"```yaml\n(.*?)\n```", re.DOTALL)


def validate(handoff_path: Path, framework_root: Path) -> HandoffValidation:
    """驗證 handoff 檔案是否有效、是否與當前 framework 相容。"""
    handoff_path = Path(handoff_path)
    rpt = HandoffValidation(valid=False)

    if not handoff_path.is_file():
        rpt.issues.append(f"檔案不存在：{handoff_path}")
        return rpt

    text = core.read_text(handoff_path)

    # 抓第一個 yaml 區塊（識別資訊）
    m = FRONTMATTER_YAML_RE.search(text)
    if not m:
        rpt.issues.append("找不到識別資訊（第一個 yaml 區塊）")
        return rpt
    meta = _simple_yaml_load(m.group(1))

    # 必填欄位
    required = ["handoff-id", "framework-version", "created-at"]
    for k in required:
        if k not in meta or not meta[k]:
            rpt.issues.append(f"必填欄位缺失：{k}")

    if "framework-version" in meta:
        rpt.framework_version = meta["framework-version"]
        # 與當前 VERSION 比較
        try:
            current = version.get_current(framework_root)
            current_v = str(current.version)
            rpt.last_known_version = rpt.framework_version
            cv = core.Version.parse(rpt.framework_version)
            cur_v = core.Version.parse(current_v)
            rpt.delta_type = cur_v.delta_type(cv)
            rpt.is_compatible = (rpt.delta_type != "major")
            if not rpt.is_compatible:
                rpt.issues.append(f"framework-version 為 MAJOR 落差（{rpt.framework_version} → {current_v}），必須重啟 session")
        except Exception as e:
            rpt.warnings.append(f"無法比對版本：{e}")

    # 過期檢查
    if "created-at" in meta:
        try:
            ts = datetime.fromisoformat(meta["created-at"])
            age_days = (datetime.now(ts.tzinfo) - ts).days
            if age_days > 7 and rpt.is_compatible:
                rpt.warnings.append(f"handoff 已 {age_days} 天；同版本 7 天後視為過期，建議重新確認")
        except ValueError:
            rpt.warnings.append("created-at 格式不正確")

    rpt.valid = len(rpt.issues) == 0
    return rpt


def print_validation(rpt: HandoffValidation) -> None:
    ui.header("Handoff Validation")
    if rpt.valid:
        ui.success("通過")
    else:
        ui.error("不通過")
    if rpt.issues:
        ui.subheader("Issues")
        for i in rpt.issues:
            ui.error(i)
    if rpt.warnings:
        ui.subheader("Warnings")
        for w in rpt.warnings:
            ui.warn(w)
    ui.subheader("版本相容性")
    ui.kv("framework-version", rpt.framework_version)
    ui.kv("delta-type", rpt.delta_type)
    ui.kv("is-compatible", str(rpt.is_compatible))
