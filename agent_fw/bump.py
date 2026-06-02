"""bump.py — 一次完成版本 bump 的所有副作用。

對應 templates/version-bump.template.md：
1. 改 VERSION
2. 追加 CHANGELOG 條目
3. 若 major：在 MIGRATION 補章節
4. 更新 INDEX（不需要，INDEX 是動態清單）
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional

from . import core, ui, version, changelog_update


def run(
    root: Path,
    bump_type: str,
    reason: str,
    breaking_changes: Optional[list] = None,
    notes: Optional[str] = None,
) -> core.VersionManifest:
    """執行 bump，回傳新 manifest。"""
    root = Path(root)
    if bump_type not in ("major", "minor", "patch"):
        raise ValueError(f"bump_type 應為 major/minor/patch，目前是 {bump_type!r}")

    old = version.get_current(root)
    manifest = version.bump(root, bump_type, reason)
    new_ver = str(manifest.version)

    # 追加 CHANGELOG
    changelog_update.append_entry(
        root=root,
        version=new_ver,
        date=date.today().isoformat(),
        bump_type=bump_type,
        reason=reason,
        breaking_changes=breaking_changes or [],
        notes=notes or "",
    )

    # 若 major：在 MIGRATION 補章節
    if bump_type == "major":
        _append_migration_section(
            root,
            from_ver=str(old.version),
            to_ver=new_ver,
            reason=reason,
            breaking_changes=breaking_changes or [],
        )

    return manifest


def _append_migration_section(root: Path, from_ver: str, to_ver: str, reason: str, breaking_changes: list) -> None:
    path = root / "MIGRATION.md"
    if not path.is_file():
        return
    text = core.read_text(path)
    section = (
        f"\n## v{from_ver} → v{to_ver}（{date.today().isoformat()}）\n\n"
        f"### 原因\n{reason}\n\n"
        f"### 破壞性變更\n"
        + ("\n".join(f"- {c}" for c in breaking_changes) if breaking_changes else "- 無\n")
        + "\n\n### 動作\n- 重啟 session 並重跑 BOOTSTRAP\n"
    )
    # 簡單加在檔案末尾（在「給維護者的檢查清單」之前）
    marker = "## 給維護者的檢查清單（每次 bump）"
    if marker in text:
        text = text.replace(marker, section + "\n" + marker)
    else:
        text = text + section
    core.write_text(path, text)
