"""backoff_strategies.lild — Linear Increase Linear Decrease。"""

from __future__ import annotations

from typing import Any, Dict

from .base import BaseStrategy
from .registry import register


@register
class LILD(BaseStrategy):
    """Linear Increase Linear Decrease。

    失敗：CW ← min(CW_max, CW + α)
    成功：CW ← max(CW_min, CW − β)

    比 BEB 溫和：碰撞慢慢爬、傳完慢慢降，避免突然回到 CW_min 又碰撞。
    """

    name = "lild"
    description = "Linear Increase Linear Decrease。失敗/成功各線性調整 CW。"
    default_params: Dict[str, Any] = {
        "cw_min": 15,
        "cw_max": 1023,
        "alpha": 1,    # 失敗時 CW 增量
        "beta": 1,     # 成功時 CW 減量
    }

    def initial_cw(self, **ctx) -> int:
        return ctx.get("cw_min", self.cw_min)

    def update_on_failure(self, current_cw: int, **ctx) -> int:
        cw_max = ctx.get("cw_max", self.cw_max)
        alpha = ctx.get("alpha", self.alpha)
        return min(cw_max, current_cw + alpha)

    def update_on_success(self, current_cw: int, **ctx) -> int:
        cw_min = ctx.get("cw_min", self.cw_min)
        beta = ctx.get("beta", self.beta)
        return max(cw_min, current_cw - beta)
