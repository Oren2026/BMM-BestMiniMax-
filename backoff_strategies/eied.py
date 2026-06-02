"""backoff_strategies.eied — Exponential Increase Exponential Decrease。"""

from __future__ import annotations

from typing import Any, Dict

from .base import BaseStrategy
from .registry import register


@register
class EIED(BaseStrategy):
    """Exponential Increase Exponential Decrease。

    失敗：CW ← min(CW_max, ⌊CW × m⌋)
    成功：CW ← max(CW_min, ⌊CW × n⌋)

    跟 BEB 一樣對碰撞反應快（指數增），但成功時也用指數降
    （不是直接重置）。在高負載下比 BEB 表現更好。
    """

    name = "eied"
    description = "Exponential Increase Exponential Decrease。碰撞指數增、成功指數降。"
    default_params: Dict[str, Any] = {
        "cw_min": 15,
        "cw_max": 1023,
        "m": 2.0,     # 失敗倍數（> 1）
        "n": 0.5,     # 成功倍數（< 1）
    }

    def initial_cw(self, **ctx) -> int:
        return ctx.get("cw_min", self.cw_min)

    def update_on_failure(self, current_cw: int, **ctx) -> int:
        cw_max = ctx.get("cw_max", self.cw_max)
        m = ctx.get("m", self.m)
        return min(cw_max, int(current_cw * m))

    def update_on_success(self, current_cw: int, **ctx) -> int:
        cw_min = ctx.get("cw_min", self.cw_min)
        n = ctx.get("n", self.n)
        return max(cw_min, int(current_cw * n))
