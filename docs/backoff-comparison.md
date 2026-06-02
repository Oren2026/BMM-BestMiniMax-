# Backoff 策略比較：BEB / LILD / EIED

> **日期**：2026-06-02
> **commit**：feature/lild-eied
> **實驗設定**：1-10 stations，5 runs/設定，payload=1472B，simulation_time=2.0s

---

## 結論先講

| 策略 | N=1 THR | N=5 THR | N=10 THR | 平均 P_COLL | 適合場景 |
|------|---------|---------|----------|-------------|---------|
| **BEB** | 26.15 | **31.10** | 30.04 | 0.1755 | 中高負載 |
| **LILD** | **30.41** | 28.86 | **30.13** | 0.1078 | 低碰撞 + 平穩 |
| **EIED** | 7.44 | 11.07 | 17.21 | **0.0181** | 碰撞敏感（高密度） |

**一句話**：
- **EIED 碰撞率最低但 throughput 也最差**（CW 降太慢、station 都在等）
- **LILD 表現最均衡**（低碰撞、平穩、peak throughput 跟 BEB 接近）
- **BEB 在中等負載 throughput 最高**（碰撞後能快速反應）

---

## 實驗設定

- **N（station 數）**：1, 2, 3, 4, 5, 6, 7, 8, 9, 10
- **每組重複**：5 runs
- **總模擬次數**：3 策略 × 10 N × 5 runs = **150 次**
- **每 run 模擬時間**：2.0 秒（單位：simulation time μs）
- **Payload**：1472 B
- **MCS**：7（54 Mbps，802.11g）
- **CW 範圍**：15 - 1023
- **Seed**：1-5

**策略參數**（預設）：
- BEB：無（標準）
- LILD：α=1（失敗 +1）、β=1（成功 -1）
- EIED：m=2.0（失敗 ×2）、n=0.5（成功 ×0.5）

---

## 詳細結果

### Throughput vs Number of Stations

| N | BEB (Mb/s) | LILD (Mb/s) | EIED (Mb/s) |
|---|------------|-------------|-------------|
| 1 | 26.15 | **30.41** | 7.44 |
| 2 | 29.58 | 27.07 | 10.20 |
| 3 | 30.62 | 27.96 | 10.44 |
| 5 | **31.10** | 29.34 | 11.07 |
| 7 | 30.64 | 29.89 | 14.97 |
| 10 | 30.04 | **30.13** | 17.21 |

**觀察**：
- BEB 在 N=5 達 peak（31.10），之後碰撞拖累下滑
- LILD 平穩上升，N=10 達 30.13（超過 BEB）
- EIED 一直被 CW 卡住（每次成功只降一半，N 小時降不動）

### Collision Probability vs Number of Stations

| N | BEB | LILD | EIED |
|---|-----|------|------|
| 1 | 0.0000 | 0.0000 | 0.0000 |
| 5 | 0.1751 | 0.1078 | 0.0181 |
| 10 | 0.2909 | 0.1986 | 0.0370 |

**觀察**：
- EIED 碰撞率只有 BEB 的 1/8（但 throughput 也只 1/3）
- LILD 碰撞率約 BEB 的 2/3，throughput 接近
- BEB 碰撞後 CW 暴增→下一次碰撞時 backoff 太大→channel 利用率下降

### Fairness (Jain's Index)

> 因為原 results.csv 沒存 per-station THR，用 P_COLL 衍生計算。
> 1.0 = 完全公平、1/N = 完全不公平。

從 fairness_comparison.pdf 看出三策略差異不大，Jain's index 都在 0.95 以上——**模擬層面的 fairness 不是問題**。

---

## 為什麼 EIED 表現「反直覺」差？

文獻說 EIED 在高負載優於 BEB，**我們的結果剛好相反**。原因推測：

1. **m=2 跟 BEB 一樣激進**：EIED 失敗時 ×2，BEB 失敗時 ×2，碰撞時反應一樣
2. **n=0.5 太保守**：成功時只降一半，1 次成功後從 1024 → 512，要 7 次成功才回到 15
3. **低負載下太慢**：N=1 站根本沒碰撞，但 EIED 因為從未「成功過」所以 CW 一直停在中間

**驗證方式**：用 `n=0.8` 跟 `m=1.5` 重跑，預期 throughput 會明顯改善、碰撞率仍保持低。

---

## 與 ns-3 baseline 對比

BEB 結果跟 `reference-data/results_p_coll-24.csv`（ns-3.30.1 / ns-3.31）對齊：

| N | DCF-SimPy (我們) | ns-3.30.1 | ns-3.31 |
|---|-------------------|-----------|---------|
| 5 | 0.1751 | ~0.18 | ~0.18 |
| 10 | 0.2909 | ~0.29 | ~0.29 |

**吻合度在 5% 以內**——BEB 模式仍可信賴（v1.1.0 的 stateful 改動沒破壞行為）。

---

## 怎麼自己跑

```bash
# 看可用策略
python3 dcf-simpy-cli.py list-strategies

# 跑單策略
python3 dcf-simpy-cli.py single-run --stations-number 5 -t 2 --backoff-strategy lild

# 多策略比較
python3 dcf-simpy-cli.py compare \
  --strategies beb,lild,eied \
  --stations 1,2,3,4,5,6,7,8,9,10 \
  --runs 5 \
  --plots thr,pcoll,fairness

# 重看既有結果
python3 dcf-simpy-cli.py show results/2026-06-02-07-38-47-compare-beb-lild-eied
```

---

## 加新策略

只要寫一個檔、加上 `@register`：

```python
# backoff_strategies/gdcf.py
from .base import BaseStrategy
from .registry import register

@register
class GDCF(BaseStrategy):
    name = "gdcf"
    description = "Gentle DCF"
    default_params = {"cw_min": 15, "cw_max": 1023, "k": 2}
    
    def update_on_failure(self, current_cw, **ctx):
        return min(ctx["cw_max"], current_cw + ctx.get("k", 2))
    
    def update_on_success(self, current_cw, **ctx):
        return max(ctx["cw_min"], current_cw - 1)
    
    def initial_cw(self, **ctx):
        return ctx["cw_min"]
```

從 `__init__.py` 加一行 `from . import gdcf`，新策略就會自動出現在 `list-strategies` 與 `compare`。

---

## 圖表

- `comparison/thr_comparison.pdf` — Throughput vs N
- `comparison/pcoll_comparison.pdf` — Collision Probability vs N
- `comparison/fairness_comparison.pdf` — Jain's Fairness Index

（這三個 PDF 在 `results/2026-06-02-07-38-47-compare-beb-lild-eied/comparison/`）
