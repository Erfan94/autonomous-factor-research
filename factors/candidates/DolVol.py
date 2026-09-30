"""
DolVol — log dollar trading volume of the calendar month two months before the
signal month; a stock that trades heavily in dollar terms is liquid, and
liquidity is predicted to be rewarded with a LOWER return.

OSAP: DolVol, Brennan, Chordia and Subrahmanyam 1998, Journal of Financial
Economics (Table 6A). Predicted sign: - (high dollar volume earns low returns).
Spec: osap_source/cache/b4e911e6/DolVol/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  Target month = the calendar month two months before the signal month
  (signal month t -> month t-2; a fixed two-month skip, fully observed).
  Daily SEP rows (close, volume) for the universe are sorted by date per ID and
  restricted to that calendar month. For each ID:
    monthly share volume = sum of SEP.volume over the month;
    month-end price      = SEP.close on the month's last trading-day row;
    dollar volume        = monthly share volume x month-end price;
    DolVol               = log(dollar volume), after dollar volume > 0.
  SEP.volume and SEP.close are both restated to today's split basis, so their
  product is split-invariant; closeunadj is never paired with volume. No SF1
  input, so no dimension and no ART/ARQ question. history_months=2: the
  harness nulls a name with no price near the month-(t-2) end, so a name that
  did not trade at t-2 is never scored (a name listing inside month t-2 keeps
  its partial-month volume, as CRSP's monthly vol would). The window is
  fetched as 100 calendar days back from the signal date, which covers all
  of month t-2 (at most about 92 days).

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? A name with no trading all of
  month t-2 has either no rows (listed later, NaN) or rows with volume 0 and a
  carried-forward price, whose dollar volume is exactly 0. The log of 0 is
  undefined, so these are set to NaN, not -inf and not a floor.
  What share of the universe does nothing? Expected ~0% of universe members
  (the membership band requires a positive trailing dollar volume); the spec's
  probe shows 0 zero-volume names in month t-2, about 1% of names with no t-2
  row (listed after it), mode share 0.04-0.06% and >= 99.5% distinct values.
  Preflight decides.
  Tie handling: null. Non-positive dollar volume becomes NaN and blend_ranks
  renormalises over the remaining signals; nothing is floored. The signal is
  continuous, so no mass point is expected.

DEVIATIONS FROM OSAP:
  - crsp.vol: CRSP monthly volume is the exchange's monthly total, and NASDAQ
    volume before 2004 counts dealer-to-dealer trades (double counting). SEP
    volume is the vendor's consolidated daily volume summed over the month, so
    the exchange mix of the level differs from CRSP's; the formula is the same.
  - crsp.prc: OSAP's prc is the month's last price, or the bid/ask mean when a
    month's last day had no trade. SEP.close on the last row carries the last
    trade price forward on a no-trade day; there is no bid/ask mean.
  - no-trade month: CRSP has no row; SEP may hold volume-0 rows. Both end as
    NaN here (dollar volume 0 is dropped, OSAP would return log(0) = -inf).
  - lag: OSAP shifts two ROWS of a permno's monthly panel, which skips a
    missing month; here the lag is two CALENDAR months, so a name with a gap
    at t-2 is NaN instead of picking up an older month.
  - the snapshot's first month (1997-12, a one-day stub) is never used as a
    target month; the first decision month's t-2 is 1998-10, fully inside SEP.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef

_DAYS_BACK = 100        # month t-2 starts at most ~92 days before the signal date
_SKIP_MONTHS = 2        # OSAP DolVol uses month t-2


def _compute(ctx):
    target = ctx.signal_asof.to_period("M") - _SKIP_MONTHS
    if target in ctx.partial_months("SEP"):
        return pd.Series(dtype=float)
    d = ctx.daily("SEP", ["close", "volume"], _DAYS_BACK)
    if d.empty:
        return pd.Series(dtype=float)
    d = d[d["date"].dt.to_period("M") == target]
    if d.empty:
        return pd.Series(dtype=float)
    d = d.sort_values(["ID", "date"], kind="mergesort")

    g = d.groupby("ID")
    share_vol = g["volume"].sum().astype(float)
    month_end_px = g["close"].last().astype(float)
    dollar_vol = share_vol * month_end_px
    return np.log(dollar_vol.where(dollar_vol > 0))


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="DolVol",
    col="f_dolvol",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: high dollar volume predicts low returns
    weight=1.0,
    inputs=("SEP.close", "SEP.volume"),
    osap_acronym="DolVol",
    source="Brennan, Chordia and Subrahmanyam 1998 (Journal of Financial Economics)",
    history_months=2,               # price must exist at the month t-2 end (harness gate)
    lookback_months=3,              # calendar month t-2 is read, within 100 days of the signal
    notes="log(monthly share volume x month-end close) of calendar month t-2; non-positive dollar volume NaN",
    field_mappings=(
        ("crsp.vol", "SEP.volume", "sum of daily consolidated volume over the month, split-restated; CRSP NASDAQ volume pre-2004 includes dealer double counting, so the level differs by exchange mix"),
        ("crsp.prc", "SEP.close", "last trading-day close of the month on the same split basis as volume (never closeunadj); no bid/ask-mean fallback, a no-trade day carries the last price"),
        ("shift(2) rows", "calendar month t-2", "two calendar months, not two panel rows; a gap at t-2 is NaN"),
        ("log(0) = -inf", "NaN", "non-positive dollar volume nulled, not floored"),
    ),
)
