"""
The data layer against the synthetic snapshot: point-in-time universe,
survivorship, fundamentals as-of, delisting returns, the history gate.
Every property here was a lesson the BQuant project paid for in a run.
"""
import numpy as np
import pandas as pd
import pytest

from harness.data_layer import (MonthContext, Snapshot, build_rebalance_schedule,
                                build_universe, classify_delistings, forward_returns,
                                membership, screen_month, to_bme)
from tests.fixtures import synthetic_snapshot as S


def _alive_in(universe, synthetic):
    """An ordinary fixture name (Txxx) that survived the month's relative
    screens; the screens drop ~20% of them, so no fixed name is guaranteed."""
    ids = set(universe.index)
    for i in range(60):
        t = f"T{i:03d}"
        if str(synthetic["perma"][t]) in ids:
            return t
    raise AssertionError("no ordinary name survived the universe screens")


def _ctx(snap, pidx, cfg, asof):
    u = build_universe(pidx, pd.Timestamp(asof), cfg)
    return MonthContext(snap, pidx, u, pd.Timestamp(asof), cfg, {}), u


# ---- snapshot integrity -----------------------------------------------------

def test_snapshot_refuses_a_file_that_does_not_match_its_manifest(synthetic, tmp_path):
    import shutil
    bad = tmp_path / "bad"
    shutil.copytree(synthetic["root"], bad)
    p = bad / "sharadar" / "ACTIONS.parquet"
    p.write_bytes(p.read_bytes() + b"\x00")
    with pytest.raises(RuntimeError, match="DOES NOT MATCH"):
        Snapshot(bad / "sharadar", synthetic["manifest"], verify_hashes=True)


def test_snapshot_refuses_an_empty_manifest(synthetic):
    with pytest.raises(RuntimeError, match="No snapshot"):
        Snapshot(synthetic["root"] / "sharadar", {"status": "EMPTY", "tables": {}})


def test_ticker_map_is_permaticker_strings(snap, synthetic):
    m = snap.ticker_map("SEP")
    assert m["T000"] == str(synthetic["perma"]["T000"])
    assert m.dtype == object


# ---- calendar ---------------------------------------------------------------

def test_schedule_signal_precedes_return_window():
    sched = build_rebalance_schedule("1999-01-01", "1999-12-31")
    assert len(sched) == 12
    for reb, sig, rs, re_ in sched:
        assert sig < rs <= re_
        assert sig.month != rs.month or sig.year != rs.year


def test_schedule_clips_at_eval_end_never_past_it():
    sched = build_rebalance_schedule("1999-01-01", "1999-06-15")
    assert sched[-1][3] == pd.Timestamp("1999-06-15")


def test_to_bme_rolls_weekend_month_ends_back_not_forward():
    # 1999-01-31 is a Sunday; the business month-end is Friday the 29th.
    assert to_bme([pd.Timestamp("1999-01-15")]).iloc[0] == pd.Timestamp("1999-01-29")
    assert to_bme([pd.Timestamp("1999-03-10")]).iloc[0] == pd.Timestamp("1999-03-31")


# ---- point-in-time universe --------------------------------------------------

def test_universe_applies_every_screen(snap, pidx, cfg, synthetic):
    u = build_universe(pidx, pd.Timestamp("1999-01-29"), cfg)
    ids = set(u.index)
    perma = synthetic["perma"]
    # The relative cuts drop roughly the bottom 20% by cap and then by ADV, so
    # most ordinary names survive and T000 is not guaranteed to.
    alive = [str(perma[f"T{i:03d}"]) for i in range(60)]
    assert 0.55 <= sum(a in ids for a in alive) / len(alive) <= 0.9
    assert str(perma[S.PENNY]) not in ids, "sub-$1 name must be screened out"
    assert str(perma[S.TINY]) not in ids, "microcap name must be screened out by the relative size cut"
    assert str(perma[S.LATE_LISTING]) not in ids, "not yet listed"
    assert (u["px_usd"] >= 1.0).all()
    # Relative screens with the hysteresis band: a name NOT retained by the band
    # is at or above the month's ENTRY cuts; a retained prior member is at or
    # above the EXIT cuts (which sit below the entry cuts).
    assert u["size_cut_usd"].nunique() == 1 and u["adv_cut_usd"].nunique() == 1
    assert u["size_cut_usd"].iloc[0] > 0 and u["adv_cut_usd"].iloc[0] > 0
    fresh = u[~u["retained_by_band"]]
    assert (fresh["mkt_cap_usd"] >= fresh["size_cut_usd"]).all() and (fresh["adv_usd"] >= fresh["adv_cut_usd"]).all()
    kept = u[u["retained_by_band"]]
    assert (kept["mkt_cap_usd"] >= kept["size_exit_cut_usd"]).all() and (kept["adv_usd"] >= kept["adv_exit_cut_usd"]).all()
    assert (u["size_exit_cut_usd"] <= u["size_cut_usd"]).all() and (u["adv_exit_cut_usd"] <= u["adv_cut_usd"]).all()
    assert set(u["region"]) == {"US"}
    assert set(u["liq_tier"]) <= {"MEGA", "MID", "SMALL"}


# ---- membership hysteresis (V3 universe rule) ----------------------------------

def test_hysteresis_keeps_a_prior_member_between_the_exit_and_entry_cuts(pidx, cfg):
    """With every name a prior member, anyone between the exit and entry cuts
    is retained; with no prior members the screens are the plain entry cuts."""
    me = pd.Timestamp("1999-06-30")
    cold = screen_month(pidx, me, cfg, None)
    empty_prev = screen_month(pidx, me, cfg, frozenset())
    assert set(cold.index) == set(empty_prev.index) and not empty_prev["retained_by_band"].any()
    everyone = frozenset(pidx.month_rows(me)["ID"].astype(str))
    warm = screen_month(pidx, me, cfg, everyone)
    assert set(warm.index) >= set(cold.index)
    extra = warm.loc[sorted(set(warm.index) - set(cold.index))]
    assert len(extra) > 0, "the band between the 15th and 20th percentiles should hold some names"
    assert extra["retained_by_band"].all()
    below_entry = (extra["mkt_cap_usd"] < extra["size_cut_usd"]) | (extra["adv_usd"] < extra["adv_cut_usd"])
    assert below_entry.all()
    assert (extra["mkt_cap_usd"] >= extra["size_exit_cut_usd"]).all() and (extra["adv_usd"] >= extra["adv_exit_cut_usd"]).all()


def test_membership_is_a_function_of_data_and_month_not_of_call_order(pidx, cfg):
    """The chain starts cold at the first panel month, so asking for 1999-12
    first or after 1999-06 yields the same universe."""
    m1, m2 = pd.Timestamp("1999-06-30"), pd.Timestamp("1999-12-31")
    pidx.membership.clear()
    direct = set(build_universe(pidx, m2, cfg).index)
    pidx.membership.clear()
    build_universe(pidx, m1, cfg)
    after = set(build_universe(pidx, m2, cfg).index)
    assert direct == after
    assert membership(pidx, m2, cfg) == frozenset(direct)


def test_the_chained_universe_contains_the_cold_universe_and_equals_it_without_hysteresis(pidx, cfg):
    import copy
    off = copy.deepcopy(cfg); off["universe"]["membership_hysteresis"] = False
    for me in pd.date_range("1999-03-31", "2000-02-29", freq="BME"):
        chained = set(build_universe(pidx, me, cfg).index)
        cold = set(screen_month(pidx, me, cfg, None).index)
        assert chained >= cold
        assert set(build_universe(pidx, me, off).index) == cold


def test_universe_is_point_in_time_not_survivorship_filtered(pidx, cfg, synthetic):
    """The performance-delisted name is IN the universe before it delists and
    OUT after — the screen is applied to that month's rows, not today's list."""
    p = str(synthetic["perma"][S.DELIST_PERF])
    assert p in build_universe(pidx, pd.Timestamp("1999-06-30"), cfg).index
    assert p not in build_universe(pidx, pd.Timestamp("1999-12-31"), cfg).index


def test_late_listing_enters_when_it_lists(pidx, cfg, synthetic):
    p = str(synthetic["perma"][S.LATE_LISTING])
    assert p not in build_universe(pidx, pd.Timestamp("1999-06-30"), cfg).index
    assert p in build_universe(pidx, pd.Timestamp("1999-12-31"), cfg).index


def test_stale_price_excludes_a_name(pidx, cfg, synthetic):
    """A name whose last trade is older than the staleness window at the signal
    date is not tradable there."""
    p = str(synthetic["perma"][S.DELIST_PERF])
    # PERF_LAST is 1999-09-15; the 1999-09-30 month-end is 15 days later.
    assert p not in build_universe(pidx, pd.Timestamp("1999-09-30"), cfg).index


# ---- fundamentals as-of -------------------------------------------------------

def test_fundamentals_use_the_latest_filing_on_or_before_the_signal(snap, pidx, cfg, synthetic):
    ctx, u = _ctx(snap, pidx, cfg, "1999-06-30")
    f = ctx.fundamentals(["assets"])
    assert (f["datekey"].dropna() <= pd.Timestamp("1999-06-30")).all()
    assert f["assets"].notna().mean() > 0.9


def test_restatement_filed_later_is_invisible_at_the_earlier_signal(snap, pidx, cfg, synthetic):
    """RESTATED's 1998-12-31 assets were 1000 when filed 1999-02-14 and were
    restated to 5000 on 1999-08-01. A 1999-04-30 signal (after the original
    filing, before Q1's on 1999-05-15) must see 1000. A 1999-08-06 signal
    (after the restatement, before Q2's filing on 1999-08-14) sees the
    restated row, because it is the latest by datekey."""
    p = str(synthetic["perma"][S.RESTATED])
    ctx, _ = _ctx(snap, pidx, cfg, "1999-04-30")
    assert ctx.fundamentals(["assets"]).loc[p, "assets"] == 1000.0
    # 1999-08-06 is not a month-end, so build the universe at July's and set
    # the signal date on the context directly.
    u = build_universe(pidx, pd.Timestamp("1999-07-30"), cfg)
    ctx2 = MonthContext(snap, pidx, u, pd.Timestamp("1999-08-06"), cfg, {})
    got = ctx2.fundamentals(["assets"]).loc[p]
    assert got["datekey"] == pd.Timestamp("1999-08-01") and got["assets"] == 5000.0


def test_lagged_fundamentals_are_as_known_then(snap, pidx, cfg, synthetic):
    """assets 12 months ago = the latest filing with datekey <= signal - 12m,
    NOT the earlier period's figure as known today."""
    p = str(synthetic["perma"][S.RESTATED])
    ctx, _ = _ctx(snap, pidx, cfg, "2000-04-28")
    lag = ctx.fundamentals(["assets"], lag_months=12)      # target 1999-04-28
    assert lag.loc[p, "datekey"] == pd.Timestamp("1999-02-14")
    assert lag.loc[p, "assets"] == 1000.0, "the restated 5000 (filed 1999-08-01) must not leak back"


def test_fundamentals_respect_the_dimension(snap, pidx, cfg):
    ctx, _ = _ctx(snap, pidx, cfg, "1999-06-30")
    art = ctx.fundamentals(["assets"])
    arq = ctx.fundamentals(["assets"], dimension="ARQ")
    assert (art["assets"].dropna() > 0).all()
    # Twenty 1999-Q1 ARQ rows in the fixture carry assets = -1; ART never does.
    assert (arq["assets"].dropna() == -1.0).any()


def test_stale_filing_beyond_the_age_limit_is_missing(snap, pidx, cfg, synthetic):
    """DELIST_PERF stopped filing after 1999-09; by 2001-06 its last filing is
    >15 months old — but it is not in the universe then anyway. Use a manual
    context on the full ID set instead."""
    p = str(synthetic["perma"][S.DELIST_PERF])
    u = build_universe(pidx, pd.Timestamp("1999-06-30"), cfg)
    ctx = MonthContext(snap, pidx, u, pd.Timestamp("2001-06-29"), cfg, {})
    f = ctx.fundamentals(["assets"])
    assert np.isnan(f.loc[p, "assets"])


# ---- returns and delistings ---------------------------------------------------

def test_forward_return_is_the_closeadj_ratio(snap, pidx, cfg, synthetic):
    u = build_universe(pidx, pd.Timestamp("1999-06-30"), cfg)
    fr = forward_returns(pidx, u, "1999-06-30", pd.Timestamp("1999-07-30"), cfg)
    tkr = _alive_in(u, synthetic)
    p = str(synthetic["perma"][tkr])
    sep = snap.table("SEP")
    s = sep[sep["ticker"] == tkr].set_index("date")["closeadj"]
    expect = s.loc["1999-07-30"] / s.loc["1999-06-30"] - 1
    assert fr.loc[p, "monthly_ret"] == pytest.approx(expect)
    assert fr.loc[p, "ret_kind"] == "full"


def test_delisting_classification(pidx, synthetic):
    d = pidx.delist
    assert d.loc[str(synthetic["perma"][S.DELIST_PERF]), "kind"] == "performance"
    assert d.loc[str(synthetic["perma"][S.DELIST_MERGER]), "kind"] == "merger"
    assert d.loc[str(synthetic["perma"]["T000"]), "kind"] == "none"


def test_performance_delisting_earns_the_shumway_haircut(snap, pidx, cfg, synthetic):
    """PERF's last trade is 1999-09-15, inside the September window."""
    u = build_universe(pidx, pd.Timestamp("1999-08-31"), cfg)
    p = str(synthetic["perma"][S.DELIST_PERF])
    assert p in u.index
    fr = forward_returns(pidx, u, "1999-08-31", pd.Timestamp("1999-09-30"), cfg)
    sep = snap.table("SEP")
    s = sep[sep["ticker"] == S.DELIST_PERF].set_index("date")["closeadj"]
    partial = s.loc[S.PERF_LAST] / s.loc["1999-08-31"] - 1
    expect = (1 + partial) * (1 + cfg["returns"]["delisting"]["performance_return"]) - 1
    assert fr.loc[p, "monthly_ret"] == pytest.approx(expect)
    assert fr.loc[p, "ret_kind"] == "partial_delisted_performance"


def test_merger_delisting_earns_only_the_partial_return(snap, pidx, cfg, synthetic):
    u = build_universe(pidx, pd.Timestamp("2000-02-29"), cfg)
    p = str(synthetic["perma"][S.DELIST_MERGER])
    fr = forward_returns(pidx, u, "2000-02-29", pd.Timestamp("2000-03-31"), cfg)
    sep = snap.table("SEP")
    s = sep[sep["ticker"] == S.DELIST_MERGER].set_index("date")["closeadj"]
    partial = s.loc[S.MERGER_LAST] / s.loc["2000-02-29"] - 1
    assert fr.loc[p, "monthly_ret"] == pytest.approx(partial)
    assert fr.loc[p, "ret_kind"] == "partial_delisted_merger"


def test_delisting_convention_is_read_from_config(snap, pidx, cfg, synthetic):
    import copy
    c2 = copy.deepcopy(cfg)
    c2["returns"]["delisting"]["performance_return"] = -1.0
    u = build_universe(pidx, pd.Timestamp("1999-08-31"), c2)
    fr = forward_returns(pidx, u, "1999-08-31", pd.Timestamp("1999-09-30"), c2)
    assert fr.loc[str(synthetic["perma"][S.DELIST_PERF]), "monthly_ret"] == pytest.approx(-1.0)


# ---- history gate -------------------------------------------------------------

def test_history_gate_excludes_a_name_without_a_price_at_the_window_start(snap, pidx, cfg, synthetic):
    """LATE lists 1999-07-01. At the 1999-12-31 signal it has no price 12
    months back, so a 12-month gate must be False; at 2000-12-29 it is True."""
    p = str(synthetic["perma"][S.LATE_LISTING])
    ctx, _ = _ctx(snap, pidx, cfg, "1999-12-31")
    assert not ctx.has_price_at(12).loc[p]
    assert ctx.has_price_at(12).loc[str(synthetic["perma"][_alive_in(_, synthetic)])]
    ctx2, _ = _ctx(snap, pidx, cfg, "2000-12-29")
    assert ctx2.has_price_at(12).loc[p]


def test_monthly_closeadj_is_bounded_by_the_signal(snap, pidx, cfg):
    ctx, _ = _ctx(snap, pidx, cfg, "1999-12-31")
    px = ctx.monthly_closeadj(12)
    assert px.columns.max() == pd.Timestamp("1999-12-31")
    assert px.columns.min() >= pd.Timestamp("1998-12-31")


def test_daily_is_bounded_by_the_signal(snap, pidx, cfg):
    ctx, _ = _ctx(snap, pidx, cfg, "1999-12-31")
    d = ctx.daily("SEP", ["closeadj", "volume"], 30)
    assert d["date"].max() <= pd.Timestamp("1999-12-31")
    assert d["date"].min() > pd.Timestamp("1999-12-01")
    assert set(d["ID"]) <= set(ctx.ids)


def test_at_month_end_reads_the_business_month_end_not_the_calendar_date(snap, pidx, cfg):
    # 2000-06-30 minus 6 months is 1999-12-30 by calendar arithmetic, but the
    # business month-end is 1999-12-31: the row read must be that one.
    ctx, _ = _ctx(snap, pidx, cfg, "2000-06-30")
    got = ctx.at_month_end("SEP", ["close"], 6)
    dates = got["date"].dropna()
    assert len(dates) > 0
    assert (dates <= pd.Timestamp("1999-12-31")).all()
    assert (dates >= pd.Timestamp("1999-12-24")).all()
    assert (dates == pd.Timestamp("1999-12-31")).mean() > 0.9


def test_at_month_end_is_bounded_by_the_signal(snap, pidx, cfg):
    ctx, _ = _ctx(snap, pidx, cfg, "1999-12-31")
    got = ctx.at_month_end("DAILY", ["marketcap"], 0)
    assert got["date"].dropna().max() <= pd.Timestamp("1999-12-31")
    assert list(got.index) == list(ctx.ids)


def test_at_month_ends_matches_at_month_end_lag_by_lag(snap, pidx, cfg):
    ctx, _ = _ctx(snap, pidx, cfg, "2000-06-30")
    many = ctx.at_month_ends("SEP", ["close"], [0, 6, 18])
    for m in (0, 6, 18):
        one = ctx.at_month_end("SEP", ["close"], m).dropna(subset=["date"])
        got = many[many["months_back"] == m].set_index("ID")
        assert set(got.index) == set(one.index)
        assert (got.loc[one.index, "date"] == one["date"]).all()
        assert (got.loc[one.index, "close"] == one["close"]).all()


# ---- direct-API naming ----------------------------------------------------------

def test_modern_sf1_and_tickers_names_load(synthetic, tmp_path):
    """The direct API names the SF1 filing date `date` and scopes tickers by
    `stocks` / `fundamentals`. A snapshot in that shape must load identically."""
    import shutil
    from harness.provenance import data_sha
    root = tmp_path / "modern"; shutil.copytree(synthetic["root"], root)
    sf1 = pd.read_parquet(root / "sharadar" / "SF1.parquet").rename(columns={"datekey": "date"})
    sf1.to_parquet(root / "sharadar" / "SF1.parquet", index=False)
    tk = pd.read_parquet(root / "sharadar" / "TICKERS.parquet")
    tk["table"] = tk["table"].map({"SEP": "stocks", "SF1": "fundamentals"})
    tk.to_parquet(root / "sharadar" / "TICKERS.parquet", index=False)
    from harness.data_layer import Snapshot, sha256_file
    m = dict(synthetic["manifest"]); m["tables"] = {k: dict(v) for k, v in m["tables"].items()}
    for t in ("SF1", "TICKERS"):
        m["tables"][t]["sha256"] = sha256_file(root / "sharadar" / f"{t}.parquet")
    snap = Snapshot(root / "sharadar", m, verify_hashes=True)
    assert "datekey" in snap.columns("SF1")
    assert "datekey" in snap.table("SF1", ["ticker", "dimension", "datekey", "reportperiod"]).columns
    assert snap.ticker_map("SEP")["T000"] == str(synthetic["perma"]["T000"])
    assert snap.ticker_map("SF1")["T000"] == str(synthetic["perma"]["T000"])
    assert "exchange" in snap.ticker_meta().columns


def test_price_window_includes_the_start_month_when_its_calendar_date_is_a_weekend(snap, pidx, cfg, synthetic):
    """2001-12-31 minus 12 months is Sunday 2000-12-31; December 2000's
    business month-end is Friday the 29th. The window must include it.
    The defect this guards was silent momentum NaNs in ~22% of months on the
    first real baseline run."""
    from factors.composite import MOMENTUM
    u = build_universe(pidx, pd.Timestamp("2001-12-31"), cfg)
    ctx = MonthContext(snap, pidx, u, pd.Timestamp("2001-12-31"), cfg, {})
    px = ctx.monthly_closeadj(12)
    assert px.columns.min() == pd.Timestamp("2000-12-29")
    assert len(px.columns) == 13
    mom = MOMENTUM.compute(ctx)
    p = str(synthetic["perma"][_alive_in(u, synthetic)])
    assert mom.loc[p] == mom.loc[p]  # not NaN
    assert mom.notna().mean() > 0.9


def test_ticker_meta_accessor_returns_current_classifications(snap, pidx, cfg, synthetic):
    ctx, u = _ctx(snap, pidx, cfg, "1999-06-30")
    m = ctx.ticker_meta(["siccode", "sector"])
    assert list(m.index) == list(ctx.ids)
    assert (m["siccode"] == 3000).all()
    with pytest.raises(KeyError):
        ctx.ticker_meta(["not_a_column"])


def test_fundamentals_history_is_point_in_time_and_period_aligned(snap, pidx, cfg, synthetic):
    """Quarterly ART rows in the fixture file 45 days after each quarter end.
    At 1999-06-30 the latest KNOWN filing is Q1 1999 (filed 1999-05-15); the
    1999-06-30 quarter itself is not yet filed. RESTATED's restatement of
    1998-12-31 (filed 1999-08-01) must not appear at a 1999-06-30 signal, and
    must supersede the original at a 1999-09-30 signal."""
    p = str(synthetic["perma"][S.RESTATED])
    ctx, u = _ctx(snap, pidx, cfg, "1999-06-30")
    h = ctx.fundamentals_history(["assets"], 4)
    assert (h["datekey"] <= pd.Timestamp("1999-06-30")).all()
    mine = h[h["ID"] == p].set_index("q_back")
    assert mine.loc[0, "reportperiod"] == pd.Timestamp("1999-03-31")
    assert mine.loc[1, "reportperiod"] == pd.Timestamp("1998-12-31")
    assert mine.loc[1, "assets"] == 1000.0
    assert set(h.groupby("ID").size().unique()) <= {4}
    ctx2, _ = _ctx(snap, pidx, cfg, "1999-09-30")
    h2 = ctx2.fundamentals_history(["assets"], 4)
    m2 = h2[h2["ID"] == p].set_index("reportperiod")
    assert m2.loc[pd.Timestamp("1998-12-31"), "assets"] == 5000.0
    assert m2.loc[pd.Timestamp("1998-12-31"), "datekey"] == pd.Timestamp("1999-08-01")


def test_fundamentals_yoy_aligns_by_report_period_and_is_point_in_time(snap, pidx, cfg, synthetic):
    """At 1999-06-30 the latest known quarter is 1999-03-31, so the year-ago
    period is 1998-03-31. At 2000-03-31 the latest is 1999-12-31 and its
    year-ago period is RESTATED's 1998-12-31, whose restatement (filed
    1999-08-01) is public by then and must be the value returned; at
    1999-06-30 that restatement must not be visible anywhere."""
    p = str(synthetic["perma"][S.RESTATED])
    ctx, _ = _ctx(snap, pidx, cfg, "1999-06-30")
    y = ctx.fundamentals_yoy(["assets"])
    assert list(y.index) == list(ctx.ids)
    assert y.loc[p, "reportperiod"] == pd.Timestamp("1999-03-31")
    assert y.loc[p, "reportperiod_lag"] == pd.Timestamp("1998-03-31")
    assert (y["datekey"].dropna() <= pd.Timestamp("1999-06-30")).all()
    assert (y["datekey_lag"].dropna() <= pd.Timestamp("1999-06-30")).all()
    both = y.dropna(subset=["reportperiod", "reportperiod_lag"])
    gap = (both["reportperiod"] - both["reportperiod_lag"]).dt.days
    assert gap.between(365 - 45, 366 + 45).all()
    ctx2, _ = _ctx(snap, pidx, cfg, "2000-03-31")
    y2 = ctx2.fundamentals_yoy(["assets"])
    assert y2.loc[p, "reportperiod_lag"] == pd.Timestamp("1998-12-31")
    assert y2.loc[p, "assets_lag"] == 5000.0
    assert y2.loc[p, "datekey_lag"] == pd.Timestamp("1999-08-01")
    # No period ten years back exists in the fixture (it starts 1994): every lag is NaN, the
    # current leg is still returned.
    y5 = ctx.fundamentals_yoy(["assets"], years=10)
    assert y5["reportperiod_lag"].isna().all() and y5["assets_lag"].isna().all()
    assert y5.loc[p, "reportperiod"] == pd.Timestamp("1999-03-31")


def test_fundamentals_history_drops_names_with_a_stale_latest_filing(snap, pidx, cfg, synthetic):
    p = str(synthetic["perma"][S.DELIST_PERF])
    u = build_universe(pidx, pd.Timestamp("1999-06-30"), cfg)
    ctx = MonthContext(snap, pidx, u, pd.Timestamp("2001-06-29"), cfg, {})
    h = ctx.fundamentals_history(["assets"], 4)
    assert p not in set(h["ID"])



def test_fundamentals_at_month_ends_lag_zero_equals_fundamentals(snap, pidx, cfg):
    ctx, _ = _ctx(snap, pidx, cfg, "2000-06-30")
    many = ctx.fundamentals_at_month_ends(["assets", "revenue"], [0, 3, 12])
    one = ctx.fundamentals(["assets", "revenue"]).dropna(subset=["datekey"])
    got = many[many["months_back"] == 0].set_index("ID")
    assert set(got.index) == set(one.index)
    for c in ("datekey", "reportperiod", "assets", "revenue"):
        a, b = got.loc[one.index, c], one[c]
        assert ((a == b) | (a.isna() & b.isna())).all(), c


def test_fundamentals_at_month_ends_never_sees_a_filing_after_its_month_end(snap, pidx, cfg, synthetic):
    """Each lag's filing is bounded by that lag's business month-end, not the
    signal. RESTATED's restatement (filed 1999-08-01) must not reach the
    1999-04-30 lag of a 2000-04-28 signal, which sees the original 1000."""
    ctx, _ = _ctx(snap, pidx, cfg, "2000-04-28")
    lags = list(range(0, 16))
    many = ctx.fundamentals_at_month_ends(["assets"], lags)
    assert not many.empty
    targets = {m: to_bme([(pd.Timestamp("2000-04-28") - pd.DateOffset(months=m)).normalize()]).iloc[0]
               for m in lags}
    assert (many["datekey"] <= many["months_back"].map(targets)).all()
    tol = pd.Timedelta(days=int(round(30.4375 * float(cfg["point_in_time"]["max_fundamental_age_months"]))))
    assert (many["datekey"] >= many["months_back"].map(targets) - tol).all()
    p = str(synthetic["perma"][S.RESTATED])
    mine = many[many["ID"] == p].set_index("months_back")
    assert mine.loc[12, "datekey"] == pd.Timestamp("1999-02-14")
    assert mine.loc[12, "assets"] == 1000.0
    assert mine.loc[8, "datekey"] >= pd.Timestamp("1999-08-01")
    # lag 12 agrees with the calendar lag of fundamentals() on this name
    lag = ctx.fundamentals(["assets"], lag_months=12)
    assert lag.loc[p, "datekey"] == mine.loc[12, "datekey"]


# ---------------------------------------------------------------------------
# Corporate actions and material events (HX-3)
# ---------------------------------------------------------------------------
# ACTIONS and EVENTS sat in the snapshot from the start — ACTIONS from 1997-12,
# EVENTS from 1993-11, both spanning the decision window — but MonthContext
# reached only four of the snapshot's ten tables, so the whole dividend/event
# predictor family had no source it could read. These pin the accessors' two
# load-bearing properties: they never look past the signal, and an absent row
# stays absent rather than becoming a zero.

def test_actions_never_returns_a_row_dated_after_the_signal(snap, pidx, cfg):
    ctx, _ = _ctx(snap, pidx, cfg, "1999-06-30")
    got = ctx.actions("dividend", 120)
    assert not got.empty, "fixture should have dividends before 1999-06-30"
    assert (got["date"] <= pd.Timestamp("1999-06-30")).all()


def test_actions_window_lower_bound_is_exclusive_and_in_months(snap, pidx, cfg):
    ctx, _ = _ctx(snap, pidx, cfg, "1999-06-30")
    wide = ctx.actions("dividend", 24)
    narrow = ctx.actions("dividend", 3)
    assert len(narrow) <= len(wide)
    if not narrow.empty:
        assert (narrow["date"] > pd.Timestamp("1999-06-30") - pd.DateOffset(months=3)).all()


def test_actions_filters_on_the_action_kinds_asked_for(snap, pidx, cfg):
    ctx, _ = _ctx(snap, pidx, cfg, "1999-12-31")
    assert set(ctx.actions("dividend", 120)["action"].unique()) <= {"dividend"}
    both = ctx.actions(("dividend", "initiated"), 120)
    assert set(both["action"].unique()) <= {"dividend", "initiated"}
    assert len(both) >= len(ctx.actions("dividend", 120))


def test_actions_accepts_a_single_kind_as_a_bare_string(snap, pidx, cfg):
    ctx, _ = _ctx(snap, pidx, cfg, "1999-12-31")
    assert ctx.actions("dividend", 120).equals(ctx.actions(("dividend",), 120))


def test_actions_is_restricted_to_universe_ids(snap, pidx, cfg):
    ctx, u = _ctx(snap, pidx, cfg, "1999-12-31")
    got = ctx.actions("dividend", 120)
    assert set(got["ID"]).issubset(set(u.index))


def test_actions_leaves_a_non_payer_absent_rather_than_zero(snap, pidx, cfg):
    """An absent dividend record is not a zero dividend. A factor that fills it
    with 0.0 manufactures a mass point; the accessor must not do it for them."""
    ctx, u = _ctx(snap, pidx, cfg, "1999-12-31")
    got = ctx.actions("dividend", 120)
    assert len(set(u.index) - set(got["ID"])) > 0, "fixture needs a non-payer"
    assert got["value"].notna().all()


def test_actions_returns_the_value_column_for_dividend_size(snap, pidx, cfg):
    ctx, _ = _ctx(snap, pidx, cfg, "1999-12-31")
    got = ctx.actions("dividend", 120)
    assert "value" in got.columns and (got["value"] > 0).any()


def test_actions_unknown_kind_is_empty_not_an_error(snap, pidx, cfg):
    ctx, _ = _ctx(snap, pidx, cfg, "1999-12-31")
    assert ctx.actions("no-such-action", 120).empty


def test_events_never_returns_a_row_dated_after_the_signal(snap, pidx, cfg):
    ctx, _ = _ctx(snap, pidx, cfg, "1999-06-30")
    got = ctx.events(120)
    assert (got["date"] <= pd.Timestamp("1999-06-30")).all()


def test_events_keeps_eventcodes_raw_for_the_factor_to_parse(snap, pidx, cfg):
    """eventcodes is a pipe-separated list of 8-K item numbers. The harness does
    not guess which codes matter — that is the predictor's business."""
    ctx, _ = _ctx(snap, pidx, cfg, "1999-12-31")
    got = ctx.events(120)
    assert not got.empty and got["eventcodes"].map(lambda s: isinstance(s, str)).all()
    assert set(got.columns) == {"ID", "date", "eventcodes"}


def test_events_is_restricted_to_universe_ids(snap, pidx, cfg):
    ctx, u = _ctx(snap, pidx, cfg, "1999-12-31")
    assert set(ctx.events(120)["ID"]).issubset(set(u.index))


# ---- daily value-weighted market return ------------------------------------------

def _hand_vw(sep, daily, day, prev, tickers):
    """sum(w_{d-1} r_d) / sum(w_{d-1}) over `tickers` printing on both days."""
    a = sep[sep["date"] == prev].set_index("ticker")["closeadj"]
    b = sep[sep["date"] == day].set_index("ticker")["closeadj"]
    w = daily[daily["date"] == prev].set_index("ticker")["marketcap"]
    both = sorted(set(a.index) & set(b.index) & set(w.index) & set(tickers))
    r = b[both] / a[both] - 1.0
    return float((w[both] * r).sum() / w[both].sum()), len(both)


def _copy_snapshot(synthetic, tmp_path, edit):
    """Copy the fixture, apply `edit(tables_dir)` and re-hash the manifest."""
    import shutil
    from harness.data_layer import sha256_file
    root = tmp_path / "copy"
    shutil.copytree(synthetic["root"], root)
    edit(root / "sharadar")
    m = dict(synthetic["manifest"]); m["tables"] = {k: dict(v) for k, v in m["tables"].items()}
    for t in m["tables"]:
        m["tables"][t]["sha256"] = sha256_file(root / "sharadar" / m["tables"][t]["file"])
    return Snapshot(root / "sharadar", m, verify_hashes=True)


def test_market_daily_is_bounded_by_the_signal_date(snap, pidx, cfg):
    ctx, _ = _ctx(snap, pidx, cfg, "2000-06-30")
    full = pidx.market()
    assert full.index.max() > pd.Timestamp("2000-06-30")      # later days exist to leak
    got = ctx.market_daily(60)
    assert got.index.max() == pd.Timestamp("2000-06-30")
    assert got.index.min() > pd.Timestamp("2000-06-30") - pd.Timedelta(days=60)
    assert got.name == "mkt_ret" and got.notna().all() and len(got) >= 40
    wn = ctx.market_daily(60, with_names=True)
    assert list(wn.columns) == ["mkt_ret", "n_names"] and (wn["n_names"] > 50).all()
    # Same bounds as ctx.daily: signal - days_back < date <= signal.
    dd = ctx.daily("SEP", ["closeadj"], 60)
    assert set(got.index) == set(dd["date"].unique())


def test_market_daily_equals_prior_day_cap_weighted_mean(snap, pidx, synthetic):
    sep = pd.read_parquet(synthetic["root"] / "sharadar" / "SEP.parquet")
    daily = pd.read_parquet(synthetic["root"] / "sharadar" / "DAILY.parquet")
    day, prev = pd.Timestamp("1999-09-15"), pd.Timestamp("1999-09-14")
    want, n = _hand_vw(sep, daily, day, prev, sep["ticker"].unique())
    got = pidx.market().loc[day]
    assert got["mkt_ret"] == pytest.approx(want, rel=1e-12)
    assert int(got["n_names"]) == n
    # Weights are the PRIOR day's caps: same-day caps give a different number.
    a = sep[sep["date"] == prev].set_index("ticker")["closeadj"]
    b = sep[sep["date"] == day].set_index("ticker")["closeadj"]
    w0 = daily[daily["date"] == day].set_index("ticker")["marketcap"]
    both = sorted(set(a.index) & set(b.index) & set(w0.index))
    same_day = float((w0[both] * (b[both] / a[both] - 1)).sum() / w0[both].sum())
    assert got["mkt_ret"] != pytest.approx(same_day, rel=1e-9)
    # A name that printed its last trade on the prior day has no return on d
    # (PERF last trades 1999-09-15, so it IS in; the day after it is not).
    nxt = pidx.market().loc[pd.Timestamp("1999-09-16")]
    assert int(nxt["n_names"]) == n - 1


def test_market_daily_admits_no_name_outside_category_and_exchange(synthetic, cfg, tmp_path):
    from harness.data_layer import build_market_daily, market_constituent_ids
    etf, otc = "T000", "T001"

    def edit(d):
        tk = pd.read_parquet(d / "TICKERS.parquet")
        tk.loc[tk["ticker"] == etf, "category"] = "ETF"
        tk.loc[tk["ticker"] == otc, "exchange"] = "OTC"
        tk.to_parquet(d / "TICKERS.parquet", index=False)
        # Make the excluded names huge, so entering would move the market.
        dl = pd.read_parquet(d / "DAILY.parquet")
        dl.loc[dl["ticker"].isin([etf, otc]), "marketcap"] *= 1e6
        dl.to_parquet(d / "DAILY.parquet", index=False)

    snap2 = _copy_snapshot(synthetic, tmp_path, edit)
    ids = market_constituent_ids(snap2, cfg)
    assert str(synthetic["perma"][etf]) not in ids and str(synthetic["perma"][otc]) not in ids
    mkt = build_market_daily(snap2, cfg, log=lambda *a, **k: None)
    sep = pd.read_parquet(snap2.path("SEP"))
    daily = pd.read_parquet(snap2.path("DAILY"))
    keep = [t for t in sep["ticker"].unique() if t not in (etf, otc)]
    for day, prev in [("1999-09-15", "1999-09-14"), ("2001-03-07", "2001-03-06")]:
        want, n = _hand_vw(sep, daily, pd.Timestamp(day), pd.Timestamp(prev), keep)
        assert mkt.loc[pd.Timestamp(day), "mkt_ret"] == pytest.approx(want, rel=1e-12)
        assert int(mkt.loc[pd.Timestamp(day), "n_names"]) == n


def _market_edit(synthetic, cfg, tmp_path, edit):
    from harness.data_layer import build_market_daily
    snap2 = _copy_snapshot(synthetic, tmp_path, edit)
    mkt = build_market_daily(snap2, cfg, log=lambda *a, **k: None)
    return mkt, pd.read_parquet(snap2.path("SEP")), pd.read_parquet(snap2.path("DAILY"))


def _scale_close(ticker, mask_fn, k):
    def edit(d):
        sp = pd.read_parquet(d / "SEP.parquet")
        m = (sp["ticker"] == ticker) & mask_fn(sp["date"])
        sp.loc[m, "closeadj"] *= k
        sp.to_parquet(d / "SEP.parquet", index=False)
    return edit


def test_market_daily_drops_a_plain_bad_print(synthetic, cfg, tmp_path):
    """A permanent +900% level jump (no reversal) is dropped on its day by the
    |r| > 5 rule; the next day is an ordinary return and stays."""
    from harness.data_layer import MARKET_MAX_ABS_RET
    day, nxt = pd.Timestamp("2000-02-15"), pd.Timestamp("2000-02-16")
    mkt, sep, daily = _market_edit(synthetic, cfg, tmp_path,
                                   _scale_close("T002", lambda d: d >= day, 10.0))
    allt = sep["ticker"].unique()
    keep = [t for t in allt if t != "T002"]
    assert MARKET_MAX_ABS_RET == 5.0
    want, n = _hand_vw(sep, daily, day, pd.Timestamp("2000-02-14"), keep)
    assert mkt.loc[day, "mkt_ret"] == pytest.approx(want, rel=1e-12)
    assert int(mkt.loc[day, "n_names"]) == n
    want2, n2 = _hand_vw(sep, daily, nxt, day, allt)
    assert mkt.loc[nxt, "mkt_ret"] == pytest.approx(want2, rel=1e-12)
    assert int(mkt.loc[nxt, "n_names"]) == n2


@pytest.mark.parametrize("k", [3.0, 0.1], ids=["spike-up", "spike-down"])
def test_market_daily_drops_both_legs_of_a_spike_and_reversal(synthetic, cfg, tmp_path, k):
    """One bad close on day d: +200% then -67% (k=3), or -90% then +900%
    (k=0.1). Both day d AND day d+1 must drop the name — dropping only the
    |r| > 5 leg would keep the matching reversal in the market."""
    prev, day, nxt = (pd.Timestamp("2000-02-14"), pd.Timestamp("2000-02-15"),
                      pd.Timestamp("2000-02-16"))
    mkt, sep, daily = _market_edit(synthetic, cfg, tmp_path,
                                   _scale_close("T004", lambda d: d == day, k))
    # k=3: +200% is the spike, -67% the reversal. k=0.1: -90% is the spike and
    # +900% is itself an extreme print (a spike), so no separate reversal.
    assert (mkt.attrs["n_spike"], mkt.attrs["n_reversal"]) == ((1, 1) if k == 3.0 else (2, 0))
    keep = [t for t in sep["ticker"].unique() if t != "T004"]
    for d, p_ in [(day, prev), (nxt, day)]:
        want, n = _hand_vw(sep, daily, d, p_, keep)
        assert mkt.loc[d, "mkt_ret"] == pytest.approx(want, rel=1e-12), d
        assert int(mkt.loc[d, "n_names"]) == n, d
    # The day after the pair is back to every name.
    d3 = pd.Timestamp("2000-02-17")
    want3, n3 = _hand_vw(sep, daily, d3, nxt, sep["ticker"].unique())
    assert mkt.loc[d3, "mkt_ret"] == pytest.approx(want3, rel=1e-12)


def test_market_daily_ignores_a_stray_date_row(synthetic, cfg, tmp_path):
    """One name printing on a Saturday must not become every other name's
    'prior day' and empty the Monday."""
    from harness.data_layer import MARKET_MIN_NAMES
    sat, fri, mon = pd.Timestamp("2000-02-12"), pd.Timestamp("2000-02-11"), pd.Timestamp("2000-02-14")

    def edit(d):
        for t in ("SEP", "DAILY"):
            x = pd.read_parquet(d / f"{t}.parquet")
            row = x[(x["ticker"] == "T005") & (x["date"] == fri)].assign(date=sat)
            pd.concat([x, row], ignore_index=True).to_parquet(d / f"{t}.parquet", index=False)

    mkt, sep, daily = _market_edit(synthetic, cfg, tmp_path, edit)
    assert sat not in mkt.index
    assert mkt.attrs["n_stray_rows"] == 1
    want, n = _hand_vw(sep, daily, mon, fri, sep["ticker"].unique())
    assert mkt.loc[mon, "mkt_ret"] == pytest.approx(want, rel=1e-12)
    assert int(mkt.loc[mon, "n_names"]) == n
    assert (mkt["n_names"] >= MARKET_MIN_NAMES).all()


def test_market_daily_min_days_returns_empty_on_a_thin_window(snap, pidx, cfg):
    first = pidx.market().index.min()
    ctx, _ = _ctx(snap, pidx, cfg, "2000-06-30")
    n = len(ctx.market_daily(365))
    assert n > 200
    assert len(ctx.market_daily(365, min_days=n)) == n
    assert ctx.market_daily(365, min_days=n + 1).empty
    assert ctx.market_daily(365, with_names=True, min_days=n + 1).empty
    # A window that reaches before the series start is thin, not padded.
    sig = first + pd.offsets.BMonthEnd(1)
    ctx2, _ = _ctx(snap, pidx, cfg, sig)
    w = ctx2.market_daily(365)
    assert 0 < len(w) < 40 and w.index.min() >= first
    assert ctx2.market_daily(365, min_days=200).empty


def test_monthly_market_compounds_the_daily_series_within_business_months(snap, pidx, cfg):
    ctx, _ = _ctx(snap, pidx, cfg, "2000-06-30")
    full = pidx.market()
    got = ctx.monthly_market(6)
    assert len(got) == 6 and got.index.max() == pd.Timestamp("2000-06-30")
    assert list(got.index) == sorted(got.index) and got.name == "mkt_ret"
    d = full.loc[(full.index > pd.Timestamp("2000-05-31")) & (full.index <= pd.Timestamp("2000-06-30")),
                 "mkt_ret"]
    assert got.loc[pd.Timestamp("2000-06-30")] == pytest.approx(float((1 + d).prod() - 1), rel=1e-12)
    ew = ctx.monthly_market(6, col="ew")
    d_ew = full.loc[d.index, "ew_ret"]
    assert ew.loc[pd.Timestamp("2000-06-30")] == pytest.approx(float((1 + d_ew).prod() - 1), rel=1e-12)
    # Nothing after the signal: the value for the signal month is unchanged by later days.
    ctx_late, _ = _ctx(snap, pidx, cfg, "2000-09-29")
    assert ctx_late.monthly_market(6).loc[pd.Timestamp("2000-06-30")] == got.loc[pd.Timestamp("2000-06-30")]
    # Months before the series start are NaN, not partial compounding.
    first = full.index.min()
    early = ctx.monthly_market(24)
    assert early[early.index < first].isna().all()
    # The month holding the first day is partial and blanked.
    first_bme = pd.Timestamp(first) + pd.offsets.BMonthEnd(0)
    if first_bme in early.index:
        assert pd.isna(early.loc[first_bme])
    # The index is exactly the return months of monthly_closeadj over the same horizon.
    px = ctx.monthly_closeadj(6)
    assert list(got.index) == list(px.columns[1:])
    # min_days bites on a month that HAS days: demand more days than June 2000 has.
    n_june = int(((full.index > pd.Timestamp("2000-05-31")) & (full.index <= pd.Timestamp("2000-06-30"))).sum())
    thin = ctx.monthly_market(6, min_days=n_june + 1)
    assert pd.isna(thin.loc[pd.Timestamp("2000-06-30")])
    assert ctx.monthly_market(6, min_days=n_june).loc[pd.Timestamp("2000-06-30")] == got.loc[pd.Timestamp("2000-06-30")]
    with pytest.raises(ValueError):
        ctx.monthly_market(6, col="xx")


def test_market_cache_key_moves_with_the_builder_source(cfg, monkeypatch):
    import harness.data_layer as DL
    k0 = DL.market_cache_key("abc", cfg)
    assert k0 == DL.market_cache_key("abc", cfg)
    monkeypatch.setattr(DL.inspect, "getsource", lambda f: "changed " + f.__name__)
    assert DL.market_cache_key("abc", cfg) != k0


def test_market_daily_drops_an_implausible_cap_weight(synthetic, cfg, tmp_path):
    """A DAILY.marketcap vendor error with no price symptom (the real snapshot's
    ISWI at $2.4T in Feb 2000) must not carry the next day's market."""
    from harness.data_layer import MARKET_MAX_CAP_TO_ADV, build_market_daily
    prev, day = pd.Timestamp("2000-02-14"), pd.Timestamp("2000-02-15")

    def edit(d):
        dl = pd.read_parquet(d / "DAILY.parquet")
        dl.loc[(dl["ticker"] == "T003") & (dl["date"] == prev), "marketcap"] *= 1e7
        dl.to_parquet(d / "DAILY.parquet", index=False)

    snap2 = _copy_snapshot(synthetic, tmp_path, edit)
    mkt = build_market_daily(snap2, cfg, log=lambda *a, **k: None)
    sep = pd.read_parquet(snap2.path("SEP"))
    daily = pd.read_parquet(snap2.path("DAILY"))
    keep = [t for t in sep["ticker"].unique() if t != "T003"]
    want, n = _hand_vw(sep, daily, day, prev, keep)
    assert MARKET_MAX_CAP_TO_ADV == 1e5
    assert mkt.loc[day, "mkt_ret"] == pytest.approx(want, rel=1e-12)
    assert int(mkt.loc[day, "n_names"]) == n
    # The guard is point-in-time: T003's weight on the next day is untouched.
    nxt = pd.Timestamp("2000-02-16")
    want2, n2 = _hand_vw(sep, daily, nxt, day, sep["ticker"].unique())
    assert mkt.loc[nxt, "mkt_ret"] == pytest.approx(want2, rel=1e-12)


def _cut_after(day):
    """Edit: delete every SEP and DAILY row dated after `day`."""
    def edit(d):
        for t in ("SEP", "DAILY"):
            x = pd.read_parquet(d / f"{t}.parquet")
            x[x["date"] <= day].to_parquet(d / f"{t}.parquet", index=False)
    return edit


def _chain(*edits):
    def edit(d):
        for e in edits:
            e(d)
    return edit


@pytest.mark.parametrize("k", [3.0, 0.1], ids=["spike-up", "spike-down"])
def test_market_daily_is_causal_no_value_moves_when_later_rows_are_deleted(synthetic, cfg, tmp_path, k):
    """The market on date d must read nothing after d. A spike on the cut day
    whose reversal is the day after is the case a d+1-reading pair rule got
    wrong: with the future deleted it kept the spike, with it present it
    dropped it. Every date <= the cut must be identical either way."""
    cut = pd.Timestamp("2000-02-15")
    spike = _scale_close("T004", lambda d: d == cut, k)
    full, sep, daily = _market_edit(synthetic, cfg, tmp_path / "full", spike)
    trunc, _, _ = _market_edit(synthetic, cfg, tmp_path / "trunc", _chain(spike, _cut_after(cut)))
    assert trunc.index.max() == cut and full.index.max() > cut
    a = full.loc[full.index <= cut]
    pd.testing.assert_frame_equal(a, trunc, check_exact=True)
    # And the spike day itself is dropped from both, judged on r_d alone.
    keep = [t for t in sep["ticker"].unique() if t != "T004"]
    want, n = _hand_vw(sep, daily, cut, pd.Timestamp("2000-02-14"), keep)
    assert trunc.loc[cut, "mkt_ret"] == pytest.approx(want, rel=1e-12)
    assert int(trunc.loc[cut, "n_names"]) == n


def test_market_daily_is_causal_on_the_unedited_fixture(synthetic, cfg, tmp_path):
    cut = pd.Timestamp("2001-06-29")
    full, _, _ = _market_edit(synthetic, cfg, tmp_path / "full", lambda d: None)
    trunc, _, _ = _market_edit(synthetic, cfg, tmp_path / "trunc", _cut_after(cut))
    pd.testing.assert_frame_equal(full.loc[full.index <= cut], trunc, check_exact=True)


def test_market_daily_serves_the_equal_weighted_series(snap, pidx, cfg, synthetic):
    ctx, _ = _ctx(snap, pidx, cfg, "2000-06-30")
    vw = ctx.market_daily(60)
    assert vw.equals(ctx.market_daily(60, col="vw"))
    ew = ctx.market_daily(60, col="ew")
    assert ew.name == "ew_ret" and ew.index.equals(vw.index) and not ew.equals(vw)
    # Hand check: the plain mean of the same name-days as the VW number.
    sep = pd.read_parquet(synthetic["root"] / "sharadar" / "SEP.parquet")
    day, prev = pd.Timestamp("2000-06-15"), pd.Timestamp("2000-06-14")
    a = sep[sep["date"] == prev].set_index("ticker")["closeadj"]
    b = sep[sep["date"] == day].set_index("ticker")["closeadj"]
    both = sorted(set(a.index) & set(b.index))
    assert ew.loc[day] == pytest.approx(float((b[both] / a[both] - 1).mean()), rel=1e-12)
    wn = ctx.market_daily(60, with_names=True, col="ew")
    assert list(wn.columns) == ["ew_ret", "n_names"]
    assert ctx.market_daily(60, col="ew", min_days=len(ew) + 1).empty
    with pytest.raises(ValueError):
        ctx.market_daily(60, col="rf")


# ---- annual anchor-month estimation window ------------------------------------

@pytest.mark.parametrize("signal,start,end", [
    # June window first used at the July signal; June itself still uses last year's.
    ("2000-06-30", "1998-07-01", "1999-06-30"),
    ("2000-07-31", "1999-07-01", "2000-06-30"),
    ("2001-01-31", "1999-07-01", "2000-06-30"),
    ("2004-06-30", "2002-07-01", "2003-06-30"),
    ("2004-07-30", "2003-07-01", "2004-06-30"),
    ("2020-07-31", "2019-07-01", "2020-06-30"),
    ("2020-12-31", "2019-07-01", "2020-06-30"),
    # June BME on a weekday before the 30th: 2002-06-28 (Sat 29, Sun 30).
    ("2002-07-31", "2001-07-01", "2002-06-28"),
])
def test_annual_window_june_anchor(signal, start, end):
    from harness.data_layer import annual_window
    s, e = annual_window(pd.Timestamp(signal), 6, 1)
    assert (s, e) == (pd.Timestamp(start), pd.Timestamp(end))
    assert e <= pd.Timestamp(signal)


@pytest.mark.parametrize("year,end", [(2000, "2000-02-29"), (2004, "2004-02-27"),
                                      (2020, "2020-02-28")])
def test_annual_window_leap_years_end_on_the_business_month_end(year, end):
    """Feb 29 2000 is a Tuesday (kept); 2004's is a Sunday and 2020's a
    Saturday (rolled back to Friday). The start is always March 1 of the
    prior year: twelve whole months, never a 365-day count."""
    from harness.data_layer import annual_window
    s, e = annual_window(pd.Timestamp(f"{year}-03-31"), anchor_month=2, publish_lag_months=1)
    assert e == pd.Timestamp(end) and s == pd.Timestamp(f"{year - 1}-03-01")
    # One month earlier (the anchor month itself) is too soon at lag 1.
    s0, e0 = annual_window(pd.Timestamp(f"{year}-02-{pd.Timestamp(end).day}"), 2, 1)
    assert e0.year == year - 1 and e0.month == 2
    # June windows spanning a leap Feb contain the 29th.
    s6, e6 = annual_window(pd.Timestamp(f"{year}-07-31"), 6, 1)
    assert s6 <= pd.Timestamp(f"{year}-02-29") <= e6


def test_annual_window_publish_lag_and_accessor(snap, pidx, cfg):
    from harness.data_layer import annual_window
    sig = pd.Timestamp("2000-06-30")
    assert annual_window(sig, 6, 0)[1] == pd.Timestamp("2000-06-30")   # lag 0: same month
    assert annual_window(pd.Timestamp("2000-07-31"), 6, 2)[1] == pd.Timestamp("1999-06-30")
    assert annual_window(pd.Timestamp("2000-08-31"), 6, 2)[1] == pd.Timestamp("2000-06-30")
    assert annual_window(pd.Timestamp("2000-01-31"), 12, 1)[0] == pd.Timestamp("1999-01-01")
    ctx, _ = _ctx(snap, pidx, cfg, "2000-07-31")
    assert ctx.annual_window() == (pd.Timestamp("1999-07-01"), pd.Timestamp("2000-06-30"))
    with pytest.raises(ValueError):
        annual_window(sig, 13, 1)


# ---- market scope (industry aggregates) ----------------------------------------

def test_market_scope_fundamentals_extend_the_universe_rows_unchanged(snap, pidx, cfg):
    """scope="market" reads every listed common stock: at lag 0 the universe's
    rows are identical to the default scope's, and names the size/liquidity
    screen dropped this month are present too. At a lag, only names that
    traded in that lag's month appear, and their rows match."""
    from harness.data_layer import market_constituent_ids
    ctx, u = _ctx(snap, pidx, cfg, "2000-06-30")
    uni = ctx.fundamentals_at_month_ends(["revenue"], [0, 12])
    mkt = ctx.fundamentals_at_month_ends(["revenue"], [0, 12], scope="market")
    assert set(uni.loc[uni["months_back"] == 0, "ID"]) <= set(mkt.loc[mkt["months_back"] == 0, "ID"])
    assert set(mkt["ID"]) <= set(market_constituent_ids(snap, cfg))
    assert len(set(mkt["ID"]) - set(u.index.astype(str))) > 0
    a = uni.set_index(["ID", "months_back"]).sort_index()
    both = a.index.intersection(mkt.set_index(["ID", "months_back"]).index)
    assert len(both) > 0
    a = a.loc[both]
    b = mkt.set_index(["ID", "months_back"]).loc[both]
    for c in ("datekey", "reportperiod", "revenue"):
        assert ((a[c] == b[c]) | (a[c].isna() & b[c].isna())).all(), c


def test_market_scope_excludes_non_common_and_unlisted(synthetic, cfg, tmp_path):
    from harness.data_layer import build_monthly_panel, PanelIndex
    etf, otc = "T000", "T001"

    def edit(d):
        tk = pd.read_parquet(d / "TICKERS.parquet")
        tk.loc[tk["ticker"] == etf, "category"] = "ETF"
        tk.loc[tk["ticker"] == otc, "exchange"] = "OTC"
        tk.to_parquet(d / "TICKERS.parquet", index=False)

    snap2 = _copy_snapshot(synthetic, tmp_path, edit)
    pidx2 = PanelIndex(build_monthly_panel(snap2, cfg, log=lambda *a, **k: None), snap2, cfg)
    ctx, _ = _ctx(snap2, pidx2, cfg, "2000-06-30")
    got = ctx.fundamentals_at_month_ends(["revenue"], [0], scope="market")
    meta = ctx.ticker_meta(["exchange", "category"], scope="market")
    for t in (etf, otc):
        pid = str(synthetic["perma"][t])
        assert pid not in set(got["ID"]) and pid not in meta.index


def test_scope_rejects_unknown_value(snap, pidx, cfg):
    ctx, _ = _ctx(snap, pidx, cfg, "2000-06-30")
    with pytest.raises(ValueError):
        ctx.fundamentals_at_month_ends(["revenue"], [0], scope="all")


def test_market_scope_drops_names_not_trading_in_the_lag_month(snap, pidx, cfg, synthetic):
    """DELIST_PERF last trades 1999-09-15. Its filings are still under
    max_fundamental_age_months old in mid-2000, but it is not trading, so the
    market scope drops it at lag 0 and keeps it at the 1999-08 lag."""
    p = str(synthetic["perma"][S.DELIST_PERF])
    ctx, _ = _ctx(snap, pidx, cfg, "2000-06-30")
    mkt = ctx.fundamentals_at_month_ends(["assets"], [0, 10], scope="market")
    mine = mkt[mkt["ID"] == p]
    assert 0 not in set(mine["months_back"])
    assert 10 in set(mine["months_back"])
    for m, t in [(0, pd.Timestamp("2000-06-30")), (10, pd.Timestamp("1999-08-31"))]:
        listed = set(pidx.date_wide[t].dropna().index.astype(str))
        assert set(mkt.loc[mkt["months_back"] == m, "ID"]) <= listed


def test_market_context_is_listed_market_names_superset_of_universe(snap, pidx, cfg):
    from harness.data_layer import market_constituent_ids
    ctx, u = _ctx(snap, pidx, cfg, "2000-06-30")
    m = ctx.market_context()
    ids = set(m.ids.astype(str))
    assert set(u.index.astype(str)) <= ids
    assert ids <= set(market_constituent_ids(snap, cfg))
    assert ids <= set(pidx.date_wide[pd.Timestamp("2000-06-30")].dropna().index.astype(str))
    assert len(ids - set(u.index.astype(str))) > 0
    f_u = ctx.fundamentals(["assets"])
    f_m = m.fundamentals(["assets"]).reindex(f_u.index)
    assert ((f_u["assets"] == f_m["assets"]) | (f_u["assets"].isna() & f_m["assets"].isna())).all()
    assert ctx.market_context() is m


# ---- scope="market" on at_month_end / at_month_ends / daily --------------------------
# PERF (DELIST_PERF) last trades 1999-09-15. At the 2000-06-30 signal it is
# out of the universe, but a market-wide pooled sample over trailing lags must
# still hold it at the lags when it was alive.

MKT_ASOF = "2000-06-30"


def test_market_scope_at_month_ends_keeps_a_dead_name_only_where_it_traded(snap, pidx, cfg, synthetic):
    ctx, u = _ctx(snap, pidx, cfg, MKT_ASOF)
    perf = str(synthetic["perma"][S.DELIST_PERF])
    assert perf not in set(u.index)
    lags = [0, 6, 8, 9, 10, 12]
    mk = ctx.at_month_ends("DAILY", ["marketcap"], lags, scope="market")
    un = ctx.at_month_ends("DAILY", ["marketcap"], lags)
    have = set(mk.loc[mk["ID"] == perf, "months_back"])
    # Aug 1999 (lag 10) and Jun 1999 (lag 12): traded, present. Sep 1999
    # (lag 9): listed but no row within 7 days of the 30th. Oct 1999 on: gone.
    assert have == {10, 12}
    assert perf not in set(un["ID"])
    row = mk[(mk["ID"] == perf) & (mk["months_back"] == 10)].iloc[0]
    assert row["date"] <= pd.Timestamp("1999-08-31")
    # Universe rows are the universe-scope output, unchanged.
    sub = mk[mk["ID"].isin(set(u.index))].reset_index(drop=True)
    pd.testing.assert_frame_equal(sub, un.reset_index(drop=True), check_dtype=False)


def test_market_scope_at_month_ends_masks_by_the_lag_month_not_just_the_tolerance(snap, pidx, cfg, synthetic):
    """With a 60-day tolerance PERF's 1999-09-15 print sits inside the Oct-1999
    window, but PERF did not trade in October: the market scope drops it
    there (it was not in the market that month)."""
    ctx, _ = _ctx(snap, pidx, cfg, MKT_ASOF)
    perf = str(synthetic["perma"][S.DELIST_PERF])
    mk = ctx.at_month_ends("DAILY", ["marketcap"], [8, 9], tolerance_days=60, scope="market")
    assert set(mk.loc[mk["ID"] == perf, "months_back"]) == {9}


def test_market_scope_at_month_end_matches_at_month_ends(snap, pidx, cfg, synthetic):
    ctx, u = _ctx(snap, pidx, cfg, MKT_ASOF)
    perf = str(synthetic["perma"][S.DELIST_PERF])
    a10 = ctx.at_month_end("DAILY", ["marketcap"], 10, scope="market")
    assert perf in a10.index and a10.loc[perf, "marketcap"] > 0
    a8 = ctx.at_month_end("DAILY", ["marketcap"], 8, scope="market")
    assert perf not in a8.index                     # not in the market in Oct 1999
    assert len(a8) > len(u)                         # non-universe names are in
    many = ctx.at_month_ends("DAILY", ["marketcap"], [10], scope="market").set_index("ID")
    got = a10.dropna(subset=["marketcap"])
    pd.testing.assert_series_equal(got["marketcap"].sort_index(), many["marketcap"].sort_index(),
                                   check_names=False)


def test_default_scope_is_the_universe_for_the_three_accessors(snap, pidx, cfg):
    ctx, _ = _ctx(snap, pidx, cfg, MKT_ASOF)
    pd.testing.assert_frame_equal(ctx.daily("SEP", ["closeadj"], 90),
                                  ctx.daily("SEP", ["closeadj"], 90, scope="universe"))
    pd.testing.assert_frame_equal(ctx.at_month_end("DAILY", ["marketcap"], 3),
                                  ctx.at_month_end("DAILY", ["marketcap"], 3, scope="universe"))
    pd.testing.assert_frame_equal(ctx.at_month_ends("DAILY", ["marketcap"], [1, 3, 12]),
                                  ctx.at_month_ends("DAILY", ["marketcap"], [1, 3, 12], scope="universe"))
    assert list(ctx.at_month_end("DAILY", ["marketcap"], 3).index) == list(ctx.ids)
    with pytest.raises(ValueError):
        ctx.daily("SEP", ["closeadj"], 90, scope="everything")


def test_market_scope_daily_has_non_universe_names_and_nothing_after_the_signal(snap, pidx, cfg, synthetic):
    ctx, u = _ctx(snap, pidx, cfg, MKT_ASOF)
    sig = pd.Timestamp(MKT_ASOF)
    mk = ctx.daily("SEP", ["closeadj"], 400, scope="market")
    un = ctx.daily("SEP", ["closeadj"], 400)
    assert mk["date"].max() == sig and mk["date"].min() > sig - pd.Timedelta(days=400)
    ids = set(mk["ID"])
    for t in (S.DELIST_PERF, S.PENNY, S.TINY):
        assert str(synthetic["perma"][t]) in ids and str(synthetic["perma"][t]) not in set(u.index)
    perf = mk[mk["ID"] == str(synthetic["perma"][S.DELIST_PERF])]
    assert perf["date"].max() == S.PERF_LAST
    # Restricted to the universe, the market pull IS the universe pull.
    pd.testing.assert_frame_equal(mk[mk["ID"].isin(set(u.index))], un)


def test_market_scope_daily_admits_only_market_constituents(panel, snap, cfg, synthetic):
    from harness.data_layer import PanelIndex, market_constituent_ids
    p = PanelIndex(panel, snap, cfg)                 # fresh: the scope-ID cache is per index
    drop = str(synthetic["perma"][S.PENNY])
    p._market_scope_ids = pd.Index(sorted(i for i in market_constituent_ids(snap, cfg) if i != drop))
    ctx, _ = _ctx(snap, p, cfg, MKT_ASOF)
    mk = ctx.daily("SEP", ["closeadj"], 60, scope="market")
    assert drop not in set(mk["ID"]) and str(synthetic["perma"][S.TINY]) in set(mk["ID"])
