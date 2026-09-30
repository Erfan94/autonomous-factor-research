"""
Monthly market series rebuilt from the daily name-days: the Pastor-Stambaugh
aggregate liquidity innovation (build_ps_innov_monthly,
MonthContext.monthly_ps_innov) and the Kelly-Jiang tail-risk factor
(build_tailex_monthly, MonthContext.monthly_tailex), against the synthetic
snapshot and against hand-built inputs to the pure steps. In the fixture the
even-indexed names (and PERF, LATE, TINY) are NYSE, the odd ones NASDAQ;
every name trades every business day with positive volume, no splits.
"""
import shutil

import numpy as np
import pandas as pd
import pytest

import harness.data_layer as DL
from harness.data_layer import (MonthContext, PanelIndex, Snapshot, _series_name_days,
                                build_market_daily, build_ps_innov_monthly, build_tailex_monthly,
                                build_universe, ff3_cache_key, load_or_build_ps,
                                load_or_build_tailex, market_cache_key, ps_aggregate,
                                ps_cache_key, ps_gamma_from_pairs, ps_innovations,
                                ps_exchange_asof, ps_refit_residuals, ps_stock_months,
                                sha256_file, tailex_cache_key, tailex_from_pool, to_bme)

QUIET = dict(log=lambda *a, **k: None)
FIXTURE_MIN_NAMES = 20      # the fixture holds ~47 NYSE names; the real floor is 100


@pytest.fixture(scope="module", autouse=True)
def _fixture_sized_min_names():
    """PS_MIN_NAMES (100) would blank every fixture month; the rule itself is
    tested with hand frames and once at full size."""
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(DL, "PS_MIN_NAMES", FIXTURE_MIN_NAMES)
        yield


# ---- fixtures and helpers ------------------------------------------------------------

@pytest.fixture(scope="module")
def ps(snap, cfg):
    return build_ps_innov_monthly(snap, cfg, **QUIET)


@pytest.fixture(scope="module")
def tx(snap, cfg):
    return build_tailex_monthly(snap, cfg, **QUIET)


@pytest.fixture(scope="module")
def stock_months(snap, cfg):
    return ps_stock_months(snap, cfg)[0]


@pytest.fixture(scope="module")
def spidx(panel, snap, cfg, ps, tx):
    p = PanelIndex(panel, snap, cfg)
    p.set_ps_loader(lambda: ps)
    p.set_tailex_loader(lambda: tx)
    return p


def _rehash(root, manifest):
    m = dict(manifest)
    m["tables"] = {k: dict(v) for k, v in m["tables"].items()}
    for t in m["tables"]:
        m["tables"][t]["sha256"] = sha256_file(root / "sharadar" / m["tables"][t]["file"])
    return Snapshot(root / "sharadar", m, verify_hashes=True)


def _edited(synthetic, tmp_path, edit):
    root = tmp_path / "copy"
    shutil.copytree(synthetic["root"], root)
    edit(root / "sharadar")
    return _rehash(root, synthetic["manifest"])


def _cut_after(day):
    def edit(d):
        for t in ("SEP", "DAILY"):
            x = pd.read_parquet(d / f"{t}.parquet")
            x[x["date"] <= day].to_parquet(d / f"{t}.parquet", index=False)
    return edit


def _ctx(snap, pidx, cfg, asof):
    u = build_universe(pidx, pd.Timestamp(asof), cfg)
    return MonthContext(snap, pidx, u, pd.Timestamp(asof), cfg, {})


def _id(synthetic, ticker):
    return str(synthetic["perma"][ticker])


def _bme(s):
    return to_bme([pd.Timestamp(s)]).iloc[0]


# ---- shared name-days ------------------------------------------------------------------

def test_series_name_days_ok_rows_are_the_market_series_exactly(snap, cfg):
    nd = _series_name_days(snap, cfg)
    mkt = build_market_daily(snap, cfg, **QUIET)
    got = DL._vw_market_from_name_days(nd)
    assert got.index.equals(mkt.index)
    pd.testing.assert_series_equal(got, mkt["mkt_ret"], check_names=False, check_exact=True)
    # The return guards are a superset of the market's rows (no weight guard).
    assert (nd["clean"] | ~nd["ok"]).all()
    assert nd["clean"].sum() >= nd["ok"].sum()


# ---- PS: per-stock gamma -----------------------------------------------------------------

def _pairs_from_model(gammas, n_obs=21, noise=0.0, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for i, (sid, g) in enumerate(gammas.items()):
        for m in (pd.Timestamp("2000-01-31"), pd.Timestamp("2000-02-29")):
            x1 = rng.normal(0, 0.02, n_obs)
            x2 = rng.choice([-1.0, 1.0], n_obs) * rng.uniform(0.5, 20.0, n_obs)
            theta, phi = 0.001 * (i + 1), -0.1 * (i + 1)
            y = theta + phi * x1 + g * x2 + noise * rng.normal(size=n_obs)
            rows.append(pd.DataFrame({"ID": sid, "month": m, "y": y, "x1": x1, "x2": x2}))
    return pd.concat(rows, ignore_index=True)


def test_ps_gamma_recovers_a_known_gamma_per_stock():
    gammas = {"A": -0.02, "B": 0.0, "C": 0.005, "D": -0.5}
    got = ps_gamma_from_pairs(_pairs_from_model(gammas))
    for sid, g in gammas.items():
        for m in got.loc[sid].index:
            assert got.loc[(sid, m), "gamma"] == pytest.approx(g, abs=1e-12)
            assert got.loc[(sid, m), "n_obs"] == 21
    # With noise it is the OLS coefficient, exactly np.linalg.lstsq's.
    pairs = _pairs_from_model(gammas, noise=0.01, seed=3)
    got = ps_gamma_from_pairs(pairs)
    for (sid, m), grp in pairs.groupby(["ID", "month"]):
        X = np.column_stack([np.ones(len(grp)), grp["x1"], grp["x2"]])
        coef = np.linalg.lstsq(X, grp["y"].to_numpy(), rcond=None)[0]
        assert got.loc[(sid, m), "gamma"] == pytest.approx(coef[2], rel=1e-9, abs=1e-12)
        assert got.loc[(sid, m), "phi"] == pytest.approx(coef[1], rel=1e-9, abs=1e-12)


def test_ps_gamma_is_nan_for_a_degenerate_regression():
    p = _pairs_from_model({"A": 0.01, "B": 0.01})
    p.loc[p["ID"] == "A", "x2"] = 3.0                       # no variance
    p.loc[p["ID"] == "B", "x2"] = 2.0 * p.loc[p["ID"] == "B", "x1"] + 1.0   # collinear
    got = ps_gamma_from_pairs(p)
    assert got["gamma"].isna().all()


def test_ps_builder_gamma_matches_a_hand_regression_on_the_raw_parquet(snap, cfg, stock_months, synthetic):
    """The builder's pairs: consecutive market days in the month, y = r^e_{d+1},
    x1 = r_d, x2 = sign(r^e_d) close_d volume_d / 1e6, r^e = r - the VW market."""
    sep = pd.read_parquet(snap.path("SEP"))
    mkt = build_market_daily(snap, cfg, **QUIET)["mkt_ret"]
    for tk, month in [("T000", "2000-03-31"), ("T010", "1999-11-30")]:
        s = sep[sep["ticker"] == tk].sort_values("date").set_index("date")
        r = s["closeadj"] / s["closeadj"].shift(1) - 1.0
        me = pd.Timestamp(month)
        days = [d for d in s.index if to_bme([d]).iloc[0] == me]
        re = r - mkt.reindex(r.index)
        ys, x1, x2 = [], [], []
        for d0, d1 in zip(days[:-1], days[1:]):
            ys.append(re[d1])
            x1.append(r[d0])
            x2.append(np.sign(re[d0]) * s.loc[d0, "close"] * s.loc[d0, "volume"] / 1e6)
        X = np.column_stack([np.ones(len(ys)), x1, x2])
        coef = np.linalg.lstsq(X, np.array(ys), rcond=None)[0]
        row = stock_months[(stock_months["ID"] == _id(synthetic, tk)) & (stock_months["month"] == me)]
        assert len(row) == 1
        assert int(row["n_obs"].iloc[0]) == len(ys) == len(days) - 1
        assert row["gamma"].iloc[0] == pytest.approx(coef[2], rel=1e-8)


# ---- PS: aggregation, by hand ------------------------------------------------------------

def test_ps_aggregation_reproduces_a_hand_computation():
    m1, m2, m3 = pd.Timestamp("2000-01-31"), pd.Timestamp("2000-02-29"), pd.Timestamp("2000-03-31")
    # A in all three months, B in months 1-2, C in months 2-3.
    elig = pd.DataFrame([
        ("A", m1, 0.10, 100.0), ("B", m1, 0.30, 300.0),
        ("A", m2, 0.20, 110.0), ("B", m2, 0.10, 290.0), ("C", m2, 0.50, 50.0),
        ("A", m3, 0.05, 120.0), ("C", m3, 0.80, 60.0),
    ], columns=["ID", "month", "gamma", "cap_prev"])
    got = ps_aggregate(elig, min_names=1)
    assert list(got.index) == [m1, m2, m3]
    assert got["gamma_hat"].tolist() == pytest.approx([0.20, 0.80 / 3, 0.425])
    assert got["m_usd"].tolist() == pytest.approx([400.0, 450.0, 180.0])
    assert got["m_scale"].tolist() == pytest.approx([1.0, 450.0 / 400.0, 180.0 / 400.0])
    assert got["n_eligible"].tolist() == [2, 3, 2]
    assert got["n_both"].tolist() == [0, 2, 2]
    # Month 2: A +0.10, B -0.20 -> mean -0.05; month 3: A -0.15, C +0.30 -> +0.075.
    assert np.isnan(got["dgamma"].iloc[0])
    assert got["dgamma"].iloc[1] == pytest.approx(450.0 / 400.0 * -0.05)
    assert got["dgamma"].iloc[2] == pytest.approx(180.0 / 400.0 * 0.075)


def test_ps_aggregation_index_is_contiguous_across_an_empty_month():
    elig = pd.DataFrame([("A", pd.Timestamp("2000-01-31"), 0.1, 1.0),
                         ("A", pd.Timestamp("2000-03-31"), 0.2, 1.0)],
                        columns=["ID", "month", "gamma", "cap_prev"])
    got = ps_aggregate(elig, min_names=1)
    assert list(got.index) == [pd.Timestamp("2000-01-31"), pd.Timestamp("2000-02-29"),
                               pd.Timestamp("2000-03-31")]
    assert got["n_eligible"].tolist() == [1, 0, 1]
    assert got["dgamma"].isna().all()                     # no name in both t and t-1


# ---- PS: the expanding-window innovation ------------------------------------------------

def _agg(n=60, seed=1):
    rng = np.random.default_rng(seed)
    idx = pd.DatetimeIndex(to_bme(pd.period_range("2000-01", periods=n, freq="M")
                                  .to_timestamp(how="start")).to_numpy(), name="me")
    return pd.DataFrame({"gamma_hat": rng.normal(-0.02, 0.01, n),
                         "m_scale": np.linspace(1.0, 2.0, n),
                         "dgamma": rng.normal(0, 0.01, n)}, index=idx)


def test_ps_innovation_is_the_expanding_residual_at_t():
    agg = _agg()
    got = ps_innovations(agg, min_months=24)
    y = agg["dgamma"].to_numpy()
    lvl = (agg["m_scale"] * agg["gamma_hat"]).to_numpy()
    rows = list(range(1, len(y)))                      # month 0 has no lag
    assert got["ps_innov"].iloc[:24].isna().all()      # 23 regression months through index 23
    assert got["ps_innov"].iloc[24:].notna().all()
    for t in (24, 40, 59):
        use = [k for k in rows if k <= t]
        X = np.column_stack([np.ones(len(use)), y[[k - 1 for k in use]], lvl[[k - 1 for k in use]]])
        b = np.linalg.lstsq(X, y[use], rcond=None)[0]
        want = (y[t] - X[-1] @ b) / 100.0
        assert got["ps_innov"].iloc[t] == pytest.approx(want, rel=1e-10, abs=1e-15)
        assert got["n_fit"].iloc[t] == len(use)


def test_ps_innovation_at_t_does_not_move_when_later_months_are_appended():
    agg = _agg(n=80)
    full = ps_innovations(agg)
    for cut in (30, 45, 79):
        trunc = ps_innovations(agg.iloc[:cut + 1])
        pd.testing.assert_frame_equal(full.iloc[:cut + 1], trunc, check_exact=True)
    # A wild later month changes nothing before it.
    wild = agg.copy()
    wild.iloc[60:, wild.columns.get_loc("dgamma")] *= 1e3
    pd.testing.assert_frame_equal(ps_innovations(wild).iloc[:60], full.iloc[:60], check_exact=True)


def test_ps_innovation_refuses_a_non_contiguous_index():
    agg = _agg(n=30).drop(index=_agg(n=30).index[10])
    with pytest.raises(RuntimeError, match="contiguous"):
        ps_innovations(agg)


@pytest.mark.parametrize("cut", ["1996-06-28", "1998-12-31"])
def test_ps_builder_is_causal_no_value_moves_when_later_rows_are_deleted(synthetic, cfg, ps, tmp_path, cut):
    cut = pd.Timestamp(cut)
    snap2 = _edited(synthetic, tmp_path, _cut_after(cut))
    trunc = build_ps_innov_monthly(snap2, cfg, **QUIET)
    assert trunc.index.max() == cut and ps.index.max() > cut
    assert trunc["ps_innov"].notna().sum() > 10
    pd.testing.assert_frame_equal(ps.loc[ps.index <= cut], trunc, check_exact=True)


# ---- PS: eligibility -------------------------------------------------------------------------

def test_ps_exchange_filter_keeps_only_nyse_and_amex(snap, stock_months, synthetic, cfg):
    meta = snap.ticker_meta()
    ids = set(stock_months["ID"])
    assert ids == set(meta.index[meta["exchange"].isin(["NYSE", "NYSEMKT"])])
    assert _id(synthetic, "T001") not in ids              # NASDAQ, otherwise a clean name


def test_ps_amex_names_are_in(synthetic, cfg, tmp_path):
    def edit(d):
        tk = pd.read_parquet(d / "TICKERS.parquet")
        tk.loc[tk["ticker"] == "T001", "exchange"] = "NYSEMKT"
        tk.to_parquet(d / "TICKERS.parquet", index=False)
    snap2 = _edited(synthetic, tmp_path, edit)
    sm, _ = ps_stock_months(snap2, cfg)
    t1 = sm[sm["ID"] == _id(synthetic, "T001")]
    assert len(t1) > 100 and t1["eligible"].mean() > 0.95


def test_ps_short_months_and_first_months_are_ineligible(stock_months, synthetic):
    sm = stock_months.set_index(["ID", "month"])
    perf = _id(synthetic, "PERF")                       # stops trading 1999-09-15
    assert sm.loc[(perf, _bme("1999-08-31")), "eligible"]
    assert sm.loc[(perf, _bme("1999-09-30")), "n_days"] < 15
    assert np.isfinite(sm.loc[(perf, _bme("1999-09-30")), "gamma"])    # identified, still out
    assert not sm.loc[(perf, _bme("1999-09-30")), "eligible"]
    late = _id(synthetic, "LATE")                       # first trades 1999-07-01
    assert not sm.loc[(late, _bme("1999-07-31")), "eligible"]    # no month t-1 row
    assert np.isnan(sm.loc[(late, _bme("1999-07-31")), "px_prev"])
    assert sm.loc[(late, _bme("1999-08-31")), "eligible"]


def test_ps_a_fifteen_trading_day_month_is_eligible(synthetic, cfg, tmp_path):
    """The 2001-09 shape (markets shut for a week): April 2000 has 20 trading
    days in the fixture; deleting 10-14 April for every name leaves 15 days,
    15 valid returns and 14 pairs. The rule counts returns, so the month is
    kept; the return on the 17th runs from the 7th (the previous MARKET day)."""
    def edit(d):
        for t in ("SEP", "DAILY"):
            x = pd.read_parquet(d / f"{t}.parquet")
            gone = (x["date"] >= pd.Timestamp("2000-04-10")) & (x["date"] <= pd.Timestamp("2000-04-14"))
            x[~gone].to_parquet(d / f"{t}.parquet", index=False)
    snap2 = _edited(synthetic, tmp_path, edit)
    sm2 = ps_stock_months(snap2, cfg)[0]
    apr = sm2[sm2["month"] == pd.Timestamp("2000-04-28")]
    t0 = apr[apr["ID"] == _id(synthetic, "T000")].iloc[0]
    assert (t0["n_days"], t0["n_obs"]) == (15, 14)
    assert t0["eligible"] and apr["eligible"].mean() > 0.9


def test_ps_price_filter_bites_on_the_unadjusted_price(synthetic, cfg, stock_months, tmp_path):
    """closeunadj < $5 or > $1000 at the end of t-1 excludes the name in t;
    closeadj (and so every return and gamma) is untouched by the edit."""
    lo = (pd.Timestamp("1997-01-01"), pd.Timestamp("1997-06-30"))

    def edit(d):
        sp = pd.read_parquet(d / "SEP.parquet")
        w = (sp["date"] >= lo[0]) & (sp["date"] <= lo[1])
        sp.loc[w & (sp["ticker"] == "T000"), "closeunadj"] = 4.99
        sp.loc[w & (sp["ticker"] == "T002"), "closeunadj"] = 1000.01
        sp.loc[w & (sp["ticker"] == "T004"), "closeunadj"] = 1000.0     # the bound is inclusive
        sp.to_parquet(d / "SEP.parquet", index=False)
    snap2 = _edited(synthetic, tmp_path, edit)
    sm2 = ps_stock_months(snap2, cfg)[0].set_index(["ID", "month"])
    base = stock_months.set_index(["ID", "month"])
    hit = [_bme(m) for m in ("1997-02-28", "1997-04-30", "1997-07-31")]   # t-1 inside the window
    for tk, want in [("T000", False), ("T002", False), ("T004", True)]:
        for m in hit:
            assert bool(sm2.loc[(_id(synthetic, tk), m), "eligible"]) is want, (tk, m)
            assert base.loc[(_id(synthetic, tk), m), "eligible"]
    # The month after the window reads a normal t-1 price again.
    assert sm2.loc[(_id(synthetic, "T000"), _bme("1997-08-29")), "eligible"]
    pd.testing.assert_series_equal(sm2["gamma"], base["gamma"], check_exact=True)


def test_ps_market_value_is_the_t_minus_1_cap_of_the_averaged_set(ps, stock_months):
    e = stock_months[stock_months["eligible"]]
    m = pd.Timestamp("2000-03-31")
    em = e[e["month"] == m]
    assert ps.loc[m, "n_eligible"] == len(em)
    assert ps.loc[m, "m_usd"] == pytest.approx(em["cap_prev"].sum(), rel=1e-12)
    assert ps.loc[m, "gamma_hat"] == pytest.approx(em["gamma"].mean(), rel=1e-12)
    assert ps["m_scale"].iloc[0] == 1.0


def test_ps_drops_no_trade_days_and_spikes(synthetic, cfg, stock_months, tmp_path):
    """A zero-volume day removes the two pairs it touches; a -85% print and
    its reversal the next day are dropped by the market's guards."""
    zero, crash = pd.Timestamp("2000-03-15"), pd.Timestamp("2000-05-16")

    def edit(d):
        sp = pd.read_parquet(d / "SEP.parquet")
        sp.loc[(sp["ticker"] == "T000") & (sp["date"] == zero), "volume"] = 0
        c = (sp["ticker"] == "T002") & (sp["date"] == crash)
        sp.loc[c, "closeadj"] *= 0.15
        sp.to_parquet(d / "SEP.parquet", index=False)
    snap2 = _edited(synthetic, tmp_path, edit)
    sm2 = ps_stock_months(snap2, cfg)[0].set_index(["ID", "month"])
    base = stock_months.set_index(["ID", "month"])
    k0 = (_id(synthetic, "T000"), _bme("2000-03-31"))
    assert sm2.loc[k0, "n_obs"] == base.loc[k0, "n_obs"] - 2
    k2 = (_id(synthetic, "T002"), _bme("2000-05-31"))
    # crash day and its reversal each lose the pairs they are in: 3 pairs.
    assert sm2.loc[k2, "n_obs"] == base.loc[k2, "n_obs"] - 3


# ---- PS: the accessor ------------------------------------------------------------------------

def test_monthly_ps_innov_is_bounded_by_the_signal_month(snap, spidx, cfg, ps):
    ctx = _ctx(snap, spidx, cfg, "1997-06-30")
    got = ctx.monthly_ps_innov(12)
    assert ps.index.max() > pd.Timestamp("1997-06-30")            # later months exist to leak
    assert len(got) == 12 and got.index.max() == pd.Timestamp("1997-06-30")
    assert got.index.is_monotonic_increasing
    pd.testing.assert_series_equal(got, ps["ps_innov"].reindex(got.index).astype(float),
                                   check_names=False)
    # Before the series is defined: NaN, never a later value.
    first = ps["ps_innov"].first_valid_index()
    early = _ctx(snap, spidx, cfg, "1993-12-31").monthly_ps_innov(36)
    assert early.index.max() == pd.Timestamp("1993-12-31") < first
    assert early.isna().all()
    # A frame whose later months are wild is read identically up to the signal.
    wild = ps.copy()
    wild.loc[wild.index > pd.Timestamp("1997-06-30"), "ps_innov"] = 1e9
    p2 = PanelIndex(spidx.panel, snap, cfg)
    p2.set_ps_loader(lambda: wild)
    pd.testing.assert_series_equal(_ctx(snap, p2, cfg, "1997-06-30").monthly_ps_innov(12), got)


# ---- tailex: the pure statistic ---------------------------------------------------------------

def test_tailex_equals_a_hand_computation():
    m = pd.Timestamp("2000-01-31")
    r = np.array([-0.10, -0.05, -0.20, 0.01, 0.02, 0.0, 0.03, -0.01, 0.04, 0.05,
                  -0.02, 0.06, 0.07, 0.01, -0.03, 0.02, 0.03, 0.08, 0.00, -0.04, 0.09])
    got = tailex_from_pool([m] * len(r), r)
    # n = 21: floor(20 x 0.05) = 1 -> the second smallest, -0.10.
    assert got.loc[m, "retp5"] == -0.10
    want = np.mean([np.log(-0.20 / -0.10), np.log(-0.10 / -0.10)])
    assert got.loc[m, "tailex"] == pytest.approx(want, rel=1e-15)
    assert got.loc[m, "n_tail"] == 2 and got.loc[m, "n_pooled"] == 21


def test_tailex_quantile_is_the_lower_interpolation():
    rng = np.random.default_rng(7)
    for n in list(range(1, 90)) + [1000, 12345]:
        x = rng.normal(0, 0.03, n)
        got = tailex_from_pool([pd.Timestamp("2000-01-31")] * n, x)
        assert got["retp5"].iloc[0] == np.quantile(x, 0.05, method="lower"), n
    x = np.arange(30, dtype=float) - 100.0                 # n = 30: floor(29 x .05) = 1
    got = tailex_from_pool([pd.Timestamp("2000-01-31")] * 30, x)
    assert got["retp5"].iloc[0] == -99.0


def test_tailex_is_nan_when_the_percentile_is_not_negative():
    x = np.r_[0.0, 0.0, np.linspace(0.01, 0.1, 38)]      # n = 40: the 2nd smallest is 0
    got = tailex_from_pool([pd.Timestamp("2000-01-31")] * 40, x)
    assert got["retp5"].iloc[0] == 0.0 and np.isnan(got["tailex"].iloc[0])
    got = tailex_from_pool([pd.Timestamp("2000-01-31")] * 40, x + 0.001)
    assert got["retp5"].iloc[0] > 0 and np.isnan(got["tailex"].iloc[0])


def test_tailex_months_are_independent():
    a, b = pd.Timestamp("2000-01-31"), pd.Timestamp("2000-02-29")
    rng = np.random.default_rng(0)
    ra, rb = rng.normal(0, 0.02, 300), rng.normal(0, 0.05, 500)
    both = tailex_from_pool([a] * 300 + [b] * 500, np.r_[ra, rb])
    pd.testing.assert_frame_equal(both.loc[[a]], tailex_from_pool([a] * 300, ra))
    pd.testing.assert_frame_equal(both.loc[[b]], tailex_from_pool([b] * 500, rb))


# ---- tailex: the builder -----------------------------------------------------------------------

def test_tailex_builder_matches_a_hand_pool_on_the_raw_parquet(snap, cfg, tx):
    sep = pd.read_parquet(snap.path("SEP")).sort_values(["ticker", "date"])
    sep["r"] = sep.groupby("ticker")["closeadj"].transform(lambda s: s / s.shift(1) - 1.0)
    for month in ("1996-02-29", "2000-03-31"):
        me = pd.Timestamp(month)
        pool = sep[(to_bme(sep["date"]).to_numpy() == me.to_datetime64()) & sep["r"].notna()]["r"]
        p5 = np.quantile(pool.to_numpy(), 0.05, method="lower")
        tail = pool[pool <= p5]
        assert tx.loc[me, "n_pooled"] == len(pool)
        assert tx.loc[me, "retp5"] == p5
        assert tx.loc[me, "tailex"] == pytest.approx(np.log(tail / p5).mean(), rel=1e-12)


def test_tailex_first_month_is_blank_and_later_ones_complete(tx):
    first = pd.Timestamp("1992-01-31")                    # SEP starts 1992-01-01
    assert tx.index.min() == first and np.isnan(tx.loc[first, "tailex"])
    assert tx["tailex"].iloc[1:].notna().all()
    assert (tx["n_days"].iloc[1:] >= DL.TAIL_MIN_DAYS).all()


def test_tailex_drops_spikes_and_no_trade_days_from_the_pool(synthetic, cfg, tx, tmp_path):
    crash, zero = pd.Timestamp("2000-05-16"), pd.Timestamp("2000-05-18")

    def edit(d):
        sp = pd.read_parquet(d / "SEP.parquet")
        c = (sp["ticker"] == "T002") & (sp["date"] == crash)
        sp.loc[c, "closeadj"] *= 0.15                   # -85% then +567%: both guarded out
        sp.loc[(sp["ticker"] == "T003") & (sp["date"] == zero), "volume"] = 0
        sp.to_parquet(d / "SEP.parquet", index=False)
    snap2 = _edited(synthetic, tmp_path, edit)
    t2 = build_tailex_monthly(snap2, cfg, **QUIET)
    me = pd.Timestamp("2000-05-31")
    assert t2.loc[me, "n_pooled"] == tx.loc[me, "n_pooled"] - 3
    assert t2.loc[me, "retp5"] > -0.5                     # the crash is not in the tail


@pytest.mark.parametrize("cut", ["1996-06-28", "2000-03-31"])
def test_tailex_builder_is_causal(synthetic, cfg, tx, tmp_path, cut):
    cut = pd.Timestamp(cut)
    snap2 = _edited(synthetic, tmp_path, _cut_after(cut))
    trunc = build_tailex_monthly(snap2, cfg, **QUIET)
    assert trunc.index.max() == cut and tx.index.max() > cut
    pd.testing.assert_frame_equal(tx.loc[tx.index <= cut], trunc, check_exact=True)


def test_monthly_tailex_is_bounded_by_the_signal_month(snap, spidx, cfg, tx):
    ctx = _ctx(snap, spidx, cfg, "1999-06-30")
    got = ctx.monthly_tailex(24)
    assert len(got) == 24 and got.index.max() == pd.Timestamp("1999-06-30")
    assert tx.index.max() > pd.Timestamp("1999-06-30")
    pd.testing.assert_series_equal(got, tx["tailex"].reindex(got.index), check_names=False)
    # The window reaching before the series: NaN there, values after.
    early = _ctx(snap, spidx, cfg, "1992-06-30").monthly_tailex(12)
    assert early.index.max() == pd.Timestamp("1992-06-30")
    assert early.loc[:pd.Timestamp("1992-01-31")].isna().all()
    assert early.loc[pd.Timestamp("1992-02-28"):].notna().all()
    wild = tx.copy()
    wild.loc[wild.index > pd.Timestamp("1999-06-30"), "tailex"] = 1e9
    p2 = PanelIndex(spidx.panel, snap, cfg)
    p2.set_tailex_loader(lambda: wild)
    pd.testing.assert_series_equal(_ctx(snap, p2, cfg, "1999-06-30").monthly_tailex(24), got)


# ---- loaders and cache -----------------------------------------------------------------------------

def test_series_loaders_are_called_once_and_only_on_demand(panel, snap, cfg, ps, tx):
    calls = []
    p = PanelIndex(panel, snap, cfg)
    p.set_ps_loader(lambda: calls.append("ps") or ps)
    p.set_tailex_loader(lambda: calls.append("tx") or tx)
    ctx = _ctx(snap, p, cfg, "2000-06-30")
    ctx.market_context()
    assert calls == []
    ctx.monthly_ps_innov(12)
    ctx.monthly_ps_innov(24)
    assert calls == ["ps"]
    ctx.monthly_tailex(12)
    ctx.monthly_tailex(6)
    assert calls == ["ps", "tx"]


def test_series_cache_keys_move_with_data_config_and_source(cfg, monkeypatch):
    kp, kt = ps_cache_key("abc", cfg), tailex_cache_key("abc", cfg)
    assert kp == ps_cache_key("abc", cfg) and kt == tailex_cache_key("abc", cfg)
    assert kp != ps_cache_key("abd", cfg) and kt != tailex_cache_key("abd", cfg)
    assert len({kp, kt, ff3_cache_key("abc", cfg), market_cache_key("abc", cfg)}) == 4
    c2 = {**cfg, "universe": {**cfg["universe"], "exchanges": ["NYSE"]}}
    assert ps_cache_key("abc", c2) != kp and tailex_cache_key("abc", c2) != kt
    monkeypatch.setattr(DL, "PS_MIN_MONTHS", 36)
    monkeypatch.setattr(DL, "TAIL_Q", 0.01)
    assert ps_cache_key("abc", cfg) != kp and tailex_cache_key("abc", cfg) != kt
    monkeypatch.undo()
    monkeypatch.setattr(DL.inspect, "getsource", lambda f: "changed " + f.__name__)
    assert ps_cache_key("abc", cfg) != kp and tailex_cache_key("abc", cfg) != kt


@pytest.mark.parametrize("which", ["ps", "tailex"])
def test_load_or_build_series_caches_on_disk(snap, cfg, ps, tx, tmp_path, which):
    fn, key, stem, want = {"ps": (load_or_build_ps, ps_cache_key, "ps_innov_monthly", ps),
                           "tailex": (load_or_build_tailex, tailex_cache_key, "tailex_monthly", tx)}[which]
    rt = {"cache": {"dir": str(tmp_path / "cache"), "enabled": True}}
    a = fn(snap, cfg, rt, "sha-x", root=tmp_path, **QUIET)
    files = [f.name for f in (tmp_path / "cache").glob(f"{stem}_*.parquet")]
    assert files == [f"{stem}_{key('sha-x', cfg)}.parquet"]
    msgs = []
    b = fn(snap, cfg, rt, "sha-x", root=tmp_path, log=msgs.append)
    assert any("cache hit" in m for m in msgs)
    pd.testing.assert_frame_equal(a, b, check_exact=True, check_freq=False)
    pd.testing.assert_frame_equal(a, want, check_exact=True, check_freq=False)


# ---- review round 1: PS_MIN_NAMES ------------------------------------------------------------

def _elig(rows):
    return pd.DataFrame(rows, columns=["ID", "month", "gamma", "cap_prev"])


def test_ps_min_names_blanks_a_thin_month_and_its_neighbour_changes():
    m1, m2, m3, m4 = (pd.Timestamp(d) for d in ("2000-01-31", "2000-02-29", "2000-03-31", "2000-04-28"))
    rows = [("A", m1, 0.1, 10.0),                                    # month 1: one name -> thin
            ("A", m2, 0.2, 10.0), ("B", m2, 0.4, 30.0),
            ("A", m3, 0.3, 20.0),                                    # month 3: thin
            ("A", m4, 0.5, 10.0), ("B", m4, 0.1, 10.0)]
    got = ps_aggregate(_elig(rows), min_names=2)
    assert got["n_eligible"].tolist() == [1, 2, 1, 2]
    assert got["gamma_hat"].isna().tolist() == [True, False, True, False]
    assert got["m_usd"].isna().tolist() == [True, False, True, False]
    # m_1 is the first DEFINED month's m (month 2), not the thin month 1's.
    assert got.loc[m2, "m_scale"] == 1.0 and got.loc[m4, "m_scale"] == pytest.approx(20.0 / 40.0)
    # Month 2's change would use thin month 1, month 4's thin month 3: all undefined.
    assert got["dgamma"].isna().all() and got["n_both"].tolist() == [0, 0, 0, 0]
    assert got.attrs["m1_month"] == "2000-02-29"
    # min_names=1 defines everything.
    assert ps_aggregate(_elig(rows), min_names=1)["gamma_hat"].notna().all()


def test_ps_min_names_at_full_size_blanks_the_fixture(snap, cfg, monkeypatch):
    monkeypatch.setattr(DL, "PS_MIN_NAMES", 100)
    got = build_ps_innov_monthly(snap, cfg, **QUIET)
    assert (got["n_eligible"] < 100).all() and (got["n_eligible"] > 30).any()
    assert got["gamma_hat"].isna().all() and got["ps_innov"].isna().all()


# ---- review round 1: the AR regression and the refit residual ------------------------------------

def test_a_nan_dgamma_removes_exactly_two_regression_months():
    agg = _agg(n=60)
    base = ps_innovations(agg)
    hole = agg.copy()
    hole.iloc[30, hole.columns.get_loc("dgamma")] = np.nan     # gamma_hat_30 stays defined
    got = ps_innovations(hole)
    assert base["n_fit"].iloc[-1] == 59
    assert got["n_fit"].iloc[-1] == 57                            # month 30 (y) and 31 (lag)
    assert got["ps_innov"].iloc[[30, 31]].isna().all()
    assert got["ps_innov"].iloc[32:].notna().all()


def test_ps_refit_is_one_fit_through_the_last_month_and_ends_on_the_expanding_value():
    agg = _agg(n=60)
    exp = ps_innovations(agg)
    for t in (30, 59):
        sub = agg.iloc[:t + 1]
        got = ps_refit_residuals(sub)
        y = sub["dgamma"].to_numpy()
        lvl = (sub["m_scale"] * sub["gamma_hat"]).to_numpy()
        X = np.column_stack([np.ones(t), y[:-1], lvl[:-1]])
        b = np.linalg.lstsq(X, y[1:], rcond=None)[0]
        want = (y[1:] - X @ b) / 100.0
        assert np.isnan(got.iloc[0])
        np.testing.assert_allclose(got.iloc[1:].to_numpy(), want, rtol=1e-10, atol=1e-15)
        assert got.iloc[-1] == pytest.approx(exp["ps_innov"].iloc[t], rel=1e-10, abs=1e-15)
    assert ps_refit_residuals(agg.iloc[:20]).isna().all()        # < PS_MIN_MONTHS regression months


def test_monthly_ps_innov_refit_reads_nothing_after_the_signal(snap, spidx, cfg, ps):
    sig = pd.Timestamp("1997-06-30")
    got = _ctx(snap, spidx, cfg, sig).monthly_ps_innov(24, refit=True)
    assert len(got) == 24 and got.index.max() == sig and got.notna().all()
    want = ps_refit_residuals(ps.loc[ps.index <= sig]).reindex(got.index)
    pd.testing.assert_series_equal(got, want.astype(float), check_names=False)
    assert got.iloc[-1] == pytest.approx(ps.loc[sig, "ps_innov"], rel=1e-10)
    wild = ps.copy()
    later = wild.index > sig
    wild.loc[later, ["dgamma", "gamma_hat"]] = 1e6
    p2 = PanelIndex(spidx.panel, snap, cfg)
    p2.set_ps_loader(lambda: wild)
    pd.testing.assert_series_equal(_ctx(snap, p2, cfg, sig).monthly_ps_innov(24, refit=True), got)


# ---- review round 1: exchange as of t-1 ------------------------------------------------------------

def test_ps_exchange_asof_rules():
    moves = pd.DataFrame({"ID": ["a", "a", "b"],
                          "date": pd.to_datetime(["2000-03-10", "2002-01-15", "2001-06-01"]),
                          "ex_to": ["NYSE", "OTC", "NASDAQ"], "ex_from": ["NASDAQ", "NYSE", "NYSE"]})
    cur = pd.Series({"a": "NYSE", "b": "NASDAQ", "c": "NYSEMKT"})
    ids = ["a", "a", "a", "a", "b", "b", "c"]
    dates = pd.to_datetime(["2000-01-31", "2000-03-10", "2001-12-31", "2002-02-28",
                            "2001-05-31", "2001-06-29", "2000-01-31"])
    causal = ps_exchange_asof(ids, dates, moves, cur, rule="causal")
    # Before a's first move the causal rule can only say today's (NYSE); on the
    # move date the move counts; b before its only move: today's (NASDAQ).
    assert list(causal) == ["NYSE", "NYSE", "NYSE", "OTC", "NASDAQ", "NASDAQ", "NYSEMKT"]
    retro = ps_exchange_asof(ids, dates, moves, cur, rule="retro")
    assert list(retro) == ["NASDAQ", "NYSE", "NYSE", "OTC", "NYSE", "NASDAQ", "NYSEMKT"]
    empty = moves.iloc[0:0]
    assert list(ps_exchange_asof(ids, dates, empty, cur)) == list(cur.reindex(ids))
    with pytest.raises(ValueError):
        ps_exchange_asof(ids, dates, moves, cur, rule="today")


def _add_moves(rows):
    def edit(d):
        a = pd.read_parquet(d / "ACTIONS.parquet")
        new = []
        for tk, day, frm, to in rows:
            for act, ex in (("exchangefrom", frm), ("exchangeto", to)):
                new.append({"date": pd.Timestamp(day), "action": act, "ticker": tk, "name": tk,
                            "value": np.nan, "contraticker": None, "contraname": ex})
        pd.concat([a, pd.DataFrame(new)], ignore_index=True).to_parquet(d / "ACTIONS.parquet", index=False)
    return edit


@pytest.mark.parametrize("rule", ["causal", "retro"])
def test_ps_eligibility_follows_the_exchange_at_t_minus_1(synthetic, cfg, tmp_path, monkeypatch, rule):
    monkeypatch.setattr(DL, "PS_EXCHANGE_RULE", rule)
    snap2 = _edited(synthetic, tmp_path, _add_moves([
        ("T001", "1998-06-15", "NASDAQ", "NYSE"),       # NASDAQ today, NYSE from mid-1998
        ("T000", "1997-03-10", "NASDAQ", "NYSE"),       # NYSE today, NASDAQ before 1997-03
        ("T002", "1999-01-15", "NYSE", "OTC"),          # NYSE today, OTC from 1999-01
    ]))
    sm = ps_stock_months(snap2, cfg)[0].set_index(["ID", "month"])
    el = lambda tk, m: bool(sm.loc[(_id(synthetic, tk), _bme(m)), "eligible"])      # noqa: E731
    exch = lambda tk, m: sm.loc[(_id(synthetic, tk), _bme(m)), "exchange"]         # noqa: E731
    # T001: in only once the end of t-1 is on or after the move.
    assert exch("T001", "1998-07-31") == "NYSE" and el("T001", "1998-07-31")
    assert el("T001", "2000-03-31")
    # T002: out once it is OTC at the end of t-1.
    assert el("T002", "1999-01-29") and not el("T002", "1999-02-26")
    assert exch("T002", "2000-03-31") == "OTC"
    if rule == "causal":
        # Before the first recorded move the causal rule falls back to today's
        # exchange: T001 counts as NASDAQ, T000 as NYSE (declared).
        assert exch("T001", "1998-06-30") == "NASDAQ" and not el("T001", "1998-06-30")
        assert exch("T000", "1997-02-28") == "NYSE" and el("T000", "1997-02-28")
    else:
        assert exch("T001", "1998-06-30") == "NASDAQ" and not el("T001", "1998-06-30")
        assert exch("T000", "1997-02-28") == "NASDAQ" and not el("T000", "1997-02-28")
        assert exch("T000", "1997-04-30") == "NYSE" and el("T000", "1997-04-30")


def test_editing_one_names_exchange_leaves_every_other_gamma_unchanged(synthetic, cfg, stock_months, tmp_path):
    def edit(d):
        tk = pd.read_parquet(d / "TICKERS.parquet")
        tk.loc[tk["ticker"] == "T000", "exchange"] = "NASDAQ"
        tk.to_parquet(d / "TICKERS.parquet", index=False)
    sm2 = ps_stock_months(_edited(synthetic, tmp_path, edit), cfg)[0]
    t0 = _id(synthetic, "T000")
    assert t0 not in set(sm2["ID"])
    base = stock_months[stock_months["ID"] != t0].set_index(["ID", "month"]).sort_index()
    got = sm2.set_index(["ID", "month"]).sort_index()
    assert got.index.equals(base.index)
    pd.testing.assert_series_equal(got["gamma"], base["gamma"], check_exact=True)
    pd.testing.assert_series_equal(got["eligible"], base["eligible"])


# ---- review round 1: causality on awkward rows ----------------------------------------------------

def _awkward(d):
    """A gap (T004 has no rows 1996-03-20 .. 1996-04-10, so its March close
    is stale at the month-end and its return across the gap is invalid), an
    implausible cap (T006's DAILY.marketcap x 1e6 on 1996-05-31) and a
    no-trade day (T008, 1996-05-15)."""
    for t in ("SEP", "DAILY"):
        x = pd.read_parquet(d / f"{t}.parquet")
        gap = (x["ticker"] == "T004") & (x["date"] >= "1996-03-20") & (x["date"] <= "1996-04-10")
        x = x[~gap]
        if t == "DAILY":
            x.loc[(x["ticker"] == "T006") & (x["date"] == "1996-05-31"), "marketcap"] *= 1e6
        else:
            x.loc[(x["ticker"] == "T008") & (x["date"] == "1996-05-15"), "volume"] = 0
        x.to_parquet(d / f"{t}.parquet", index=False)


def test_ps_awkward_rows_are_excluded_as_declared(synthetic, cfg, tmp_path, stock_months):
    root = tmp_path / "awk"
    shutil.copytree(synthetic["root"], root)
    _awkward(root / "sharadar")
    sm = ps_stock_months(_rehash(root, synthetic["manifest"]), cfg)[0].set_index(["ID", "month"])
    k = (_id(synthetic, "T004"), _bme("1996-04-30"))
    assert pd.Timestamp(sm.loc[k, "prev_date"]) == pd.Timestamp("1996-03-19")        # stale t-1 row
    assert not sm.loc[k, "eligible"]
    k = (_id(synthetic, "T006"), _bme("1996-06-28"))
    assert np.isnan(sm.loc[k, "cap_prev"]) and not sm.loc[k, "eligible"]              # implausible cap
    k = (_id(synthetic, "T008"), _bme("1996-05-31"))
    base = stock_months.set_index(["ID", "month"])
    assert sm.loc[k, "n_days"] == base.loc[k, "n_days"] - 1                           # the 2-day return stays
    assert sm.loc[k, "n_obs"] == base.loc[k, "n_obs"] - 2


@pytest.mark.parametrize("cut", ["1996-04-30", "1996-06-28"])
def test_series_are_causal_on_awkward_rows(synthetic, cfg, tmp_path, cut):
    cut = pd.Timestamp(cut)
    root = tmp_path / "awk"
    shutil.copytree(synthetic["root"], root)
    _awkward(root / "sharadar")
    full_snap = _rehash(root, synthetic["manifest"])
    ps_full = build_ps_innov_monthly(full_snap, cfg, **QUIET)
    tx_full = build_tailex_monthly(full_snap, cfg, **QUIET)
    root2 = tmp_path / "awk_cut"
    shutil.copytree(root, root2)
    _cut_after(cut)(root2 / "sharadar")
    cut_snap = _rehash(root2, synthetic["manifest"])
    ps_cut = build_ps_innov_monthly(cut_snap, cfg, **QUIET)
    tx_cut = build_tailex_monthly(cut_snap, cfg, **QUIET)
    pd.testing.assert_frame_equal(ps_full.loc[ps_full.index <= cut], ps_cut, check_exact=True)
    pd.testing.assert_frame_equal(tx_full.loc[tx_full.index <= cut], tx_cut, check_exact=True)


# ---- review round 1: tailex guard diagnostics ------------------------------------------------------

def test_tailex_unguarded_puts_back_only_the_down_spikes(synthetic, cfg, tx, tmp_path):
    crash = pd.Timestamp("2000-05-16")

    def edit(d):
        sp = pd.read_parquet(d / "SEP.parquet")
        sp.loc[(sp["ticker"] == "T002") & (sp["date"] == crash), "closeadj"] *= 0.15
        sp.to_parquet(d / "SEP.parquet", index=False)
    snap2 = _edited(synthetic, tmp_path, edit)
    t2 = build_tailex_monthly(snap2, cfg, **QUIET)
    me = pd.Timestamp("2000-05-31")
    assert t2.loc[me, "n_spike_dn"] == 1 and (t2["n_spike_dn"].drop(me) == 0).all()
    # The unguarded pool is the guarded pool plus the -85% day (not its +567%
    # reversal, which stays guarded out).
    nd = _series_name_days(snap2, cfg)
    m = (nd["month"] == me).to_numpy() & (nd["volume"].to_numpy() > 0)
    pool = nd.loc[m & nd["clean"].to_numpy(), "r"].to_numpy()
    dn = nd.loc[m & nd["spike_dn"].to_numpy(), "r"].to_numpy()
    assert len(dn) == 1 and -0.87 < dn[0] < -0.8
    want = tailex_from_pool([me] * (len(pool) + 1), np.r_[pool, dn]).iloc[0]
    assert t2.loc[me, "retp5_unguarded"] == want["retp5"]
    assert t2.loc[me, "tailex_unguarded"] == pytest.approx(want["tailex"], rel=1e-12)
    assert t2.loc[me, "tailex_unguarded"] > t2.loc[me, "tailex"]
    other = t2.index != me
    pd.testing.assert_series_equal(t2.loc[other, "tailex_unguarded"], t2.loc[other, "tailex"],
                                   check_names=False, check_exact=True)
    pd.testing.assert_series_equal(t2.loc[other, "tailex"], tx.loc[other, "tailex"], check_exact=True)


# ---- review round 1: monthly FF3 ---------------------------------------------------------------------

def _ff3_frame():
    """Hand-built daily FF3 frame on business days 1999-05-03 .. 2000-03-31:
    the portfolios start on the first July day (a June formation); February
    2000 keeps only 10 days (thin)."""
    rng = np.random.default_rng(5)
    days = pd.bdate_range("1999-05-03", "2000-03-31")
    days = days[~((days >= "2000-02-01") & (days <= "2000-02-14"))]
    f = pd.DataFrame({"mkt": rng.normal(0, 0.01, len(days))}, index=days)
    for p in DL.FF3_PORTS:
        f[f"r_{p}"] = np.where(days >= "1999-07-01", rng.normal(0, 0.01, len(days)), np.nan)
    f["smb"] = f[["r_SL", "r_SM", "r_SH"]].mean(axis=1) - f[["r_BL", "r_BM", "r_BH"]].mean(axis=1)
    f["hml"] = f[["r_SH", "r_BH"]].mean(axis=1) - f[["r_SL", "r_BL"]].mean(axis=1)
    return f


@pytest.fixture()
def fpidx(panel, snap, cfg):
    p = PanelIndex(panel, snap, cfg)
    f = _ff3_frame()
    p.set_ff3_loader(lambda: f)
    return p, f


def test_monthly_ff3_compounds_portfolios_and_guards_partial_months(snap, cfg, fpidx):
    p, f = fpidx
    got = _ctx(snap, p, cfg, "2000-03-31").monthly_ff3(12)
    assert list(got.columns) == ["mkt", "smb", "hml"] and len(got) == 12
    assert got.index.max() == pd.Timestamp("2000-03-31")
    may, jun, jul, feb = (pd.Timestamp(d) for d in ("1999-05-31", "1999-06-30", "1999-07-30", "2000-02-29"))
    assert got.loc[:pd.Timestamp("1999-04-30")].isna().all().all()     # before the series
    assert got.loc[may].isna().all()                                      # the series' first month
    assert np.isfinite(got.loc[jun, "mkt"]) and got.loc[jun, ["smb", "hml"]].isna().all()
    assert got.loc[feb].isna().all()                                      # 10 days < min_days
    w = f[(f.index > pd.Timestamp("1999-06-30")) & (f.index <= jul)]
    r = {q: (1 + w[f"r_{q}"]).prod() - 1 for q in DL.FF3_PORTS}
    assert got.loc[jul, "mkt"] == pytest.approx((1 + w["mkt"]).prod() - 1, rel=1e-12)
    assert got.loc[jul, "smb"] == pytest.approx((r["SL"] + r["SM"] + r["SH"]) / 3
                                                - (r["BL"] + r["BM"] + r["BH"]) / 3, rel=1e-12)
    assert got.loc[jul, "hml"] == pytest.approx((r["SH"] + r["BH"]) / 2 - (r["SL"] + r["BL"]) / 2, rel=1e-12)
    # Not the compounded daily SMB.
    assert got.loc[jul, "smb"] != pytest.approx((1 + w["smb"]).prod() - 1, rel=1e-9)
    assert got.loc[pd.Timestamp("2000-03-31")].notna().all()
    assert _ctx(snap, p, cfg, "2000-03-31").monthly_ff3(12, min_days=5).loc[feb].notna().all()


def test_monthly_ff3_is_bounded_by_the_signal(snap, cfg, fpidx, panel):
    p, f = fpidx
    sig = pd.Timestamp("1999-12-31")
    got = _ctx(snap, p, cfg, sig).monthly_ff3(6)
    assert got.index.max() == sig and got.notna().all().all()
    wild = f.copy()
    wild.loc[wild.index > sig] = 5.0
    p2 = PanelIndex(panel, snap, cfg)
    p2.set_ff3_loader(lambda: wild)
    pd.testing.assert_frame_equal(_ctx(snap, p2, cfg, sig).monthly_ff3(6), got)


def test_monthly_ff3_mkt_is_monthly_market(snap, cfg, panel):
    """On the real FF3 build's mkt (= the market series), monthly_ff3's mkt
    is monthly_market's number."""
    mkt = build_market_daily(snap, cfg, **QUIET)
    f = pd.DataFrame({"mkt": mkt["mkt_ret"]})
    for q in DL.FF3_PORTS:
        f[f"r_{q}"] = mkt["mkt_ret"]
    p = PanelIndex(panel, snap, cfg)
    p.set_ff3_loader(lambda: f)
    p.set_market_loader(lambda: mkt)
    ctx = _ctx(snap, p, cfg, "2000-06-30")
    pd.testing.assert_series_equal(ctx.monthly_ff3(24)["mkt"], ctx.monthly_market(24), check_names=False)
