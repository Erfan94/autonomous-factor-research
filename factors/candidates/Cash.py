"""
Cash — cash and short-term investments relative to total assets (asset
composition); a cash-rich balance sheet is predicted to earn HIGHER returns.

OSAP: Cash, Palazzo 2012, Journal of Financial Economics. Predicted sign: +
(SignalDoc Sign = +1: high value, high return).
Spec: osap_source/cache/b4e911e6/Cash/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  che  = SF1.cashneq + SF1.investmentsc.fillna(0)    (ART level)
  Cash = che / SF1.assets, on rows with assets > 0, from the latest filing
  known at the signal date. Both inputs are balance-sheet levels in the same
  reporting currency, so the ratio is unit-free and needs no fxusd gate.
  Guards: assets <= 0 -> NaN; cashneq null -> NaN (see below); non-finite -> NaN.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? A firm with no new filing
  carries its last ratio (piecewise constant in time) but the value is
  continuous across firms in [0, 1]-ish; there is no default value and the
  ratio is not zero-filled.
  What share of the universe sits at one value? The only exact tie is
  che == 0, about 0.2-1% of non-null rows, far below a decile; preflight to
  confirm the measured mode share.
  Tie handling: null where cashneq is missing (0.04%) and where assets <= 0;
  exact zeros are left as real values and tie at the bottom (average rank by
  the harness).

DEVIATIONS FROM OSAP:
  - cheq: SF1.cashneq + investmentsc.fillna(0). Overshoots for vendor and
    captive-finance filers (investmentsc holds current financing receivables)
    and understates for the ~20% unclassified-balance-sheet block (mostly
    financials/REITs; investmentsc null there, so che = cashneq). cashneq
    alone is never used.
  - OSAP zero-fills a missing cheq to 0; here a missing cashneq (0.04% of
    rows) stays NaN, because a fabricated 0 would be a bottom-decile outlier.
    investmentsc null IS treated as 0, which is a real zero for classified
    balance sheets.
  - timing: latest ART filing with datekey <= signal date (filing date, later
    than rdq by days to weeks), capped at max_fundamental_age_months = 15; OSAP
    holds a quarter for exactly 3 months from rdq. Levels only, so ART equals
    ARQ and the ART default is kept.
  - OSAP's shrcd/exchcd sample and raw cross-section sort are replaced by the
    harness universe and within-sector ranks (harness-owned).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    f = ctx.fundamentals(["assets", "cashneq", "investmentsc"])
    assets = f["assets"].astype(float)
    cashneq = f["cashneq"].astype(float)
    # che = cash + short-term investments; null investmentsc is a real zero on
    # classified balance sheets. A null cashneq stays null (not zero-filled).
    che = cashneq + f["investmentsc"].astype(float).fillna(0.0)
    out = che / assets.where(assets > 0)
    return out.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="Cash",
    col="f_cash",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: HIGH cash/assets is attractive
    weight=1.0,
    inputs=("SF1.assets", "SF1.cashneq", "SF1.investmentsc"),
    osap_acronym="Cash",
    source="Palazzo 2012 (Journal of Financial Economics)",
    lookback_months=15,             # latest filing within max_fundamental_age_months
    notes="(cashneq + investmentsc.fillna(0)) / assets; null cashneq stays NaN (OSAP zero-fills)",
    field_mappings=(
        ("compustat.cheq", "SF1.cashneq + SF1.investmentsc.fillna(0) (ART)",
         "approx: overshoots for captive-finance filers (financing receivables in investmentsc); understates for the ~20% unclassified block (financials/REITs, che = cashneq)"),
        ("compustat.cheq zero-fill", "none",
         "OSAP zero-fills missing cheq to 0; here null cashneq stays NaN (0.04% of rows)"),
        ("compustat.atq", "SF1.assets (ART)",
         "require > 0; none material"),
        ("compustat.rdq", "SF1.datekey (latest filing <= signal date)",
         "filing date later than rdq; no 3-month expiry, capped at 15 months by the harness"),
    ),
)
