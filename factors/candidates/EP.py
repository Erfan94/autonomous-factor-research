"""
EP — earnings-to-price: annual income before extraordinary items divided by the
company's market value six months earlier; negative values are dropped.

OSAP: EP, Basu 1977, Journal of Finance (Table 1). Predicted sign: + (high EP
earns higher returns; long D10, short D1).
Spec: osap_source/cache/b4e911e6/EP/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  ib     = SF1.netinc + SF1.netincdis  (ART, latest filing known SIX MONTHS before
           the signal date: ctx.fundamentals(..., lag_months=6)). netincdis carries the OPPOSITE sign to the discontinued-operations
           income it describes (known trap sf1_netincdis_sign_inverted), so continuing
           income is netinc PLUS netincdis. netinccmn is NOT used (it is ibcom, after
           preferred dividends).
  ME_t-6 = SEP.close x SF1.sharesbas, both at the business month-end six months
           before the signal: price via ctx.at_month_end("SEP", ["close"], 6), share
           count via ctx.fundamentals_at_month_ends(["sharesbas"], [6]) (latest
           filing public at that month-end, as CompEquIss builds ME). sharesbas is
           split-restated to today's basis and SEP.close is on the same basis, so the
           product is consistent; it is never paired with closeunadj.
  EP     = ib / ME_t-6;  EP < 0 -> NaN (OSAP's predictor.py sets negative EP missing;
           ib == 0 gives EP = 0 and is kept).
  Raw ratio, no log, no winsorising. ascending=True: HIGH EP is attractive (the long
  leg), matching SignalDoc Sign = +1.

GUARDS (every denominator; a negative one is a sign flip, not an outlier):
  - ME_t-6 > 0 (close > 0 and sharesbas > 0 at the lag), else NaN.
  - EP < 0 -> NaN (construction, as OSAP). The scored cross-section therefore
    excludes loss makers; the lowest scored decile is the lowest POSITIVE EP.
  - fxusd != 1 -> NaN: the numerator is in the reporting currency over a USD cap
    (non-USD reporters are <=0.06% of members).
  - Non-finite results -> NaN. netincdis is not zero-filled: a null netincdis nulls ib.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? ib is fixed between filings, but the
  lagged market value is a per-month historical value that changes every month, so EP
  changes monthly; there is no stale-value default.
  The only exact-0 case is ib == 0 to the dollar: ~0.01% of non-null ART rows.
  What share of the universe does nothing? Well under 1% at any single value; not
  measured here (preflight measures it).
  Tie handling: null (loss makers, missing lag cap, non-USD -> NaN so blend_ranks
  renormalises). No zero-fill, no floor, no restriction. Coverage is the open question
  (losses are 30-45% of rows and the 1999-01/02 ART TTM is thin): preflight measures it.

DEVIATIONS FROM OSAP:
  - ib (Compustat, before preferred dividends and before extraordinary items and
    discontinued operations) -> netinc + netincdis: continuing income after
    non-controlling interest; Sharadar has no separate extraordinary-items line, so
    any extraordinary item stays in.
  - Timing: ART (trailing four quarters) from the latest filing known at t-6, so the
    t-6 price is at or after the earnings period end, as in OSAP (annual ib at
    datadate + 6 months, held 12 months; its t-6 price always falls after the fiscal
    year-end). Reading the fresh filing at t instead would pair earnings with a price
    set 1-5 months BEFORE the period ended (alpha_review batch08, medium). The
    earnings are therefore 6-21 months past period end here vs OSAP's 6-17; the
    ART update is quarterly, not annual. ART is a TTM sum (a level), no smear and
    no dimension override. Thin early ART (1998Q1-Q3 ~50%) shortens coverage until
    about 1999-09.
  - Lagged cap: SEP.close x SF1.sharesbas at the t-6 month-end, not CRSP
    mve_permco; shares step at filing dates; company-level all-class cap at the
    primary's price, few-% level error on <=2% of names. The t-6 price is read within
    7 calendar days of that month-end; history_months=6 gates names with no such
    price (OSAP's "row at t-6" requirement).
  - SignalDoc Filter exchcd == 1 (NYSE only) is portfolio-stage, not in predictor.py,
    and is not reproduced; nor is the annual June rebalance (harness).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    # ib as known at t-6, so the t-6 price is at or after its period end (OSAP: annual ib
    # public at datadate + 6m, price six months before t always after the fiscal year-end)
    f = ctx.fundamentals(["netinc", "netincdis", "fxusd"], lag_months=6)
    ib = f["netinc"].astype(float) + f["netincdis"].astype(float)   # netincdis sign inverted: PLUS
    usd = f["fxusd"].astype(float) == 1.0

    p6 = ctx.at_month_end("SEP", ["close"], 6)
    sh = ctx.fundamentals_at_month_ends(["sharesbas"], [6])
    if sh.empty:
        return pd.Series(np.nan, index=ctx.ids)
    sh6 = (sh.pivot_table(index="ID", columns="months_back", values="sharesbas", aggfunc="last")
           .get(6, pd.Series(dtype=float)).astype(float).reindex(ctx.ids))
    c6 = p6["close"].astype(float).reindex(ctx.ids)
    me6 = (c6 * sh6).where((c6 > 0) & (sh6 > 0))

    ep = ib.reindex(ctx.ids) / me6
    ep = ep.where(ep >= 0)              # OSAP: EP < 0 -> missing; EP == 0 kept
    ep = ep.where(usd.reindex(ctx.ids))
    return ep.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="EP",
    col="f_ep",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: high EP is attractive (the long leg)
    weight=1.0,
    inputs=("SF1.netinc", "SF1.netincdis", "SF1.sharesbas", "SF1.fxusd", "SEP.close"),
    osap_acronym="EP",
    source="Basu 1977 (Journal of Finance)",
    lookback_months=21,             # latest filing within 15 months of the t-6 month-end
    history_months=6,               # price read 6 months back (level read, gates a missing t-6 price)
    notes="(netinc + netincdis) / (SEP.close x sharesbas at t-6); EP < 0 -> NaN; fxusd==1; ART",
    field_mappings=(
        ("compustat.ib", "SF1.netinc + SF1.netincdis (ART)",
         "remap: the map's netinccmn is ibcom, not ib; netincdis sign inverted so PLUS; continuing income after NCI; extraordinary items not separable"),
        ("crsp.mve_permco at t-6", "SEP.close x SF1.sharesbas at the t-6 month-end",
         "company-level cap, share count steps at filing dates; sharesbas split-restated, paired with split-adjusted close, never closeunadj"),
        ("EP < 0 -> missing", "EP.where(EP >= 0)", "as OSAP predictor.py; loss makers unscored, ib == 0 kept"),
        ("compustat.curcd", "SF1.fxusd", "gate fxusd == 1"),
        ("timing", "ART latest filing (0-3 months old)", "vs annual ib at datadate + 6 months (6-17 months old)"),
        ("Filter exchcd==1", "not reproduced", "portfolio-stage NYSE-only filter; harness universe spans NYSE/NASDAQ/NYSEMKT"),
    ),
)
