"""
SP — sales to price: trailing revenue over market capitalisation, a revenue-based
valuation ratio.

OSAP: SP, Barbee, Mukherji and Raines 1996, Financial Analysts Journal (Table 2,
model 1; Acronym2 Rev2Price). Predicted sign: + (high sales-to-price earns higher
returns; long D10, short D1).
Spec: osap_source/cache/b4e911e6/SP/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  sale = SF1.revenue (ART, trailing-twelve-month, latest filing known at the signal)
  M    = ctx.universe["mkt_cap_usd"]   (DAILY.marketcap at the signal month-end)
  score = revenue / M.where(M > 0), nulled where fxusd != 1.
  Raw ratio, no log, no winsorising. ascending=True (SignalDoc Sign = +1).

GUARDS (every denominator; a negative one is a sign flip, not an outlier):
  - M > 0 (the only denominator).
  - fxusd == 1: revenue is in reporting currency over a USD market cap, so non-USD
    reporters are NaN (0.03% of names, max 0.06%).
  - revenue <= 0 is NOT guarded, as in OSAP: sale == 0 gives SP = 0 and a negative
    revenue is scored as is (the numerator is not a denominator).
  - Non-finite results -> NaN.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? SP has no structural constant and
  moves with price every month. The only point mass is revenue == 0 (pre-revenue
  names), which gives exactly 0.0.
  What share of the universe does nothing? Spec measurement on 92 of 276 decision
  months: modal value 0.0 in 89 of 92 months; modal share 0.56% mean, max 3.77%
  (2021-03-31, SPAC-era zero-revenue shells), 1.8-2.3% in 2020-09..2021-09; 10 qcut
  bins. revenue <= 0 among revenue-non-null names: 0.7% mean (max 4.2%). Preflight
  measures it again.
  Tie handling: none. OSAP has no tie rule, the mass is far below the 10% cliff, and
  zero revenue is a real observation rather than a missing one (average rank).

OVERLAP WITH THE v0 COMPOSITE (factual):
  The Value leg is equity.where(equity > 0) / mkt_cap_usd (ART). SP has the SAME
  denominator (universe mkt_cap_usd); the numerators differ (revenue versus book
  equity). Spec-measured Spearman of raw SP with the raw Value leg: mean 0.40
  (range 0.24-0.74, 92 months).

DEVIATIONS FROM OSAP:
  - sale: fiscal-year annual `sale` available datadate + 6 months, held 12 months ->
    SF1.revenue ART (TTM as of the latest filing; no extra 6-month lag). ARQ would
    put one quarter of revenue over a full market value, so ART is kept.
  - mve_permco -> ctx.universe["mkt_cap_usd"] (DAILY.marketcap at the month-end;
    company-level on the primary ticker's price, no class sum). The market value is
    contemporaneous at the signal date, as in OSAP's month-t mve_permco.
  - fxusd == 1 gate is an addition (OSAP: curcd reasoning, no explicit gate).
  - OSAP's annual-row requirement (at, prcc_c, ni non-missing) is not reproduced.
  - Coverage: SF1 revenue is ~57% populated at the first decision month and >= 85%
    from 1999-03.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    f = ctx.fundamentals(["revenue", "fxusd"])
    rev = f["revenue"].astype(float)
    usd = f["fxusd"].astype(float) == 1.0

    mcap = ctx.universe["mkt_cap_usd"].astype(float).reindex(f.index)
    m = mcap.where(mcap > 0)

    out = (rev / m).where(usd)
    return out.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="SP",
    col="f_sp",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: high sales-to-price is attractive (the long leg)
    weight=1.0,
    inputs=("SF1.revenue", "SF1.fxusd", "DAILY.marketcap"),
    osap_acronym="SP",
    source="Barbee, Mukherji and Raines 1996 (Financial Analysts Journal)",
    lookback_months=15,             # latest filing within max_fundamental_age_months
    notes="revenue (ART TTM) / universe mkt_cap_usd; cap > 0 guard; fxusd==1; revenue <= 0 not guarded",
    field_mappings=(
        ("compustat.sale", "SF1.revenue (ART)",
         "TTM as of the latest filing, not fiscal year + 6-month lag; revenue <= 0 left unguarded as in OSAP"),
        ("crsp.mve_permco", "DAILY.marketcap via ctx.universe['mkt_cap_usd']",
         "company-level cap at the primary ticker's price, month-end; one route, no class sum"),
        ("compustat.curcd", "SF1.fxusd", "gate fxusd == 1 (reporting-currency numerator over a USD denominator); drops ~0.03% of names"),
        ("guard", "mkt_cap_usd > 0", "non-positive cap -> NaN"),
    ),
)
