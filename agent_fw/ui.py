"""ui.py — 純 ANSI 色彩的顯示輔助。

不依賴 `rich` `textual` `colorama`，跨平台行為：
- TTY 自動啟用色彩
- 非 TTY（pipe、redirect）關閉色彩
- 支援 NO_COLOR 環境變數
"""

from __future__ import annotations

import os
import sys
from typing import Optional


# ---------------------------------------------------------------------------
# 色彩開關
# ---------------------------------------------------------------------------

def _color_enabled() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR") in ("1", "true", "yes"):
        return True
    return sys.stdout.isatty()


_ENABLED = _color_enabled()


def _c(code: str, s: str) -> str:
    if not _ENABLED:
        return s
    return f"\033[{code}m{s}\033[0m"


# 便捷包裝
def red(s: str) -> str:    return _c("31", s)
def green(s: str) -> str:  return _c("32", s)
def yellow(s: str) -> str: return _c("33", s)
def blue(s: str) -> str:   return _c("34", s)
def magenta(s: str) -> str: return _c("35", s)
def cyan(s: str) -> str:   return _c("36", s)
def gray(s: str) -> str:   return _c("90", s)
def bold(s: str) -> str:   return _c("1", s)
def dim(s: str) -> str:    return _c("2", s)


# ---------------------------------------------------------------------------
# 輸出區塊
# ---------------------------------------------------------------------------

def header(title: str) -> None:
    bar = "═" * max(0, 60 - len(title) - 2)
    print(cyan(bold(f"══ {title} {bar}")))


def subheader(title: str) -> None:
    print(blue(bold(f"── {title}")))


def info(msg: str) -> None:
    print(f"  {cyan('•')} {msg}")


def success(msg: str) -> None:
    print(f"  {green('✓')} {msg}")


def warn(msg: str) -> None:
    print(f"  {yellow('⚠')}  {msg}", file=sys.stderr)


def error(msg: str) -> None:
    print(f"  {red('✗')} {msg}", file=sys.stderr)


def kv(key: str, value: str, indent: int = 2) -> None:
    pad = " " * indent
    print(f"{pad}{gray(key + ':')} {value}")


def restart_warning(reason: str, action: str, impact: str, alt: Optional[str] = None) -> None:
    print()
    print(yellow(bold("⚠️  框架重啟建議")))
    print(f"  {yellow('原因')}：{reason}")
    print(f"  {yellow('建議')}：{action}")
    print(f"  {yellow('影響')}：{impact}")
    if alt:
        print(f"  {yellow('替代')}：{alt}")
    print()


def prompt_yes_no(question: str, default: bool = False) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    try:
        ans = input(f"  {cyan('?')} {question} {suffix}: ").strip().lower()
    except EOFError:
        return default
    if not ans:
        return default
    return ans in ("y", "yes")


def prompt_choice(question: str, choices: list) -> Optional[int]:
    print(f"  {cyan('?')} {question}")
    for i, c in enumerate(choices, 1):
        print(f"      {i}) {c}")
    try:
        ans = input(f"      {cyan('>')} ").strip()
    except EOFError:
        return None
    try:
        idx = int(ans) - 1
        return idx if 0 <= idx < len(choices) else None
    except ValueError:
        return None


def prompt_text(question: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    try:
        ans = input(f"  {cyan('?')} {question}{suffix}: ").strip()
    except EOFError:
        return default
    return ans or default
