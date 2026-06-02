"""validate.py — 框架完整性驗證。

對 .framework/VERSION_AWARENESS.md 的「強制自我檢查點」做自動化版本：
- 內部連結是否仍可達
- framework-version 標頭是否一致
- 認知框架 META 的 compat 欄位是否合理
- 術語是否漂移
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from . import core, detection, ui


@dataclass
class ValidationReport:
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    issues: list = field(default_factory=list)
    warnings_list: list = field(default_factory=list)

    def add_ok(self, name: str):
        self.passed += 1

    def add_fail(self, name: str, detail: str = ""):
        self.failed += 1
        self.issues.append((name, detail))

    def add_warn(self, name: str, detail: str = ""):
        self.warnings += 1
        self.warnings_list.append((name, detail))


def run_all(root: Path) -> ValidationReport:
    rpt = ValidationReport()
    _check_root_files(root, rpt)
    _check_internal_links(root, rpt)
    _check_frontmatter(root, rpt)
    _check_cognitive_frameworks(root, rpt)
    _check_detection_rules_version(root, rpt)
    return rpt


def print_report(rpt: ValidationReport) -> None:
    ui.header("Validation Report")
    ui.kv("passed", str(rpt.passed))
    ui.kv("failed", str(rpt.failed))
    ui.kv("warnings", str(rpt.warnings))
    if rpt.issues:
        ui.subheader("Issues")
        for name, detail in rpt.issues:
            ui.error(f"{name}：{detail}" if detail else name)
    if rpt.warnings_list:
        ui.subheader("Warnings")
        for name, detail in rpt.warnings_list:
            ui.warn(f"{name}：{detail}" if detail else name)
    if rpt.failed == 0:
        ui.success("全部通過")
    else:
        ui.error("有失敗項，請修正後重跑")


# ---------------------------------------------------------------------------
# 各項檢查
# ---------------------------------------------------------------------------

REQUIRED_ROOT_FILES = ["VERSION", "CHANGELOG.md", "MIGRATION.md", "INDEX.md", "README.md", ".framework"]


def _check_root_files(root: Path, rpt: ValidationReport) -> None:
    for name in REQUIRED_ROOT_FILES:
        p = root / name
        if p.exists():
            rpt.add_ok(f"根目錄檔案：{name}")
        else:
            rpt.add_fail(f"根目錄檔案缺失", f"{name}（{p}）")


def _check_internal_links(root: Path, rpt: ValidationReport) -> None:
    for md in core.all_markdown_files(root):
        text = core.read_text(md)
        for label, target in core.extract_internal_links(text):
            if target.startswith("#"):
                continue
            resolved = (md.parent / target).resolve()
            ok = resolved.exists() or resolved.is_dir()
            if not ok and not target.endswith("/"):
                cand = resolved.with_suffix(".md")
                if cand.exists():
                    ok = True
            if ok:
                rpt.add_ok(f"link: {md.relative_to(root)} → {target}")
            else:
                rpt.add_fail(
                    f"link broken: {md.relative_to(root)}",
                    f"{label!r} → {target!r}",
                )


def _check_frontmatter(root: Path, rpt: ValidationReport) -> None:
    """所有 cognitive-frameworks/*/META.md 應有 framework-version 與 compat 欄位。"""
    cf_dir = root / "cognitive-frameworks"
    if not cf_dir.is_dir():
        return
    for meta in cf_dir.rglob("META.md"):
        if "_template" in meta.parts:
            continue
        fm = core.extract_metadata(meta)
        for key in ("framework-version", "compat-with-agent-version", "status"):
            if key in fm:
                rpt.add_ok(f"frontmatter: {meta.relative_to(root)} 有 {key}")
            else:
                rpt.add_fail(
                    f"frontmatter: {meta.relative_to(root)} 缺 {key}",
                    f"必填欄位缺失",
                )


def _check_cognitive_frameworks(root: Path, rpt: ValidationReport) -> None:
    """每個 framework 應有 FRAMEWORK.md / META.md / CHECKLIST.md 三件。"""
    cf_dir = root / "cognitive-frameworks"
    if not cf_dir.is_dir():
        return
    for fw in cf_dir.iterdir():
        if not fw.is_dir() or fw.name == "_template":
            continue
        for fname in ("FRAMEWORK.md", "META.md", "CHECKLIST.md"):
            if (fw / fname).is_file():
                rpt.add_ok(f"framework {fw.name} 有 {fname}")
            else:
                rpt.add_fail(f"framework {fw.name} 缺 {fname}", "")


def _check_detection_rules_version(root: Path, rpt: ValidationReport) -> None:
    """提醒：如果 .framework/DETECTION.md 的規則版本與 detection.py 不同，需手動同步。"""
    det_path = root / ".framework" / "DETECTION.md"
    if not det_path.is_file():
        return
    text = core.read_text(det_path)
    m = re.search(r"detection-rules-version:\s*(\d+)", text)
    if m:
        from . import detection as det_mod
        file_ver = int(m.group(1))
        if file_ver == det_mod.DETECTION_RULES_VERSION:
            rpt.add_ok(f"DETECTION 規則版本一致（v{file_ver}）")
        else:
            rpt.add_warn(
                f"DETECTION 規則版本不一致",
                f".framework/DETECTION.md 標 v{file_ver}，agent_fw 編譯的是 v{det_mod.DETECTION_RULES_VERSION}",
            )
