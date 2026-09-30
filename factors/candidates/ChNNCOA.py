"""
ChNNCOA — 12-month change in net noncurrent operating assets scaled by total
assets (Soliman 2008, Table 7 DeltaNCO); firms whose noncurrent operating
asset base grows fastest are predicted to earn LOWER returns.

OSAP: ChNNCOA, Soliman 2008, The Accounting Review. Predicted sign: -
(SignalDoc Sign = -1: high growth, low return).
Spec: osap_source/cache/b4e911e6/ChNNCOA/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  y = ctx.fundamentals_yoy(["assets","assetsc","investmentsnc","liabilities",
      "debt"])   (ART default; latest filing known at the signal and the same
      fiscal period one year earlier, aligned by reportperiod within 45 days)
  r      = (assets - assetsc0 - investmentsnc0 - liabilities + debt) / assets
  ChNNCOA = r - r_lag                     (the same expression on the _lag set)
  which is OSAP's ((at-act-ivao)-(lt-dlc-dltt))/at, dlc and dltt entering only
  as their sum = SF1.debt.
  assetsc0 / investmentsnc0 = the field with a NULL treated as 0 ONLY where
  that period's filing exists (reportperiod / reportperiod_lag present),
  matching OSAP's zero-fill of act and ivao; applied identically to the
  current and the year-ago side. The NaN that fundamentals_yoy returns for a
  missing year-ago period is never filled. No fill on assets, liabilities or
  debt (OSAP does not fill at, lt, dlc, dltt).
  Guards: assets <= 0 or null, or assets_lag <= 0 or null -> NaN; missing
  year-ago period -> NaN; non-finite -> NaN.
  Classification-mismatch guard: where assetsc is null in exactly ONE of the
  two periods (a balance sheet that is unclassified at one date and classified
  at the other, e.g. the thin 1998 year-ago coverage), the fill would add the
  whole current-asset share of the balance sheet to one side only and the
  difference is a format artefact, not a change in operating assets. Those
  names are NaN. A balance sheet unclassified at BOTH dates stays in, with
  r = (assets - investmentsnc0 - liabilities + debt)/assets, which is OSAP's
  own value for a Compustat-null act.
  Levels only (ART equals ARQ on the same reportperiod): no flow, no TTM
  smear, no dimension override; both sides in the filer's reporting currency,
  so the ratio needs no fxusd gate.
  Score = -ChNNCOA (ascending=False).

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0.0 (r unchanged).
  What share of the universe does nothing? Approximately none: assets,
  liabilities and debt move every quarter, so the four-quarter difference of
  the ratio is continuous. Sharadar's own zero-fill of investmentsnc (64% zero
  on ART) does not tie the DIFFERENCE. A stale filing (the only route to an
  exact-zero difference) is excluded by fundamentals_yoy. Field-checker
  measured modal share <= 0.06%.
  Tie handling: none needed (no mass point). Unclassified balance sheets are
  scored, not tied.

DEVIATIONS FROM OSAP:
  - investmentsnc (ivao) scope is broader than Compustat ivao: it carries
    equity-method investments and long-term loans receivable as well.
  - debt (dlc + dltt) includes operating-lease liabilities from FY2019
    (ASC 842), while liabilities and assets also include the lease and the
    right-of-use asset; Compustat dltt excludes leases. Lessees therefore show
    a one-off step of roughly ROU/assets in the 12-month change in the 2019-2021
    signal months (retailers, airlines, restaurants). Declared, not corrected.
  - assetsc / investmentsnc null on ART for ~20% of names (unclassified
    balance sheets: financials, REITs). OSAP zero-fills act and ivao, so these
    stay in the sample (see the mismatch guard above for the one exception).
  - timing: latest ART filing against the same fiscal period one year earlier
    (rolling four-quarter change, refreshed quarterly), not OSAP's fiscal-year
    values with datadate + 6 months held 12 months. The 6-month lag is not
    reproduced.
  - year-ago levels by reportperiod (fundamentals_yoy), not shift(12) monthly
    rows; a stale filing yields NaN rather than a false exact-zero change.
  - assets > 0 guard (OSAP has none); upstream non-null at/prcc_c/ni row filter
    not reproduced (sample difference, not value).
  - early window: SF1 calendardate starts 1997Q4, so the first 1999 signal
    months can lack a year-ago period (NaN, not back-filled).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    y = ctx.fundamentals_yoy(["assets", "assetsc", "investmentsnc", "liabilities", "debt", "debtc"])
    have_now = y["reportperiod"].notna()
    have_ago = y["reportperiod_lag"].notna()

    def fill(col, have):
        s = y[col].astype(float)
        return s.where(~(have & s.isna()), 0.0)

    assets = y["assets"].astype(float)
    assets_lag = y["assets_lag"].astype(float)

    ac = fill("assetsc", have_now)
    ac_lag = fill("assetsc_lag", have_ago)
    iv = fill("investmentsnc", have_now)
    iv_lag = fill("investmentsnc_lag", have_ago)

    r = (assets - ac - iv - y["liabilities"].astype(float) + y["debt"].astype(float)) \
        / assets.where(assets > 0)
    r_lag = (assets_lag - ac_lag - iv_lag - y["liabilities_lag"].astype(float)
             + y["debt_lag"].astype(float)) / assets_lag.where(assets_lag > 0)

    chg = r - r_lag
    # classification mismatch: assetsc or investmentsnc null at exactly one of
    # the two dates (a one-sided zero-fill would add a whole-level step)
    mismatch = (y["assetsc"].isna() != y["assetsc_lag"].isna()) | \
        (y["investmentsnc"].isna() != y["investmentsnc_lag"].isna())
    # debt gate ruling: debtc null (unclassified block) -> NaN, as OSAP's dlc/dltt are not zero-filled
    out = chg.where(have_now & have_ago & ~mismatch & y["debtc"].notna() & y["debtc_lag"].notna())
    return out.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="ChNNCOA",
    col="f_chnncoa",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: LOW growth in net noncurrent operating assets is attractive
    weight=1.0,
    inputs=("SF1.assets", "SF1.assetsc", "SF1.investmentsnc", "SF1.liabilities", "SF1.debt", "SF1.debtc"),
    osap_acronym="ChNNCOA",
    source="Soliman 2008 (The Accounting Review)",
    lookback_months=31,             # latest filing up to 15 months old + year-ago period 12 months earlier + ~4m report-period-to-filing lag
    notes="12m change in ((assets-assetsc-investmentsnc)-(liabilities-debt))/assets; null assetsc/investmentsnc -> 0 where filing exists; sign -1",
    field_mappings=(
        ("compustat.at", "SF1.assets (ART)", "guard > 0 on both sides; null -> NaN (OSAP has no guard)"),
        ("compustat.act", "SF1.assetsc (ART)",
         "null (unclassified balance sheet, ~20%) -> 0 where the filing exists, both sides, as OSAP zero-fills act; null at exactly one date -> NaN (format artefact)"),
        ("compustat.ivao", "SF1.investmentsnc (ART)",
         "APPROX: scope broader than ivao (equity-method investments, LT loans receivable); null -> 0 where filing exists (OSAP zero-fill); null at exactly one date -> NaN, as assetsc"),
        ("compustat.lt", "SF1.liabilities (ART)", "1:1, no fill"),
        ("compustat.dlc + compustat.dltt", "SF1.debt (ART)",
         "enters only as the sum; includes operating-lease liabilities from FY2019 (ASC 842): lessee step in 2019-2021 signal months, declared"),
        ("temp shift(12)", "*_lag via ctx.fundamentals_yoy",
         "year-ago levels by reportperiod (45-day tolerance), not 12 monthly rows; missing/stale -> NaN"),
        ("datadate + 6 months availability", "latest ART filing with datekey <= signal",
         "rolling quarterly refresh, four-quarter span; OSAP's 6-month lag and annual step not reproduced"),
    ),
)
