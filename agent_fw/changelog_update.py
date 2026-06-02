"""changelog_update.py — 自動往 CHANGELOG 追加條目。

對應 templates/changelog-entry.template.md。
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from . import core


UNRELEASED_HEADER_RE = re.compile(r"^##\s+\[Unreleased\]\s*$", re.MULTILINE)


def append_entry(
    root: Path,
    version: str,
    date: str,
    bump_type: str,
    reason: str,
    breaking_changes: Optional[list] = None,
    notes: str = "",
) -> None:
    """在 CHANGELOG.md 內插入新條目（位於 Unreleased 之後、其他已釋出條目之前）。"""
    path = root / "CHANGELOG.md"
    if not path.is_file():
        return
    text = core.read_text(path)

    entry = _build_entry(version, date, bump_type, reason, breaking_changes or [], notes)

    # 若有 Unreleased 區段，插在其後
    if UNRELEASED_HEADER_RE.search(text):
        # 找 Unreleased 區段的結尾（下一個 `## [` 或檔案結尾）
        new_text = UNRELEASED_HEADER_RE.sub(
            lambda m: m.group(0) + "\n\n" + entry + "\n",
            text,
            count=1,
        )
    else:
        # 沒有 Unreleased 就插在檔頭
        new_text = entry + "\n" + text

    core.write_text(path, new_text)


def _build_entry(version: str, date: str, bump_type: str, reason: str, breaking_changes: list, notes: str) -> str:
    lines = [f"## [{version}] - {date}"]
    lines.append("")
    # 根據 bump_type 自動分類
    if bump_type == "major":
        lines.append("### Changed")
        lines.append(f"- {reason}")
        if breaking_changes:
            lines.append("")
            lines.append("### Migration")
            for c in breaking_changes:
                lines.append(f"- {c}")
    elif bump_type == "minor":
        lines.append("### Added")
        lines.append(f"- {reason}")
    else:  # patch
        lines.append("### Fixed")
        lines.append(f"- {reason}")
    if notes:
        lines.append("")
        lines.append("### Notes")
        lines.append(f"- {notes}")
    return "\n".join(lines)
