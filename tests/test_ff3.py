"""
Daily Fama-French three factors (build_ff3_daily, MonthContext.ff3_daily)
against the synthetic snapshot. The fixture has no ARY rows, so this module
copies it and adds annual filings: each December ART row becomes an ARY row
filed 75 days after the fiscal year-end, with taxliabilities = 5% of equity.
Two names carry planted book-equity cases: NEG_BE has negative book equity
every year (must never be in a portfolio) and NO_EQ has equity missing (BE
falls back to assets - liabilities).
"""
import shutil

import numpy as np
import pandas as pd
import pytest

import harness.data_layer as DL
from harness.data_layer import (FF3_PORTS, MonthContext, PanelIndex, Snapshot, _ff3_book_equity,
                                _ff3_name_days, build_ff3_daily, build_market_daily,
                                build_universe, ff3_assignments, ff3_cache_key,
                                ff3_formation_date, load_or_build_ff3, market_cache_key,
                                sha256_file)

NEG_BE, NO_EQ = "T011", "T012"
ARY_LAG = pd.Timedelta(days=75)


def _rehash(root, manifest):
    m = dict(manifest)
    m["tables"] = {k: dict(v) for k, v in m["tables"].items()}
    for t in m["tables"]:
        m["tables"][t]["sha256"] = sha256_file(root / "sharadar" / m["tables"][t]["file"])
    return Snapshot(root / "sharadar", m, verify_hashes=True)


def _add_ary(d):
    sf1 = pd.read_parquet(d / "SF1.parquet")
    ary = sf1[(sf1["dimension"] == "ART") & (sf1["reportperiod"].dt.month == 12)].copy()
    ary = ary.drop_duplicates(["ticker", "reportperiod"], keep="first")
    ary["dimension"] = "ARY"
    ary["datekey"] = ary["reportperiod"] + ARY_LAG
    ary["taxliabilities"] = ary["equity"].abs() * 0.05
    ary.loc[ary["ticker"] == NEG_BE, "equity"] = -ary.loc[ary["ticker"] == NEG_BE, "equity"].abs()
    ary.loc[ary["ticker"] == NO_EQ, "equity"] = np.nan
    pd.concat([sf1, ary], ignore_index=True).to_parquet(d / "SF1.parquet", index=False)


@pytest.fixture(scope="module")
def ary_root(synthetic, tmp_path_factory):
    root = tmp_path_factory.mktemp("ff3") / "base"
    shutil.copytree(synthetic["root"], root)
    _add_ary(root / "sharadar")
    return root


@pytest.fixture(scope="module")
def asnap(ary_root, synthetic):
    return _rehash(ary_root, synthetic["manifest"])


@pytest.fixture(scope="module")
def ff3(asnap, cfg):
    return build_ff3_daily(asnap, cfg, log=lambda *a, **k: None)


@pytest.fixture(scope="module")
def formed(asnap, cfg):
    nd = _ff3_name_days(asnap, cfg)
    be = _ff3_book_equity(asnap)
    assign, bps = ff3_assignments(nd, be, asnap.ticker_meta(), cfg)
    return nd, be, assign, bps


@pytest.fixture(scope="module")
def apidx(panel, asnap, cfg, ff3):
    p = PanelIndex(panel, asnap, cfg)
    p.set_ff3_loader(lambda: ff3)
    return p


def _edited(ary_root, synthetic, tmp_path, edit):
    root = tmp_path / "copy"
    shutil.copytree(ary_root, root)
    edit(root / "sharadar")
    return _rehash(root, synthetic["manifest"])


def _ctx(snap, pidx, cfg, asof):
    u = build_universe(pidx, pd.Timestamp(asof), cfg)
    return MonthContext(snap, pidx, u, pd.Timestamp(asof), cfg, {})


def _raw(asnap):
    sep = pd.read_parquet(asnap.path("SEP"))
    daily = pd.read_parquet(asnap.path("DAILY"))
    sf1 = pd.read_parquet(asnap.path("SF1"))
    return sep, daily, sf1


# ---- the market leg ------------------------------------------------------------

def test_ff3_mkt_is_the_market_series_exactly(asnap, cfg, ff3):
    mkt = build_market_daily(asnap, cfg, log=lambda *a, **k: None)
    assert ff3.index.equals(mkt.index)
    pd.testing.assert_series_equal(ff3["mkt"], mkt["mkt_ret"], check_names=False, check_exact=True)
    assert (ff3["n_names"] == mkt["n_names"]).all()


def test_ff3_smb_hml_start_after_the_first_june_formation(ff3, formed):
    _, _, _, bps = formed
    first = ff3_formation_date(bps["fy"].min())
    # DAILY starts 1992-01 in the fixture, so the first December cap is 1992's
    # and the first formation is June 1993.
    assert bps["fy"].min() == 1993 and first == pd.Timestamp("1993-06-30")
    assert ff3.loc[ff3.index <= first, ["smb", "hml"]].isna().all().all()
    held = ff3.loc[ff3.index > first]
    assert held[["mkt", "smb", "hml"]].notna().all().all()
    assert (held[[f"n_{p}" for p in FF3_PORTS]] >= DL.FF3_MIN_PORT_NAMES).all().all()


# ---- formation: hand computation ---------------------------------------------------

def _hand_assign(asnap, cfg, yy):
    """The June-yy 2x3 sort from the raw parquet, written independently."""
    sep, daily, sf1 = _raw(asnap)
    tk = pd.read_parquet(asnap.path("TICKERS"))
    tk = tk[tk["table"] == "SEP"].set_index("ticker")
    scale = float(cfg["universe"]["daily_marketcap_scale"])
    F = pd.offsets.BMonthEnd().rollback(pd.Timestamp(f"{yy}-06-30"))
    dec_end = pd.offsets.BMonthEnd().rollback(pd.Timestamp(f"{yy - 1}-12-31"))
    traded = set(zip(sep["ticker"], sep["date"]))
    daily = daily[[(t, d) in traded for t, d in zip(daily["ticker"], daily["date"])]]

    def last_cap(lo, hi):
        w = daily[(daily["date"] >= lo) & (daily["date"] <= hi)].sort_values("date")
        return w.groupby("ticker")["marketcap"].last() * scale

    me_jun = last_cap(F - pd.Timedelta(days=7), F)
    me_dec = last_cap(dec_end - pd.Timedelta(days=7), dec_end)
    a = sf1[(sf1["dimension"] == "ARY") & (sf1["reportperiod"].dt.year == yy - 1)
            & (sf1["datekey"] <= F)].sort_values(["reportperiod", "datekey"])
    a = a.groupby("ticker").tail(1).set_index("ticker")
    se = a["equity"].where(a["equity"].notna(), a["assets"] - a["liabilities"])
    be = se + a["taxliabilities"].fillna(0)
    x = pd.DataFrame({"me_jun": me_jun}).join(me_dec.rename("me_dec"), how="inner") \
        .join(be.rename("be"), how="inner")
    x = x[(x["me_jun"] > 0) & (x["me_dec"] > 0) & (x["be"] > 0)]
    x["bm"] = x["be"] / x["me_dec"]
    ny = x[tk["exchange"].reindex(x.index) == "NYSE"]
    s_bp = np.percentile(ny["me_jun"], 50)
    lo, hi = np.percentile(ny["bm"], 30), np.percentile(ny["bm"], 70)
    port = {}
    for t, r in x.iterrows():
        s = "S" if r["me_jun"] <= s_bp else "B"
        v = "L" if r["bm"] <= lo else ("M" if r["bm"] <= hi else "H")
        port[t] = s + v
    return port, (s_bp, lo, hi)


@pytest.mark.parametrize("yy", [1999, 2000])
def test_june_assignment_matches_a_hand_computation(asnap, cfg, formed, synthetic, yy):
    _, _, assign, bps = formed
    want, (s_bp, lo, hi) = _hand_assign(asnap, cfg, yy)
    perma = {str(v): k for k, v in synthetic["perma"].items()}
    got = assign[assign["fy"] == yy]
    got = {perma[i]: p for i, p in zip(got["ID"], got["port"])}
    assert got == want
    assert set(got.values()) == set(FF3_PORTS)
    row = bps.set_index("fy").loc[yy]
    assert row["size_bp"] == pytest.approx(s_bp, rel=1e-12)
    assert (row["bm_lo"], row["bm_hi"]) == (pytest.approx(lo, rel=1e-12), pytest.approx(hi, rel=1e-12))


def test_negative_book_equity_is_never_in_a_portfolio(formed, synthetic):
    nd, _, assign, _ = formed
    neg = str(synthetic["perma"][NEG_BE])
    assert neg in set(nd["ID"])                     # it has prices and caps ...
    assert neg not in set(assign["ID"])             # ... and is still excluded


def test_missing_equity_falls_back_to_assets_minus_liabilities(asnap, formed, synthetic):
    _, _, assign, _ = formed
    no_eq = str(synthetic["perma"][NO_EQ])
    got = assign[(assign["ID"] == no_eq) & (assign["fy"] == 2000)]
    assert len(got) == 1
    sf1 = pd.read_parquet(asnap.path("SF1"))
    r = sf1[(sf1["ticker"] == NO_EQ) & (sf1["dimension"] == "ARY")
            & (sf1["reportperiod"] == pd.Timestamp("1999-12-31"))].iloc[0]
    assert np.isnan(r["equity"])
    assert got["be"].iloc[0] == pytest.approx(r["assets"] - r["liabilities"] + r["taxliabilities"])


# ---- formation: point in time -----------------------------------------------------

def test_june_formation_uses_only_filings_with_datekey_on_or_before_formation(asnap, cfg, formed):
    nd, be, assign, _ = formed
    meta = asnap.ticker_meta()
    yy = 2000
    F = ff3_formation_date(yy)
    base = assign[assign["fy"] == yy].set_index("ID")["port"]
    victim = base.index[0]
    fy_rows = (be["ID"] == victim) & (be["reportperiod"].dt.year == yy - 1)
    assert fy_rows.sum() == 1

    # (a) The FY(y-1) 10-K filed the day AFTER formation: the name has no
    # book equity that June and drops out; every other name is unchanged.
    late = be.copy()
    late.loc[fy_rows, "datekey"] = F + pd.Timedelta(days=1)
    a2, _ = ff3_assignments(nd, late, meta, cfg)
    got = a2[a2["fy"] == yy].set_index("ID")["port"]
    assert victim not in got.index
    # (b) Filed ON the formation date: usable.
    on = be.copy()
    on.loc[fy_rows, "datekey"] = F
    a3, _ = ff3_assignments(nd, on, meta, cfg)
    pd.testing.assert_series_equal(a3[a3["fy"] == yy].set_index("ID")["port"], base)
    # (c) A restatement of the same fiscal year filed after F, with a wildly
    # different book equity, cannot reach the June-y sort.
    rest = be[fy_rows].assign(datekey=F + pd.Timedelta(days=30), be=be.loc[fy_rows, "be"] * 1e4)
    a4, b4 = ff3_assignments(nd, pd.concat([be, rest], ignore_index=True), meta, cfg)
    pd.testing.assert_frame_equal(a4[a4["fy"] == yy].reset_index(drop=True),
                                  assign[assign["fy"] == yy].reset_index(drop=True))
    # And June y+1 reads fiscal year y only, so the FY y-1 restatement is
    # invisible there too.
    assert (a4[a4["fy"] == yy + 1]["be"].to_numpy() == assign[assign["fy"] == yy + 1]["be"].to_numpy()).all()


# ---- daily portfolio returns: hand computation and sign conventions ------------------

def _members(assign, synthetic, yy, ports):
    perma = {str(v): k for k, v in synthetic["perma"].items()}
    a = assign[(assign["fy"] == yy) & assign["port"].isin(ports)]
    return sorted(perma[i] for i in a["ID"])


def _hand_vw(sep, daily, day, prev, tickers):
    a = sep[sep["date"] == prev].set_index("ticker")["closeadj"]
    b = sep[sep["date"] == day].set_index("ticker")["closeadj"]
    w = daily[daily["date"] == prev].set_index("ticker")["marketcap"]
    both = sorted(set(a.index) & set(b.index) & set(w.index) & set(tickers))
    r = b[both] / a[both] - 1.0
    return float((w[both] * r).sum() / w[both].sum()), len(both)


def test_portfolio_returns_are_prior_day_cap_weighted_and_factors_follow_the_formulas(asnap, ff3, formed, synthetic):
    _, _, assign, _ = formed
    sep, daily, _ = _raw(asnap)
    day, prev = pd.Timestamp("2000-03-15"), pd.Timestamp("2000-03-14")
    for p in FF3_PORTS:
        want, n = _hand_vw(sep, daily, day, prev, _members(assign, synthetic, 1999, [p]))
        assert ff3.loc[day, f"r_{p}"] == pytest.approx(want, rel=1e-12), p
        assert int(ff3.loc[day, f"n_{p}"]) == n, p
    row = ff3.loc[day]
    r = {p: row[f"r_{p}"] for p in FF3_PORTS}
    assert row["smb"] == pytest.approx((r["SL"] + r["SM"] + r["SH"]) / 3 - (r["BL"] + r["BM"] + r["BH"]) / 3)
    assert row["hml"] == pytest.approx((r["SH"] + r["BH"]) / 2 - (r["SL"] + r["BL"]) / 2)
    # The first July trading day holds the June assignment of the SAME year
    # (its return runs from the June-end close); June 30 still holds last year's.
    jul, jun = pd.Timestamp("2000-07-03"), pd.Timestamp("2000-06-30")
    want, _ = _hand_vw(sep, daily, jul, jun, _members(assign, synthetic, 2000, ["SL"]))
    assert ff3.loc[jul, "r_SL"] == pytest.approx(want, rel=1e-12)
    want, _ = _hand_vw(sep, daily, jun, pd.Timestamp("2000-06-29"), _members(assign, synthetic, 1999, ["SL"]))
    assert ff3.loc[jun, "r_SL"] == pytest.approx(want, rel=1e-12)


def _shock(tickers, day, k=1.05):
    """Edit: a one-day jump of k on `day` for `tickers` (closeadj from `day`
    on is scaled, so only day's return moves; caps and dollar volume are
    untouched, so no formation or weight moves)."""
    def edit(d):
        sp = pd.read_parquet(d / "SEP.parquet")
        m = sp["ticker"].isin(tickers) & (sp["date"] >= day)
        sp.loc[m, "closeadj"] *= k
        sp.to_parquet(d / "SEP.parquet", index=False)
    return edit


@pytest.mark.parametrize("side", ["small", "value"])
def test_smb_and_hml_sign_conventions(ary_root, synthetic, cfg, ff3, formed, tmp_path, side):
    """+5% on every SMALL name moves SMB up by 5% x (1 + mean small-portfolio
    return) and HML by only the small-value vs small-growth spread; +5% on
    every HIGH-B/M name moves HML up by 5% x (1 + mean value return)."""
    _, _, assign, _ = formed
    day = pd.Timestamp("2000-03-15")
    ports = ["SL", "SM", "SH"] if side == "small" else ["SH", "BH"]
    snap2 = _edited(ary_root, synthetic, tmp_path, _shock(_members(assign, synthetic, 1999, ports), day))
    f2 = build_ff3_daily(snap2, cfg, log=lambda *a, **k: None)
    r = {p: ff3.loc[day, f"r_{p}"] for p in FF3_PORTS}
    d_smb = f2.loc[day, "smb"] - ff3.loc[day, "smb"]
    d_hml = f2.loc[day, "hml"] - ff3.loc[day, "hml"]
    if side == "small":
        assert d_smb == pytest.approx(0.05 * (1 + (r["SL"] + r["SM"] + r["SH"]) / 3), rel=1e-9)
        assert d_hml == pytest.approx(0.025 * (r["SH"] - r["SL"]), abs=1e-12)
        assert d_smb > 0.04
    else:
        assert d_hml == pytest.approx(0.05 * (1 + (r["SH"] + r["BH"]) / 2), rel=1e-9)
        assert d_smb == pytest.approx(0.05 * (r["SH"] - r["BH"]) / 3, abs=1e-12)
        assert d_hml > 0.04
    # Only the shocked day moves.
    other = f2.index != day
    pd.testing.assert_frame_equal(f2.loc[other, ["smb", "hml"]], ff3.loc[other, ["smb", "hml"]],
                                  check_exact=False, rtol=1e-12, atol=1e-15)


# ---- causality and guards ------------------------------------------------------------

def _cut_after(day):
    """Edit: delete every SEP / DAILY row dated after `day` and every SF1 row
    filed after it."""
    def edit(d):
        for t in ("SEP", "DAILY"):
            x = pd.read_parquet(d / f"{t}.parquet")
            x[x["date"] <= day].to_parquet(d / f"{t}.parquet", index=False)
        s = pd.read_parquet(d / "SF1.parquet")
        s[s["datekey"] <= day].to_parquet(d / "SF1.parquet", index=False)
    return edit


@pytest.mark.parametrize("cut", ["2000-06-30", "2000-07-14", "2001-03-07"])
def test_ff3_is_causal_no_value_moves_when_later_rows_are_deleted(ary_root, synthetic, cfg, ff3,
                                                                   tmp_path, cut):
    cut = pd.Timestamp(cut)
    snap2 = _edited(ary_root, synthetic, tmp_path, _cut_after(cut))
    trunc = build_ff3_daily(snap2, cfg, log=lambda *a, **k: None)
    assert trunc.index.max() == cut and ff3.index.max() > cut
    pd.testing.assert_frame_equal(ff3.loc[ff3.index <= cut], trunc, check_exact=True)


def test_ff3_ignores_stray_date_rows(ary_root, synthetic, cfg, ff3, tmp_path):
    """A name printing on a Saturday must not become every other name's prior
    day (as in the market builder), and a stray row after a December
    business month-end with an absurd cap must not reach the B/M sort."""
    sat, fri = pd.Timestamp("2000-02-12"), pd.Timestamp("2000-02-11")
    sat_dec, fri_dec = pd.Timestamp("2000-12-30"), pd.Timestamp("2000-12-29")

    def edit(d):
        for t in ("SEP", "DAILY"):
            x = pd.read_parquet(d / f"{t}.parquet")
            a = x[(x["ticker"] == "T005") & (x["date"] == fri)].assign(date=sat)
            b = x[(x["ticker"] == "T006") & (x["date"] == fri_dec)].assign(date=sat_dec)
            if t == "DAILY":
                b = b.assign(marketcap=b["marketcap"] * 1e3)
            pd.concat([x, a, b], ignore_index=True).to_parquet(d / f"{t}.parquet", index=False)

    snap2 = _edited(ary_root, synthetic, tmp_path, edit)
    f2 = build_ff3_daily(snap2, cfg, log=lambda *a, **k: None)
    assert sat not in f2.index and sat_dec not in f2.index
    assert f2.attrs["n_stray_rows"] == 2
    pd.testing.assert_frame_equal(f2, ff3, check_exact=True)


def test_ff3_refuses_a_thin_breakpoint_sample(ary_root, synthetic, cfg, tmp_path):
    def edit(d):
        tk = pd.read_parquet(d / "TICKERS.parquet")
        tk["exchange"] = "NASDAQ"
        tk.loc[tk["ticker"].isin(["T000", "T002"]), "exchange"] = "NYSE"
        tk.to_parquet(d / "TICKERS.parquet", index=False)

    snap2 = _edited(ary_root, synthetic, tmp_path, edit)
    with pytest.raises(RuntimeError, match="eligible NYSE"):
        build_ff3_daily(snap2, cfg, log=lambda *a, **k: None)


# ---- the accessor ------------------------------------------------------------------------

def test_ff3_daily_is_bounded_by_the_signal_date(asnap, apidx, cfg, ff3):
    ctx = _ctx(asnap, apidx, cfg, "2000-06-30")
    assert ff3.index.max() > pd.Timestamp("2000-06-30")          # later days exist to leak
    got = ctx.ff3_daily(60)
    assert list(got.columns) == ["mkt", "smb", "hml"]
    assert got.index.max() == pd.Timestamp("2000-06-30")
    assert got.index.min() > pd.Timestamp("2000-06-30") - pd.Timedelta(days=60)
    assert got.notna().all().all() and len(got) >= 40
    # Same calendar and the same mkt as market_daily.
    md = ctx.market_daily(60)
    assert got.index.equals(md.index)
    assert (got["mkt"].to_numpy() == md.to_numpy()).all()


def test_ff3_daily_serves_complete_rows_and_honours_min_days(asnap, apidx, cfg):
    ctx = _ctx(asnap, apidx, cfg, "2000-06-30")
    n = len(ctx.ff3_daily(365))
    assert n > 200
    assert len(ctx.ff3_daily(365, min_days=n)) == n
    assert ctx.ff3_daily(365, min_days=n + 1).empty
    # Just after the first formation: mkt exists for a year, smb/hml for a month.
    ctx2 = _ctx(asnap, apidx, cfg, "1993-07-30")
    w = ctx2.ff3_daily(365)
    assert 15 <= len(w) <= 23 and w.index.min() > pd.Timestamp("1993-06-30")
    assert len(ctx2.market_daily(365)) > 200
    assert ctx2.ff3_daily(365, min_days=200).empty


def test_ff3_loader_is_called_once_and_only_on_demand(panel, asnap, cfg, ff3):
    calls = []
    p = PanelIndex(panel, asnap, cfg)
    p.set_ff3_loader(lambda: calls.append(1) or ff3)
    assert calls == []
    ctx = _ctx(asnap, p, cfg, "2000-06-30")
    ctx.market_context()
    assert calls == []
    ctx.ff3_daily(30)
    ctx.ff3_daily(60)
    assert calls == [1]


# ---- cache -------------------------------------------------------------------------------

def test_ff3_cache_key_moves_with_the_builder_source(cfg, monkeypatch):
    k0 = ff3_cache_key("abc", cfg)
    assert k0 == ff3_cache_key("abc", cfg)
    assert k0 != ff3_cache_key("abd", cfg)
    assert k0 != market_cache_key("abc", cfg)
    monkeypatch.setattr(DL.inspect, "getsource", lambda f: "changed " + f.__name__)
    assert ff3_cache_key("abc", cfg) != k0


def test_ff3_cache_key_moves_with_a_builder_constant(cfg, monkeypatch):
    k0 = ff3_cache_key("abc", cfg)
    monkeypatch.setattr(DL, "FF3_BM_PCTLS", (0.2, 0.8))
    assert ff3_cache_key("abc", cfg) != k0


def test_load_or_build_ff3_caches_on_disk(asnap, cfg, ff3, tmp_path):
    rt = {"cache": {"dir": str(tmp_path / "cache"), "enabled": True}}
    a = load_or_build_ff3(asnap, cfg, rt, "sha-x", root=tmp_path, log=lambda *a, **k: None)
    files = list((tmp_path / "cache").glob("ff3_daily_*.parquet"))
    assert [f.name for f in files] == [f"ff3_daily_{ff3_cache_key('sha-x', cfg)}.parquet"]
    msgs = []
    b = load_or_build_ff3(asnap, cfg, rt, "sha-x", root=tmp_path, log=msgs.append)
    assert any("cache hit" in m for m in msgs)
    pd.testing.assert_frame_equal(a, b, check_exact=True)
    pd.testing.assert_frame_equal(a, ff3, check_exact=True)
