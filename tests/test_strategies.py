"""test_strategies.py — 策略行為的單元測試。"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backoff_strategies import create, list_strategies


# ---------------------------------------------------------------------------
# 註冊
# ---------------------------------------------------------------------------

def test_strategies_registered():
    names = list_strategies()
    assert "beb" in names
    assert "lild" in names
    assert "eied" in names


# ---------------------------------------------------------------------------
# BEB
# ---------------------------------------------------------------------------

def test_beb_initial_cw():
    s = create("beb")
    assert s.initial_cw(cw_min=15, cw_max=1023) == 15


def test_beb_failure_doubles_cw():
    s = create("beb")
    assert s.update_on_failure(15, cw_min=15, cw_max=1023) == 30
    assert s.update_on_failure(30, cw_min=15, cw_max=1023) == 60
    assert s.update_on_failure(480, cw_min=15, cw_max=1023) == 960


def test_beb_failure_capped_at_cw_max():
    s = create("beb")
    # 1000 * 2 = 2000 > 1023 → 應被 cap 在 1023
    assert s.update_on_failure(1000, cw_min=15, cw_max=1023) == 1023


def test_beb_success_resets_to_cw_min():
    s = create("beb")
    assert s.update_on_success(1023, cw_min=15, cw_max=1023) == 15
    assert s.update_on_success(500, cw_min=15, cw_max=1023) == 15


# ---------------------------------------------------------------------------
# LILD
# ---------------------------------------------------------------------------

def test_lild_initial_cw():
    s = create("lild")
    assert s.initial_cw(cw_min=15, cw_max=1023) == 15


def test_lild_failure_increments_by_alpha():
    s = create("lild", alpha=2)
    assert s.update_on_failure(15, cw_min=15, cw_max=1023) == 17
    assert s.update_on_failure(17, cw_min=15, cw_max=1023) == 19


def test_lild_success_decrements_by_beta():
    s = create("lild", beta=3)
    assert s.update_on_success(100, cw_min=15, cw_max=1023) == 97
    assert s.update_on_success(17, cw_min=15, cw_max=1023) == 15  # floor
    assert s.update_on_success(15, cw_min=15, cw_max=1023) == 15  # can't go below


def test_lild_failure_capped_at_cw_max():
    s = create("lild", alpha=1)
    # 1023 + 1 → 1024，應被 cap 在 1023
    assert s.update_on_failure(1023, cw_min=15, cw_max=1023) == 1023


# ---------------------------------------------------------------------------
# EIED
# ---------------------------------------------------------------------------

def test_eied_initial_cw():
    s = create("eied")
    assert s.initial_cw(cw_min=15, cw_max=1023) == 15


def test_eied_failure_multiplies_by_m():
    s = create("eied", m=2.0)
    assert s.update_on_failure(15, cw_min=15, cw_max=1023) == 30
    assert s.update_on_failure(30, cw_min=15, cw_max=1023) == 60


def test_eied_success_multiplies_by_n():
    s = create("eied", n=0.5)
    assert s.update_on_success(1023, cw_min=15, cw_max=1023) == 511
    assert s.update_on_success(20, cw_min=15, cw_max=1023) == 15  # floor


def test_eied_failure_capped_at_cw_max():
    s = create("eied", m=10.0)
    assert s.update_on_failure(200, cw_min=15, cw_max=1023) == 1023


# ---------------------------------------------------------------------------
# 比較（用同樣條件看三策略差異）
# ---------------------------------------------------------------------------

def test_three_strategies_diverge():
    """同樣 5 次失敗後，三策略的 CW 應該都不一樣。"""
    cw_min, cw_max = 15, 1023
    cw = cw_min
    for _ in range(5):
        cw = create("beb").update_on_failure(cw, cw_min=cw_min, cw_max=cw_max)
    beb_after_5 = cw

    cw = cw_min
    for _ in range(5):
        cw = create("lild").update_on_failure(cw, cw_min=cw_min, cw_max=cw_max)
    lild_after_5 = cw

    cw = cw_min
    for _ in range(5):
        cw = create("eied").update_on_failure(cw, cw_min=cw_min, cw_max=cw_max)
    eied_after_5 = cw

    # 5 次失敗後：BEB = 480, LILD = 20, EIED = 480
    assert beb_after_5 == 480
    assert lild_after_5 == 20
    assert eied_after_5 == 480
    # BEB 跟 EIED 失敗時都指數增、會相等
    assert beb_after_5 == eied_after_5
    # LILD 線性增，會比指數增慢很多
    assert lild_after_5 < beb_after_5
