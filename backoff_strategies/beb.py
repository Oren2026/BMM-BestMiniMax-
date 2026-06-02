"""backoff_strategies.beb — 802.11 標準 Binary Exponential Backoff。"""

from __future__ import annotations

from typing import Any, Dict

from .base import BaseStrategy
from .registry import register


@register
class BEB(BaseStrategy):
    """802.11 標準 Binary Exponential Backoff。

    失敗：CW ← min(CW_max, 2 × CW)（指數成長）
    成功：CW ← CW_min（直接重置——這是 BEB 的爭議點）
    """

    name = "beb"
    description = "802.11 標準 Binary Exponential Backoff。失敗指數倍增、傳完直接重置。"
    default_params: Dict[str, Any] = {
        "cw_min": 15,
        "cw_max": 1023,
    }

    def initial_cw(self, **ctx) -> int:
        return ctx.get("cw_min", self.cw_min)

    def update_on_failure(self, current_cw: int, **ctx) -> int:
        cw_max = ctx.get("cw_max", self.cw_max)
        return min(cw_max, current_cw * 2)

    def update_on_success(self, current_cw: int, **ctx) -> int:
        return ctx.get("cw_min", self.cw_min)
