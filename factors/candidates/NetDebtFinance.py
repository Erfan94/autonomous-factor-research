"""
NetDebtFinance — net debt financing: net long-term debt raised plus the change
in current debt, scaled by average total assets. Firms that raise debt are
predicted to earn LOWER returns.

OSAP: NetDebtFinance, Bradshaw, Richardson and Sloan 2006, Journal of
Accounting and Economics (Table 3). Predicted sign: - (SignalDoc Sign = -1: LOW
net debt financing is the long leg).
Spec: osap_source/cache/b4e911e6/NetDebtFinance/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  y = ctx.fundamentals_yoy(["ncfdebt","assets","debt"])   (ART default; latest
      filing known at the signal and the same fiscal period one year earlier,
      aligned by reportperiod within 45 days)
  OSAP code: (dltis - dltr + dlcch) / (0.5 * (at + l12_at)), NaN where |ratio| > 1.
  Here: numerator = SF1.ncfdebt (ART trailing-four-quarter NET debt cash flow:
  issuance - repayment, incl. the short-term/CP net change), which is exactly
  the code's sum dltis - dltr + dlcch (the code's sign, dlcch added).
  avg = (assets + assets_lag) / 2, guard avg > 0 (else NaN);
  ratio = ncfdebt / avg; |ratio| > 1 -> NaN, as OSAP. ncfdebt null -> NaN
  (never zero-filled); non-finite -> NaN.
  Tie rule (standing rule applied literally): SF1.debt exactly 0 at BOTH the
  latest period and the year-ago period (debt and debt_lag via
  fundamentals_yoy) -> NaN; a zero flow there is structural (no debt to issue
  or repay), not information. A firm with debt at either end and zero net
  flow keeps its 0. A null debt is not a zero and does not trigger the rule.
  No debtc gate: OSAP has no dltt/dlc term, and ncfdebt is populated for the
  unclassified block (financials/REITs).
  Flow LEVEL over a 12-month span against average year-end assets: nothing
  smears under TTM; dimension is NOT ARQ (one quarter's flow over a year's
  average assets would be wrong).
  Score ascending=False (LOW net debt financing is the long leg).

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0.0 (no net debt
  flow). ncfdebt == 0 is 15.4% of non-null ART rows pooled; literally kept, 0.0
  is the modal value in every month at a 7.9%-13.6% share (>= 10% in 201 of 276
  months), a hard mass-point failure.
  What share of the universe does nothing after the tie rule? The spec measured
  the rule (debt == 0 at both year-ends -> NaN): it removes a median 7.5% of the
  scored names and leaves a modal share of 2.1%-10.3% (median 3.9%), >= 5% in 38
  months and >= 10% in 2 (2020-03 10.3%, 2020-04 10.0%), 9.5% at the 2021-11
  probe, 2.4% at the first probe and 4.7% at the middle one. The leftover zeros
  are firms with debt but zero net flow (median 3.5% of scored, up to 10.1%).
  This is close to the 10% hard-fail line at the last probe. Preflight decides.
  Tie handling: REMOVE the structural zeros (restrict the sample to names with
  debt at either end), as a coordinator decision (events.jsonl id
  netdebtfinance_ties): nulling every ncfdebt == 0 would also drop real
  zero-issuance borrowers and is not adopted. No floor, no null beyond that.

DEVIATIONS FROM OSAP:
  - dltis / dltr / dlcch -> the single net SF1.ncfdebt: exact for OSAP's sum,
    not usable for one gross side; ncfdebt includes the short-term/CP leg that
    dlcch carries, so dlcch's zero-fill (dlcch null -> 0) is subsumed.
  - ncfdebt null -> NaN; the vendor may 0-fill an absent flow (true no-activity
    and 0-fill are not separable; 99.9% of zero rows have operating cash flow
    present). ncfdebt is null for 3.0% of the universe (median), >10% in
    1998-12..2000-11 where the cash-flow statement is missing.
  - tie rule: debt exactly 0 at both year-ends -> NaN (no OSAP analogue; OSAP
    keeps the zeros).
  - avg assets > 0 guard (OSAP has none); assets_lag by reportperiod
    (fundamentals_yoy), not shift(12) of monthly rows; a missing year-ago
    period is NaN. Early window: SF1 starts 1997Q4, so the first signal months
    lack a year-ago filing (spec: 43.4% coverage at 1998-12-31, 74.5%-89.1%
    from 1999-03).
  - timing: ART TTM flow (rolling four quarters, refreshed quarterly) and the
    latest ART assets against the year-ago period, not OSAP's annual items with
    datadate + 6 months held; the 6-month availability lag is not reproduced.
  - no fxusd gate (same-reporting-currency ratio).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    y = ctx.fundamentals_yoy(["ncfdebt", "assets", "debt"])
    ncfdebt = y["ncfdebt"].astype(float)
    assets = y["assets"].astype(float)
    assets_lag = y["assets_lag"].astype(float)
    avg = (assets + assets_lag) / 2.0
    ratio = ncfdebt / avg.where(avg > 0)
    ratio = ratio.where(ratio.abs() <= 1.0)          # OSAP: |ratio| > 1 -> NaN
    # tie rule: no debt at either year-end (exactly 0, not null) AND zero net flow -> structural
    # zero, removed; a non-zero flow against vendor-0 debt keeps its value
    no_debt = (y["debt"].astype(float) == 0) & (y["debt_lag"].astype(float) == 0) & (ncfdebt == 0)
    return ratio.where(~no_debt).replace([np.inf, -np.inf], np.nan)


# ASC 842 break (alpha_review batch15-16 M1): SF1.debt includes operating-lease liabilities
# from FY2019, so the share of the universe with debt == 0 falls from 9.1% (2018) to 2.9%
# (2019) and the tie rule removes far fewer names from 2019; lessees without financial debt
# and with ncfdebt == 0 return as exact zeros (mode 10.3% / 10.0% in 2020-03 / 2020-04,
# 9.5% at the 2021-11 probe). SF1.debt is read without the debtc gate because it feeds only
# the tie test, never the value (debt populated on 99.86% of unclassified rows).
FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="NetDebtFinance",
    col="f_netdebtfinance",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: LOW net debt financing is the long leg
    weight=1.0,
    inputs=("SF1.ncfdebt", "SF1.assets", "SF1.debt"),
    osap_acronym="NetDebtFinance",
    source="Bradshaw, Richardson and Sloan 2006 (Journal of Accounting and Economics)",
    lookback_months=31,             # latest filing up to 15 months old + year-ago period 12 months earlier + ~4m report-period-to-filing lag
    notes="ncfdebt (ART TTM net debt flow) / average ART assets; |ratio|>1 NaN; debt==0 at both year-ends NaN (tie rule); sign -1",
    field_mappings=(
        ("compustat.dltis - dltr + dlcch", "SF1.ncfdebt (ART)",
         "APPROX: net flow collapses the gross items, exact for OSAP's sum; includes the short-term/CP leg (dlcch); null -> NaN, vendor 0-fill inseparable"),
        ("compustat.at (average of at and l12_at)", "(SF1.assets + SF1.assets_lag)/2 via ctx.fundamentals_yoy",
         "year-ago assets by reportperiod (45-day tolerance); avg > 0 guard"),
        ("abs(ratio) > 1 -> NaN", "same", "1:1"),
        ("(none) zero flow kept", "SF1.debt == 0 at both year-ends -> NaN",
         "tie rule (netdebtfinance_ties): structural zero flows removed; debt with zero net flow keeps 0"),
        ("datadate + 6 months availability", "latest ART filing with datekey <= signal",
         "rolling quarterly refresh of a four-quarter flow; OSAP's 6-month lag and annual step not reproduced"),
    ),
)
