"""
CashProd — market value of equity above book assets, per dollar of cash and
short-term investments (cash productivity); a high value is predicted to earn
LOWER returns, so the long leg is LOW CashProd.

OSAP: CashProd, Chandrashekar and Rao 2009, Working Paper (Table 4A). Predicted
sign: - (SignalDoc Sign = -1: high value, low return).
Spec: osap_source/cache/b4e911e6/CashProd/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  che = SF1.cashneq + SF1.investmentsc.fillna(0)     (ART level)
  CashProd = (mkt_cap_usd - assets) / che, from the latest filing known at the
  signal date and the month-end company market cap (ctx.universe["mkt_cap_usd"],
  DAILY.marketcap, raw USD). Raw ratio, no log, no scaling.
  Numerator MAY be negative (mve < assets): that is a real low value, kept.
  Guards: che <= 0 or null -> NaN (OSAP would produce +/-inf); assets <= 0 ->
  NaN; mkt_cap <= 0 -> NaN; non-finite -> NaN.
  Currency gate: assets, cashneq, investmentsc are in the reporting currency
  and mkt cap is USD, so names with SF1.fxusd != 1 are set NaN (not converted).
  Orientation: ascending=False (a LOW raw value is attractive; the harness
  negates so low raw = top decile = long leg).

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? None in particular: between
  filings assets and che are fixed while market cap moves daily, so the ratio
  changes continuously; there is no default value.
  What share of the universe sits at one value? ~0%. The only degenerate
  inputs are che == 0 (exact zero 0.17-1.06% of non-null), che null (0.04%)
  and mkt_cap == 0 (0.06%); all become NaN, not a tied value. Preflight to
  confirm the measured mode share.
  Tie handling: null (blend_ranks renormalises). Tiny-che names give extreme
  |CashProd|; rank transformation contains them.

DEVIATIONS FROM OSAP:
  - che: SF1.cashneq + investmentsc.fillna(0). Overshoots for vendor and
    captive-finance filers (financing receivables in investmentsc) and
    understates for the ~20% unclassified block (financials/REITs, che =
    cashneq). cashneq alone is never used.
  - OSAP zero-fills che and then gets +/-inf; here che null or <= 0 is NaN
    (~0.2-1% exact zero plus ~0.04% null of the universe). A missing che is
    NOT zero-filled.
  - mve_permco: DAILY.marketcap at month-end (primary close x all-class
    shares), via ctx.universe["mkt_cap_usd"], not SF1.marketcap (filing date).
    Level error of a few % on <= 2% of multi-class names.
  - timing: latest ART filing with datekey <= signal date (0-3 months old,
    capped at max_fundamental_age_months = 15) vs OSAP annual balance items at
    datadate + 6 months held 12 months (6-17 months old). The 6-month lag is
    not reproduced. Levels only, so ART equals ARQ.
  - Upstream annual-row filter (at, prcc_c, ni non-null) is not reproduced.
  - fxusd != 1 names nulled rather than converted.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    f = ctx.fundamentals(["assets", "cashneq", "investmentsc", "fxusd"])
    assets = f["assets"].astype(float)
    che = f["cashneq"].astype(float) + f["investmentsc"].astype(float).fillna(0.0)
    mcap = ctx.universe["mkt_cap_usd"].astype(float).reindex(f.index)

    num = mcap.where(mcap > 0) - assets.where(assets > 0)   # may be negative: kept
    out = num / che.where(che > 0)
    out = out.where(f["fxusd"].astype(float) == 1.0)         # USD cap vs reporting-currency SF1
    return out.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="CashProd",
    col="f_cashprod",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: LOW CashProd is attractive
    weight=1.0,
    inputs=("SF1.assets", "SF1.cashneq", "SF1.investmentsc", "SF1.fxusd", "DAILY.marketcap"),
    osap_acronym="CashProd",
    source="Chandrashekar and Rao 2009 (Working Paper)",
    lookback_months=15,             # latest filing within max_fundamental_age_months
    notes="(mkt_cap_usd - assets) / che; che <= 0 or null -> NaN (OSAP gives +/-inf); fxusd==1",
    field_mappings=(
        ("compustat.at", "SF1.assets (ART)",
         "latest filing (0-3 months old, capped at 15) vs OSAP annual + 6-month lag (6-17 months old); assets <= 0 -> NaN"),
        ("compustat.che", "SF1.cashneq + SF1.investmentsc.fillna(0) (ART)",
         "approx: overshoots for captive-finance filers; understates for the ~20% unclassified block (che = cashneq)"),
        ("compustat.che zero-fill", "none",
         "OSAP zero-fills che then gets +/-inf; here che null or <= 0 -> NaN (~0.2-1% of universe)"),
        ("crsp.mve_permco", "ctx.universe['mkt_cap_usd'] (DAILY.marketcap)",
         "primary close x all-class shares; other classes priced at the primary's price; a few % level error on <= 2% of names"),
        ("compustat.curcd", "SF1.fxusd",
         "names with fxusd != 1 nulled (USD cap vs reporting-currency SF1) rather than converted"),
    ),
)
