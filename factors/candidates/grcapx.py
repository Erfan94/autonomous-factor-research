"""
grcapx — two-year growth in annual capital expenditure. Firms whose capex grew
most over two fiscal years have expanded investment fastest; OSAP predicts
they earn lower returns.

OSAP: grcapx, Anderson and Garcia-Feijoo 2006 (Journal of Finance), Table 3B
cegth2. Predicted sign: - (SignalDoc Sign = -1; low value = long side).
Spec: osap_source/cache/b4e911e6/grcapx/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  capx     = -SF1.capex at dimension ARY (latest fiscal-year value; Sharadar
             reports capex as a cash outflow, negative).
  capx_l24 = -SF1.capex for the fiscal year two years earlier, from
             ctx.fundamentals_yoy(["capex"], years=2, dimension="ARY"),
             aligned by reportperiod (tolerance 45 days).
  grcapx   = (capx - capx_l24) / capx_l24      where capx_l24 > 0, else null.
  No winsorising, clipping or zero-fill (none in OSAP). The helper takes
  `years`, so the three-year sibling in the same OSAP script is the same
  function with years=3.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? grcapx = 0 exactly (capex
    identical in both years).
  What share of the universe does nothing? Measured in the spec on 46 probe
    months: mean 0.04%, max 0.16%. The only other cluster is capex falling to
    exactly 0 from a positive base, grcapx = -1 (the lowest value, the long
    extreme): mean 0.16%, max 0.31%. Modal share of the guarded cross-section
    mean 0.20%, max 0.41%; qcut gave 10 bins in every probe month. Preflight
    measures it again.
  Tie handling: null. Base <= 0 is nulled (never floored): base == 0 is about
    2.7% and base < 0 (Sharadar positive capex, a sign-inverted outflow) about
    1.8% of the universe. The small -1 cluster is left to the harness's
    average-rank treatment (far below the 10% bar).

DEVIATIONS FROM OSAP:
  - capx: -SF1.capex at ARY, not ART. ART capex is a TTM sum, null on 46% of
    firms in 1998 (ARY 0.5%); a two-year-apart difference of ART flows agrees
    with ARY at fiscal year-end, but ARY matches OSAP's annual item and does
    not refresh quarterly.
  - ppent fallback (capx := ppent - ppent_l12 where capx is missing, FirmAge
    >= 24) NOT reproduced: SF1.ppnenet zeros are vendor zero-fill,
    indistinguishable from missing. A missing capx stays null (about 1.5% of
    the universe). FirmAge is therefore not read.
  - Denominator: OSAP divides by l24.capx unguarded (inf or NaN at 0, keeps a
    negative base); here base <= 0 is null. Sign-flipped negative bases
    (Sharadar positive capex) are therefore dropped, not carried.
  - Lags: fiscal-year alignment by reportperiod (tolerance 45 days) instead of
    OSAP's calendar-month lag of a datadate+6-month replicated series. The new
    year enters at the 10-K filing date (about 3 months after year-end), 2-4
    months fresher than OSAP; OSAP's 6-month annual lag is not reproduced.
    Updates once per firm-year.
  - Early-window coverage: SF1 ARY starts FY1997, so the two-year form exists
    from about 2000 (spec: 24% of the universe at 1999-01, 74% at 2000-12,
    79-91% thereafter); the first-year coverage warning is expected.
  - Currency: a capex ratio is currency-invariant within a firm, so non-USD
    reporters need no fxusd gate.
  - OSAP keeps financials and applies no filter; none applied here.
"""

import pandas as pd

from harness.factor_def import FactorDef


def _grcapx(ctx, years):
    """Growth of annual capex over capex `years` fiscal years earlier, null
    where the base is not positive. `ctx` is a MonthContext."""
    y = ctx.fundamentals_yoy(["capex"], years=years, dimension="ARY")
    capx = -y["capex"].astype(float)
    base = -y["capex_lag"].astype(float)
    return (capx - base) / base.where(base > 0)


def _compute(ctx):
    return _grcapx(ctx, 2)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="grcapx",
    col="f_grcapx",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: high capex growth predicts low returns
    weight=1.0,
    inputs=("SF1.capex",),
    osap_acronym="grcapx",
    source="Anderson and Garcia-Feijoo 2006 (Journal of Finance)",
    lookback_months=43,             # 24m (two fiscal years) + 15m max filing age + ~4m report-period-to-filing lag
    # No history_months: no SEP price window is read.
    dimension="ARY",                # ART capex is a TTM sum, 46% null in 1998; annual item wanted
    notes="annual capex growth over two fiscal years, base > 0 only, no ppent fallback",
    field_mappings=(
        ("compustat.capx", "-SF1.capex (ARY)",
         "sign flip (Sharadar capex is an outflow); ARY fiscal-year value, filing-date lag not datadate+6m; "
         "two-year-earlier value by reportperiod alignment (45d), not a calendar-month lag"),
        ("compustat.ppent (capx fallback)", "dropped",
         "SF1.ppnenet is vendor zero-filled; missing capx stays null (about 1.5% of the universe)"),
        ("l24.capx denominator", "base.where(base > 0)",
         "OSAP unguarded (inf/NaN at 0, keeps negative base); here base <= 0 null (about 4.5% of the universe)"),
    ),
)
