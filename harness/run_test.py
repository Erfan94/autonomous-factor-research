#!/usr/bin/env python3
"""
Run one factor test on the frozen Sharadar snapshot, locally, end to end.

    python3 harness/run_test.py --baseline --stage 2                 # measure the composite
    python3 harness/run_test.py --baseline --stage 3                 # construct the composite (portfolio variants)
    python3 harness/run_test.py --baseline --construction-layer      # Phase E layer (config/construction_layer.yaml)
    python3 harness/run_test.py --factors A,B,C,D,E,F,G,H --stage 1  # batch screen
    python3 harness/run_test.py --factor A --stage 2                 # ratchet, ONE passer
    python3 harness/run_test.py --factors A,B,C --stage 2            # batched ladder (max 5)
    python3 harness/run_test.py --baseline --stage 2 --include-holdout   # FINAL ONLY
    python3 harness/run_test.py --factors A,B --stage 1 --dry-run    # preflight only

Every result block carries HARNESS_SHA, CONFIG_SHA, COMPOSITE_SHA (Stage 2,
3 and baseline), DATA_SHA and UNIVERSE_SHA, computed from the repo at run
time; factor-evaluator refuses a result whose stamps do not match the repo.

Output, per run, in research/results/:
    NNN_<label>_stage<N>_<date>.txt          full report + result blocks (the record)
    NNN_<label>_stage<N>_<date>_summary.md   a few KB per member: verdict, bars,
                                             decile shape, tiers, annual IC (what
                                             the evaluator reads first)
    NNN_<label>_stage<N>_<date>.meta.json    stamps and timing

The Stage 2 ladder decides in-script because rung i+1's base depends on rung
i's verdict; every rung emits a full block and factor-evaluator re-derives
the verdict via check_stage2(). A disagreement is an integrity failure.
"""

import argparse
import importlib.util
import io
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from harness import analytics as A                                          # noqa: E402
from harness.analytics import (SERIES_KEYS, align_arms, assign_composite_decile,  # noqa: E402
                               compute_bucket_diagnostics, compute_ic,
                               compute_leg_coverage, emit_result_block, family_members,
                               family_weights,
                               leg_coverage_scalars, ls_month_floor, print_bucket_diagnostics,
                               print_summary, rank_one_factor, render_progress,
                               residual_ic_series, spanning_test, stage1_checks,
                               stage2_checks, survivorship_check, tier_scalars, nw_tstat)
from harness.data_layer import (PanelIndex, build_rebalance_schedule,      # noqa: E402
                                compute_month_frame, last_completed_month_end,
                                load_or_build_cs_spread, load_or_build_ff3, load_or_build_market,
                                load_or_build_panel, load_or_build_ps,
                                load_or_build_tailex, load_or_build_trend, load_snapshot)
from harness import construction_layer as CL                                # noqa: E402
from harness.portfolio import run_construction                              # noqa: E402
from harness.preflight import probe_scalars, run_preflight                  # noqa: E402
from harness.provenance import (ACCEPTED_DIR, CANDIDATES_DIR, ROOT,        # noqa: E402
                                all_stamps, load_config, load_runtime)

RUNNER_VERSION = "2.0.0"
LAYER_STAGE = "E"                  # Phase E: the construction layer's run token (file name, meta)
MAX_LADDER_RUNGS = 5
EARLY_ABORT_MONTHS = 3
BAR_OPS = {"ge": ">=", "gt": ">", "le": "<=", "lt": "<"}   # bar direction -> printed comparator


# =============================================================================
# Loading factors
# =============================================================================

def load_candidate(name, candidates_dir=CANDIDATES_DIR):
    p = Path(candidates_dir) / f"{name}.py"
    if not p.exists():
        raise FileNotFoundError(f"no candidate {p}. Translate it first (sharadar-translator).")
    spec = importlib.util.spec_from_file_location(f"candidate_{name}", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    f = getattr(mod, "FACTOR", None)
    if f is None:
        raise AttributeError(f"{p} defines no FACTOR")
    if f.name != name:
        raise ValueError(f"{p} defines FACTOR.name={f.name!r}, expected {name!r}")
    return f


def load_composite():
    import factors.composite as C
    return C


# =============================================================================
# Backtest engine
# =============================================================================

def precompute_month_frames(snap, pidx, factors, schedule, cfg, label="Backtest", log=print):
    """Universe + every factor column + forward return for every month, ONCE.
    Every arm and every batch member is scored off these frames."""
    sf1_cache = {}
    frames, failures = [], {}
    total, t0 = len(schedule), time.time()
    for i, (reb, sig, rs, re_) in enumerate(schedule):
        try:
            fr = compute_month_frame(snap, pidx, sf1_cache, factors, reb, sig, rs, re_, cfg)
            if fr is not None and fr["monthly_ret"].notna().any():
                frames.append(fr)
        except Exception as e:
            sigx = f"{type(e).__name__}: {e}"
            if sigx not in failures:
                log(f"\n  [warn] {sig.date()}: {sigx}")
            failures[sigx] = failures.get(sigx, 0) + 1
        if not frames and (i + 1) >= EARLY_ABORT_MONTHS:
            diag = "".join(f"      {n:>4}x  {s}\n" for s, n in failures.items()) or \
                   "      every month returned an empty universe or no returns\n"
            raise SystemExit(f"\nABORTED after {i + 1} of {total} months — not one produced "
                             f"usable rows.\n\n{diag}")
        print(f"\r{render_progress(i + 1, total, reb, t0, label)}", end="", flush=True)
    print()
    if failures:
        n = sum(failures.values())
        log(f"\n  [warn] {n} of {total} months failed and are ABSENT from the sample:")
        for s, k in sorted(failures.items(), key=lambda kv: -kv[1]):
            log(f"      {k:>4}x  {s}")
    return frames


def score_arm(frames, metas, weights, n_deciles, group_col=None):
    """Rank, blend and cut deciles for one composite over every month.
    Returns (factor_monthly, count_monthly, audit). group_col: the within-
    group ranking of config `ranking` (A.rank_group_col)."""
    ret_slices, cnt_slices, audits = [], [], []
    keep_cols = ["ID", "DATE", "monthly_ret", "ret_kind", "RET_START", "RET_END", "SIGNAL_ASOF",
                 "region", "liq_tier", "sector", "industry_group", "mkt_cap_usd", "adv_usd"]
    for fr in frames:
        df = assign_composite_decile(fr, metas, weights, n_deciles, group_col=group_col)
        cols = [c for c in keep_cols if c in df.columns] + ["DECILE", "COMPOSITE_SCORE"]
        cols += [m["col"] for m in metas if m["col"] in df.columns]
        audits.append(df[cols])
        long = df.dropna(subset=["DECILE", "monthly_ret"])
        if long.empty:
            continue
        g = long.groupby(["DATE", "DECILE"])["monthly_ret"]
        ret = g.mean().unstack("DECILE").sort_index()
        ret.columns = [f"D{int(c)}" for c in ret.columns]
        cnt = g.count().unstack("DECILE").sort_index()
        cnt.columns = [f"N_D{int(c)}" for c in cnt.columns]
        if f"D{n_deciles}" in ret.columns and "D1" in ret.columns:
            ret["LS"] = ret[f"D{n_deciles}"] - ret["D1"]
        else:
            ret["LS"] = pd.NA
        ret_slices.append(ret)
        cnt_slices.append(cnt)
    if not ret_slices:
        return None, None, None
    fm = pd.concat(ret_slices).sort_index()
    fm = fm[~fm.index.duplicated(keep="first")]
    cm = pd.concat(cnt_slices).sort_index()
    cm = cm[~cm.index.duplicated(keep="first")]
    audit = pd.concat(audits, ignore_index=True).sort_values("DATE").reset_index(drop=True)
    return fm, cm, audit


def print_leg_coverage(cov):
    overall = cov.get("overall")
    if overall is None or len(overall) == 0:
        print("  (no factor legs on the audit frame — coverage unavailable)")
        return
    print("\n\n  --- Per-leg coverage (% of universe-months with a non-null leg) ---")
    for leg, pct in overall.items():
        print(f"    {leg:<28s} {pct:6.2f}%  {'#' * int(round(pct / 4.0))}")
    lp = cov.get("legs_per_name", {})
    if lp and lp.get("n_legs_total", 0) > 1:
        print(f"\n    Legs per scored name: mean {lp.get('mean_legs', float('nan')):.2f} of {lp.get('n_legs_total')}")
        print(f"    Names scored on ALL legs      : {lp.get('pct_full', float('nan')):6.2f}%")
        print(f"    Names scored on HALF or fewer : {lp.get('pct_half_or_less', float('nan')):6.2f}%")
    by = cov.get("by_sector")
    if by is not None and len(by):
        print("\n  Coverage by sector (worst-covered sector first):")
        with pd.option_context("display.width", 200, "display.max_columns", 50,
                               "display.float_format", lambda v: f"{v:6.1f}"):
            print(by.to_string())


def print_return_kinds(audit):
    if "ret_kind" not in audit.columns:
        return
    vc = audit.dropna(subset=["monthly_ret"])["ret_kind"].value_counts()
    tot = int(vc.sum())
    print("\n  --- Forward-return composition ---")
    for k, n in vc.items():
        print(f"    {k:<32s} {n:>10,d}  {100.0 * n / tot:6.2f}%")


def full_report(title, fm, cm, audit, cfg, metas=None, oos_start=None):
    ic_df = compute_ic(audit)
    if len(ic_df) == 0:
        print("  (no months with a computable IC)")
        return None, None
    stats = print_summary(title, fm, cm, ic_df, audit,
                          nw_lags=int(cfg["statistics"]["newey_west_lags"]),
                          hedge=A.hedge_params(cfg), regime=A.regime_params(cfg), oos_start=oos_start)
    print("\n\n  Per-(region × liq_tier) diagnostics")
    print("=" * 72)
    buckets = compute_bucket_diagnostics(audit)
    print_bucket_diagnostics(buckets)
    if stats is not None:
        stats.update(tier_scalars(buckets))
    if metas:
        cov = compute_leg_coverage(audit, metas)
        print_leg_coverage(cov)
        if stats is not None:
            stats.update(leg_coverage_scalars(cov))
    print_return_kinds(audit)
    if stats is not None and "ret_kind" in audit.columns:
        d = audit.dropna(subset=["monthly_ret"])["ret_kind"]
        stats["delisting_adjusted_pct"] = float(100.0 * d.str.startswith("partial_delisted").mean())
    print("\n\n  --- Survivorship-bias check ---")
    gone = survivorship_check(audit)
    if stats is not None:
        stats["survivorship_max_gone_pct"] = gone
    return stats, buckets


def _solo_ls(audit, meta, n_deciles, group_col=None, hedge=None):
    """Standalone long-short for ONE candidate off the rung's own audit frame,
    ranked and hedged exactly as the composite is (the spanning diagnostic
    compares like with like)."""
    if meta["col"] not in audit.columns:
        return pd.Series(dtype=float)
    extra = [c for c in (group_col, "mkt_cap_usd") if c and c in audit.columns]
    solo = audit[["ID", "DATE", meta["col"], "monthly_ret"] + extra].dropna(
        subset=["ID", "DATE", meta["col"], "monthly_ret"]).copy()
    parts = []
    for dt, sub in solo.groupby("DATE"):
        rk = rank_one_factor(sub, meta["col"], ascending=meta["ascending"], winsorize=meta["winsorize"],
                             group_col=group_col)
        if rk.notna().sum() < n_deciles:
            continue
        d = pd.qcut(rk.dropna(), n_deciles, labels=False, duplicates="drop")
        if d.isna().all():
            continue
        top = sub.loc[d[d == d.max()].index, "monthly_ret"].mean()
        bot = sub.loc[d[d == d.min()].index, "monthly_ret"].mean()
        if pd.notna(top) and pd.notna(bot):
            parts.append({"DATE": pd.Timestamp(dt), "LS": top - bot})
    if not parts:
        return pd.Series(dtype=float)
    ls = pd.DataFrame(parts).set_index("DATE")["LS"].sort_index()
    if hedge:
        ls, _ = A.hedge_long_short(ls, A.universe_market_return(audit),
                                   hedge["beta_window_months"], hedge["beta_min_months"])
    return ls


def _verdict(checks):
    """(ok, rows) from a list of (name, value, bound, direction)."""
    rows, ok = [], True
    for name, val, bound, d in checks:
        if val is None or val != val:
            rows.append((name, val, bound, d, "MISSING")); ok = False; continue
        good = {"ge": val >= bound, "gt": val > bound, "le": val <= bound, "lt": val < bound}[d]
        rows.append((name, val, bound, d, "PASS" if good else "FAIL"))
        ok = ok and good
    return ok, rows


def _print_bars(rows, title):
    print(f"\n  --- {title} (ALL must hold) ---")
    for cn, cv, cb, cd, cr in rows:
        vs = "    n/a" if (cv is None or cv != cv) else f"{cv:+.6f}"
        print(f"    {cn:<26}{vs:>14}  {BAR_OPS[cd]:<2} {cb:<10}  {cr}")


def _families_str(metas):
    """'size:Size|value:Value,X|...' — the family table a block records."""
    return "|".join(f"{fam}:{','.join(names)}" for fam, names in family_members(metas).items())


def _print_families(metas, title="Family blend"):
    groups = family_members(metas)
    n = len(groups)
    print(f"\n  {title}: {n} families, 1/{n} each, equal within (two-level, renormalised)")
    for fam, names in groups.items():
        print(f"      {fam:<16} 1/{n} -> {', '.join(names)}  (1/{n * len(names)} each)")


def _common_fields(stamps, cfg, eval_start, eval_end, include_holdout, factors):
    dims = {f.col: f.dimension for f in factors if f.dimension}
    gates = {f.col: f.history_months for f in factors if f.history_months is not None}
    return {"harness_sha": stamps["harness_sha"], "config_sha": stamps["config_sha"],
            "data_sha": stamps["data_sha"], "universe_sha": stamps["universe_sha"],
            "eval_start": eval_start, "eval_end": eval_end,
            "include_holdout": str(bool(include_holdout)),
            "dimension_overrides": repr(dims), "history_gates": repr(gates)}


def _summary_record(name, stage, stats, buckets, rows, verdict, extra=None):
    """What the summary file carries per member. Small on purpose."""
    rec = {"name": name, "stage": stage, "verdict": verdict, "bars": rows,
           "stats": {k: v for k, v in (stats or {}).items() if k not in SERIES_KEYS},
           "annual_ic": {}, "tiers": []}
    if stats is not None and "ic_series" in stats:
        ic = stats["ic_series"]
        rec["annual_ic"] = {int(y): float(v) for y, v in ic.groupby(ic.index.year).mean().items()}
    if buckets is not None and len(buckets):
        for _, r in buckets.iterrows():
            rec["tiers"].append((str(r["tier"]), float(r["mean_IC"]), r["ICIR"], r["LS_Sharpe"],
                                 r["LS_ann_%"], int(r["avg_N"])))
    if extra:
        rec.update(extra)
    return rec


# =============================================================================
# Drivers
# =============================================================================

def drive_stage1(frames, candidates, cfg, stamps, eval_start, eval_end, include_holdout, probes):
    n_dec = int(cfg["rebalance"]["n_deciles"])
    thr = cfg["acceptance_thresholds"]["stage1_standalone"]
    blocks, summaries = [], []
    names = ",".join(f.name for f in candidates)
    print(f"\n  BATCH STAGE 1 — {len(candidates)} members, screened independently off one panel.")
    print("  DECLARATION ORDER = Stage 2 order, fixed now:")
    for i, f in enumerate(candidates):
        print(f"      {i + 1}. {f.name:<24} col={f.col}")
    for f in candidates:
        meta = f.meta()
        fm, cm, audit = score_arm(frames, [meta], None, n_dec, A.rank_group_col(cfg))
        print("\n\n" + "#" * 72 + f"\n#  STAGE 1 : {f.name}\n" + "#" * 72)
        if fm is None:
            print(f"  {f.name}: no month produced deciles — no result block.")
            continue
        cov = 100.0 * audit[f.col].notna().mean()
        stats, buckets = full_report(f"US UNIVERSE  —  {f.name} (standalone)", fm, cm, audit, cfg, [meta])
        if stats is None:
            continue
        values = dict(stats); values["coverage_pct"] = cov
        floor = ls_month_floor(stats["n_months"], cfg["rebalance"]["min_months"])
        ok, rows = _verdict(stage1_checks(values, thr, floor))
        _print_bars(rows, "Stage 1 bars")
        print(f"\n  STAGE 1 VERDICT: {'PASS' if ok else 'FAIL'} — "
              + ("earns a Stage 2 rung." if ok else "does not reach Stage 2."))
        fields = {"stage": "1", "factor": f.name}
        fields.update(_common_fields(stamps, cfg, eval_start, eval_end, include_holdout, [f]))
        fields.update({"batch_size": len(candidates), "batch_members": names,
                       "declaration_order": candidates.index(f) + 1, "coverage_pct": cov,
                       "stage1_decision": "PASS" if ok else "FAIL",
                       "stage1_bars_failed": ",".join(r[0] for r in rows if r[4] != "PASS") or "(none)"})
        fields.update(probes.get(f.name, {}))
        fields.update({k: v for k, v in stats.items() if k not in SERIES_KEYS})
        blocks.append(emit_result_block(fields))
        summaries.append(_summary_record(f.name, "1", values, buckets, rows, "PASS" if ok else "FAIL"))
    return blocks, summaries


def drive_baseline(frames, legs, cfg, stamps, eval_start, eval_end, include_holdout, probes, C):
    n_dec = int(cfg["rebalance"]["n_deciles"])
    metas = [f.meta() for f in legs]
    _print_families(metas)
    fm, cm, audit = score_arm(frames, metas, None, n_dec, A.rank_group_col(cfg))
    if fm is None:
        print("FATAL: no data collected — nothing to evaluate.")
        return [], []
    stats, buckets = full_report(f"US UNIVERSE  —  {len(metas)}-factor composite {C.COMPOSITE_VERSION}, "
                                 "family blend", fm, cm, audit, cfg, metas,
                                 oos_start=(cfg["dates"]["out_of_sample_start"] if include_holdout else None))
    if stats is None:
        return [], []
    cov = 100.0 * audit["COMPOSITE_SCORE"].notna().mean()
    fields = {"stage": "baseline", "factor": f"BASELINE_{C.COMPOSITE_VERSION}",
              "composite_sha": stamps["composite_sha"], "composite_version": C.COMPOSITE_VERSION,
              "composite_legs": ",".join(f.name for f in legs),
              "composite_families": _families_str(metas)}
    fields.update(_common_fields(stamps, cfg, eval_start, eval_end, include_holdout, legs))
    fields["coverage_pct"] = cov
    fields.update({k: v for k, v in stats.items() if k not in SERIES_KEYS})
    values = dict(stats); values["coverage_pct"] = cov
    return [emit_result_block(fields)], [_summary_record(fields["factor"], "baseline", values, buckets, [], "MEASURED")]


def drive_stage3(frames, legs, cfg, stamps, eval_start, eval_end, include_holdout, C):
    """Portfolio construction on the live composite. Reports, never decides."""
    n_dec = int(cfg["rebalance"]["n_deciles"])
    metas = [f.meta() for f in legs]
    _print_families(metas)
    fm, cm, audit = score_arm(frames, metas, None, n_dec, A.rank_group_col(cfg))
    if fm is None:
        print("FATAL: no data collected — nothing to construct.")
        return [], []
    print("\n\n" + "#" * 72 + f"\n#  STAGE 3 : construction of {C.COMPOSITE_VERSION} "
          f"({', '.join(m['name'] for m in metas)})\n" + "#" * 72)
    results = run_construction(audit, metas, cfg)
    blocks, summaries = [], []
    for variant, st in results:
        if st.get("n_months", 0) < 2:
            print(f"  {variant}: no months produced a long-short — no block emitted.")
            continue
        fields = {"stage": "3", "factor": f"CONSTRUCTION_{C.COMPOSITE_VERSION}", "variant": variant,
                  "composite_sha": stamps["composite_sha"], "composite_version": C.COMPOSITE_VERSION,
                  "composite_legs": ",".join(f.name for f in legs),
                  "composite_families": _families_str(metas)}
        fields.update(_common_fields(stamps, cfg, eval_start, eval_end, include_holdout, legs))
        fields.update({k: v for k, v in st.items() if k not in SERIES_KEYS})
        blocks.append(emit_result_block(fields))
        summaries.append({"name": variant, "stage": "3", "verdict": "REPORTED", "bars": [],
                          "stats": {k: v for k, v in st.items() if k not in SERIES_KEYS},
                          "annual_ic": {}, "tiers": []})
    return blocks, summaries


def drive_layer(frames, legs, cfg, stamps, eval_start, eval_end, include_holdout, holdout_only, C,
                lcfg, layer_sha, paths_path=None, info=None, spread=None):
    """Phase E: the construction layer on the live composite, scored exactly as
    `--baseline --stage 2` scores it. One block per (row, AUM). Reports, never
    decides (D8, D15). The monthly path of every (row, AUM) is written to
    `paths_path` (…paths.csv beside the .txt); its hash is each block's paths_sha.
    `spread`: the harness-built Corwin-Schultz series the cost model reads
    (data_layer.load_or_build_cs_spread; D7 item 2)."""
    n_dec = int(cfg["rebalance"]["n_deciles"])
    metas = [f.meta() for f in legs]
    _print_families(metas)
    fm, cm, audit = score_arm(frames, metas, None, n_dec, A.rank_group_col(cfg))
    if fm is None:
        print("FATAL: no data collected — nothing to construct.")
        return [], []
    print("\n\n" + "#" * 72 + f"\n#  CONSTRUCTION LAYER : {C.COMPOSITE_VERSION} "
          f"(LAYER_SHA {layer_sha}, book from {lcfg['window']['book_start']})\n" + "#" * 72)
    oos = cfg["dates"]["out_of_sample_start"] if (include_holdout or holdout_only) else None
    results, meta = CL.run_layer(audit, metas, cfg, lcfg, stamps["composite_sha"], oos_start=oos, spread=spread)
    CL.print_layer_table(results)
    print(f"\n  first live month {meta['first_live_month']}; risk model first ready {meta['risk_first_ready']}; "
          f"vol factor first estimable {meta['vol_factor_first_month']}; {meta['sector_groups']} sector groups")
    print(f"  constraints {meta['constraints']}; market beta first estimable {meta['market_beta_first_month']}, "
          f"own estimate for {_f(meta['market_beta_own_estimate_pct'])}% of book name-months (rest: "
          f"sector-month median); CS spread measured on {_f(meta['spread_measured_pct'])}% of ID-months")
    print("  In-window figures describe TRADABILITY of a composite selected on this window, not an "
          "expected return (CONSTRUCTION.md §1).")
    paths_sha = "none"
    if paths_path is not None:
        paths_sha = CL.write_paths_csv(meta["paths"], paths_path)
        print(f"  monthly paths: {Path(paths_path).name}  (paths_sha {paths_sha})")
    if info is not None:
        info.update({"paths_sha": paths_sha, "paths_file": Path(paths_path).name if paths_path else None})
    blocks, summaries = [], []
    for row, aum, st in results:
        variant = f"{row}@{CL.aum_tag(aum)}"
        fields = {"stage": LAYER_STAGE, "factor": f"LAYER_{C.COMPOSITE_VERSION}", "variant": variant,
                  "composite_sha": stamps["composite_sha"], "composite_version": C.COMPOSITE_VERSION,
                  "composite_legs": ",".join(f.name for f in legs),
                  "composite_families": _families_str(metas), "layer_sha": layer_sha}
        fields.update(_common_fields(stamps, cfg, eval_start, eval_end, include_holdout, legs))
        fields.update({"holdout_only": str(bool(holdout_only)), "layer_book_start": lcfg["window"]["book_start"],
                       "first_live_month": meta["first_live_month"], "risk_first_ready": meta["risk_first_ready"],
                       "vol_factor_first_month": meta["vol_factor_first_month"],
                       "sector_groups": meta["sector_groups"], "sector_group_labels": meta["sector_group_labels"],
                       "constraints": meta["constraints"], "market_beta_first_month": meta["market_beta_first_month"],
                       "market_beta_own_estimate_pct": meta["market_beta_own_estimate_pct"],
                       "spread_measured_pct": meta["spread_measured_pct"],
                       "paths_sha": paths_sha})
        fields.update({k: v for k, v in st.items() if k not in SERIES_KEYS})
        blocks.append(emit_result_block(fields))
        keys = ["gross_ann_return_pct", "net_ann_return_pct", "net_sharpe", "net_tstat_nw", "net_beta_on_market",
                "exp_beta_mean", "net_maxdd_pct",
                "net_maxdd_peak", "net_maxdd_trough", "net_worst_12m_pct", "turnover_oneway_pct",
                "reproj_share_of_turnover_pct", "cost_spread_ann_pct", "cost_impact_ann_pct", "cost_borrow_ann_pct",
                "participation_hit_share_pct", "budget_scaled_months", "flat_months", "avg_n_long",
                "avg_n_short", "bias_stat_mean", "cut_exyears_net_sharpe", "cut_2011_2020_net_sharpe",
                "cut_holdout_net_sharpe"]
        line = "  ".join(f"{k}={_f(st[k])}" for k in keys if k in st)
        tiers = "; ".join(f"{t} net {_f(st.get(f'tier_{t}_net_ann_return_pct'))}% cost {_f(st.get(f'tier_{t}_cost_ann_pct'))}%"
                          for t in CL.TIERS)
        cut_keys = ["net_n_months", "gross_ann_return_pct", "net_ann_return_pct", "net_sharpe", "net_tstat_nw",
                    "net_beta_on_market",
                    "net_maxdd_pct", "net_maxdd_peak", "net_maxdd_trough", "net_worst_12m_pct",
                    "turnover_oneway_pct", "cost_spread_ann_pct", "cost_impact_ann_pct", "cost_borrow_ann_pct",
                    "flat_months", "budget_scaled_months_live", "gross_budget_mean_live",
                    "participation_hit_share_pct", "new_positions_delisting_n"]
        cuts = [f"{pre[:-1]}: " + "  ".join(f"{k}={_f(st[pre + k])}" for k in cut_keys if pre + k in st)
                for pre in ("cut_holdout_", "cut_inwindow_", "cut_exyears_", "cut_2011_2020_")
                if f"{pre}net_n_months" in st]
        summaries.append({"name": variant, "stage": LAYER_STAGE, "verdict": "REPORTED", "bars": [], "stats": {},
                          "annual_ic": {}, "tiers": [],
                          "extra_lines": [f"{st.get('row_note') or row}", line, f"by tier: {tiers}", *cuts,
                                          f"annual net %: {st.get('annual_net_returns_pct', '')}"]})
    return blocks, summaries


def drive_stage2(frames, legs, candidates, cfg, stamps, eval_start, eval_end, include_holdout, probes, C):
    """The batched sequential ratchet. Rung i faces the base PLUS every earlier
    rung that PASSED, in declaration order."""
    n_dec = int(cfg["rebalance"]["n_deciles"])
    thr = cfg["acceptance_thresholds"]["stage2_marginal"]
    lags = int(cfg["statistics"]["newey_west_lags"])
    base_meta = [f.meta() for f in legs]
    solo = len(candidates) == 1
    print(f"\n  {'SOLO' if solo else 'BATCHED SEQUENTIAL'} RATCHET — {len(candidates)} candidate(s).")
    print(f"  Base composite {C.COMPOSITE_VERSION}: {', '.join(m['name'] for m in base_meta)}")
    if not solo:
        print("\n  DECLARATION ORDER — fixed before any number exists:")
        for i, f in enumerate(candidates):
            print(f"      {i + 1}. {f.name:<24} col={f.col}")

    _print_families(base_meta, "Base family blend")
    gc = A.rank_group_col(cfg)
    base_fm, base_cm, base_audit = score_arm(frames, base_meta, None, n_dec, gc)
    if base_fm is None:
        print("FATAL: base arm produced no data.")
        return [], []
    print("\n\n" + "#" * 72 + "\n#  BASE ARM\n" + "#" * 72)
    cur_stats, _ = full_report(f"US UNIVERSE  —  {len(base_meta)}-factor composite, family blend",
                               base_fm, base_cm, base_audit, cfg, base_meta)
    del base_fm, base_cm, base_audit
    cur_meta, accepted, blocks, summaries, ladder = list(base_meta), [], [], [], []
    members = ",".join(f.name for f in candidates)

    for i, f in enumerate(candidates):
        meta = f.meta()
        trial = cur_meta + [meta]
        base_legs = ",".join(m["name"] for m in cur_meta)
        print("\n\n" + "#" * 72)
        print(f"#  RUNG {i + 1} of {len(candidates)} : {f.name}")
        print(f"#  base ({len(cur_meta)} legs) : {base_legs}")
        print(f"#  accepted so far      : {', '.join(accepted) if accepted else '(none — base is the declared composite)'}")
        print(f"#  candidate family     : {f.family}")
        print("#" * 72 + "\n")
        _print_families(trial, f"Family blend WITH {f.name}")
        fm, cm, audit = score_arm(frames, trial, None, n_dec, gc)
        if fm is None:
            print(f"FATAL: rung {i + 1} ({f.name}) produced no data — the ladder stops here.")
            break
        stats, buckets = full_report(f"US UNIVERSE  —  {len(trial)}-factor composite (base + {f.name}), "
                                     "family blend", fm, cm, audit, cfg, trial)
        if stats is None or cur_stats is None:
            print(f"FATAL: rung {i + 1} ({f.name}) produced no statistics — the ladder stops here.")
            break
        cov = 100.0 * audit[f.col].notna().mean()

        # --- the marginal-information tests, construction-invariant --------
        resid = residual_ic_series(audit, cur_meta, meta, group_col=gc)
        resid_mean = float(resid["IC"].mean()) if len(resid) else float("nan")
        resid_t = float(nw_tstat(resid["IC"], lags)) if len(resid) else float("nan")
        solo_ls = _solo_ls(audit, meta, n_dec, gc, A.hedge_params(cfg))
        span = spanning_test(solo_ls, cur_stats["ls_series"], lags)
        arm = align_arms(cur_stats, stats, lags)
        # HD-001/HD-002: the share is residual IC over the candidate's OWN IC on this
        # frame; solo_ic_mean is named apart from the cand_-prefixed WITH-arm stats.
        solo_ic = A.standalone_ic_series(audit, meta, group_col=gc)
        solo_ic_mean = float(solo_ic["IC"].mean()) if len(solo_ic) else float("nan")
        del fm, cm, audit

        values = {"resid_ic_mean": resid_mean, "resid_ic_tstat_nw": resid_t, "resid_ic_n": int(len(resid)),
                  "solo_ic_mean": solo_ic_mean,
                  "resid_ic_share": float(A._safe_ratio(resid_mean, solo_ic_mean))}
        values.update(span)
        values.update(arm)
        ok, rows = _verdict(stage2_checks(values, thr))

        print("\n\n" + "=" * 72 + f"\n  RATCHET RUNG {i + 1} — {f.name} against {len(cur_meta)} legs\n" + "=" * 72)
        print(f"  Residual IC (after the base legs) : mean {resid_mean:+.4f}  NW t {resid_t:+.2f}  "
              f"({len(resid)} months; {values['resid_ic_share'] * 100:.0f}% of the candidate's own IC "
              f"{solo_ic_mean:+.4f} on this frame)")
        print(f"  Spanning alpha (solo LS on base LS): {span['spanning_alpha_ann_pct']:+.2f}%/yr  "
              f"NW t {span['spanning_alpha_tstat_nw']:+.2f}  beta {span['spanning_beta']:+.2f}  "
              f"R2 {span['spanning_r2']:.2f}  corr {span['corr_to_composite']:+.2f}")
        print(f"\n  Composite under the SEARCH construction (family blend) — the paired LS-return guard\n"
              "  is a BAR; the paired IC delta, Sharpe and MaxDD are diagnostics:")
        print(f"  {'':<18}{'WITHOUT':>12}{'WITH':>12}{'DELTA':>12}{'paired t':>10}")
        print(f"  {'Mean IC':<18}{cur_stats['ic_mean']:>12.4f}{stats['ic_mean']:>12.4f}"
              f"{arm['paired_delta_ic_mean']:>+12.5f}{arm['paired_delta_ic_tstat']:>+10.2f}")
        print(f"  {'LS Sharpe':<18}{cur_stats['ls_sharpe']:>12.4f}{stats['ls_sharpe']:>12.4f}"
              f"{arm['delta_ls_sharpe']:>+12.4f}{arm['paired_delta_ls_tstat']:>+10.2f}")
        print(f"  {'LS MaxDD %':<18}{cur_stats['ls_maxdd_pct']:>12.2f}{stats['ls_maxdd_pct']:>12.2f}"
              f"{arm['maxdd_worsening_pct']:>+12.2f}")
        print(f"  {'LS ann ret %':<18}{cur_stats['ls_ann_return_pct']:>12.4f}{stats['ls_ann_return_pct']:>12.4f}"
              f"{stats['ls_ann_return_pct'] - cur_stats['ls_ann_return_pct']:>+12.4f}{arm['paired_delta_ls_tstat']:>+10.2f}")
        k_top = A.regime_params(cfg)["ex_regime_top_years"]
        print(f"  {'-- diagnostics (never bars): the book the rule cannot see --':<62}")
        print(f"  {'LS beta (full)':<18}{cur_stats['ls_beta_fullwindow']:>12.3f}{stats['ls_beta_fullwindow']:>12.3f}"
              f"{stats['ls_beta_fullwindow'] - cur_stats['ls_beta_fullwindow']:>+12.3f}")
        print(f"  {'LS beta (ex ante)':<18}{cur_stats['ls_beta_mean']:>12.3f}{stats['ls_beta_mean']:>12.3f}"
              f"{stats['ls_beta_mean'] - cur_stats['ls_beta_mean']:>+12.3f}")
        print(f"  {'Raw LS Sharpe':<18}{cur_stats['ls_raw_sharpe']:>12.4f}{stats['ls_raw_sharpe']:>12.4f}"
              f"{stats['ls_raw_sharpe'] - cur_stats['ls_raw_sharpe']:>+12.4f}")
        print(f"  {f'Sharpe ex top-{k_top}y':<18}{cur_stats['ls_sharpe_ex_top_years']:>12.4f}"
              f"{stats['ls_sharpe_ex_top_years']:>12.4f}"
              f"{stats['ls_sharpe_ex_top_years'] - cur_stats['ls_sharpe_ex_top_years']:>+12.4f}"
              f"   (years without: {cur_stats['ls_top_years'] or '-'}; with: {stats['ls_top_years'] or '-'})")
        print(f"  {'Sharpe bear/bull':<18}{cur_stats['ls_sharpe_bear']:>6.2f}/{cur_stats['ls_sharpe_bull']:<5.2f}"
              f"{stats['ls_sharpe_bear']:>6.2f}/{stats['ls_sharpe_bull']:<5.2f}")
        _print_bars(rows, "Stage 2 bars")
        print(f"\n  RUNG {i + 1} VERDICT: {'PASS' if ok else 'FAIL'} — "
              + (f"{f.name} JOINS the composite." if ok else f"{f.name} does NOT join; the base is unchanged."))
        print("  (factor-evaluator re-derives this via check_stage2(); a disagreement is an integrity failure.)")

        fields = {"stage": "2", "factor": f.name, "composite_sha": stamps["composite_sha"],
                  "composite_version": C.COMPOSITE_VERSION}
        fields.update(_common_fields(stamps, cfg, eval_start, eval_end, include_holdout, legs + [f]))
        if not solo:
            fields.update({"batch_size": len(candidates), "batch_members": members})
        fields.update({"ratchet_order": i + 1, "ratchet_base_legs": base_legs,
                       "family": f.family, "families_with": _families_str(trial),
                       "family_weight_with": family_weights(trial)[f.name],
                       "ratchet_accepted_before": ",".join(accepted) if accepted else "(none)",
                       "ratchet_decision": "PASS" if ok else "FAIL", "coverage_pct": cov,
                       "stage2_bars_failed": ",".join(r[0] for r in rows if r[4] != "PASS") or "(none)"})
        fields.update(probes.get(f.name, {}))
        for k, v in cur_stats.items():
            if k not in SERIES_KEYS:
                fields["base_" + k] = v
        fields["n_months"] = cur_stats["n_months"]
        for k, v in stats.items():
            if k not in SERIES_KEYS:
                fields["cand_" + k] = v
        fields.update(values)
        blocks.append(emit_result_block(fields))
        ladder.append((i + 1, f.name, len(cur_meta), ok, resid_t, arm["paired_delta_ic_tstat"],
                       arm["paired_delta_ls_tstat"], span["spanning_alpha_tstat_nw"],
                       arm["delta_ls_sharpe"], span["corr_to_composite"],
                       stats["ls_beta_fullwindow"], stats["ls_sharpe_ex_top_years"]))
        s_values = dict(stats); s_values.update(values); s_values["coverage_pct"] = cov
        summaries.append(_summary_record(f.name, "2", s_values, buckets, rows, "PASS" if ok else "FAIL",
                                         {"base_legs": base_legs, "rung": i + 1,
                                          "base": {k: cur_stats[k] for k in ("ic_mean", "ls_sharpe", "ls_maxdd_pct", "ls_ann_return_pct")}}))
        if ok:
            accepted.append(f.name); cur_meta = trial; cur_stats = stats

    print("\n\n" + "=" * 72 + "\n  LADDER SUMMARY — rungs in declaration order\n" + "=" * 72)
    print(f"  {'#':<3}{'candidate':<22}{'base':>5}{'resid t':>9}{'dIC t':>8}{'dLS t':>8}{'span t':>8}{'dSharpe':>9}{'corr':>7}"
          f"{'beta':>7}{'exReg':>7}  verdict")
    for o, n, nb, ok2, rt, dt, lt, st_, ds, cr, bt, xr in ladder:
        print(f"  {o:<3}{n:<22}{nb:>5}{rt:>+9.2f}{dt:>+8.2f}{lt:>+8.2f}{st_:>+8.2f}{ds:>+9.3f}{cr:>+7.2f}"
              f"{bt:>+7.2f}{xr:>+7.2f}  {'PASS' if ok2 else 'FAIL'}")
    print("  (bars: resid t (> bound), dLS t; dIC t, span t, dSharpe, corr, the WITH-arm's full-window beta and its "
          "Sharpe ex the top LS years are diagnostics)")
    if accepted:
        print(f"\n  ACCEPTED, in order: {', '.join(accepted)}")
        print(f"  Final composite   : {len(cur_meta)} legs — {', '.join(m['name'] for m in cur_meta)}")
        print(f"  Final mean IC {cur_stats['ic_mean']:.6f}  LS Sharpe {cur_stats['ls_sharpe']:.6f}  "
              f"ann ret {cur_stats['ls_ann_return_pct']:.4f}%  MaxDD {cur_stats['ls_maxdd_pct']:.6f}")
        print("\n  NOTE the ladder is ORDER-DEPENDENT by construction; the order was fixed before any number existed.")
    else:
        print("\n  ACCEPTED: none. The composite is unchanged.")
    return blocks, summaries


# =============================================================================
# Summary file — what the evaluator reads first
# =============================================================================

_KEY_STATS = ["ic_mean", "ic_tstat_nw", "icir", "ic_half1_mean", "ic_half2_mean", "ls_sharpe",
              "ls_ann_return_pct", "ls_ann_vol_pct", "ls_maxdd_pct", "ls_hit_rate_pct",
              "turnover_d10_pct", "turnover_d1_pct", "coverage_pct", "avg_names_per_decile",
              "n_months", "ls_n_months", "delisting_adjusted_pct", "leg_coverage_pct_full",
              "resid_ic_mean", "resid_ic_tstat_nw", "spanning_alpha_ann_pct", "spanning_alpha_tstat_nw",
              "spanning_r2", "corr_to_composite", "paired_delta_ic_mean", "paired_delta_ic_tstat",
              "paired_delta_ls_mean", "paired_delta_ls_tstat",
              "delta_ls_sharpe", "maxdd_worsening_pct", "worst_12m_pct", "turnover_long_pct",
              "turnover_short_pct", "construction_weights",
              "ls_raw_sharpe", "ls_beta_mean", "ls_beta_fullwindow", "ls_sharpe_ex_top_years", "ls_top_years",
              "ls_sharpe_bear", "ls_sharpe_bull",
              "cut_inwindow_n_months", "cut_inwindow_ic_mean", "cut_inwindow_ic_tstat_nw", "cut_inwindow_ls_sharpe",
              "cut_inwindow_ls_ann_return_pct", "cut_inwindow_ls_maxdd_pct", "cut_inwindow_ls_raw_sharpe",
              "cut_inwindow_ls_beta_mean",
              "cut_holdout_n_months", "cut_holdout_ic_mean", "cut_holdout_ic_tstat_nw", "cut_holdout_ls_sharpe",
              "cut_holdout_ls_ann_return_pct", "cut_holdout_ls_maxdd_pct", "cut_holdout_ls_raw_sharpe",
              "cut_holdout_ls_beta_mean"]


def _f(v):
    if v is None:
        return "NA"
    if isinstance(v, float):
        return "NA" if v != v else (f"{v:.4f}" if abs(v) < 100 else f"{v:.1f}")
    return str(v)


def write_summary(path, header, summaries):
    lines = [f"# {header['title']}", "",
             f"stamps: HARNESS {header['harness_sha']} CONFIG {header['config_sha']} "
             f"COMPOSITE {header['composite_sha']} DATA {header['data_sha']}"
             + (f" LAYER {header['layer_sha']}" if header.get("layer_sha") else ""),
             f"window: {header['eval_start']} .. {header['eval_end']}  holdout_included: {header['include_holdout']}",
             f"composite: {header['composite']}", ""]
    for s in summaries:
        st = s["stats"]
        lines.append(f"## {s['name']}  (stage {s['stage']})  → **{s['verdict']}**")
        if s.get("rung"):
            b = s["base"]
            lines.append(f"rung {s['rung']} vs {s['base_legs']}  | base IC {b['ic_mean']:.4f} Sharpe {b['ls_sharpe']:.3f} "
                         f"ann ret {b['ls_ann_return_pct']:.2f}% MaxDD {b['ls_maxdd_pct']:.1f}")
        if s["bars"]:
            lines.append("| bar | value | bound | result |")
            lines.append("|---|---|---|---|")
            for cn, cv, cb, cd, cr in s["bars"]:
                lines.append(f"| {cn} | {_f(cv)} | {BAR_OPS[cd]} {cb} | {cr} |")
        keys = [k for k in _KEY_STATS if k in st and st[k] is not None]
        lines.append("stats: " + "  ".join(f"{k}={_f(st[k])}" for k in keys))
        if "decile_avg_ret_pct" in st:
            lines.append(f"deciles D1..D10 avg %/mo: {st['decile_avg_ret_pct']}")
        if "ls_beta_mean" in st:
            lines.append(f"hedge/regime (diagnostics): beta ex-ante {_f(st.get('ls_beta_mean'))} full-window "
                         f"{_f(st.get('ls_beta_fullwindow'))}  raw Sharpe {_f(st.get('ls_raw_sharpe'))}  "
                         f"Sharpe ex top years {_f(st.get('ls_sharpe_ex_top_years'))} ({st.get('ls_top_years') or '-'})  "
                         f"bear/bull {_f(st.get('ls_sharpe_bear'))}/{_f(st.get('ls_sharpe_bull'))}")
        if "cut_holdout_n_months" in st:
            for pre in ("cut_inwindow_", "cut_holdout_"):
                lines.append(f"{pre[:-1]}: " + "  ".join(f"{k}={_f(st.get(pre + k))}" for k in
                             ("n_months", "ic_mean", "ic_tstat_nw", "ls_sharpe", "ls_ann_return_pct", "ls_maxdd_pct",
                              "ls_raw_sharpe", "ls_beta_mean")))
        dec = [k for k in st if k.startswith("ic_decay_h")]
        if dec:
            lines.append("ic decay: " + "  ".join(f"{k[9:]}={_f(st[k])}" for k in dec))
        if s["tiers"]:
            lines.append("tiers (tier, IC, ICIR, Sharpe, ann%, avgN): "
                         + "; ".join(f"{t} {ic:.4f} {_f(icir)} {_f(sh)} {_f(ar)} {n}" for t, ic, icir, sh, ar, n in s["tiers"]))
        if s["annual_ic"]:
            lines.append("annual IC: " + " ".join(f"{y}:{v:+.3f}" for y, v in s["annual_ic"].items()))
        if "annual_returns_pct" in st:
            lines.append(f"annual LS %: {st['annual_returns_pct']}")
        lines.extend(s.get("extra_lines", []))
        lines.append("")
    Path(path).write_text("\n".join(lines), encoding="utf-8")


# =============================================================================
# Orchestration
# =============================================================================

class Tee(io.TextIOBase):
    def __init__(self, *streams):
        self.streams = streams
    def write(self, s):
        for st in self.streams:
            st.write(s)
        return len(s)
    def flush(self):
        for st in self.streams:
            st.flush()


SEQ_RE = re.compile(r"^(\d{3})_.*\.txt$")


def next_seq(results_dir):
    n = 0
    for p in Path(results_dir).glob("*.txt"):
        m = SEQ_RE.match(p.name)
        if m:
            n = max(n, int(m.group(1)))
    return n + 1


def resolve_run(args, C, cfg=None):
    legs = C.active_factors()
    if getattr(args, "construction_layer", False):
        if not args.baseline or args.factor or args.factors:
            raise SystemExit("--construction-layer runs on the live composite only: use --baseline --construction-layer")
        return legs, [], "LAYER"
    if args.baseline:
        if args.factor or args.factors:
            raise SystemExit("--baseline takes no --factor/--factors")
        if args.stage not in (2, 3):
            raise SystemExit("--baseline is a Stage 2 measurement or a Stage 3 construction of the composite")
        return legs, [], "BASELINE" if args.stage == 2 else "CONSTRUCTION"
    if args.stage == 3:
        raise SystemExit("--stage 3 constructs the ACCEPTED composite only: use --baseline --stage 3")
    names = []
    if args.factors:
        names = [n.strip() for n in args.factors.split(",") if n.strip()]
        if len(names) < 2:
            raise SystemExit("--factors needs at least two names; use --factor for one")
    elif args.factor:
        names = [args.factor.strip()]
    else:
        raise SystemExit("one of --baseline, --factor NAME, --factors A,B,... is required")
    if len(set(names)) != len(names):
        raise SystemExit(f"duplicate names in the batch: {names}")
    if args.stage == 2 and len(names) > MAX_LADDER_RUNGS:
        raise SystemExit(f"a Stage 2 ladder is capped at {MAX_LADDER_RUNGS} rungs; split it in "
                         "declaration order (CLAUDE.md).")
    cands = [load_candidate(n) for n in names]
    for c in cands:
        if any(c.name == l.name or c.col == l.col for l in legs):
            raise SystemExit(f"{c.name}/{c.col} collides with a composite leg")
    if args.stage == 2:
        missing = [c.name for c in cands if c.family is None]
        if missing:
            raise SystemExit("Stage 2 needs a family on every candidate, assigned after Stage 1 and "
                             f"before any Stage 2 number (research/families.yaml): {missing} have none")
        fmax = int(((cfg or {}).get("search") or {}).get("families_max", 0) or 0)
        if fmax:
            leg_metas = [l.meta() for l in legs]
            for c in cands:
                n_fam = len(family_members(leg_metas + [c.meta()]))
                if n_fam > fmax:
                    raise SystemExit(f"{c.name} in family {c.family!r} would make {n_fam} families; "
                                     f"the pre-registered cap is {fmax} (config search.families_max)")
    label = ("BATCH" if len(cands) > 1 else cands[0].name)
    return legs, cands, label


def materialise_live_snapshot(runtime, out_stream=None):
    """`--source api`: fetch the whole snapshot from the live API for THIS run.

    Nothing on disk is read. The run then constructs every factor from bytes
    that arrived over the wire in this invocation, and is stamped
    LIVE_DATA_SHA, the sha256 of those bytes' manifest, instead of inheriting
    DATA_SHA from the recorded materialisation.

    The cost is real and is the point: the bulk exports are large, so this is
    minutes-to-tens-of-minutes of download before a single month is evaluated.
    That is why it is not the default for a ratchet — a decision run must be
    reproducible and comparable to the 33 runs before it, and bytes that change
    under you are neither. Use it to answer "does this result survive on today's
    vendor data?", not to replace the frozen measurement.
    """
    import hashlib
    import tempfile

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import snapshot as S
    from data_layer import Snapshot

    echo = (lambda *a, **k: print(*a, **k)) if out_stream is None else print
    dest = Path(tempfile.mkdtemp(prefix="live_snapshot_"))
    echo(f"  --source api: fetching the snapshot from {runtime['data']['api_base']} into {dest}")
    dest, man = S.materialise_from_api(dest, echo=echo)
    digest = hashlib.sha256(
        "".join(f"{t}:{e['sha256']}" for t, e in sorted(man["tables"].items())).encode()
    ).hexdigest()[:12]
    snap = Snapshot(dest, {"tables": man["tables"]}, verify_hashes=False)
    return snap, digest, dest


def authorise_against_api(stamps, schema_only=False):
    """Require the LIVE API to vouch for the bytes before anything is measured.

    The goal on record is that factors construct from the Sharadar API and not
    merely from cached data. This is the gate that makes it true at RUN time
    rather than at maintenance time: before a single month is evaluated, the
    API is asked what it publishes, and the local materialisation must still be
    exactly that — every column, and all of its history. A run whose data the
    API does not vouch for does not start.

    The bytes stay content-addressed so DATA_SHA keeps meaning what it means
    and past runs stay comparable; what changes is that the API, not a
    directory, is the authority on whether those bytes may be used today.

    Returns LIVE_API_SHA, a hash of the authorisation, stamped on the run.
    """
    import hashlib
    import json as _json

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import snapshot as S

    try:
        rows, problems, absent = S.live_report(schema_only=schema_only)
    except Exception as e:
        raise SystemExit(
            f"live API authorisation could not run ({type(e).__name__}: {e}).\n"
            "  A decision run may not measure on data the API has not vouched for.\n"
            "  Fix the credential or connectivity, or pass --frozen to run on the\n"
            "  recorded materialisation alone (the run is stamped LIVE_API_SHA=frozen\n"
            "  and is NOT an API-authorised measurement)."
        )
    if problems:
        raise SystemExit(
            "live API authorisation FAILED — the materialisation is not what Sharadar now publishes:\n"
            + "\n".join(f"    !! {x}" for x in problems)
            + "\n  Refresh the snapshot (`snapshot.py download` / `verify` / `manifest`),\n"
              "  which moves DATA_SHA and is stop-and-ask item 3."
        )
    state = {t: {"cols": n, "history": h, "span": hd} for t, _a, n, _sn, _note, h, hd in rows}
    payload = _json.dumps({"data_sha": stamps["data_sha"], "tables": state}, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:12], len(rows), absent


def resolve_window(cfg, include_holdout=False, holdout_only=False):
    """The measured window. Decisions use [eval_start, eval_end]. The
    out-of-sample block [out_of_sample_start, out_of_sample_end] is FIXED in
    config (an end of "rolling" means the last completed month) and is
    measured only on the finished composite: --include-holdout appends it to
    the decision window, --holdout-only measures it alone."""
    d = cfg["dates"]
    oos_end = d.get("out_of_sample_end", "rolling")
    oos_end = last_completed_month_end() if str(oos_end).lower() == "rolling" else str(oos_end)
    if holdout_only:
        return d["out_of_sample_start"], oos_end
    if include_holdout:
        return d["eval_start"], oos_end
    return d["eval_start"], d["eval_end"]


def run(args, C=None, cfg=None, runtime=None, stamps=None, snap=None, root=ROOT, out_stream=None,
        layer_cfg=None, layer_cfg_path=None):
    holdout_only = bool(getattr(args, "holdout_only", False))
    if (args.include_holdout or holdout_only) and not args.baseline:
        raise SystemExit("--include-holdout / --holdout-only are for the FINAL baseline validation only. "
                         "The out-of-sample block is spent once, on the finished composite.")
    C = C or load_composite()
    cfg = cfg or load_config()
    runtime = runtime or load_runtime()
    stamps = stamps or all_stamps()
    if stamps["data_sha"] == "nodata":
        raise SystemExit("No snapshot recorded (DATA_SHA = nodata). See data/README.md.")
    live_snap_dir = None
    if getattr(args, "source", "recorded") == "api":
        snap, live_data_sha, live_snap_dir = materialise_live_snapshot(runtime, out_stream)
        stamps = dict(stamps)
        stamps["data_sha"] = f"live:{live_data_sha}"
        live_api_sha, n_auth, auth_absent = f"live:{live_data_sha}", 0, []
    elif getattr(args, "frozen", False):
        live_api_sha, n_auth, auth_absent = "frozen", 0, []
    else:
        live_api_sha, n_auth, auth_absent = authorise_against_api(
            stamps, schema_only=getattr(args, "schema_only", False))
    layer = bool(getattr(args, "construction_layer", False))
    if layer and holdout_only:
        raise SystemExit("--construction-layer refuses --holdout-only: its frames would start at the holdout "
                         "and the risk model would have no history (a flat book for 24 months). Spend the "
                         "holdout with --include-holdout; see CONSTRUCTION.md §8.")
    if layer and args.stage is not None:
        raise SystemExit("--construction-layer takes no --stage (it is its own run, stage E)")
    if not layer and args.stage is None:
        raise SystemExit("--stage is required (1, 2 or 3)")
    legs, cands, label = resolve_run(args, C, cfg)
    stage = LAYER_STAGE if layer else args.stage
    lcfg = layer_sha = None
    layer_info = {}
    if layer:
        lcfg = layer_cfg or CL.load_layer_config()
        layer_sha = CL.layer_sha(layer_cfg_path) if layer_cfg_path else CL.layer_sha()
        try:
            CL.check_composite(lcfg, stamps["composite_sha"])
            CL.row_specs(lcfg)
        except CL.LayerRefused as e:
            raise SystemExit(str(e))
        if str(lcfg["costs"]["half_spread"]) not in CL.SPREAD_COLUMNS:
            raise SystemExit(f"construction layer refused: unknown costs.half_spread "
                             f"{lcfg['costs']['half_spread']!r}")
    factors_needed = (legs + cands) if (stage in (2, 3) or args.baseline) else cands

    eval_start, eval_end = resolve_window(cfg, args.include_holdout, holdout_only)
    # The block's include_holdout flag says whether ANY out-of-sample month was
    # measured: --include-holdout and --holdout-only both set it (the predecessor
    # printed False under --holdout-only; HD-HOLDOUT-FLAG).
    oos_flag = bool(args.include_holdout or holdout_only)

    results_dir = root / runtime["results"]["dir"]
    results_dir.mkdir(parents=True, exist_ok=True)
    seq = next_seq(results_dir)
    stamp_day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_path = results_dir / f"{seq:03d}_{label}_stage{stage}_{stamp_day}.txt"
    if args.dry_run:
        out_path = None
    fh = open(out_path, "w", encoding="utf-8") if out_path else None
    real_stdout = sys.stdout
    sys.stdout = Tee(*(s for s in (real_stdout if out_stream is None else out_stream, fh) if s))
    run_start = time.time()
    blocks, summaries = [], []
    try:
        print("=" * 72)
        print(f"  {'DRY RUN (preflight only)' if args.dry_run else 'RUN'} {seq:03d}  {label}  stage {stage}")
        print(f"  runner {RUNNER_VERSION}  generated {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
        print(f"  HARNESS_SHA   {stamps['harness_sha']}")
        print(f"  CONFIG_SHA    {stamps['config_sha']}")
        print(f"  COMPOSITE_SHA {stamps['composite_sha']}   ({C.COMPOSITE_VERSION}: "
              f"{', '.join(f.name for f in legs)})")
        print(f"  FAMILIES      {_families_str([f.meta() for f in legs])}")
        print(f"  DATA_SHA      {stamps['data_sha']}")
        print(f"  UNIVERSE_SHA  {stamps['universe_sha']}")
        if layer:
            print(f"  LAYER_SHA     {layer_sha}   (config/construction_layer.yaml; informational, not a gate stamp)")
        if live_snap_dir is not None:
            print(f"  LIVE_API_SHA  {live_api_sha}  !! --source api: every byte fetched from the "
                  "live API for this run; NOT comparable to runs stamped on the recorded snapshot")
        elif live_api_sha == "frozen":
            print("  LIVE_API_SHA  frozen  !! --frozen: the API did NOT authorise these bytes for this run")
        else:
            print(f"  LIVE_API_SHA  {live_api_sha}  ({n_auth} tables vouched for by the live API at run start)")
        print(f"  Backtest window : {eval_start}  →  {eval_end}")
        if args.include_holdout or holdout_only:
            print("!! OUT-OF-SAMPLE " + ("ONLY" if holdout_only else "INCLUDED")
                  + " — this run MUST NOT inform an accept/reject decision.")
        dims = {f.col: f.dimension for f in factors_needed if f.dimension}
        if dims:
            print("\n!! PER-FACTOR SF1 DIMENSION OVERRIDES — these legs were NOT measured under")
            print(f"!! the project default {cfg['point_in_time']['sf1_dimension']}:")
            for c, d in sorted(dims.items()):
                print(f"!!   {c}: {d}")
        gates = {f.col: f.history_months for f in factors_needed if f.history_months is not None}
        if gates:
            print("\n** HISTORY GATES IN EFFECT — scored only for names with a trade near the")
            print("** window start: " + ", ".join(f"{c}: {n}m" for c, n in sorted(gates.items())))
        print("=" * 72)

        print("\nSTAGE 0 : Snapshot, panel, preflight")
        print("=" * 72)
        snap = snap or load_snapshot(runtime, root=root)
        panel = load_or_build_panel(snap, cfg, runtime, stamps["data_sha"], root=root)
        pidx = PanelIndex(panel, snap, cfg)
        pidx.set_market_loader(lambda: load_or_build_market(snap, cfg, runtime,
                                                            stamps["data_sha"], root=root))
        pidx.set_ff3_loader(lambda: load_or_build_ff3(snap, cfg, runtime,
                                                      stamps["data_sha"], root=root))
        pidx.set_ps_loader(lambda: load_or_build_ps(snap, cfg, runtime,
                                                    stamps["data_sha"], root=root))
        pidx.set_tailex_loader(lambda: load_or_build_tailex(snap, cfg, runtime,
                                                            stamps["data_sha"], root=root))
        pidx.set_trend_loader(lambda: load_or_build_trend(snap, cfg, runtime,
                                                          stamps["data_sha"], root=root))
        schedule = build_rebalance_schedule(eval_start, eval_end)
        print(f"    rebalances      : {len(schedule)} months")
        hard, warns, probes = run_preflight(snap, pidx, factors_needed, schedule, cfg)
        if hard:
            raise SystemExit(f"\nPREFLIGHT FAILED — {len(hard)} hard failure(s) above. Nothing ran.")
        probe_fields = probe_scalars(probes)
        if args.dry_run:
            print("\n  dry run complete — no backtest executed.")
            return []

        print("\nBuilding PIT universes + factor columns monthly")
        print("=" * 72)
        frames = precompute_month_frames(snap, pidx, factors_needed, schedule, cfg)
        print("\nScoring and reporting")
        print("=" * 72)
        if layer:
            spread = load_or_build_cs_spread(snap, runtime, stamps["data_sha"], root=root)
            blocks, summaries = drive_layer(frames, legs, cfg, stamps, eval_start, eval_end,
                                            oos_flag, holdout_only, C, lcfg, layer_sha,
                                            out_path.with_suffix(".paths.csv") if out_path else None,
                                            layer_info, spread=spread)
        elif args.baseline and stage == 3:
            blocks, summaries = drive_stage3(frames, legs, cfg, stamps, eval_start, eval_end,
                                             oos_flag, C)
        elif args.baseline:
            blocks, summaries = drive_baseline(frames, legs, cfg, stamps, eval_start, eval_end,
                                               oos_flag, probe_fields, C)
        elif stage == 1:
            blocks, summaries = drive_stage1(frames, cands, cfg, stamps, eval_start, eval_end,
                                             oos_flag, probe_fields)
        else:
            blocks, summaries = drive_stage2(frames, legs, cands, cfg, stamps, eval_start, eval_end,
                                             oos_flag, probe_fields, C)
        print("\n" + "=" * 72)
        print(f"  DONE — total runtime: {int((time.time() - run_start) // 60)}m "
              f"{int((time.time() - run_start) % 60)}s   ({len(blocks)} result block(s))")
        print("=" * 72 + "\n")
        for b in blocks:
            print(b); print()
        if out_path:
            print(f"Written to {out_path.relative_to(root)}")
        return blocks
    finally:
        sys.stdout = real_stdout
        if fh:
            fh.close()
        if out_path and out_path.exists():
            meta = {"seq": seq, "label": label, "stage": stage, "baseline": bool(args.baseline),
                    "include_holdout": bool(args.include_holdout or holdout_only), "holdout_only": holdout_only, "stamps": stamps,
                    "live_api_sha": live_api_sha, "live_api_tables": n_auth,
                    "api_authorised": live_api_sha != "frozen",
                    "factors": [f.name for f in cands], "composite_version": C.COMPOSITE_VERSION,
                    "composite_legs": [f.name for f in legs], "eval_start": eval_start,
                    "eval_end": eval_end, "runtime_seconds": round(time.time() - run_start, 1)}
            if layer:
                meta.update({"construction_layer": True, "layer_sha": layer_sha,
                             "paths_sha": layer_info.get("paths_sha"), "paths_file": layer_info.get("paths_file")})
            out_path.with_suffix(".meta.json").write_text(json.dumps(meta, indent=2))
            header = {"title": f"RUN {seq:03d} {label} stage {stage}", "composite":
                      f"{C.COMPOSITE_VERSION}: {', '.join(f.name for f in legs)}",
                      "eval_start": eval_start, "eval_end": eval_end,
                      "include_holdout": bool(args.include_holdout or holdout_only), "holdout_only": holdout_only, **stamps}
            if layer:
                header["layer_sha"] = layer_sha
            write_summary(out_path.with_name(out_path.stem + "_summary.md"), header, summaries)


def build_parser():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--factor")
    ap.add_argument("--factors")
    ap.add_argument("--baseline", action="store_true")
    ap.add_argument("--stage", type=int, choices=(1, 2, 3))
    ap.add_argument("--construction-layer", action="store_true",
                    help="with --baseline: the Phase E construction layer (docs/CONSTRUCTION.md, "
                         "config/construction_layer.yaml); takes no --stage")
    ap.add_argument("--include-holdout", action="store_true",
                    help="FINAL validation only: decision window plus the out-of-sample block")
    ap.add_argument("--holdout-only", action="store_true",
                    help="FINAL validation only: the out-of-sample block alone")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--source", choices=("recorded", "api"), default="recorded",
                    help="DEFAULT 'recorded': measure on the frozen snapshot this project downloaded "
                         "from the Sharadar API, after the live API authorises its schema and history "
                         "at run start; every run is then on the same bytes and DATA_SHA. 'api' "
                         "fetches the whole snapshot from the live API for this one run (slow, stamped "
                         "LIVE_DATA_SHA, NOT comparable to recorded runs).")
    ap.add_argument("--frozen", action="store_true",
                    help="skip live API authorisation and measure on the recorded materialisation alone")
    ap.add_argument("--schema-only", action="store_true",
                    help="authorise on columns only, skipping the history probe (faster)")
    return ap


def cli_preflight():
    ap = argparse.ArgumentParser()
    ap.add_argument("--factors"); ap.add_argument("--factor"); ap.add_argument("--baseline", action="store_true")
    a = ap.parse_args()
    ns = argparse.Namespace(factor=a.factor, factors=a.factors, baseline=a.baseline,
                            stage=2 if a.baseline else 1, include_holdout=False, dry_run=True)
    run(ns)


if __name__ == "__main__":
    run(build_parser().parse_args())
