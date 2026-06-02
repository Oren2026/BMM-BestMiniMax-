"""plotters.base — Plotter 抽象基底。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Tuple

import pandas as pd


class StrategyResult:
    """單一策略的結果包裝：給 plotters 用。"""

    def __init__(self, name: str, csv_path: str):
        self.name = name
        self.df = pd.read_csv(csv_path)


class BasePlotter(ABC):
    """所有 plotter 的統一介面。

    inputs 是一組 StrategyResult（每個代表一個策略）。
    output_path 是 PDF 檔案路徑。
    """

    name: str = "base"
    title: str = ""
    ylabel: str = ""
    xlabel: str = "Number of stations"

    @abstractmethod
    def plot(self, inputs: List[StrategyResult], output_path: str) -> None:
        ...

    def _group_by_stations(self, df: pd.DataFrame, value_col: str):
        """把多次 run 的結果按 N 聚合（mean + std）。"""
        grouped = df.groupby("N_OF_STATIONS")[value_col].agg(["mean", "std", "count"])
        grouped["sem"] = grouped["std"] / grouped["count"] ** 0.5
        return grouped
