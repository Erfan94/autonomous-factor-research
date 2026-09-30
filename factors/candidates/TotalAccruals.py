"""
TotalAccruals — total accruals by the cash-flow method: net income not accounted
for by operating, investing and financing cash flow, net of net stock issuance and
dividends, scaled by the previous year's total assets; high accruals are predicted
to earn lower returns.

OSAP: TotalAccruals, Richardson, Sloan, Soliman and Tuna 2005, Journal of
Accounting and Economics (Table 8A TACC). Predicted sign: - (SignalDoc Sign = -1).
Spec: osap_source/cache/b4e911e6/TotalAccruals/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  OSAP (post-1989 cash-flow branch):
      (ni - (oancf + ivncf + fincf) + (sstk - prstkc - dv)) / at_lag12
  Sharadar, SF1 ART (trailing four quarters, as filed), one ctx.fundamentals_yoy call:
      ni            = netinc                      null -> NaN (OSAP: not zero-filled)
      oancf         = ncfo                        null -> NaN
      ivncf         = ncfi                        null -> NaN
      fincf         = ncff                        null -> NaN
      sstk - prstkc = ncfcommon (fillna(0))       NET common-equity flow, inflow-positive;
                                                  OSAP zero-fills both sstk and prstkc
      dv            = -min(ncfdiv, 0)             ncfdiv is outflow-NEGATIVE, so -dv = ncfdiv;
                                                  the 0.0-0.6% of rows with a positive ncfdiv are
                                                  clipped to 0. NOT zero-filled: OSAP leaves dv
                                                  missing after 1989 (dv is not in its
                                                  zero_fill_vars), so a null ncfdiv is NaN.
      numerator     = netinc - (ncfo + ncfi + ncff) + ncfcommon + min(ncfdiv, 0)
      at_lag12      = assets_lag: total assets at the fiscal period one year before the latest
                      filing, aligned by reportperiod (ctx.fundamentals_yoy), guarded > 0.
      score         = numerator / assets_lag
  Every numerator item is a TTM flow over the same window inside ONE ratio and there is no
  year-over-year difference of a flow, so nothing smears under ART; no dimension override.
  The only year-over-year read is on the balance-sheet level `assets`. ib is not used (OSAP
  uses ni), so netincdis is not added.
  Numerator identity: on Sharadar the numerator equals that of the reviewed
  factors/candidates/PctTotAcc.py (same -ncfcommon and -ncfdiv collapse). The two
  differ only in the denominator (|ni| there, lagged total assets here) and in the
  null rule for ncfdiv (filled 0 there, NaN here). The spec measured the Spearman
  correlation of the two scores at 0.871-0.898 on four months.
  Sign: SignalDoc Sign = -1 (high accruals earn low returns), so ascending=False.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? 0 / assets_lag = 0, but the
  cash-flow totals are essentially never all zero, so no value is a mode. Continuous
  ratio of flows.
  What share of the universe does nothing? Spec measurement on 276 months: modal
  value 0.041-0.112% of scored names (median 0.055%), distinct values equal the scored
  count (1,070-2,439), ten qcut bins in every month. ncfdiv == 0 is 38.9-44.7% of
  names in the four probe months, but it is one additive term, not the score.
  Tie handling: null. ncfdiv null -> NaN and assets_lag <= 0 -> NaN, so
  blend_ranks renormalises; average rank for the rest. |score| > 1 on median 0.72%
  of scored names (max 6.5%): rank (and the harness winsorisation), never z-score.

DEVIATIONS FROM OSAP:
  - Preferred flows: Compustat sstk/prstkc/dv include preferred issuance,
    redemption and dividends; Sharadar ncfcommon excludes preferred and ncfdiv is
    mostly common-only, so preferred flows stay un-netted inside ncff (material for
    financials in 2008-11, TARP).
  - Net-share-settlement tax and option-exercise flows sit inside ncfcommon.
  - ART (trailing four quarters, known at datekey) replaces the fiscal year at
    datadate + 6 months: the signal refreshes quarterly and is available 1-3 months
    after the period end, earlier than OSAP's stamp. assets_lag is the assets of
    the period one year before the latest filing (OSAP at_lag12: the preceding fiscal
    year's assets), reportperiod tolerance 45 days.
  - ncfdiv: positive rows clipped to 0; null -> NaN (OSAP dv unfilled); ncfcommon null -> 0.
  - netinc is after non-controlling interest; Compustat ni is after extraordinary items.
  - The pre-1990 balance-sheet branch (year <= 1989) is not built: the window starts 1999.
  - No sample restriction: financials and utilities stay in, as in OSAP.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    y = ctx.fundamentals_yoy(["netinc", "ncfo", "ncfi", "ncff", "ncfcommon", "ncfdiv", "assets"])
    ni = y["netinc"].astype(float)
    oancf = y["ncfo"].astype(float)
    ivncf = y["ncfi"].astype(float)
    fincf = y["ncff"].astype(float)
    # sstk - prstkc = ncfcommon; OSAP zero-fills both terms.
    net_issue = y["ncfcommon"].astype(float).fillna(0.0)
    # -dv = ncfdiv (outflow-negative); positive rows are the wrong sign -> 0; null stays NaN.
    neg_dv = y["ncfdiv"].astype(float).clip(upper=0.0)
    num = ni - (oancf + ivncf + fincf) + net_issue + neg_dv

    den = y["assets_lag"].astype(float)
    score = num / den.where(den > 0)
    return score.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="TotalAccruals",
    col="f_totalaccruals",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: HIGH accruals earn LOWER returns
    weight=1.0,
    inputs=("SF1.netinc", "SF1.ncfo", "SF1.ncfi", "SF1.ncff", "SF1.ncfcommon", "SF1.ncfdiv", "SF1.assets"),
    osap_acronym="TotalAccruals",
    source="Richardson, Sloan, Soliman and Tuna 2005 (Journal of Accounting and Economics)",
    lookback_months=27,             # latest filing (<=15m old) vs the same period ~12m before it
    notes="(ni - (ncfo+ncfi+ncff) + ncfcommon + min(ncfdiv,0)) / assets one year earlier, SF1 ART; ncfdiv null NaN",
    field_mappings=(
        ("compustat.ni", "SF1.netinc (ART)", "null -> NaN as OSAP; after NCI"),
        ("compustat.oancf / ivncf / fincf", "SF1.ncfo / ncfi / ncff (ART)",
         "null -> NaN as OSAP; preferred flows stay un-netted inside ncff"),
        ("compustat.sstk - compustat.prstkc", "SF1.ncfcommon (ART), null -> 0",
         "NET common-equity flow, preferred excluded; OSAP zero-fills both terms"),
        ("compustat.dv", "-min(SF1.ncfdiv, 0) (ART), null -> NaN",
         "outflow-negative sign flipped; positive rows clipped; mostly common-only; NOT zero-filled, as OSAP leaves dv missing"),
        ("compustat.at at lag 12 months", "SF1.assets_lag via fundamentals_yoy",
         "assets at the period one year before the latest filing, aligned by reportperiod (tol 45 days); guarded > 0"),
        ("year <= 1989 balance-sheet branch", "not built", "window starts 1999"),
        ("fiscal year at datadate + 6 months", "ART as of datekey", "TTM as filed, refreshed quarterly, available earlier"),
    ),
)
