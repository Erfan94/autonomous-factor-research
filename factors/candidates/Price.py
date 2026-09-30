"""
Price — log of the raw as-traded stock price; low-priced stocks are predicted
to earn higher returns (a size / lottery-like trait).

OSAP: Price, Blume and Husic 1973, Journal of Finance (Table 2 column c).
Predicted sign: - (SignalDoc Sign = -1).
Spec: osap_source/cache/b4e911e6/Price/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  score = ln(SEP.closeunadj) on the last trading day of the signal month
  (ctx.at_month_end("SEP", ["closeunadj"], 0): the last SEP row on or before the
  business month-end, at most 7 calendar days earlier). closeunadj is the
  as-traded price, exactly what OSAP's CRSP prc is: OSAP never applies cfacpr,
  so the level is NOT split-restated. SEP.close / closeadj are NOT used (today's
  split basis, or dividend-adjusted, would make the level depend on the snapshot
  date). Price-only: no filing date, no ART/ARQ choice, nothing to smear.
  Guard: the log is taken only where closeunadj > 0 (SEP has no non-positive
  closes; OSAP's abs() for CRSP's negative bid/ask midpoints is a no-op).

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Its price just keeps its own
  value; there is no zero and no do-nothing value.
  What share of the universe does nothing? n/a. Prices sit on a cent grid so
  pairwise ties occur, but no single value is a mass point: the spec measured a
  modal log-price share of 0.13-0.67% (median 0.21%; a round-dollar level that
  changes by month), 1,227-2,141 distinct values, ten qcut bins every month.
  Tie handling: average rank; no noise, no secondary key.

HISTORY: a signal-date price level reads one month-end close. No return window
  and no history gate is needed (no_history_gate_because below).

DEVIATIONS FROM OSAP:
  - closeunadj replaces CRSP prc; they agree except CRSP's bid/ask midpoint on a
    no-trade month-end (Sharadar carries the last close instead; immaterial).
  - The harness price >= $1 floor truncates the low-price tail that OSAP keeps
    (sub-$1 stocks, i.e. the extreme low-price decile of a log-price signal).
    The universe is the harness's and is not removable here.
  - Within-sector ranking and harness winsorisation replace OSAP's sort.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    d = ctx.at_month_end("SEP", ["closeunadj"], 0)
    px = d["closeunadj"].astype(float)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.log(px.where(px > 0))


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="Price",
    col="f_price",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: LOW price is attractive
    weight=1.0,
    inputs=("SEP.closeunadj",),
    osap_acronym="Price",
    source="Blume and Husic 1973 (Journal of Finance)",
    lookback_months=0,              # the signal-month-end close only
    no_history_gate_because=(
        "signal-date price level: reads only the signal month-end close "
        "(at_month_end, 7-day tolerance); no return window, so no name needs a "
        "price at any earlier month"),
    notes="ln(SEP.closeunadj) at the signal month-end (as-traded, not split-restated, as OSAP prc); $1 universe floor truncates the low tail",
    field_mappings=(
        ("crsp.prc (abs)", "SEP.closeunadj at the signal month-end via ctx.at_month_end",
         "as-traded price, same object; CRSP bid/ask midpoint on a no-trade month-end becomes the last close; abs() a no-op"),
        ("no price screen in OSAP", "harness price >= $1 universe floor",
         "sub-$1 stocks (the lowest log-price tail) are not in the harness universe"),
    ),
)
