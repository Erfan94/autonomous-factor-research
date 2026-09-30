"""
High52 — the month-end price relative to the highest daily close of the prior twelve
months: a stock near its 52-week high keeps earning (anchoring on the high).

OSAP: High52, George and Hwang 2004, Journal of Finance (Table 1). Predicted sign: +
(SignalDoc Sign = +1: nearer the 52-week high, higher return; ascending=True).
Spec: osap_source/cache/b4e911e6/High52/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  Daily SEP.closeunadj (the RAW price, as the pinned code's "absolute price without split
  adjustment": dailyCRSP prc, never divided by cfacpr) for the universe, grouped by
  calendar month per ID:
    numerator   = the last closeunadj row of the signal month t
    denominator = the maximum over the 12 calendar months t-12 .. t-1 of each month's
                  maximum daily closeunadj (the current month is EXCLUDED; months in which
                  the ID has no row are skipped, max over the months present)
    High52      = numerator / denominator   (denominator > 0 guarded)
  The ratio can exceed 1 (a new 52-week high in month t, about 15% of the universe on
  average); no cap. Daily CLOSE maxima, not intraday highs (SEP.high is not used). SEP
  carries a row on no-trade days (price carried forward), as CRSP dsf does; they are not
  filtered. The 1997-12 snapshot-start stub month is dropped from the window through
  ctx.partial_months("SEP") (the first signal month then sees 11 full prior months).
  No minimum-history rule of its own (OSAP's max skips NaN, so one prior month is enough);
  history_months=12 is the harness's price-at-lag-12 gate, a stricter sample for young
  listings (spec: 3.4% of rows have 1-11 prior months). No SF1 input: no ART/ARQ question.
  Split basis: a split INSIDE the 13-month window drops the raw ratio by the split factor
  for about 12 months (an OSAP artefact, reproduced). The split-restated SEP.close would
  reproduce the SignalDoc's "prc/cfacshr" wording and be invariant to such splits; it is
  the declared alternative construction, NOT used here.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? A name whose daily close is flat for 13
  months (for example a pending-deal stock) gives exactly 1.0, a name at its high in month
  t with an equal prior max likewise.
  What share of the universe does nothing? Spec measured on the harness universe, all 276
  signal months: exactly 1.0 averages 0.10% (max 0.53% at 1998-12); cross-section modal
  share mean 0.14%, max 0.53%; 0 months at or above 5% or the 10% cliff; 10 qcut bins
  every month; 1,733-2,794 distinct values. Preflight re-measures it.
  Tie handling: none needed; the average rank the harness applies covers the few exact
  ties. Nothing is removed, nulled or floored. The only guard is denominator > 0.

DEVIATIONS FROM OSAP:
  - Price basis: SEP.closeunadj is the vendor's unadjusted close, the counterpart of CRSP
    raw prc. No negative-price (bid/ask average) convention in SEP, so there is no abs().
  - Window: the 12 preceding CALENDAR months; OSAP shifts 12 ROWS of a permno's monthly
    panel, which reaches further back when a month has no CRSP row (rare).
  - 1997-12 stub dropped from the prior-month maxima (snapshot start): the 1998-12 signal
    has 11 full prior months, every later one has 12 (subject to the firm's own history).
  - history_months=12: the harness nulls a name with no price near the month-(t-12) end,
    stricter than OSAP's "at least one prior month".
  - Sharadar METRICS.high52w is not used (current snapshots only, not a history, and not
    OSAP's construction).
  - Holding design (OSAP Portfolio Period 6) is not reproduced: the harness holds one month.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef

_WINDOW_MONTHS = 12     # prior calendar months whose maxima form the denominator
_DAYS_BACK = 410        # month t-12 starts at most ~400 days before the signal date


def _compute(ctx):
    cur = ctx.signal_asof.to_period("M")
    d = ctx.daily("SEP", ["closeunadj"], _DAYS_BACK)
    if d.empty:
        return pd.Series(dtype=float)
    d = d.sort_values(["ID", "date"], kind="mergesort")
    d = d.assign(per=d["date"].dt.to_period("M"))
    d = d[d["per"] >= cur - _WINDOW_MONTHS]
    partial = ctx.partial_months("SEP")
    if partial:
        d = d[~d["per"].isin(partial)]       # the one-day snapshot-start stub is not a month

    now = d[d["per"] == cur]
    if now.empty:
        return pd.Series(dtype=float)
    numer = now.groupby("ID")["closeunadj"].last().astype(float)

    prior = d[d["per"] < cur]
    if prior.empty:
        return pd.Series(dtype=float)
    monthly_max = prior.groupby(["ID", "per"])["closeunadj"].max().astype(float)
    denom = monthly_max.groupby(level="ID").max()     # max over months present; current month excluded

    ratio = numer / denom.reindex(numer.index).where(lambda s: s > 0)
    return ratio.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="High52",
    col="f_high52",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: a price near its 52-week high earns more
    weight=1.0,
    inputs=("SEP.closeunadj",),
    osap_acronym="High52",
    source="George and Hwang 2004 (Journal of Finance)",
    history_months=12,              # return-window signal: price must exist at the month t-12 end (harness gate)
    lookback_months=13,             # 12 prior calendar months plus the signal month of daily closes
    notes="last closeunadj of month t over the max of the prior 12 monthly maxima of daily closeunadj (current month excluded); raw price as OSAP",
    field_mappings=(
        ("crsp.prc.abs() (dailyCRSP, raw)", "SEP.closeunadj",
         "raw price as the pinned code states; a split inside the 13-month window scales the ratio by the split factor for ~12 months (OSAP artefact). Declared alternative, not used: SEP.close (split-restated), rank rho 0.94 mean vs this"),
        ("groupby permno, calendar month: max and last of prc", "max and last of closeunadj per calendar month",
         "SEP carries a row on no-trade days, as dsf does; daily close, never intraday SEP.high"),
        ("shift(1..12) by row, max(axis=1, skipna)", "12 preceding calendar months, max over months present",
         "calendar window, not panel rows (differs only when a month has no row); no minimum-history rule inside the factor"),
        ("(no minimum history)", "history_months=12 (harness gate)",
         "stricter than OSAP's at-least-one-prior-month: drops young listings with 1-11 prior months (~3.4% of rows)"),
        ("1997-12 start", "ctx.partial_months('SEP') drop",
         "the one-day stub month is excluded from the prior maxima; first signal has 11 full prior months"),
    ),
)
