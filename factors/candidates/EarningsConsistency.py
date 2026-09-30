"""
EarningsConsistency — average annual EPS growth over the last five fiscal years,
blanked where the latest growth is an outlier or its sign is inconsistent with the
prior year's: steadily growing earnings are followed by higher returns.

OSAP: EarningsConsistency, Alwathainani 2009, British Accounting Review (Table 11A
CLG-CHG). Predicted sign: + (SignalDoc Sign = +1; high value = long side).
Spec: osap_source/cache/b4e911e6/EarningsConsistency/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  e_k = SF1.eps at dimension ARY (fiscal-year reported EPS), k = 0..6 fiscal years
        back from the latest 10-K known at the signal (ctx.fundamentals_history,
        n_periods = 7, deduplicated on reportperiod). Years are aligned by
        reportperiod: e_k is the filing whose report month is 12k months before the
        latest (report date + 10 days, rounded to a month ordinal, +-1 month
        tolerance for 52/53-week calendars); a year not found is NaN, never a
        shifted one.
  g_k = (e_k - e_{k+1}) / (0.5 * (|e_{k+1}| + |e_{k+2}|)),   k = 0..4
        denominator must be > 0, otherwise g_k is NaN (OSAP: inf -> NaN, 0/0 NaN).
  score = mean(g_0..g_4), skipping NaN (one valid term is enough).
  Score is NaN where (OSAP's own exception, asymmetric, NOT symmetrised):
    - e_0 or e_1 is missing;
    - |e_0 / e_1| > 6 (also where e_1 == 0 and e_0 != 0; 0/0 is not > 6);
    - g_0 > 0 and g_1 < 0;
    - g_0 < 0 and (g_1 > 0 or g_1 is missing).
  A positive g_0 with a MISSING g_1 is kept; g_0 == 0 triggers neither sign test.
  ascending=True: high consistency is the long side.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Between 10-Ks the score is the
  latest annual value held constant, which is firm-specific and continuous across
  firms; there is no common stale value. The only exact value shared by firms is
  g_0 == 0 / score 0, needing equal EPS in consecutive years (or all five terms 0).
  What share of the universe does nothing? Estimated below 1% (ARY eps exact zero
  0.04-0.18% of the universe; the 0.001 lattice of eps makes growth coarse only for
  tiny EPS, mainly in 1999-2002 when one term is valid). Preflight measures it.
  Tie handling: null / do nothing. No floor on |e| (the growth denominator is
  guarded > 0 only), no winsorising, average-rank ties by the harness. The scored
  cross-section is selected by the sign rules, which is the construction.

DEVIATIONS FROM OSAP:
  - epspx -> SF1.eps ARY. eps is a REPORTED figure (netinccmn-based basic EPS,
    includes discontinued operations and preferred adjustments), nearer Compustat
    epspi than epspx (which excludes extraordinary items); never rebuilt from
    netinccmn / shareswa (they agree within 0.005 on only ~64% of ARY rows).
  - eps is restated to today's split basis on every row (no split jump); growth ratios
    are scale-free. ARY is the fiscal-year level (equals ART at the FY end);
    ART is a moving four-quarter sum and is not used. FactorDef.dimension = "ARY" is
    recorded only (dimension_overrides).
  - Fiscal-year alignment by reportperiod, not by 12 / 24 / ... rows of a monthly
    panel. A year enters at its 10-K datekey (about 2-3 months after year end), 3-4
    months earlier than OSAP's datadate + 6 months; the 6-month lag is not
    reproduced. The value is a step that changes once per filing. A name whose
    latest 10-K is older than max_fundamental_age_months is not scored.
  - OSAP's portfolio filters (abs(prc) > 1, "price < 5" in the Definition) are not
    in predictor.py and are not reproduced; the harness universe applies price >= 1.
  - History: SF1 ARY starts at 1992-12 and is thin before FY1997 (>= 3 annual values
    for 24% of the universe at 1999-01, 37% at 1999-12, 69% at 2000-06; >= 4 values
    12% / 20% / 34%; all 7 values 0.1% at 1999-12, 27% at 2002-12, 81% at 2008-06).
    Partial windows score as in OSAP (skipna), so 1999-2002 rests on one to four terms,
    and coverage is further cut by the sign rules (negative growth needs a known,
    non-positive prior growth, i.e. four annual values). The 40% coverage bar is at
    risk in early months; preflight measures it.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef

_N_Y = 7             # e_0..e_6 -> g_0..g_4 needs e_0..e_6


def _year_matrix(ctx):
    """ID x fiscal-year-offset (0 = latest 10-K) matrix of SF1 ARY eps, aligned by
    reportperiod (+-1 month tolerance on 12-month multiples)."""
    h = ctx.fundamentals_history(["eps"], n_periods=_N_Y, dimension="ARY")
    if h.empty:
        return pd.DataFrame(columns=range(_N_Y), dtype=float)
    rp = pd.to_datetime(h["reportperiod"]) + pd.Timedelta(days=10)
    h = h.assign(m=(rp.dt.year * 12 + rp.dt.month).astype("int64"))
    m0 = h.loc[h["q_back"] == 0].set_index("ID")["m"]
    d = h["ID"].map(m0) - h["m"]
    j = np.rint(d / 12.0)
    err = (d - 12.0 * j).abs()
    keep = (err <= 1) & (j >= 0) & (j < _N_Y)
    h = h.assign(j=j, err=err)[keep]
    h = (h.sort_values(["ID", "j", "err"], kind="mergesort")
          .drop_duplicates(["ID", "j"], keep="first"))
    e = h.assign(j=h["j"].astype(int)).pivot(index="ID", columns="j", values="eps")
    return e.reindex(columns=range(_N_Y)).astype(float)


def _compute(ctx):
    e = _year_matrix(ctx)
    if e.empty:
        return pd.Series(dtype=float)

    g = {}
    for k in range(5):
        den = 0.5 * (e[k + 1].abs() + e[k + 2].abs())
        g[k] = (e[k] - e[k + 1]) / den.where(den > 0)       # den == 0 -> NaN (OSAP inf/0-0 -> NaN)
    gdf = pd.DataFrame(g)
    score = gdf.mean(axis=1, skipna=True)

    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = (e[0] / e[1]).replace([np.inf, -np.inf], np.inf)
    g0, g1 = gdf[0], gdf[1]
    exception = (
        e[0].isna() | e[1].isna()
        | (ratio.abs() > 6)                                  # inf (e_1 == 0, e_0 != 0) is > 6; 0/0 is NaN -> False
        | ((g0 > 0) & (g1 < 0))
        | ((g0 < 0) & ((g1 > 0) | g1.isna()))                # asymmetric: missing prior growth excludes negative growth only
    )
    return score.where(~exception)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="EarningsConsistency",
    col="f_earncons",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: high consistent growth -> high return
    weight=1.0,
    inputs=("SF1.eps",),
    osap_acronym="EarningsConsistency",
    source="Alwathainani 2009 (British Accounting Review)",
    lookback_months=90,             # 7 fiscal years = 72m back from the latest period + 15m max filing age + ~3m filing lag
    # No history_months: no price window is read.
    dimension="ARY",                # annual EPS; ART is a moving 4-quarter sum on a different cadence
    notes="mean of five annual EPS growth rates (vs avg |EPS| of two prior years), blanked by OSAP's ratio and asymmetric sign tests",
    field_mappings=(
        ("compustat.epspx", "SF1.eps (ARY)",
         "reported basic EPS incl. discontinued ops (nearer epspi); split-restated; not rebuilt from netinccmn/shareswa"),
        ("12/24/.. row lags", "reportperiod alignment (ctx.fundamentals_history, 7 fiscal years)",
         "known at 10-K datekey (3-4 months earlier than datadate+6m); missing year = NaN; partial windows score as OSAP"),
        ("price filters", "not reproduced",
         "abs(prc)>1 / price<5 are portfolio-stage in OSAP; harness universe applies price >= 1"),
    ),
)
