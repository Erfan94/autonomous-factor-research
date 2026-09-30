"""
ShareIss1Y — one-year share issuance: growth in the share count between 18 and 6
months before the signal, skipping the most recent six months.

OSAP: ShareIss1Y, Pontiff and Woodgate 2008, Journal of Finance ("Share issuance and
cross-sectional returns", Table 3A ISSUE; Acronym2 ShareIs5). Predicted sign: -
(high issuance earns lower returns; the lowest-issuance end is the long leg, harness D10).
Spec: osap_source/cache/b4e911e6/ShareIss1Y/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  s6  = SF1.sharesbas, latest filing with datekey <= the business month-end 6 months
        before the signal   (ctx.fundamentals_at_month_ends lag 6)
  s18 = SF1.sharesbas at the business month-end 18 months before the signal (lag 18)
  score = s6 / s18.where(s18 > 0) - 1        (== (s6 - s18) / s18, as OSAP)
  Raw ratio, no winsorising. ascending=False: HIGH issuance is unattractive (the
  low-issuance end is the long leg, harness D10), matching SignalDoc Sign = -1.
  Follows the OSAP CODE (shrout * cfacshr), not the docstring wording (shrout /
  cfacshr). Sharadar restates sharesbas to today's split basis, so the ratio of two
  readings is split-neutral (checked in the spec on AAPL, NVDA, TSLA: no step across
  a split). sharesbas is never paired with closeunadj.
  Both readings are in the past (t-6, t-18): no contemporaneous leakage. Each sees only
  the filings public at its own month-end. Default dimension (ART); sharesbas is a
  level and ART and ARQ carry the same count.

GUARDS (every denominator; a negative one is a sign flip, not an outlier):
  - s18 > 0.
  - Non-finite results -> NaN.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? An unchanged share count between the
  two readings (no issuance, buyback or option exercise) gives exactly 0.0.
  What share of the universe does nothing? Spec measurement on 92 of 276 decision
  months (90 with >= 100 scored names): exact 0.0 is 0.92% of scored names mean
  (max 1.54%), modal value 0.0 in all 90 months; |change| < 0.1% is 4.5% mean (max
  6.4%); 10 qcut bins everywhere (distinct/n 97%). Same filing at both lags (a stale
  count): 0.03% mean (max 0.7%). Preflight measures it again.
  Tie handling: none. OSAP has no tie rule, no winsorisation and no floor; the mass is
  far below the 10% cliff and an unchanged count is a real observation (average rank).
  Buyback names are negative, not zeroed, as in OSAP.

DEVIATIONS FROM OSAP:
  - shrout * cfacshr (CRSP, per PERMNO, monthly) -> SF1.sharesbas: company-level (all
    classes) count on the primary ticker, stepping at filing dates (10-K/10-Q cover
    count), split-restated by Sharadar so no cfacshr is needed.
  - Calendar-exact lag match -> latest filing known at the business month-end t-6 / t-18,
    so each reading can be up to ~one quarter stale (max_fundamental_age_months caps it
    at 15).
  - history_months=18 approximates OSAP's requirement of a CRSP row at t-18: the harness
    gate needs a PRICE within 7 days of the t-18 month-end. A share-count filing known
    at t-18 may be up to 15 months older, hence lookback_months = 18 + 15 = 33.
  - Coverage start: SF1 filings begin early 1998, so the first decision months are empty
    (spec: 0% at 1998-12 and 1999-03, 45.7% at 1999-06, ~82% at 1999-09..12, 88-98% from
    2002).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    sh = ctx.fundamentals_at_month_ends(["sharesbas"], [6, 18])
    w = sh.pivot_table(index="ID", columns="months_back", values="sharesbas", aggfunc="last")
    nan = pd.Series(np.nan, index=ctx.ids)
    s6 = w[6].astype(float).reindex(ctx.ids) if 6 in w.columns else nan
    s18 = w[18].astype(float).reindex(ctx.ids) if 18 in w.columns else nan

    out = s6 / s18.where(s18 > 0) - 1.0
    return out.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="ShareIss1Y",
    col="f_shareiss1y",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: LOW issuance (net repurchasers) is attractive
    weight=1.0,
    inputs=("SF1.sharesbas",),
    osap_acronym="ShareIss1Y",
    source="Pontiff and Woodgate 2008 (Journal of Finance)",
    lookback_months=33,             # 18-month window + latest filing up to 15 months old at the t-18 end
    history_months=18,              # a listed name (price) at t-18, as OSAP needs a CRSP row there
    notes="sharesbas(t-6)/sharesbas(t-18) - 1, ART as-of-filing; split-restated counts; sign -1",
    field_mappings=(
        ("crsp.shrout * cfacshr", "SF1.sharesbas at business month-ends t-6 and t-18 (ART)",
         "company-level count on the primary ticker, steps at filing dates; split-restated to today's basis so no cfacshr; never paired with closeunadj"),
        ("calendar-exact t-6 / t-18 match", "ctx.fundamentals_at_month_ends lags 6 and 18",
         "latest filing known at each business month-end (up to ~a quarter stale, age cap 15 months)"),
        ("CRSP row at t-18", "history_months=18", "harness price gate within 7 days of the t-18 month-end"),
        ("coverage start", "first valid month 1999-06", "no filing known at t-18 before ~1998; 1999-01..1999-05 empty, 1999-06..08 thin"),
    ),
)
