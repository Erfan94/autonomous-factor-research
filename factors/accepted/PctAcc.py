"""
PctAcc — percent operating accruals: income before extraordinary items less
operating cash flow, scaled by the ABSOLUTE value of income; high percent
accruals are predicted to earn lower returns.

OSAP: PctAcc, Hafzalla, Lundholm and Van Winkle 2011, The Accounting Review
(Table 4A). Predicted sign: - (SignalDoc Sign = -1, so ascending=False).
Spec: osap_source/cache/b4e911e6/PctAcc/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  OSAP: (ib - oancf) / abs(ib), with ib == 0 divided by 0.01; where oancf is
  missing, a balance-sheet accrual (d act - d che - (d lct - d dlc) - d txp - dp)
  replaces the numerator.
  Sharadar, SF1 ART (trailing four quarters, as filed), one ctx.fundamentals call:
      ib    = netinc + netincdis      (PLUS: netincdis carries the opposite sign
                                       to the income it describes, so the sum is
                                       income before discontinued operations)
      oancf = ncfo                    (TTM flow, inflow-positive)
      score = (ib - oancf) / abs(ib), NaN where ib == 0
  Numerator and denominator are flows of the SAME trailing year in one ratio:
  no year-over-year difference, nothing to smear, so ART is the right dimension
  (no override). The ratio is unit-free, so non-USD reporting currency
  (fxusd != 1) is NOT gated.
  Raw value is PctAcc; ascending=False makes a LOW value the long side. The
  ratio is heavy-tailed where |ib| is small: ranks (and the harness
  winsorisation), never a z-score.

NULL HANDLING:
  - ib: netinc or netincdis null -> NaN (OSAP does not fill ib).
  - oancf: null -> NaN (OSAP does not fill oancf; there it routes to the
    balance-sheet fallback, not reproduced, see DEVIATIONS).
  - ib == 0 -> NaN (see mass-point design); non-finite -> NaN.
  - No balance-sheet item is read, so financials and unclassified balance
    sheets stay scorable (OSAP has no sample filter on this signal either).

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? None: a do-nothing firm has no
  natural value, because ib and ncfo both change with every filing and the ratio
  is continuous. Exact hits are few: ncfo == 0 gives exactly +/-1 (0.055% of
  non-null ncfo); ncfo == ib gives exactly 0 (<= 0.16% of the universe); ib == 0
  is 0.00-0.11% of the universe.
  What share of the universe does nothing? Spec measurement on 264 months
  (1999-12-31..2021-11-30): distinct values equal the number of scored names,
  modal value share 0.037-0.168% (median 0.055%), coverage 84.9-99.6% of the
  universe (median 97.1%); 1998-12..1999-02 only 51.4-57.2% (ART needs four
  quarters of history).
  Tie handling: null. ib == 0 -> NaN, removing the only manufactured
  values (OSAP's divide-by-0.01 blow-up); blend_ranks renormalises; average
  rank for any residual ties.

DEVIATIONS FROM OSAP:
  - Balance-sheet fallback NOT reproduced: it is used by OSAP only where oancf is
    missing and needs txp, which Sharadar does not publish and OSAP does not
    zero-fill (a missing txp makes the OSAP fallback NaN). Names with null ncfo
    are NaN: 0.0-1.7% of the universe (median 0.3%) from 1999-12-31. A coverage
    loss on a separable branch; the primary branch is fully mapped.
  - ib = netinc + netincdis is approx: netinc is after non-controlling interest,
    and extraordinary items are not separable in SF1.
  - ib == 0 -> NaN, where OSAP divides by 0.01.
  - Timing: ART as of the filing date (refreshed quarterly, earnings 1-3 months
    old) replaces the annual fiscal year at datadate + 6 months.
  - SignalDoc quantile filter abs(prc) > 5 is portfolio-stage, not reproduced;
    the harness price floor is $1.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    f = ctx.fundamentals(["netinc", "netincdis", "ncfo"])
    ib = f["netinc"].astype(float) + f["netincdis"].astype(float)    # PLUS (sign trap)
    oancf = f["ncfo"].astype(float)                                   # null -> NaN
    den = ib.abs()
    score = (ib - oancf) / den.where(den > 0)                         # ib == 0 -> NaN
    return score.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    family="investment",                # Phase C, 2026-10-01: Cat.Economic "accruals" (decision phase_c_family_partition)
    name="PctAcc",
    col="f_pctacc",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: HIGH percent accruals earn LOWER returns
    weight=1.0,
    inputs=("SF1.netinc", "SF1.netincdis", "SF1.ncfo"),
    osap_acronym="PctAcc",
    source="Hafzalla, Lundholm and Van Winkle 2011 (The Accounting Review)",
    lookback_months=15,             # one ART filing, age-limited
    notes="(ib - ncfo) / |ib|, ib = netinc + netincdis, SF1 ART; ib == 0 NaN; balance-sheet fallback (txp) not reproduced",
    field_mappings=(
        ("compustat.ib", "SF1.netinc + SF1.netincdis (ART)",
         "approx: PLUS (netincdis sign inverted); after NCI, extraordinary items not separable; null -> NaN as OSAP"),
        ("compustat.oancf", "SF1.ncfo (ART)", "null -> NaN; OSAP would use the balance-sheet fallback there"),
        ("balance-sheet fallback (act, che, lct, dlc, txp, dp)", "not reproduced",
         "txp unavailable and not zero-filled in OSAP; ncfo-null names NaN (median 0.3% of universe)"),
        ("ib == 0 -> / 0.01", "NaN", "zero-income firms unscored instead of a manufactured +/-100x value"),
        ("fiscal year at datadate + 6 months", "ART as of datekey", "TTM as filed, refreshed quarterly, available earlier"),
        ("SignalDoc filter abs(prc) > 5", "not reproduced", "portfolio-stage; harness price floor is $1"),
    ),
)
