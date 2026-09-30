"""
The runner end to end on the synthetic snapshot: Stage 1 batch, baseline,
solo Stage 2, batched ladder, Stage 3 construction. What is asserted is the
CONTRACT: blocks parse, stamps match, the in-run verdict agrees with
check_stage1()/check_stage2(), rung 1 of a ladder equals a solo Stage 2, the
holdout is refused for candidates, preflight blocks a mass point, and every
run writes its summary file.
"""
import argparse

import numpy as np
import pandas as pd
import pytest

from harness import run_test as RT
from harness.analytics import (check_stage1, check_stage2, parse_result_blocks,
                               validate_results)
from harness.factor_def import FactorDef
from factors import composite as C


def _value_like(ctx):
    f = ctx.fundamentals(["equity"])
    return f["equity"] / ctx.universe["mkt_cap_usd"]


def _noise(ctx):
    rng = np.random.default_rng(int(ctx.signal_asof.value % 100000))
    s = pd.Series(rng.normal(size=len(ctx.ids)), index=ctx.ids)
    s.iloc[:2] = np.nan
    return s


def _masspoint(ctx):
    s = pd.Series(0.0, index=ctx.ids)
    s.iloc[: len(s) // 2] = np.arange(len(s) // 2, dtype=float)
    return s


CAND_VALUE = FactorDef(name="ValueLike", col="f_vl", compute=_value_like, ascending=True,
                       weight=1.0, inputs=("SF1.equity", "DAILY.marketcap"), lookback_months=15,
                       family="value")
CAND_NOISE = FactorDef(name="Noise", col="f_noise", compute=_noise, ascending=True, weight=1.0,
                       inputs=("DAILY.marketcap",), family="noise")
CAND_MASS = FactorDef(name="Massy", col="f_mass", compute=_masspoint, ascending=True, weight=1.0,
                      inputs=("DAILY.marketcap",))
CANDS = {f.name: f for f in (CAND_VALUE, CAND_NOISE, CAND_MASS)}

def _pinned_v0(module):
    """A copy of the composite module frozen at v0 (the five seeds). The
    runner contract is tested on a composite whose legs the synthetic fixture
    can compute; accepted legs read SF1 columns the fixture does not carry,
    and which legs are live is the manifest's business, not this suite's.
    Every function is rebound to the copy's globals so active_factors(),
    families() and weights() see the pinned leg list."""
    import types
    v0 = types.ModuleType(module.__name__ + "_pinned_v0")
    v0.__dict__.update(module.__dict__)
    for k, obj in list(module.__dict__.items()):
        if isinstance(obj, types.FunctionType) and obj.__module__ == module.__name__:
            v0.__dict__[k] = types.FunctionType(obj.__code__, v0.__dict__, obj.__name__,
                                                obj.__defaults__, obj.__closure__)
    v0.COMPOSITE_FACTORS = [module.SIZE, module.VALUE, module.PROFITABILITY,
                            module.INVESTMENT, module.MOMENTUM]
    v0.COMPOSITE_VERSION = "v0"
    return v0


C_V0 = _pinned_v0(C)

STAMPS = {"harness_sha": "aaaaaaaaaaaa", "config_sha": "bbbbbbbbbbbb", "composite_sha": "cccccccccccc",
          "data_sha": "dddddddddddd", "universe_sha": "eeeeeeeeeeee"}


def _ns(**kw):
    # frozen=True: these tests measure harness LOGIC on a synthetic fixture, so
    # there is nothing for the live Sharadar API to authorise — and a test suite
    # that needs the network is not a test suite. The production default is the
    # opposite: a real run authorises against the API before it measures.
    d = dict(factor=None, factors=None, baseline=False, stage=1, include_holdout=False,
             dry_run=False, frozen=True, schema_only=False)
    d.update(kw)
    return argparse.Namespace(**d)


@pytest.fixture(autouse=True)
def _patch_candidates(monkeypatch):
    monkeypatch.setattr(RT, "load_candidate", lambda name, candidates_dir=None: CANDS[name])


def _run(ns, synthetic, cfg, runtime, snap, comp=C_V0):
    import io
    sink = io.StringIO()
    blocks = RT.run(ns, C=comp, cfg=cfg, runtime=runtime, stamps=STAMPS, snap=snap,
                    root=synthetic["root"], out_stream=sink)
    return blocks, sink.getvalue()


def _latest(synthetic, pattern):
    files = sorted((synthetic["root"] / "results").glob(pattern))
    assert files, pattern
    return files[-1]


# ---- Stage 1 ----------------------------------------------------------------

def test_stage1_batch_emits_one_block_per_member_with_stamps_and_verdict(synthetic, cfg, runtime, snap):
    blocks, text = _run(_ns(factors="ValueLike,Noise", stage=1), synthetic, cfg, runtime, snap)
    parsed = parse_result_blocks("\n".join(blocks))
    assert [b["factor"] for b in parsed] == ["ValueLike", "Noise"]
    for b in parsed:
        assert b["stage"] == "1" and b["batch_size"] == 2
        assert b["harness_sha"] == STAMPS["harness_sha"] and b["data_sha"] == STAMPS["data_sha"]
        assert validate_results(b, STAMPS["harness_sha"], STAMPS["config_sha"], cfg, STAMPS["data_sha"]) == []
        ok, details = check_stage1(b, cfg["acceptance_thresholds"]["stage1_standalone"],
                                   cfg["rebalance"]["min_months"])
        assert (b["stage1_decision"] == "PASS") == ok, "the runner's verdict must equal check_stage1()"
    v, n = parsed
    assert v["ic_mean"] > 0.01, "the planted value signal must be recovered"
    assert v["declaration_order"] == 1 and n["declaration_order"] == 2
    # (tier_* scalars need >= 30 names per tier; the 90-name fixture has none)
    for k in ("ic_tstat_nw", "ic_half_min", "ls_ann_return_pct", "ic_decay_h1",
              "preflight_masspoint_max_pct", "decile_avg_ret_pct",
              "ls_beta_mean", "ls_beta_fullwindow", "ls_raw_sharpe", "hedge_on", "ls_sharpe_ex_top_years"):
        assert k in v, k
    assert v["hedge_on"] == "True", "the search construction hedges the standalone screen too"
    assert not any(k.startswith("ls_net") for k in v), "no cost figure may reach a block"


def test_stage1_writes_report_summary_and_meta(synthetic, cfg, runtime, snap):
    _run(_ns(factors="ValueLike,Noise", stage=1), synthetic, cfg, runtime, snap)
    f = _latest(synthetic, "*_BATCH_stage1_*.txt")
    txt = f.read_text()
    assert "--- BEGIN RESULT BLOCK ---" in txt and "Survivorship-bias check" in txt
    assert f.with_suffix(".meta.json").exists()
    summ = f.with_name(f.stem + "_summary.md").read_text()
    assert "## ValueLike" in summ and "## Noise" in summ and "| ic_tstat_nw |" in summ
    assert len(summ) < 6000, "the summary must stay small — it is what the evaluator reads first"


def test_preflight_blocks_a_mass_point_before_any_backtest(synthetic, cfg, runtime, snap):
    with pytest.raises(SystemExit, match="PREFLIGHT FAILED"):
        _run(_ns(factors="ValueLike,Massy", stage=1), synthetic, cfg, runtime, snap)


def test_dry_run_executes_no_backtest(synthetic, cfg, runtime, snap):
    blocks, text = _run(_ns(factors="ValueLike,Noise", stage=1, dry_run=True), synthetic, cfg, runtime, snap)
    assert blocks == [] and "dry run complete" in text


# ---- baseline and construction ------------------------------------------------

def test_baseline_measures_the_composite(synthetic, cfg, runtime, snap):
    blocks, _ = _run(_ns(baseline=True, stage=2), synthetic, cfg, runtime, snap)
    b = parse_result_blocks(blocks[0])[0]
    assert b["stage"] == "baseline" and b["composite_sha"] == STAMPS["composite_sha"]
    assert b["composite_legs"] == ",".join(f.name for f in C_V0.active_factors())
    assert b["n_months"] > 12 and b["survivorship_max_gone_pct"] > 0
    assert validate_results(b, STAMPS["harness_sha"], STAMPS["config_sha"], cfg, STAMPS["data_sha"]) == []
    assert "delisting_adjusted_pct" in b and "ls_sharpe" in b


def test_baseline_with_the_holdout_emits_the_cut_fields(synthetic, cfg, runtime, snap):
    """The final validation reads the holdout from cut_holdout_* on a
    continuous run (the hedge beta needs history the holdout alone lacks)."""
    blocks, text = _run(_ns(baseline=True, stage=2, include_holdout=True), synthetic, cfg, runtime, snap)
    b = parse_result_blocks(blocks[0])[0]
    assert b["include_holdout"] == "True" and b["eval_end"] == cfg["dates"]["out_of_sample_end"]
    assert b["cut_holdout_n_months"] > 0 and b["cut_inwindow_n_months"] > 0
    assert b["cut_holdout_n_months"] + b["cut_inwindow_n_months"] == b["ls_n_months"]
    for k in ("cut_holdout_ic_mean", "cut_holdout_ls_sharpe", "cut_holdout_ls_raw_sharpe", "cut_holdout_ls_beta_mean",
              "cut_inwindow_ls_sharpe"):
        assert k in b, k
    assert "--- Cuts at " in text
    warns = validate_results(b, STAMPS["harness_sha"], STAMPS["config_sha"], cfg, STAMPS["data_sha"])
    assert any("OUT-OF-SAMPLE" in w for w in warns), "a holdout block must be flagged for the evaluator"


def test_holdout_only_block_says_the_holdout_was_measured(synthetic, cfg, runtime, snap):
    ns = _ns(baseline=True, stage=2); ns.holdout_only = True
    blocks, _ = _run(ns, synthetic, cfg, runtime, snap)
    b = parse_result_blocks(blocks[0])[0]
    assert b["include_holdout"] == "True" and b["eval_start"] == cfg["dates"]["out_of_sample_start"]


def test_stage3_constructs_the_composite_one_block_per_variant(synthetic, cfg, runtime, snap):
    blocks, text = _run(_ns(baseline=True, stage=3), synthetic, cfg, runtime, snap)
    parsed = parse_result_blocks("\n".join(blocks))
    # tier_neutral needs >= 50 names per tier and the fixture has ~27, so it
    # emits no block and says so; every other variant must.
    emitted = [b["variant"] for b in parsed]
    assert emitted == [v for v in cfg["construction"]["variants"] if v != "tier_neutral"]
    assert "tier_neutral: no months" in text
    for b in parsed:
        assert b["stage"] == "3" and b["composite_sha"] == STAMPS["composite_sha"]
        assert validate_results(b, STAMPS["harness_sha"], STAMPS["config_sha"], cfg, STAMPS["data_sha"]) == []
    assert "Stage 3: portfolio construction" in text
    f = _latest(synthetic, "*_CONSTRUCTION_stage3_*.txt")
    assert "## icir_weighted" in f.with_name(f.stem + "_summary.md").read_text()


def test_stage3_is_refused_for_candidates(synthetic, cfg, runtime, snap):
    with pytest.raises(SystemExit, match="ACCEPTED composite"):
        _run(_ns(factor="ValueLike", stage=3), synthetic, cfg, runtime, snap)


def test_holdout_is_refused_for_candidates(synthetic, cfg, runtime, snap):
    with pytest.raises(SystemExit, match="FINAL"):
        _run(_ns(factor="ValueLike", stage=2, include_holdout=True), synthetic, cfg, runtime, snap)


# ---- Stage 2 --------------------------------------------------------------------

def test_solo_stage2_verdict_agrees_with_check_stage2(synthetic, cfg, runtime, snap):
    blocks, text = _run(_ns(factor="Noise", stage=2), synthetic, cfg, runtime, snap)
    b = parse_result_blocks(blocks[0])[0]
    assert b["stage"] == "2" and "batch_size" not in b
    passed, details = check_stage2(b, cfg["acceptance_thresholds"]["stage2_marginal"])
    assert (b["ratchet_decision"] == "PASS") == passed
    assert b["ratchet_base_legs"] == ",".join(f.name for f in C_V0.active_factors())
    assert b["arm_months_aligned"] == "True"
    for k in ("resid_ic_tstat_nw", "spanning_alpha_tstat_nw", "spanning_r2", "paired_delta_ic_tstat",
              "paired_delta_ls_tstat", "delta_ls_sharpe", "maxdd_worsening_pct",
              "base_ls_ann_return_pct", "cand_ls_ann_return_pct", "family", "families_with",
              "family_weight_with", "base_ls_beta_mean", "cand_ls_beta_mean", "base_ls_beta_fullwindow",
              "cand_ls_beta_fullwindow", "cand_ls_raw_sharpe", "cand_ls_sharpe_ex_top_years"):
        assert k in b, k
    assert "LS beta (full)" in text and "diagnostics (never bars)" in text
    assert b["family"] == "noise" and b["families_with"].endswith("|noise:Noise")
    assert b["stage2_bars_failed"] in ("resid_ic_tstat_nw", "resid_ic_tstat_nw,paired_delta_ls_tstat",
                                       "paired_delta_ls_tstat", "(none)")
    assert "paired_delta_ic_tstat" not in b["stage2_bars_failed"]
    assert "Residual IC" in text and "Spanning alpha" in text and "Family blend" in text
    assert validate_results(b, STAMPS["harness_sha"], STAMPS["config_sha"], cfg, STAMPS["data_sha"]) == []


def test_noise_carries_no_residual_information(synthetic, cfg, runtime, snap):
    blocks, _ = _run(_ns(factor="Noise", stage=2), synthetic, cfg, runtime, snap)
    b = parse_result_blocks(blocks[0])[0]
    assert abs(b["resid_ic_tstat_nw"]) < 2.5 and b["ratchet_decision"] == "FAIL"


def test_ladder_rung1_is_numerically_identical_to_solo_stage2(synthetic, cfg, runtime, snap):
    solo, _ = _run(_ns(factor="ValueLike", stage=2), synthetic, cfg, runtime, snap)
    ladder, _ = _run(_ns(factors="ValueLike,Noise", stage=2), synthetic, cfg, runtime, snap)
    s = parse_result_blocks(solo[0])[0]
    r1, r2 = parse_result_blocks("\n".join(ladder))
    for k in ("resid_ic_tstat_nw", "spanning_alpha_tstat_nw", "paired_delta_ic_tstat",
              "paired_delta_ls_tstat", "delta_ls_sharpe", "corr_to_composite", "base_ls_sharpe",
              "cand_ls_sharpe", "n_months"):
        assert s[k] == pytest.approx(r1[k], abs=1e-12), k
    assert r1["ratchet_order"] == 1 and r2["ratchet_order"] == 2
    assert r1["batch_members"] == "ValueLike,Noise"
    if r1["ratchet_decision"] == "PASS":
        assert r2["ratchet_accepted_before"] == "ValueLike"
        assert r2["ratchet_base_legs"].endswith(",ValueLike")
        assert r2["base_ls_sharpe"] == pytest.approx(r1["cand_ls_sharpe"])
    else:
        assert r2["ratchet_accepted_before"] == "(none)"
    for b in (r1, r2):
        passed, _ = check_stage2(b, cfg["acceptance_thresholds"]["stage2_marginal"])
        assert (b["ratchet_decision"] == "PASS") == passed


def test_stage2_refuses_a_candidate_without_a_family(synthetic, cfg, runtime, snap):
    """The V3 rule: a family is assigned after Stage 1 and before any Stage 2
    number; the runner refuses to ratchet a candidate that has none."""
    with pytest.raises(SystemExit, match="family"):
        _run(_ns(factor="Massy", stage=2), synthetic, cfg, runtime, snap)


def test_stage2_refuses_a_family_count_over_the_cap(synthetic, cfg, runtime, snap):
    import copy
    tight = copy.deepcopy(cfg); tight["search"]["families_max"] = len(C_V0.families())
    with pytest.raises(SystemExit, match="families"):
        _run(_ns(factor="Noise", stage=2), synthetic, tight, runtime, snap)


def test_a_candidate_joining_a_seed_family_is_measured_inside_that_family(synthetic, cfg, runtime, snap):
    blocks, text = _run(_ns(factor="ValueLike", stage=2), synthetic, cfg, runtime, snap)
    b = parse_result_blocks(blocks[0])[0]
    assert b["family"] == "value" and "value:Value,ValueLike" in b["families_with"]
    n_fam = len(C_V0.families())
    assert float(b["family_weight_with"]) == pytest.approx(1 / (2 * n_fam))


def test_ladder_is_capped_at_five_rungs(synthetic, cfg, runtime, snap):
    with pytest.raises(SystemExit, match="capped"):
        _run(_ns(factors="A,B,C,D,E,F", stage=2), synthetic, cfg, runtime, snap)


def test_factors_needs_two_names(synthetic, cfg, runtime, snap):
    with pytest.raises(SystemExit, match="at least two"):
        _run(_ns(factors="ValueLike", stage=1), synthetic, cfg, runtime, snap)


def test_nodata_snapshot_is_refused(synthetic, cfg, runtime, snap):
    with pytest.raises(SystemExit, match="nodata"):
        RT.run(_ns(baseline=True, stage=2), C=C, cfg=cfg, runtime=runtime,
               stamps=dict(STAMPS, data_sha="nodata"), snap=snap, root=synthetic["root"])


def test_preflight_does_not_call_a_thin_cross_section_a_mass_point(synthetic, cfg, runtime, snap):
    def _lonely(ctx):
        s = pd.Series(np.nan, index=ctx.ids)
        s.iloc[0] = 1.5
        return s
    CANDS["Lonely"] = FactorDef(name="Lonely", col="f_lonely", compute=_lonely, ascending=True,
                                weight=1.0, inputs=("DAILY.marketcap",))
    try:
        blocks, text = _run(_ns(factors="ValueLike,Lonely", stage=1, dry_run=True), synthetic, cfg, runtime, snap)
        assert "PREFLIGHT FAILED" not in text and "dry run complete" in text
    finally:
        del CANDS["Lonely"]
