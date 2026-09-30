"""
EntMult — enterprise multiple: (market cap + debt + convertible debt - cash and
short-term investments) divided by operating income before depreciation.

OSAP: EntMult, Loughran and Wellman 2011, Journal of Financial and Quantitative
Analysis (Table 3B). Predicted sign: - (a LOW multiple earns higher returns; long
the lowest EntMult, short the highest; SignalDoc Sign = -1).
Spec: osap_source/cache/b4e911e6/EntMult/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  M      = ctx.universe["mkt_cap_usd"]              (DAILY.marketcap at the month-end)
  debt   = SF1.debt (ART)                           (OSAP dltt + dlc)
  dc     = 0                                        (convertible debt; OSAP zero-fills it)
  che    = SF1.cashneq + SF1.investmentsc.fillna(0) (OSAP che)
  oibdp  = SF1.opinc + SF1.depamor (ART, TTM)       (NOT SF1.ebitda, which is bottom-up
           and carries non-operating items; a null depamor is NOT zero-filled to
           rescue the sum, the sum is NaN)
  EV     = M + debt + dc - che;   score = EV / oibdp.
  Raw ratio, no log, no winsorising (the harness ranks within sector).
  ascending=False: a HIGH raw multiple is unattractive, so the LOW multiple is the
  long leg, matching SignalDoc Sign = -1.

OSAP FILTERS REPRODUCED (predictor.py):
  - oibdp < 0 -> NaN (negative operating income dropped).
  - ceq < 0 -> NaN, here SF1.equity < 0. A missing equity does NOT exclude
    (in OSAP NaN < 0 is False), reproduced: no notna() requirement on equity.

GUARDS (every denominator; a negative one is a sign flip, not an outlier):
  - oibdp > 0 is required: OSAP drops oibdp < 0 and would carry +/-inf at exactly 0;
    here oibdp == 0 is NaN too (0 to 1 names per probe month).
  - M > 0, and EV = M + debt - che > 0: a non-positive EV (cash above cap plus debt)
    would flip the sign of the multiple, so it is NaN (not in OSAP, which keeps it).
    No positive floor: scoring is a within-sector percentile rank.
  - Non-finite results -> NaN.
  - fxusd != 1 -> NaN: the balance-sheet and flow inputs are in reporting currency
    (no *usd form for investmentsc/opinc) while M is USD.
  - debt gate: SF1.debt is populated for financials whose debtc/debtnc are null (the
    unclassified balance-sheet block, ~20% of rows), a different balance-sheet
    format, not a zero debt; names with debtc null are NaN (known trap
    unclassified_balance_sheet_block). The same gate keeps che from zero-filling
    investmentsc on that block. OSAP likewise does not zero-fill dltt/dlc.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? A firm with no new filing keeps
  debt, cash, dc and oibdp fixed but M moves with the price every month, so EntMult
  changes continuously: no stale-value default.
  The only exact-0 case is EV = 0 to the dollar, and EV <= 0 is NaN anyway; the
  oibdp == 0 case is NaN, not inf, and not a scored value.
  What share of the universe does nothing? The spec measured a modal share of any
  single value of 0.07-0.11% of the cross-section with 880-1,530 distinct values;
  preflight re-measures it.
  Tie handling: null (the guards above); no zero-fill of the ratio, no floored
  denominator. The risk is the right tail (tiny positive oibdp), which a rank
  absorbs.

DEVIATIONS FROM OSAP:
  - che: OSAP zero-fills che; here a null cashneq makes the score NaN (stricter;
    investmentsc is filled with 0 inside the debtc-gated block only).
  - oibdp for financials: the vendor records depamor as exactly 0 on ~8% of
    financial rows (field_map compustat.oibdp), so there oibdp = opinc.
  - EV <= 0 names (0-3 a month per the review; OSAP's cheapest) are NaN here.
  - dc (convertible debt): no SF1 field; OSAP zero-fills it, so 0 here for every
    firm. EV is understated for convertible issuers.
  - dltt + dlc -> SF1.debt (debtc + debtnc). INCLUDES operating-lease liabilities
    from FY2019 filings (ASC 842), overstating EV for lessees after adoption.
  - che -> cashneq + investmentsc.fillna(0): financing receivables of captive-finance
    names are included; NaN only where cashneq is NaN or the debtc gate removes the row.
  - oibdp -> opinc + depamor: top-down operating income plus cash-flow-statement D&A,
    approximates Compustat oibdp.
  - ceq -> SF1.equity, which includes preferred stock; it only feeds the sign filter.
  - Flow and balance sheet are the latest filed ART quarter (0-3 months old) vs OSAP
    annual items at datadate + 6 months (6-17 months old). M is the month-end value
    in both. ART, the project default; ARY would be the faithful annual flow.
  - mve_permco -> DAILY.marketcap (primary-class ticker, all-class shares), a
    few-percent difference on <= 2% of names.
  - oibdp == 0 -> NaN, EV > 0, M > 0, fxusd == 1 and the debtc gate are additions.
  - OSAP's annual June rebalance and any portfolio price filter are not reproduced
    (universe and rebalance belong to the harness).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    f = ctx.fundamentals(
        ["equity", "debt", "debtc", "cashneq", "investmentsc", "opinc", "depamor", "fxusd"]
    )
    equity = f["equity"].astype(float)
    debt = f["debt"].astype(float)
    che = f["cashneq"].astype(float) + f["investmentsc"].astype(float).fillna(0.0)
    oibdp = f["opinc"].astype(float) + f["depamor"].astype(float)   # null depamor -> NaN, not 0
    usd = f["fxusd"].astype(float) == 1.0

    mcap = ctx.universe["mkt_cap_usd"].astype(float).reindex(f.index)
    m = mcap.where(mcap > 0)

    ev = m + debt - che                # dc = 0 (OSAP zero-fill)
    ev = ev.where(ev > 0)              # EV <= 0 is a sign flip -> NaN
    den = oibdp.where(oibdp > 0)       # OSAP drops oibdp < 0; oibdp == 0 would be inf -> NaN

    mult = ev / den
    keep = usd & f["debtc"].notna() & ~(equity < 0)   # NaN equity does not exclude, as in OSAP
    out = mult.where(keep)
    return out.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="EntMult",
    col="f_entmult",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: a LOW multiple is attractive (the long leg)
    weight=1.0,
    inputs=(
        "SF1.debt", "SF1.debtc", "SF1.cashneq", "SF1.investmentsc", "SF1.opinc",
        "SF1.depamor", "SF1.equity", "SF1.fxusd", "DAILY.marketcap",
    ),
    osap_acronym="EntMult",
    source="Loughran and Wellman 2011 (Journal of Financial and Quantitative Analysis)",
    lookback_months=15,             # latest filing within max_fundamental_age_months
    notes="(M + debt + dc - che)/(opinc + depamor); dc=0; oibdp<=0, EV<=0, equity<0 -> NaN; fxusd==1; debtc gate",
    field_mappings=(
        ("crsp.mve_permco", "DAILY.marketcap via ctx.universe['mkt_cap_usd']",
         "company-level all-class cap at the primary ticker's price; few-% level error on <=2% of names"),
        ("compustat.dltt_plus_dlc", "SF1.debt (ART)",
         "includes operating leases from FY2019 (ASC 842); gated on SF1.debtc notna (unclassified balance-sheet block -> NaN)"),
        ("compustat.dc", "none -> 0",
         "convertible debt; OSAP zero-fills when blank, here 0 for every firm (convertible issuers' EV understated)"),
        ("compustat.che", "SF1.cashneq + SF1.investmentsc.fillna(0)",
         "approx: captive-finance receivables included; investmentsc zero-fill is safe only inside the debtc gate"),
        ("compustat.oibdp", "SF1.opinc + SF1.depamor (ART, TTM)",
         "approx: top-down operating income + cash-flow D&A, NOT SF1.ebitda; null depamor is not zero-filled, the sum is NaN"),
        ("compustat.ceq", "SF1.equity (ART)",
         "includes preferred stock; sign filter only, NaN equity does not exclude (as OSAP)"),
        ("compustat.curcd", "SF1.fxusd", "gate fxusd == 1 (reporting-currency inputs vs USD market cap)"),
        ("guard", "oibdp > 0, EV > 0, M > 0",
         "OSAP drops only oibdp < 0 and keeps inf at 0 and negative EV; here all NaN"),
    ),
)
