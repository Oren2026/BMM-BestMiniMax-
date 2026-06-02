# DCF-SimPy（v1.1.0 模組化版）

基於 SimPy 的 IEEE 802.11 DCF（Distributed Coordination Function）模擬工具。

> 原始版本：[ToporPawel/DCF-Simpy](https://github.com/ToporPawel/DCF-Simpy)
> 本 fork 在 v1.1.0 做了模組化改動（見 `docs/backoff-comparison.md`）

---

## v1.1.0 改動重點

從「hardcode BEB」改為「可切換 + 可擴充的策略平台」。

| 改動 | 說明 |
|------|------|
| **`backoff_strategies/` 新套件** | BEB / LILD / EIED 三種 backoff 策略，自動註冊 |
| **`dcfsimpy/plotters/` 新套件** | 結果繪圖模組化（THR / P_COLL / Fairness） |
| **`dcf-simpy-cli.py` 改寫** | 新增 `list-strategies` / `list-plots` / `compare` / `show` 子命令 |
| **`dcfsimpy/DcfFunction.py` 改** | Station 用策略物件取代 hardcode BEB |
| **`tests/test_strategies.py` 新增** | 14 個策略行為單元測試 |
| **`docs/backoff-comparison.md` 新增** | BEB / LILD / EIED 比較報告 + 圖表 |

**完全向後相容**：預設 `backoff_strategy="beb"`，行為跟 v1.0.0 一致。

---

## 安裝

```bash
git clone https://github.com/ToporPawel/DCF-Simpy.git
cd DCF-Simpy
git checkout feature/lild-eied   # 切到本 fork 的模組化 branch
pip install -r requirements.txt
```

## 快速上手

```bash
# 看可用 backoff 策略
python3 dcf-simpy-cli.py list-strategies

# 看可用 plotter
python3 dcf-simpy-cli.py list-plots

# 跑單一策略
python3 dcf-simpy-cli.py single-run --stations-number 5 -t 2 \
  --backoff-strategy lild --lild-alpha 1 --lild-beta 1

# ⭐ 跑多策略比較
python3 dcf-simpy-cli.py compare \
  --strategies beb,lild,eied \
  --stations 1,2,3,4,5,6,7,8,9,10 \
  --runs 5 \
  --plots thr,pcoll,fairness

# 重看既有結果
python3 dcf-simpy-cli.py show results/2026-06-02-07-38-47-compare-beb-lild-eied
```

執行 `python3 dcf-simpy-cli.py --help` 看完整子命令。

## 跑測試

```bash
PYTHONPATH=. python3 -m pytest tests/ -v
```

## 加新策略

1. 寫一個檔案到 `backoff_strategies/your_strategy.py`
2. 繼承 `BaseStrategy`、實作三個方法
3. 結尾加 `@register`
4. 從 `backoff_strategies/__init__.py` 加 `from . import your_strategy`

就會自動出現在 `list-strategies` 與 CLI 選項裡。

## 加新 plotter

類似策略，寫一個檔到 `dcfsimpy/plotters/your_plot.py`、加 `@register`。

## 模組化架構

```
┌──────────────────────────────────────────────┐
│  策略層（backoff_strategies/）                 │
│  BEB / LILD / EIED / 自訂                      │
└──────────────┬───────────────────────────────┘
               ↓
┌──────────────────────────────────────────────┐
│  模擬層（dcfsimpy/）                           │
│  跟策略解耦，產出結果 CSV                       │
└──────────────┬───────────────────────────────┘
               ↓
┌──────────────────────────────────────────────┐
│  呈現層（dcfsimpy/plotters/）                  │
│  THR / P_COLL / Fairness / 自訂                │
└──────────────────────────────────────────────┘
```

---

## 原始版本文件

### Installation

- (Optional) virtual env: `python3 -m venv env && source env/bin/activate`
- Install requirements: `pip install -r requirements.txt`

### Structure

Main program in `dcfsimpy` module. `dcf-simpy-cli.py` is the CLI.

### Reference

波蘭工程師學位論文專案，用 SimPy 模擬 IEEE 802.11 DCF，跟 ns-3 結果比對驗證。
原版詳細說明請見 `Engineering_Thesis.pdf`（668KB）。

## License

跟原版一致。
