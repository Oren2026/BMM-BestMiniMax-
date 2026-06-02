"""plotters.backoff_dist — 畫 backoff 分布（單一策略）。"""

from __future__ import annotations

from typing import List

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .base import BasePlotter, StrategyResult
from .registry import register


@register
class BackoffDistPlotter(BasePlotter):
    name = "backoff"
    title = "Backoff Distribution"
    ylabel = "Frequency"
    xlabel = "Backoff value"

    def plot(self, inputs: List[StrategyResult], output_path: str) -> None:
        # 這個 plotter 一次處理一個策略（取 backoffs.csv）
        if not inputs:
            return
        r = inputs[0]
        # 從檔名推 backoffs.csv：results.csv 在同目錄
        csv_path = r.df._path if hasattr(r.df, "_path") else None
        # 簡化：從 StrategyResult 拿不到 backoffs 路徑就先跳過
        # 真實使用會從 input 結構拿
        plt.figure(figsize=(10, 4))
        plt.title(f"{self.title} — {r.name}")
        plt.text(0.5, 0.5,
                 "Backoff distribution 需要 backoffs.csv（透過 run-sim CLI 自動產生）",
                 ha="center", va="center", transform=plt.gca().transAxes)
        plt.savefig(output_path)
        plt.close()
