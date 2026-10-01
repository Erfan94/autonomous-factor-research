"""
roaq — return on assets, quarterly: the latest quarter's income before extraordinary items
divided by the PREVIOUS quarter's total assets. High quarterly ROA is predicted to earn
HIGHER returns.

OSAP: roaq, Balakrishnan, Bartov and Faurel 2010, Journal of Accounting and Economics.
Predicted sign: + (SignalDoc Sign = +1).
Spec: osap_source/cache/b4e911e6/roaq/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  ibq_0    = SF1.netinc + SF1.netincdis of the latest filing known at the signal, read at
             dimension="ARQ" (a single-QUARTER flow; the harness default ART is a trailing
             four-quarter sum and would turn this into a TTM ROA). PLUS, not minus:
             SF1.netincdis carries the opposite sign to the discontinued-operations income
             it describes, so continuing-operations income is netinc + netincdis.
  assets_1 = SF1.assets (ARQ, a balance-sheet level) of the PREVIOUS report period, taken
             from ctx.fundamentals_history(["netinc","netincdis","assets"], 2, "ARQ").
             The previous quarter is the history row whose reportperiod lies 2..4 months
             before the latest reportperiod; a missing intermediate quarter gives NaN (as
             OSAP's panel row at t-3 would be absent), never a silently older quarter.
  roaq     = ibq_0 / assets_1, assets_1 > 0 else NaN.
  Raw ratio; no winsorising, no industry adjustment, no price. ascending=True: HIGH
  quarterly ROA is the long leg.

GUARDS:
  - assets_1 > 0 (exact-zero assets are data errors on a few hundredths of a percent).
  - Staleness: the latest ARQ filing must be at most 110 days old at the signal (mirrors
    OSAP's three-month availability plateau, as in EarningsSurprise); older -> NaN.
  - Neither ibq nor atq is zero-filled in OSAP and neither is here; a null netinc, netincdis
    or assets is a NaN (OSAP drops the row on a missing roaq).

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? ibq = 0, hence roaq = exactly 0.0.
  What share of the universe does nothing? Well under 1%: the spec measured, on every one
  of the 276 decision months, a modal exact value holding at most 0.17% of scored names
  (mean 0.06%), exact zeros on at most 3 names per month (mean 0.6), and at least 1,722
  distinct values per month. Names that do not file are NaN (stale), not a value. Preflight
  re-measures it.
  Tie handling: null (missing inputs, a stale filing, a missing intermediate quarter or a
  non-positive assets_1 -> NaN, so blend_ranks renormalises). No zero-fill, no floor, no
  sample restriction.

DEVIATIONS FROM OSAP:
  - ibq (Compustat income before extraordinary items, quarterly) -> SF1.netinc + SF1.netincdis
    at ARQ: netinc is after non-controlling interest (Compustat ib is before the NCI split)
    and extraordinary items are not separable, so the numerator is income after NCI and
    before discontinued operations only.
  - Timing: OSAP availability is datadate + 3 months or the rdq month if later, each quarter
    held three monthly rows; here the SF1 filing date (datekey) governs, with a 110-day
    latest-filing gate in place of the harness's 15-month staleness tolerance.
  - Restatements: OSAP's Compustat quarter is overwritten on restatement; SF1 ARQ keeps the
    as-reported row known at the signal.
  - Previous assets are located by reportperiod (2..4 month gap), not by the panel's
    month-3 row.
  - SignalDoc Filter abs(prc)>1 is portfolio-stage and not reproduced (universe: price >= $1).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef

_MAX_FILING_AGE_DAYS = 110
_GAP_MONTHS = (2, 4)            # previous-quarter reportperiod lies 2..4 months before the latest


def _compute(ctx):
    h = ctx.fundamentals_history(["netinc", "netincdis", "assets"], 2, dimension="ARQ")
    if h.empty:
        return pd.Series(dtype=float)
    h = h.copy()
    h["ID"] = h["ID"].astype(str)

    latest = h[h["q_back"] == 0].set_index("ID")
    fresh = latest["datekey"] >= (ctx.signal_asof - pd.Timedelta(days=_MAX_FILING_AGE_DAYS))
    latest = latest[fresh]
    if latest.empty:
        return pd.Series(dtype=float)

    # previous quarter: the history row 2..4 months before the latest reportperiod
    prev = h[(h["q_back"] >= 1) & h["ID"].isin(latest.index)].copy()
    rp0 = pd.to_datetime(prev["ID"].map(latest["reportperiod"]))
    rp = pd.to_datetime(prev["reportperiod"])
    gap = (rp0.dt.year - rp.dt.year) * 12 + (rp0.dt.month - rp.dt.month)
    prev = prev[(gap >= _GAP_MONTHS[0]) & (gap <= _GAP_MONTHS[1])]
    prev = prev.sort_values(["ID", "q_back"], kind="mergesort").drop_duplicates("ID", keep="first")
    assets_1 = prev.set_index("ID")["assets"].astype(float)

    ib0 = latest["netinc"].astype(float) + latest["netincdis"].astype(float)   # PLUS: netincdis sign is inverted
    den = assets_1.reindex(ib0.index)
    out = ib0 / den.where(den > 0)
    out = out.replace([np.inf, -np.inf], np.nan)

    out.index = out.index.astype(str)
    return out.reindex(ctx.ids.astype(str)).set_axis(ctx.ids)


FACTOR = FactorDef(
    family="profitability",                # Phase C, 2026-10-01: Cat.Economic "profitability" (decision phase_c_family_partition)
    name="roaq",
    col="f_roaq",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: HIGH quarterly ROA is attractive (the long leg)
    weight=1.0,
    dimension="ARQ",                # ibq is a single-quarter flow; ART would be a TTM sum (a different signal)
    inputs=("SF1.netinc", "SF1.netincdis", "SF1.assets"),
    osap_acronym="roaq",
    source="Balakrishnan, Bartov and Faurel 2010 (Journal of Accounting and Economics)",
    lookback_months=10,             # 110-day gate + period-end-to-filing gap, plus the prior quarter's row
    notes="(netinc + netincdis) ARQ latest quarter / previous-quarter assets by reportperiod (2..4 month gap); OVERRIDE: latest ARQ filing <= 110 days old (in place of max_fundamental_age_months 15), as EarningsSurprise; assets_1 > 0",
    field_mappings=(
        ("compustat.ibq", "SF1.netinc + SF1.netincdis (dimension ARQ)",
         "netincdis sign inverted so PLUS; netinc is after NCI and extraordinary items are not separable; single-quarter flow, never ART"),
        ("compustat.atq", "SF1.assets (dimension ARQ)",
         "level; previous report period located by reportperiod 2..4 months before the latest, not by the panel's month-3 row"),
        ("3-month availability plateau (time_avail_m)", "SF1 datekey with latest filing <= 110 days old",
         "replaces OSAP's datadate+3 / rdq month rule and the harness 15-month staleness tolerance"),
        ("Filter abs(prc)>1", "not reproduced", "portfolio-stage, not in predictor.py; harness universe is price >= $1"),
    ),
)
