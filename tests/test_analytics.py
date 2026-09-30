"""
Regression tests for harness/analytics.py — the maths every factor is judged by.

Run `pytest tests/` after ANY harness change. A harness bug does not produce
an obviously wrong number; it produces a plausible one, and every registry
row compared against it inherits the error silently.
"""

import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from harness.analytics import (  # noqa: E402
    RESULT_BEGIN, RESULT_END, SERIES_KEYS, align_arms, assign_composite_decile,
    blend_ranks, check_stage1, check_stage2, compute_bucket_diagnostics,
    compute_factor_ranks, compute_ic, compute_ic_decay, compute_turnover,
    cut_deciles, emit_result_block, ic_halves, ls_month_floor, net_of_cost, normal_scores,
    nw_tstat, ols_nw, paired_delta, parse_result_block, parse_result_blocks,
    print_bucket_diagnostics, print_summary, rank_one_factor, residual_ic_series,
    standalone_ic_series,
    spanning_test, stage1_checks, stage2_checks, survivorship_check, tier_scalars,
    validate_results,
)

CONFIG = {"dates": {"out_of_sample_start": "2026-01-01"}, "rebalance": {"min_months": 120}}
META = [{"name": "A", "col": "f_a", "ascending": True, "winsorize": True, "weight": 1.0},
        {"name": "B", "col": "f_b", "ascending": False, "winsorize": True, "weight": 1.0}]
WEIGHTS = {"A": 0.5, "B": 0.5}


def _panel(n_dates=36, n_names=120, seed=0, ic=0.3, regions=True):
    """Synthetic audit frame with a KNOWN signal->return relationship."""
    rng = np.random.default_rng(seed)
    rows = []
    tiers = ["MEGA", "MID", "SMALL"]
    for d in pd.date_range("2003-01-31", periods=n_dates, freq="ME"):
        score = rng.random(n_names)
        ret = ic * (score - 0.5) * 0.2 + rng.normal(0, 0.05, n_names)
        for i in range(n_names):
            rows.append({"ID": f"S{i}", "DATE": d, "COMPOSITE_SCORE": score[i], "monthly_ret": ret[i],
                         "region": "US", "liq_tier": tiers[i % 3] if regions else "MEGA"})
    df = pd.DataFrame(rows)
    df["DECILE"] = df.groupby("DATE")["COMPOSITE_SCORE"].transform(
        lambda x: pd.qcut(x, 10, labels=False, duplicates="drop") + 1)
    return df


def _monthly_tables(audit):
    g = audit.dropna(subset=["DECILE", "monthly_ret"]).groupby(["DATE", "DECILE"])["monthly_ret"]
    ret = g.mean().unstack("DECILE").sort_index()
    ret.columns = [f"D{int(c)}" for c in ret.columns]
    cnt = g.count().unstack("DECILE").sort_index()
    cnt.columns = [f"N_D{int(c)}" for c in cnt.columns]
    ret["LS"] = ret["D10"] - ret["D1"]
    return ret, cnt


# =============================================================================
# Statistics helpers
# =============================================================================

def test_nw_tstat_with_zero_lags_is_the_plain_tstat():
    x = pd.Series(np.random.default_rng(1).normal(0.1, 1, 200))
    plain = x.mean() / (x.std(ddof=0) / np.sqrt(len(x)))
    assert nw_tstat(x, lags=0) == pytest.approx(plain, rel=1e-9)


def test_nw_tstat_shrinks_under_positive_autocorrelation():
    rng = np.random.default_rng(2)
    e = rng.normal(size=400)
    ar = np.zeros(400)
    for i in range(1, 400):
        ar[i] = 0.6 * ar[i - 1] + e[i]
    ar = ar + 0.3
    assert abs(nw_tstat(ar, lags=6)) < abs(nw_tstat(ar, lags=0))


def test_nw_tstat_nan_on_degenerate_input():
    assert np.isnan(nw_tstat([1.0]))
    assert np.isnan(nw_tstat([0.5, 0.5, 0.5]))


def test_ols_nw_recovers_known_coefficients():
    rng = np.random.default_rng(3)
    x = rng.normal(size=300)
    y = 0.02 + 0.8 * x + rng.normal(0, 0.1, 300)
    r = ols_nw(y, np.column_stack([np.ones(300), x]))
    assert r["coef"][0] == pytest.approx(0.02, abs=0.02)
    assert r["coef"][1] == pytest.approx(0.8, abs=0.05)
    assert r["tstat"][1] > 20 and 0.9 < r["r2"] < 1.0


def test_normal_scores_are_symmetric_and_finite():
    z = normal_scores(pd.Series(np.arange(1, 101) / 100.0))
    assert np.isfinite(z).all() and abs(z.mean()) < 1e-9 and z.iloc[-1] == pytest.approx(-z.iloc[0])


def test_ic_halves_split_by_month_count():
    ic = pd.Series([0.1] * 10 + [-0.1] * 10)
    h1, h2, n1, n2 = ic_halves(ic)
    assert (h1, h2, n1, n2) == (pytest.approx(0.1), pytest.approx(-0.1), 10, 10)


def test_net_of_cost_charges_both_sides_of_both_books():
    n = net_of_cost(10.0, 10.0, 25.0, 25.0, 20)
    # 2 * 20bp * (0.25 + 0.25) = 0.20% per month = 2.4% per year
    assert n["ls_cost_drag_ann_pct"] == pytest.approx(2.4)
    assert n["ls_net_ann_return_pct"] == pytest.approx(7.6)
    assert n["ls_net_sharpe"] == pytest.approx(0.76)


def test_net_of_cost_zero_cost_is_gross():
    assert net_of_cost(10.0, 10.0, 30.0, 30.0, 0)["ls_net_ann_return_pct"] == pytest.approx(10.0)


# =============================================================================
# Ranking, blending, deciles
# =============================================================================

def test_ascending_true_puts_high_values_on_top():
    r = rank_one_factor(pd.DataFrame({"x": range(50)}), "x", ascending=True, winsorize=False)
    assert r.iloc[-1] > r.iloc[0]


def test_ascending_false_inverts():
    r = rank_one_factor(pd.DataFrame({"x": range(50)}), "x", ascending=False, winsorize=False)
    assert r.iloc[-1] < r.iloc[0]


def test_rank_returns_nan_for_thin_cross_sections():
    assert rank_one_factor(pd.DataFrame({"x": range(5)}), "x", min_obs=10).isna().all()


def test_rank_of_missing_column_is_nan_not_an_error():
    assert rank_one_factor(pd.DataFrame({"y": [1, 2]}), "x").isna().all()


def test_winsorize_does_not_corrupt_ordering():
    df = pd.DataFrame({"x": list(range(99)) + [10_000_000]})
    assert (rank_one_factor(df, "x", winsorize=True).rank()
            == rank_one_factor(df, "x", winsorize=False).rank()).all()


def test_compute_factor_ranks_orients_each_leg():
    df = pd.DataFrame({"f_a": np.arange(50.0), "f_b": np.arange(50.0)})
    ranks = compute_factor_ranks(df, META)
    assert ranks["A"].corr(ranks["B"]) == pytest.approx(-1.0)


def test_blend_renormalises_over_available_factors():
    out = blend_ranks(pd.DataFrame({"A": [0.8, 0.8], "B": [0.2, np.nan]}), {"A": 0.5, "B": 0.5})
    assert out.iloc[0] == pytest.approx(0.5) and out.iloc[1] == pytest.approx(0.8)


def test_blend_never_fills_missing_with_neutral_half():
    assert blend_ranks(pd.DataFrame({"A": [0.95], "B": [np.nan]}), {"A": 1.0, "B": 1.0}).iloc[0] == pytest.approx(0.95)


def test_blend_all_missing_gives_nan():
    assert blend_ranks(pd.DataFrame({"A": [np.nan], "B": [np.nan]}), {"A": 1.0, "B": 1.0}).isna().all()


def test_blend_ignores_zero_weighted_retired_factors():
    assert blend_ranks(pd.DataFrame({"A": [0.9], "B": [0.1]}), {"A": 1.0, "B": 0.0}).iloc[0] == pytest.approx(0.9)


def test_blend_respects_unequal_weights():
    assert blend_ranks(pd.DataFrame({"A": [1.0], "B": [0.0]}), {"A": 3.0, "B": 1.0}).iloc[0] == pytest.approx(0.75)


def test_deciles_are_balanced_and_span_one_to_ten():
    df = pd.DataFrame({"f_a": np.random.default_rng(1).normal(size=1000)})
    df["f_b"] = -df["f_a"]
    out = assign_composite_decile(df, META, WEIGHTS)
    counts = out["DECILE"].value_counts()
    assert set(out["DECILE"].dropna().unique()) == set(range(1, 11))
    assert counts.max() - counts.min() <= 1


def test_deciles_survive_heavy_ties():
    df = pd.DataFrame({"f_a": [0.0] * 180 + list(range(20))})
    df["f_b"] = 0.0
    assert assign_composite_decile(df, META, WEIGHTS)["DECILE"].notna().any()


def test_thin_month_gets_no_deciles_rather_than_a_bad_cut():
    df = pd.DataFrame({"f_a": [1.0, 2.0, 3.0], "f_b": [1.0, 2.0, 3.0]})
    assert assign_composite_decile(df, META, WEIGHTS)["DECILE"].isna().all()


def test_cut_deciles_keeps_na_where_score_is_na():
    s = pd.Series(list(np.arange(100.0)) + [np.nan])
    d = cut_deciles(s)
    assert pd.isna(d.iloc[-1]) and d.dropna().min() == 1 and d.dropna().max() == 10


# =============================================================================
# IC / decay / turnover
# =============================================================================

def test_ic_recovers_a_known_positive_relationship():
    ic = compute_ic(_panel(ic=0.6, seed=7))
    assert len(ic) == 36 and ic["IC"].mean() > 0.05


def test_ic_of_pure_noise_is_near_zero():
    assert abs(compute_ic(_panel(ic=0.0, seed=3, n_dates=60))["IC"].mean()) < 0.05


def test_ic_is_computed_on_the_continuous_score_not_the_decile():
    """Convention: Spearman of the continuous score. Locking it down so a
    switch back to decile IC cannot silently move every registry number."""
    from scipy.stats import spearmanr
    audit = _panel(ic=0.5, seed=11)
    ic = compute_ic(audit)
    manual = [spearmanr(g["COMPOSITE_SCORE"], g["monthly_ret"])[0] for _, g in audit.groupby("DATE")]
    assert ic["IC"].mean() == pytest.approx(np.mean(manual))
    dec = [spearmanr(g["DECILE"], g["monthly_ret"])[0] for _, g in audit.groupby("DATE")]
    assert ic["IC"].mean() != pytest.approx(np.mean(dec), abs=1e-9)


def test_ic_skips_months_below_the_minimum():
    audit = _panel(n_dates=2, n_names=120, seed=1)
    thin = audit[audit["DATE"] == audit["DATE"].min()].head(5)
    fat = audit[audit["DATE"] == audit["DATE"].max()]
    assert len(compute_ic(pd.concat([thin, fat]))) == 1


def test_ic_empty_input_returns_empty_frame_not_a_crash():
    assert len(compute_ic(pd.DataFrame(columns=["DATE", "COMPOSITE_SCORE", "monthly_ret"]))) == 0


def test_ic_decay_h0_equals_headline_and_iid_signal_decays_to_zero():
    audit = _panel(ic=0.6, seed=5, n_dates=40)
    dec = compute_ic_decay(audit, horizons=(0, 1, 3))
    assert dec[0] == pytest.approx(compute_ic(audit)["IC"].mean(), abs=1e-9)
    assert abs(dec[1]) < 0.05 and abs(dec[3]) < 0.05     # scores are redrawn each month


def test_turnover_is_zero_for_a_static_portfolio():
    dates = pd.date_range("2020-01-31", periods=6, freq="ME")
    rows = [{"ID": f"S{i}", "DATE": d, "DECILE": 10 if i < 5 else 1} for d in dates for i in range(10)]
    t = compute_turnover(pd.DataFrame(rows))
    assert t["d10"] == pytest.approx(0.0) and t["d1"] == pytest.approx(0.0)


def test_turnover_is_total_when_the_book_fully_rotates():
    dates = pd.date_range("2020-01-31", periods=2, freq="ME")
    rows = ([{"ID": f"A{i}", "DATE": dates[0], "DECILE": 10} for i in range(5)]
            + [{"ID": f"B{i}", "DATE": dates[1], "DECILE": 10} for i in range(5)])
    assert compute_turnover(pd.DataFrame(rows))["d10"] == pytest.approx(100.0)


# =============================================================================
# Marginal-information tests
# =============================================================================

def _two_leg_panel(n_dates=60, n_names=200, seed=0, cand_is_copy=False, cand_has_info=True):
    """Base leg A drives returns; candidate C either duplicates A, adds its own
    information, or is noise."""
    rng = np.random.default_rng(seed)
    rows = []
    for d in pd.date_range("2003-01-31", periods=n_dates, freq="ME"):
        a = rng.normal(size=n_names)
        c_own = rng.normal(size=n_names)
        c = a + 0.05 * rng.normal(size=n_names) if cand_is_copy else c_own
        ret = 0.02 * a + (0.02 * c_own if (cand_has_info and not cand_is_copy) else 0) + rng.normal(0, 0.05, n_names)
        for i in range(n_names):
            rows.append({"ID": f"S{i}", "DATE": d, "f_a": a[i], "f_c": c[i], "monthly_ret": ret[i]})
    return pd.DataFrame(rows)


BASE_META = [{"name": "A", "col": "f_a", "ascending": True, "winsorize": True, "weight": 1.0}]
CAND_META = {"name": "C", "col": "f_c", "ascending": True, "winsorize": True, "weight": 1.0}


def test_residual_ic_is_large_for_genuinely_new_information():
    r = residual_ic_series(_two_leg_panel(cand_has_info=True), BASE_META, CAND_META)
    assert len(r) == 60 and r["IC"].mean() > 0.05 and nw_tstat(r["IC"]) > 3


def test_residual_ic_is_near_zero_for_a_copy_of_an_existing_leg():
    """The case a correlation bar would be for: a near-duplicate with a fine
    standalone IC carries no residual information."""
    audit = _two_leg_panel(cand_is_copy=True, n_names=600)
    solo = compute_ic(audit.assign(COMPOSITE_SCORE=audit["f_c"]))["IC"].mean()
    r = residual_ic_series(audit, BASE_META, CAND_META)
    assert solo > 0.05
    assert abs(r["IC"].mean()) < 0.1 * solo


def test_standalone_ic_matches_compute_ic_on_the_oriented_score():
    """HD-001: the denominator of resid_ic_share is the candidate's own IC on
    the rung's frame, not the WITH-composite IC. On a panel where the
    candidate carries information, the standalone IC is positive and equals
    compute_ic of the oriented column; a copy of a leg keeps its full
    standalone IC while its residual share collapses."""
    audit = _two_leg_panel(cand_has_info=True)
    solo = standalone_ic_series(audit, CAND_META)
    sign = 1.0 if CAND_META["ascending"] else -1.0
    ref = compute_ic(audit.assign(COMPOSITE_SCORE=sign * audit["f_c"]))
    assert len(solo) == len(ref) == 60
    # exact up to the ties winsorising introduces in the tails
    assert np.allclose(solo["IC"].values, ref["IC"].values, atol=2e-3)
    exact = standalone_ic_series(audit, {**CAND_META, "winsorize": False})
    assert np.allclose(exact["IC"].values, ref["IC"].values, atol=1e-9)
    assert solo["IC"].mean() > 0.05
    copy = _two_leg_panel(cand_is_copy=True, n_names=600)
    share = residual_ic_series(copy, BASE_META, CAND_META)["IC"].mean() / \
        standalone_ic_series(copy, CAND_META)["IC"].mean()
    assert abs(share) < 0.1


def test_solo_ic_field_does_not_collide_with_the_with_arm_prefix():
    """HD-002: the rung writes the WITH-arm stats under a cand_ prefix, so the
    standalone IC that feeds resid_ic_share must live under its own key."""
    src = (Path(__file__).resolve().parents[1] / "harness" / "run_test.py").read_text()
    assert '"solo_ic_mean": solo_ic_mean' in src
    assert '"cand_ic_mean":' not in src


def test_residual_ic_is_near_zero_for_noise():
    r = residual_ic_series(_two_leg_panel(cand_has_info=False), BASE_META, CAND_META)
    assert abs(r["IC"].mean()) < 0.03 and abs(nw_tstat(r["IC"])) < 2.5


def test_spanning_alpha_is_positive_for_an_independent_return_stream():
    rng = np.random.default_rng(4)
    idx = pd.date_range("2000-01-31", periods=240, freq="ME")
    base = pd.Series(rng.normal(0.01, 0.04, 240), index=idx)
    cand = pd.Series(rng.normal(0.008, 0.03, 240), index=idx)
    s = spanning_test(cand, base)
    assert s["spanning_alpha_tstat_nw"] > 2 and abs(s["spanning_beta"]) < 0.3 and s["spanning_r2"] < 0.1


def test_spanning_alpha_is_zero_for_a_levered_copy():
    rng = np.random.default_rng(5)
    idx = pd.date_range("2000-01-31", periods=240, freq="ME")
    base = pd.Series(rng.normal(0.01, 0.04, 240), index=idx)
    cand = 1.5 * base + rng.normal(0, 0.002, 240)
    s = spanning_test(cand, base)
    assert abs(s["spanning_alpha_tstat_nw"]) < 2 and s["spanning_beta"] == pytest.approx(1.5, abs=0.05)
    assert s["spanning_r2"] > 0.95 and s["corr_to_composite"] > 0.97


def test_spanning_uses_only_common_months():
    idx = pd.date_range("2000-01-31", periods=30, freq="ME")
    s = spanning_test(pd.Series(0.01, index=idx[:20]), pd.Series(0.01, index=idx[10:]))
    assert s["spanning_n"] == 10


def test_paired_delta_is_on_the_intersection():
    idx = pd.date_range("2000-01-31", periods=24, freq="ME")
    b = pd.Series(0.01, index=idx)
    c = pd.Series(0.02, index=idx[:12])
    m, t, n = paired_delta(b, c)
    assert n == 12 and m == pytest.approx(0.01)


def test_align_arms_reports_aligned_and_unmatched_months():
    idx = pd.date_range("2000-01-31", periods=24, freq="ME")
    rng = np.random.default_rng(6)
    base = {"ic_series": pd.Series(rng.normal(0.02, 0.1, 24), index=idx),
            "ls_series": pd.Series(rng.normal(0.01, 0.04, 24), index=idx)}
    cand = {"ic_series": base["ic_series"] + 0.01 + rng.normal(0, 0.001, 24),
            "ls_series": base["ls_series"] + 0.002}
    a = align_arms(base, cand)
    assert a["arm_months_aligned"] == "True" and a["arm_n_common_ic"] == 24
    assert a["paired_delta_ic_mean"] == pytest.approx(0.01, abs=0.001) and a["paired_delta_ic_tstat"] > 10
    cand2 = {"ic_series": cand["ic_series"].iloc[:-1], "ls_series": cand["ls_series"]}
    buf = io.StringIO()
    with redirect_stdout(buf):
        a2 = align_arms(base, cand2)
    assert a2["arm_months_aligned"] == "False" and a2["arm_n_common_ic"] == 23
    assert "ARM MONTH MISMATCH" in buf.getvalue()


# =============================================================================
# The report — the output contract
# =============================================================================

def _run_report(audit=None):
    audit = _panel(ic=0.5, seed=5) if audit is None else audit
    ret, cnt = _monthly_tables(audit)
    buf = io.StringIO()
    with redirect_stdout(buf):
        stats = print_summary("US UNIVERSE  —  test", ret, cnt, compute_ic(audit), audit)
        print_bucket_diagnostics(compute_bucket_diagnostics(audit))
        survivorship_check(audit)
    return buf.getvalue(), stats


def test_report_prints_every_section_in_order():
    out, _ = _run_report()
    expected = ["US UNIVERSE", "D1 = worst | D10 = best | LS = D10 − D1", "--- IC Summary",
                "Mean IC   :", "t-stat    :", "Newey-West", "Halves    :", "Decay     :",
                "--- LS Portfolio Economics", "Sharpe Ratio    :", "Max Drawdown    :",
                "Avg D1  Turnover:", "--- Annual IC ---", "--- Annual LS Return (%) ---",
                "IC + LS economics by (region × tier)", "Names appearing in year-Y but ABSENT in"]
    pos = -1
    for marker in expected:
        found = out.find(marker, pos + 1)
        assert found > pos, f"missing or out of order: {marker!r}"
        pos = found


def test_returned_stats_match_the_printed_numbers():
    out, stats = _run_report()
    assert f"Mean IC   : {stats['ic_mean']:.4f}" in out
    assert f"Sharpe Ratio    : {stats['ls_sharpe']:.4f}" in out
    assert f"Max Drawdown    : {stats['ls_maxdd_pct']:.2f}%" in out
    assert f"Months    : {stats['n_months']}" in out
    for k in ("ic_tstat_nw", "ic_half_min", "ls_ann_return_pct", "turnover_d10_pct",
              "ic_decay_h1", "decile_avg_ret_pct"):
        assert k in stats


def test_report_charges_no_cost_anywhere():
    out, stats = _run_report()
    assert "After cost" not in out
    assert not any(k.startswith("ls_net") or "cost" in k for k in stats)


def test_report_returns_none_when_there_is_no_long_short_series():
    ret = pd.DataFrame({"D1": [0.01], "D10": [0.02], "LS": [np.nan]}, index=pd.to_datetime(["2020-01-31"]))
    cnt = pd.DataFrame({"N_D1": [10], "N_D10": [10]}, index=pd.to_datetime(["2020-01-31"]))
    buf = io.StringIO()
    with redirect_stdout(buf):
        stats = print_summary("t", ret, cnt, pd.DataFrame({"IC": [0.1]}), pd.DataFrame(), decay=False)
    assert stats is None and "insufficient LS data" in buf.getvalue()


def test_report_counts_months_with_no_long_short():
    idx = pd.to_datetime([f"2020-{m:02d}-28" for m in range(1, 13)])
    ret = pd.DataFrame({"D1": [0.00] * 12, "D10": [0.01] * 12, "LS": [0.01, np.nan] * 6}, index=idx)
    cnt = pd.DataFrame({"N_D1": [50] * 12, "N_D10": [50] * 12}, index=idx)
    audit = pd.DataFrame({"ID": ["A", "B"] * 12, "DATE": np.repeat(idx, 2), "DECILE": [1, 10] * 12,
                          "COMPOSITE_SCORE": [0.1, 0.9] * 12, "monthly_ret": [0.0, 0.01] * 12})
    buf = io.StringIO()
    with redirect_stdout(buf):
        stats = print_summary("t", ret, cnt, pd.DataFrame({"IC": [0.1] * 12}, index=idx), audit, decay=False)
    assert stats["ls_n_months"] == 6 and stats["ls_n_months_missing"] == 6
    assert "WARNING" in buf.getvalue()


def test_bucket_table_has_an_all_all_row_and_tier_scalars():
    b = compute_bucket_diagnostics(_panel(ic=0.5, seed=4))
    assert ("ALL", "ALL") in list(zip(b["region"].astype(str), b["tier"].astype(str)))
    ts = tier_scalars(b)
    assert {"tier_MEGA_ic_mean", "tier_MID_ls_sharpe", "tier_SMALL_avg_n"} <= set(ts)


def test_bucket_skips_cells_below_the_minimum_cross_section():
    b = compute_bucket_diagnostics(_panel(n_names=12, seed=8))
    assert b.empty or set(zip(b["region"].astype(str), b["tier"].astype(str))) == {("ALL", "ALL")}


def test_survivorship_reports_high_attrition_when_names_actually_leave():
    rows = [{"ID": f"S{i}", "DATE": pd.Timestamp(f"{y}-06-30"), "region": "US"}
            for y, ids in [(2003, range(100)), (2025, range(50, 150))] for i in ids]
    buf = io.StringIO()
    with redirect_stdout(buf):
        pct = survivorship_check(pd.DataFrame(rows))
    assert pct == pytest.approx(50.0)


def test_survivorship_reports_zero_when_the_universe_is_not_point_in_time():
    rows = [{"ID": f"S{i}", "DATE": pd.Timestamp(f"{y}-06-30"), "region": "US"}
            for y in (2003, 2025) for i in range(100)]
    buf = io.StringIO()
    with redirect_stdout(buf):
        assert survivorship_check(pd.DataFrame(rows)) == pytest.approx(0.0)


# =============================================================================
# Result block round trip
# =============================================================================

def test_block_round_trips_and_skips_series():
    fields = {"stage": "1", "factor": "X", "ic_mean": 0.0123456789, "ls_series": pd.Series([1, 2]),
              "harness_sha": "123456789012", "nanval": float("nan"), "decile_avg_ret_pct": "0.1,0.2"}
    block = emit_result_block(fields)
    assert "ls_series" not in block
    p = parse_result_block(block)
    assert p["stage"] == "1" and p["harness_sha"] == "123456789012" and p["nanval"] is None
    assert p["ic_mean"] == pytest.approx(0.012346) and p["decile_avg_ret_pct"] == "0.1,0.2"


def test_parse_rejects_truncated_and_multi_block_text():
    with pytest.raises(ValueError):
        parse_result_block(f"{RESULT_BEGIN}\nic_mean: 0.02\n")
    with pytest.raises(ValueError):
        parse_result_block(f"{RESULT_BEGIN}\na: 1\n{RESULT_END}\n" * 2)


def test_parse_blocks_checks_batch_size_and_duplicates():
    two = "\n".join(emit_result_block({"factor": n, "batch_size": 2}) for n in ("A", "B"))
    assert [b["factor"] for b in parse_result_blocks(two)] == ["A", "B"]
    with pytest.raises(ValueError):
        parse_result_blocks(emit_result_block({"factor": "A", "batch_size": 2}))
    with pytest.raises(ValueError):
        parse_result_blocks("\n".join(emit_result_block({"factor": "A"}) for _ in range(2)))


def test_stage3_blocks_are_distinct_by_variant():
    three = "\n".join(emit_result_block({"factor": "CONSTRUCTION_v0", "variant": v}) for v in ("a", "b"))
    assert [b["variant"] for b in parse_result_blocks(three)] == ["a", "b"]


# =============================================================================
# Validation
# =============================================================================

def _good_stage1():
    return {"stage": "1", "factor": "BM", "harness_sha": "abc", "config_sha": "def", "data_sha": "ghi",
            "ic_mean": 0.02, "icir": 0.3, "ic_tstat": 3.0, "ic_tstat_nw": 2.8, "ic_half_min": 0.01,
            "ls_sharpe": 0.5, "ls_ann_return_pct": 4.0, "ls_raw_ann_return_pct": 4.5, "coverage_pct": 70.0,
            "avg_names_per_decile": 200.0, "n_months": 324.0, "ls_n_months": 324.0,
            "eval_start": "1999-01-01", "eval_end": "2025-12-31", "survivorship_max_gone_pct": 45.0,
            "ls_beta_mean": -0.1, "ls_raw_sharpe": 0.45, "ls_sharpe_ex_top_years": 0.3}


def _good_stage2():
    return {"stage": "2", "factor": "X", "harness_sha": "abc", "config_sha": "def", "data_sha": "ghi",
            "base_ic_mean": 0.02, "base_ls_sharpe": 0.7, "cand_ic_mean": 0.024, "cand_ls_sharpe": 0.68,
            "resid_ic_mean": 0.01, "resid_ic_tstat_nw": 3.1, "spanning_alpha_tstat_nw": 2.2,
            "spanning_r2": 0.2, "paired_delta_ic_mean": 0.003, "paired_delta_ic_tstat": 2.5,
            "paired_delta_ls_mean": 0.0005, "paired_delta_ls_tstat": 0.6,
            "delta_ls_sharpe": -0.02, "corr_to_composite": 0.4, "n_months": 324.0,
            "eval_start": "1999-01-01", "eval_end": "2025-12-31",
            "base_ls_beta_mean": -0.1, "cand_ls_beta_mean": -0.12, "cand_ls_sharpe_ex_top_years": 0.3}


def test_clean_results_have_no_warnings():
    assert validate_results(_good_stage1(), "abc", "def", CONFIG, "ghi") == []
    assert validate_results(_good_stage2(), "abc", "def", CONFIG, "ghi") == []


def test_stamp_mismatches_are_flagged():
    assert any("HARNESS MISMATCH" in x for x in validate_results(_good_stage1(), "OTHER", "def", CONFIG))
    assert any("CONFIG MISMATCH" in x for x in validate_results(_good_stage1(), "abc", "OTHER", CONFIG))
    assert any("DATA MISMATCH" in x for x in validate_results(_good_stage1(), "abc", "def", CONFIG, "OTHER"))


def test_out_of_sample_breach_is_flagged():
    r = _good_stage1(); r["eval_end"] = "2026-03-31"
    assert any("OUT-OF-SAMPLE" in x for x in validate_results(r, "abc", "def", CONFIG))


def test_thin_sample_and_decile_collapse_are_inconclusive():
    r = _good_stage1(); r["n_months"] = 60.0; r["ls_n_months"] = 60.0
    assert any("INCONCLUSIVE" in x for x in validate_results(r, "abc", "def", CONFIG))
    r = _good_stage1(); r["ls_n_months"] = 130.0
    assert any("DECILE COLLAPSE" in x for x in validate_results(r, "abc", "def", CONFIG))


def test_missing_required_field_is_flagged():
    r = _good_stage2(); del r["resid_ic_tstat_nw"]
    assert any("resid_ic_tstat_nw" in x for x in validate_results(r, "abc", "def", CONFIG))


def test_implausible_coverage_is_flagged_for_a_leg_but_not_a_baseline():
    r = _good_stage1(); r["coverage_pct"] = 100.0
    assert any("implausibly complete" in x for x in validate_results(r, "abc", "def", CONFIG))
    r["stage"] = "baseline"
    assert not any("implausibly" in x for x in validate_results(r, "abc", "def", CONFIG))


def test_ls_month_floor_is_the_stricter_of_absolute_and_relative():
    assert ls_month_floor(372, 120) == int(0.9 * 372)
    assert ls_month_floor(100, 120) == 120


# =============================================================================
# The bars
# =============================================================================

S1 = {"min_ic_mean": 0.010, "min_ic_tstat_nw": 2.5, "min_ic_half_mean": 0.0,
      "min_ls_ann_return_pct": 0.0, "min_coverage_pct": 40.0, "min_avg_names_per_decile": 30}
S2 = {"min_resid_ic_tstat_nw": 2.0, "min_paired_delta_ls_tstat": -2.0}


def test_stage1_passes_a_strong_factor_and_lists_every_bar():
    passed, details = check_stage1(_good_stage1(), S1, min_ls_months=120)
    assert passed
    assert [d["check"] for d in details] == ["ic_mean", "ic_tstat_nw", "ic_half_min",
                                             "ls_raw_ann_return_pct", "coverage_pct",
                                             "avg_names_per_decile", "ls_n_months"]


def test_stage1_has_no_sharpe_or_hit_rate_bar():
    names = [c[0] for c in stage1_checks(_good_stage1(), S1)]
    assert "ls_sharpe" not in names and "ls_hit_rate_pct" not in names


def test_stage1_has_no_cost_bar():
    names = [c[0] for c in stage1_checks(_good_stage1(), S1)]
    assert "ls_net_ann_return_pct" not in names and "ls_raw_ann_return_pct" in names
    assert "ls_ann_return_pct" not in names, "the hedged headline is not a Stage 1 bar (D11)"


def test_stage1_fails_on_one_regime_or_a_negative_gross_spread():
    r = _good_stage1(); r["ic_half_min"] = -0.002
    assert not check_stage1(r, S1)[0]
    r = _good_stage1(); r["ls_raw_ann_return_pct"] = -0.5
    assert not check_stage1(r, S1)[0]
    r = _good_stage1(); r["ls_ann_return_pct"] = -0.5     # the hedged headline is not read by Stage 1
    assert check_stage1(r, S1)[0]


def test_missing_value_fails_rather_than_passing_by_default():
    r = _good_stage1(); r["ic_tstat_nw"] = None
    passed, details = check_stage1(r, S1)
    assert not passed and any(d["result"] == "MISSING" for d in details)


def test_stage2_accepts_new_information_even_when_sharpe_falls():
    """Information up, Sharpe of the family blend down but not
    significantly: accepted — construction is Stage 3's job."""
    r = _good_stage2(); r["delta_ls_sharpe"] = -0.15; r["paired_delta_ls_tstat"] = -1.2
    passed, details = check_stage2(r, S2)
    assert passed and [d["check"] for d in details] == ["resid_ic_tstat_nw", "paired_delta_ls_tstat"]


def test_stage2_has_exactly_two_bars_residual_ic_and_the_return_guard():
    """The V3 rule: a signal is accepted on the information it adds (residual
    IC) with a guard on the blend's gross return. The paired composite-dIC
    is a diagnostic, never a bar."""
    names = [c[0] for c in stage2_checks(_good_stage2(), S2)]
    assert names == ["resid_ic_tstat_nw", "paired_delta_ls_tstat"]
    assert "paired_delta_ic_tstat" not in names


def test_stage2_residual_ic_bar_is_strictly_greater_than_two():
    r = _good_stage2(); r["resid_ic_tstat_nw"] = 2.0
    assert not check_stage2(r, S2)[0]
    r["resid_ic_tstat_nw"] = 2.0001
    assert check_stage2(r, S2)[0]


def test_stage2_spanning_alpha_is_a_diagnostic_not_a_bar():
    r = _good_stage2(); r["spanning_alpha_tstat_nw"] = -3.0
    assert check_stage2(r, S2)[0]
    assert "spanning_alpha_tstat_nw" not in [c[0] for c in stage2_checks(r, S2)]


def test_stage2_does_not_bar_on_the_composite_dic():
    """A negative or insignificant paired dIC is reported, not decided on."""
    r = _good_stage2(); r["paired_delta_ic_tstat"] = -1.2
    assert check_stage2(r, S2)[0]


def test_stage2_rejects_a_redundant_factor_through_the_residual_test():
    r = _good_stage2(); r["resid_ic_tstat_nw"] = 0.8
    assert not check_stage2(r, S2)[0]


def test_stage2_guard_fires_only_on_a_significant_ls_return_fall():
    r = _good_stage2(); r["paired_delta_ls_tstat"] = -1.5
    assert check_stage2(r, S2)[0]
    r["paired_delta_ls_tstat"] = -2.5
    assert not check_stage2(r, S2)[0]


def test_stage2_checks_are_the_same_list_the_runner_uses():
    assert [c[0] for c in stage2_checks(_good_stage2(), S2)] == [d["check"] for d in check_stage2(_good_stage2(), S2)[1]]


def test_series_keys_never_reach_a_block():
    for k in SERIES_KEYS:
        assert k not in emit_result_block({k: pd.Series([1.0])})


# ---- the family blend (V3 search construction) --------------------------------

from harness.analytics import blend_family_ranks, family_members, family_weights  # noqa: E402

FAM_METAS = [{"name": "a1", "col": "f_a1", "ascending": True, "winsorize": True, "weight": 1.0, "family": "alpha"},
             {"name": "a2", "col": "f_a2", "ascending": True, "winsorize": True, "weight": 1.0, "family": "alpha"},
             {"name": "b", "col": "f_b", "ascending": True, "winsorize": True, "weight": 1.0, "family": "beta"}]


def test_family_weights_are_one_over_f_per_family_split_equally_within():
    w = family_weights(FAM_METAS)
    assert w == {"a1": 0.25, "a2": 0.25, "b": 0.5}
    assert family_members(FAM_METAS) == {"alpha": ["a1", "a2"], "beta": ["b"]}


def test_a_single_meta_without_a_family_is_its_own_family_but_a_blend_needs_one_per_leg():
    solo = [{"name": "x", "col": "f_x", "ascending": True, "winsorize": True, "weight": 1.0, "family": None}]
    assert family_weights(solo) == {"x": 1.0}
    with pytest.raises(ValueError, match="family"):
        family_weights(solo + [FAM_METAS[2]])


def test_family_blend_keeps_a_family_weight_when_one_member_is_missing():
    """Two-level: a name missing a2 still gets alpha's full half weight from
    a1 alone; a flat 0.25/0.25/0.5 blend would hand the gap to beta."""
    ranks = pd.DataFrame({"a1": [0.9, 0.9], "a2": [0.1, np.nan], "b": [0.2, 0.2]})
    s = blend_family_ranks(ranks, FAM_METAS)
    assert s.iloc[0] == pytest.approx(((0.9 + 0.1) / 2 + 0.2) / 2)
    assert s.iloc[1] == pytest.approx((0.9 + 0.2) / 2)
    flat = blend_ranks(ranks, family_weights(FAM_METAS))
    assert flat.iloc[1] != pytest.approx(s.iloc[1])
    assert flat.iloc[0] == pytest.approx(s.iloc[0])


def test_family_blend_is_nan_only_where_no_leg_is_available():
    ranks = pd.DataFrame({"a1": [np.nan], "a2": [np.nan], "b": [np.nan]})
    assert blend_family_ranks(ranks, FAM_METAS).isna().all()
    ranks = pd.DataFrame({"a1": [np.nan], "a2": [np.nan], "b": [0.3]})
    assert blend_family_ranks(ranks, FAM_METAS).iloc[0] == pytest.approx(0.3)


def test_assign_composite_decile_default_is_the_family_blend():
    from harness.analytics import assign_composite_decile
    rng = np.random.default_rng(0)
    df = pd.DataFrame({"f_a1": rng.normal(size=200), "f_a2": rng.normal(size=200), "f_b": rng.normal(size=200)})
    df.loc[:20, "f_a2"] = np.nan
    out = assign_composite_decile(df, FAM_METAS)
    from harness.analytics import compute_factor_ranks
    ranks = pd.DataFrame(compute_factor_ranks(df, FAM_METAS), index=df.index)
    assert np.allclose(out["COMPOSITE_SCORE"], blend_family_ranks(ranks, FAM_METAS))
