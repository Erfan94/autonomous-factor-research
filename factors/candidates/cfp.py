"""
cfp — operating cash flow to price: cash from operations over the market value
of equity. A firm whose operating cash flow is large against its price is cheap.

OSAP: cfp, Desai, Rajgopal and Venkatachalam 2004, The Accounting Review
(Table 2E R1). Predicted sign: + (SignalDoc Sign = +1: high cash-flow-to-price
earns high returns; long D10, short D1; ascending=True).
Spec: osap_source/cache/b4e911e6/cfp/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  f   = ctx.fundamentals(["ncfo", "fxusd"])      (ART default: trailing-four-quarter
        flow to the latest filing known at the signal date)
  M   = ctx.universe["mkt_cap_usd"]              (DAILY.marketcap at the month-end)
  cfp = SF1.ncfo / M          with M > 0 and fxusd == 1, else NaN
  OSAP: cfp = oancf / mve_permco where oancf is present; where oancf is missing the
  numerator is replaced by (ib - accrual_level), accrual_level = (d act - d che) -
  (d lct - d dlc - d txp - dp).
  Raw ratio, no log, no winsorising. Negative cfp is kept (negative operating cash
  flow is a real value). ncfo is a FLOW used as a level ratio (no year-over-year
  difference), so ART is right and there is no TTM smear issue; ncfo is never read
  as a balance-sheet level.

FALLBACK BRANCH NOT REPRODUCED (coordinator decision cfp_fallback_branch):
  OSAP's txp fallback applies only where oancf is missing. txp (taxes payable) has
  no SF1 field and OSAP does not zero-fill it, so the fallback cannot be built.
  Names with ncfo null are NaN (never zero-filled: a null ncfo is a cash-flow
  statement not reported, not a zero). blend_ranks renormalises around the null.
  Per the spec, ncfo is null on median 2.7% of filed universe names (1.0-3.2%
  2003-2020), but 40-48% at the first three signal months (ART needs four quarters
  of SF1 history; SF1 starts 1997Q4) and ~10-13% through 1999-2000.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? None: a firm with no new filing
  keeps ncfo fixed, but the denominator (market cap) moves every month, so cfp moves
  continuously. No default value and no zero-fill of the signal. The only exact-zero
  case is ncfo == 0 (0.055% of non-null ncfo).
  What share of the universe does nothing? Spec measured over 276 months on the
  scored cross-section: exact-zero share median 0.053%, max 0.114%; modal-value
  share median 0.054%, max 0.118% (at most 2-3 names); distinct values equal n
  scored; 10 qcut bins in every month. Preflight to confirm.
  Tie handling: none needed; nulls (ncfo missing, M <= 0, fxusd != 1) stay NaN.

DEVIATIONS FROM OSAP:
  - Fallback numerator (ib - accrual_level) not built (above); ncfo-null names NaN.
  - Timing: the numerator is a TTM sum to the latest filed quarter (0-3 months old,
    capped at 15) against OSAP's fiscal-year oancf available 6 months after year-end
    and held 12 (6-17 months old). The 6-month lag is not reproduced. Coverage is
    thin at the first three signal months (ART needs four quarters of history); the
    40% bar is cleared under ART, so no ARY override.
  - oancf -> SF1.ncfo: net cash flow from operations as reported by Sharadar,
    inflow-positive, in the filer's reporting currency.
  - mve_permco -> DAILY.marketcap (primary-class ticker's price x all-class shares):
    a few-percent level difference on <= 2% of names.
  - fxusd != 1 names NaN rather than converted: the numerator is in reporting
    currency and the denominator in USD (<= 0.06% of universe names).
  - (for reference) the dropped fallback's ib would be netinc + netincdis, not
    netinccmn.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    f = ctx.fundamentals(["ncfo", "fxusd"])
    ncfo = f["ncfo"].astype(float)
    usd = f["fxusd"].astype(float) == 1.0

    mcap = ctx.universe["mkt_cap_usd"].astype(float).reindex(f.index)
    m = mcap.where(mcap > 0)

    cfp = (ncfo / m).where(usd)       # ncfo NaN stays NaN: no zero-fill, fallback not built
    return cfp.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="cfp",
    col="f_cfp",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: high cash-flow-to-price is the long leg
    weight=1.0,
    inputs=("SF1.ncfo", "SF1.fxusd", "DAILY.marketcap"),
    osap_acronym="cfp",
    source="Desai, Rajgopal and Venkatachalam 2004 (The Accounting Review)",
    lookback_months=15,             # latest filing within max_fundamental_age_months
    notes="ART ncfo / market cap; fxusd==1; cap>0; ncfo null -> NaN; OSAP ib-accrual fallback (txp) not built; sign +1",
    field_mappings=(
        ("compustat.oancf", "SF1.ncfo (ART)",
         "TTM flow to the latest filed quarter vs OSAP fiscal-year value at datadate + 6 months; null never zero-filled"),
        ("compustat.ib, act, che, lct, dlc, txp, dp (fallback where oancf is missing)", "none",
         "fallback branch NOT reproduced: txp has no SF1 field and OSAP does not zero-fill it; ncfo-null names NaN"),
        ("crsp.mve_permco", "DAILY.marketcap via ctx.universe['mkt_cap_usd']",
         "company-level all-class cap at the primary ticker's price; few-% level error on <=2% of names; cap <= 0 -> NaN"),
        ("compustat.curcd", "SF1.fxusd", "gate fxusd == 1 (numerator reporting currency, denominator USD); <=0.06% of names NaN"),
    ),
)
