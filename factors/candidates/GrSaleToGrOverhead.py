"""
GrSaleToGrOverhead — sales growth minus overhead (SG&A) growth, each against a
two-year average base: a firm whose sales grow faster than its overhead is
gaining operating leverage.

OSAP: GrSaleToGrOverhead, Abarbanell and Bushee 1998, The Accounting Review
(Table 2b, RS&A). Predicted sign: + (SignalDoc Sign = +1: a HIGH value is the long side).
Spec: osap_source/cache/b4e911e6/GrSaleToGrOverhead/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  sale  = SF1.revenue (ART, trailing-twelve-month flow)
  xsga  = SF1.sgna + SF1.rnd.fillna(0)   (ART TTM), NaN where sgna is null or exactly 0
  Three values of each, aligned by REPORT PERIOD with ctx.fundamentals_yoy:
  latest (P), one year earlier (P-1y, years=1) and two years earlier (P-2y, years=2).
  The three ART windows are exactly four quarters apart and do not overlap, so each
  growth term is a clean annual change (no TTM smear); dimension stays ART.
    primary  = (sale - B_s)/B_s - (xsga - B_x)/B_x,   B = 0.5*(value[P-1y] + value[P-2y])
    fallback = (sale - sale[P-1y])/sale[P-1y] - (xsga - xsga[P-1y])/xsga[P-1y]
    score    = primary where it exists, else fallback (OSAP's rule).
  Primary is NaN when any of the four lagged values is missing or a base is not
  positive; the fallback then fires. Raw value, no winsorising (harness ranks within sector).

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0.0, but only if sales AND SG&A
  are identical at all three dates; a TTM flow that exact is essentially non-existent.
  What share of the universe does nothing? Spec measured a modal-value share of
  0.05-0.13% of the scored cross-section (n scored 777-2,165, distinct values ~= n).
  Zero SG&A is the one manufactured tie: sgna == 0 is a vendor zero-fill (2.5% of non-null
  ART rows, 2.7-5.9% of the universe) and OSAP does not zero-fill xsga, so it is NaN here,
  before any ratio. Zero (or non-positive) base -> NaN in both paths.
  Tie handling: null (sgna == 0 -> NaN; non-positive base -> NaN). No zero-fill and no
  floored denominator.

DEVIATIONS FROM OSAP:
  - xsga: Compustat xsga includes R&D and excludes D&A; SF1.sgna is the as-reported SG&A
    line, EXCLUDING R&D and INCLUDING D&A for filers that report D&A inside SG&A. The proxy
    is sgna + rnd (rnd is vendor-zero-filled, a true zero, so fillna(0)); embedded D&A is a
    level issue that largely cancels in a same-line growth rate, the cross-filer
    presentation switch is the residual risk. The field_map status is approx.
  - Base guard: OSAP nulls a term only where its base == 0; here a base <= 0 is NaN (a
    negative base flips the sign of the growth rate). Differs only where a two-year-average
    base of revenue or SG&A is negative (vendor data errors).
  - sgna == 0 nulled at each of the three dates separately (a zero at P-1y removes that
    date's growth term, as a zero xsga would be missing in OSAP).
  - Timing: OSAP uses annual fiscal-year records at datadate + 6 months; here the latest
    filed ART quarter and the same fiscal period one and two years earlier (report-period
    aligned). No extra reporting lag (datekey bounds the information).
  - Currency: reporting-currency ratios of the same firm's own values; the rate cancels.
  - Data start: the snapshot's SF1 begins 1997Q4 with partly populated early-1998 ART
    flows, so the primary exists from P = 1999Q4 and the 1999-2000 months lean on the
    fallback; coverage is below 40% at 1999-01 and 1999-02 (spec-measured 32.6% at 1999-01).
  - OSAP's annual June rebalance and any price filter are not reproduced (harness-owned).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _xsga(sgna, rnd):
    """sgna + rnd (rnd null is a true zero); NaN where sgna is null or exactly 0."""
    s = sgna.astype(float)
    return (s + rnd.astype(float).fillna(0.0)).where(s.notna() & (s != 0.0))


def _growth(x, base):
    """(x - base)/base, NaN unless base > 0 (a negative base is a sign flip)."""
    return (x - base) / base.where(base > 0)


def _compute(ctx):
    fields = ["revenue", "sgna", "rnd"]
    y1 = ctx.fundamentals_yoy(fields, years=1)
    y2 = ctx.fundamentals_yoy(fields, years=2)

    sale = y1["revenue"].astype(float)
    sale_1 = y1["revenue_lag"].astype(float)
    sale_2 = y2["revenue_lag"].astype(float).reindex(y1.index)
    xs = _xsga(y1["sgna"], y1["rnd"])
    xs_1 = _xsga(y1["sgna_lag"], y1["rnd_lag"])
    xs_2 = _xsga(y2["sgna_lag"].reindex(y1.index), y2["rnd_lag"].reindex(y1.index))

    # primary: two-year-average base; NaN if either lagged value is missing
    primary = (_growth(sale, 0.5 * (sale_1 + sale_2))
               - _growth(xs, 0.5 * (xs_1 + xs_2)))
    # fallback: one-year base
    fallback = _growth(sale, sale_1) - _growth(xs, xs_1)

    out = primary.where(primary.notna(), fallback)
    return out.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="GrSaleToGrOverhead",
    col="f_grsalegrovh",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: HIGH (sales growth - overhead growth) is the long side
    weight=1.0,
    inputs=("SF1.revenue", "SF1.sgna", "SF1.rnd"),
    osap_acronym="GrSaleToGrOverhead",
    source="Abarbanell and Bushee 1998 (The Accounting Review)",
    lookback_months=44,             # latest filing <= 15 months + 24 + 45-day tolerance + lag
    notes="sales growth minus (sgna+rnd) growth vs 2y-average base, fallback to 1y base; sgna==0 -> NaN; ART yoy by report period",
    field_mappings=(
        ("compustat.sale", "SF1.revenue (ART TTM)", "latest, P-1y, P-2y by report period via fundamentals_yoy; ART refreshes quarterly vs OSAP annual fiscal year"),
        ("compustat.xsga", "SF1.sgna + SF1.rnd.fillna(0) (ART TTM)",
         "approx: sgna excludes R&D (added back) and includes D&A for some filers; sgna == 0 -> NaN (OSAP does not zero-fill xsga)"),
        ("guard", "base > 0 in every growth term",
         "OSAP nulls only base == 0; a negative base is a sign flip here NaN (then the fallback fires)"),
    ),
)
