#!/usr/bin/env python3
"""dcf-simpy-cli.py — DCF 模擬 CLI（v1.1.0 模組化版）

變更摘要：
- 新增 `list-strategies` / `list-plots` 子命令（自動從 registry 抓）
- 新增 `compare` 子命令：跑多策略並列、產出比較圖
- `single-run` / `run-changing-*` 加 `--backoff-strategy` 與策略參數選項
- 預設仍然是 BEB，行為向後相容
"""

import json
import logging
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import click

import dcfsimpy
from backoff_strategies import describe_all as describe_strategies
from backoff_strategies import list_strategies
from dcfsimpy.plotters import describe_all_plots
from dcfsimpy.plotters import list_plots


# ---------------------------------------------------------------------------
# 頂層群組
# ---------------------------------------------------------------------------

@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("-v", "--verbose", count=True, help="Enable informational/debug logging.")
def cli(verbose: int) -> None:
    if verbose > 1:
        logging.basicConfig(format="%(message)s", level=logging.DEBUG)
    elif verbose > 0:
        logging.basicConfig(format="%(message)s", level=logging.INFO)
    else:
        logging.basicConfig(format="%(message)s", level=logging.WARNING)


# ---------------------------------------------------------------------------
# 列出可用策略 / 圖表
# ---------------------------------------------------------------------------

@cli.command("list-strategies")
def list_strategies_cmd():
    """列出所有可用的 backoff 策略（含參數說明）。"""
    click.echo("可用 backoff 策略：\n")
    click.echo(describe_strategies())


@cli.command("list-plots")
def list_plots_cmd():
    """列出所有可用的 plotter。"""
    click.echo("可用 plotter：\n")
    click.echo(describe_all_plots())


# ---------------------------------------------------------------------------
# 共用策略選項
# ---------------------------------------------------------------------------

def _strategy_options(f):
    """裝飾器：給所有跑模擬的子命令加 --backoff-strategy + 策略參數。"""
    f = click.option(
        "--backoff-strategy", "backoff_strategy", default="beb",
        type=click.Choice(list_strategies()),
        help=f"backoff 策略（可用：{', '.join(list_strategies())}）",
    )(f)
    f = click.option("--lild-alpha", default=1, help="LILD 失敗增量", type=int)(f)
    f = click.option("--lild-beta", default=1, help="LILD 成功減量", type=int)(f)
    f = click.option("--eied-m", default=2.0, help="EIED 失敗倍數", type=float)(f)
    f = click.option("--eied-n", default=0.5, help="EIED 成功倍數", type=float)(f)
    return f


def _build_strategy_params(backoff_strategy, lild_alpha, lild_beta, eied_m, eied_n) -> dict:
    if backoff_strategy == "lild":
        return {"alpha": lild_alpha, "beta": lild_beta}
    if backoff_strategy == "eied":
        return {"m": eied_m, "n": eied_n}
    return {}


# ---------------------------------------------------------------------------
# single-run
# ---------------------------------------------------------------------------

@cli.command()
@_strategy_options
@click.option("--stations-number", type=int, required=True, help="Number of stations.")
@click.option("-t", "--simulation-time", default=100.0, help="Duration in s.")
@click.option("-p", "--payload-size", default=1472, help="Payload size in B.")
@click.option("-m", "--mcs-value", default=7, help="MCS value.")
@click.option("--cw-min", default=15, help="CW min.")
@click.option("--cw-max", default=1023, help="CW max.")
@click.option("--r-limit", default=7, help="Retry limit.")
@click.option("--seed", default=1, help="Random seed.")
@click.option("-s", "--skip-results", is_flag=True, help="Don't save results.")
def single_run(
    seed, stations_number, simulation_time, skip_results,
    cw_min, cw_max, r_limit, payload_size, mcs_value,
    backoff_strategy, lild_alpha, lild_beta, eied_m, eied_n,
):
    """跑單一設定的模擬。"""
    strategy_params = _build_strategy_params(backoff_strategy, lild_alpha, lild_beta, eied_m, eied_n)
    config = dcfsimpy.Config(
        data_size=payload_size, cw_min=cw_min, cw_max=cw_max,
        r_limit=r_limit, mcs=mcs_value,
        backoff_strategy=backoff_strategy, strategy_params=strategy_params,
    )
    results = {}
    backoffs = {key: {stations_number: 0} for key in range(cw_max + 1)}
    dcfsimpy.run_simulation(
        stations_number, seed, simulation_time, skip_results, config, backoffs, results,
    )
    if not skip_results:
        dcfsimpy.save_results(results, backoffs, f"single_run_{backoff_strategy}")


# ---------------------------------------------------------------------------
# run-changing-stations
# ---------------------------------------------------------------------------

@cli.command("run-changing-stations")
@_strategy_options
@click.option("-r", "--runs", default=10)
@click.option("--stations-start", type=int, required=True)
@click.option("--stations-end", type=int, required=True)
@click.option("-t", "--simulation-time", default=100.0)
@click.option("-p", "--payload-size", default=1472)
@click.option("--cw-min", default=15)
@click.option("--cw-max", default=1023)
@click.option("--r-limit", default=7)
@click.option("--seed", default=1)
@click.option("-s", "--skip-results", is_flag=True)
@click.option("--skip-results-show", is_flag=True)
@click.option("-m", "--mcs-value", default=7)
def run_changing_stations(
    runs, seed, stations_start, stations_end, simulation_time, skip_results,
    cw_min, cw_max, r_limit, payload_size, mcs_value, skip_results_show,
    backoff_strategy, lild_alpha, lild_beta, eied_m, eied_n,
):
    """改變 station 數量，觀察 throughput / collision 變化。"""
    strategy_params = _build_strategy_params(backoff_strategy, lild_alpha, lild_beta, eied_m, eied_n)
    config = dcfsimpy.Config(
        data_size=payload_size, cw_min=cw_min, cw_max=cw_max,
        r_limit=r_limit, mcs=mcs_value,
        backoff_strategy=backoff_strategy, strategy_params=strategy_params,
    )
    results = {}
    backoffs = {
        key: {i: 0 for i in range(stations_start, stations_end + 1)}
        for key in range(cw_max + 1)
    }
    for _ in range(runs):
        threads = [
            threading.Thread(
                target=dcfsimpy.run_simulation,
                args=(n, seed * _, simulation_time, skip_results, config, backoffs, results),
            )
            for n in range(stations_start, stations_end + 1)
        ]
        for t in threads: t.start()
        for t in threads: t.join()
    if not skip_results:
        path = dcfsimpy.save_results(results, backoffs, f"run_changing_stations_{backoff_strategy}")
        if not skip_results_show:
            _show_results_for_strategy(path, backoff_strategy)


def _show_results_for_strategy(path: str, strategy: str) -> None:
    """跑完後自動畫圖（沿用舊 CompareResults）。"""
    from dcfsimpy.CompareResults import (
        show_results_changing_stations,
        show_results_changing_mcs,
        show_results_changing_cw,
        show_results_changing_payload,
    )
    if "changing_stations" in path:
        show_results_changing_stations(path)
    elif "changing_mcs" in path:
        show_results_changing_mcs(path)
    elif "changing_cw" in path:
        show_results_changing_cw(path)
    elif "changing_payload" in path:
        show_results_changing_payload(path)


# ---------------------------------------------------------------------------
# run-changing-mcs（簡化版，策略 + mcs sweep）
# ---------------------------------------------------------------------------

@cli.command("run-changing-mcs")
@_strategy_options
@click.option("-r", "--runs", default=10)
@click.option("--stations-number", type=int, required=True)
@click.option("-t", "--simulation-time", default=100.0)
@click.option("-p", "--payload-size", default=1472)
@click.option("--cw-min", default=15)
@click.option("--cw-max", default=1023)
@click.option("--r-limit", default=7)
@click.option("--seed", default=1)
@click.option("-s", "--skip-results", is_flag=True)
def run_changing_mcs(
    runs, seed, stations_number, simulation_time, skip_results,
    cw_min, cw_max, r_limit, payload_size,
    backoff_strategy, lild_alpha, lild_beta, eied_m, eied_n,
):
    """改變 MCS 值，觀察 throughput 變化。"""
    results = {}
    backoffs = {key: {stations_number: 0} for key in range(cw_max + 1)}
    for _ in range(runs):
        threads = []
        for mcs_value in range(0, 8):
            sp = _build_strategy_params(backoff_strategy, lild_alpha, lild_beta, eied_m, eied_n)
            config = dcfsimpy.Config(
                data_size=payload_size, cw_min=cw_min, cw_max=cw_max,
                r_limit=r_limit, mcs=mcs_value,
                backoff_strategy=backoff_strategy, strategy_params=sp,
            )
            threads.append(threading.Thread(
                target=dcfsimpy.run_simulation,
                args=(stations_number, seed * _, simulation_time, skip_results, config, backoffs, results),
            ))
        for t in threads: t.start()
        for t in threads: t.join()
    if not skip_results:
        path = dcfsimpy.save_results(results, backoffs, f"run_changing_mcs_{backoff_strategy}")
        _show_results_for_strategy(path, backoff_strategy)


# ---------------------------------------------------------------------------
# run-changing-cw
# ---------------------------------------------------------------------------

@cli.command("run-changing-cw")
@_strategy_options
@click.option("-r", "--runs", default=10)
@click.option("--stations-start", type=int, required=True)
@click.option("--stations-end", type=int, required=True)
@click.option("--stations-step", default=5, type=int)
@click.option("-t", "--simulation-time", default=100.0)
@click.option("-p", "--payload-size", default=1472)
@click.option("--cw-min-start", default=3)
@click.option("--cw-min-stop", default=1023)
@click.option("--cw-max", default=1023)
@click.option("--r-limit", default=7)
@click.option("--seed", default=1)
@click.option("-s", "--skip-results", is_flag=True)
@click.option("-m", "--mcs-value", default=7)
def run_changing_cw(
    runs, seed, stations_start, stations_end, stations_step, simulation_time, skip_results,
    cw_min_start, cw_min_stop, cw_max, r_limit, payload_size, mcs_value,
    backoff_strategy, lild_alpha, lild_beta, eied_m, eied_n,
):
    """改變 CW_min，觀察飽和吞吐量。"""
    results = {}
    backoffs = {
        key: {i: 0 for i in range(stations_start, stations_end + 1)}
        for key in range(cw_max + 1)
    }
    for cw_min in [
        pow(2, x) - 1
        for x in range(int((cw_min_start + 1) / 2), int((cw_min_stop + 1) / 2))
    ]:
        for _ in range(runs):
            sp = _build_strategy_params(backoff_strategy, lild_alpha, lild_beta, eied_m, eied_n)
            config = dcfsimpy.Config(
                data_size=payload_size, cw_min=cw_min, cw_max=cw_max,
                r_limit=r_limit, mcs=mcs_value,
                backoff_strategy=backoff_strategy, strategy_params=sp,
            )
            threads = [
                threading.Thread(
                    target=dcfsimpy.run_simulation,
                    args=(n, seed * _, simulation_time, skip_results, config, backoffs, results),
                )
                for n in range(stations_start, stations_end + 1, stations_step)
            ]
            for t in threads: t.start()
            for t in threads: t.join()
    if not skip_results:
        path = dcfsimpy.save_results(results, backoffs, f"run_changing_cw_{backoff_strategy}")
        _show_results_for_strategy(path, backoff_strategy)


# ---------------------------------------------------------------------------
# run-changing-payload
# ---------------------------------------------------------------------------

@cli.command("run-changing-payload")
@_strategy_options
@click.option("-r", "--runs", default=10)
@click.option("--stations-number", type=int, required=True)
@click.option("-t", "--simulation-time", default=100.0)
@click.option("--payload-start-size", default=100)
@click.option("--payload-end-size", default=2000)
@click.option("--payload-step-size", default=100)
@click.option("--cw-min", default=15)
@click.option("--cw-max", default=1023)
@click.option("--r-limit", default=7)
@click.option("--seed", default=1)
@click.option("-s", "--skip-results", is_flag=True)
@click.option("-m", "--mcs-value", default=7)
def run_changing_payload(
    runs, seed, stations_number, simulation_time, skip_results,
    cw_min, cw_max, r_limit,
    payload_start_size, payload_end_size, payload_step_size, mcs_value,
    backoff_strategy, lild_alpha, lild_beta, eied_m, eied_n,
):
    """改變 payload 大小，觀察 throughput 變化。"""
    results = {}
    backoffs = {key: {stations_number: 0} for key in range(cw_max + 1)}
    for _ in range(runs):
        threads = []
        for payload_size in range(payload_start_size, payload_end_size + 1, payload_step_size):
            sp = _build_strategy_params(backoff_strategy, lild_alpha, lild_beta, eied_m, eied_n)
            config = dcfsimpy.Config(
                data_size=payload_size, cw_min=cw_min, cw_max=cw_max,
                r_limit=r_limit, mcs=mcs_value,
                backoff_strategy=backoff_strategy, strategy_params=sp,
            )
            threads.append(threading.Thread(
                target=dcfsimpy.run_simulation,
                args=(stations_number, seed * _, simulation_time, skip_results, config, backoffs, results),
            ))
        for t in threads: t.start()
        for t in threads: t.join()
    if not skip_results:
        path = dcfsimpy.save_results(results, backoffs, f"run_changing_payload_{backoff_strategy}")
        _show_results_for_strategy(path, backoff_strategy)


# ---------------------------------------------------------------------------
# compare（⭐ 重點：多策略並列）
# ---------------------------------------------------------------------------

@cli.command("compare")
@click.option("--strategies", "-s", required=True,
              help="策略清單（逗號分隔），例如：beb,lild,eied")
@click.option("--stations", required=True,
              help="station 數清單（逗號分隔），例如：1,2,3,4,5,6,7,8,9,10")
@click.option("-r", "--runs", default=5, help="每組設定的 run 次數")
@click.option("-t", "--simulation-time", default=2.0)
@click.option("-p", "--payload-size", default=1472)
@click.option("--cw-min", default=15)
@click.option("--cw-max", default=1023)
@click.option("--r-limit", default=7)
@click.option("--seed", default=1)
@click.option("--plots", default="thr,pcoll,fairness",
              help="要畫的圖（逗號分隔），例如：thr,pcoll,fairness")
@click.option("-o", "--output-dir", default=None,
              help="結果輸出目錄（預設自動產生 timestamp 目錄）")
def compare(strategies, stations, runs, simulation_time, payload_size,
            cw_min, cw_max, r_limit, seed, plots, output_dir):
    """⭐ 重點：跑多策略並列比較、產出疊圖。

    用法：
        python3 dcf-simpy-cli.py compare \\
          --strategies beb,lild,eied \\
          --stations 1,2,3,4,5,6,7,8,9,10 \\
          --runs 5 --plots thr,pcoll,fairness
    """
    strategy_list = [s.strip() for s in strategies.split(",")]
    station_list = [int(s.strip()) for s in stations.split(",")]
    plot_list = [p.strip() for p in plots.split(",")]

    # 驗證
    for s in strategy_list:
        if s not in list_strategies():
            raise click.BadParameter(f"未知策略：{s}。可用：{list_strategies()}")
    for p in plot_list:
        if p not in list_plots():
            raise click.BadParameter(f"未知 plotter：{p}。可用：{list_plots()}")

    if output_dir is None:
        ts = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        output_dir = f"results/{ts}-compare-{'-'.join(strategy_list)}"
    os.makedirs(output_dir, exist_ok=True)
    for s in strategy_list:
        os.makedirs(f"{output_dir}/{s}", exist_ok=True)
    os.makedirs(f"{output_dir}/comparison", exist_ok=True)

    click.echo(f"== Compare run ==")
    click.echo(f"  strategies: {strategy_list}")
    click.echo(f"  stations:   {station_list}")
    click.echo(f"  runs:       {runs}")
    click.echo(f"  output:     {output_dir}")
    click.echo()

    # 跑每個策略
    for strategy_name in strategy_list:
        click.echo(f"→ 跑 {strategy_name}...")
        results = {}
        backoffs = {
            key: {n: 0 for n in station_list}
            for key in range(cw_max + 1)
        }
        for run_id in range(runs):
            for n in station_list:
                sp = _build_strategy_params(strategy_name, 1, 1, 2.0, 0.5)
                config = dcfsimpy.Config(
                    data_size=payload_size, cw_min=cw_min, cw_max=cw_max,
                    r_limit=r_limit, mcs=7,
                    backoff_strategy=strategy_name, strategy_params=sp,
                )
                dcfsimpy.run_simulation(
                    n, seed * run_id, simulation_time, False, config, backoffs, results,
                )
        # 存到該策略的子目錄
        import pandas as pd
        df = pd.DataFrame(results)
        # P_COLL 在原程式是字串，要轉 float
        if "P_COLL" in df.columns:
            df["P_COLL"] = df["P_COLL"].astype(float)
        df.to_csv(f"{output_dir}/{strategy_name}/results.csv", index=False)
        # mean
        df_mean = df.groupby("N_OF_STATIONS").mean(numeric_only=True)
        if "THR" in df.columns:
            df_mean["THR_STD"] = df.groupby("N_OF_STATIONS")["THR"].std()
        df_mean.to_csv(f"{output_dir}/{strategy_name}/results-mean.csv")
        click.echo(f"  ✓ {strategy_name} 完成（{len(results.get('N_OF_STATIONS', []))} 筆）")

    # 畫並列圖
    click.echo()
    click.echo(f"→ 畫比較圖（{', '.join(plot_list)}）...")
    from dcfsimpy.plotters import get_plotter, StrategyResult
    for plot_name in plot_list:
        PlotterCls = get_plotter(plot_name)
        plotter = PlotterCls()
        inputs = [
            StrategyResult(name, f"{output_dir}/{name}/results.csv")
            for name in strategy_list
        ]
        out = f"{output_dir}/comparison/{plot_name}_comparison.pdf"
        plotter.plot(inputs, out)
        click.echo(f"  ✓ {out}")

    # 自動寫 summary
    _write_compare_summary(output_dir, strategy_list, plot_list)

    click.echo()
    click.echo(f"== 完成 ==")
    click.echo(f"結果：{output_dir}/")
    click.echo(f"摘要：{output_dir}/summary.md")


def _write_compare_summary(output_dir: str, strategies: List[str], plots: List[str]) -> None:
    """自動產出 summary.md（每策略的關鍵數字）。"""
    import pandas as pd
    lines = [f"# 比較結果摘要", ""]
    lines.append(f"- 策略：{', '.join(strategies)}")
    lines.append(f"- 圖表：{', '.join(plots)}")
    lines.append(f"- 輸出目錄：`{output_dir}/`")
    lines.append("")
    lines.append("## 各策略的關鍵指標")
    lines.append("")
    lines.append("| 策略 | 1 station THR | 5 stations THR | 10 stations THR | 平均 P_COLL |")
    lines.append("|------|---------------|----------------|-----------------|-------------|")
    for s in strategies:
        try:
            df = pd.read_csv(f"{output_dir}/{s}/results.csv")
            # P_COLL 是字串，要轉 float
            if "P_COLL" in df.columns:
                df["P_COLL"] = df["P_COLL"].astype(float)
            df_mean = df.groupby("N_OF_STATIONS").mean(numeric_only=True)
            thr_1 = df_mean.loc[1, "THR"] if 1 in df_mean.index else "N/A"
            thr_5 = df_mean.loc[5, "THR"] if 5 in df_mean.index else "N/A"
            thr_10 = df_mean.loc[10, "THR"] if 10 in df_mean.index else "N/A"
            avg_pcoll = df["P_COLL"].mean() if "P_COLL" in df.columns else 0
            t1 = f"{thr_1:.2f}" if isinstance(thr_1, (int, float)) else thr_1
            t5 = f"{thr_5:.2f}" if isinstance(thr_5, (int, float)) else thr_5
            t10 = f"{thr_10:.2f}" if isinstance(thr_10, (int, float)) else thr_10
            lines.append(f"| {s} | {t1} | {t5} | {t10} | {avg_pcoll:.4f} |")
        except Exception as e:
            lines.append(f"| {s} | (error: {e}) | | | |")
    lines.append("")
    lines.append("## 圖表")
    lines.append("")
    for p in plots:
        lines.append(f"- `{p}_comparison.pdf`")
    Path(output_dir, "summary.md").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# show（看既有結果）
# ---------------------------------------------------------------------------

@cli.command("show")
@click.argument("result_dir")
@click.option("--plots", default="thr,pcoll,fairness", help="要畫的圖")
def show_cmd(result_dir, plots):
    """從既有多策略結果目錄畫比較圖。"""
    from dcfsimpy.plotters import get_plotter, StrategyResult
    subdirs = [d.name for d in Path(result_dir).iterdir() if d.is_dir() and not d.name.startswith("comparison")]
    if not subdirs:
        raise click.BadParameter(f"{result_dir} 裡找不到策略子目錄")
    plot_list = [p.strip() for p in plots.split(",")]
    for p in plot_list:
        if p not in list_plots():
            raise click.BadParameter(f"未知 plotter：{p}")
    os.makedirs(f"{result_dir}/comparison", exist_ok=True)
    for plot_name in plot_list:
        PlotterCls = get_plotter(plot_name)
        inputs = [
            StrategyResult(name, f"{result_dir}/{name}/results.csv")
            for name in subdirs
        ]
        out = f"{result_dir}/comparison/{plot_name}_comparison.pdf"
        PlotterCls().plot(inputs, out)
        click.echo(f"  ✓ {out}")


if __name__ == "__main__":
    cli(obj=None)
