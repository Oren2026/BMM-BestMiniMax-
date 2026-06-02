"""framework_new.py — 從 _template/ 複製出新的認知框架。

對應 templates/new-framework.template.md。
"""

from __future__ import annotations

import re
import shutil
from datetime import date
from pathlib import Path
from typing import Optional

from . import core, ui


TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "cognitive-frameworks" / "_template"
SLUG_RE = re.compile(r"^[a-z][a-z0-9-]*$")


def create(root: Path, slug: str, name: Optional[str] = None, one_liner: Optional[str] = None) -> Path:
    """從 _template/ 複製出新框架目錄，回傳新目錄路徑。"""
    if not SLUG_RE.match(slug):
        raise ValueError(f"slug 應為 kebab-case，目前是 {slug!r}")
    target = Path(root) / "cognitive-frameworks" / slug
    if target.exists():
        raise FileExistsError(f"目錄已存在：{target}")

    name = name or slug.replace("-", " ").title()
    one_liner = one_liner or "（請在 FRAMEWORK.md 補一句話定義）"

    shutil.copytree(TEMPLATE_DIR, target)

    # 重新命名：去掉 .template
    rename_map = {
        "FRAMEWORK.template.md": "FRAMEWORK.md",
        "META.template.md": "META.md",
        "CHECKLIST.template.md": "CHECKLIST.md",
    }
    for old, new in rename_map.items():
        old_p = target / old
        if old_p.is_file():
            old_p.rename(target / new)

    # 填入基本欄位
    today = date.today().isoformat()
    _fill_template(target / "FRAMEWORK.md", {
        "<Framework Name>": name,
        "<framework-version>": "1.0.0",
        "<一句話定義>": one_liner,
    })
    _fill_template(target / "META.md", {
        "<Framework Name>": name,
        "<framework-slug>": slug,
        "<X.Y.Z>": "1.0.0",
        "<YYYY-MM-DD>": today,
    })
    _fill_template(target / "CHECKLIST.md", {
        "<Framework Name>": name,
    })

    return target


def _fill_template(path: Path, replacements: dict) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    for old, new in replacements.items():
        text = text.replace(old, str(new))
    path.write_text(text, encoding="utf-8")
