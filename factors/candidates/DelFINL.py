"""
DelFINL — change in financial liabilities (long-term debt + current debt +
preferred stock) scaled by average total assets; firms that raise external
debt financing are predicted to earn LOWER returns.

OSAP: DelFINL, Richardson, Sloan, Soliman and Tuna 2005, Journal of
Accounting and Economics (Table 8C). Predicted sign: - (SignalDoc Sign = -1).
Spec: osap_source/cache/b4e911e6/DelFINL/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  y = ctx.fundamentals_yoy(["debt", "debtc", "assets"])
      (ART default; the latest filing known at the signal and the same fiscal
      period one year earlier, aligned by reportperiod within 45 days)
  DelFINL = (debt - debt_lag) / ((assets + assets_lag) / 2)
  Guards: average assets <= 0 or null -> NaN; debt null at either date -> NaN;
  missing year-ago period -> NaN; non-finite -> NaN. Standing tie rule: debt
  exactly 0 at BOTH dates -> NaN. Both fields are balance-sheet levels (ART
  equals ARQ on the same reportperiod): no flow, no TTM smear, no dimension
  override, same reporting currency so the ratio needs no fxusd gate.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0.0, for a firm with
  no debt at either date (a firm with unchanged nonzero debt is also 0 but is
  continuous-rare).
  What share of the universe does nothing? Debt exactly 0 at both ends was
  4.6-16.3% of non-null raw SF1 ART rows in the spec's probe years (10.3%
  1999, 15.7% 2008, 16.3% 2015, 4.6% 2020): above the 10% cliff.
  Tie handling: null (restrict the sample). Names with debt exactly 0 at both
  ends are NaN, because that zero change is structural, not information;
  blend_ranks renormalises. One-end-zero names (debt raised from nothing, or
  fully repaid) are kept; a zero may be a vendor fill rather than a true zero
  (field_map dltt_plus_dlc), and after 2019 one-end-zero is mostly lease
  adoption. Null debt is NaN, never
  zero-filled.

DEVIATIONS FROM OSAP:
  - pstk is absent from SF1 and OSAP's own code fills it with 0 when missing,
    so the preferred-stock term is DROPPED (approx). Where Compustat reports
    preferred stock its y/y change is lost here; preferred sits inside SF1
    equity and is not separable.
  - dltt + dlc -> SF1.debt (= debtc + debtnc, field-mapped as a single field,
    not debtc.fillna(0) + debtnc.fillna(0), which would fabricate values on
    unclassified balance sheets). debt is populated for unclassified balance
    sheets (0.03% null), but they are gated OUT: debtc null at either end ->
    NaN (field_map unclassified_balance_sheet_block ruling), matching OSAP's
    un-zero-filled dltt/dlc coverage.
  - ASC 842 lessee step: SF1 debt includes capital AND operating lease
    obligations from FY2019 filings; Compustat dltt/dlc excludes operating
    leases. The year-over-year change carries a one-off positive lessee-wide
    step in the 2019-2020 filings (and lessees move off the exact zero). It is
    declared, not adjusted away.
  - timing: latest ART filing (0-3 months old, at most
    max_fundamental_age_months = 15) against the same fiscal period one year
    earlier (rolling four-quarter change, refreshed quarterly), not OSAP's
    fiscal-year values with datadate + 6 months held 12 months. The 6-month
    lag is not reproduced.
  - year-ago levels by reportperiod (fundamentals_yoy), not OSAP's calendar
    merge on time_avail_m; a stale or missing year-ago filing is NaN.
  - avg assets > 0 guard (OSAP has none).
  - early window: SF1 starts 1997Q4, so the 1999-01 signal has a year-ago
    period for only part of the universe (~38-48%), ~71-89% from 1999-03.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    y = ctx.fundamentals_yoy(["debt", "debtc", "assets"])
    debt = y["debt"].astype(float)
    debt_lag = y["debt_lag"].astype(float)
    avg_assets = (y["assets"].astype(float) + y["assets_lag"].astype(float)) / 2.0
    out = (debt - debt_lag) / avg_assets.where(avg_assets > 0)
    # standing tie rule: zero debt at both ends is a structural zero change
    out = out.where(~((debt == 0) & (debt_lag == 0)))
    # debt gate ruling: unclassified balance sheets (debtc null) are NaN, as OSAP's dltt/dlc
    out = out.where(y["debtc"].notna() & y["debtc_lag"].notna())
    return out.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="DelFINL",
    col="f_delfinl",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: LOW growth in financial liabilities is attractive
    weight=1.0,
    inputs=("SF1.debt", "SF1.debtc", "SF1.assets"),
    osap_acronym="DelFINL",
    source="Richardson, Sloan, Soliman and Tuna 2005 (Journal of Accounting and Economics)",
    lookback_months=31,             # latest filing up to 15 months old + year-ago period 12 months earlier + ~4m report-period-to-filing lag
    notes="(debt - year-ago debt) / average assets; pstk term dropped; NaN where debt is 0 at both ends; ASC 842 step 2019-20; sign -1",
    field_mappings=(
        ("compustat.dltt + compustat.dlc", "SF1.debt (ART)",
         "debt includes capital and operating leases from FY2019 (ASC 842 lessee step in 2019-2020 changes, declared); debtc null at either end -> NaN (unclassified block gated out); null stays NaN"),
        ("compustat.pstk (fillna 0)", "dropped",
         "no SF1 field and OSAP fills it with 0; preferred changes are lost (approx)"),
        ("compustat.at", "SF1.assets (ART)",
         "average of latest and year-ago assets, guard > 0; null -> NaN; no fxusd gate (same-currency ratio)"),
        ("tie handling", "debt == 0 at both dates -> NaN",
         "standing tie rule for change-in-level signals; one-end-zero kept"),
        ("lagged levels (calendar-month merge)", "*_lag via ctx.fundamentals_yoy",
         "year-ago level by reportperiod (45-day tolerance); missing/stale year-ago -> NaN"),
        ("datadate + 6 months availability", "latest ART filing with datekey <= signal",
         "rolling quarterly refresh, four-quarter span; OSAP's 6-month lag and annual step not reproduced"),
    ),
)
