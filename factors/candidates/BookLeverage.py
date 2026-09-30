"""
BookLeverage — total assets relative to book equity (Fama-French A/BE); a
highly levered firm (much asset base per dollar of book equity) is predicted
to earn LOWER returns, so the long leg is LOW book leverage.

OSAP: BookLeverage, Fama and French 1992, Journal of Finance (Table 3,
Ln(A/BE)). Predicted sign: - (SignalDoc Sign = -1: high value, low return).
Spec: osap_source/cache/b4e911e6/BookLeverage/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  BE = SF1.equity (ART; falls back to SF1.assets - SF1.liabilities where
       equity is null, ~0.05% of rows) + SF1.taxliabilities.fillna(0)
  BookLeverage = SF1.assets / BE, all from the latest filing known at the
  signal date. Raw ratio, no log (ln is monotone; ranks match the paper's
  Ln(A/BE)). All four inputs are balance-sheet levels in the same reporting
  currency, so the ratio is unit-free and needs no fxusd gate.
  Guards: assets <= 0 -> NaN (data-error rows); BE == 0 -> NaN; any
  non-finite result -> NaN. NO positivity filter on BE (see below).

NEGATIVE BOOK EQUITY (OSAP-faithful, deliberate):
  OSAP keeps firms with BE < 0, so their ratio assets/BE is NEGATIVE and is
  the LOWEST value in the cross-section (liabilities > assets on ~6% of ART
  rows). The orientation is ascending=False (a LOW raw value is attractive;
  the harness negates so low raw = top decile = long leg). Negative-BE firms
  therefore land on the LONG leg, ranked above every positive-BE firm, even
  though they are the most levered in economic terms. This is how the OSAP
  signal behaves; it is reproduced as is and not masked. A flipped-sign
  screen would be a second hypothesis (|t| >= 2.74 at Stage 1).

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? A firm with no new filing
  carries the same value from its last filing (the signal is piecewise
  constant in time) but it is continuous across firms; there is no default
  value and no zero-fill of the ratio. taxliabilities is a mass point in the
  INPUT (~51% exact zero in SF1, which OSAP also zero-fills) but is only a
  small additive term in BE, so the ratio stays continuous.
  What share of the universe sits at one value? ~0%; the only exact tie is
  equity + taxliabilities == 0 (~0.01%), set to NaN. Preflight to confirm.
  Tie handling: null (BE == 0, assets <= 0 become NaN and blend_ranks
  renormalises); otherwise harness default (average rank).

DEVIATIONS FROM OSAP:
  - pstk/pstkrv/pstkl: not in SF1. Preferred stock is not removed from book
    equity (ruling book_equity_preferred_terms): SF1.equity includes it, so
    the denominator is larger for preferred issuers than OSAP's common
    equity + txditc.
  - OSAP's "book equity missing when pstk, pstkrv and pstkl are all missing"
    gate cannot be reproduced: Compustat pstk is often blank for firms with
    no preferred, so OSAP's sample is narrower; here every firm with an
    equity (or assets and liabilities) figure is scored, so coverage is
    wider than OSAP's.
  - txditc: SF1.taxliabilities is a generic tax-liability line, not deferred
    taxes + ITC; zero-filled as OSAP zero-fills txditc (mixes true zeros with
    vendor imputation).
  - timing: latest ART filing with datekey <= signal date (0-3 months old,
    at most max_fundamental_age_months = 15), not OSAP's annual balance sheet
    + 6-month lag held 12 months (6-17 months old). The 6-month lag is not
    reproduced.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    f = ctx.fundamentals(["assets", "equity", "liabilities", "taxliabilities"])
    assets = f["assets"].astype(float)
    equity = f["equity"].astype(float)
    liabilities = f["liabilities"].astype(float)
    tax = f["taxliabilities"].astype(float).fillna(0.0)   # OSAP zero-fills txditc

    # OSAP tempSE chain: seq, else ceq (same SF1 column), else at - lt.
    se = equity.fillna(assets - liabilities)
    be = se + tax

    # Negative BE is KEPT (OSAP-faithful); only an exact-zero denominator is a
    # non-value. assets <= 0 is a data-error row.
    out = assets.where(assets > 0) / be.where(be != 0)
    return out.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="BookLeverage",
    col="f_booklev",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: LOW book leverage is attractive (negative-BE firms land long)
    weight=1.0,
    inputs=("SF1.assets", "SF1.equity", "SF1.liabilities", "SF1.taxliabilities"),
    osap_acronym="BookLeverage",
    source="Fama and French 1992 (Journal of Finance)",
    lookback_months=15,             # latest filing within max_fundamental_age_months
    notes="assets / (equity + taxliabilities); negative BE kept (OSAP), lands on the long leg under sign -1",
    field_mappings=(
        ("compustat.at", "SF1.assets (ART)",
         "latest filing (0-3 months old, capped at 15) vs OSAP annual + 6-month lag (6-17 months old); assets <= 0 -> NaN"),
        ("compustat.seq", "SF1.equity (ART)",
         "equity includes preferred (the seq concept); preferred NOT subtracted as OSAP does (no pstk/pstkrv/pstkl in SF1)"),
        ("compustat.ceq", "SF1.equity (ART)",
         "same column as seq; OSAP's ceq + pstk branch is dead here"),
        ("compustat.lt", "SF1.liabilities (ART)",
         "fallback only where equity is null (~0.05%): BE = assets - liabilities"),
        ("compustat.txditc", "SF1.taxliabilities (ART), fillna(0)",
         "generic tax-liability line, not deferred tax + ITC; ~51% exact zero (vendor zero-fill); OSAP also zero-fills"),
        ("compustat.pstk/pstkrv/pstkl", "none",
         "preferred not removed (ruling book_equity_preferred_terms); OSAP's all-preferred-missing NaN gate not reproduced, coverage wider than OSAP"),
    ),
)
