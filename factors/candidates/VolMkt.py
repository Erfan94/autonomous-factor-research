"""
VolMkt — volume to market equity: the 12-month average of monthly dollar
trading volume divided by the current market capitalisation; a stock that
turns over a large share of its value in dollar terms is predicted to earn a
LOWER return.

OSAP: VolMkt, Haugen and Baker 1996, Journal of Financial Economics (Table 1).
Predicted sign: - (SignalDoc Sign = -1: high volume / market cap -> low
returns), so ascending=False (HIGH raw is the short leg).
Spec: osap_source/cache/b4e911e6/VolMkt/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  Daily SEP rows (close, volume) for the universe over the 12 CALENDAR months
  t-11 .. t (the signal month included, read in full), restricted to the market
  trading calendar (harness market_trading_calendar applied to the universe's
  own SEP dates, so a stray weekend/holiday row never enters a month), with the
  1997-12 snapshot-start stub month (ctx.partial_months("SEP")) dropped. For
  each ID and month m with at least one row:
    monthly share volume = sum of SEP.volume over the month (zero counts);
    month-end price      = SEP.close on the month's last trading-day row;
    dollar volume_m      = monthly share volume x month-end price.
  mean12 = mean of dollar volume_m over the observed months, required to have
           AT LEAST 10 of the 12 (OSAP's rolling_mean min_samples=10;
           decision volume_windows: VolMkt follows OSAP's floor).
  VolMkt = mean12 / ctx.universe["mkt_cap_usd"], cap guarded > 0.
  SEP.volume and SEP.close are both restated to today's split basis, so their
  product is a split-invariant dollar volume; closeunadj is never paired with
  volume. The market cap is DAILY.marketcap at the signal month-end (OSAP's
  month-t mve_c), in raw USD like the numerator, so the ratio is dimensionless.
  No SF1 input, so no dimension and no ART/ARQ question. history_months=9: the
  harness nulls a name with no price near the month t-9 end, so a name is
  scored only with 10 months of price history, which is exactly what the
  min-10 rule needs (the compute enforces the 10-observed-month count itself).

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? A name with volume 0 in every
  observed month gives mean12 = 0 and VolMkt = 0; a name with no SEP rows in a
  month has a missing month, not a zero.
  What share of the universe does nothing? ~0%. The spec measured, on 11 probe
  months (1998-12 .. 2021-11), no exact-zero or negative value, a modal share of
  0.043-0.058% of scored names (a single tie), and distinct values equal to the
  scored names (1,710-2,346), with 10 qcut bins everywhere. Preflight decides.
  Tie handling: null. A non-positive VolMkt (zero volume throughout) is set NaN
  and blend_ranks renormalises; nothing is floored.

DEVIATIONS FROM OSAP:
  - crsp.shrout: OSAP's mve_c = shrout x |prc| is the share-CLASS market cap
    and the volume is that class's; ctx.universe["mkt_cap_usd"] is the
    COMPANY-level cap (all classes) while the volume is one ticker's, so a
    multi-class issuer reads low. Not measured.
  - crsp.vol: SEP.volume is the vendor's consolidated daily volume summed over
    the month; CRSP NASDAQ volume before 2004 double counts dealer-to-dealer
    trades, so the LEVEL differs by exchange mix (ranks are formed within sector).
  - crsp.prc: SEP.close on the month's last row carries the last trade price
    forward on a no-trade day; there is no bid/ask mean.
  - window: 12 CALENDAR months t-11..t, not 12 rows of the permno's own monthly
    panel (a gap month is missing here, not skipped).
  - SignalDoc's abs(prc) > 5 portfolio filter is not in OSAP's predictor.py and
    is not applied; the harness universe decides.
  - the 1997-12 one-day stub month is dropped from the count (never reached:
    the first window is 1998-01..1998-12).
  - history_months=9 (not the full 12) follows from the min-10 floor.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef
from harness.data_layer import market_trading_calendar

_MONTHS = 12            # calendar months t-11 .. t
_MIN_MONTHS = 10        # OSAP rolling_mean min_samples
_DAYS_BACK = 400        # 12 calendar months (<= ~366 days) plus margin


def _compute(ctx):
    month = ctx.signal_asof.to_period("M")
    window = pd.period_range(month - (_MONTHS - 1), month, freq="M")
    d = ctx.daily("SEP", ["close", "volume"], _DAYS_BACK)
    if d.empty:
        return pd.Series(dtype=float)
    cal = market_trading_calendar(d["date"])             # trading days, stray rows excluded
    d = d[d["date"].isin(cal)]
    d = d[d["close"].astype(float) > 0]
    d = d.assign(m=d["date"].dt.to_period("M"))
    d = d[d["m"].isin(window) & ~d["m"].isin(ctx.partial_months("SEP"))]
    if d.empty:
        return pd.Series(dtype=float)
    d = d.sort_values(["ID", "date"], kind="mergesort")

    g = d.groupby(["ID", "m"])
    share_vol = g["volume"].sum(min_count=1).astype(float)   # month with rows but all-NaN volume -> missing
    month_end_px = g["close"].last().astype(float)
    dollar_vol = (share_vol * month_end_px).dropna()         # zero is an observation, a missing month is not

    by_id = dollar_vol.groupby(level=0)
    mean12 = by_id.mean().where(by_id.count() >= _MIN_MONTHS)

    cap = ctx.universe["mkt_cap_usd"].astype(float)
    cap = cap.where(cap > 0)
    val = mean12 / cap.reindex(mean12.index)
    val = val.replace([np.inf, -np.inf], np.nan)
    return val.where(val > 0)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="VolMkt",
    col="f_volmkt",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: high volume / market cap predicts low returns
    weight=1.0,
    inputs=("SEP.close", "SEP.volume"),
    osap_acronym="VolMkt",
    source="Haugen and Baker 1996 (Journal of Financial Economics)",
    history_months=9,               # price at the month t-9 end = 10 months of history (min-10 floor)
    lookback_months=12,             # 12 calendar months t-11..t
    notes="mean over calendar months t-11..t (>= 10 observed) of monthly sum(volume) x month-end close, / ctx.universe mkt_cap_usd; dollar volume split-invariant",
    field_mappings=(
        ("crsp.vol", "SEP.volume",
         "sum of daily consolidated volume over the calendar month, split-restated; CRSP NASDAQ volume pre-2004 includes dealer double counting, so the level differs by exchange mix"),
        ("crsp.prc (abs)", "SEP.close",
         "last trading-day close of the month on the same split basis as volume (never closeunadj); no bid/ask-mean fallback, a no-trade day carries the last price"),
        ("shrout x |prc| (share-class mve_c)", "ctx.universe['mkt_cap_usd']",
         "DAILY.marketcap at the signal month-end: COMPANY-level (all share classes) while the volume is one ticker's, so multi-class issuers read low; guarded > 0"),
        ("rolling_mean(12, min_samples=10) over panel rows", "calendar months t-11..t, >= 10 observed",
         "calendar months not panel rows; a gap month is missing; 1997-12 stub dropped"),
        ("SignalDoc abs(prc) > 5", "harness universe", "portfolio filter, not in predictor.py; not applied"),
    ),
)
