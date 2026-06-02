"""core.py — 共用操作：版本解析、frontmatter、檔案定位。

純 stdlib，無外部依賴。
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# 框架根目錄定位
# ---------------------------------------------------------------------------

def find_framework_root(start: Optional[Path] = None) -> Path:
    """從 start 開始往上找，找不到任何 framework 標記時回傳 start。

    標記順序：VERSION 檔 > .framework/ 目錄 > framework-version 標頭。
    找不到時 raise FileNotFoundError（呼叫端決定 fallback）。
    """
    p = Path(start or os.getcwd()).resolve()
    # 1) 找當前目錄與所有父目錄的 VERSION
    for cand in [p, *p.parents]:
        if (cand / "VERSION").is_file():
            return cand
    # 2) 找 .framework/
    for cand in [p, *p.parents]:
        if (cand / ".framework").is_dir():
            return cand
    raise FileNotFoundError(
        f"找不到 framework 根目錄（從 {p} 往上）"
    )


# ---------------------------------------------------------------------------
# SemVer 解析與比較
# ---------------------------------------------------------------------------

SEMVER_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?(?:\+([0-9A-Za-z.-]+))?$")


@dataclass(frozen=True)
class Version:
    major: int
    minor: int
    patch: int
    pre: str = ""
    build: str = ""

    @classmethod
    def parse(cls, s: str) -> "Version":
        s = (s or "").strip()
        m = SEMVER_RE.match(s)
        if not m:
            raise ValueError(f"不是合法的 SemVer：{s!r}")
        return cls(int(m.group(1)), int(m.group(2)), int(m.group(3)),
                   m.group(4) or "", m.group(5) or "")

    def __str__(self) -> str:
        s = f"v{self.major}.{self.minor}.{self.patch}"
        if self.pre:
            s += f"-{self.pre}"
        if self.build:
            s += f"+{self.build}"
        return s

    def __lt__(self, other: "Version") -> bool:
        return (self.major, self.minor, self.patch, self.pre) < (
            other.major, other.minor, other.patch, other.pre,
        )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Version) and (
            self.major, self.minor, self.patch, self.pre, self.build
        ) == (other.major, other.minor, other.patch, other.pre, other.build)

    def delta_type(self, other: "Version") -> str:
        """回傳 self 對 other 的落差類型。

        - "none"    : 相同
        - "patch"   : patch 變動
        - "minor"   : minor 變動
        - "major"   : major 變動
        - "bootstrap" : other 是空字串
        """
        if self == other:
            return "none"
        if other.major != self.major:
            return "major"
        if other.minor != self.minor:
            return "minor"
        return "patch"


# ---------------------------------------------------------------------------
# VERSION 檔
# ---------------------------------------------------------------------------

@dataclass
class VersionManifest:
    raw: str
    version: Version
    schema_version: int = 1
    last_updated: str = ""
    framework_status: str = "stable"
    breaking_changes_since_v0: str = "none"
    min_compatible_agent_version: str = "1.0.0"
    recommended_restart_on_bump: bool = True
    extra: dict = field(default_factory=dict)

    @classmethod
    def parse(cls, path: Path) -> "VersionManifest":
        text = Path(path).read_text(encoding="utf-8")
        first = text.splitlines()[0].strip()
        if not first.startswith("v"):
            raise ValueError(f"{path} 第一行應為 SemVer，目前是 {first!r}")
        version = Version.parse(first)
        meta: dict = {}
        for line in text.splitlines()[1:]:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                k, _, v = line.partition(":")
                meta[k.strip()] = v.strip()
        return cls(
            raw=text,
            version=version,
            schema_version=int(meta.get("schema-version", "1")),
            last_updated=meta.get("last-updated", ""),
            framework_status=meta.get("framework-status", "stable"),
            breaking_changes_since_v0=meta.get("breaking-changes-since-v0", "none"),
            min_compatible_agent_version=meta.get("min-compatible-agent-version", "1.0.0"),
            recommended_restart_on_bump=_to_bool(meta.get("recommended-restart-on-bump", "true")),
            extra=meta,
        )

    def write(self, path: Path) -> None:
        lines = [str(self.version)]
        lines.append(f"# Agent Framework — Version Manifest")
        lines.append(f"# 任何 AI 讀取本框架的第一個檔案應是 VERSION。")
        lines.append(f"# 接著依序讀取：CHANGELOG → MIGRATION → .framework/PROTOCOL → INDEX。")
        lines.append("")
        lines.append(f"schema-version: {self.schema_version}")
        lines.append(f"last-updated: {self.last_updated}")
        lines.append(f"framework-status: {self.framework_status}")
        lines.append(f"breaking-changes-since-v0: {self.breaking_changes_since_v0}")
        lines.append(f"min-compatible-agent-version: {self.min_compatible_agent_version}")
        lines.append(f"recommended-restart-on-bump: {str(self.recommended_restart_on_bump).lower()}")
        Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def _to_bool(s: str) -> bool:
    return s.strip().lower() in ("true", "1", "yes", "y", "on")


# ---------------------------------------------------------------------------
# Frontmatter 解析（YAML 簡化版，支援我們用的 key: value 形式）
# ---------------------------------------------------------------------------

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def extract_metadata(path) -> dict:
    """從 markdown 抓出 framework-version / compat-* / status 等關鍵中继資料。

    支援兩種格式：
    1. YAML frontmatter（以 --- 開頭）
    2. ```yaml``` 程式碼區塊（多個區塊也會合併，後者覆蓋前者）
    3. 前 5 行的 `key: value` 行

    回傳 dict，可能有也可能沒有值。
    """
    p = Path(path)
    if not p.is_file():
        return {}
    text = p.read_text(encoding="utf-8")
    out: dict = {}

    # 1) Frontmatter
    fm, _ = parse_frontmatter(text)
    out.update(fm)

    # 2) ```yaml``` 區塊
    for m in re.finditer(r"```(?:yaml|yml)\n(.*?)\n```", text, re.DOTALL):
        for line in m.group(1).splitlines():
            if ":" in line and not line.strip().startswith("#"):
                k, _, v = line.partition(":")
                k = k.strip()
                v = v.strip().strip("'\"")
                if k and v:
                    out.setdefault(k, v)

    # 3) 前 5 行的 key: value（適用純自由格式的檔案）
    for line in text.splitlines()[:5]:
        if re.match(r"^[a-z][a-z0-9-]*:\s*\S", line.strip()):
            k, _, v = line.partition(":")
            out.setdefault(k.strip(), v.strip())

    return out


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """從 markdown 文字拆出 frontmatter 與 body。

    支援的格式：簡單 `key: value` 與 `key:` 後接縮排行（多行值）。
    """
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    raw = m.group(1)
    body = text[m.end():]
    out: dict = {}
    lines = raw.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if ":" in line:
            k, _, v = line.partition(":")
            k = k.strip()
            v = v.strip()
            if not v:
                # 多行值：往後找縮排行
                j = i + 1
                collected = []
                while j < len(lines) and (lines[j].startswith(" ") or lines[j].startswith("\t")):
                    collected.append(lines[j].strip())
                    j += 1
                if collected:
                    out[k] = collected
                    i = j
                    continue
            out[k] = v
        i += 1
    return out, body


# ---------------------------------------------------------------------------
# CHANGELOG 解析
# ---------------------------------------------------------------------------

CHANGELOG_HEADER_RE = re.compile(r"^##\s+\[([^\]]+)\]\s*-?\s*(.*)$")


@dataclass
class ChangelogEntry:
    version: str
    date: str
    body: str
    is_unreleased: bool = False

    @classmethod
    def parse_file(cls, text: str) -> list:
        out: list = []
        current = None
        body_buf: list = []
        for line in text.splitlines():
            m = CHANGELOG_HEADER_RE.match(line)
            if m:
                if current is not None:
                    current.body = "\n".join(body_buf).strip()
                    out.append(current)
                version = m.group(1).strip()
                date = m.group(2).strip()
                current = cls(
                    version=version,
                    date=date,
                    body="",
                    is_unreleased=(version.lower() == "unreleased" or date.lower() == "unreleased"),
                )
                body_buf = []
            elif current is not None and not line.startswith("# "):
                body_buf.append(line)
        if current is not None:
            current.body = "\n".join(body_buf).strip()
            out.append(current)
        return out

    def changes_by_section(self) -> dict:
        sections: dict = {}
        current_section = "Other"
        for line in self.body.splitlines():
            if line.startswith("### "):
                current_section = line[4:].strip()
                sections.setdefault(current_section, [])
            elif line.strip().startswith("- "):
                sections.setdefault(current_section, []).append(line.strip()[2:])
        return sections


# ---------------------------------------------------------------------------
# 小工具
# ---------------------------------------------------------------------------

def read_text(path: Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def all_markdown_files(root: Path) -> list:
    root = Path(root)
    out = []
    for p in root.rglob("*.md"):
        # 跳過隱藏目錄（除了 .framework）
        parts = p.relative_to(root).parts
        skip = False
        for part in parts[:-1]:
            if part.startswith(".") and part != ".framework":
                skip = True
                break
        if not skip:
            out.append(p)
    return sorted(out)


def extract_internal_links(text: str) -> list:
    """從 markdown 文字中抓出所有內部連結（不含 http）。"""
    pat = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    out = []
    for m in pat.finditer(text):
        target = m.group(2).strip()
        if target.startswith("http") or target.startswith("#"):
            continue
        out.append((m.group(1), target))
    return out


def safe_relpath(from_file: Path, link_target: str) -> Path:
    """解析相對路徑，自動補上 .md 後綴。"""
    base = Path(from_file).parent
    target = (base / link_target).resolve()
    if not target.exists() and not target.is_dir() and not link_target.endswith("/"):
        cand = target.with_suffix(".md")
        if cand.exists():
            return cand
    return target
