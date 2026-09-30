"""
EBM — enterprise book-to-market: (book equity + net financial assets T) divided by
(market cap + T), i.e. book over enterprise value with financial leverage removed.

OSAP: EBM, Penman, Richardson and Tuna 2007, Journal of Accounting Research
(Table 4A, enterprise component of BM). Predicted sign: + (high EBM earns higher
returns; long D10, short D1).
Spec: osap_source/cache/b4e911e6/EBM/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  M  = ctx.universe["mkt_cap_usd"]                  (DAILY.marketcap at the month-end)
  T  = che - debt, with che = SF1.cashneq + SF1.investmentsc.fillna(0) and
       debt = SF1.debt (ART, latest filing known at the signal date).
       OSAP's  T = che - dltt - dlc - dc - dvpa + tstkp  with dc = dvpa = tstkp = 0.
  EV = M + T;   score = (SF1.equity + T) / EV.
  Raw ratio, no log, no winsorising. ascending=True: a HIGH EBM is attractive
  (the long leg), matching SignalDoc Sign = +1.

GUARDS (every denominator; a negative one is a sign flip, not an outlier):
  - M > 0.
  - Enterprise value EV = M + T must be > 0. The EBM denominator IS EV, so a
    non-positive EV (cash and investments exceeding market cap plus debt, T >= M)
    flips the sign of the ratio; those names are set NaN. No positive floor
    above zero: scoring is a within-sector percentile rank, so magnitude is moot and
    the small-positive-EV tail keeps its large values.
  - Non-finite results -> NaN.
  - fxusd != 1 -> NaN: the four balance-sheet inputs stay in one currency
    (investmentsc has no *usd form and M is USD; non-USD reporters are <=0.06% of
    members).
  - debt gate: SF1.debt is populated for financials whose debtc/debtnc are null
    (the unclassified balance-sheet block, ~20% of rows), a different balance-sheet
    format rather than a zero debt; names with debtc null are NaN (known trap
    unclassified_balance_sheet_block). OSAP likewise leaves dltt/dlc un-zero-filled.
  - equity is NOT required positive: negative book is a real value (the numerator
    of EBM), as in OSAP.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? A firm with no new filing keeps
  equity, cashneq, investmentsc and debt fixed but M moves with price every month,
  so EBM changes continuously; there is no stale-value default.
  The only exact-0 case is equity + T = 0 to the dollar: effectively never.
  What share of the universe does nothing? Expected modal share of any single value
  well under 0.1%; not measured here (preflight measures it).
  Tie handling: null (guards above); no zero-fill of the ratio. The real risk is
  the tail (EV small and positive, or EV <= 0), handled by the EV > 0 guard.

DEVIATIONS FROM OSAP:
  - dc (convertible debt), dvpa (preferred dividends in arrears), tstkp (treasury
    preferred): no SF1 field; all three are in OSAP's zero-fill list, so 0. dc is 0
    for convertible issuers where OSAP has a value, so their T is overstated.
  - dltt + dlc -> SF1.debt (debtc + debtnc). INCLUDES operating lease liabilities
    from FY2019 filings (ASC 842) and bank repo.
  - ceq -> SF1.equity, which includes preferred stock (OSAP ceq excludes it).
  - che -> cashneq + investmentsc.fillna(0): financing receivables for captive
    finance names are included, banks/insurers understated. NaN only if cashneq is NaN.
  - Book side is the latest filed quarter (usually 0-3 months old, at most 15:
    max_fundamental_age_months) vs OSAP annual items at datadate + 6 months
    (6-17 months old). M is the month-end value in both.
  - mve_permco -> DAILY.marketcap (primary-class ticker, all-class shares), a
    few-percent level difference on <=2% of names.
  - EV > 0 guard, fxusd == 1 gate and the debtc gate are additions; OSAP has no EV
    guard and keeps only curcd == 'USD' reporters.
  - OSAP's abs(prc) > 5 portfolio filter and the annual June rebalance are not
    reproduced (universe and rebalance belong to the harness).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    f = ctx.fundamentals(["equity", "debt", "debtc", "cashneq", "investmentsc", "fxusd"])
    ceq = f["equity"].astype(float)
    debt = f["debt"].astype(float)
    che = f["cashneq"].astype(float) + f["investmentsc"].astype(float).fillna(0.0)
    usd = f["fxusd"].astype(float) == 1.0

    mcap = ctx.universe["mkt_cap_usd"].astype(float).reindex(f.index)
    m = mcap.where(mcap > 0)

    t = che - debt                     # net financial assets; dc = dvpa = tstkp = 0
    ev = m + t
    ev = ev.where(ev > 0)              # EV <= 0 is a sign flip -> NaN

    ebm = (ceq + t) / ev
    out = ebm.where(usd & f["debtc"].notna())   # unclassified block NaN (debt gate ruling)
    return out.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="EBM",
    col="f_ebm",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: high EBM is attractive (the long leg)
    weight=1.0,
    inputs=("SF1.equity", "SF1.debt", "SF1.debtc", "SF1.cashneq", "SF1.investmentsc", "SF1.fxusd", "DAILY.marketcap"),
    osap_acronym="EBM",
    source="Penman, Richardson and Tuna 2007 (Journal of Accounting Research)",
    lookback_months=15,             # latest filing within max_fundamental_age_months
    notes="(equity + T)/(M + T); T = cashneq + investmentsc - debt; dc=dvpa=tstkp=0; EV > 0 guard; fxusd==1; debtc gate",
    field_mappings=(
        ("compustat.ceq", "SF1.equity (ART)",
         "includes preferred stock (OSAP ceq excludes it); latest filing, not annual + 6-month lag; negative book kept"),
        ("compustat.che", "SF1.cashneq + SF1.investmentsc.fillna(0)",
         "approx: captive-finance receivables included, banks/insurers understated; NaN only where cashneq is NaN"),
        ("compustat.dltt_plus_dlc", "SF1.debt (ART)",
         "includes operating leases from FY2019 (ASC 842) and bank repo; gated on SF1.debtc notna (unclassified balance-sheet block -> NaN)"),
        ("compustat.dc", "none -> 0", "convertible debt; OSAP zero-fills when blank, here 0 for every firm (convertible issuers' T overstated)"),
        ("compustat.dvpa", "none -> 0", "OSAP zero-fill var; 0 for every firm"),
        ("compustat.tstkp", "none -> 0", "OSAP zero-fill var; 0 for every firm"),
        ("crsp.mve_permco", "DAILY.marketcap via ctx.universe['mkt_cap_usd']",
         "company-level all-class cap at the primary ticker's price; few-% level error on <=2% of names"),
        ("compustat.curcd", "SF1.fxusd", "gate fxusd == 1 (investmentsc has no *usd variant; kept so the inputs share one currency)"),
        ("guard", "EV > 0", "M + T <= 0 -> NaN (OSAP keeps inf/negative values); not in OSAP"),
    ),
)
