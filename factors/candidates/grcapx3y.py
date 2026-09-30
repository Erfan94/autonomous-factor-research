"""
grcapx3y — annual capital expenditure relative to its own prior three-year
average. Firms spending far more than their recent norm have stepped up
investment; OSAP predicts they earn lower returns.

OSAP: grcapx3y, Anderson and Garcia-Feijoo 2006 (Journal of Finance), Table 3D
cegth3. Predicted sign: - (SignalDoc Sign = -1; low value = long side).
Spec: osap_source/cache/b4e911e6/grcapx3y/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  capx     = -SF1.capex at dimension ARY (latest fiscal-year value; Sharadar
             reports capex as a cash outflow, negative).
  capx_k   = -SF1.capex for the fiscal year k = 1, 2, 3 years earlier, from
             ctx.fundamentals_history(["capex"], n_periods=8, dimension="ARY"),
             aligned by reportperiod to (latest reportperiod - k years),
             tolerance 45 days, closest period wins (the fundamentals_yoy rule,
             extended to three lags because that helper takes one).
  base     = capx_1 + capx_2 + capx_3         all three required (any missing
                                              lag makes the base null)
  grcapx3y = capx / base * 3                  where base > 0, else null.
  A LEVEL ratio, not a growth rate: 1.0 = capex equal to the trailing
  three-year mean, no "-1". The OSAP code multiplies by 3 (current over the
  AVERAGE of the prior three years); the SignalDoc wording says "sum" and omits
  the 3. The code is followed. No winsorising, clipping or zero-fill (none in
  OSAP).

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 1.0 (capex identical
    in all four years).
  What share of the universe does nothing? Measured in the spec on 46 probe
    months: 0.00% in most months, max 0.11%, mean 0.03% from 2001-06 on. The
    only real cluster is capex exactly 0 this year from a positive base, signal
    exactly 0 (the lowest value, the long extreme under Sign -1): mean 0.27%
    over the 46 months, max 0.49% from 2001-06 on. Modal share of the ranked
    cross-section mean 0.28%, max 0.76% (2000-06); qcut gave 10 bins in every
    probe month. Preflight measures it again.
  Tie handling: null. Base <= 0 is nulled (never floored): base == 0 (all three
    lags present, sum exactly 0) is about 2.3% and base < 0 (Sharadar positive
    capex, a sign-inverted outflow) about 1.4% of the universe. The small 0
    cluster is left to the harness's average-rank treatment (far below the 10%
    bar).

DEVIATIONS FROM OSAP:
  - Sharadar positive capex (a sign-inverted outflow) is NaN at every date read
    (capex_sign_ruling; OSAP's gross capx is never negative).
  - capx: -SF1.capex at ARY, not ART. ART capex is a TTM sum, null on 46% of
    firms in 1998 (ARY 0.5%); year-over-year windows one to three years apart
    do not overlap, but ARY matches OSAP's annual item and does not refresh
    quarterly.
  - ppent fallback (capx := ppent - ppent_l12 where capx is missing, FirmAge
    >= 24) NOT reproduced: SF1.ppnenet zeros are vendor zero-fill,
    indistinguishable from missing. A missing capx, current or lagged, stays
    null (about 1.4% of the universe for the current value). FirmAge is
    therefore not read. OSAP applies the fallback before the lags, so it would
    also have filled lagged capx; that is not reproduced either.
  - Denominator: OSAP divides by the lag sum unguarded (inf or NaN at 0, keeps
    a negative base); here base <= 0 is null (about 3.7% of the universe).
  - Lags: fiscal-year alignment by reportperiod (tolerance 45 days) instead of
    OSAP's calendar-month lags (12, 24, 36) of a datadate+6-month replicated
    series. The new year enters at the 10-K filing date (about 3 months after
    year-end), 2-4 months fresher than OSAP; OSAP's 6-month annual lag is not
    reproduced. Updates once per firm-year.
  - Early-window coverage: three prior fiscal years are needed and SF1 ARY
    starts FY1997, so the signal exists from about early 2001. Measured
    coverage of the universe: 12.7% at 1998-12, 19.4% at 1999-06, 20.1% at
    1999-12, 34.8% at 2000-06, 39.3% at 2000-12, then 69% and above from
    2001-06. The 1999-2000 months are below the 40% coverage floor; the
    preflight first-month coverage warning is expected.
  - Currency: a capex ratio is currency-invariant within a firm, so non-USD
    reporters need no fxusd gate.
  - OSAP keeps financials and applies no filter; none applied here.
"""

import pandas as pd

from harness.factor_def import FactorDef

_LAGS = (1, 2, 3)        # fiscal years back
_TOL_DAYS = 45           # same report-period tolerance as fundamentals_yoy


def _lagged_capx(ctx):
    """Latest -capex (ARY) and the -capex of the fiscal years 1, 2 and 3 earlier,
    aligned by reportperiod. Frame indexed by ctx ID: capx, l1, l2, l3."""
    h = ctx.fundamentals_history(["capex"], n_periods=8, dimension="ARY")
    out = pd.DataFrame(index=ctx.ids, columns=["capx", "l1", "l2", "l3"], dtype=float)
    if h.empty:
        return out
    # Sharadar positive capex is a sign-inverted outflow: capx < 0 -> NaN at every date (capex_sign_ruling)
    h = h.assign(capex=-h["capex"].astype(float))
    h = h.assign(capex=h["capex"].where(h["capex"] >= 0))
    cur = h[h["q_back"] == 0].set_index("ID")
    out["capx"] = cur["capex"].reindex(out.index)
    past = h[h["q_back"] > 0]
    for k in _LAGS:
        target = (cur["reportperiod"] - pd.DateOffset(years=k)).rename("target")
        p = past.merge(target, left_on="ID", right_index=True)
        p["gap"] = (p["reportperiod"] - p["target"]).abs()
        p = p[p["gap"] <= pd.Timedelta(days=_TOL_DAYS)]
        p = (p.sort_values(["ID", "gap", "q_back"], kind="mergesort")
              .drop_duplicates("ID", keep="first").set_index("ID"))
        out[f"l{k}"] = p["capex"].reindex(out.index)
    return out


def _compute(ctx):
    d = _lagged_capx(ctx)
    # all three lags required: a plain sum of columns propagates NaN
    base = d["l1"] + d["l2"] + d["l3"]
    return d["capx"] / base.where(base > 0) * 3.0


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="grcapx3y",
    col="f_grcapx3y",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: high capex vs its 3-year mean predicts low returns
    weight=1.0,
    inputs=("SF1.capex",),
    osap_acronym="grcapx3y",
    source="Anderson and Garcia-Feijoo 2006 (Journal of Finance)",
    lookback_months=55,             # 36m (three fiscal years) + 15m max filing age + ~4m report-period-to-filing lag
    # No history_months: no SEP price window is read.
    dimension="ARY",                # ART capex is a TTM sum, 46% null in 1998; annual item wanted
    notes="current annual capex over the mean of the prior three fiscal years (level ratio, 1.0 = flat), base > 0 only, all three lags required, no ppent fallback",
    field_mappings=(
        ("compustat.capx", "-SF1.capex (ARY)",
         "sign flip (Sharadar capex is an outflow); ARY fiscal-year value, filing-date lag not datadate+6m"),
        ("l12/l24/l36.capx", "-SF1.capex (ARY) via fundamentals_history(n_periods=8)",
         "reportperiod alignment to 1/2/3 fiscal years back (45d), not calendar-month lags; all three required, so the signal starts about 2001 and 1999-2000 coverage is below 40%"),
        ("compustat.ppent (capx fallback)", "dropped",
         "SF1.ppnenet is vendor zero-filled; missing capx (current or lagged) stays null"),
        ("sum of three lags denominator", "base.where(base > 0), x3",
         "OSAP unguarded (inf/NaN at 0, keeps negative base); here base <= 0 null (about 3.7% of the universe); code's x3 followed over the SignalDoc 'sum' wording"),
    ),
)
