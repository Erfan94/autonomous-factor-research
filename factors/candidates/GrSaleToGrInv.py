"""
GrSaleToGrInv — percentage sales growth minus percentage inventory growth, each
measured against the average of the two prior years (Abarbanell-Bushee RINV):
sales outgrowing inventory signals strong demand and lean stock not yet priced.

OSAP: GrSaleToGrInv, Abarbanell and Bushee 1998 (The Accounting Review),
Table 2b RINV. Predicted sign: + (SignalDoc Sign = +1, so ascending=True).
Spec: osap_source/cache/b4e911e6/GrSaleToGrInv/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  Report-period-aligned ART filings at three dates: latest P, P-1y, P-2y
  (ctx.fundamentals_yoy with years=1 and years=2). sale = revenue (ART TTM),
  invt = inventory (ART level).
    base_s = (sale_1y + sale_2y) / 2;    base_i = (invt_1y + invt_2y) / 2
    primary  = (sale - base_s)/base_s - (invt - base_i)/base_i
               each term NaN if its base is not strictly positive
    fallback = (sale - sale_1y)/sale_1y - (invt - invt_1y)/invt_1y
               each term NaN if its l12 base is not strictly positive
    GrSaleToGrInv = primary, else fallback where primary is NaN
  The fallback fires when P-2y is unknown AND whenever one primary term is
  undefined (OSAP's pandas arithmetic, reproduced). A -100% inventory growth
  (invt = 0 over a positive base) is a legitimate value. Raw value is
  GrSaleToGrInv; ascending=True makes a HIGH value the long side.
  revenue is an ART trailing-four-quarter sum used as a level at three dates
  exactly four quarters apart: the windows do not overlap, so each growth term
  is a clean annual change. dimension stays the ART default (a single-quarter
  ARQ revenue over annual-scale bases would understate growth about 4x).

NULL HANDLING:
  - inventory is zero-filled as OSAP does, but ONLY on a filing whose total
    assets are reported (a null on a populated balance sheet is a real absent
    item; an empty row stays NaN). Sharadar already stores 0 for a
    non-reporter (exact zero ~46% of ART rows). OSAP's own base-zero rule then
    drops those firms (base 0 -> NaN, then l12 == 0 -> NaN in the fallback), so
    the exclusion is identical to OSAP's.
  - revenue, and every year-ago filing, is NEVER zero-filled: a name with no
    known filing for a required date is NaN, not a zero growth.
  - Early coverage is thin by data start: ART flow revenue for the first 1998
    quarters is only about half populated and P-2y needs the 1997Q4 period, the
    earliest held, so signal months to ~2000-02 run mostly on the fallback and
    some are below the coverage floor. A data-start reason; nothing weakened.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? A firm with sales and
  inventory unchanged at all three dates gives exactly 0 (both growth terms 0),
  and it must carry a nonzero inventory base: essentially no operating firm.
  The zero-inventory population is NOT a mass point at 0: it is NaN through
  the base guards. Zero sales over a positive base is growth -1, a legitimate
  value that varies with the inventory term.
  What share of the universe does nothing? Spec-measured modal-value share of
  the scored cross-section 0.07-0.17% at 9 probe months (distinct values ~= n);
  preflight measures it.
  Tie handling: null, by construction. Inventory exactly 0 at both ends makes
  the base zero in the primary path (avg of two zeros) and, at l12 == 0, in the
  fallback path, so the standing level-0-at-both-ends rule is already applied
  by OSAP's own base rule (confirmed, nothing added). The factor therefore
  carries no extra tie rule.

DEVIATIONS FROM OSAP:
  - sale: revenue (ART TTM); invt: inventory (ART level), vendor 0 kept (the
    same as OSAP's zero-fill, see above); no unavailable input.
  - Base guard is strictly positive (OSAP: base != 0 -> NaN). A negative
    revenue or inventory base (data error, well under 0.1% of rows) is NaN here
    rather than a sign-flipped growth.
  - Timing: OSAP reads the fiscal year at datadate + 6 months, refreshed
    annually; here the latest filed ART level (refreshed quarterly) against the
    same periods one and two years earlier. The growth spans four quarters, not
    the fiscal year.
  - Coverage ceiling ~55-62% from 2003 is the OSAP zero-inventory rule itself
    (inventory exactly 0 at t on 35-45% of the universe), not an approximation.
  - SignalDoc Filter is blank; none added (the harness universe owns price).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _growth(cur, base):
    """(cur - base)/base, NaN unless base > 0."""
    return (cur - base) / base.where(base > 0)


def _compute(ctx):
    y1 = ctx.fundamentals_yoy(["revenue", "inventory", "assets"], years=1)
    y2 = ctx.fundamentals_yoy(["revenue", "inventory", "assets"], years=2)

    def invt(y, suffix):   # OSAP zero-fills invt: only inside a filing with assets reported
        s = y["inventory" + suffix].astype(float)
        return s.where(s.notna() | y["assets" + suffix].isna(), 0.0)

    s0 = y1["revenue"].astype(float)
    s1 = y1["revenue_lag"].astype(float)
    s2 = y2["revenue_lag"].astype(float)
    i0 = invt(y1, "")
    i1 = invt(y1, "_lag")
    i2 = invt(y2, "_lag")

    # Primary: growth against the average of the two prior years. NaN if either
    # prior year is missing (pandas arithmetic) or either term's base is not > 0.
    base_s = 0.5 * (s1 + s2)
    base_i = 0.5 * (i1 + i2)
    primary = _growth(s0, base_s) - _growth(i0, base_i)

    # Fallback: growth against the prior year only.
    fallback = _growth(s0, s1) - _growth(i0, i1)

    out = primary.where(primary.notna(), fallback)
    return out.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="GrSaleToGrInv",
    col="f_grstgi",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: sales growth above inventory growth is the long side
    weight=1.0,
    inputs=("SF1.revenue", "SF1.inventory", "SF1.assets"),
    osap_acronym="GrSaleToGrInv",
    source="Abarbanell and Bushee 1998 (The Accounting Review)",
    lookback_months=44,             # latest filing (<=15m old) + 2 fiscal years back + 45d period tolerance + ~4m report-period-to-filing lag (honest figure ~43.5, rounded up)
    # No history_months: no SEP price window is read; year-ago levels come from
    # fundamentals_yoy (report-period aligned).
    notes="sale growth minus inventory growth vs avg of 2 prior years, fallback vs 1 prior year; OSAP zero-inventory rule kept; ART, yoy by reportperiod",
    field_mappings=(
        ("sale", "SF1.revenue", "ART TTM flow at three dates four quarters apart (windows do not overlap); null is NaN, never zero-filled"),
        ("invt", "SF1.inventory", "ART level; vendor 0 for non-reporters equals OSAP's zero-fill, then OSAP's base-zero rule drops them; null zero-filled only on a filing with assets reported"),
        ("base guard", "base > 0", "OSAP drops base == 0 only; negative base (data error) is NaN here"),
        ("time_avail_m", "SF1.datekey", "filing-date bound, quarterly refresh, three report-period-aligned dates; no 6-month annual lag"),
    ),
)
