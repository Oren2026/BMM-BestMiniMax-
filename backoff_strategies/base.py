"""backoff_strategies.base — 策略抽象基底類別。

所有 backoff 策略都必須繼承 BaseStrategy 並實作三個方法。
這樣加新策略只要寫一個檔、掛上 @register 即可。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseStrategy(ABC):
    """所有 backoff 策略的統一介面。"""

    # 必填：中繼資料
    name: str = "base"
    description: str = ""
    default_params: Dict[str, Any] = {}

    def __init__(self, **params):
        """以 kwargs 傳入策略參數；未提供者用 default_params。"""
        merged = {**self.default_params, **params}
        self.params = merged
        for k, v in merged.items():
            setattr(self, k, v)

    @abstractmethod
    def initial_cw(self, **ctx) -> int:
        """回傳新 station 的初始 CW。ctx 提供 cw_min / cw_max 等環境參數。"""
        raise NotImplementedError

    @abstractmethod
    def update_on_failure(self, current_cw: int, **ctx) -> int:
        """碰撞後的新 CW。"""
        raise NotImplementedError

    @abstractmethod
    def update_on_success(self, current_cw: int, **ctx) -> int:
        """成功後的新 CW。"""
        raise NotImplementedError

    def __repr__(self) -> str:
        param_str = ", ".join(f"{k}={v!r}" for k, v in self.params.items())
        return f"{self.__class__.__name__}({param_str})"
