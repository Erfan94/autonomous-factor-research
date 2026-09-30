"""
ChNWC — 12-month change in non-cash, non-debt net working capital scaled by
total assets (Soliman 2008, Table 7 DeltaWC); firms whose operating working
capital grows fastest are predicted to earn LOWER returns.

OSAP: ChNWC (Acronym2 NWCgr), Soliman 2008, The Accounting Review.
Predicted sign: - (SignalDoc Sign = -1: high growth, low return).
Spec: osap_source/cache/b4e911e6/ChNWC/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  y = ctx.fundamentals_yoy(["assets","assetsc","cashneq","investmentsc",
      "liabilitiesc","debtc"])   (ART default; latest filing known at the
      signal and the same fiscal period one year earlier, by reportperiod)
  che = cashneq + investmentsc.fillna(0)   (investmentsc null -> 0 only where
        that period's filing exists; cashneq is not filled)
  NWC = ((assetsc - che) - (liabilitiesc - debtc)) / assets
  ChNWC = NWC - NWC_lag                    (the same expression on the _lag set)
  Guards: assets <= 0 or null, or assets_lag <= 0 or null -> NaN; missing
  year-ago period -> NaN; non-finite -> NaN.
  No zero-fill on debtc (OSAP does not zero-fill dlc) and none on assetsc /
  liabilitiesc: OSAP fills act and lct, but debtc is null on exactly the same
  unclassified block (financials, REITs), so those names are NaN either way;
  leaving the two NaN rather than 0 differs only for a name with assetsc null
  and debtc present, where a fill would be a format artefact.
  Levels only (ART equals ARQ on the same reportperiod): no flow, no TTM
  smear, no dimension override; ratio in the filer's currency, no fxusd gate.
  Score = -ChNWC (ascending=False).

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0.0 (all levels
  unchanged).
  What share of the universe does nothing? Approximately none. debtc is
  exactly zero for 17-27% of names by year, but that ties a component, not the
  difference: assetsc, liabilitiesc and cash move every quarter. The only route
  to an exact-zero difference is a stale filing, which fundamentals_yoy turns
  into NaN. Expected modal share ~0%; preflight measures it.
  Tie handling: none needed. The ~20% unclassified names are NaN (coverage
  ~80%), not tied.

DEVIATIONS FROM OSAP:
  - che scope: cashneq + investmentsc overshoots Compustat che on financing
    receivables and understates it for financials.
  - ~20% of names (unclassified balance sheets: 71% financials, 20% REITs)
    cannot be scored: debtc is null there and OSAP does not fill dlc, so
    coverage is ~80% against OSAP's higher share.
  - debtc absorbs current operating-lease liabilities from FY2019 (ASC 842;
    median debtc/assets 0.0053 -> 0.0127, 60% of 2018 zeros positive in 2019),
    while liabilitiesc always carried them: from FY2019 the lessee's debtc
    rises with liabilitiesc unchanged, so (liabilitiesc - debtc) falls and NWC
    rises by about the current lease liability over assets (~1-2%), a one-off
    step in
    the 2019-2020 signal months (the year-ago side is pre-842). Declared, not
    corrected.
  - timing: latest ART filing against the same fiscal period one year earlier
    (rolling four-quarter change, refreshed quarterly), not OSAP's fiscal-year
    values with datadate + 6 months held 12 months. The 6-month lag is not
    reproduced.
  - year-ago levels by reportperiod (fundamentals_yoy), not a 12-month
    calendar lag on time_avail_m; a stale filing yields NaN, not a false zero.
  - SignalDoc Filter abs(prc)>5 is a portfolio-stage filter, not applied; the
    harness universe applies. Upstream non-null at/prcc_c/ni row filter not
    reproduced.
  - early window: the first 1999 signal months can lack a year-ago period
    (NaN, not back-filled).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    y = ctx.fundamentals_yoy(["assets", "assetsc", "cashneq", "investmentsc",
                              "liabilitiesc", "debtc"])
    have_now = y["reportperiod"].notna()
    have_ago = y["reportperiod_lag"].notna()

    def fill(col, have):
        s = y[col].astype(float)
        return s.where(~(have & s.isna()), 0.0)

    def nwc(sfx, have):
        che = y["cashneq" + sfx].astype(float) + fill("investmentsc" + sfx, have)
        assets = y["assets" + sfx].astype(float)
        num = (y["assetsc" + sfx].astype(float) - che) \
            - (y["liabilitiesc" + sfx].astype(float) - y["debtc" + sfx].astype(float))
        return num / assets.where(assets > 0)

    chg = nwc("", have_now) - nwc("_lag", have_ago)
    out = chg.where(have_now & have_ago)
    return out.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="ChNWC",
    col="f_chnwc",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: LOW working-capital growth is attractive
    weight=1.0,
    inputs=("SF1.assets", "SF1.assetsc", "SF1.cashneq", "SF1.investmentsc",
            "SF1.liabilitiesc", "SF1.debtc"),
    osap_acronym="ChNWC",
    source="Soliman 2008 (The Accounting Review)",
    lookback_months=31,             # latest filing up to 15 months old + year-ago period 12 months earlier + ~4m report-period-to-filing lag
    notes="12m change in ((assetsc-che)-(liabilitiesc-debtc))/assets; che=cashneq+investmentsc; unclassified names NaN; sign -1",
    field_mappings=(
        ("compustat.act", "SF1.assetsc (ART)", "null (unclassified, ~20%) stays NaN, not 0: debtc is null on the same block (OSAP zero-fills act, moot)"),
        ("compustat.che", "SF1.cashneq + SF1.investmentsc (ART)",
         "APPROX: investmentsc null -> 0 where filing exists; scope overshoots on financing receivables, understates for financials"),
        ("compustat.lct", "SF1.liabilitiesc (ART)", "null stays NaN (OSAP zero-fills lct, moot: same block as debtc null)"),
        ("compustat.dlc", "SF1.debtc (ART)",
         "no fill (as OSAP); null on the unclassified block -> NaN; absorbs current operating-lease liabilities from FY2019 (ASC 842), step in 2019-2020 signal months"),
        ("compustat.at", "SF1.assets (ART)", "guard > 0 on both sides -> NaN"),
        ("*_lag12", "*_lag via ctx.fundamentals_yoy",
         "year-ago levels by reportperiod (45-day tolerance), not a 12-month calendar lag; missing/stale -> NaN"),
        ("datadate + 6 months availability", "latest ART filing with datekey <= signal",
         "rolling quarterly refresh, four-quarter span; OSAP's 6-month lag and annual step not reproduced"),
    ),
)
