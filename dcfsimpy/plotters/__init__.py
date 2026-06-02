"""plotters — 結果繪圖模組。

使用方式：
    from dcfsimpy.plotters import list_plots, get_plotter

    print(list_plots())  # ['backoff', 'fairness', 'pcoll', 'thr']

    PlotterCls = get_plotter('thr')
    plotter = PlotterCls()
    plotter.plot([StrategyResult('BEB', 'results/beb.csv'),
                  StrategyResult('LILD', 'results/lild.csv')],
                 'output.pdf')

加新 plotter 只要：
1. 寫一個新檔，class 繼承 BasePlotter
2. 結尾加 @register（從 .registry import）
3. 從 __init__.py import 一次（觸發註冊）
"""

from .base import BasePlotter, StrategyResult
from .registry import register, get as get_plotter, list_plots, describe_all as describe_all_plots

# 觸發自動註冊
from . import throughput  # noqa: F401
from . import collision  # noqa: F401
from . import fairness  # noqa: F401
from . import backoff_dist  # noqa: F401

__all__ = [
    "BasePlotter",
    "StrategyResult",
    "register",
    "get_plotter",
    "list_plots",
    "describe_all_plots",
]
