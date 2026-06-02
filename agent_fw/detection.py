"""detection.py — 多版本混雜偵測。

對應 .framework/DETECTION.md 的五條規則：
- D1 標頭一致性
- D2 章節廢棄引用
- D3 時間軸衝突
- D4 術語漂移
- D5 路徑失效
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional

from . import core, ui


# 規則版本——bump detection rules 時同步更新
DETECTION_RULES_VERSION = 1


# 核心術語表（給 D4 用）
TERMINOLOGY_TABLE: dict = {
    "bootstrap": ["cold-start", "init", "startup"],
    "handoff": ["handover", "transfer", "pass-down"],
    "framework-version": [],   # 不要跟 schema-version 混
    "mixed-version": ["version-drift", "multi-version"],
    "restart-recommended": ["reload-required", "session-reset"],
}


@dataclass
class Finding:
    rule: str
    severity: str   # "low" | "medium" | "high"
    evidence: str
    recommendation: str


@dataclass
class DetectionReport:
    rules_version: int = DETECTION_RULES_VERSION
    triggered: list = field(default_factory=list)
    findings: list = field(default_factory=list)
    overall: str = "clean"   # "clean" | "minor" | "major"

    def to_dict(self) -> dict:
        return {
            "rules_version": self.rules_version,
            "triggered": self.triggered,
            "findings": [f.__dict__ for f in self.findings],
            "overall": self.overall,
        }


def run_all(root: Path) -> DetectionReport:
    """跑全部五條規則，回傳彙整報告。"""
    root = Path(root)
    rpt = DetectionReport()

    for fn in (_check_d1, _check_d2, _check_d3, _check_d4, _check_d5):
        for f in fn(root):
            rpt.findings.append(f)
            rpt.triggered.append(f.rule)

    # 計算 overall
    sevs = {f.severity for f in rpt.findings}
    if "high" in sevs:
        rpt.overall = "major"
    elif "medium" in sevs:
        rpt.overall = "minor"
    else:
        rpt.overall = "clean"

    return rpt


def print_report(rpt: DetectionReport) -> None:
    ui.header(f"Detection Report (rules v{rpt.rules_version})")
    if not rpt.findings:
        ui.success("無觸發")
        return
    for f in rpt.findings:
        sev = {"high": ui.red, "medium": ui.yellow, "low": ui.gray}[f.severity]
        print(f"\n  {sev(f'[{f.rule}]')} {sev(f.severity.upper())}")
        ui.kv("evidence", f.evidence, indent=4)
        ui.kv("recommendation", f.recommendation, indent=4)
    print()
    badge = {"clean": ui.green("CLEAN"), "minor": ui.yellow("MINOR"), "major": ui.red("MAJOR")}[rpt.overall]
    ui.kv("overall", badge)


# ---------------------------------------------------------------------------
# D1：標頭一致性
# ---------------------------------------------------------------------------

def _check_d1(root: Path) -> list:
    """所有 markdown 應有 framework-version 標頭（位於 frontmatter 或前 5 行）。"""
    findings: list = []
    versions_seen: dict = {}
    files_no_header: list = []
    for md in core.all_markdown_files(root):
        try:
            text = core.read_text(md)
        except Exception:
            continue
        fm = core.extract_metadata(md)
        fv = fm.get("framework-version") or fm.get("framework_version")
        if fv is None:
            # 不是每個檔案都強制要；只對關鍵檔案要求
            rel = str(md.relative_to(root))
            if rel in ("VERSION", "CHANGELOG.md", "MIGRATION.md", "INDEX.md", "README.md"):
                continue   # 這些檔案的版本是隱含的
            if "_template" in md.parts:
                continue   # 範本本來就含佔位符
            files_no_header.append(rel)
        else:
            # 跳過範本佔位符（如 <X.Y.Z>）
            if "<" in str(fv) or ">" in str(fv):
                continue
            versions_seen.setdefault(str(fv), []).append(rel)

    if len(versions_seen) > 1:
        findings.append(Finding(
            rule="D1",
            severity="medium",
            evidence=f"不同檔案標記的 framework-version 不一致：{dict(versions_seen)}",
            recommendation="統一所有檔案的 framework-version 標頭；當前 framework 版本是事實來源",
        ))
    if files_no_header:
        findings.append(Finding(
            rule="D1",
            severity="low",
            evidence=f"{len(files_no_header)} 個檔案缺 framework-version 標頭（如 {files_no_header[:3]}）",
            recommendation="補上標頭；或忽略（純敘述檔可豁免）",
        ))
    return findings


# ---------------------------------------------------------------------------
# D2：章節廢棄引用
# ---------------------------------------------------------------------------

def _check_d2(root: Path) -> list:
    findings: list = []
    cl_path = root / "CHANGELOG.md"
    if not cl_path.is_file():
        return findings
    entries = core.ChangelogEntry.parse_file(core.read_text(cl_path))
    removed: list = []
    deprecated: list = []
    for e in entries:
        for item in e.changes_by_section().get("Removed", []):
            removed.append(item)
        for item in e.changes_by_section().get("Deprecated", []):
            deprecated.append(item)
    if not removed and not deprecated:
        return findings

    for md in core.all_markdown_files(root):
        if md == cl_path:
            continue
        try:
            text = core.read_text(md)
        except Exception:
            continue
        for item in removed:
            if item and item in text:
                findings.append(Finding(
                    rule="D2",
                    severity="high",
                    evidence=f"{md.relative_to(root)} 引用了已移除的章節：{item!r}",
                    recommendation="替換為新章節路徑",
                ))
        for item in deprecated:
            if item and item in text:
                findings.append(Finding(
                    rule="D2",
                    severity="medium",
                    evidence=f"{md.relative_to(root)} 引用了已廢棄章節：{item!r}",
                    recommendation="規劃遷移；新版釋出後移除",
                ))
    return findings


# ---------------------------------------------------------------------------
# D3：時間軸衝突
# ---------------------------------------------------------------------------

def _check_d3(root: Path) -> list:
    findings: list = []
    cl_path = root / "CHANGELOG.md"
    if not cl_path.is_file():
        return findings
    entries = core.ChangelogEntry.parse_file(core.read_text(cl_path))
    # 建立 version -> date 對照
    ver_to_date: dict = {}
    for e in entries:
        if e.is_unreleased or not e.date:
            continue
        try:
            ver_to_date[e.version] = date.fromisoformat(e.date)
        except ValueError:
            continue
    if not ver_to_date:
        return findings

    today = date.today()
    for md in core.all_markdown_files(root):
        try:
            text = core.read_text(md)
        except Exception:
            continue
        # 找 `framework-version: X.Y.Z` + `created-at: YYYY-MM-DD` 的配對
        # 簡化：直接 grep
        m_ver = re.search(r"framework-version:\s*([vV]?\d+\.\d+\.\d+)", text)
        m_date = re.search(r"created-at:\s*(\d{4}-\d{2}-\d{2})", text)
        if not (m_ver and m_date):
            continue
        ver_str, date_str = m_ver.group(1), m_date.group(1)
        if ver_str not in ver_to_date:
            continue
        try:
            file_date = date.fromisoformat(date_str)
        except ValueError:
            continue
        expected_date = ver_to_date[ver_str]
        if file_date > expected_date + _date_delta() and file_date > today - _date_delta():
            findings.append(Finding(
                rule="D3",
                severity="high",
                evidence=f"{md.relative_to(root)} 標 framework-version {ver_str}（CHANGELOG 顯示 {expected_date}），但 created-at {file_date} 早於版本釋出——可能是時間軸錯誤或偽造",
                recommendation="拒絕套用 handoff；請重新確認",
            ))
    return findings


def _date_delta():
    from datetime import timedelta
    return timedelta(days=1)


# ---------------------------------------------------------------------------
# D4：術語漂移
# ---------------------------------------------------------------------------

def _check_d4(root: Path) -> list:
    findings: list = []
    for md in core.all_markdown_files(root):
        try:
            text = core.read_text(md)
        except Exception:
            continue
        rel = str(md.relative_to(root))
        # 豁免：定義型檔案（列出別名本身就會用到）
        if rel in (".framework/DETECTION.md", "README.md", "INDEX.md"):
            continue
        for canonical, aliases in TERMINOLOGY_TABLE.items():
            if not aliases:
                continue
            for alias in aliases:
                # 嚴格匹配：作為完整單詞出現（避免誤判「initiate」之類）
                pat = re.compile(rf"\b{re.escape(alias)}\b", re.IGNORECASE)
                if pat.search(text):
                    findings.append(Finding(
                        rule="D4",
                        severity="low",
                        evidence=f"{rel} 使用別名 {alias!r}（基準術語：{canonical!r}）",
                        recommendation=f"替換為 {canonical!r}；若是歷史引用可在文末加 gloss",
                    ))
    return findings


# ---------------------------------------------------------------------------
# D5：路徑失效
# ---------------------------------------------------------------------------

def _check_d5(root: Path) -> list:
    findings: list = []
    for md in core.all_markdown_files(root):
        try:
            text = core.read_text(md)
        except Exception:
            continue
        rel = str(md.relative_to(root))
        for label, target in core.extract_internal_links(text):
            # 跳過錨點
            if target.startswith("#"):
                continue
            resolved = (md.parent / target).resolve()
            # 目錄形式
            if target.endswith("/"):
                if not resolved.is_dir():
                    findings.append(Finding(
                        rule="D5",
                        severity="medium",
                        evidence=f"{rel} 連結 {label!r} → {target!r}（目錄不存在）",
                        recommendation="建立目錄或修正路徑",
                    ))
                continue
            # 檔案形式：可能需要加 .md
            if not resolved.exists():
                cand = resolved.with_suffix(".md")
                if cand.exists():
                    continue
                findings.append(Finding(
                    rule="D5",
                    severity="medium",
                    evidence=f"{rel} 連結 {label!r} → {target!r}（檔案不存在）",
                    recommendation="建立檔案或修正路徑",
                ))
    return findings
