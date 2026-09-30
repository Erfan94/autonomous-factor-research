"""
MeanRankRevGrowth — the 5,4,3,2,1 weighted mean of a firm's annual revenue-growth
RANK at the five past year-ends (12, 24, 36, 48, 60 months ago). Rank 1 = the
HIGHEST growth that month, so a HIGH score means persistently LOW past revenue
growth: the contrarian (value) side, which is the LONG leg.

OSAP: MeanRankRevGrowth (Acronym2 RevGrowth), Lakonishok, Shleifer and Vishny 1994,
Journal of Finance (Table 6 panel 2). Predicted sign: + on the rank NUMBER
(SignalDoc Sign = +1). ascending=True on the raw mean rank; the SignalDoc wording
"rank firms by revenue growth" invites the opposite orientation; the code's
ordering (gsort -temp, rank 1 = highest growth) is followed.
Spec: osap_source/cache/b4e911e6/MeanRankRevGrowth/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  Market scope (ctx.fundamentals_at_month_ends(..., scope="market"): every listed
  common stock that traded at the lag's month-end, no price/size/liquidity screen;
  OSAP ranks over all of Compustat-CRSP, not the harness universe). ART revenue
  (SF1.revenue, TTM, as known by datekey at each business month-end) read at the
  month-ends s = 12, 24, ..., 72 before the signal.
  For k = 1..5, at month s = 12k:
    g_k = ln(rev_s) - ln(rev_{s+12})    only if rev_s > 0 and rev_{s+12} > 0,
                                        else NaN (no zero-fill, no log of <= 0)
    R_k = ordinal rank of g_k among the market-scope names with a valid g_k at
          that month, DESCENDING (1 = highest growth), method="first" (ties in
          g_k broken by ID order; OSAP's unstable-sort tie order is arbitrary
          too). RAW ordinals 1..N, not percentiles.
  Signal = (5 R_1 + 4 R_2 + 3 R_3 + 2 R_4 + 1 R_5) / 15, ALL FIVE ranks required
  (any missing lag -> NaN; no partial windows, as OSAP). Raw value, no
  winsorising. Only universe names are scored (reindexed to ctx.ids); the harness
  ranks the score within sector afterwards.
  These input ranks at historical lags are part of the signal DEFINITION (an
  input transform at past dates), not the harness's cross-sectional or sector
  ranking of the final signal; hence pandas rank inside the factor, over
  scope="market" names (coordinator decision, logged).
  N DIFFERS ACROSS LAGS: the number of ranked names is that month's count, so the
  five ranks in one signal run on different scales (spec measured 2003-12: lag 12
  runs to 5,185, lag 60 only to 1,734 because few firms then had two readings;
  converging by 2005-03: 5,083 vs 5,382). In early months the mean rank therefore
  overweights the recent lags. Raw ordinals are kept, as OSAP.
  Revenue currency: log growth is taken within one firm, so revenue stays in
  reporting currency (no revenue/fxusd; no cross-firm sum); it is growth in the
  currency the firm reports in, free of FX-rate noise.
  lookback_months=87: the t-72 reading (a filing up to 15 months stale) feeds the lag-60 growth. No history gate
  (no SEP input). Default dimension ART (quarterly-refreshed TTM); ARQ must not be
  used (a single quarter vs the same quarter a year ago is a different signal).
  First scorable signal 2003-12-31 (60 leading null months).

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Flat revenue year on year gives
  g = 0 exactly, a mid-table rank (ties among exactly-flat names are broken by ID
  order); nothing is zero-filled, and a missing or non-positive revenue is NaN,
  not a rank. The mean of five ordinal ranks takes many distinct values.
  What share of the universe does nothing? The spec measured a modal share of any
  value at most 0.32% (mean 0.17%), 715 (2003-12) to 1,529 distinct values per
  month, and 10 qcut(10) bins in every scorable month. Preflight to confirm.
  Tie handling: none needed (null where a lag is missing, which blend_ranks
  renormalises); the harness average rank covers exact ties.

DEVIATIONS FROM OSAP:
  - Each growth pair is required to span one fiscal year by reportperiod (+-45 days,
    the project's yoy convention); under the 15-month staleness limit a firm that
    stopped filing could otherwise return the same filing at both lags (g = 0) or a
    9/15-month span (alpha_review batch14 major).
  - The rank pool at lag s needs readings at both s and s+12 (OSAP: an m_aCompustat row).
  - revt (annual, available datadate + 6 months, stepping once a year) -> ART TTM
    revenue refreshed every quarter; growth is a true year-over-year change
    between two non-overlapping trailing-four-quarter sums. ARY is the closer
    annual-cadence alternative; ART is the default.
  - Revenue as known by datekey at each lag month-end (restatements filed later
    are not seen); OSAP uses the as-restated annual figures at download.
  - Ranks over the market scope (every listed common stock that traded that
    month) not all m_aCompustat permnos: a different N per month, no
    delisted-before-linking firms; N differs across the five lags.
  - method="first" ordinal ranks; tie order arbitrary as OSAP's.
  - No NASDAQ exclusion (SignalDoc filter, not in predictor.py); the harness
    universe decides.
  - First 60 decision months null (t-72 ART is thin before 1998-12); 3 early
    months (2003-12 .. 2004-02) under 40% coverage; 47-53% to 2005-02.
  - Harness ranks the score within sector afterwards (D3).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef

_LAGS = (12, 24, 36, 48, 60, 72)            # growth at s = 12k needs revenue at s and s+12
_WEIGHTS = (5.0, 4.0, 3.0, 2.0, 1.0)        # rank at lag 12k weighs 6-k; sum 15


def _compute(ctx):
    nan = pd.Series(np.nan, index=ctx.ids)
    f = ctx.fundamentals_at_month_ends(["revenue"], _LAGS, scope="market")
    if f.empty:
        return nan
    rev = f.pivot_table(index="ID", columns="months_back", values="revenue", aggfunc="last").astype(float)
    rev = rev.where(rev > 0)                 # revenue <= 0 or missing -> growth NaN
    rp = f.assign(rp=pd.to_datetime(f["reportperiod"])).pivot_table(
        index="ID", columns="months_back", values="rp", aggfunc="last")

    score = pd.Series(0.0, index=ctx.ids)
    for w, s in zip(_WEIGHTS, _LAGS[:-1]):
        if s not in rev.columns or (s + 12) not in rev.columns:
            return nan                       # a lag with no reading at all: no name has all five
        with np.errstate(divide="ignore", invalid="ignore"):
            g = np.log(rev[s]) - np.log(rev[s + 12])
        # the two readings must be one fiscal year apart (the yoy convention, +-45 days);
        # a stale repeat of the same filing or a 9/15-month span is NaN
        gap = (rp[s] - rp[s + 12]).dt.days
        g = g.where((gap - 365).abs() <= 45)
        g = g.replace([np.inf, -np.inf], np.nan).dropna()
        # raw ordinal rank among that month's market-scope names, 1 = highest growth
        r = g.rank(ascending=False, method="first")
        score = score + w * r.reindex(ctx.ids)   # NaN if any of the five ranks is missing
    return (score / sum(_WEIGHTS)).reindex(ctx.ids)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="MeanRankRevGrowth",
    col="f_meanrankrevg",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1 on the rank number; rank 1 = HIGHEST growth, so a HIGH score = low growth = long
    weight=1.0,
    inputs=("SF1.revenue",),
    osap_acronym="MeanRankRevGrowth",
    source="Lakonishok, Shleifer and Vishny 1994 (Journal of Finance)",
    lookback_months=87,             # revenue at lag 72 from a filing up to 15 months stale (as Herf)
    notes="5,4,3,2,1 weighted mean of annual revenue-growth raw ordinal ranks (1 = highest growth) at lags 12..60, market scope, all five required; HIGH = low growth = long",
    field_mappings=(
        ("compustat.revt (annual, datadate + 6m)", "SF1.revenue (ART, market scope, at each lag month-end)",
         "quarterly-refreshed TTM as known by datekey vs an annual step; reporting currency, no fxusd (log growth within one firm)"),
        ("tempRank (gsort -temp, row number, all m_aCompustat)", "pandas rank(ascending=False, method='first') over market-scope names",
         "raw ordinals; N differs per month and across the five lags; tie order arbitrary as OSAP's"),
        ("tempRank_lag12..60 (calendar merge)", "rank at month-ends 12..60 back",
         "all five required, no partial windows, as OSAP"),
        ("SignalDoc Filter exchcd in (1,2)", "harness universe",
         "NASDAQ exclusion is a portfolio filter, not in predictor.py; not applied"),
        ("coverage start", "first valid signal 2003-12-31",
         "t-72 ART reading needed; 60 leading decision months empty; 2003-12..2004-02 below 40% coverage"),
    ),
)
