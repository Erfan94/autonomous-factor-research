"""
AnnouncementReturn -- four-day market-adjusted return around the most recent earnings announcement.

OSAP: AnnouncementReturn, Chan, Jegadeesh and Lakonishok 1996 (Journal of Finance). Predicted sign: +.
Spec: osap_source/cache/b4e911e6/AnnouncementReturn/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  Announcement date = the EVENTS row whose eventcodes contain '22' (8-K Item 2.02,
  results of operations). Option B: EVENTS only, NO SF1 datekey fallback, so the
  signal is NaN before the first code-22 row (2004-08-23) and for any quarter with
  no code-22 8-K. A code-22 row within 10 calendar days of the cluster's FIRST kept row
  (an amendment) is dropped; the earliest of the cluster is the announcement.
  Daily excess return r_d = closeadj[d]/closeadj[d-1] - 1 (consecutive SEP rows of
  the name) minus ctx.market_daily (raw value-weighted market; OSAP's mktrf + rf, in
  which rf cancels). Window = the name's SEP rows ann-2, ann-1, ann, ann+1 (four
  trading days, per the pinned OSAP code; the SignalDoc text says -1..+2), ARITHMETIC
  sum of r_d. The announcement date must itself be a SEP row for the name, else the
  quarter is dropped (no shifting). Only windows whose last day ann+1 <= signal_asof
  exist (the daily frame is bounded by the signal). The value is the most recent
  such window whose last day falls in the signal month or the 5 months before it
  (OSAP: stamped at the last window day's month, carried 0-6 months = ages 0..6).

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? NaN (no announcement window closed in
    the last 7 months); never a zero default. A no-trade name gets minus the market sum,
    a continuous value, not a zero.
  What share of the universe does nothing? Expected ~25-30% of quarters unmatched by
    code 22 and 100% before 2004-08; preflight measures the universe share.
  Tie handling: null. The value is a sum of four returns less four market returns, so
    exact ties are ~0%; a stale carried value ranks like a fresh one (staleness 0..6 months).

DEVIATIONS FROM OSAP:
  - rdq: EVENTS code 22 8-K filing date (up to a few business days after the release,
    ann-2 usually still covers it); no SF1 datekey fallback; NaN for 1999-01..2004-07.
  - The Compustat hygiene rule (rdq within 6 months of quarter end) and (gvkey, fyearq,
    fqtr) dedupe are not reproduced: no SF1 read; the 10-day cluster dedupe stands in.
  - mktrf + rf: Sharadar value-weighted market (market_daily), raw, prior-day cap weights,
    bad-print guards; no delisting return; closeadj quantises sub-$0.50 returns.
  - Ticker identity instead of the CCM link; harness universe instead of no filter.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef

_DAYS_BACK = 240          # ~9.5 months of SEP rows: covers a 7-month carry plus the window's pre-days
_EVENT_MONTHS = 8         # one month beyond the carry so the dedupe sees the cluster start at the far edge
_CARRY_MONTHS = 7         # window stamp month in [t-6m, t]: ages 0..6 months (OSAP carries 0-6)
_CLUSTER_DAYS = 10


def _compute(ctx):
    ev = ctx.events(_EVENT_MONTHS)
    if ev.empty:
        return pd.Series(dtype=float)
    codes = ev["eventcodes"].fillna("").astype(str).str.split("|")
    ev = ev.loc[codes.map(lambda c: "22" in c)]
    if ev.empty:
        return pd.Series(dtype=float)
    ev = ev[["ID", "date"]].drop_duplicates().sort_values(["ID", "date"])
    # amendment dedupe: keep a row only if >= _CLUSTER_DAYS after the LAST KEPT row (the
    # cluster's first), so rows at days 0, 8, 16 keep days 0 and 16, not one row
    keep = np.zeros(len(ev), dtype=bool)
    last_id, last_kept = None, None
    for i, (eid, d) in enumerate(zip(ev["ID"].to_numpy(), ev["date"].to_numpy())):
        if eid != last_id or (d - last_kept) >= np.timedelta64(_CLUSTER_DAYS, "D"):
            keep[i] = True
            last_id, last_kept = eid, d
    ev = ev[keep]

    px = ctx.daily("SEP", ["closeadj"], _DAYS_BACK)
    if px.empty:
        return pd.Series(dtype=float)
    px = px.sort_values(["ID", "date"]).drop_duplicates(["ID", "date"]).reset_index(drop=True)
    px["closeadj"] = px["closeadj"].astype(float)
    px["closeadj"] = px["closeadj"].where(px["closeadj"] > 0)
    g = px.groupby("ID", sort=False)
    ret = px["closeadj"] / g["closeadj"].shift(1) - 1.0
    mkt = ctx.market_daily(_DAYS_BACK)
    ex = ret - px["date"].map(mkt)           # NaN where the market or a price is missing

    # rows ann-2, ann-1, ann, ann+1 of the name's own SEP sequence; NaN propagates
    px["_ex"] = ex
    g = px.groupby("ID", sort=False)["_ex"]
    px["ar"] = g.shift(2) + g.shift(1) + px["_ex"] + g.shift(-1)
    px["end"] = px.groupby("ID", sort=False)["date"].shift(-1)

    m = px.merge(ev.rename(columns={"date": "ann"}), left_on=["ID", "date"],
                 right_on=["ID", "ann"], how="inner")          # ann must be a SEP row
    m = m.dropna(subset=["ar", "end"])
    if m.empty:
        return pd.Series(dtype=float)
    end_m = m["end"].dt.to_period("M")
    now_m = pd.Timestamp(ctx.signal_asof).to_period("M")
    age = (now_m - end_m).map(lambda k: k.n)
    m = m[(age >= 0) & (age < _CARRY_MONTHS)]
    if m.empty:
        return pd.Series(dtype=float)
    m = m.sort_values(["ID", "end"])
    return m.groupby("ID")["ar"].last().astype(float)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="AnnouncementReturn",
    col="f_annret",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: high announcement return predicts high return
    weight=1.0,
    inputs=("SEP.closeadj", "DAILY.marketcap", "EVENTS.eventcodes"),
    osap_acronym="AnnouncementReturn",
    source="Chan, Jegadeesh and Lakonishok 1996 (Journal of Finance)",
    lookback_months=8,              # anchor up to 6 months back, plus the window's pre-days and the event-fetch margin
    # history_months=1: the project rule requires a declared gate on any return-window factor.
    # The window needs only ~4 consecutive SEP rows (ann-2..ann+1), which exist for any name
    # listed a few weeks; OSAP has no listing-age gate. 1 is the smallest meaningful gate
    # (price within 7 days of signal - 1 month); a longer gate would drop real recent listings.
    history_months=1,
    notes="sum over SEP rows ann-2..ann+1 of (ret - VW market); ann = EVENTS code 22 only; latest window ages 0..6m",
    field_mappings=(
        ("rdq", "EVENTS.eventcodes contains '22' (date)", "8-K Item 2.02 filing date, not Compustat rdq; NO SF1 datekey fallback; NaN before 2004-08-23 and for ~27% of quarters"),
        ("ret", "SEP.closeadj day-over-day", "consecutive SEP rows; no delisting return; 3-decimal grid quantises sub-$0.50 returns; no-trade days carry the price (return 0)"),
        ("mktrf + rf", "ctx.market_daily (raw VW, DAILY.marketcap weights)", "rf cancels exactly; Sharadar all-stock VW with bad-print guards, not CRSP VW; starts 1998-12-02"),
        ("ccm link", "ticker identity", "EVENTS/SEP ticker map instead of gvkey-permno link"),
        ("rdq hygiene", "none", "no ann-minus-quarter-end <= 6 months check (no SF1 read); 10-day cluster dedupe of code-22 rows instead"),
    ),
)
