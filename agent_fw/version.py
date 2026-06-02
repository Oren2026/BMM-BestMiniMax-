"""version.py — 版本管理。

主要職責：讀取與更新 VERSION 檔、計算版本落差。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional

from . import core, ui


def get_current(root: Path) -> core.VersionManifest:
    """讀取 framework 根目錄下的 VERSION。"""
    return core.VersionManifest.parse(Path(root) / "VERSION")


def bump(root: Path, bump_type: str, reason: str) -> core.VersionManifest:
    """bump 版本並寫回 VERSION 檔。

    bump_type: "major" | "minor" | "patch"
    reason: 為什麼要 bump（會寫進 CHANGELOG）
    """
    if bump_type not in ("major", "minor", "patch"):
        raise ValueError(f"bump_type 應為 major/minor/patch，目前是 {bump_type!r}")

    manifest = get_current(root)
    v = manifest.version
    if bump_type == "major":
        new = core.Version(v.major + 1, 0, 0)
    elif bump_type == "minor":
        new = core.Version(v.major, v.minor + 1, 0)
    else:
        new = core.Version(v.major, v.minor, v.patch + 1)

    manifest.version = new
    manifest.last_updated = date.today().isoformat()
    if bump_type == "major":
        manifest.breaking_changes_since_v0 = "see MIGRATION.md"
    manifest.write(Path(root) / "VERSION")
    return manifest
