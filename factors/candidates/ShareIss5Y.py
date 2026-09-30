"""
ShareIss5Y — five-year share issuance: growth in the share count over the 60 months
ending 5 months before the signal.

OSAP: ShareIss5Y, Daniel and Titman 2006, Journal of Finance (Acronym2 ShareIs1;
Cat.Economic external financing). Predicted sign: - (high issuance earns lower returns;
long the lowest-issuance decile D1).
Spec: osap_source/cache/b4e911e6/ShareIss5Y/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  s5  = SF1.sharesbas (ARQ), latest filing with datekey <= the business month-end 5
        months before the signal    (ctx.fundamentals_at_month_ends lag 5)
  s65 = SF1.sharesbas (ARQ) at the business month-end 65 months before the signal (lag 65)
  score = s5 / s65.where(s65 > 0) - 1        (== (s5 - s65) / s65, as OSAP)
  Raw ratio, no winsorising. ascending=False: HIGH issuance is unattractive (D1 is
  the long leg), matching SignalDoc Sign = -1.
  The OSAP CODE is temp = shrout * cfacshr and (temp[t-5] - temp[t-65]) / temp[t-65]; the
  SignalDoc text says "shrout/cfacshr". The code is followed. Sharadar restates sharesbas
  to today's split basis on every historical row, so the ratio of two readings on the
  same route is split-neutral (spec: ratio-1 on AAPL -0.108, NVDA +0.167, C +0.047, TSLA
  +0.438, no step across a split or reverse split). sharesbas is never paired with
  closeunadj and the two ends never mix routes (no DAILY.marketcap / SEP.close ratio).
  Both readings are in the past (t-5, t-65); each sees only the filings public at its own
  month-end. The 5-month gap is OSAP's own skip (Daniel-Titman "t-5..t"), reproduced.
  Same idiom as the ShareIss1Y leg (ratio of two fundamentals_at_month_ends readings,
  denominator guarded, non-finite to NaN), with lags 5 and 65.
  dimension="ARQ": ARQ is the quarterly as-reported series and reaches back further than
  ART for a level read 65 months earlier; sharesbas is a level, not a flow, so ART vs
  ARQ does not change the count's meaning, only the depth of history on the t-65 end.

GUARDS (every denominator; a negative one is a sign flip, not an outlier):
  - s65 > 0.
  - Non-finite results -> NaN.
  - A name with no filing known at either end is NaN (no zero-fill; OSAP zero-fills
    nothing here and drops the row).

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? An unchanged share count between the
  two readings (no issuance, buyback or option exercise in 60 months) gives exactly 0.0.
  What share of the universe does nothing? Spec measurement on the 270 decision months
  with >= 10 scored names (1999-06 .. 2021-12): exact 0.0 is 0.27% of scored names mean
  (max 1.67%); the modal-value share of the cross-section is 0.29% mean (max 3.45%, a
  29-name month); within +-1% of zero is 5.4% mean (3.6-8.3%); 10 qcut bins in all 270
  months; ~1,350 distinct values per month on average. Not a mass point, far below the
  10% cliff. Tie handling: none (average rank); nothing floored, nothing nulled; an
  unchanged count is a real observation. Buyback names are negative, not zeroed.
  The right tail is heavy (median over months p1 -0.34, p50 +0.05, p99 +4.5); the
  harness 1/99 winsorise handles it, nothing is clipped here. Preflight measures it again.

DATA-START FACT (declared, not a rule): SF1 ARQ is thin before ~1998, so the t-65 end
  is unknown for most names until the snapshot has 65 months behind it. Coverage of the
  harness universe is >= 40% only from 2002-07; 43 early decision months (1999-01 ..
  2002-06) sit below the coverage bar and are a small, survivor-biased sample; 233 of 276
  months are above it and 270 have >= 10 scored names (first 1999-06). The first probe
  month (1998-12) scores 0 names and the 80-month lookback reaches before the panel
  start; both are data limits and preflight warnings, not factor defects.

DEVIATIONS FROM OSAP:
  - shrout * cfacshr (CRSP, per PERMNO, monthly) -> SF1.sharesbas (ARQ): company-level
    (all classes) count on the primary ticker, stepping at filing dates (10-K/10-Q cover
    count), split-restated by Sharadar so no cfacshr is read.
  - Exact-month CRSP row at t-5 and t-65 -> latest filing known at the business
    month-end (<= 15 months old): carried forward between filings, no gap requirement;
    each reading can be up to ~one quarter stale against CRSP's monthly shrout.
  - No history gate: the factor reads share counts only, not prices.
    A price-history gate (has_price_at(65)) would null every month before 2003-06
    (SEP starts 1997-12) and is deliberately not declared.
  - lookback_months = 65 + 15 = 80: the latest ARQ filing behind the t-65 end may be up
    to 15 months old.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    sh = ctx.fundamentals_at_month_ends(["sharesbas"], [5, 65], dimension="ARQ")
    w = sh.pivot_table(index="ID", columns="months_back", values="sharesbas", aggfunc="last")
    nan = pd.Series(np.nan, index=ctx.ids)
    s5 = w[5].astype(float).reindex(ctx.ids) if 5 in w.columns else nan
    s65 = w[65].astype(float).reindex(ctx.ids) if 65 in w.columns else nan

    out = s5 / s65.where(s65 > 0) - 1.0
    return out.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="ShareIss5Y",
    col="f_shareiss5y",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: LOW issuance (net repurchasers) is attractive
    weight=1.0,
    inputs=("SF1.sharesbas",),
    osap_acronym="ShareIss5Y",
    source="Daniel and Titman 2006 (Journal of Finance)",
    dimension="ARQ",                # quarterly series reaches back furthest for the t-65 reading
    lookback_months=80,             # 65-month window end + latest filing up to 15 months old
    no_history_gate_because=("reads share counts only, no price; a name without a filing "
                             "known at t-65 is NaN by construction"),
    notes="sharesbas(t-5)/sharesbas(t-65) - 1, ARQ as-of-filing; split-restated counts; sign -1; coverage >= 40% only from 2002-07",
    field_mappings=(
        ("crsp.shrout * cfacshr", "SF1.sharesbas (ARQ) at business month-ends t-5 and t-65",
         "company-level count on the primary ticker, steps at filing dates; split-restated to today's basis so no cfacshr; never paired with closeunadj"),
        ("exact-month CRSP row at t-5 and t-65", "ctx.fundamentals_at_month_ends lags 5 and 65",
         "latest filing known at each business month-end (up to ~a quarter stale, age cap 15 months); a name with no filing at t-65 is NaN"),
        ("shrout / cfacshr (SignalDoc text)", "shrout * cfacshr (OSAP code) -> split-restated sharesbas",
         "the code multiplies; the ratio of two restated readings is split-neutral"),
        ("coverage start", "coverage >= 40% only from 2002-07 (43 early months below the bar)",
         "SF1 ARQ thin before ~1998, so the t-65 end is unknown for most names early; data limit, no rule applied"),
    ),
)
