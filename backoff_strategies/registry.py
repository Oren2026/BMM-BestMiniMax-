"""backoff_strategies.registry — 自動註冊機制。

新策略只要：
1. 繼承 BaseStrategy
2. 在模組最底加上 @register

就會自動出現在 list_strategies() 與 factory.create()。
"""

from __future__ import annotations

from typing import Dict, List, Type

from .base import BaseStrategy


_REGISTRY: Dict[str, Type[BaseStrategy]] = {}


def register(cls: Type[BaseStrategy]) -> Type[BaseStrategy]:
    """把策略類別註冊到全域字典。"""
    if not cls.name or cls.name == "base":
        raise ValueError(f"{cls.__name__} 必須設定 name 屬性（不能是 'base'）")
    if cls.name in _REGISTRY:
        raise ValueError(f"策略名稱衝突：{cls.name} 已被 {_REGISTRY[cls.name].__name__} 註冊")
    _REGISTRY[cls.name] = cls
    return cls


def get(name: str) -> Type[BaseStrategy]:
    """取得策略類別（不是實例）。"""
    if name not in _REGISTRY:
        raise KeyError(
            f"找不到策略 {name!r}。可用策略：{list_strategies()}"
        )
    return _REGISTRY[name]


def list_strategies() -> List[str]:
    """列出所有已註冊的策略名稱。"""
    return sorted(_REGISTRY.keys())


def all_strategies() -> Dict[str, Type[BaseStrategy]]:
    """取得所有策略類別的字典（給 list-style 顯示用）。"""
    return dict(_REGISTRY)
