"""backoff_strategies — 模組化的 backoff 策略套件。

使用方式：

    from backoff_strategies import create, list_strategies
    
    # 看有哪些策略
    print(list_strategies())  # ['beb', 'eied', 'lild']
    
    # 建立策略
    s = create("lild", alpha=1, beta=1)
    
    # 餵給 Station
    station.use_strategy(s)

內建策略：
- BEB   — 802.11 標準 Binary Exponential Backoff
- LILD  — Linear Increase Linear Decrease
- EIED  — Exponential Increase Exponential Decrease

加新策略只要：
1. 寫一個 `your_strategy.py`，class 繼承 BaseStrategy
2. 結尾加 `@register`
3. 從 `__init__.py` import 一次（觸發註冊）

就會自動出現在 list / create / CLI 裡。
"""

# 觸發自動註冊
from .base import BaseStrategy
from .registry import get, list_strategies, register, all_strategies
from .factory import create, describe_all

# 匯入內建策略（觸發 @register）
from . import beb  # noqa: F401
from . import lild  # noqa: F401
from . import eied  # noqa: F401

__all__ = [
    "BaseStrategy",
    "create",
    "describe_all",
    "list_strategies",
    "get",
    "register",
    "all_strategies",
]
