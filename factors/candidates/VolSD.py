"""
VolSD — volume variance: the standard deviation of monthly trading volume over
the last 36 months; a stock whose trading volume is highly variable is
predicted to earn a LOWER return.

OSAP: VolSD, Chordia, Subrahmanyam and Anshuman 2001, Journal of Financial
Economics (Table 5B, DVOL). Predicted sign: - (SignalDoc Sign = -1: high
volume variability -> low returns), so ascending=False (HIGH raw is the short
leg).
Spec: osap_source/cache/b4e911e6/VolSD/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  Daily SEP rows (close, closeunadj, volume) for the universe over the 36
  CALENDAR months t-35 .. t (the signal month included, read in full),
  restricted to the market trading calendar (harness market_trading_calendar
  applied to the universe's own SEP dates, so a stray weekend/holiday row never
  enters a month). Rows with closeunadj <= 0 or close <= 0 are dropped.
    as-traded shares_d = SEP.volume x SEP.close / SEP.closeunadj
    monthly volume_m   = sum of as-traded shares_d over the calendar month.
  VolSD = sample standard deviation (ddof = 1) of volume_m over the 36 months,
  FULL window required (all 36 calendar months present), else NaN; exactly 0
  set NaN.
  Why as-traded: CRSP vol is UNADJUSTED for splits, and VolSD is the standard
  deviation of RAW SHARES, unscaled. SEP.volume is restated to today's split
  basis, so on that basis a cross-firm rank at a past date favours later
  splitters (future information: the later a split the larger the restated
  past volume). volume x close / closeunadj undoes the restatement per day
  (closeunadj is used only as the ratio that undoes it, never paired raw with
  volume). A split INSIDE the window creates a step in as-traded volume exactly
  as in OSAP; it is not corrected (faithful).
  If any of the 36 window months is the 1997-12 snapshot-start stub
  (ctx.partial_months("SEP")), every name is NaN. history_months=35: the
  harness nulls a name with no price near the month t-35 end. The first fully
  scorable signal is 2000-12 (252 of 276 decision months; decision
  volume_windows).
  No SF1 input, so no dimension and no ART/ARQ question.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0.0 (no trading, or a
  constant monthly volume, over the 36 months).
  What share of the universe does nothing? ~0%. The spec measured, at 11 probe
  months, 0 names with an exact-zero std (also 0 on the restated basis), a modal
  share of 0.046-0.061% of scored names and distinct values equal to the scored
  names (1,641-2,170), with 10 qcut bins. Preflight decides.
  Tie handling: null. A zero std is set NaN (an all-zero or constant series is a
  stale or non-trading artefact) and blend_ranks renormalises; nothing is floored.
  Structural: the signal is a raw share level, so it scales with how many shares
  the firm trades (a size/turnover proxy); ranks are formed within sector by the
  harness and OSAP does not deflate.

DEVIATIONS FROM OSAP:
  - min_samples: OSAP's rolling_std(36, min_samples=24) floor is NOT
    reproduced; the full 36-month window is required (decision volume_windows,
    extending momentum_partial_windows to volume windows), so names with 24-35
    months are NaN and the first scorable signal is 2000-12, not 1999-12.
  - crsp.vol: as-traded volume is rebuilt as SEP.volume x close / closeunadj
    (SEP.volume is split-restated). This avoids the split look-ahead that
    restated volume carries in a raw-shares signal. Residual: massive reverse
    splits (close/closeunadj > 1000) lose shares in the vendor restatement and
    can show spurious low-volume months for a handful of names; closeunadj > 0
    is the only guard.
  - crsp.vol: SEP.volume is consolidated; CRSP NASDAQ volume before 2004 double
    counts dealer-to-dealer trades, so the LEVEL differs by exchange mix.
  - window: 36 CALENDAR months, not 36 rows of the permno's own monthly panel.
  - SignalDoc's exchcd == 1 (NYSE only) filter is not in predictor.py and is not
    applied; the harness universe decides.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef
from harness.data_layer import market_trading_calendar

_MONTHS = 36            # calendar months t-35 .. t
_DAYS_BACK = 1150       # 36 calendar months (<= ~1100 days) plus margin


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
    wide = monthly.unstack("m").reindex(columns=window)       # ID x 36 months
    full = wide.notna().all(axis=1)
    val = wide.std(axis=1, ddof=1).where(full)                # full window required
    val = val.where(np.isfinite(val) & (val > 0))
    return val.reindex(ctx.ids)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="VolSD",
    col="f_volsd",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: high volume variability predicts low returns
    weight=1.0,
    inputs=("SEP.close", "SEP.closeunadj", "SEP.volume"),
    osap_acronym="VolSD",
    source="Chordia, Subrahmanyam and Anshuman 2001 (Journal of Financial Economics)",
    history_months=35,              # full 36-month window: a price at the month t-35 end (harness gate)
    lookback_months=36,             # calendar months t-35..t
    notes="sample std (ddof 1) of monthly AS-TRADED share volume (volume x close / closeunadj) over calendar months t-35..t, all 36 required; zero std NaN",
    field_mappings=(
        ("crsp.vol (as traded, unadjusted)", "SEP.volume x SEP.close / SEP.closeunadj, summed by calendar month",
         "SEP.volume is split-restated; the close/closeunadj ratio undoes it per day (removes a split look-ahead in raw shares); reverse-split tail can lose shares; consolidated volume vs CRSP exchange volume (NASDAQ dealer double count pre-2004)"),
        ("rolling_std(36, min_samples=24) over panel rows", "std(ddof=1) over calendar months t-35..t, all 36 required",
         "OSAP's min-24 floor not reproduced (decision volume_windows); calendar months not panel rows; first scorable signal 2000-12"),
        ("SignalDoc exchcd == 1", "harness universe", "not in predictor.py; not applied"),
    ),
)
