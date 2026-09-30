"""
DelNetFin — 12-month change in net financial assets (short-term investments
plus long-term investments and advances, minus debt) over average total
assets; firms that build net financial assets are predicted to earn more.

OSAP: DelNetFin (Acronym2 DelNetFin), Richardson, Sloan, Soliman & Tuna 2005,
Journal of Accounting and Economics. Predicted sign: + (SignalDoc Sign = +1,
ascending=True).
Spec: osap_source/cache/b4e911e6/DelNetFin/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  y = ctx.fundamentals_yoy(["investmentsc","investmentsnc","debt","assets"])
  (ART default; latest filing known at the signal and the same fiscal period
  one year earlier, aligned by reportperiod). All four are balance-sheet
  levels (ART equals ARQ on the same reportperiod): no flow, no TTM smear, no
  dimension override.
    nf     = investmentsc + investmentsnc - debt        (debt = dltt + dlc)
    avgAT  = 0.5 * (assets + assets_lag), guarded > 0
    DelNetFin = (nf - nf_lag) / avgAT
  Any null leg in either period -> NaN; missing year-ago filing -> NaN.
  The pstk term is dropped (see DEVIATIONS). The che term is NOT used: the
  OSAP predictor reads ivst and ivao, not che.
  No zero-fill on investmentsc / investmentsnc: OSAP zero-fills ivst and ivao,
  but on SF1 both are null only on the unclassified-balance-sheet block (71%
  financials, 20% real estate; 100% coincident with assetsc null), a
  different balance-sheet format and not a real zero, so those names stay NaN
  (~20% structural gap).
  Ratio of same-currency levels: no fxusd gate is needed.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0.0 (none of the four
  levels changed, in practice a stale or identical filing pair).
  What share of the universe does nothing? Spec measured 0.6-2.2% exact-zero
  of scored names by month (no decile collapse); preflight measures the
  modal-value share on the harness universe.
  Tie handling: none needed beyond the NaN rules above (null via the
  unclassified block, assets guard); the harness averages ranks over residual
  ties, below the 5% warn line.

DEVIATIONS FROM OSAP:
  - pstk: no SF1 field. OSAP itself does pstk.fillna(0) (tempPSTK), so the term
    is dropped (approx): firms with preferred stock get net financial assets
    overstated by pstk and a change that omits preferred issuance / retirement.
  - ivst -> investmentsc: also carries current financing / loan receivables of
    captive-finance filers (e.g. CSCO, F, GM, IBM, HPE, HOG): overstated there.
  - ivao -> investmentsnc: includes equity-method investments.
  - dltt + dlc -> SF1.debt: total debt INCLUDES operating-lease obligations from
    ASC 842 adoption (FY2019 filings, FY2018 for early adopters). Lessees show
    a one-off negative step in the 12-month change in the 2019-2020 signal
    months (about 24-36 decision months), a lessee-vs-non-lessee artefact, not
    a financing decision. No lease-free field exists in SF1. Declared, not
    corrected.
  - ~20% of names (unclassified balance sheets) are NaN where OSAP's zero-fill
    of ivst / ivao would still score them.
  - Timing: OSAP reads the fiscal year available at datadate + 6 months,
    refreshed annually; here the latest filed ART level against the same
    period a year earlier (rolling four-quarter change, refreshed quarterly),
    no 6-month lag. The 1999-01 month is thin (year-ago assets ~50% available
    at the snapshot start).
  - avgAT > 0 guard (OSAP has none).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    y = ctx.fundamentals_yoy(["investmentsc", "investmentsnc", "debt", "debtc", "assets"])

    def nf(sfx):
        # No fill: any null leg propagates to NaN (null block = unclassified format).
        return (y["investmentsc" + sfx].astype(float)
                + y["investmentsnc" + sfx].astype(float)
                - y["debt" + sfx].astype(float))

    at = y["assets"].astype(float)
    at_lag = y["assets_lag"].astype(float)
    den = 0.5 * (at + at_lag)
    score = (nf("") - nf("_lag")) / den.where(den > 0)
    score = score.where(y["reportperiod"].notna() & y["reportperiod_lag"].notna())
    score = score.where(y["debtc"].notna() & y["debtc_lag"].notna())   # debt gate ruling, explicit
    return score.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="DelNetFin",
    col="f_delnetfin",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: HIGH change in net financial assets is attractive
    weight=1.0,
    inputs=("SF1.investmentsc", "SF1.investmentsnc", "SF1.debt", "SF1.debtc", "SF1.assets"),
    osap_acronym="DelNetFin",
    source="Richardson, Sloan, Soliman & Tuna 2005 (Journal of Accounting and Economics)",
    lookback_months=31,             # latest filing up to 15 months old + year-ago period 12 months earlier + ~4m report-period-to-filing lag
    notes=("12m change in (investmentsc + investmentsnc - debt) / avg assets; ART yoy by reportperiod; "
           "unclassified names NaN (no zero-fill); pstk dropped"),
    field_mappings=(
        ("compustat.ivst", "SF1.investmentsc (ART)",
         "APPROX: includes financing receivables of captive-finance filers; null (unclassified block) stays NaN, OSAP zero-fills"),
        ("compustat.ivao", "SF1.investmentsnc (ART)",
         "APPROX: includes equity-method investments; null (unclassified block) stays NaN, OSAP zero-fills"),
        ("compustat.dltt + compustat.dlc", "SF1.debt (ART)",
         "total debt = dltt + dlc; includes operating-lease obligations from ASC 842 (FY2019), one-off step in 2019-2020 signal months"),
        ("compustat.pstk", "none",
         "no SF1 field; OSAP itself zero-fills pstk (tempPSTK); term dropped (approx)"),
        ("compustat.at", "SF1.assets (ART)", "avg of latest and year-ago, guarded > 0"),
        ("*_lag12", "*_lag via ctx.fundamentals_yoy",
         "year-ago levels by reportperiod (45-day tolerance), not a 12-month calendar lag; missing/stale -> NaN"),
        ("datadate + 6 months availability", "latest ART filing with datekey <= signal",
         "rolling quarterly refresh, four-quarter span; OSAP's 6-month lag and annual step not reproduced"),
    ),
)
