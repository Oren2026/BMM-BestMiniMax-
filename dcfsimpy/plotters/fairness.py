"""plotters.fairness — 畫 Jain's Fairness Index vs N。"""

from __future__ import annotations

from typing import List

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .base import BasePlotter, StrategyResult
from .registry import register


def jains_index(values: np.ndarray) -> float:
    """Jain's Fairness Index：(sum x_i)^2 / (n * sum x_i^2)

    1.0 = 完全公平、1/n = 完全不公平
    """
    n = len(values)
    if n == 0:
        return 0.0
    s = values.sum()
    s2 = (values ** 2).sum()
    return (s ** 2) / (n * s2) if s2 > 0 else 0.0


@register
class FairnessPlotter(BasePlotter):
    name = "fairness"
    title = "Jain's Fairness Index vs Number of Stations"
    ylabel = "Jain's index (1.0 = perfect fairness)"
    ylim = (0, 1.05)

    def plot(self, inputs: List[StrategyResult], output_path: str) -> None:
        plt.figure(figsize=(8, 5))
        for r in inputs:
            df = r.df.copy()
            df["P_COLL"] = df["P_COLL"].astype(float)
            fairness_per_n = []
            for n, group in df.groupby("N_OF_STATIONS"):
                # 用 P_COLL 的「補集」做 per-station 公平性代理
                # 嚴格說應該每 station 算一次，但原 results 沒存 per-station THR
                p_succ = 1.0 - group["P_COLL"].values
                fairness_per_n.append(jains_index(p_succ))
            x = sorted(df["N_OF_STATIONS"].unique())
            plt.plot(x, fairness_per_n, marker="o", label=r.name)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.title(self.title)
        plt.ylim(self.ylim)
        plt.grid(alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
