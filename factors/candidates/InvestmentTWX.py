"""
InvestmentTWX — capex-to-revenue divided by the firm's own mean of that ratio
over the current and two prior fiscal years: investment relative to its own
history. High relative investment is predicted to earn low returns.

OSAP: Investment (Acronym2 InvToRev), Titman, Wei and Xie 2004, Journal of
Financial and Quantitative Analysis (Table 1B Average). Predicted sign: -
(SignalDoc Sign = -1: long LOW, short HIGH).
Spec: osap_source/cache/b4e911e6/Investment/spec.md
NAMING: the file and factor are InvestmentTWX; the OSAP acronym is "Investment".
The v0 composite leg NAMED Investment is AssetGrowth (total-assets growth), a
different signal built from different inputs.

CONSTRUCTION (as translated; every deviation from OSAP stated):
  x_k = (-SF1.capex_k) / SF1.revenue_k  for the latest fiscal year (k = 0) and the
        two fiscal years before it (k = -1, -2), dimension ARY, aligned by
        reportperiod via ctx.fundamentals_yoy(years=1) and (years=2). Capex is
        negated (Sharadar capex is a cash outflow, OSAP capx is positive).
  tempMean = mean(x_0, x_-1, x_-2). The mean INCLUDES the current year's own
        ratio, as OSAP codes it (asrol window contains the current month); it is
        not "corrected" to the prior years. THREE ratios are required (the
        faithful reading of OSAP's min_samples = 24 over annual records each
        repeated 12 months); fewer than three -> NaN.
  score = x_0 / tempMean, NaN where tempMean <= 0 (OSAP divides by any tempMean).
  Revenue filter as OSAP: current-year revenue < $10m (USD: revenue / fxusd) -> NaN.
  Raw ratio, no winsorising, no log. ascending=False: a LOW score is the long leg,
  matching SignalDoc Sign = -1.
  dimension="ARY" (passed explicitly to every accessor): capex and revenue are
  FLOWS; ART would be a quarterly-refreshed TTM sum, so a three-window mean would
  overlap and smear, and ART capex is 46% null in 1998. ARY is one fiscal-year
  value per year.

OVERLAP WITH THE v0 AssetGrowth LEG (measured in the spec, Spearman per month on
the harness universe, averaged over 276 months): mean 0.076, range -0.011 .. 0.200.
Inputs differ (capex and revenue here; total assets there).

GUARDS (every denominator; a negative one is a sign flip, not an outlier):
  - revenue_k > 0 for each of the three ratios (a zero/negative revenue year
    nulls the ratio, hence the score).
  - tempMean > 0 (a non-positive mean flips or removes the sign; ~3.9% of
    computable names per the spec, nulled; OSAP keeps the ratio).
  - fxusd > 0 for the $10m conversion; non-finite results -> NaN.
  - The current ratio x_0 is NOT required positive: a positive Sharadar capex
    (sign-inverted row, ~3.4% of ARY rows) gives a negative ratio which OSAP
    also keeps, and only tempMean is guarded.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Capex exactly 0 this year with
  positive history gives exactly 0; a constant capex/revenue ratio over the three
  years gives exactly 1.0; capex only this year (zero in both prior years) gives
  exactly 3.0; capex 0 in all three years gives 0/0 and is NaN.
  What share of the universe does nothing? The spec measured a modal share of
  max 0.49%, mean 0.20% of scored names (exact zero mean 0.17%, max 0.49%), and
  no qcut(10) collapse. Preflight to confirm.
  Tie handling: null (the guards above; 0/0 -> NaN); nothing removed or floored;
  the harness average rank covers the few exact ties.

DEVIATIONS FROM OSAP:
  - Mean weights: equal weight over three fiscal-year ratios, not OSAP's
    (n_cur, 12, 12, 12 - n_cur)/36 month weights over four annual vintages.
  - Timing: ARY filing at datekey (known from filing) not datadate + 6 months;
    fiscal years aligned by reportperiod (45-day tolerance), not calendar months.
  - Guards: revenue_k > 0 on each ratio and tempMean > 0 are additions; OSAP has
    neither. Positive Sharadar capex rows are kept in x (as OSAP) but a
    non-positive mean is nulled.
  - Currency: only the $10m threshold is currency-sensitive (revenue / fxusd);
    the ratio itself is currency-free, so there is no fxusd == 1 gate.
  - curcd = USD and at, prcc_c, ni non-null gates of the OSAP annual-data
    build are not reproduced.
  - Early coverage: SF1 starts 1997Q4, so three consecutive ARY fiscal years
    exist only from about 2000; the spec measured coverage below 40% for the
    first 15 decision months (1998-12 .. 2000-02). A data-start truncation, not
    a construction choice; no history_months (no SEP window).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef

_MIN_REV_USD = 1.0e7     # OSAP: revt < 10 ($ millions) -> NaN


def _compute(ctx):
    flds = ["capex", "revenue", "fxusd"]
    y1 = ctx.fundamentals_yoy(flds, years=1, dimension="ARY")
    y2 = ctx.fundamentals_yoy(["capex", "revenue"], years=2, dimension="ARY")
    idx = y1.index

    cap0 = -y1["capex"].astype(float)
    rev0 = y1["revenue"].astype(float)
    cap1 = -y1["capex_lag"].astype(float)
    rev1 = y1["revenue_lag"].astype(float)
    cap2 = -y2["capex_lag"].reindex(idx).astype(float)
    rev2 = y2["revenue_lag"].reindex(idx).astype(float)

    x0 = cap0 / rev0.where(rev0 > 0)
    x1 = cap1 / rev1.where(rev1 > 0)
    x2 = cap2 / rev2.where(rev2 > 0)

    xs = pd.concat([x0, x1, x2], axis=1)
    xs = xs.replace([np.inf, -np.inf], np.nan)
    three = xs.notna().all(axis=1)              # min_samples=24 over annual records -> three ratios
    temp_mean = xs.mean(axis=1).where(three)    # includes the current year, as OSAP
    score = x0 / temp_mean.where(temp_mean > 0)

    fx = y1["fxusd"].astype(float)
    rev_usd = rev0 / fx.where(fx > 0)
    score = score.where(rev_usd >= _MIN_REV_USD)
    return score.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="InvestmentTWX",
    col="f_investmenttwx",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: high relative investment -> low return; long LOW
    weight=1.0,
    inputs=("SF1.capex", "SF1.revenue", "SF1.fxusd"),
    osap_acronym="Investment",
    source="Titman, Wei and Xie 2004 (Journal of Financial and Quantitative Analysis)",
    lookback_months=43,             # 24m (two prior fiscal years) + 15m max filing age + ~4m report-period-to-filing lag
    # No history_months: no SEP price window is read.
    dimension="ARY",                # flows: ART is a TTM sum (46% capex null in 1998); fiscal-year value wanted
    notes="(-capex/revenue) / mean of the current and two prior fiscal-year ratios (three required, current included); revenue >= $10m; ARY",
    field_mappings=(
        ("compustat.capx", "-SF1.capex (ARY)",
         "sign flip (Sharadar capex is an outflow; 3.4% of ARY rows are positive, kept in the ratio); "
         "ARY fiscal-year value aligned by reportperiod; filing-date timing, not datadate + 6 months"),
        ("compustat.revt", "SF1.revenue (ARY)",
         "revenue > 0 guard on each ratio (OSAP none); $10m floor applied to revenue / fxusd on the current year"),
        ("asrol mean, 36 months, min_samples 24", "equal-weight mean of three fiscal-year ratios, all three required",
         "OSAP's (n_cur,12,12,12-n_cur)/36 four-vintage month weights not reproduced; current year included as OSAP"),
        ("Investment / tempMean", "x_0 / mean, NaN where mean <= 0",
         "OSAP has no positivity guard (keeps the sign-flipped ratio); ~3.9% of computable names nulled"),
        ("compustat.curcd", "SF1.fxusd", "used only to express the $10m floor in USD; no fxusd == 1 gate (ratio is currency-free)"),
        ("coverage start", "first ~15 decision months below 40% coverage",
         "three consecutive ARY years need SF1 history from 1997Q4; data-start truncation"),
    ),
)
