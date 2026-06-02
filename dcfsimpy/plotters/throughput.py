"""plotters.throughput — 畫 Throughput vs N（多策略疊圖）。"""

from __future__ import annotations

from typing import List

import matplotlib

matplotlib.use("Agg")  # 無 X11
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as st

from .base import BasePlotter, StrategyResult
from .registry import register


@register
class ThroughputPlotter(BasePlotter):
    name = "thr"
    title = "Throughput vs Number of Stations"
    ylabel = "Throughput [Mb/s]"

    def plot(self, inputs: List[StrategyResult], output_path: str) -> None:
        plt.figure(figsize=(8, 5))
        for r in inputs:
            grouped = self._group_by_stations(r.df, "THR")
            x = grouped.index.values
            y = grouped["mean"].values
            std = grouped["std"].fillna(0).values
            n = grouped["count"].values
            yerr = std / np.sqrt(n) * st.t.ppf(0.975, np.maximum(n - 1, 1))
            plt.errorbar(x, y, yerr=yerr, marker="o", capsize=3, label=r.name)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.title(self.title)
        plt.grid(alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
