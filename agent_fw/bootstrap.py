"""bootstrap.py — 啟動 session 時跑的盤點流程。

對應 .framework/BOOTSTRAP.md。
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

from . import core, ui, version


@dataclass
class BootstrapReport:
    framework_version: str = ""
    schema_version: int = 1
    last_updated: str = ""
    changelog_new_entries: int = 0
    changelog_key_points: list = field(default_factory=list)
    last_known_version: str = "unknown"
    delta_type: str = "bootstrap"
    restart_recommended: bool = False
    detection_triggered: bool = False
    restart_reason: str = ""
    cognitive_frameworks_loaded: list = field(default_factory=list)
    handoffs_received: int = 0
    handoffs_source: list = field(default_factory=list)
    bootstrap_status: str = "complete"
    block_reason: Optional[str] = None
    ready_for_task: bool = True

    def to_dict(self) -> dict:
        return asdict(self)

    def to_yaml(self) -> str:
        """輸出為簡單 YAML（為了不引入 PyYAML 依賴）。"""
        lines = []
        for k, v in self.to_dict().items():
            if isinstance(v, list):
                if not v:
                    lines.append(f"{k}: []")
                else:
                    lines.append(f"{k}:")
                    for item in v:
                        if isinstance(item, dict):
                            lines.append(f"  - {{{', '.join(f'{ik!r}: {iv!r}' for ik, iv in item.items())}}}")
                        else:
                            lines.append(f"  - {item!r}")
            elif isinstance(v, bool):
                lines.append(f"{k}: {str(v).lower()}")
            elif v is None:
                lines.append(f"{k}: null")
            else:
                lines.append(f"{k}: {v!r}")
        return "\n".join(lines) + "\n"


def run(
    root: Path,
    last_known: Optional[str] = None,
    handoff_path: Optional[Path] = None,
    frameworks_to_load: Optional[list] = None,
) -> BootstrapReport:
    """跑完整 bootstrap 流程，回傳 BootstrapReport。"""
    root = Path(root)
    rpt = BootstrapReport()

    # Step 1: 讀 VERSION
    try:
        manifest = version.get_current(root)
    except FileNotFoundError as e:
        rpt.bootstrap_status = "blocked"
        rpt.block_reason = str(e)
        rpt.ready_for_task = False
        return rpt
    rpt.framework_version = str(manifest.version)
    rpt.schema_version = manifest.schema_version
    rpt.last_updated = manifest.last_updated

    # Step 2: 讀 CHANGELOG，看有幾條新條目
    changelog_path = root / "CHANGELOG.md"
    if changelog_path.is_file():
        text = core.read_text(changelog_path)
        entries = core.ChangelogEntry.parse_file(text)
        # 跳過 Unreleased，算已發布的數量
        released = [e for e in entries if not e.is_unreleased]
        if last_known:
            rpt.changelog_new_entries = sum(
                1 for e in released
                if e.version != last_known and _is_newer(e.version, last_known)
            )
            # 抽三個關鍵點
            for e in released[:3]:
                sections = e.changes_by_section()
                for sec, items in sections.items():
                    if sec in ("Added", "Fixed", "Security") and items:
                        rpt.changelog_key_points.append(f"[{e.version}] {sec}: {items[0]}")
                        break
        else:
            rpt.changelog_new_entries = len(released)
            for e in released[:3]:
                rpt.changelog_key_points.append(f"[{e.version}] released")

    # Step 3: 跑 VERSION_AWARENESS
    if last_known:
        try:
            current = core.Version.parse(str(manifest.version))
            known = core.Version.parse(last_known)
            rpt.last_known_version = last_known
            rpt.delta_type = current.delta_type(known)
        except ValueError:
            rpt.last_known_version = "unknown"
            rpt.delta_type = "bootstrap"

    # 決策重啟
    if rpt.delta_type == "major":
        rpt.restart_recommended = True
        rpt.restart_reason = f"MAJOR 版本變更（{rpt.last_known_version} → {rpt.framework_version}）"
    elif rpt.delta_type == "minor" and _has_deprecated_reference(root, str(manifest.version)):
        rpt.restart_recommended = True
        rpt.restart_reason = "MINOR 變更且本 session 載入了將被取代的章節"

    # 偵測
    from . import detection
    det = detection.run_all(root)
    if det.findings:
        rpt.detection_triggered = True
        if det.overall in ("major", "minor"):
            if not rpt.restart_recommended:
                rpt.restart_recommended = True
                rpt.restart_reason = f"多版本混雜偵測觸發：{', '.join(det.triggered)}"

    # 載入的認知框架
    rpt.cognitive_frameworks_loaded = frameworks_to_load or ["layered-task-execution (default)"]

    # handoff
    if handoff_path:
        from . import handoff
        h = handoff.validate(handoff_path, root)
        rpt.handoffs_received = 1
        rpt.handoffs_source.append(str(handoff_path))
        if not h.valid:
            rpt.bootstrap_status = "incomplete"
            rpt.ready_for_task = False
            rpt.block_reason = f"handoff 驗證失敗：{', '.join(h.issues)}"

    return rpt


def print_report(rpt: BootstrapReport) -> None:
    """把報告以人類可讀的形式印出。"""
    ui.header("Session Bootstrap Report")
    ui.subheader("框架狀態")
    ui.kv("framework-version", rpt.framework_version)
    ui.kv("schema-version", str(rpt.schema_version))
    ui.kv("last-updated", rpt.last_updated or "(unknown)")
    ui.kv("changelog-new-entries", str(rpt.changelog_new_entries))
    if rpt.changelog_key_points:
        ui.info("關鍵點：")
        for kp in rpt.changelog_key_points:
            print(f"      {ui.dim('•')} {kp}")

    ui.subheader("版本感知")
    ui.kv("last-known-version", rpt.last_known_version)
    ui.kv("delta-type", rpt.delta_type)
    ui.kv("restart-recommended", str(rpt.restart_recommended))
    if rpt.restart_reason:
        ui.info(f"理由：{rpt.restart_reason}")
    if rpt.detection_triggered:
        ui.info("DETECTION 觸發")

    ui.subheader("已載入資源")
    for f in rpt.cognitive_frameworks_loaded:
        ui.info(f"cognitive-framework: {f}")
    if rpt.handoffs_received:
        ui.info(f"handoffs: {rpt.handoffs_received} 份")
        for s in rpt.handoffs_source:
            ui.info(f"  - {s}")

    ui.subheader("啟動結果")
    ui.kv("bootstrap-status", rpt.bootstrap_status)
    ui.kv("ready-for-task", str(rpt.ready_for_task))
    if rpt.block_reason:
        ui.error(f"block-reason: {rpt.block_reason}")
    print()

    if rpt.restart_recommended:
        ui.restart_warning(
            reason=rpt.restart_reason or "觸發重啟條件",
            action="開新 session 並重跑 BOOTSTRAP",
            impact="沿用舊版行為會誤觸已廢棄的規則",
            alt="若任務極短（< 5 分鐘）可原地升級",
        )


# ---------------------------------------------------------------------------
# 內部輔助
# ---------------------------------------------------------------------------

def _is_newer(a_str: str, b_str: str) -> bool:
    try:
        a = core.Version.parse(a_str)
        b = core.Version.parse(b_str)
        return a > b
    except ValueError:
        return False


def _has_deprecated_reference(root: Path, _current_version: str) -> bool:
    """檢查 root 下的 markdown 是否有引用被 CHANGELOG 標 Removed 的東西。"""
    cl_path = root / "CHANGELOG.md"
    if not cl_path.is_file():
        return False
    text = core.read_text(cl_path)
    entries = core.ChangelogEntry.parse_file(text)
    removed: list = []
    for e in entries:
        for item in e.changes_by_section().get("Removed", []):
            removed.append(item)
    if not removed:
        return False
    # 簡化：找 markdown 內文是否含任何 removed 字串
    for md in core.all_markdown_files(root):
        if md == cl_path:
            continue
        try:
            body = core.read_text(md)
        except Exception:
            continue
        for item in removed:
            if item and item in body:
                return True
    return False
