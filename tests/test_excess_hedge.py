"""
The excess-hedge DIAGNOSTIC and the external rf table it reads.

  * hedged_excess_t = hedged_t + beta_t * rf_t, beta_t exactly the declared
    ex-ante beta; ls_rf_credit_pp = 12 * mean(beta_t * rf_t) * 100.
  * With no rf table the fields are absent and every block is what it was.
  * The Stage 2 guard BAR reads the declared hedged series, never the excess.
  * The external table (FRED TB3MS) round-trips download -> verify ->
    manifest -> Snapshot -> rf, keyless, with a DTB3 fill path that is
    recorded and never silent. No test touches the network or data/.
"""
import argparse
import io
from contextlib import redirect_stdout

import numpy as np
import pandas as pd
import pytest

from harness import analytics as A
from harness import run_test as RT
from harness import snapshot as S
from harness.analytics import (EXCESS_KEYS, check_stage2, compute_ic, excess_hedge, excess_stats,
                               parse_result_blocks, print_summary, regime_diagnostics, stage2_checks)
from harness.data_layer import (EXTERNAL_TABLES, RF_TABLE, Snapshot, build_rebalance_schedule,
                                load_rf_monthly, sha256_file)
from harness.provenance import data_sha, load_config
from tests.test_run_end_to_end import C_V0, CANDS, _ns, _run
from tests.test_v4_construction import _audit, _tables

HEDGE = {"beta_window_months": 24, "beta_min_months": 12}


def _rf_monthly(start="1990-01", end="2030-12", seed=3):
    """A per-month rf with DISTINCT values, so a misalignment cannot hide."""
    per = pd.period_range(start, end, freq="M")
    rng = np.random.default_rng(seed)
    return pd.Series(rng.uniform(0.0005, 0.006, len(per)), index=per)


def _quiet(fn, *a, **k):
    with redirect_stdout(io.StringIO()):
        return fn(*a, **k)


# =============================================================================
# The maths
# =============================================================================

def test_excess_series_is_hedged_plus_beta_rf_and_the_credit_is_12_mean_beta_rf():
    audit = _audit(); ret, cnt = _tables(audit)
    rf = _rf_monthly()
    st = _quiet(print_summary, "t", ret, cnt, compute_ic(audit), audit, hedge=HEDGE, rf=rf)
    h, b, x = st["ls_series"], st["ls_beta_series"], st["ls_excess_series"]
    rf_al = pd.Series(rf.reindex(h.index.to_period("M")).values, index=h.index)
    pd.testing.assert_series_equal(x, h + b * rf_al, check_names=False)
    assert st["ls_rf_credit_pp"] == pytest.approx(12 * float((b * rf_al).mean()) * 100)
    # same months, so the annual excess return is the declared one plus the credit
    assert st["ls_excess_ann_return_pct"] == pytest.approx(st["ls_ann_return_pct"] + st["ls_rf_credit_pp"])
    # the unhedged first months (beta = 0) carry no credit
    first = b[b == 0.0].index
    assert len(first) == HEDGE["beta_min_months"]
    pd.testing.assert_series_equal(x.loc[first], h.loc[first], check_names=False)
    assert st["ls_excess_n_months"] == len(h)
    sh, dd = A.ls_stats_of(x)
    assert st["ls_excess_sharpe"] == pytest.approx(sh) and st["ls_excess_maxdd_pct"] == pytest.approx(dd)
    assert st["ls_excess_tstat_nw"] == pytest.approx(A.nw_tstat(x, 3))


def test_excess_ex_top_years_runs_the_d5_rule_on_the_excess_series_and_leaves_the_declared_one():
    audit = _audit(); ret, cnt = _tables(audit)
    rf = _rf_monthly()
    base = _quiet(print_summary, "t", ret, cnt, compute_ic(audit), audit, hedge=HEDGE)
    st = _quiet(print_summary, "t", ret, cnt, compute_ic(audit), audit, hedge=HEDGE, rf=rf)
    reg_x = regime_diagnostics(st["ls_excess_series"], None, 3)
    assert st["ls_excess_top_years"] == reg_x["ls_top_years"]
    assert st["ls_excess_sharpe_ex_top_years"] == pytest.approx(reg_x["ls_sharpe_ex_top_years"])
    assert st["ls_top_years"] == base["ls_top_years"]
    assert st["ls_sharpe_ex_top_years"] == base["ls_sharpe_ex_top_years"]


def test_rf_leaves_every_declared_field_unchanged_and_adds_only_the_excess_keys():
    audit = _audit(); ret, cnt = _tables(audit)
    kw = dict(hedge=HEDGE, regime={"ex_regime_top_years": 2, "market_state_lookback_months": 6},
              oos_start="2004-01-01")
    base = _quiet(print_summary, "t", ret, cnt, compute_ic(audit), audit, **kw)
    st = _quiet(print_summary, "t", ret, cnt, compute_ic(audit), audit, rf=_rf_monthly(), **kw)
    for k, v in base.items():
        if k in A.SERIES_KEYS:
            pd.testing.assert_series_equal(st[k], v)
        elif v == v:
            assert st[k] == v, k
    added = set(st) - set(base)
    want = (set(EXCESS_KEYS) | {"ls_excess_series"}
            | {pre + k for pre in ("cut_inwindow_", "cut_holdout_") for k in EXCESS_KEYS})
    assert added == want
    # the holdout cut's excess is the cut of the continuous excess series
    x = st["ls_excess_series"]
    ho = x[x.index >= pd.Timestamp("2004-01-01")]
    assert st["cut_holdout_ls_excess_n_months"] == len(ho) == 12
    assert st["cut_holdout_ls_excess_ann_return_pct"] == pytest.approx(ho.mean() * 1200)


def test_without_rf_no_excess_field_exists_and_the_report_says_nothing_of_it():
    audit = _audit(); ret, cnt = _tables(audit)
    buf = io.StringIO()
    with redirect_stdout(buf):
        st = print_summary("t", ret, cnt, compute_ic(audit), audit, hedge=HEDGE, oos_start="2004-01-01")
    assert not [k for k in st if "excess" in k or "rf_credit" in k]
    assert "Excess hedge" not in buf.getvalue() and "excess:" not in buf.getvalue()


def test_rf_pairs_with_the_calendar_month_of_the_holding_month():
    """DATE on a long-short row is ret_end, inside the holding month; rf_t is
    TB3MS dated the first of that same month."""
    for reb, asof, start, end in build_rebalance_schedule("1999-01-01", "2021-12-31"):
        assert end.to_period("M") == reb.to_period("M") == start.to_period("M")
        assert asof.to_period("M") == reb.to_period("M") - 1
    idx = pd.DatetimeIndex(["1999-01-29", "1999-02-26", "1999-03-31"])
    rf = pd.Series([0.1, 0.2, 0.3, 0.4], index=pd.period_range("1998-12", "1999-03", freq="M"))
    x, c = excess_hedge(pd.Series(0.0, index=idx), pd.Series(1.0, index=idx), rf)
    assert list(x.values) == [0.2, 0.3, 0.4]
    # a datetime-indexed rf (month starts, as FRED dates it) reads the same
    rf2 = pd.Series(rf.values, index=rf.index.to_timestamp())
    x2, _ = excess_hedge(pd.Series(0.0, index=idx), pd.Series(1.0, index=idx), rf2)
    assert list(x2.values) == [0.2, 0.3, 0.4]


def test_a_month_without_rf_is_dropped_and_counted_never_filled():
    idx = pd.date_range("2000-01-31", periods=36, freq="ME")
    h = pd.Series(np.random.default_rng(0).normal(0.01, 0.03, 36), index=idx)
    b = pd.Series(0.5, index=idx)
    rf = pd.Series(0.004, index=pd.period_range("2000-01", "2002-12", freq="M")).drop(pd.Period("2001-06", "M"))
    x, c = excess_hedge(h, b, rf)
    assert len(x) == 35 and pd.Timestamp("2001-06-30") not in x.index
    st = excess_stats(x, c)
    assert st["ls_excess_n_months"] == 35
    assert st["ls_rf_credit_pp"] == pytest.approx(0.5 * 0.004 * 1200)


# =============================================================================
# The runner: absent without rf, present with it, the guard bar untouched
# =============================================================================

@pytest.fixture(autouse=True)
def _patch_candidates(monkeypatch):
    monkeypatch.setattr(RT, "load_candidate", lambda name, candidates_dir=None: CANDS[name])


def _with_rf(monkeypatch):
    monkeypatch.setattr(RT, "load_rf_monthly", lambda snap: _rf_monthly())


def _keys_excess(block):
    return {k for k in block if "excess" in k or "rf_credit" in k}


def test_the_synthetic_snapshot_holds_no_rf_and_its_blocks_carry_no_excess_field(synthetic, cfg, runtime, snap):
    assert load_rf_monthly(snap) is None
    blocks, text = _run(_ns(baseline=True, stage=2, include_holdout=True), synthetic, cfg, runtime, snap)
    assert _keys_excess(parse_result_blocks("\n".join(blocks))[0]) == set()
    assert "Excess hedge" not in text and "rf (TB3MS)" not in text


def test_baseline_with_rf_adds_the_excess_fields_and_changes_no_declared_field(
        synthetic, cfg, runtime, snap, monkeypatch):
    ns = _ns(baseline=True, stage=2, include_holdout=True)
    without = parse_result_blocks("\n".join(_run(ns, synthetic, cfg, runtime, snap)[0]))[0]
    _with_rf(monkeypatch)
    blocks, text = _run(ns, synthetic, cfg, runtime, snap)
    with_ = parse_result_blocks("\n".join(blocks))[0]
    for k, v in without.items():
        assert with_[k] == v, k
    assert set(with_) - set(without) == _keys_excess(with_)
    for k in ("ls_excess_sharpe", "ls_excess_ann_return_pct", "ls_excess_maxdd_pct", "ls_excess_tstat_nw",
              "ls_excess_sharpe_ex_top_years", "ls_rf_credit_pp", "cut_holdout_ls_excess_sharpe",
              "cut_holdout_ls_rf_credit_pp", "cut_inwindow_ls_excess_ann_return_pct"):
        assert k in with_, k
    assert "Excess hedge" in text and "rf (TB3MS)" in text


def test_the_stage2_guard_bar_reads_the_declared_hedged_series_not_the_excess(
        synthetic, cfg, runtime, snap, monkeypatch):
    thr = cfg["acceptance_thresholds"]["stage2_marginal"]
    without = parse_result_blocks("\n".join(_run(_ns(factor="Noise", stage=2), synthetic, cfg, runtime, snap)[0]))[0]
    _with_rf(monkeypatch)
    with_ = parse_result_blocks("\n".join(_run(_ns(factor="Noise", stage=2), synthetic, cfg, runtime, snap)[0]))[0]
    for k in ("paired_delta_ls_tstat", "paired_delta_ls_mean", "ratchet_decision", "stage2_bars_failed",
              "resid_ic_tstat_nw"):
        assert with_[k] == without[k], k
    assert check_stage2(with_, thr) == check_stage2(without, thr)
    assert "guard_excess_tstat_nw" in with_ and "guard_excess_tstat_nw" not in without
    assert "base_ls_excess_sharpe" in with_ and "cand_ls_excess_sharpe" in with_
    # the bar list never names the excess series, whatever value it takes
    vals = {"resid_ic_tstat_nw": 3.0, "paired_delta_ls_tstat": 0.5}
    assert stage2_checks({**vals, "guard_excess_tstat_nw": -99.0}, thr) == stage2_checks(vals, thr)
    assert all("excess" not in r[0] for r in stage2_checks(vals, thr))


def test_stage3_with_rf_adds_the_excess_fields_per_variant(synthetic, cfg, runtime, snap, monkeypatch):
    without = parse_result_blocks("\n".join(_run(_ns(baseline=True, stage=3), synthetic, cfg, runtime, snap)[0]))
    _with_rf(monkeypatch)
    with_ = parse_result_blocks("\n".join(_run(_ns(baseline=True, stage=3), synthetic, cfg, runtime, snap)[0]))
    assert len(with_) == len(without)
    for a, b in zip(without, with_):
        for k, v in a.items():
            assert b[k] == v, (a["variant"], k)
        assert "ls_excess_sharpe" in b and "ls_rf_credit_pp" in b


# =============================================================================
# The external table: keyless fetch, fill, verify, manifest, Snapshot, live
# =============================================================================

TB3MS_CSV = "observation_date,TB3MS\n" + "".join(
    f"{p.to_timestamp().date()},{v:.2f}\n"
    for p, v in zip(pd.period_range("1998-01", "2026-08", freq="M"),
                    np.round(np.linspace(5.0, 3.7, len(pd.period_range("1998-01", "2026-08", freq="M"))), 2)))
# FRED DTB3, September 2026 as published (one holiday blank, 2026-09-07)
DTB3_SEP = [("2026-08-31", "3.78"), ("2026-09-01", "3.78"), ("2026-09-02", "3.78"), ("2026-09-03", "3.75"),
            ("2026-09-04", "3.77"), ("2026-09-07", ""), ("2026-09-08", "3.80"), ("2026-09-09", "3.81"),
            ("2026-09-10", "3.86"), ("2026-09-11", "3.92"), ("2026-09-14", "3.97"), ("2026-09-15", "3.97"),
            ("2026-09-16", "3.99"), ("2026-09-17", "3.97"), ("2026-09-18", "3.99"), ("2026-09-21", "4.02"),
            ("2026-09-22", "4.01"), ("2026-09-23", "4.04"), ("2026-09-24", "4.08"), ("2026-09-25", "4.08"),
            ("2026-09-28", "4.10"), ("2026-09-29", "4.07"), ("2026-09-30", "4.03")]
DTB3_CSV = "observation_date,DTB3\n" + "".join(f"{d},{v}\n" for d, v in DTB3_SEP)
SEP_MEAN = float(np.mean([float(v) for d, v in DTB3_SEP if v and d.startswith("2026-09")]))


@pytest.fixture
def fred_files(tmp_path, monkeypatch):
    """Point the spec at file:// fixtures, so the REAL keyless reader runs and
    no byte crosses the network."""
    src = tmp_path / "fred"; src.mkdir()
    (src / "TB3MS.csv").write_text(TB3MS_CSV)
    (src / "DTB3.csv").write_text(DTB3_CSV)
    spec = dict(EXTERNAL_TABLES[RF_TABLE])
    spec.update(source_url=(src / "TB3MS.csv").as_uri(), fill_url=(src / "DTB3.csv").as_uri())
    monkeypatch.setitem(EXTERNAL_TABLES, RF_TABLE, spec)
    return spec


NOW = pd.Timestamp("2026-10-01 12:00")


def test_external_table_round_trips_through_verify_manifest_and_the_snapshot(tmp_path, fred_files):
    root = tmp_path / "sharadar"
    meta = S.fetch_external(RF_TABLE, root / "TB3MS.parquet", echo=lambda *a, **k: None, now=NOW)
    assert meta["filled_months"] == {} and meta["source_url"] == fred_files["source_url"]
    pd.DataFrame({"ticker": ["A"], "date": [pd.Timestamp("2000-01-03")], "close": [1.0]}).to_parquet(
        root / "SEP.parquet", index=False)                       # a Sharadar-shaped neighbour
    probs, notes = S.verify_external(root, RF_TABLE, load_config())
    assert probs == [], probs
    m = S.build_manifest(root, echo=lambda *a, **k: None)
    e = m["tables"][RF_TABLE]
    assert e["kind"] == "external" and e["source_url"] == fred_files["source_url"]
    assert e["fetched_at"] == "2026-10-01T12:00:00Z" and e["filled_months"] == {}
    assert e["columns"] == ["date", "value"] and e["rows"] == TB3MS_CSV.count("\n") - 1
    assert e["sha256"] == sha256_file(root / "TB3MS.parquet")
    assert (e["min_date"], e["max_date"]) == ("1998-01-01", "2026-08-01")
    assert m["data_sha"] == data_sha(m) and "external" in m["source"]
    snap = Snapshot(root, m, verify_hashes=True)
    rf = load_rf_monthly(snap)
    assert rf[pd.Period("1998-01", "M")] == pytest.approx(5.0 / 1200)
    assert rf.index.max() == pd.Period("2026-08", "M")
    # DATA_SHA covers the table: a manifest without it hashes differently
    m2 = {**m, "tables": {k: v for k, v in m["tables"].items() if k != RF_TABLE}}
    assert data_sha(m2) not in ("nodata", m["data_sha"])
    assert "kind" not in m["tables"]["SEP"]                     # Sharadar rows are unchanged
    rep = S.external_report(root)
    assert rep[RF_TABLE]["vouched_by_api"] is False and rep[RF_TABLE]["kind"] == "external"


def test_the_dtb3_fill_is_explicit_recorded_and_the_mean_of_the_daily_values(tmp_path, fred_files):
    root = tmp_path / "sharadar"
    lines = []
    meta = S.fetch_external(RF_TABLE, root / "TB3MS.parquet", fill_through=pd.Period("2026-09", "M"),
                            echo=lines.append, now=NOW)
    assert meta["filled_months"] == {"2026-09": "dtb3_daily_mean"} and meta["fill_days"] == {"2026-09": 21}
    df = pd.read_parquet(root / "TB3MS.parquet")
    assert df["date"].iloc[-1] == pd.Timestamp("2026-09-01")
    assert df["value"].iloc[-1] == pytest.approx(SEP_MEAN) and round(SEP_MEAN, 2) == 3.94
    assert any("FILLED 2026-09" in ln for ln in lines)
    e = S.build_manifest(root, echo=lambda *a, **k: None)["tables"][RF_TABLE]
    assert e["filled_months"] == {"2026-09": "dtb3_daily_mean"} and e["fill_url"] == fred_files["fill_url"]
    assert S.verify_external(root, RF_TABLE, load_config())[0] == []


def test_without_the_fill_flag_an_unpublished_month_is_absent_and_said_so(tmp_path, fred_files):
    lines = []
    meta = S.fetch_external(RF_TABLE, tmp_path / "TB3MS.parquet", echo=lines.append, now=NOW)
    assert meta["filled_months"] == {}
    assert pd.read_parquet(tmp_path / "TB3MS.parquet")["date"].iloc[-1] == pd.Timestamp("2026-08-01")
    assert any("has not published 2026-09" in ln for ln in lines)


def test_a_month_that_has_not_ended_is_never_filled_and_a_thin_month_is_refused(tmp_path, fred_files):
    df, meta = S.build_external(RF_TABLE, fill_through="2026-09", now=pd.Timestamp("2026-09-20"))
    assert meta["filled_months"] == {} and df["date"].iloc[-1] == pd.Timestamp("2026-08-01")
    daily = S.parse_fred_csv(DTB3_CSV)
    with pytest.raises(RuntimeError, match="refusing to fill"):
        S.daily_month_mean(daily, "2026-08")          # one August day only


def test_verify_refuses_a_hole_and_a_window_it_does_not_cover(tmp_path, fred_files):
    df, meta = S.build_external(RF_TABLE, now=NOW)
    S.write_external(df.drop(index=100).reset_index(drop=True), meta, tmp_path / "TB3MS.parquet")
    probs, _ = S.verify_external(tmp_path, RF_TABLE, load_config())
    assert any("missing inside" in p for p in probs)
    S.write_external(df[df["date"] >= "2005-01-01"].reset_index(drop=True), meta, tmp_path / "TB3MS.parquet")
    probs, _ = S.verify_external(tmp_path, RF_TABLE, load_config())
    assert any("does not cover the decision window" in p for p in probs)
    assert S.verify_external(tmp_path / "nowhere", RF_TABLE)[0] == []      # absent: a note, not a problem


def test_fred_csv_is_read_positionally_with_blanks_as_missing():
    old = S.parse_fred_csv("DATE,TB3MS\n2020-01-01,1.52\n2020-02-01,.\n")
    new = S.parse_fred_csv("observation_date,TB3MS\n2020-01-01,1.52\n2020-02-01,\n")
    for d in (old, new):
        assert list(d.columns) == ["date", "value"] and d["value"].isna().tolist() == [False, True]


def test_download_of_the_external_table_alone_never_loads_the_sharadar_key(tmp_path, fred_files, monkeypatch):
    rt = {"data": {"root": str(tmp_path / "sharadar"), "manifest": str(tmp_path / "M.yaml"),
                   "required_tables": ["SEP"], "optional_tables": []}}
    monkeypatch.setattr(S, "load_runtime", lambda: rt)

    def _no_key(*a, **k):
        raise AssertionError("the Sharadar key was loaded for an external-only download")
    monkeypatch.setattr(S, "load_api_key", _no_key)
    monkeypatch.setattr(S, "_request", _no_key)
    with redirect_stdout(io.StringIO()):
        S.cmd_download(argparse.Namespace(tables=[RF_TABLE], force=False, fill_latest=False))
    assert (tmp_path / "sharadar" / "TB3MS.parquet").exists()
