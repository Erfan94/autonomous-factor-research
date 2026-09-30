"""
The Han-Zhou-Zhu trend-factor coefficients (build_trend_monthly,
MonthContext.monthly_trend_coefs) and moving-average signals
(trend_ma_signals, MonthContext.trend_ma_signals), against hand-built inputs
to the pure steps and against the synthetic snapshot. In the fixture the
even-indexed names (and TINY) are NYSE, the odd ones NASDAQ; every name
trades every business day from 1992-01-01, no splits, prices near $30
(PENNY near $0.40), so the 1000-row window is complete from about 1995-10.
"""
import shutil

import numpy as np
import pandas as pd
import pytest

import harness.data_layer as DL
from harness.crosssection import ols_coef
from harness.data_layer import (TREND_LAGS, MonthContext, PanelIndex, Snapshot,
                                build_trend_monthly, build_universe, ff3_cache_key,
                                load_or_build_trend, market_cache_key, ps_cache_key, sha256_file,
                                tailex_cache_key, to_bme, trend_cache_key, trend_ebar,
                                trend_ma_cols, trend_ma_signals, trend_regressions,
                                trend_stock_months)

QUIET = dict(log=lambda *a, **k: None)
ACOLS = trend_ma_cols()
BCOLS = ["b_const"] + [f"b_{c}" for c in ACOLS]


@pytest.fixture(scope="module")
def tr(snap, cfg):
    return build_trend_monthly(snap, cfg, **QUIET)


@pytest.fixture(scope="module")
def sm(snap, cfg):
    return trend_stock_months(snap, cfg)[0]


@pytest.fixture(scope="module")
def tpidx(panel, snap, cfg, tr):
    p = PanelIndex(panel, snap, cfg)
    p.set_trend_loader(lambda: tr)
    return p


def _bme(s):
    return to_bme([pd.Timestamp(s)]).iloc[0]


def _ctx(snap, pidx, cfg, asof):
    u = build_universe(pidx, pd.Timestamp(asof), cfg)
    return MonthContext(snap, pidx, u, pd.Timestamp(asof), cfg, {})


def _rehash(root, manifest):
    m = dict(manifest)
    m["tables"] = {k: dict(v) for k, v in m["tables"].items()}
    for t in m["tables"]:
        m["tables"][t]["sha256"] = sha256_file(root / "sharadar" / m["tables"][t]["file"])
    return Snapshot(root / "sharadar", m, verify_hashes=True)


def _edited(synthetic, tmp_path, edit, name="copy"):
    root = tmp_path / name
    shutil.copytree(synthetic["root"], root)
    edit(root / "sharadar")
    return _rehash(root, synthetic["manifest"])


def _cut_after(day):
    def edit(d):
        for t in ("SEP", "DAILY"):
            x = pd.read_parquet(d / f"{t}.parquet")
            x[x["date"] <= day].to_parquet(d / f"{t}.parquet", index=False)
    return edit


# ---- ols_coef on the trend design: coefficient recovery -------------------------------------

def _panel(n_months=30, n_names=400, noise=0.0, seed=0, lags=TREND_LAGS):
    """A synthetic stock-month frame: every name fit every month, A_L drawn
    around 1, and closeadj built so the month-m return is EXACTLY
    a_m + sum_L b_m,L A_L(m-1) (+ noise)."""
    rng = np.random.default_rng(seed)
    months = pd.DatetimeIndex(to_bme(pd.period_range("2000-01", periods=n_months, freq="M")
                                     .to_timestamp(how="start")).to_numpy())
    coefs = pd.DataFrame(rng.normal(0, 0.05, (n_months, len(lags) + 1)), index=months,
                         columns=["const"] + trend_ma_cols(lags))
    rows = []
    px = np.full(n_names, 50.0)
    for k, m in enumerate(months):
        A = 1.0 + rng.normal(0, 0.1, (n_names, len(lags)))
        f = pd.DataFrame(A, columns=trend_ma_cols(lags))
        f.insert(0, "ID", [f"S{i:04d}" for i in range(n_names)])
        f.insert(1, "month", m)
        f["closeadj"] = px.copy()
        f["fit"] = True
        rows.append(f)
        if k + 1 < n_months:
            b = coefs.iloc[k + 1]
            y = b["const"] + A @ b[trend_ma_cols(lags)].to_numpy() + rng.normal(0, noise, n_names)
            px = px * (1.0 + y)
    return pd.concat(rows, ignore_index=True), coefs


def test_regressions_recover_planted_coefficients_exactly():
    sm, coefs = _panel()
    b = trend_regressions(sm)
    assert b.index[0] == coefs.index[1]                    # first row: the month after the first fit month
    got = b[BCOLS].to_numpy(dtype=float)
    want = coefs.iloc[1:].to_numpy()
    assert np.allclose(got, want, atol=1e-8)
    assert (b["n_obs"] == 400).all() and (b["n_dropped"] == 0).all()
    assert (pd.DatetimeIndex(b["fit_month"]) == coefs.index[:-1]).all()


def test_regressions_recover_coefficients_under_noise():
    sm, coefs = _panel(n_months=6, n_names=20000, noise=0.01, seed=3)
    b = trend_regressions(sm)
    err = np.abs(b[BCOLS].to_numpy(dtype=float) - coefs.iloc[1:].to_numpy())
    assert err.max() < 0.05 and np.median(err) < 0.01


def test_ols_coef_omits_the_later_of_two_identical_columns():
    """The real 1998-12 case: every name has < 400 rows, so A_400 == A_1000
    exactly. The earlier column keeps the weight; the fit is lstsq's."""
    rng = np.random.default_rng(5)
    n = 300
    X = pd.DataFrame({"A_3": 1 + rng.normal(0, .1, n), "A_400": 1 + rng.normal(0, .1, n)})
    X["A_1000"] = X["A_400"]
    y = pd.Series(0.01 + 0.3 * X["A_3"] - 0.2 * X["A_400"] + rng.normal(0, .01, n))
    b = ols_coef(y, X)
    assert b.attrs["dropped"] == ["A_1000"] and b["A_1000"] == 0.0
    ref, *_ = np.linalg.lstsq(np.column_stack([np.ones(n), X.to_numpy()]), y.to_numpy(), rcond=None)
    A = np.column_stack([np.ones(n), X.to_numpy()])
    assert np.allclose(A @ b.to_numpy(), A @ ref, atol=1e-10)      # same fitted values
    assert abs(b["A_400"] - (ref[2] + ref[3])) < 1e-8               # the pair's total weight


def test_ols_coef_constant_column_min_obs_and_listwise():
    rng = np.random.default_rng(6)
    X = pd.DataFrame({"a": rng.normal(size=50), "c": 1.0})
    y = pd.Series(2.0 + 3.0 * X["a"])
    b = ols_coef(y, X, min_obs=10)
    assert b.attrs["dropped"] == ["c"] and b["c"] == 0.0
    assert abs(b["const"] - 2.0) < 1e-10 and abs(b["a"] - 3.0) < 1e-10
    assert ols_coef(y, X, min_obs=51).isna().all()
    y2 = y.copy()
    y2.iloc[0] = 1e9
    X2 = X.copy()
    X2.iloc[0, 0] = np.nan                                           # that row is out
    b2 = ols_coef(y2, X2, min_obs=10)
    assert b2.attrs["n_obs"] == 49 and abs(b2["a"] - 3.0) < 1e-10
    b3 = ols_coef(y, X[["a"]], add_intercept=False, min_obs=10)
    assert list(b3.index) == ["a"]


def test_require_fit_next_drops_names_that_fail_the_screen_in_the_return_month():
    sm, coefs = _panel(n_months=4, n_names=200, seed=7)
    bad = (sm["ID"] == "S0000") & (sm["month"] == sm["month"].unique()[2])
    sm.loc[bad, "fit"] = False
    wild = (sm["ID"] == "S0000") & (sm["month"] == sm["month"].unique()[2])
    sm.loc[wild, "closeadj"] *= 50.0                                 # a +4900% month for S0000
    b = trend_regressions(sm)
    m2 = sm["month"].unique()[2]
    assert b.loc[m2, "n_drop_next"] == 1 and b.loc[m2, "n_obs"] == 199
    assert np.allclose(b.loc[m2, BCOLS].to_numpy(dtype=float), coefs.loc[m2].to_numpy(), atol=1e-8)
    # It is also out of the NEXT month's regression (not fit at that fit month).
    m3 = sm["month"].unique()[3]
    assert b.loc[m3, "n_obs"] == 199 and b.loc[m3, "n_drop_next"] == 0


# ---- ebar: the trailing mean ---------------------------------------------------------------------

def test_ebar_is_the_trailing_twelve_month_mean_with_min_one():
    sm, coefs = _panel(n_months=30, n_names=100, seed=8)
    b = trend_regressions(sm)
    b["ma_full"] = True
    e = trend_ebar(b)
    for k in (0, 5, 11, 12, 28):
        lo = max(0, k - 11)
        want = b[BCOLS].iloc[lo:k + 1].astype(float).mean().to_numpy()
        got = e[["ebar_const"] + [f"ebar_{c}" for c in ACOLS]].iloc[k].to_numpy(dtype=float)
        assert np.allclose(got, want, rtol=0, atol=1e-12)
        assert e["n_betas"].iloc[k] == k - lo + 1
        assert e["ebar_full"].iloc[k] == (k >= 11)


def test_ebar_does_not_move_when_later_betas_change():
    sm, _ = _panel(n_months=30, n_names=100, seed=9)
    b = trend_regressions(sm)
    b["ma_full"] = True
    full = trend_ebar(b)
    wild = b.copy()
    wild.iloc[20:, [wild.columns.get_loc(c) for c in BCOLS]] = 1e6
    pd.testing.assert_frame_equal(trend_ebar(wild).iloc[:20], full.iloc[:20], check_exact=True)
    pd.testing.assert_frame_equal(trend_ebar(b.iloc[:15]), full.iloc[:15], check_exact=True)


def test_ebar_skips_a_missing_beta_and_flags_the_window():
    sm, _ = _panel(n_months=20, n_names=100, seed=10)
    b = trend_regressions(sm)
    b["ma_full"] = True
    b.iloc[3, [b.columns.get_loc(c) for c in BCOLS]] = np.nan
    e = trend_ebar(b)
    want = b[BCOLS].iloc[0:12].astype(float).drop(index=b.index[3]).mean().to_numpy()
    assert np.allclose(e[["ebar_const"] + [f"ebar_{c}" for c in ACOLS]].iloc[11].to_numpy(dtype=float), want)
    assert e["n_betas"].iloc[11] == 11 and not e["ebar_full"].iloc[11]
    assert e["ebar_full"].iloc[15]                                    # the gap has left the window


def test_ebar_refuses_a_non_contiguous_index():
    sm, _ = _panel(n_months=10, n_names=100, seed=11)
    b = trend_regressions(sm)
    b["ma_full"] = True
    with pytest.raises(RuntimeError, match="contiguous"):
        trend_ebar(b.drop(index=b.index[4]))


# ---- MA signals: the pure function ---------------------------------------------------------------

def _rows(closes, start="2001-01-02", ident="X"):
    d = pd.bdate_range(start, periods=len(closes))
    return pd.DataFrame({"ID": ident, "date": d, "close": np.asarray(closes, dtype=float)})


def test_ma_signals_are_trailing_row_means_over_the_month_end_close():
    rng = np.random.default_rng(12)
    closes = 20 * np.cumprod(1 + rng.normal(0, 0.02, 1300))
    r = _rows(closes)
    got = trend_ma_signals(r)
    p = pd.Series(closes, index=r["date"])
    for _, row in got.iterrows():
        i = int(np.flatnonzero(r["date"].to_numpy() == np.datetime64(row["date"]))[0])
        assert row["date"] == r["date"][r["date"] <= row["month"]].max()     # the month's last row
        assert row["n_rows"] == i + 1
        for L in TREND_LAGS:
            want = p.iloc[max(0, i - L + 1):i + 1].mean() / closes[i]         # min_samples=1
            assert abs(row[f"A_{L}"] - want) < 1e-12 * max(1.0, abs(want))
    # Early months: every window longer than the history is the full mean, identical.
    first = got.iloc[0]
    long = [f"A_{L}" for L in TREND_LAGS if L >= first["n_rows"]]
    assert len(long) >= 5 and len({first[c] for c in long}) == 1


def test_ma_signals_are_invariant_to_a_common_rescaling_and_to_row_order():
    rng = np.random.default_rng(13)
    r = pd.concat([_rows(10 * np.cumprod(1 + rng.normal(0, .02, 700)), ident="A"),
                   _rows(80 * np.cumprod(1 + rng.normal(0, .02, 400)), ident="B", start="2002-03-01")])
    base = trend_ma_signals(r)
    scaled = trend_ma_signals(r.assign(close=r["close"] * 7.25))           # a split restated onto today's basis
    pd.testing.assert_frame_equal(base[ACOLS], scaled[ACOLS], rtol=1e-12)
    shuffled = trend_ma_signals(r.sample(frac=1.0, random_state=0))
    pd.testing.assert_frame_equal(base, shuffled, check_exact=True)


def test_ma_signals_skip_a_null_close_and_keep_the_last_duplicate():
    closes = np.arange(1.0, 61.0)
    r = _rows(closes)
    r.loc[40, "close"] = np.nan
    got = trend_ma_signals(r, lags=(3, 50))
    last = got.iloc[-1]
    i = len(closes) - 1
    assert abs(last["A_3"] - closes[i - 2:i + 1].mean() / closes[i]) < 1e-12
    window = np.r_[closes[i - 49:40], closes[41:i + 1]]                    # 49 non-null of the last 50 rows
    assert abs(last["A_50"] - window.mean() / closes[i]) < 1e-12 and last["n_rows"] == 59
    dup = pd.concat([r, r.tail(1).assign(close=999.0)], ignore_index=True)
    assert trend_ma_signals(dup, lags=(3,)).iloc[-1]["close"] == 999.0


def test_ma_signals_read_nothing_after_the_row():
    rng = np.random.default_rng(14)
    r = _rows(30 * np.cumprod(1 + rng.normal(0, .02, 900)))
    full = trend_ma_signals(r)
    cut = full["month"].iloc[20]
    part = trend_ma_signals(r[r["date"] <= cut])
    pd.testing.assert_frame_equal(part, full[full["month"] <= cut].reset_index(drop=True), check_exact=True)


def test_ma_signals_never_evaluate_a_weekend_row_after_the_business_month_end():
    """2001-03-31 is a Saturday: BME(2001-03) is Friday 2001-03-30. A stray
    Saturday print with an outlier close is not the month's row and is in
    none of that month's windows; it is a past print for April's windows."""
    rng = np.random.default_rng(15)
    r = _rows(30 * np.cumprod(1 + rng.normal(0, .02, 120)))                # 2001-01-02 .. mid-June
    sat = pd.Timestamp("2001-03-31")
    assert sat.day_name() == "Saturday" and _bme(sat) == pd.Timestamp("2001-03-30")
    base = trend_ma_signals(r, lags=(3, 20, 100))
    stray = pd.concat([r, pd.DataFrame({"ID": ["X"], "date": [sat], "close": [1e6]})], ignore_index=True)
    got = trend_ma_signals(stray, lags=(3, 20, 100))
    mar = got.set_index("month").loc[pd.Timestamp("2001-03-30")]
    assert mar["date"] == pd.Timestamp("2001-03-30") and mar["close"] < 1e3
    pd.testing.assert_series_equal(mar, base.set_index("month").loc[pd.Timestamp("2001-03-30")],
                                   check_exact=True)
    assert (got["date"] <= got["month"]).all() and len(got) == len(base)
    apr = got.set_index("month").loc[pd.Timestamp("2001-04-30")]
    assert apr["A_100"] > 100 and apr["n_rows"] == base.set_index("month").loc[
        pd.Timestamp("2001-04-30"), "n_rows"] + 1                          # in April's history
    only = trend_ma_signals(pd.DataFrame({"ID": ["Y"], "date": [sat], "close": [5.0]}), lags=(3,))
    assert only.empty                                                     # its only row is after the BME


# ---- the builder on the fixture ----------------------------------------------------------------------

def test_builder_matches_a_hand_regression_on_the_raw_parquet(snap, cfg, tr, synthetic):
    """One month by hand from the parquet: pandas rolling means of close,
    the $5 / NYSE p10 screen at both ends, np.linalg.lstsq."""
    root = synthetic["root"] / "sharadar"
    sep = pd.read_parquet(root / "SEP.parquet")
    daily = pd.read_parquet(root / "DAILY.parquet")
    tk = pd.read_parquet(root / "TICKERS.parquet")
    tk = tk[tk["table"] == "SEP"].set_index("ticker")
    sep = sep.sort_values(["ticker", "date"])
    for L in TREND_LAGS:
        sep[f"A_{L}"] = (sep.groupby("ticker")["close"].rolling(L, min_periods=1).mean()
                         .reset_index(level=0, drop=True) / sep["close"])
    sep["month"] = to_bme(sep["date"]).to_numpy()
    last = sep.groupby(["ticker", "month"]).tail(1).merge(
        daily[["ticker", "date", "marketcap"]], on=["ticker", "date"], how="left")
    last["cap"] = last["marketcap"] * 1e6
    last["ex"] = last["ticker"].map(tk["exchange"])

    def fit(m):
        x = last[last["month"] == m]
        cut = x.loc[x["ex"] == "NYSE", "cap"].quantile(0.10)
        return x[(x["closeunadj"] >= 5) & (x["cap"] >= cut)].set_index("ticker")

    fm, me = _bme("1997-05-30"), _bme("1997-06-30")
    x0, x1 = fit(fm), fit(me)
    j = x0.index.intersection(x1.index)
    y = x1.loc[j, "closeadj"] / x0.loc[j, "closeadj"] - 1
    A = np.column_stack([np.ones(len(j)), x0.loc[j, ACOLS].to_numpy()])
    ref, *_ = np.linalg.lstsq(A, y.to_numpy(), rcond=None)
    assert tr.loc[me, "n_obs"] == len(j) >= 30
    assert "PENNY" not in j and "TINY" not in j
    assert np.allclose(tr.loc[me, BCOLS].to_numpy(dtype=float), ref, rtol=1e-6, atol=1e-8)
    assert pd.Timestamp(tr.loc[me, "fit_month"]) == fm


def test_builder_first_rows_and_censoring_flags(tr, synthetic):
    first = tr.index[0]
    assert first == _bme("1992-02-28")                          # first fit month 1992-01
    assert tr["ebar_const"].first_valid_index() == first        # ebar on ONE beta (OSAP min 1)
    assert tr.loc[first, "n_betas"] == 1
    early = tr[~tr["ma_full"]]
    assert len(early) and (early["n_dropped"] > 0).any()        # the long lags collinear at first
    assert (tr.loc[tr["ma_full"], "n_dropped"] == 0).all()
    assert (tr.loc[tr["ma_full"], "n_cal_fit"] >= 1000).all()
    assert (tr.loc[~tr["ma_full"], "n_cal_fit"] < 1000).all()
    ff = tr.index[tr["ebar_full"].to_numpy()].min()
    assert tr.loc[:ff, "ma_full"].iloc[-12:].all() and not tr.loc[:ff, "ma_full"].iloc[-13]


@pytest.mark.parametrize("cut", ["1996-06-28", "1998-12-31"])
def test_builder_is_causal_no_value_moves_when_later_rows_are_deleted(synthetic, cfg, tr, tmp_path, cut):
    cut = pd.Timestamp(cut)
    snap2 = _edited(synthetic, tmp_path, _cut_after(cut))
    trunc = build_trend_monthly(snap2, cfg, **QUIET)
    assert trunc.index.max() == cut and tr.index.max() > cut
    assert trunc["ebar_const"].notna().sum() > 10
    pd.testing.assert_frame_equal(tr.loc[tr.index <= cut], trunc, check_exact=True)


def test_price_screen_bites_on_the_unadjusted_price(synthetic, cfg, sm, tmp_path):
    """T010's closeunadj drops below $5 for June 1997 (close / closeadj
    untouched): it leaves fit(1997-06) only, and the May regression row
    (1997-06) loses it through REQUIRE_FIT_NEXT."""
    def edit(d):
        x = pd.read_parquet(d / "SEP.parquet")
        m = (x["ticker"] == "T010") & (x["date"] >= "1997-06-01") & (x["date"] <= "1997-06-30")
        x.loc[m, "closeunadj"] = 4.0
        x.to_parquet(d / "SEP.parquet", index=False)
    snap2 = _edited(synthetic, tmp_path, edit)
    sm2, _ = trend_stock_months(snap2, cfg)
    i = str(synthetic["perma"]["T010"])
    k = lambda f, m: f.set_index(["ID", "month"]).loc[(i, _bme(m)), "fit"]
    assert k(sm, "1997-06-30") and not k(sm2, "1997-06-30")
    assert k(sm2, "1997-05-30") and k(sm2, "1997-07-31")
    tr2 = trend_regressions(sm2)
    tr1 = trend_regressions(sm)
    assert tr2.loc[_bme("1997-06-30"), "n_drop_next"] == tr1.loc[_bme("1997-06-30"), "n_drop_next"] + 1
    assert tr2.loc[_bme("1997-07-31"), "n_obs"] == tr1.loc[_bme("1997-07-31"), "n_obs"] - 1


def test_a_saturday_print_after_the_month_end_is_neither_signal_nor_return_row(synthetic, cfg, sm, tmp_path):
    """1997-05-31 is a Saturday (BME Friday 1997-05-30). A stray SEP row for
    T010 on it, with an outlier price and no DAILY row, must not become the
    May row (the signal row of the June regression, its p0 and fit(May)) nor
    the May return row (p1 and fit(May) of the May regression): both
    regressions are unchanged, bit for bit."""
    sat = pd.Timestamp("1997-05-31")
    assert sat.day_name() == "Saturday"

    def edit(d):
        x = pd.read_parquet(d / "SEP.parquet")
        row = x[(x["ticker"] == "T010") & (x["date"] == "1997-05-30")].copy()
        assert len(row) == 1
        row["date"] = sat
        for c in ("open", "high", "low", "close", "closeadj", "closeunadj"):
            row[c] = row[c] * 50.0
        pd.concat([x, row], ignore_index=True).to_parquet(d / "SEP.parquet", index=False)
    snap2 = _edited(synthetic, tmp_path, edit)
    sm2, _ = trend_stock_months(snap2, cfg)
    i = str(synthetic["perma"]["T010"])
    k = lambda f: f.set_index(["ID", "month"]).loc[(i, _bme("1997-05-30"))]
    a, b = k(sm), k(sm2)
    assert b["date"] == pd.Timestamp("1997-05-30") and b["fit"]
    pd.testing.assert_series_equal(a, b, check_exact=True)
    tr1, tr2 = trend_regressions(sm), trend_regressions(sm2)
    for m in ("1997-05-30", "1997-06-30"):
        pd.testing.assert_series_equal(tr1.loc[_bme(m)], tr2.loc[_bme(m)], check_exact=True)


def test_exchange_in_force_decides_the_nyse_breakpoint_set(synthetic, cfg, sm, tmp_path):
    """T001 (NASDAQ today) moved from NYSE on 1998-01-15: under the retro
    rule it is NYSE at 1997-12 and joins that month's breakpoint set."""
    def edit(d):
        a = pd.read_parquet(d / "ACTIONS.parquet")
        mv = [{"date": pd.Timestamp("1998-01-15"), "action": "exchangefrom", "ticker": "T001",
               "name": "T001", "value": np.nan, "contraticker": None, "contraname": "NYSE"},
              {"date": pd.Timestamp("1998-01-15"), "action": "exchangeto", "ticker": "T001",
               "name": "T001", "value": np.nan, "contraticker": None, "contraname": "NASDAQ"}]
        pd.concat([a, pd.DataFrame(mv)], ignore_index=True).to_parquet(d / "ACTIONS.parquet", index=False)
    sm2, _ = trend_stock_months(_edited(synthetic, tmp_path, edit), cfg)
    i = str(synthetic["perma"]["T001"])
    e1 = sm.set_index(["ID", "month"])["exchange"]
    e2 = sm2.set_index(["ID", "month"])["exchange"]
    assert e1[(i, _bme("1997-12-31"))] == "NASDAQ" and e2[(i, _bme("1997-12-31"))] == "NYSE"
    assert e2[(i, _bme("1998-01-30"))] == "NASDAQ"
    c1 = sm.groupby("month")["cut_usd"].first()
    c2 = sm2.groupby("month")["cut_usd"].first()
    assert c1[_bme("1997-12-31")] != c2[_bme("1997-12-31")]
    assert c1[_bme("1998-02-27")] == c2[_bme("1998-02-27")]


# ---- accessors -----------------------------------------------------------------------------------------

def test_monthly_trend_coefs_is_bounded_by_the_signal_month(snap, tpidx, cfg, tr):
    ctx = _ctx(snap, tpidx, cfg, "1997-06-30")
    got = ctx.monthly_trend_coefs(12)
    assert tr.index.max() > pd.Timestamp("1997-06-30")
    assert len(got) == 12 and got.index.max() == pd.Timestamp("1997-06-30")
    assert list(got.columns[:12]) == ["const"] + ACOLS
    want = tr.loc[got.index, ["ebar_const"] + [f"ebar_{c}" for c in ACOLS]].to_numpy(dtype=float)
    assert np.array_equal(got[["const"] + ACOLS].to_numpy(dtype=float), want)
    beta = ctx.monthly_trend_coefs(1, which="beta")
    assert np.array_equal(beta[["const"] + ACOLS].to_numpy(dtype=float),
                          tr.loc[[pd.Timestamp("1997-06-30")], BCOLS].to_numpy(dtype=float))
    early = _ctx(snap, tpidx, cfg, "1992-01-31").monthly_trend_coefs(6)
    assert early[["const"] + ACOLS].isna().all().all() and not early["ebar_full"].any()
    wild = tr.copy()
    wild.loc[wild.index > pd.Timestamp("1997-06-30"), BCOLS + ["ebar_const"]] = 1e9
    p2 = PanelIndex(tpidx.panel, snap, cfg)
    p2.set_trend_loader(lambda: wild)
    pd.testing.assert_frame_equal(_ctx(snap, p2, cfg, "1997-06-30").monthly_trend_coefs(12), got)
    with pytest.raises(ValueError):
        ctx.monthly_trend_coefs(1, which="other")


def test_trend_ma_signals_accessor_equals_the_builders_values(snap, tpidx, cfg, sm):
    """Parity: the factor's A_L at t are the numbers the regression used."""
    for asof in ("1996-06-28", "1999-06-30"):
        ctx = _ctx(snap, tpidx, cfg, asof)
        got = ctx.trend_ma_signals()
        assert got.index.equals(ctx.ids) and got[ACOLS].notna().all(axis=1).mean() > 0.9
        ref = sm[sm["month"] == pd.Timestamp(asof)].set_index("ID").reindex(ctx.ids)
        ok = got["A_3"].notna()
        assert np.allclose(got.loc[ok, ACOLS].to_numpy(dtype=float),
                           ref.loc[ok, ACOLS].to_numpy(dtype=float), rtol=1e-10, atol=0)
        assert (got.loc[ok, "date"] <= pd.Timestamp(asof)).all()
    mk = _ctx(snap, tpidx, cfg, "1999-06-30").trend_ma_signals(scope="market")
    assert len(mk) > len(_ctx(snap, tpidx, cfg, "1999-06-30").ids)


def test_trend_ma_signals_accessor_reads_nothing_after_the_signal(synthetic, cfg, panel, snap, tpidx, tmp_path):
    asof = pd.Timestamp("1998-12-31")
    base = _ctx(snap, tpidx, cfg, asof).trend_ma_signals()

    def edit(d):
        x = pd.read_parquet(d / "SEP.parquet")
        x.loc[x["date"] > asof, "close"] *= 1e3
        x.to_parquet(d / "SEP.parquet", index=False)
    snap2 = _edited(synthetic, tmp_path, edit)
    p2 = PanelIndex(panel, snap2, cfg)
    got = MonthContext(snap2, p2, build_universe(tpidx, asof, cfg), asof, cfg, {}).trend_ma_signals()
    pd.testing.assert_frame_equal(got, base, check_exact=True)


# ---- loader and cache -------------------------------------------------------------------------------------

def test_trend_loader_is_called_once_and_only_on_demand(panel, snap, cfg, tr):
    calls = []
    p = PanelIndex(panel, snap, cfg)
    p.set_trend_loader(lambda: calls.append("tr") or tr)
    ctx = _ctx(snap, p, cfg, "2000-06-30")
    ctx.market_context()
    ctx.trend_ma_signals()
    assert calls == []
    ctx.monthly_trend_coefs(12)
    ctx.monthly_trend_coefs(1, which="beta")
    assert calls == ["tr"]


def test_trend_cache_key_moves_with_data_config_and_source(cfg, monkeypatch):
    k = trend_cache_key("abc", cfg)
    assert k == trend_cache_key("abc", cfg) and k != trend_cache_key("abd", cfg)
    assert len({k, ps_cache_key("abc", cfg), tailex_cache_key("abc", cfg),
                ff3_cache_key("abc", cfg), market_cache_key("abc", cfg)}) == 5
    c2 = {**cfg, "universe": {**cfg["universe"], "exchanges": ["NYSE"]}}
    assert trend_cache_key("abc", c2) != k
    for name, val in (("TREND_LAGS", (3, 5)), ("PS_EXCHANGE_RULE", "causal"),
                      ("TREND_REQUIRE_FIT_NEXT", False), ("TREND_PRICE_MIN", 1.0),
                      ("TREND_BETA_WINDOW", 6), ("MARKET_MAX_CAP_TO_ADV", 1e6)):
        with monkeypatch.context() as mp:
            mp.setattr(DL, name, val)
            assert trend_cache_key("abc", cfg) != k, name
    orig = DL.inspect.getsource
    with monkeypatch.context() as mp:                                  # the OLS is in the hash
        mp.setattr(DL.inspect, "getsource", lambda f: "changed" if f is ols_coef else orig(f))
        assert trend_cache_key("abc", cfg) != k
    assert trend_cache_key("abc", cfg) == k


def test_load_or_build_trend_caches_on_disk(snap, cfg, tr, tmp_path):
    rt = {"cache": {"dir": str(tmp_path / "cache"), "enabled": True}}
    a = load_or_build_trend(snap, cfg, rt, "sha-x", root=tmp_path, **QUIET)
    files = [f.name for f in (tmp_path / "cache").glob("trend_monthly_*.parquet")]
    assert files == [f"trend_monthly_{trend_cache_key('sha-x', cfg)}.parquet"]
    msgs = []
    b = load_or_build_trend(snap, cfg, rt, "sha-x", root=tmp_path, log=msgs.append)
    assert any("cache hit" in m for m in msgs)
    pd.testing.assert_frame_equal(a, b, check_exact=True, check_freq=False)
    pd.testing.assert_frame_equal(a, tr, check_exact=True, check_freq=False)
