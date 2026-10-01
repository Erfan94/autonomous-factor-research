"""
The Phase E construction layer (docs/CONSTRUCTION.md r2, harness/construction_layer.py).

Asserted: the closed-form KKT solution equals a dense solve (with and
without the market-beta column); the constraint (sector groups, plus the
market beta under sector_beta_neutral) holds to 1e-10 after the steps that
impose it (1, 2 and 5; the
buffer and the participation cap move names one at a time by design, and
step 5 exists to re-project after them); name caps hold on the target and
participation caps on the final trades; the drift accounting on a hand-built
three-month, four-name book; point-in-time: poisoning monthly_ret for months
>= t leaves every input at t unchanged; the cost formula; a flat book when
IC_t <= 0; the LAYER_SHA / composite refusal; the LAYER block parses and
validates; records.py does not DRIFT on a LAYER run; the Stage 3 books the
layer re-costs reproduce Stage 3's own series; the per-name market beta is
analytics.trailing_beta's; the harness-built Corwin-Schultz series equals the
BidAskSpread candidate's raw value and the cost model charges half of it; the
runner runs the layer on a composite with no spread leg.
"""
import argparse
import copy
import hashlib
import importlib.util
import io
import json
from contextlib import redirect_stdout

import numpy as np
import pandas as pd
import pytest

from harness import construction_layer as CL
from harness import portfolio as PF
from harness.analytics import emit_result_block, parse_result_blocks, validate_results
from harness.provenance import ROOT, load_config
from tests.layer_synthetic import METAS, make_audit

LCFG = CL.load_layer_config()
CFG = load_config()
SHA = LCFG["composite"]["composite_sha"]


@pytest.fixture(scope="module")
def panel():
    audit = make_audit(n_names=260, n_months=40, seed=1)
    P = CL.LayerPanel(audit, LCFG, METAS)
    R = CL.build_risk_model(P, LCFG)
    ic_t, _ = CL.ic_forecast(P, LCFG)
    return audit, P, R, ic_t


def _book_month(P):
    return next(m for m in range(P.M) if P.dates[m] >= pd.Timestamp("2001-01-01"))


# ---- §5 optimiser ------------------------------------------------------------

def _random_risk(n=50, n_groups=5, seed=3):
    rng = np.random.default_rng(seed)
    g = rng.integers(0, n_groups, n)
    X = np.zeros((n, n_groups + 2))
    X[np.arange(n), g] = 1.0
    X[:, n_groups:] = rng.normal(size=(n, 2))
    B = rng.normal(size=(n_groups + 2, n_groups + 2)) * 0.02
    F = B @ B.T
    D = rng.uniform(0.002, 0.02, n)
    alpha = rng.normal(size=n) * 0.01
    C = (g[:, None] == np.arange(n_groups)[None, :]).astype(float)
    return X, F, D, alpha, C, g


def test_kkt_closed_form_equals_a_dense_solve_on_n50():
    X, F, D, alpha, C, _ = _random_risk()
    lam = 3.7
    Sigma = X @ F @ X.T + np.diag(D)
    n, k = C.shape
    K = np.block([[lam * Sigma, C], [C.T, np.zeros((k, k))]])
    dense = np.linalg.solve(K, np.concatenate([alpha, np.zeros(k)]))[:n]
    w = CL.solve_neutral_mv(alpha, X, F, D, C, lam=lam)
    assert np.allclose(w, dense, rtol=1e-9, atol=1e-12)
    assert np.max(np.abs(C.T @ w)) < 1e-12
    v = np.arange(n, dtype=float)
    assert np.allclose(CL.sigma_inv(v, X, F, D), np.linalg.solve(Sigma, v), rtol=1e-9)
    # a singular factor covariance is fine: Woodbury is written without F^-1
    F0 = F.copy(); F0[0, :] = F0[:, 0] = 0.0
    S0 = X @ F0 @ X.T + np.diag(D)
    assert np.allclose(CL.sigma_inv(v, X, F0, D), np.linalg.solve(S0, v), rtol=1e-9)


def test_name_cap_holds_and_keeps_groups_neutral():
    rng = np.random.default_rng(0)
    n, G = 120, 6
    g = rng.integers(0, G, n)
    w = rng.standard_t(2, n) * 0.01
    w = CL.project_neutral(w, g, G)
    w2, it, excess, resid = CL.apply_name_cap(w, CL.Constraint(g, G), 0.01, 5.0, 1e-10, 50)
    nL, nS = (w > 0).sum(), (w < 0).sum()
    cap = np.where(w2 > 0, max(0.01, 5 / nL), max(0.01, 5 / nS))
    assert np.all(np.abs(w2) <= cap + 1e-10) and excess <= 1e-10
    assert np.max(np.abs(np.bincount(g, w2, G))) <= 1e-10 and resid <= 1e-10
    assert abs(w2.sum()) <= 1e-10


def test_buffer_and_participation_arithmetic():
    t = np.array([0.010, 0.010, 0.0, -0.02])
    h = np.array([0.009, 0.004, 0.00015, -0.001])
    w, keep = CL.buffer_step(t, h, 0.25, 0.0002, 0.5)
    # |0.001| <= 0.0025+0.0002 keep; |0.006| > 0.0027 move half; |0.00015| <= 0.0002 keep; move half
    assert keep.tolist() == [True, False, True, False]
    assert np.allclose(w, [0.009, 0.007, 0.00015, -0.0105])
    capd = np.array([1.0, 0.001, 1.0, 0.004])
    w4, hit = CL.participation_cap(w, h, capd)
    assert hit.tolist() == [False, True, False, True]
    assert np.allclose(w4, [0.009, 0.005, 0.00015, -0.005])


def test_constraints_after_each_pipeline_step(panel):
    audit, P, R, ic_t = panel
    m = _book_month(P)
    for constraint, check in (("sector_beta_neutral", "beta"), ("sector_neutral", "sector"),
                              ("dollar_neutral", "dollar")):
        T = CL.build_target(P, R, m, abs(ic_t[m]) + 0.05, LCFG, constraint)
        assert not T["flat"]
        I, groups, G = T["eligible"], T["groups"], T["n_groups"]
        beta = P.market_betas(m)[0]
        assert (T["beta"] is not None) == (check == "beta") and not T["beta_dropped"]
        # step 1 (target) and step 2 (name cap): the constraint to 1e-10
        assert T["resid_step1"] <= 1e-10 and T["resid_step2"] <= 1e-10
        assert np.max(np.abs(np.bincount(groups[I], T["w_step1"], G))) <= 1e-10
        assert np.max(np.abs(np.bincount(groups, T["t"], G))) <= 1e-10
        if check == "beta":
            assert abs(T["w_step1"] @ beta[I]) <= 1e-10 and abs(T["t"] @ beta) <= 1e-10
        else:                                                  # the unconstrained books carry beta
            assert abs(T["t"] @ beta) > 1e-6
        assert abs(T["t"].sum()) <= 1e-10                      # sector-neutral implies dollar-neutral
        assert np.abs(T["t"]).sum() <= LCFG["alpha"]["gross_cap"] + 1e-12
        w = T["t"][I]
        nL, nS = (w > 0).sum(), (w < 0).sum()
        o = LCFG["optimiser"]
        cap = np.where(w > 0, max(o["name_cap_floor"], o["name_cap_mult"] / nL),
                       max(o["name_cap_floor"], o["name_cap_mult"] / nS))
        assert np.all(np.abs(w) <= cap + 1e-10)
        # steps 3-5 against a held book far from the target, at an AUM where
        # the participation cap binds on many names
        rng = np.random.default_rng(5)
        hU = T["cons"].project(T["t"] * 0.3 + rng.normal(0, 0.002, len(T["t"])) * I)
        aum = 5e10
        dec = CL.layer_decider(P, {m: T}, LCFG, aum)
        w5, diag = dec(m, hU)
        assert diag["n_participation_hit"] > 0
        assert np.max(np.abs(np.bincount(groups, w5, G))) <= 1e-10
        assert abs(w5.sum()) <= 1e-10
        if check in ("sector", "beta"):
            assert np.max(np.abs(np.bincount(P.sector[P.sl(m)], w5, P.G))) <= 1e-10
        if check == "beta":
            assert abs(w5 @ beta) <= 1e-10 and diag["resid_beta_final"] <= 1e-10
            assert diag["reproj_traded"] > 0                   # step 5 had work to do
        capd = o["participation_pct"] / 100 * P.adv[P.sl(m)] * o["participation_days"] / aum
        assert np.all(np.abs(w5 - hU) <= capd * (1 + 1e-9) + 1e-15)
        assert diag["overrides"] == 0
        assert np.abs(w5).sum() <= LCFG["alpha"]["gross_cap"] * (1 + 1e-9)


def test_full_path_neutral_every_month_and_first_book_2001_01(panel):
    audit, P, R, ic_t = panel
    res, meta = CL.run_layer(audit, METAS, CFG, LCFG, SHA, log=lambda *a: None,
                             rows=["layer", "layer_no_beta_constraint", "layer_dollar_neutral_only"])
    assert meta["constraints"] == "sector_beta_neutral"
    assert meta["market_beta_first_month"].startswith("2000-01")    # 12 months of M (1999-01..12) behind it
    assert meta["market_beta_own_estimate_pct"] > 60
    assert meta["first_live_month"].startswith("2001-01")
    assert meta["risk_first_ready"].startswith("2001-01")
    assert meta["vol_factor_first_month"].startswith("1999-07")     # 6 obs of history
    assert meta["sector_groups"] == 12
    for row, aum, st in res:
        assert st["book_start"].startswith("2001-01")
        assert st["max_neutrality_residual"] <= 1e-10, (row, aum)
        assert st["participation_overrides"] == 0
        assert st["constraint"] == {"layer": "sector_beta_neutral", "layer_no_beta_constraint": "sector_neutral",
                                    "layer_dollar_neutral_only": "dollar_neutral"}[row]
        if row == "layer":
            assert st["max_beta_residual"] <= 1e-10 and st["beta_constraint_dropped_months"] == 0
            assert abs(st["exp_beta_mean"]) <= 1e-10
        else:
            assert st["max_beta_residual"] == 0.0
        assert st["budget_scaled_months"] >= 0 and st["flat_months"] == 0
        for k in ("cut_exyears_net_n_months", "cut_2011_2020_net_n_months", "tier_MEGA_net_ann_return_pct",
                  "cost_spread_ann_pct", "cost_impact_ann_pct", "cost_borrow_ann_pct", "bias_stat_mean",
                  "net_maxdd_trough", "exp_size_mean", "exp_family_fa_mean", "reproj_share_of_turnover_pct",
                  "net_beta_on_market", "gross_beta_on_market", "net_beta_on_market_live", "exp_beta_mean",
                  "cut_exyears_net_beta_on_market"):
            assert k in st, k


# ---- §5 drift accounting -------------------------------------------------------

def _tiny_panel():
    """Three months, four names. Month 2: D delists (Shumway). Month 3: B has
    left the universe."""
    d = pd.date_range("2001-01-01", periods=3, freq="BME")
    sig = [d[0] - pd.offsets.BMonthEnd(1), d[0], d[1]]
    rows = []
    rets = {0: {"A": 0.10, "B": 0.0, "C": 0.10, "D": -0.20},
            1: {"A": 0.0, "B": 0.10, "C": 0.0, "D": -0.30},
            2: {"A": 0.05, "C": -0.05}}
    for t in range(3):
        for i, r in rets[t].items():
            rows.append({"ID": i, "DATE": d[t], "RET_END": d[t], "SIGNAL_ASOF": sig[t], "monthly_ret": r,
                         "ret_kind": "partial_delisted_performance" if (t == 1 and i == "D") else "full",
                         "liq_tier": "MID", "sector": "Energy", "mkt_cap_usd": 1e9, "adv_usd": 1e7,
                         "COMPOSITE_SCORE": 0.5, "cs_spread": 0.002})
    return pd.DataFrame(rows), d


def test_drift_accounting_on_a_hand_built_three_month_book():
    audit, d = _tiny_panel()
    P = CL.LayerPanel(audit, LCFG)
    R = [CL.RiskMonth(None, None, None, np.ones(P.offsets[m + 1] - P.offsets[m]), False, 0, False)
         for m in range(P.M)]
    books = [(d[0], {"A", "B"}, {"C", "D"}), (d[2], {"A"}, {"C"})]      # month 2 holds the drifted book
    rec = CL.run_book(P, R, LCFG, [0, 1, 2], 1e8, CL.reference_decider(P, books), eta=0.0)
    hs, bor = 0.001, 25.0 / 1e4 / 12
    # month 1: build 0.5/0.5/-0.5/-0.5 from cash
    g1 = 0.5 * 0.10 + 0.5 * 0.0 - 0.5 * 0.10 - 0.5 * -0.20
    n1 = g1 - hs * 2.0 - bor * 1.0
    assert rec[0]["gross"] == pytest.approx(0.10) and rec[0]["net"] == pytest.approx(n1)
    h = np.array([0.5 * 1.10, 0.5 * 1.0, -0.5 * 1.10, -0.5 * 0.80]) / (1 + n1)
    # month 2: no trade; D earns its Shumway return and closes to cash at no cost
    g2 = h @ np.array([0.0, 0.10, 0.0, -0.30])
    n2 = g2 - bor * -(h[2] + h[3])
    assert rec[1]["gross"] == pytest.approx(g2) and rec[1]["net"] == pytest.approx(n2)
    assert rec[1]["spread"] == 0.0 and rec[1]["turnover"] == 0.0
    h2 = np.array([h[0], h[1] * 1.10, h[2], 0.0]) / (1 + n2)
    # month 3: B left the universe -> sold at its last half-spread; A,C to +1/-1; D already cash
    traded = abs(1.0 - h2[0]) + abs(-1.0 - h2[2]) + abs(h2[1])
    g3 = 0.05 * 1.0 + -1.0 * -0.05
    assert rec[2]["spread"] == pytest.approx(hs * traded)
    assert rec[2]["borrow"] == pytest.approx(bor * 1.0)
    assert rec[2]["net"] == pytest.approx(g3 - hs * traded - bor)
    assert rec[2]["n_exit_sales"] == 1 and rec[2]["turnover"] == pytest.approx(traded / 2)


# ---- §6 costs --------------------------------------------------------------------

def test_cost_formula_on_a_hand_example():
    sp, im = CL.trade_costs(np.array([0.01, -0.01]), np.array([0.0005, 0.0005]),
                            np.array([0.02, 0.02]), np.array([1e7, 1e7]), 1e8, 0.5)
    # Q = $1M, Q/ADV = 0.1: spread 0.01*5bp; impact 0.01 * 0.5 * 0.02 * sqrt(0.1)
    assert sp == pytest.approx([5e-6, 5e-6])
    assert im == pytest.approx([0.01 * 0.5 * 0.02 * np.sqrt(0.1)] * 2)
    tier = np.array([0, 0, 0, 2, 2])
    hs = CL.half_spreads(np.array([0.0001, 0.004, np.nan, 0.01, np.nan]), tier, LCFG)
    # floor 1bp beats 0.5bp; missing -> the tier's median of the floored values
    assert hs == pytest.approx([1e-4, 2e-3, np.median([1e-4, 2e-3]), 5e-3, 5e-3])
    fixed = CL.half_spreads(np.full(3, np.nan), np.array([0, 1, 2]), LCFG, mode="fixed")
    assert fixed == pytest.approx([2e-4, 5e-4, 12e-4])


# ---- §3 flat book ----------------------------------------------------------------

def test_flat_book_when_ic_is_not_positive(panel):
    audit, P, R, ic_t = panel
    m = _book_month(P)
    for ic in (0.0, -0.01, np.nan):
        T = CL.build_target(P, R, m, ic, LCFG)
        assert T["flat"] and not np.any(T["t"])
    assert CL.build_target(P, R, m, -0.01, LCFG)["reason"] == "ic_nonpositive"
    T = CL.build_target(P, R, m, -0.01, LCFG)
    hU = np.full(len(T["t"]), 0.001)
    w, diag = CL.layer_decider(P, {m: T}, LCFG, 1e9)(m, hU)
    assert not np.any(w) and diag["flat"]
    # a composite with negative realised IC is flat in every book month
    neg = make_audit(n_names=200, n_months=36, seed=2, signal=-0.03)
    res, _ = CL.run_layer(neg, METAS, CFG, LCFG, SHA, log=lambda *a: None, rows=["layer"])
    for _, _, st in res:
        assert st["flat_months"] == st["n_months"] == st["flat_months_ic_nonpositive"]
        assert st["gross_ann_return_pct"] == 0.0 and st["avg_n_long"] == 0.0


# ---- §2 point in time ------------------------------------------------------------

def test_poisoned_future_returns_do_not_move_anything_at_t():
    audit = make_audit(n_names=220, n_months=36, seed=4)
    dates = sorted(audit["DATE"].unique())
    t_date = dates[27]
    bad = audit.copy()
    fut = bad["DATE"] >= t_date
    bad.loc[fut, "monthly_ret"] = np.random.default_rng(9).normal(5.0, 3.0, fut.sum())

    def weights_at(frame):
        P = CL.LayerPanel(frame, LCFG, METAS)
        R = CL.build_risk_model(P, LCFG)
        ic, _ = CL.ic_forecast(P, LCFG)
        m = int(np.searchsorted(P.dates.values, np.datetime64(t_date)))
        book = [k for k in range(P.M) if P.dates[k] >= pd.Timestamp("2001-01-01")]
        targets = {k: CL.build_target(P, R, k, ic[k], LCFG) for k in book}
        seen = {}
        dec = CL.layer_decider(P, targets, LCFG, 1e9)

        def spy(k, hU):
            w, dg = dec(k, hU)
            seen[k] = w.copy()
            return w, dg
        CL.run_book(P, R, LCFG, [k for k in book if k <= m], 1e9, spy, 0.5)
        return P, R, ic, m, targets[m], seen[m]

    P0, R0, ic0, m, T0, w0 = weights_at(audit)
    P1, R1, ic1, _, T1, w1 = weights_at(bad)
    assert m == 27 and not T0["flat"]
    assert ic0[m] == ic1[m]
    assert np.array_equal(R0[m].X, R1[m].X)                  # trailing vol (and size) exposures
    assert np.array_equal(R0[m].F, R1[m].F) and np.array_equal(R0[m].D, R1[m].D)
    assert np.array_equal(R0[m].sigma, R1[m].sigma)
    assert np.array_equal(T0["t"], T1["t"])
    assert np.array_equal(w0, w1)                            # the held (drifted) book too
    # the test has power: month t+1 does see month t's poisoned return
    assert not np.allclose(R0[m + 1].sigma, R1[m + 1].sigma)
    assert ic0[m + 1] != ic1[m + 1]


# ---- references ------------------------------------------------------------------

def test_stage3_books_reproduce_stage3_series_and_numbers_are_unchanged(panel):
    audit, P, R, _ = panel
    for name in ("equal_rank_decile", "buffered"):
        plain = getattr(PF, name)(audit, METAS, CFG)
        books = []
        s, tl, ts, desc = getattr(PF, name)(audit, METAS, CFG, books=books)
        assert s.equals(plain[0]) and (tl, ts, desc) == plain[1:]
        months = [m for m in range(P.M) if P.dates[m] >= pd.Timestamp("2001-01-01")]
        rec = CL.run_book(P, R, LCFG, months, 1e8, CL.reference_decider(P, books), 0.5)
        gross = pd.Series({r["date"]: r["gross"] for r in rec})
        assert np.allclose(gross.values, s.loc[gross.index].values, atol=1e-14)


# ---- stamps, refusal, blocks, records --------------------------------------------

def test_layer_sha_and_refusal_of_another_composite(tmp_path):
    assert CL.layer_sha() == hashlib.sha256(CL.LAYER_CONFIG_PATH.read_bytes()).hexdigest()[:12]
    p = tmp_path / "l.yaml"
    p.write_bytes(CL.LAYER_CONFIG_PATH.read_bytes() + b"\n# edit\n")
    assert CL.layer_sha(p) != CL.layer_sha()
    CL.check_composite(LCFG, SHA)
    with pytest.raises(CL.LayerRefused):
        CL.check_composite(LCFG, "000000000000")
    wrong = copy.deepcopy(LCFG)
    wrong["composite"]["composite_sha"] = "deadbeef0000"
    with pytest.raises(CL.LayerRefused):
        CL.run_layer(make_audit(50, 6), METAS, CFG, wrong, SHA, log=lambda *a: None)


def test_runner_refuses_the_layer_on_a_wrong_composite(tmp_path):
    from harness import run_test as RT
    ns = argparse.Namespace(factor=None, factors=None, baseline=True, stage=None, include_holdout=False,
                            holdout_only=False, dry_run=False, frozen=True, schema_only=False,
                            construction_layer=True)
    stamps = {"harness_sha": "a" * 12, "config_sha": "b" * 12, "composite_sha": "c" * 12,
              "data_sha": "d" * 12, "universe_sha": "e" * 12}
    runtime = {"results": {"dir": str(tmp_path)}}
    with pytest.raises(SystemExit, match="refused"):
        RT.run(ns, cfg=CFG, runtime=runtime, stamps=stamps, root=tmp_path, out_stream=io.StringIO())
    ns.stage = 2
    with pytest.raises(SystemExit, match="no --stage"):
        RT.run(ns, cfg=CFG, runtime=runtime, stamps=stamps, root=tmp_path, out_stream=io.StringIO())
    assert not list(tmp_path.glob("*.txt"))


def _layer_blocks(audit):
    res, meta = CL.run_layer(audit, METAS, CFG, LCFG, SHA, log=lambda *a: None)
    blocks = []
    for row, aum, st in res:
        f = {"stage": "E", "factor": "LAYER_v0", "variant": f"{row}@{CL.aum_tag(aum)}",
             "composite_sha": SHA, "layer_sha": "012345678901", "harness_sha": "h" * 12,
             "config_sha": "c" * 12, "data_sha": "d" * 12, "eval_start": CFG["dates"]["eval_start"],
             "eval_end": CFG["dates"]["eval_end"]}
        f.update(st)
        blocks.append(emit_result_block(f))
    return res, blocks


def test_layer_blocks_parse_and_validate(panel):
    audit, *_ = panel
    res, blocks = _layer_blocks(audit)
    rows = list(CL.row_specs(LCFG))
    assert len(blocks) == len(rows) * len(LCFG["report"]["aum_usd"]) == 33
    assert rows[6:] == ["equal_rank_decile", "buffered", "layer_no_buffer", "layer_no_beta_constraint",
                        "layer_dollar_neutral_only"]
    assert rows[:6] == ["layer", "layer_eta_0.25", "layer_eta_1", "layer_fixed_tier_spread",
                        "layer_exec_half_month", "layer_tiered_borrow"]
    parsed = parse_result_blocks("\n".join(blocks))
    cfg = dict(CFG)
    cfg["rebalance"] = dict(CFG["rebalance"], min_months=12)
    for b in parsed:
        assert b["stage"] == "E" and isinstance(b["layer_sha"], str) and b["layer_sha"] == "012345678901"
        assert isinstance(b["net_sharpe"], float) and isinstance(b["gross_maxdd_trough"], str)
        assert validate_results(b, "h" * 12, "c" * 12, cfg, "d" * 12) == []


def _records_module():
    spec = importlib.util.spec_from_file_location("records_under_test", ROOT / "scripts" / "records.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_records_check_does_not_drift_on_a_layer_run(tmp_path, monkeypatch):
    from harness import provenance
    rec = _records_module()
    res_dir = tmp_path / "results"; res_dir.mkdir()
    stamps = provenance.all_stamps()
    meta = {"seq": 999, "label": "LAYER", "stage": "E", "baseline": True, "stamps": stamps,
            "construction_layer": True, "layer_sha": CL.layer_sha()}
    (res_dir / "999_LAYER_stageE_2026-09-27.meta.json").write_text(json.dumps(meta))
    events = tmp_path / "events.jsonl"
    events.write_text(json.dumps({"event": "run_started", "seq": "999", "label": "LAYER", "stage": "E"}) + "\n")
    monkeypatch.setattr(rec, "RESULTS", res_dir)
    monkeypatch.setattr(rec, "EVENTS", events)
    buf = io.StringIO()
    with redirect_stdout(buf):
        assert rec.unevaluated_runs() is True            # unevaluated but not stranded
        assert rec.phase_gate({}) is True                # a stage-E run is not a Stage 2 start
    assert "unevaluated run 999" in buf.getvalue()
    with events.open("a") as fh:
        fh.write(json.dumps({"event": "construction_reported", "seq": "999"}) + "\n")
    buf = io.StringIO()
    with redirect_stdout(buf):
        assert rec.unevaluated_runs() is True
    assert "999" not in buf.getvalue()
    # a LAYER run whose stamps moved IS stranded, like any other run
    meta["stamps"] = dict(stamps, harness_sha="000000000000")
    (res_dir / "999_LAYER_stageE_2026-09-27.meta.json").write_text(json.dumps(meta))
    events.write_text("")
    with redirect_stdout(io.StringIO()):
        assert rec.unevaluated_runs() is False


# ---- the runner, end to end on the synthetic snapshot -----------------------------

def test_layer_panel_refuses_a_frame_without_the_harness_spread():
    """The cost model reads the harness-built series (attach_spread), never a
    leg; a frame without it is refused rather than charged the floor."""
    with pytest.raises(CL.LayerRefused, match="spread column"):
        CL.LayerPanel(make_audit(50, 6).drop(columns=["cs_spread"]), LCFG)
    # a frame without any spread-like leg runs once the series is attached
    audit = make_audit(60, 6).drop(columns=["cs_spread", "f_bidaskspreadflip"])
    cs = pd.DataFrame({"me": audit["SIGNAL_ASOF"], "ID": audit["ID"], "cs_spread": 0.01})
    P = CL.LayerPanel(CL.attach_spread(audit, cs), LCFG)
    assert np.all(P.spread == 0.01)


def test_runner_refuses_holdout_only_with_the_layer(tmp_path):
    from harness import run_test as RT
    ns = argparse.Namespace(factor=None, factors=None, baseline=True, stage=None, include_holdout=False,
                            holdout_only=True, dry_run=False, frozen=True, schema_only=False,
                            construction_layer=True)
    stamps = {"harness_sha": "a" * 12, "config_sha": "b" * 12, "composite_sha": SHA,
              "data_sha": "d" * 12, "universe_sha": "e" * 12}
    with pytest.raises(SystemExit, match="spend the holdout with --include-holdout|Spend the holdout with --include-holdout"):
        RT.run(ns, cfg=CFG, runtime={"results": {"dir": str(tmp_path)}}, stamps=stamps, root=tmp_path,
               out_stream=io.StringIO())
    assert not list(tmp_path.glob("*"))


@pytest.mark.parametrize("holdout", [False, True])
def test_runner_layer_end_to_end_on_the_synthetic_snapshot(synthetic, cfg, runtime, snap, holdout):
    from harness import run_test as RT
    from tests.test_run_end_to_end import C_V0, STAMPS
    # the plain pinned v0 composite: no leg carries a spread (D7 item 2)
    assert not any("spread" in f.col for f in C_V0.active_factors())
    lcfg = copy.deepcopy(LCFG)
    lcfg["composite"]["composite_sha"] = STAMPS["composite_sha"]
    ns = argparse.Namespace(factor=None, factors=None, baseline=True, stage=None, include_holdout=holdout,
                            holdout_only=False, dry_run=False, frozen=True, schema_only=False,
                            construction_layer=True)
    sink = io.StringIO()
    blocks = RT.run(ns, C=C_V0, cfg=cfg, runtime=runtime, stamps=STAMPS, snap=snap, root=synthetic["root"],
                    out_stream=sink, layer_cfg=lcfg)
    parsed = parse_result_blocks("\n".join(blocks))
    assert len(parsed) == len(CL.row_specs(lcfg)) * len(lcfg["report"]["aum_usd"])
    for b in parsed:
        assert b["stage"] == "E" and b["factor"] == "LAYER_v0" and b["layer_sha"] == CL.layer_sha()
        assert b["composite_sha"] == STAMPS["composite_sha"] and b["include_holdout"] == str(holdout)
        assert b["book_start"].startswith("2001-01")
        warns = validate_results(b, STAMPS["harness_sha"], STAMPS["config_sha"], cfg, STAMPS["data_sha"])
        assert all(w.startswith("OUT-OF-SAMPLE") or w.startswith("Only") for w in warns), warns
        assert ("cut_holdout_net_n_months" in b) == holdout
        assert "Spread" not in b["composite_legs"] and b["constraints"] == "sector_beta_neutral"
        assert b["spread_measured_pct"] > 50
        for k in ("unclassified_share_pct", "delisted_share_unclassified_pct", "new_positions_delisting_n"):
            assert k in b, k
    txt = sorted((synthetic["root"] / "results").glob("*_LAYER_stageE_*.txt"))[-1]
    meta = json.loads(txt.with_suffix(".meta.json").read_text())
    assert meta["label"] == "LAYER" and meta["stage"] == "E" and meta["layer_sha"] == CL.layer_sha()
    paths = txt.with_suffix(".paths.csv")
    assert paths.exists() and meta["paths_file"] == paths.name
    assert meta["paths_sha"] == hashlib.sha256(paths.read_bytes()).hexdigest()[:12]
    csv = pd.read_csv(paths)
    for b in parsed:
        assert b["paths_sha"] == meta["paths_sha"]
        row, tag = b["variant"].split("@")
        sub = csv[(csv["row"] == row) & (csv["aum_usd"] == b["aum_usd"])]
        assert len(sub) == b["n_months"]
        if b.get("gross_ann_return_pct") is not None:
            assert sub["gross"].mean() * 1200 == pytest.approx(b["gross_ann_return_pct"], abs=2e-6)
            assert sub["net"].mean() * 1200 == pytest.approx(b["net_ann_return_pct"], abs=2e-6)
        if holdout:
            assert "cut_inwindow_net_maxdd_pct" in b or b["cut_inwindow_net_n_months"] < 2
            assert "cut_holdout_participation_hit_share_pct" in b or row in ("equal_rank_decile", "buffered")
    summ = txt.with_name(txt.stem + "_summary.md").read_text()
    assert f"LAYER {CL.layer_sha()}" in summ and "layer@100M" in summ
    assert "LAYER_SHA" in sink.getvalue()


def test_holdout_only_window_is_flat_until_the_risk_model_has_history():
    """--holdout-only hands the layer frames from 2023-01 only (the same window
    logic as every baseline run). book_start still applies; the risk model
    needs 24 months of factor returns inside the frames, so the book is flat,
    and counted as such, until then."""
    audit = make_audit(n_names=150, n_months=30, start="2023-01-01", seed=6)
    # the beta constraint has no estimate in the first 12 book months: refused (alpha-review of 41edba9)
    with pytest.raises(CL.LayerRefused, match="market-beta constraint has no estimate in 12 book month"):
        CL.run_layer(audit, METAS, CFG, LCFG, SHA, log=lambda *a: None, rows=["layer"], oos_start="2023-01-01")
    lcfg = copy.deepcopy(LCFG)
    lcfg["optimiser"]["constraints"] = "sector_neutral"
    res, meta = CL.run_layer(audit, METAS, CFG, lcfg, SHA, log=lambda *a: None, rows=["layer"],
                             oos_start="2023-01-01")
    assert meta["risk_first_ready"].startswith("2025-01")
    for _, _, st in res:
        assert st["book_start"].startswith("2023-01") and st["n_months"] == 30
        assert st["flat_months_no_history_risk"] == 24
        assert st["cut_holdout_net_n_months"] == 30


# ---- alpha-review fixes (2026-09-27) -----------------------------------------------

def test_gross_never_exceeds_the_budget_in_budget_scaled_months():
    """ic_ref raised so IC_t < ic_ref in every month: G_t < 2 throughout. The
    final book's gross is <= G_t + 1e-9 every month, with the group constraint."""
    audit = make_audit(n_names=240, n_months=40, seed=11)
    lcfg = copy.deepcopy(LCFG)
    lcfg["alpha"]["ic_ref"] = 1.0
    P = CL.LayerPanel(audit, lcfg, METAS)
    R = CL.build_risk_model(P, lcfg)
    ic, _ = CL.ic_forecast(P, lcfg)
    book = [m for m in range(P.M) if P.dates[m] >= pd.Timestamp("2001-01-01")]
    for constraint in ("sector_beta_neutral", "sector_neutral", "dollar_neutral"):
        T = {m: CL.build_target(P, R, m, ic[m], lcfg, constraint) for m in book}
        for aum in (1e8, 5e10):
            seen = {}
            dec = CL.layer_decider(P, T, lcfg, aum)

            def spy(k, hU):
                w, dg = dec(k, hU)
                seen[k] = w
                return w, dg
            rec = CL.run_book(P, R, lcfg, book, aum, spy, 0.5)
            live = [m for m in book if not T[m]["flat"]]
            assert live and all(T[m]["budget_scaled"] for m in live)
            for m in live:
                w = seen[m]
                assert np.abs(w).sum() <= T[m]["G_t"] + 1e-9, (constraint, aum, m)
                assert np.max(np.abs(np.bincount(T[m]["groups"], w, T[m]["n_groups"]))) <= 1e-10
                assert abs(w.sum()) <= 1e-10
                if constraint == "sector_beta_neutral":
                    assert abs(w @ T[m]["beta"]) <= 1e-10
            st, _ = CL.summarise(rec, lcfg)
            assert st["gross_budget_max_excess"] == 0.0 and st["months_gross_exceeds_budget"] == 0


def test_execution_fraction_accounting():
    """Traded dw earns trade_frac of r: book return sum (h + f dw) r; end value
    w + (h + f dw) r; costs unchanged."""
    w = np.array([0.6, -0.4, 0.0]); h = np.array([0.2, -0.5, 0.1]); r = np.array([0.10, -0.05, 0.02])
    z = np.zeros(3)
    a1 = CL.account_month(w, h, r, np.zeros(3, bool), z, z, np.ones(3), 1e8, 0.0, 0.0, 1.0)
    a5 = CL.account_month(w, h, r, np.zeros(3, bool), z, z, np.ones(3), 1e8, 0.0, 0.0, 0.5)
    assert a1["gross"] == pytest.approx(float(w @ r))
    g5 = float((h + 0.5 * (w - h)) @ r)
    assert a5["gross"] == pytest.approx(g5) and a5["spread"] == a1["spread"]
    assert a5["h_next"] == pytest.approx((w + (h + 0.5 * (w - h)) * r) / (1 + g5))
    assert a1["h_next"] == pytest.approx(w * (1 + r) / (1 + float(w @ r)))


def test_tiered_borrow_rates_and_rows(panel):
    rates = CL.borrow_rates(LCFG, "tiered")
    assert rates.tolist() == [25.0, 75.0, 200.0, 200.0]
    assert CL.borrow_rates(LCFG).tolist() == [25.0] * 4
    w = np.array([-0.5, -0.3, 0.8]); z = np.zeros(3)
    a = CL.account_month(w, z, z, np.zeros(3, bool), z, z, np.ones(3), 1e8, 0.0, np.array([25.0, 200.0, 75.0]))
    assert a["borrow"] == pytest.approx((0.5 * 25 + 0.3 * 200) / 1e4 / 12)
    audit, *_ = panel
    res, meta = CL.run_layer(audit, METAS, CFG, LCFG, SHA, log=lambda *a: None,
                             rows=["layer", "layer_tiered_borrow", "layer_exec_half_month"])
    by = {(r, a): st for r, a, st in res}
    for aum in (1e8, 1e9, 5e9):
        base, tb, ex = by[("layer", aum)], by[("layer_tiered_borrow", aum)], by[("layer_exec_half_month", aum)]
        assert tb["cost_borrow_ann_pct"] > base["cost_borrow_ann_pct"]
        assert tb["borrow_mode"] == "tiered" and ex["trade_return_fraction"] == 0.5
        assert ex["gross_ann_return_pct"] != base["gross_ann_return_pct"]
        for st in (base, tb, ex):
            assert st["months_gross_exceeds_budget"] == 0
            assert "new_positions_delisting_n" in st and "new_positions_delisting_pnl_pct" in st
            assert st["unclassified_share_pct"] > 0


def test_halted_name_and_sector_leak_diagnostics():
    audit, d = _tiny_panel()
    P = CL.LayerPanel(audit, LCFG)
    R = [CL.RiskMonth(None, None, None, np.ones(P.offsets[m + 1] - P.offsets[m]), False, 0, False)
         for m in range(P.M)]
    # month 2: D (delisting) is INCREASED from its drifted weight, C held
    books = [(d[0], {"A", "B"}, {"C", "D"}), (d[1], {"A", "B"}, {"C", "D"}), (d[2], {"A"}, {"C"})]
    rec = CL.run_book(P, R, LCFG, [0, 1, 2], 1e8, CL.reference_decider(P, books), eta=0.0)
    assert [r["new_pos_delisting_n"] for r in rec] == [0, 1, 0]
    assert rec[1]["new_pos_delisting_pnl"] == pytest.approx(-0.5 * -0.30)
    st, _ = CL.summarise(rec, dict(LCFG), pipeline=False)
    assert st["new_positions_delisting_n"] == 1
    assert st["new_positions_delisting_pnl_pct"] == pytest.approx(0.15 / 3 * 12 * 100)
    leak = CL.LayerPanel(make_audit(200, 24, seed=3), LCFG).sector_leak()
    assert 0 < leak["unclassified_share_pct"] < 100
    assert leak["unclassified_share_min_year_pct"] <= leak["unclassified_share_pct"] <= leak["unclassified_share_max_year_pct"]
    assert {"delisted_share_unclassified_pct", "delisted_share_classified_pct"} <= set(leak)


def test_sigma_falls_back_to_tier_median_then_trailing_vol(panel):
    audit, P, R, _ = panel
    m = _book_month(P)
    sd = CL.daily_sigma(P, R, m, LCFG)
    assert np.allclose(sd, R[m].sigma / np.sqrt(21))
    R2 = list(R)
    sig = R[m].sigma.copy(); sig[:5] = np.nan
    R2[m] = CL.RiskMonth(R[m].X, R[m].F, R[m].D, sig, True, R[m].n_hist, True)
    sd2 = CL.daily_sigma(P, R2, m, LCFG)
    tier = P.tier[P.sl(m)]
    for i in range(5):
        assert sd2[i] == pytest.approx(np.median(sd[5:][tier[5:] == tier[i]]))
    early = next(k for k in range(P.M) if not R[k].ready and R[k].vol_ok)     # risk not ready, vol known
    assert np.all(np.isfinite(CL.daily_sigma(P, R, early, LCFG)))


@pytest.mark.parametrize("fill", ["finite", "nan"])
def test_poisoning_every_input_after_t_leaves_t_unchanged(fill):
    """cs_spread, adv_usd, mkt_cap_usd, ret_kind and monthly_ret for months
    strictly after t, poisoned with finite garbage or NaN: the market betas,
    the targets (every constraint set), the final weights, the costs and the
    Stage 3 books at t are unchanged."""
    audit = make_audit(n_names=200, n_months=34, seed=8)
    dates = sorted(audit["DATE"].unique())
    t_date = dates[27]
    bad = audit.copy()
    fut = bad["DATE"] > t_date
    rng = np.random.default_rng(1)
    k = int(fut.sum())
    for col, val in (("cs_spread", rng.uniform(0, 5, k)), ("adv_usd", rng.uniform(1, 1e12, k)),
                     ("mkt_cap_usd", rng.uniform(1, 1e13, k)), ("monthly_ret", rng.normal(3, 2, k))):
        bad.loc[fut, col] = np.nan if fill == "nan" else val
    bad["ret_kind"] = bad["ret_kind"].astype(object)
    bad.loc[fut, "ret_kind"] = np.nan if fill == "nan" else "partial_delisted_performance"

    def at_t(frame):
        P = CL.LayerPanel(frame, LCFG, METAS)
        R = CL.build_risk_model(P, LCFG)
        ic, _ = CL.ic_forecast(P, LCFG)
        m = int(np.searchsorted(P.dates.values, np.datetime64(t_date)))
        book = [j for j in range(P.M) if P.dates[j] >= pd.Timestamp("2001-01-01") and j <= m]
        out = {"m": m, "beta": P.market_betas(m)[0]}
        for c in ("sector_beta_neutral", "sector_neutral", "dollar_neutral"):
            T = {j: CL.build_target(P, R, j, ic[j], LCFG, c) for j in book}
            out[c] = T[m]["t"]
            seen = {}
            dec = CL.layer_decider(P, T, LCFG, 1e9)

            def spy(j, hU, dec=dec, seen=seen):
                w, dg = dec(j, hU)
                seen[j] = w.copy()
                return w, dg
            rec = CL.run_book(P, R, LCFG, book, 1e9, spy, 0.5)
            out[c + "_w"] = seen[m]
            out[c + "_cost"] = (rec[-1]["spread"], rec[-1]["impact"], rec[-1]["borrow"], rec[-1]["net"])
        for name in ("equal_rank_decile", "buffered"):
            bk = []
            getattr(PF, name)(frame, METAS, CFG, books=bk)
            got = {pd.Timestamp(dd): (L, S) for dd, L, S in bk}
            out[name] = got[pd.Timestamp(t_date)]
            rec = CL.run_book(P, R, LCFG, book, 1e9, CL.reference_decider(P, bk), 0.5)
            out[name + "_cost"] = (rec[-1]["spread"], rec[-1]["impact"], rec[-1]["borrow"], rec[-1]["net"])
        return out

    a, b = at_t(audit), at_t(bad)
    assert a["m"] == b["m"] == 27
    for k_ in a:
        if k_ == "m":
            continue
        if isinstance(a[k_], tuple) and isinstance(a[k_][0], set):
            assert a[k_] == b[k_], k_
        else:
            assert np.array_equal(np.asarray(a[k_]), np.asarray(b[k_])), k_


# ---- holdout readout (2026-09-27, before the holdout spend) ---------------------------

OOS = "2013-01-01"
_CUT_PREFIXES = ("cut_inwindow_", "cut_exyears_", "cut_2011_2020_")


@pytest.fixture(scope="module")
def holdout_pair():
    """A synthetic panel 2008-01..2013-12 run with a holdout from 2013-01, and
    the same panel truncated before 2013 (with and without a declared holdout).
    The book starts 2009-01, once 12 months of M exist for the beta constraint."""
    full = make_audit(n_names=150, n_months=72, start="2008-01-01", seed=21)
    trunc = full[full["DATE"] < pd.Timestamp(OOS)].copy()
    q = lambda *a: None  # noqa: E731
    lc = copy.deepcopy(LCFG)
    lc["window"].update({"book_start": "2009-01", "reference_rows_start": "2009-01"})
    r_full, m_full = CL.run_layer(full, METAS, CFG, lc, SHA, oos_start=OOS, log=q)
    r_tr, _ = CL.run_layer(trunc, METAS, CFG, lc, SHA, oos_start=OOS, log=q)
    r_none, _ = CL.run_layer(trunc, METAS, CFG, lc, SHA, oos_start=None, log=q)
    key = lambda res: {(r, a): st for r, a, st in res}  # noqa: E731
    return key(r_full), key(r_tr), key(r_none), m_full


def _same(a, b):
    if isinstance(a, float) and isinstance(b, float) and np.isnan(a) and np.isnan(b):
        return True
    return a == b


def test_in_window_fields_are_identical_with_and_without_the_holdout(holdout_pair):
    full, trunc, none, _ = holdout_pair
    assert full.keys() == trunc.keys() == none.keys()
    for k, st in full.items():
        assert st["cut_holdout_net_n_months"] == 12 and st["cut_inwindow_net_n_months"] == trunc[k]["n_months"]
        fields = [f for f in st if f.startswith(_CUT_PREFIXES)]
        assert len(fields) > 60
        for f in fields:
            assert _same(st[f], trunc[k][f]), (k, f, st[f], trunc[k][f])
            if not f.startswith("cut_inwindow_"):
                assert _same(st[f], none[k][f]), (k, f)
        # the in-window cut equals the truncated run's headline, field for field
        for f in [f for f in st if f.startswith("cut_inwindow_")]:
            h = f[len("cut_inwindow_"):]
            if h in none[k]:
                assert _same(st[f], none[k][h]), (k, f)
        for kind in ("gross", "net"):
            a = dict(x.split(":") for x in st[f"annual_{kind}_returns_pct"].split(","))
            b = dict(x.split(":") for x in none[k][f"annual_{kind}_returns_pct"].split(","))
            assert {y: v for y, v in a.items() if int(y) < 2013} == b
        # the ex-years cut is in-window only when a holdout is present
        assert st["cut_exyears_net_n_months"] == trunc[k]["cut_exyears_net_n_months"]


def test_each_cut_uses_only_its_own_months(holdout_pair):
    *_, meta = holdout_pair
    df = meta["paths"][("layer", 1e8)]
    rec = df.reset_index().to_dict("records")
    st0, _ = CL.summarise(rec, LCFG, 3, OOS)
    hold = df.index >= pd.Timestamp(OOS)
    bent = df.copy()
    for c in ("gross", "net", "spread", "impact", "borrow", "turnover"):
        bent.loc[~hold, c] = bent.loc[~hold, c] * 3 + 0.01
    bent.loc[~hold, "new_pos_delisting_n"] = 99
    st1, _ = CL.summarise(bent.reset_index().to_dict("records"), LCFG, 3, OOS)
    hold_fields = [f for f in st0 if f.startswith("cut_holdout_")]
    assert len(hold_fields) > 30
    for f in hold_fields:
        assert _same(st0[f], st1[f]), f
    assert st0["net_ann_return_pct"] != st1["net_ann_return_pct"]
    assert st0["cut_inwindow_net_ann_return_pct"] != st1["cut_inwindow_net_ann_return_pct"]
    # the cut's drawdown compounds from its own first month, peak floor 1.0 there
    dd = CL._drawdown(df.loc[hold, "net"])
    assert st0["cut_holdout_net_maxdd_pct"] == dd["maxdd_pct"]
    x = pd.Series([-0.10, 0.05, -0.02], index=pd.date_range("2023-01-31", periods=3, freq="ME"))
    d = CL._drawdown(x)
    assert d["maxdd_peak"] == "inception" and d["maxdd_trough"] == "2023-01-31"
    assert d["maxdd_pct"] == pytest.approx(-10.0)          # the first month's loss, from the 1.0 floor


def test_paths_csv_reproduces_the_annualised_returns(holdout_pair, tmp_path):
    full, _, _, meta = holdout_pair
    sha = CL.write_paths_csv(meta["paths"], tmp_path / "p.paths.csv")
    raw = (tmp_path / "p.paths.csv").read_bytes()
    assert sha == hashlib.sha256(raw).hexdigest()[:12]
    csv = pd.read_csv(tmp_path / "p.paths.csv", float_precision="round_trip")   # %.17g round-trips exactly
    assert list(csv.columns) == ["row", "aum_usd", "date"] + CL.PATH_COLUMNS
    assert len(csv) == sum(len(df) for df in meta["paths"].values())
    for (row, aum), st in full.items():
        sub = csv[(csv["row"] == row) & (csv["aum_usd"] == aum)]
        assert len(sub) == st["n_months"]
        assert sub["gross"].mean() * 12 * 100 == st["gross_ann_return_pct"]
        assert sub["net"].mean() * 12 * 100 == st["net_ann_return_pct"]
        hold = pd.to_datetime(sub["date"]) >= pd.Timestamp(OOS)
        assert sub.loc[hold.values, "net"].mean() * 1200 == pytest.approx(st["cut_holdout_net_ann_return_pct"], rel=1e-12)


# ---- D7 (2026-10-01): market-beta constraint, harness-built spread ------------------

def test_kkt_with_the_beta_column_equals_a_dense_solve():
    X, F, D, alpha, C, g = _random_risk()
    beta = np.random.default_rng(4).uniform(0.3, 1.8, len(alpha))
    Cb = np.hstack([C, beta[:, None]])
    Sigma = X @ F @ X.T + np.diag(D)
    n, k = Cb.shape
    K = np.block([[Sigma, Cb], [Cb.T, np.zeros((k, k))]])
    dense = np.linalg.solve(K, np.concatenate([alpha, np.zeros(k)]))[:n]
    w = CL.solve_neutral_mv(alpha, X, F, D, Cb)
    assert np.allclose(w, dense, rtol=1e-9, atol=1e-12)
    assert np.max(np.abs(Cb.T @ w)) < 1e-12
    # a beta column collinear with the dummies is a redundant constraint, not an error
    wc = CL.solve_neutral_mv(alpha, X, F, D, np.hstack([C, C @ np.arange(1.0, C.shape[1] + 1)[:, None]]))
    assert np.allclose(wc, CL.solve_neutral_mv(alpha, X, F, D, C), rtol=1e-8, atol=1e-12)


def test_constraint_projection_is_the_minimum_norm_move_of_the_free_names():
    rng = np.random.default_rng(12)
    n, G = 300, 7
    g = rng.integers(0, G, n)
    beta = rng.uniform(0.2, 2.0, n)
    w = rng.normal(0, 0.01, n)
    free = rng.random(n) < 0.7
    cons = CL.Constraint(g, G, beta[:, None])
    p = cons.project(w, free)
    assert cons.max_resid(p) <= 1e-15 and np.array_equal(p[~free], w[~free])
    # the closed form: delta_f = -A_f (A_f'A_f)^-1 A'w
    A = np.hstack([(g[:, None] == np.arange(G)[None, :]).astype(float), beta[:, None]])
    Af = A[free]
    dense = w.copy()
    dense[free] -= Af @ np.linalg.solve(Af.T @ Af, A.T @ w)
    assert np.allclose(p, dense, rtol=0, atol=1e-15)
    # without the beta column it IS project_neutral (the same arithmetic)
    assert np.array_equal(CL.Constraint(g, G).project(w, free), CL.project_neutral(w, g, G, free))
    assert np.array_equal(CL.Constraint(g, G).step(w, free) + w, CL.project_neutral(w, g, G, free))
    # a group with no free name keeps its residual; the beta row is still met
    free2 = free & (g != 0)
    p2 = cons.project(w, free2)
    r2 = cons.residual(p2)
    assert abs(r2[0] - np.sum(w[g == 0])) <= 1e-15 and np.max(np.abs(r2[1:])) <= 1e-15
    assert cons.bad_rows(p2, 1e-12).all() == False and cons.bad_rows(p2, 1e-12)[g == 0].all()  # noqa: E712


# The pre-D7 group-only step 2 and step 5, frozen here as the reference the
# generalised (constraint-matrix) code must reproduce exactly on a sector-only book.
def _old_apply_name_cap(w, groups, n_groups, floor, mult, tol, max_iter):
    gs = CL._group_sums
    w = np.asarray(w, dtype=float).copy()
    nL, nS = int((w > 0).sum()), int((w < 0).sum())
    capL = max(floor, mult / nL) if nL else floor
    capS = max(floor, mult / nS) if nS else floor
    caps = lambda x: np.where(x > 0, capL, np.where(x < 0, capS, min(capL, capS)))  # noqa: E731
    for it in range(1, int(max_iter) + 1):
        w = np.clip(w, -caps(w), caps(w))
        if np.max(np.abs(gs(w, groups, n_groups))) <= tol:
            break
        w = CL.project_neutral(w, groups, n_groups, np.abs(w) < caps(w) - tol)
        still = np.abs(gs(w, groups, n_groups)) > tol
        if still.any():
            w = CL.project_neutral(w, groups, n_groups, still[groups])
        if np.max(np.abs(w) - caps(w)) <= tol:
            break
    free = np.abs(w) < caps(w)
    return CL.project_neutral(w, groups, n_groups,
                              np.where(np.bincount(groups[free], minlength=n_groups)[groups] > 0, free, True))


def _old_exact(w, groups, n_groups, eligible, held, capd):
    pref = eligible & (np.abs(w - held) < capd * (1 - 1e-6))
    n_pref = np.bincount(groups[pref], minlength=n_groups)
    n_elig = np.bincount(groups[eligible], minlength=n_groups)
    members = np.where(n_pref[groups] > 0, pref, np.where(n_elig[groups] > 0, eligible, True))
    return CL.project_neutral(w, groups, n_groups, members)


def _old_neutralise(w, held, capd, groups, n_groups, eligible, tol, max_iter):
    gs = CL._group_sums
    w = w.copy()
    for _ in range(int(max_iter)):
        r = gs(w, groups, n_groups)
        bad = np.abs(r) > tol
        if not bad.any():
            return _old_exact(w, groups, n_groups, eligible, held, capd)
        need = -r[groups]
        d = w - held
        room = np.where(need > 0, capd - d, capd + d)
        room = np.where(eligible & bad[groups], np.maximum(room, 0.0), 0.0)
        free = room > 0
        nf = np.bincount(groups[free], minlength=n_groups)
        if not (nf[bad] > 0).any():
            break
        share = np.abs(r) / np.maximum(nf, 1)
        w = w + np.where(free, np.sign(need) * np.minimum(share[groups], room), 0.0)
    r = gs(w, groups, n_groups)
    bad = np.abs(r) > tol
    if not bad.any():
        return _old_exact(w, groups, n_groups, eligible, held, capd)
    ne = np.bincount(groups[eligible], minlength=n_groups)
    return CL.project_neutral(w, groups, n_groups, np.where(ne[groups] > 0, eligible, True) & bad[groups])


def _old_final_reproject(w, held, capd, groups, n_groups, eligible, gross_cap, tol, max_iter):
    for _ in range(int(max_iter)):
        w = _old_neutralise(w, held, capd, groups, n_groups, eligible, tol, max_iter)
        g = float(np.abs(w).sum())
        if g > gross_cap * (1 + 1e-12):
            w = w * (gross_cap / g)
        w, _ = CL.participation_cap(w, held, capd)
        if (np.max(np.abs(CL._group_sums(w, groups, n_groups))) <= tol
                and float(np.abs(w).sum()) <= gross_cap * (1 + 1e-9)):
            break
    w = _old_neutralise(w, held, capd, groups, n_groups, eligible, tol, max_iter)
    g = float(np.abs(w).sum())
    return w * (gross_cap / g) if g > gross_cap else w


def test_sector_only_book_is_unchanged_by_the_generalised_projection(panel):
    """layer_no_beta_constraint (sector_neutral) is the pre-D7 layer: the
    constraint-matrix steps 2 and 5 reproduce the group-only code bit for bit."""
    audit, P, R, ic_t = panel
    o = LCFG["optimiser"]
    rng = np.random.default_rng(3)
    book = [m for m in range(P.M) if P.dates[m] >= pd.Timestamp("2001-01-01")]
    for m in book[::3]:
        T = CL.build_target(P, R, m, abs(ic_t[m]) + 0.05, LCFG, "sector_neutral")
        I, g, G = T["eligible"], T["groups"], T["n_groups"]
        old2 = _old_apply_name_cap(T["w_step1"], g[I], G, o["name_cap_floor"], o["name_cap_mult"],
                                   o["cap_tol"], o["cap_max_iter"])
        assert np.array_equal(old2, T["t"][I])
        hU = T["cons"].project(T["t"] * 0.4 + rng.normal(0, 0.003, len(T["t"])) * I)
        for aum in (1e8, 5e10):
            capd = o["participation_pct"] / 100 * P.adv[P.sl(m)] * o["participation_days"] / aum
            w4, _ = CL.participation_cap(CL.buffer_step(T["t"], hU, o["buffer_rel"], o["buffer_abs"],
                                                        o["buffer_step"])[0], hU, capd)
            new, _ = CL.final_reproject(w4, hU, capd, T["cons"], I, T["G_t"], o["cap_tol"], o["cap_max_iter"])
            old = _old_final_reproject(w4, hU, capd, g, G, I, T["G_t"], o["cap_tol"], o["cap_max_iter"])
            assert np.array_equal(new, old), (m, aum)


def test_market_beta_is_analytics_trailing_beta_and_fills_from_the_sector_median(panel):
    from harness.analytics import trailing_beta, universe_market_return
    audit, P, R, _ = panel
    mkt = universe_market_return(audit).reindex(P.dates)
    assert np.allclose(P.mkt, mkt.to_numpy(), rtol=0, atol=1e-15)
    m = _book_month(P) + 5
    raw = CL.market_beta_raw(P, m)
    ids = P.id_code[P.sl(m)]
    checked = 0
    for j in range(0, len(ids), 7):
        y = pd.Series(P.RET[ids[j]], index=P.dates)          # the name on the panel's calendar (gaps NaN)
        tb = trailing_beta(y, mkt, P.beta_window, P.beta_min_obs).iloc[m]
        n_obs = int(np.isfinite(P.RET[ids[j], max(0, m - P.beta_window):m]).sum())
        if n_obs >= P.beta_min_obs:
            assert raw[j] == pytest.approx(tb, rel=1e-9, abs=1e-12)
            checked += 1
        else:
            assert np.isnan(raw[j]) and tb == 0.0             # trailing_beta's "no hedge" is "no estimate" here
    assert checked > 20
    # the estimate recovers the planted market loadings on average (uniform 0.4..1.6)
    assert 0.8 < np.nanmedian(raw) < 1.2
    beta, n_own = P.market_betas(m)
    valid = np.isfinite(raw)
    assert n_own == int(valid.sum()) and np.array_equal(beta[valid], raw[valid])
    g = P.sector[P.sl(m)]
    for j in np.flatnonzero(~valid)[:10]:
        assert beta[j] == np.median(raw[valid & (g == g[j])])
    # no estimate at all (the panel's first year): the constraint is dropped and counted
    T = CL.build_target(P, R, 3, 0.05, LCFG)
    assert T["beta"] is None and T["beta_dropped"] and T["cons"].extra is None
    # point in time: returns at and after t do not move beta_t
    bad = audit.copy()
    bad.loc[bad["DATE"] >= P.dates[m], "monthly_ret"] = 9.0
    assert np.array_equal(CL.LayerPanel(bad, LCFG, METAS).market_betas(m)[0], beta)


def test_realised_beta_on_the_market_is_reported_from_the_path(holdout_pair):
    from harness.analytics import fullwindow_beta
    full, _, _, meta = holdout_pair
    for (row, aum), st in full.items():
        df = meta["paths"][(row, aum)]
        assert st["net_beta_on_market"] == fullwindow_beta(df["net"], df["mkt"])
        hold = df.index >= pd.Timestamp(OOS)
        assert st["cut_holdout_net_beta_on_market"] == fullwindow_beta(df.loc[hold, "net"], df.loc[hold, "mkt"])
    # the beta-constrained book's ex-ante beta is zero every live month; the reference row's is not
    lay, ref = meta["paths"][("layer", 1e8)], meta["paths"][("layer_no_beta_constraint", 1e8)]
    live = ~lay["flat"].astype(bool)
    assert np.max(np.abs(lay.loc[live, "exp_beta"])) <= 1e-10
    assert np.mean(np.abs(ref.loc[live, "exp_beta"])) > 1e-4


# ---- the Corwin-Schultz series (data_layer) ------------------------------------------

def _candidate(name):
    spec = importlib.util.spec_from_file_location(f"cand_{name}", ROOT / "factors" / "candidates" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class _DailyCtx:
    """The two MonthContext accessors the BidAskSpread factor reads, over a
    synthetic daily frame."""

    def __init__(self, daily, signal_asof):
        self.d, self.signal_asof = daily, pd.Timestamp(signal_asof)

    def partial_months(self, table="SEP"):
        return frozenset()

    def daily(self, table, fields, days_back):
        start = self.signal_asof - pd.Timedelta(days=int(days_back))
        m = (self.d["date"] > start) & (self.d["date"] <= self.signal_asof)
        return self.d.loc[m, ["date"] + list(fields) + ["ID"]].copy()


def _synthetic_daily(seed=0, n_ids=12, start="2003-01-01", end="2004-06-30"):
    """Random-walk closes inside random high/low ranges, with every case the
    program screens: zero-volume days, high == low, a high/low > 8 print,
    overnight gaps outside the day's range, and a name that starts late."""
    rng = np.random.default_rng(seed)
    days = pd.bdate_range(start, end)
    rows = []
    for i in range(n_ids):
        d = days[rng.integers(0, 200):] if i == 0 else days
        d = d[rng.random(len(d)) > 0.03]                      # missing trading days
        px = 20 * np.exp(np.cumsum(rng.normal(0, 0.02, len(d))))
        half = px * rng.uniform(0.002, 0.03, len(d))
        hi, lo = px + half * rng.uniform(0.2, 1.5, len(d)), px - half * rng.uniform(0.2, 1.5, len(d))
        vol = rng.integers(1000, 100000, len(d)).astype(float)
        vol[rng.random(len(d)) < 0.05] = 0.0
        flat = rng.random(len(d)) < 0.04
        hi[flat] = lo[flat] = px[flat]
        if i == 1:
            hi[50] = lo[50] * 9.0                              # high/low > 8: dropped
        gap = rng.random(len(d)) < 0.05                        # close outside the day's range
        px = np.where(gap, hi * 1.01, px)
        rows.append(pd.DataFrame({"ID": f"{1000 + i}", "date": d, "high": hi, "low": lo, "close": px,
                                  "volume": vol}))
    daily = pd.concat(rows, ignore_index=True)
    return daily.sample(frac=1.0, random_state=seed).reset_index(drop=True)   # snapshot rows are unordered


def test_cs_spread_series_equals_the_bidaskspread_candidates_raw_value():
    from harness import data_layer as DL
    bas = _candidate("BidAskSpread")
    daily = _synthetic_daily()
    months = list(pd.date_range("2003-02-01", "2004-06-30", freq="BME"))
    cs = DL.cs_spread_monthly(daily, months)
    n_cmp = 0
    for s in months:
        raw = bas._compute(_DailyCtx(daily, s))
        got = cs[cs["me"] == s].set_index("ID")["cs_spread"]
        assert set(raw.index) == set(got.index), s
        r, h = raw.sort_index(), got.sort_index()
        assert np.array_equal(r.to_numpy(), h.to_numpy(), equal_nan=True), s      # bit for bit
        n_cmp += int(h.notna().sum())
    assert n_cmp > 150 and (cs["cs_spread"] > 0).mean() > 0.5
    # a partial month is not estimated; the signal date bounds the window (no later row is read)
    assert DL.cs_spread_monthly(daily, months[:1], frozenset({months[0].to_period("M")})).empty
    # point in time: rows dated AFTER the signal date but inside the same calendar
    # month (a weekend after a Friday month-end) are not read. 2003-08-29 is the
    # business month-end; extreme prints on 08-30/31 would move August's value
    # if the window ran to the calendar month-end.
    s = pd.Timestamp("2003-08-29")
    assert s in months and s + pd.offsets.BMonthEnd(0) == s and s.dayofweek == 4
    after = pd.DataFrame([{"ID": i, "date": d, "high": 30.0, "low": 20.0, "close": 25.0, "volume": 1e6}
                          for i in daily["ID"].unique() for d in (s + pd.Timedelta(days=1), s + pd.Timedelta(days=2))])
    poisoned = pd.concat([daily, after], ignore_index=True)
    a = cs[cs["me"] == s].reset_index(drop=True)
    b = DL.cs_spread_monthly(poisoned, [s])
    pd.testing.assert_frame_equal(a, b)
    # the test has power: a window that ran to the calendar month-end would read them
    leaky = DL.cs_spread_monthly(poisoned, [pd.Timestamp("2003-08-31")])
    lk = leaky.set_index("ID")["cs_spread"].reindex(a["ID"]).to_numpy()
    assert not np.allclose(lk, a["cs_spread"].to_numpy(), equal_nan=True)
    # the cost model charges half of it (floored at 1 bp)
    tier = np.zeros(len(h), dtype=np.int64)
    hs = CL.half_spreads(h.to_numpy(), tier, LCFG)
    ok = np.isfinite(h.to_numpy())
    assert np.array_equal(hs[ok], np.maximum(0.5 * h.to_numpy()[ok], 1e-4))


def test_cs_spread_attaches_on_the_signal_date_and_caches_on_data_sha(tmp_path, snap):
    from harness import data_layer as DL
    audit = make_audit(40, 5)
    cs = pd.DataFrame({"me": audit["SIGNAL_ASOF"], "ID": audit["ID"],
                       "cs_spread": np.arange(len(audit), dtype=float)})
    shuffled = cs.sample(frac=1.0, random_state=1)
    got = CL.attach_spread(audit.drop(columns=["cs_spread"]), shuffled)
    assert np.array_equal(got["cs_spread"].to_numpy(), np.arange(len(audit), dtype=float))
    # a name-month the series lacks stays NaN (half_spreads fills it from the tier-month median)
    assert CL.attach_spread(audit, shuffled.iloc[5:])["cs_spread"].isna().sum() == 5
    with pytest.raises(CL.LayerRefused):
        CL.attach_spread(audit, pd.concat([cs, cs.iloc[:1]]))
    k = DL.cs_spread_cache_key("abc")
    assert k == DL.cs_spread_cache_key("abc") and k != DL.cs_spread_cache_key("abd")
    rt = {"cache": {"dir": str(tmp_path), "enabled": True}}
    built = DL.load_or_build_cs_spread(snap, rt, "abc", root=tmp_path, log=lambda *a: None)
    assert (tmp_path / f"cs_spread_monthly_{k}.parquet").exists()
    hit = DL.load_or_build_cs_spread(snap, rt, "abc", root=tmp_path, log=lambda *a: None)
    pd.testing.assert_frame_equal(built, hit)
    assert list(built.columns) == ["me", "ID", "cs_spread", "cs_n_days"] and built["cs_spread"].notna().any()


# ---- alpha-review of 41edba9 (2026-10-01): ex-years, name-cap excess, guards --------

def test_exyears_cut_reports_declared_and_effective_years(panel, holdout_pair):
    idx = pd.date_range("2001-01-01", "2021-12-31", freq="BME")
    f = CL.exyears_fields(idx, LCFG)
    assert f == {"cut_exyears_declared": "2000,2001,2021", "cut_exyears_effective": "2001,2021", "cut_exyears_n": 2}
    # with a holdout from 2021-07 the in-window months still include 2021; from 2021-01 they do not
    assert CL.exyears_fields(idx, LCFG, "2021-07-01")["cut_exyears_effective"] == "2001,2021"
    assert CL.exyears_fields(idx, LCFG, "2021-01-01")["cut_exyears_effective"] == "2001"
    audit, P, R, _ = panel                                  # book 2001-01..2002-04
    res, _ = CL.run_layer(audit, METAS, CFG, LCFG, SHA, log=lambda *a: None, rows=["layer"])
    for _, _, st in res:
        assert st["cut_exyears_declared"] == "2000,2001,2021"
        assert st["cut_exyears_effective"] == "2001" and st["cut_exyears_n"] == 1
        assert st["cut_exyears_net_n_months"] == st["n_months"] - 12        # exactly 2001's months removed
        assert "cut_exyears_years" not in st
    full, *_ = holdout_pair                                 # 2008..2013: no declared year in the book
    for st in full.values():
        assert st["cut_exyears_effective"] == "none" and st["cut_exyears_n"] == 0
    buf = []
    CL.print_layer_table(res, log=buf.append)
    assert any("declared 2000,2001,2021 (D5 rule), effective 2001 (1 year(s)" in line for line in buf)


def test_name_cap_excess_is_measured_and_carried_to_the_summary(panel):
    # direct: every name at its cap, a beta residual only an over-cap move can fix
    w = np.array([0.01, 0.01, -0.01, -0.01])
    cons = CL.Constraint(np.zeros(4, dtype=np.int64), 1, np.array([[1.0], [1.0], [1.0], [10.0]]))
    w2, it, excess, resid = CL.apply_name_cap(w, cons, 0.01, 0.0, 1e-10, 1)
    assert resid <= 1e-12 and excess > 1e-3
    assert excess == pytest.approx(float(np.max(np.abs(w2) - 0.01)))
    # through the layer: a binding cap and a single clip-project pass leave excess in the target
    audit, P, R, ic_t = panel
    lcfg = copy.deepcopy(LCFG)
    lcfg["optimiser"].update({"name_cap_floor": 0.0, "name_cap_mult": 0.5, "cap_max_iter": 1})
    book = [m for m in range(P.M) if P.dates[m] >= pd.Timestamp("2001-01-01")]
    T = {m: CL.build_target(P, R, m, abs(ic_t[m]) + 0.05, lcfg) for m in book}
    rec = CL.run_book(P, R, lcfg, book, 1e8, CL.layer_decider(P, T, lcfg, 1e8), 0.5)
    st, _ = CL.summarise(rec, lcfg)
    want = [T[m]["name_cap_excess"] for m in book]
    assert st["name_cap_excess_max"] == max(want) > lcfg["optimiser"]["cap_tol"]
    assert st["name_cap_excess_months"] == sum(x > lcfg["optimiser"]["cap_tol"] for x in want) > 0
    # the declared config: no excess on the synthetic panel
    res, _ = CL.run_layer(audit, METAS, CFG, LCFG, SHA, log=lambda *a: None, rows=["layer"])
    for _, _, st0 in res:
        assert st0["name_cap_excess_months"] == 0 and st0["name_cap_excess_max"] <= LCFG["optimiser"]["cap_tol"]
    buf = []
    CL.print_layer_table(res, log=buf.append)
    assert any("capXsM" in line for line in buf)


def test_layer_refuses_a_spread_join_below_the_declared_floor():
    assert LCFG["costs"]["spread_measured_min_pct"] == 95.0
    audit = make_audit(n_names=150, n_months=30, seed=7)
    cs = pd.DataFrame({"me": audit["SIGNAL_ASOF"], "ID": audit["ID"], "cs_spread": 0.01})
    res, meta = CL.run_layer(audit, METAS, CFG, LCFG, SHA, log=lambda *a: None, rows=["layer"], spread=cs)
    assert meta["spread_measured_pct"] == 100.0
    # a series keyed on the wrong date (the holding month) joins nothing that month: refused
    wrong = cs.assign(me=pd.to_datetime(audit["SIGNAL_ASOF"]) + pd.offsets.Day(1))
    with pytest.raises(CL.LayerRefused, match="spread_measured_min_pct"):
        CL.run_layer(audit, METAS, CFG, LCFG, SHA, log=lambda *a: None, rows=["layer"], spread=wrong)
    # a thin series (half the names) is refused too; at the floor it runs
    book = pd.to_datetime(audit["DATE"]) >= pd.Timestamp("2001-01-01")
    thin = cs[~(book & (np.arange(len(cs)) % 2 == 0)).to_numpy()]
    with pytest.raises(CL.LayerRefused, match="below costs.spread_measured_min_pct = 95%"):
        CL.run_layer(audit, METAS, CFG, LCFG, SHA, log=lambda *a: None, rows=["layer"], spread=thin)
    lcfg = copy.deepcopy(LCFG)
    lcfg["costs"]["spread_measured_min_pct"] = 40.0
    CL.run_layer(audit, METAS, CFG, lcfg, SHA, log=lambda *a: None, rows=["layer"], spread=thin)


def test_layer_refuses_a_book_month_without_a_market_beta():
    late = make_audit(n_names=150, n_months=30, start="2000-06-01", seed=9)    # M from 2000-06: beta from 2001-06
    with pytest.raises(CL.LayerRefused, match=r"no estimate in 5 book month\(s\) from 2001-01"):
        CL.run_layer(late, METAS, CFG, LCFG, SHA, log=lambda *a: None, rows=["layer"])
    # rows that do not use the beta constraint are not refused
    CL.run_layer(late, METAS, CFG, LCFG, SHA, log=lambda *a: None, rows=["layer_no_beta_constraint"])
    ok = make_audit(n_names=150, n_months=30, start="1999-06-01", seed=9)       # beta from 2000-06
    res, _ = CL.run_layer(ok, METAS, CFG, LCFG, SHA, log=lambda *a: None, rows=["layer"])
    assert all(st["beta_constraint_dropped_months"] == 0 for _, _, st in res)
