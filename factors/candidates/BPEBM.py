"""
BPEBM — book-to-price minus enterprise book-to-market: the part of book-to-market
that is financial leverage (net financial assets T scale book and market cap
differently), which OSAP predicts is followed by lower returns when high.

OSAP: BPEBM, Penman, Richardson and Tuna 2007, Journal of Accounting Research
(Table 1D). Predicted sign: - (high BPEBM earns lower returns; long D1, short D10).
Spec: osap_source/cache/b4e911e6/BPEBM/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  M  = ctx.universe["mkt_cap_usd"]                  (DAILY.marketcap at the month-end)
  T  = che - debt, with che = SF1.cashneq + SF1.investmentsc.fillna(0) and
       debt = SF1.debt (ART, latest filing known at the signal date).
       OSAP's  T = che - dltt - dlc - dc - dvpa + tstkp  with dc = dvpa = tstkp = 0.
  BP = SF1.equity / M;   EBM = (equity + T) / (M + T);   score = BP - EBM.
  Raw ratio difference, no log, no winsorising. ascending=False: a LOW BPEBM
  is attractive (the long leg), matching SignalDoc Sign = -1.

GUARDS (every denominator; a negative one is a sign flip, not an outlier):
  - M > 0.
  - Enterprise value EV = M + T must be > 0. T = che - debt, so M + T < 0 means net
    debt exceeds market cap, and the EBM denominator changes sign there (a sign flip,
    not an outlier). Names with EV <= 0 are set NaN. No positive floor above zero is
    imposed: scoring is a within-sector percentile rank, so magnitude is moot, and the
    heavily levered names (net debt close to M, EV small and positive) are the
    leverage tail this signal is built on; they keep their (large) values.
  - Non-finite results -> NaN.
  - fxusd != 1 -> NaN. SF1 does carry equityusd, debtusd and cashnequsd, but
    investmentsc has no *usd form and M is already USD; the gate is kept so all four
    balance-sheet inputs are in one currency without a mixed USD/local construction
    (non-USD reporters are <=0.06% of members).
  - equity is NOT required positive: negative book is a real value (negative BP,
    and the numerator of EBM), as in OSAP.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? A firm with no new filing keeps
  equity, cashneq, investmentsc and debt fixed but M moves with price every
  month, so BPEBM changes continuously; there is no stale-value default.
  The only exact-0 case is T = 0 (cash-and-STI equal to debt to the dollar, or
  both zero: SF1.debt is exactly 0 on ~15% of ART rows, cashneq is rarely 0),
  a small fraction of a percent expected; equity == M is ~0.
  What share of the universe does nothing? Estimated well under 1% at exactly 0;
  not measured here (preflight measures it).
  Tie handling: null (guards above); no zero-fill of the ratio. A mass at 0 that
  preflight finds would be handled by restricting to names with T != 0, not by
  flooring. The real risk is the sign flip at EV <= 0, which the EV > 0 guard nulls.

DEVIATIONS FROM OSAP:
  - dc (convertible debt), dvpa (preferred dividends in arrears), tstkp (treasury
    preferred): no SF1 field; all three are in OSAP's zero-fill list, so 0. dc is
    0 for convertible issuers where OSAP has a value, so their T is overstated.
  - dltt + dlc -> SF1.debt (debtc + debtnc, 99.99% agreement). INCLUDES operating
    lease liabilities from FY2019 filings (ASC 842) and bank repo; populated for
    financials where debtc/debtnc are ~20% null. debtnc alone is not used.
  - ceq -> SF1.equity, which includes preferred stock (OSAP ceq excludes it).
  - che -> cashneq + investmentsc.fillna(0): financing receivables for captive
    finance names are included, banks/insurers understated. NaN only if cashneq is NaN.
  - Book side is the latest filed quarter (0-3 months old, capped at
    max_fundamental_age_months) vs OSAP annual items at datadate + 6 months
    (6-17 months old). M is the month-end value in both.
  - mve_permco -> DAILY.marketcap (primary-class ticker, all-class shares), a
    few-percent level difference on <=2% of names.
  - EV > 0 guard and fxusd == 1 gate are additions; OSAP has no guard and keeps
    only curcd == 'USD' reporters.
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
    ev = ev.where(ev > 0)              # EV <= 0 (net debt >= M) is a sign flip -> NaN

    bp = ceq / m
    ebm = (ceq + t) / ev
    out = (bp - ebm).where(usd & f["debtc"].notna())   # unclassified block NaN (debt gate ruling)
    return out.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="BPEBM",
    col="f_bpebm",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: low BPEBM is attractive (the long leg)
    weight=1.0,
    inputs=("SF1.equity", "SF1.debt", "SF1.debtc", "SF1.cashneq", "SF1.investmentsc", "SF1.fxusd", "DAILY.marketcap"),
    osap_acronym="BPEBM",
    source="Penman, Richardson and Tuna 2007 (Journal of Accounting Research)",
    lookback_months=15,             # latest filing within max_fundamental_age_months
    notes="BP - EBM; T = cashneq + investmentsc - debt; dc=dvpa=tstkp=0; EV > 0 guard; fxusd==1",
    field_mappings=(
        ("compustat.ceq", "SF1.equity (ART)",
         "includes preferred stock (OSAP ceq excludes it); latest filing, not annual + 6-month lag; negative book kept"),
        ("compustat.che", "SF1.cashneq + SF1.investmentsc.fillna(0)",
         "approx: captive-finance receivables included, banks/insurers understated; NaN only where cashneq is NaN"),
        ("compustat.dltt_plus_dlc", "SF1.debt (ART)",
         "includes operating leases from FY2019 (ASC 842) and bank repo; debtnc alone not used; populated for financials"),
        ("compustat.dc", "none -> 0", "convertible debt; OSAP zero-fills when blank, here 0 for every firm (convertible issuers' T overstated)"),
        ("compustat.dvpa", "none -> 0", "OSAP zero-fill var; 0 for every firm"),
        ("compustat.tstkp", "none -> 0", "OSAP zero-fill var; 0 for every firm"),
        ("crsp.mve_permco", "DAILY.marketcap via ctx.universe['mkt_cap_usd']",
         "company-level all-class cap at the primary ticker's price; few-% level error on <=2% of names"),
        ("compustat.curcd", "SF1.fxusd", "gate fxusd == 1 (investmentsc has no *usd variant; kept so the inputs share one currency)"),
        ("guard", "EV > 0", "M + T <= 0 (net debt >= market cap) -> NaN (OSAP keeps inf/negative values); not in OSAP"),
    ),
)
