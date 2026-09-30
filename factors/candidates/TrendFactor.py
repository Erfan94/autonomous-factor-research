"""
TrendFactor — the Han-Zhou-Zhu trend factor: the expected next-month return from a
trailing average of market-wide cross-sectional slopes on eleven normalised
moving averages of the price (3 to 1000 trading days); a pure price-path
momentum/reversal mix.

OSAP: TrendFactor, Han, Zhou and Zhu 2016, Journal of Financial Economics (Table 1).
Predicted sign: + (SignalDoc Sign = +1).
Spec: osap_source/cache/b4e911e6/TrendFactor/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  The harness owns both halves; this file only combines them.
  A_L    = ctx.trend_ma_signals(): mean of the name's last L SEP.close rows divided by
           the last close, L in (3, 5, 10, 20, 50, 100, 200, 400, 600, 800, 1000);
           a name with fewer than L rows gets a partial window (OSAP min_samples=1).
  ebar_L = ctx.monthly_trend_coefs(1).iloc[0]: the trailing 12-month mean of the
           market-wide monthly cross-sectional OLS slopes of next-month return on the
           eleven A_L (OSAP's regression sample: listed common stock, price >= $5,
           market cap >= NYSE 10th percentile), each slope known at its month-end.
  score  = sum_L ebar_L x A_L, NO intercept, null unless all eleven terms are present
           (OSAP N_MA_used == 11; sum(axis=1, min_count=11)).
  Timing: A_L and ebar are read at the signal date (a business month-end), exactly
  OSAP's month-end timing; the harness holds one month.
  Sample of months (declared choice): only months whose coefficient series is
  uncensored are scored (`ebar_full` true, first at the 2002-12 signal; NaN
  before). SEP starts 1997-12-31, so A_1000 is complete only from 2001-12-31; earlier
  fits rest on truncated windows and near-collinear regressors (1-11 betas). The
  spec measured 228 uncensored months of 276 (2002-12 .. 2021-11).
  History gate: history_months=48, a price at the month-end 48 months back (about
  1,008 trading days), so a name whose 1000-row moving average is partial is NaN.
  This is a deviation from OSAP, which scores partial windows; the gate is a
  price-presence test within 7 days, so a name with a few missing SEP rows can still
  carry a marginally partial A_1000.
  Sign: SignalDoc Sign = +1, so ascending=True.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? There is none: the score is a
  linear function of eleven name-specific price ratios, continuous and distinct.
  What share of the universe does nothing? Spec measurement on 275 scored months
  (before the history gate and the ebar_full restriction): modal value 0.035-0.058%
  of scored names (median 0.053%), distinct values equal the scored count
  (1,739-2,867), ten qcut bins in every month.
  Tie handling: none needed beyond the harness average rank; months before the
  coefficients are uncensored are removed from the sample (NaN).
  Structural feature, not a tie: within a month the score is tightly clustered
  (a month-specific linear combination of price-to-average ratios), so rank and
  within-sector treatment are appropriate.

DEVIATIONS FROM OSAP:
  - Months before 2002-12 are not scored (coefficient censoring, see above).
  - history_months=48 nulls names with a partial 1000-row moving average
    (OSAP scores partial windows).
  - Coefficient sample (inside the harness builder): exchange in force per the
    harness rule and CURRENT share category for codes 10/11; size = DAILY.marketcap
    per permaticker (not CRSP mve_c per permno), NYSE 10th percentile by linear
    quantile; price >= $5 via SEP.closeunadj; month-ahead return from month-end
    SEP.closeadj ratios (total return, no delisting return); SEP no-trade rows stand
    in for CRSP bid/ask midpoints.
  - The harness universe (price >= $1, relative size and dollar-volume screen)
    scores names between $1 and $5 that OSAP leaves blank; the coefficients
    themselves are fitted on OSAP's own filters, not the harness universe.
  - SEP.close moving averages run over SEP rows including no-trade rows.
  - No zero-fill anywhere; no fundamentals, so no ART/dimension question.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef

_TREND_LAGS = (3, 5, 10, 20, 50, 100, 200, 400, 600, 800, 1000)
_A_COLS = [f"A_{L}" for L in _TREND_LAGS]


def _compute(ctx):
    nan = pd.Series(np.nan, index=ctx.ids)
    eb = ctx.monthly_trend_coefs(1).iloc[0]
    if not bool(eb["ebar_full"]):
        return nan                      # censored coefficient series: month not scored
    ma = ctx.trend_ma_signals()
    if ma.empty:
        return nan
    coef = eb[_A_COLS].astype(float)
    score = ma[_A_COLS].astype(float).mul(coef, axis=1).sum(axis=1, min_count=len(_A_COLS))
    return score.replace([np.inf, -np.inf], np.nan).reindex(ctx.ids)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="TrendFactor",
    col="f_trendfactor",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1
    weight=1.0,
    inputs=("SEP.close", "SEP.closeadj", "SEP.closeunadj", "SEP.volume", "DAILY.marketcap", "ACTIONS.contraname"),
    osap_acronym="TrendFactor",
    source="Han, Zhou and Zhu 2016 (Journal of Financial Economics)",
    lookback_months=60,             # TREND_DAYS_BACK = 1800 calendar days for A_1000
    history_months=48,              # price 48 months back: the 1000-row moving average is not partial
    notes="sum_L ebar_L x A_L (no intercept), harness trend accessors; scored only where ebar_full (from 2002-12)",
    field_mappings=(
        ("crsp.prc / cfacpr (P)", "SEP.close", "split-adjusted, no dividend adjustment; moving averages over SEP rows incl. no-trade rows"),
        ("crsp.ret (month-ahead fRet)", "SEP.closeadj month-end ratio", "total return, no delisting return; inside the harness coefficient builder"),
        ("abs(prc) >= 5", "SEP.closeunadj >= 5", "inside the coefficient sample only"),
        ("crsp.mve_c, NYSE 10th percentile", "DAILY.marketcap, NYSE cut via exchange in force",
         "per permaticker company cap; linear quantile; inside the coefficient sample only"),
        ("exchcd 1,2,3; shrcd 10,11", "exchange in force (ACTIONS.contraname) and CURRENT TICKERS category",
         "current share category; coefficient sample only"),
        ("N_MA_used == 11", "sum(min_count=11)", "as OSAP"),
        ("partial moving-average windows scored", "history_months=48 nulls them", "deviation; OSAP min_samples=1"),
        ("coefficient months before 2002-12", "not scored (ebar_full false)", "SEP start censors A_1000 and leaves collinear regressors"),
        ("abs(prc) >= 5 on scored names", "not reproduced", "harness universe price >= $1"),
    ),
)
