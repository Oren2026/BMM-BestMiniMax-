"""backoff_strategies.factory — 策略工廠。"""

from __future__ import annotations

from typing import Any, Dict

from .base import BaseStrategy
from .registry import all_strategies, get, list_strategies


def create(name: str, **params) -> BaseStrategy:
    """用名字與參數建立策略實例。"""
    cls = get(name)
    return cls(**params)


def describe_all() -> str:
    """回傳所有策略的可讀描述（給 CLI `list-strategies` 用）。"""
    out = []
    for name in list_strategies():
        cls = all_strategies()[name]
        params = ", ".join(f"{k}={v}" for k, v in cls.default_params.items())
        out.append(f"  · {name:6s}  {cls.description}\n              預設參數：{params}")
    return "\n".join(out)


__all__ = ["create", "describe_all", "list_strategies", "get"]
