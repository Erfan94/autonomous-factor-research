#!/usr/bin/env python3
"""
Preflight: everything that can be known about a factor BEFORE a backtest.

    python3 harness/preflight.py --factors A,B,C        # candidates
    python3 harness/preflight.py --baseline             # the composite's legs

The BQuant project learned each of these checks from a run that had already
cost 100+ minutes: a field that did not exist (a 15-hour run that collected
nothing), a request shape the data layer would not route, a mass point that
collapsed the deciles, coverage under the bar, a lookback longer than the
history. With
the data on disk every one of them is a few seconds against real months, so
they run here, before the loop, and the run refuses to start on a hard fail.

Three probe months — first, middle, last of the schedule — because a mass
point that is 3% in 2005 can be 19% in 1999 (fewer filers break out the item)
and the cliff is at ~10%: `pd.qcut(q=10, duplicates="drop")` returns fewer than
ten bins once a tie block spans a decile boundary.
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from harness import analytics as A                      # noqa: E402
from harness.data_layer import MonthContext, build_universe  # noqa: E402

MASSPOINT_HARD_PCT = 10.0    # the decile cliff
MASSPOINT_WARN_PCT = 5.0
COVERAGE_WARN_PCT = 40.0     # the Stage 1 bar; below it a screen is a coin flip


def check_inputs(snap, factors):
    """Every declared TABLE.field must exist in the snapshot's on-disk schema."""
    problems = []
    for f in factors:
        for p in f.validate():
            problems.append(p)
        for inp in f.inputs:
            table, field = inp.split(".", 1)
            if not snap.has(table):
                problems.append(f"{f.name}: input {inp} — table {table} is not in the snapshot")
                continue
            if field not in snap.columns(table):
                problems.append(f"{f.name}: input {inp} — {table} has no column {field!r}")
    cols = [f.col for f in factors]
    for c in set(cols):
        if cols.count(c) > 1:
            problems.append(f"column {c!r} is declared by more than one factor")
    return problems


ROOT = Path(__file__).resolve().parent.parent


def check_orientation(factors, cfg):
    """A factor's `ascending` must match SignalDoc's published Sign for its
    osap_acronym: +1 -> ascending=True (high value in D10), -1 -> False.
    A mismatch is a HARD fail unless the factor is a declared second
    hypothesis (name ending in "Flip", which carries the |t| >= 2.74 bar and
    caveat). Added after orientation errors reached preflight (an
    alpha-reviewer finding)."""
    src = cfg.get("osap_source", {})
    doc = ROOT / "osap_source" / "cache" / str(src.get("ref", ""))[:8] / src.get("signal_doc_path", "SignalDoc.csv")
    if not doc.exists():
        return [], [f"orientation check skipped: {doc} not found"]
    sd = pd.read_csv(doc, usecols=["Acronym", "Sign"]).dropna(subset=["Sign"])
    sign = dict(zip(sd["Acronym"].astype(str), sd["Sign"].astype(float)))
    hard, warns = [], []
    for f in factors:
        acr = getattr(f, "osap_acronym", None)
        if acr not in sign:
            warns.append(f"{f.name}: osap_acronym {acr!r} not in SignalDoc; orientation unchecked")
            continue
        want = sign[acr] > 0
        if bool(f.ascending) != want and not f.name.endswith("Flip"):
            hard.append(f"{f.name}: ascending={f.ascending} contradicts SignalDoc Sign {sign[acr]:+.0f} "
                        f"for {acr} (a flipped screen must be a declared '*Flip' second hypothesis)")
    return hard, warns


def probe_months(schedule, n=3):
    if len(schedule) <= n:
        return list(schedule)
    idx = [0, len(schedule) // 2, len(schedule) - 1]
    return [schedule[i] for i in idx]


def masspoint_stats(s):
    """Share of the non-null cross-section sitting on the single most common
    value, and how many bins qcut would actually produce."""
    x = pd.to_numeric(s, errors="coerce").dropna()
    if len(x) == 0:
        return {"n": 0, "mode": None, "mode_pct": float("nan"), "n_distinct": 0, "qcut_bins": 0}
    # Exact equality, as qcut ties: rounding to 12 DECIMALS merged distinct
    # values of a factor on a ~1e-10 scale into false ties (HD-PF-ROUND).
    vc = x.value_counts()
    try:
        bins = pd.qcut(x.rank(pct=True, method="average"), 10, duplicates="drop")
        nb = int(bins.cat.categories.size)
    except Exception:
        nb = 0
    return {"n": int(len(x)), "mode": float(vc.index[0]), "mode_pct": float(100.0 * vc.iloc[0] / len(x)),
            "n_distinct": int(len(vc)), "qcut_bins": nb}


def run_preflight(snap, pidx, factors, schedule, cfg, log=print):
    """Returns (hard_failures, warnings, per_factor_probe) and prints a table."""
    hard = check_inputs(snap, factors)
    o_hard, o_warn = check_orientation(factors, cfg)
    hard += o_hard
    warns = list(o_warn)
    probes = {f.name: [] for f in factors}
    if hard:
        for h in hard:
            log(f"  !! {h}")
        return hard, warns, probes

    # Data-start check: the snapshot must reach back far enough for the
    # longest lookback at the FIRST rebalance.
    first_signal = schedule[0][1]
    data_start = pidx.months[0]
    for f in factors:
        need = (first_signal - pd.DateOffset(months=int(f.lookback_months))).normalize()
        if f.lookback_months and need < data_start:
            warns.append(f"{f.name}: lookback {f.lookback_months}m reaches {need.date()} but the "
                         f"panel starts {data_start.date()} — early months will be null, and "
                         "coverage will read low in the first years for a data reason.")

    sf1_cache = {}
    log(f"\n  Preflight on {len(probe_months(schedule))} probe months "
        f"(mass-point cliff {MASSPOINT_HARD_PCT:.0f}%, coverage bar {COVERAGE_WARN_PCT:.0f}%)")
    log(f"  {'factor':<24}{'signal':>12}{'univ':>7}{'cover%':>8}{'mode':>14}{'mode%':>7}"
        f"{'distinct':>9}{'qcut':>5}")
    for (reb, sig, rs, re_) in probe_months(schedule):
        univ = build_universe(pidx, sig, cfg)
        if univ.empty:
            warns.append(f"probe {sig.date()}: EMPTY universe")
            continue
        ctx = MonthContext(snap, pidx, univ, sig, cfg, sf1_cache)
        for f in factors:
            try:
                s = pd.to_numeric(pd.Series(f.compute(ctx)).reindex(univ.index), errors="coerce")
                if f.history_months is not None:
                    s = s.where(ctx.has_price_at(f.history_months))
            except Exception as e:                       # a factor that raises is a hard fail
                hard.append(f"{f.name}: compute raised on {sig.date()}: {type(e).__name__}: {e}")
                continue
            cov = 100.0 * s.notna().mean()
            ms = masspoint_stats(s)
            ms.update(signal=str(sig.date()), n_univ=int(len(univ)), coverage_pct=cov)
            probes[f.name].append(ms)
            mode = "" if ms["mode"] is None else f"{ms['mode']:.6g}"
            log(f"  {f.name:<24}{str(sig.date()):>12}{len(univ):>7}{cov:>8.1f}{mode:>14}"
                f"{ms['mode_pct']:>7.1f}{ms['n_distinct']:>9}{ms['qcut_bins']:>5}")
            # A cross-section below the harness's ranking floor is never ranked, so
            # its "mass point" is a sample-size artefact (one firm with a 60-month
            # history in 1998 reads as 100% at one value). Coverage reports it.
            if ms["n"] >= A.MIN_OBS_RANK and (ms["mode_pct"] >= MASSPOINT_HARD_PCT or ms["qcut_bins"] < 10):
                hard.append(f"{f.name} @ {sig.date()}: MASS POINT — {ms['mode_pct']:.1f}% of the "
                            f"cross-section at {ms['mode']!r}, qcut yields {ms['qcut_bins']} bins. "
                            "Design the tie handling (remove / null / floor) before running.")
            elif ms["n"] >= A.MIN_OBS_RANK and ms["mode_pct"] >= MASSPOINT_WARN_PCT:
                warns.append(f"{f.name} @ {sig.date()}: {ms['mode_pct']:.1f}% at {ms['mode']!r} — "
                             "below the cliff but watch the middle deciles.")
            if cov < COVERAGE_WARN_PCT:
                warns.append(f"{f.name} @ {sig.date()}: coverage {cov:.1f}% < {COVERAGE_WARN_PCT:.0f}% "
                             "Stage 1 bar.")
    log("")
    for w in warns:
        log(f"  ** {w}")
    for h in hard:
        log(f"  !! {h}")
    return hard, warns, probes


def probe_scalars(probes):
    """Flatten for the result block: worst mass-point share and lowest qcut
    bin count across probe months, per factor."""
    out = {}
    for name, rows in probes.items():
        if not rows:
            continue
        out[name] = {
            "preflight_masspoint_max_pct": max(r["mode_pct"] for r in rows if r["n"]) if any(r["n"] for r in rows) else float("nan"),
            "preflight_qcut_min_bins": min(r["qcut_bins"] for r in rows),
            "preflight_coverage_min_pct": min(r["coverage_pct"] for r in rows),
        }
    return out


if __name__ == "__main__":
    from harness.run_test import cli_preflight
    cli_preflight()
