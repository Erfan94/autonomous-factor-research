"""
VolumeTrend — volume trend: the 60-month OLS slope of monthly trading volume on
time, scaled by the 60-month mean volume (a growth rate of trading activity); a
rising volume trend is predicted to earn a LOWER return.

OSAP: VolumeTrend, Haugen and Baker 1996, Journal of Financial Economics
(Table 1, trading volume trend). Predicted sign: - (SignalDoc Sign = -1), so
ascending=False (HIGH raw is the short leg).
Spec: osap_source/cache/b4e911e6/VolumeTrend/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  Daily SEP rows (close, closeunadj, volume) for the universe over the 60
  CALENDAR months t-59 .. t (the signal month included, read in full),
  restricted to the market trading calendar (harness market_trading_calendar
  applied to the universe's own SEP dates, so a stray weekend/holiday row never
  enters a month). Rows with closeunadj <= 0 or close <= 0 are dropped.
    as-traded shares_d = SEP.volume x SEP.close / SEP.closeunadj
    monthly volume_m   = sum of as-traded shares_d over the calendar month
                         (zero is an observation, a missing month is not).
  x_m = the calendar month index (period ordinal; consecutive integers, so the
  slope is per month as OSAP's (year-1960)*12 + month - 1).
  slope = OLS slope of volume_m on x_m over the 60 months = cov(x, vol)/var(x);
  meanX = mean of volume_m over the same 60 months;
  VolumeTrend = slope / meanX, meanX guarded > 0 (meanX == 0 -> NaN, the 0/0 of
  a name that never trades). FULL window required (all 60 months present), else
  NaN (decision volume_windows).
  As-traded, not restated: CRSP vol is unadjusted, and a split inside the window
  is a step in as-traded volume as in OSAP. The ratio is scale-free, so the
  restatement causes no cross-firm look-ahead either way; as-traded is chosen
  as the faithful route (closeunadj is used only as the ratio that undoes the
  restatement, never paired raw with volume).
  If any of the 60 window months is the 1997-12 snapshot-start stub
  (ctx.partial_months("SEP")), every name is NaN. history_months=59: the harness
  nulls a name with no price near the month t-59 end. The first fully scorable
  signal is 2002-12 (228 of 276 decision months).
  No SF1 input, so no dimension and no ART/ARQ question.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? A constant monthly volume gives
  slope 0 (VolumeTrend = 0); no trading at all gives meanX = 0, which is NaN.
  What share of the universe does nothing? ~0%. The spec measured, at 11 probe
  months, 0 names with an exact-zero slope and 0 with meanX == 0, a modal share
  of 0.051-0.062% of scored names and distinct values equal to the scored names
  (1,619-1,963), with 10 qcut bins. Preflight decides.
  Tie handling: null. meanX <= 0 is NaN; an exactly-zero VolumeTrend (constant
  volume, an artefact) is also set NaN and blend_ranks renormalises; nothing is
  floored.

DEVIATIONS FROM OSAP:
  - min_periods: OSAP's regression min_periods=30 / mean min_samples=30 floor is
    NOT reproduced; the full 60-month window is required (decision
    volume_windows, extending momentum_partial_windows), so names with 30-59
    months are NaN and the first scorable signal is 2002-12, not 2000-06.
  - pooled trim: OSAP's winsor2(cut(1 99), trim) over all permno-months of the
    full sample (values outside the pooled 1st/99th percentile set missing) is
    NOT reproduced: it uses the whole sample's distribution (look-ahead in
    level). The harness's per-month winsorisation applies instead, which caps
    rather than drops the tail names.
  - crsp.vol: as-traded volume is rebuilt as SEP.volume x close / closeunadj
    (SEP.volume is split-restated). Residual: massive reverse splits
    (close/closeunadj > 100) can show spurious low-volume months for a handful of
    names; closeunadj > 0 is the only guard. SEP.volume is consolidated; CRSP
    NASDAQ volume before 2004 double counts dealer trades, so the trend of the
    double-counted series differs around 2004 (the ratio is scale-free but not
    trend-free).
  - window: OSAP's regression window is 60 panel ROWS and its mean is 60
    calendar months; here both are the 60 calendar months t-59..t.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef
from harness.data_layer import market_trading_calendar

_MONTHS = 60            # calendar months t-59 .. t
_DAYS_BACK = 1850       # 60 calendar months (<= ~1830 days) plus margin


def _compute(ctx):
    nan = pd.Series(np.nan, index=ctx.ids)
    month = ctx.signal_asof.to_period("M")
    window = pd.period_range(month - (_MONTHS - 1), month, freq="M")
    if any(p in ctx.partial_months("SEP") for p in window):
        return nan
    d = ctx.daily("SEP", ["close", "closeunadj", "volume"], _DAYS_BACK)
    if d.empty:
        return nan
    cal = market_trading_calendar(d["date"])             # trading days, stray rows excluded
    d = d[d["date"].isin(cal)]
    cl = d["close"].astype(float)
    cu = d["closeunadj"].astype(float)
    d = d[(cu > 0) & (cl > 0)]
    d = d.assign(m=d["date"].dt.to_period("M"))
    d = d[d["m"].isin(window)]
    if d.empty:
        return nan
    d = d.assign(sh=d["volume"].astype(float) * d["close"].astype(float) / d["closeunadj"].astype(float))

    monthly = d.groupby(["ID", "m"])["sh"].sum(min_count=1)   # zero is an observation
    wide = monthly.unstack("m").reindex(columns=window)       # ID x 60 months
    full = wide.notna().all(axis=1)
    wide = wide[full]
    if wide.empty:
        return nan

    x = np.array([p.ordinal for p in window], dtype=float)    # consecutive calendar-month index
    xc = x - x.mean()
    y = wide.to_numpy(dtype=float)
    slope = (y @ xc) / float(xc @ xc)                         # cov(x, y) / var(x), the OLS slope
    mean_x = y.mean(axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        val = pd.Series(slope / np.where(mean_x > 0, mean_x, np.nan), index=wide.index)
    val = val.where(np.isfinite(val) & (val != 0))
    return val.reindex(ctx.ids)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="VolumeTrend",
    col="f_voltrend",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: a rising volume trend predicts low returns
    weight=1.0,
    inputs=("SEP.close", "SEP.closeunadj", "SEP.volume"),
    osap_acronym="VolumeTrend",
    source="Haugen and Baker 1996 (Journal of Financial Economics)",
    history_months=59,              # full 60-month window: a price at the month t-59 end (harness gate)
    lookback_months=60,             # calendar months t-59..t
    notes="OLS slope of monthly AS-TRADED volume on the month index / mean monthly volume over calendar months t-59..t, all 60 required; meanX <= 0 NaN; no pooled trim",
    field_mappings=(
        ("crsp.vol (as traded, unadjusted)", "SEP.volume x SEP.close / SEP.closeunadj, summed by calendar month",
         "SEP.volume is split-restated; the close/closeunadj ratio undoes it per day so a split step appears as in OSAP; reverse-split tail can lose shares; consolidated volume vs CRSP exchange volume (NASDAQ dealer double count pre-2004)"),
        ("rolling_ols(60, min_periods=30) over panel rows; asrol mean(60, min_samples=30)", "OLS slope and mean over calendar months t-59..t, all 60 required",
         "OSAP's min-30 floor not reproduced (decision volume_windows); one calendar window for both slope and mean; first scorable signal 2002-12"),
        ("winsor2(VolumeTrend, cut(1 99), trim), pooled over the full sample", "none (harness per-month winsorisation)",
         "pooled full-sample trim is look-ahead in level and is not reproduced; the harness caps the tails per month instead of dropping them"),
        ("meanX == 0", "NaN", "meanX guarded > 0"),
    ),
)
