"""
NOA — net operating assets: (operating assets - operating liabilities) scaled
by the prior year's total assets. Firms whose balance sheet is heavy in
accumulated operating assets (accruals not yet converted to cash) are
predicted to earn LOWER returns.

OSAP: NOA, Hirshleifer, Hou, Teoh and Zhang 2004, Journal of Accounting and
Economics (Table 4 H-L). Predicted sign: - (SignalDoc Sign = -1: LOW NOA is the
long leg).
Spec: osap_source/cache/b4e911e6/NOA/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  y = ctx.fundamentals_yoy(["assets","liabilities","debtnc","debtc","cashneq",
      "investmentsc"])   (ART default; latest filing known at the signal and the
      same fiscal period one year earlier, aligned by reportperiod within 45 days)
  OSAP: OA = at - che; OL = at - dltt - mib - dc - ceq; NOA = (OA - OL)/l12_at
        = (dltt + mib + dc + ceq - che) / l12_at.
  Here: che = cashneq + investmentsc.fillna(0); dltt -> debtnc; dc = 0;
  mib := assets - liabilities - equity and ceq := equity, so mib + ceq =
  assets - liabilities and EQUITY CANCELS ALGEBRAICALLY (SF1.equity is not an
  input). Therefore
      NOA = (debtnc + assets - liabilities - che) / assets_lag
  with assets_lag the total assets of the same fiscal period one year earlier
  (fundamentals_yoy, reportperiod-aligned); assets_lag <= 0 or null -> NaN.
  Gate: NaN where debtc is null or debtnc is null (the unclassified balance
  sheets of financials/REITs, ~20% of ART rows, a different balance-sheet
  format; field_map ruling for debt users). debtnc null is that same block, so
  the gate does not change coverage. The unclassified block is never
  zero-filled. cashneq null -> NaN. Non-finite -> NaN.
  Levels only (ART equals ARQ on the same reportperiod): no flow, no TTM smear,
  no dimension override; numerator and denominator are in the filer's
  reporting currency, so the ratio needs no fxusd gate.
  Score ascending=False (LOW NOA is the long leg).

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? There is no natural value: the
  ratio is continuous and nonzero, with no default and no signal zero-fill
  (only investmentsc inside che is filled, a component, not the signal).
  What share of the universe does nothing? Approximately none. Spec measured a
  modal share of the scored cross-section of 0.05%-0.12% (median 0.07%), at most
  1 exact zero per month, distinct values equal n scored, 10 qcut bins every
  month. Preflight to confirm.
  Tie handling: none needed.

DEVIATIONS FROM OSAP:
  - dc (convertible debt; not deferred charges) has no SF1 field: set to 0,
    which is OSAP's own zero-fill for a missing dc. dc is subtracted inside OL,
    so OA - OL contains +dc: for convertible issuers NOA here is LOWER than
    OSAP's by dc/assets_lag; size unmeasured.
  - mib + ceq -> assets - liabilities (equity cancels). Preferred stock,
    redeemable/temporary equity (the 2019-23 SPAC cohort) and noncontrolling
    interest that OSAP leaves inside OL therefore sit on the financing side
    here, and Sharadar's NOA is HIGHER by those amounts than OSAP's.
    Material mainly for SPACs and preferred issuers; declared, not adjusted.
  - dltt -> debtnc, which from FY2019 (ASC 842) includes non-current
    operating-lease liabilities that Compustat dltt excludes: a level step up
    for lessees in the 2019-2021 signal months. Declared, not adjusted; the
    right-of-use asset is in assets on both sides.
  - che = cashneq + investmentsc.fillna(0) (a null investmentsc is treated as 0, as
    OSAP zero-fills che; the unclassified block is gated out anyway):
    overstates for captive-finance / vendor-financing names; OSAP's che is
    zero-filled, here cashneq null -> NaN.
  - financials/REITs (unclassified balance sheets, debtc/debtnc null) are NaN
    (10%-15% scored by sector; the coverage loss is ~20%).
  - timing: latest ART filing against the same fiscal period one year earlier,
    refreshed quarterly; OSAP's annual fiscal-year balance sheet with
    datadate + 6 months held is not reproduced.
  - assets_lag by reportperiod (fundamentals_yoy), not a shift(12) of monthly
    rows; a missing year-ago period is NaN. Early window: SF1 starts 1997Q4,
    so the first signal months lack a year-ago filing (spec: 38.1% coverage at
    1998-12, >= 40% from 1999-02).
  - assets_lag > 0 guard (OSAP has none).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    y = ctx.fundamentals_yoy(["assets", "liabilities", "debtnc", "debtc", "cashneq", "investmentsc"])
    assets = y["assets"].astype(float)
    liabilities = y["liabilities"].astype(float)
    debtnc = y["debtnc"].astype(float)
    che = y["cashneq"].astype(float) + y["investmentsc"].astype(float).fillna(0.0)
    assets_lag = y["assets_lag"].astype(float)

    # equity cancels (mib := assets - liabilities - equity, ceq := equity); dc = 0
    num = debtnc + (assets - liabilities) - che
    noa = num / assets_lag.where(assets_lag > 0)
    # unclassified block (debtc / debtnc null): a different balance-sheet format, never zero-filled
    noa = noa.where(y["debtc"].notna() & y["debtnc"].notna())
    return noa.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="NOA",
    col="f_noa",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: LOW net operating assets is the long leg
    weight=1.0,
    inputs=("SF1.assets", "SF1.liabilities", "SF1.debtnc", "SF1.debtc", "SF1.cashneq", "SF1.investmentsc"),
    osap_acronym="NOA",
    source="Hirshleifer, Hou, Teoh and Zhang 2004 (Journal of Accounting and Economics)",
    lookback_months=31,             # latest filing up to 15 months old + year-ago period 12 months earlier + ~4m report-period-to-filing lag
    notes="(debtnc + assets - liabilities - (cashneq + investmentsc)) / year-ago assets; dc=0, equity cancels; debtc/debtnc-null block NaN; sign -1",
    field_mappings=(
        ("compustat.at (OA and OL)", "SF1.assets (ART)", "current in the numerator through assets - liabilities; guard > 0 on the lagged denominator"),
        ("compustat.che (zero-filled)", "SF1.cashneq + SF1.investmentsc.fillna(0)",
         "APPROX: overstates for captive-finance/vendor-financing names; cashneq null -> NaN (OSAP zero-fills che)"),
        ("compustat.dltt", "SF1.debtnc (ART), gated on debtc and debtnc notna",
         "APPROX: includes non-current operating-lease liabilities from FY2019 (ASC 842); unclassified block (~20%) NaN, never zero-filled"),
        ("compustat.mib (zero-filled) + compustat.ceq", "SF1.assets - SF1.liabilities (equity cancels)",
         "preferred, redeemable NCI and temporary equity sit on the financing side here, NOA higher by those amounts than OSAP"),
        ("compustat.dc (convertible debt, zero-filled)", "none (0)",
         "OSAP's own missing-case value; convertible issuers differ, size unmeasured"),
        ("l12_at = at.shift(12)", "SF1.assets_lag via ctx.fundamentals_yoy",
         "same fiscal period one year earlier by reportperiod (45-day tolerance); missing -> NaN"),
        ("datadate + 6 months availability", "latest ART filing with datekey <= signal",
         "rolling quarterly refresh; OSAP's 6-month lag and annual step not reproduced"),
    ),
)
