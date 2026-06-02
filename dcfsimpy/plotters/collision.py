"""plotters.collision — 畫 Collision Probability vs N。"""

from __future__ import annotations

from typing import List

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .base import BasePlotter, StrategyResult
from .registry import register


@register
class CollisionPlotter(BasePlotter):
    name = "pcoll"
    title = "Collision Probability vs Number of Stations"
    ylabel = "Collision probability"

    def plot(self, inputs: List[StrategyResult], output_path: str) -> None:
        plt.figure(figsize=(8, 5))
        for r in inputs:
            # P_COLL 在原程式是字串，要轉 float
            df = r.df.copy()
            df["P_COLL"] = df["P_COLL"].astype(float)
            grouped = self._group_by_stations(df, "P_COLL")
            x = grouped.index.values
            y = grouped["mean"].values
            plt.plot(x, y, marker="o", label=r.name)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.title(self.title)
        plt.grid(alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
