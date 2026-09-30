"""
dNoa — change in net operating assets: the twelve-month change in (operating
assets - operating liabilities) scaled by prior-year total assets. Firms whose
balance sheet has grown heavy in operating assets over the year (accruals not yet
converted to cash) are predicted to earn LOWER returns.

OSAP: dNoa, Hirshleifer, Hou, Teoh and Zhang 2004, Journal of Accounting and
Economics (Table 7B DeltaNOA). Predicted sign: - (SignalDoc Sign = -1: LOW dNoa is
the long leg; ascending=False).
Spec: osap_source/cache/b4e911e6/dNoa/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  y = ctx.fundamentals_yoy(["assets","liabilities","debt","cashneq","investmentsc"])
      (ART default; latest filing known at the signal and the same fiscal period one
      year earlier, aligned by reportperiod within 45 days; levels only, so ART equals
      ARQ on the same reportperiod: no flow, no TTM smear, no dimension override)
  OSAP: OA = at - che; OL = at - dltt - mib - dlc - pstk - ceq;
        NOA = OA - OL = dltt + dlc + mib + pstk + ceq - che;
        dNoa = (NOA - NOA_lag12) / at_lag12.  dltt, dlc, mib, pstk are filled with 0
        by the predictor itself; at and ceq are not.
  Here: che = cashneq + investmentsc.fillna(0); dltt + dlc -> SF1.debt; and
  mib + pstk + ceq := assets - liabilities (Compustat mib + pstk + ceq ~ at - lt;
  preferred is on the financing side in OSAP's OL too; SF1.equity is not an input).
      NOA_s = debt_s + (assets_s - liabilities_s) - che_s      for s in {now, lag}
      dNoa  = (NOA - NOA_lag) / assets_lag,   assets_lag <= 0 or null -> NaN.
  Non-finite -> NaN. Numerator and denominator are in the filer's reporting currency
  (same-currency ratio), so no fxusd gate.

  NO debtc/debtnc GATE (coordinator decision dnoa_debt_no_gate): OSAP's dNoa
  zero-fills dltt and dlc itself, so it scores the financials/REITs whose balance
  sheet is unclassified. SF1.debt (debtc + debtnc) is populated on 99.86% of those
  unclassified rows, where debtc/debtnc are null, so they are scored here too. For
  banks and insurers SF1.debt includes repo and short-term borrowings (a larger
  and differently-composed debt than Compustat dltt + dlc), and their che is
  cashneq only (investmentsc is null on that block, their securities sit in
  SF1.investments with loans), an understatement SF1 cannot repair. cashneq null
  -> NaN (OSAP zero-fills che).

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0 (a balance sheet unchanged
  over the twelve months), essentially a stale-filing artefact, which
  fundamentals_yoy converts to NaN (a stale or missing year-ago period is never 0).
  The fill terms (investmentsc in che; SF1 debt zero-filled where not reported) are
  components of a difference of levels, not the signal, and do not tie it. The
  ratio is continuous, with no default and no signal zero-fill.
  What share of the universe does nothing? Spec measured over 276 months on the
  scored cross-section: exact-zero share median 0.000%, mean 0.016%, max 0.136%
  (<= 2 names); modal share median 0.068%, max 0.144%; distinct values equal n
  scored (nearly); 10 qcut bins in every month. (Measured on the gated variant; the
  ungated bank/insurer block adds scored names and is to be confirmed by preflight.)
  Tie handling: none needed; no noise-breaking, the harness averages ties.

DEVIATIONS FROM OSAP:
  - dltt + dlc -> SF1.debt, NOT gated and NOT split into debtc/debtnc. SF1.debt
    includes capital AND operating lease obligations: ASC 842 (FY2019 adoption) lifts
    debt for lessees by the lease liability while assets and liabilities rise by the
    same amount (assets - liabilities unchanged), so NOA_level steps UP for lessees
    and the twelve-month change carries a one-off lessee spike in 2019-2021 signal
    months. Compustat dltt/dlc exclude operating leases, so OSAP has no such step.
    Declared, not adjusted (3 of 23 window years). Bank debt includes repo and
    short-term borrowings.
  - mib + pstk + ceq -> assets - liabilities. Preferred stock is on the financing side
    in both OSAP and SF1.equity, so this is not a deviation. Redeemable noncontrolling
    interest and temporary/SPAC equity, which OSAP leaves inside OL (non-redeemable
    mib only), sit on the financing side here, so NOA_level is higher by those
    amounts; they largely cancel in the twelve-month change except across SPAC
    issuance and redemption in 2019-23.
  - che -> cashneq + investmentsc.fillna(0): overstates for captive-finance and
    vendor-financing names (investmentsc holds current financing receivables) and
    understates banks/insurers; cashneq null -> NaN.
  - Timing: the four-quarter span is a rolling year refreshed quarterly (latest ART
    filing vs the same period a year earlier by reportperiod), not the fiscal year
    held 12 months; no 6-month lag is reproduced. A missing year-ago period is NaN.
    Early window: SF1 starts 1997Q4, so the first two signal months lack a year-ago
    filing (spec: coverage below 40% at 1998-12 and 1999-01 on the gated variant).
  - assets_lag > 0 guard (OSAP excludes only 0).
  - Upstream row filter (at, prcc_c, ni non-null) not reproduced.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _noa_level(debt, assets, liabilities, che):
    # mib + pstk + ceq := assets - liabilities (equity cancels); dltt + dlc := debt
    return debt + (assets - liabilities) - che


def _compute(ctx):
    y = ctx.fundamentals_yoy(["assets", "liabilities", "debt", "cashneq", "investmentsc"])
    f = lambda c: y[c].astype(float)

    che = f("cashneq") + f("investmentsc").fillna(0.0)
    che_lag = f("cashneq_lag") + f("investmentsc_lag").fillna(0.0)

    # OSAP zero-fills dltt/dlc itself; a missing balance sheet still gives NaN through assets
    noa = _noa_level(f("debt").fillna(0.0), f("assets"), f("liabilities"), che)
    noa_lag = _noa_level(f("debt_lag").fillna(0.0), f("assets_lag"), f("liabilities_lag"), che_lag)

    assets_lag = f("assets_lag")
    dnoa = (noa - noa_lag) / assets_lag.where(assets_lag > 0)
    return dnoa.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="dNoa",
    col="f_dnoa",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: LOW change in NOA is the long leg
    weight=1.0,
    inputs=("SF1.assets", "SF1.liabilities", "SF1.debt", "SF1.cashneq", "SF1.investmentsc"),
    osap_acronym="dNoa",
    source="Hirshleifer, Hou, Teoh and Zhang 2004 (Journal of Accounting and Economics)",
    lookback_months=31,             # latest filing up to 15 months old + year-ago period 12 months earlier + ~4m report-period-to-filing lag
    notes="(NOA - NOA_lag)/assets_lag; NOA = debt + assets - liabilities - (cashneq + investmentsc); ungated (OSAP zero-fills dltt/dlc); ASC 842 step 2019-21; sign -1",
    field_mappings=(
        ("compustat.at (OA and OL; at_lag12)", "SF1.assets (ART), SF1.assets_lag via ctx.fundamentals_yoy",
         "same fiscal period one year earlier by reportperiod (45-day tolerance); missing -> NaN; guard assets_lag > 0"),
        ("compustat.che (zero-filled)", "SF1.cashneq + SF1.investmentsc.fillna(0)",
         "APPROX: overstates for captive-finance/vendor-financing names, understates banks/insurers; cashneq null -> NaN (OSAP zero-fills che)"),
        ("compustat.dltt + dlc (zero-filled by the predictor)", "SF1.debt (ART), no debtc/debtnc gate",
         "APPROX: includes operating-lease liabilities from FY2019 (ASC 842) -> lessee step in 2019-21 signal months; "
         "for banks/insurers includes repo and short-term borrowings; populated on unclassified balance sheets, which are scored as in OSAP"),
        ("compustat.mib (zero-filled) + pstk (zero-filled) + ceq", "SF1.assets - SF1.liabilities (equity cancels)",
         "preferred is financing-side in OSAP and SF1; redeemable NCI and temporary/SPAC equity sit on the financing side here (NOA_level higher), mostly cancelling in the change"),
        ("datadate + 6 months availability", "latest ART filing with datekey <= signal",
         "rolling quarterly refresh; OSAP's 6-month lag and annual step not reproduced"),
    ),
)
