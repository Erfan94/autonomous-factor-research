"""
Leverage — market leverage: total liabilities divided by the market value of
equity. High market leverage is predicted to earn high returns.

OSAP: Leverage (Acronym2 Leverage), Bhandari 1988, Journal of Finance (Table 1
DER). Predicted sign: + (SignalDoc Sign = +1: long HIGH).
Spec: osap_source/cache/b4e911e6/Leverage/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  score = SF1.liabilities / ctx.universe["mkt_cap_usd"]
  liabilities: ART, the latest filing with datekey <= the signal date (a level,
  so ART equals ARQ at the same reportperiod; no dimension override).
  mkt_cap_usd: DAILY.marketcap at the month-end (company-level), as EBM reads it.
  Raw ratio, no log, no winsorising. ascending=True: a HIGH ratio is the long
  leg, matching SignalDoc Sign = +1.

GUARDS (every denominator; a negative one is a sign flip, not an outlier):
  - mkt_cap_usd > 0.
  - fxusd == 1 gate: liabilities is in REPORTING currency and mkt_cap_usd is USD;
    non-USD reporters are <= 0.06% of members and are NaN (OSAP keeps curcd = USD
    rows only, which the gate matches).
  - liabilities >= 0: a zero is kept (OSAP keeps lt = 0, exact 0.0); a negative
    liabilities level (mean 0.03% of names, max 0.29% in a month) is a data
    defect, not a real value, and would rank below every firm with no debt; it is
    nulled (OSAP keeps it).
  - Non-finite results -> NaN.

OVERLAP (measured in the spec, Spearman per month on the harness universe,
averaged over 276 months): rho(Leverage, SF1 assets / mkt_cap_usd) mean 0.947
(range 0.92 .. 0.97); rho(Leverage, SF1 equity / mkt_cap_usd) mean 0.563 (range
0.44 .. 0.76), the raw equity-to-market ratio, not the v0 Value leg's book equity.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? A continuous ratio: the book
  side is fixed between filings but the market cap moves with price every month,
  so there is no stale-value default. The only exact value is liabilities = 0,
  which gives exactly 0.0.
  What share of the universe does nothing? The spec measured a modal share of the
  scored cross-section max 0.10%, mean 0.05%, distinct values equal to n scored,
  no qcut(10) collapse; exact-zero or negative liabilities mean 0.03%, max
  0.29%. Preflight to confirm.
  Tie handling: null (the guards above); nothing removed or floored; harness
  average rank.

DEVIATIONS FROM OSAP:
  - Timing: latest ART filing (mean age about 50 days) instead of OSAP's annual
    lt at datadate + 6 months (6-17 months old); the 6-month lag is not reproduced.
  - crsp.mve_permco -> DAILY.marketcap via mkt_cap_usd (other listed classes priced
    at the primary's price, unlisted classes included; <= 2% of names).
  - fxusd == 1 gate and the negative-liabilities null are additions.
  - OSAP's SignalMasterTable filter (shrcd 10/11/12, exchcd 1/2/3) is replaced by
    the harness universe.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    f = ctx.fundamentals(["liabilities", "fxusd"])
    lt = f["liabilities"].astype(float)
    usd = f["fxusd"].astype(float) == 1.0

    mcap = ctx.universe["mkt_cap_usd"].astype(float).reindex(f.index)
    m = mcap.where(mcap > 0)

    out = lt.where(lt >= 0) / m
    out = out.where(usd)
    return out.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="Leverage",
    col="f_leverage",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: high market leverage -> high return; long HIGH
    weight=1.0,
    inputs=("SF1.liabilities", "SF1.fxusd", "DAILY.marketcap"),
    osap_acronym="Leverage",
    source="Bhandari 1988 (Journal of Finance)",
    lookback_months=15,             # latest filing within max_fundamental_age_months
    notes="liabilities (ART) / mkt_cap_usd; fxusd==1 gate; mkt_cap > 0; negative liabilities nulled",
    field_mappings=(
        ("compustat.lt", "SF1.liabilities (ART)",
         "latest filing, not annual + 6-month lag; negative level nulled (OSAP keeps, 0.03% of names); lt = 0 kept"),
        ("crsp.mve_permco", "DAILY.marketcap via ctx.universe['mkt_cap_usd']",
         "company-level all-class cap at the primary ticker's price; few-% level error on <=2% of names"),
        ("compustat.curcd", "SF1.fxusd", "gate fxusd == 1 (liabilities has no USD variant; mkt_cap_usd is USD)"),
    ),
)
