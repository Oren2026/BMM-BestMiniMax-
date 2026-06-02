"""plotters.registry — 自動註冊 plotters。"""

from __future__ import annotations

from typing import Dict, List, Type

from .base import BasePlotter


_REGISTRY: Dict[str, Type[BasePlotter]] = {}


def register(cls: Type[BasePlotter]) -> Type[BasePlotter]:
    if not cls.name or cls.name == "base":
        raise ValueError(f"{cls.__name__} 必須設定 name")
    if cls.name in _REGISTRY:
        raise ValueError(f"plotter 名稱衝突：{cls.name}")
    _REGISTRY[cls.name] = cls
    return cls


def get(name: str) -> Type[BasePlotter]:
    if name not in _REGISTRY:
        raise KeyError(f"找不到 plotter {name!r}。可用：{list_plots()}")
    return _REGISTRY[name]


def list_plots() -> List[str]:
    return sorted(_REGISTRY.keys())


def describe_all() -> str:
    out = []
    for name in list_plots():
        cls = _REGISTRY[name]
        out.append(f"  · {name:10s}  {cls.title}")
    return "\n".join(out)


__all__ = ["register", "get", "list_plots", "describe_all"]
