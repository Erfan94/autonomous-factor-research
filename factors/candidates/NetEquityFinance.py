"""
NetEquityFinance — net equity financing after dividends, scaled by average assets:
(stock sold - stock repurchased - cash dividends) / average total assets.
Firms that raise external equity (and do not pay out) are expected to underperform.

OSAP: NetEquityFinance, Bradshaw, Richardson, Sloan 2006 (Journal of Accounting and
Economics, Table 3). Predicted sign: - (SignalDoc Sign = -1: high net equity financing
-> low returns), so ascending=False (HIGH raw is the UNATTRACTIVE / short leg; the
long leg is the most negative value, i.e. net payers).
Spec: osap_source/cache/b4e911e6/NetEquityFinance/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  The CODE is followed, not the SignalDoc text. predictor.py computes
      (sstk - prstkc - dv) / (0.5 * (at + at twelve months earlier)),  |ratio| > 1 -> NaN.
  The SignalDoc Detailed Definition reads "sale of common stock minus purchase of common
  stock, scaled by average total assets" and OMITS dv; the code subtracts dv (total cash
  dividends), so the published series is net equity financing AFTER dividends (negative
  for payers). The dividend term is kept here, as in the code.
  ctx.fundamentals_yoy(["assets", "ncfcommon", "ncfdiv"], years=1), ART default (latest
  filing and the filing for the same fiscal period one year earlier, aligned by
  reportperiod, never fundamentals(lag_months=12)):
      num = ncfcommon.fillna(0) + ncfdiv.clip(upper=0)
      avg = 0.5 * (assets + assets_lag)
      score = num / avg.where(avg > 0);   |score| > 1 -> NaN (OSAP's own sample screen)
  Sign conventions (verified against osap_source/field_map.yaml, sstk and dv entries):
    ncfcommon = NET common-equity cash flow, INFLOW-positive (issuance incl. option
      exercise minus repurchase), so sstk - prstkc == ncfcommon (exact for the net pair;
      a gross side alone is not reproducible, and only the net enters this signal).
    ncfdiv = cash dividends paid, OUTFLOW-NEGATIVE; Compustat dv is positive, so
      -dv == +ncfdiv. A positive ncfdiv (0.19% of ART rows, wrong sign) is clipped to 0.
  Zero-fills follow OSAP: sstk and prstkc are zero-filled by OSAP (zero_fill_vars), so a
  null ncfcommon is set to 0; dv is NOT zero-filled by OSAP (only dvt is), so a null
  ncfdiv leaves the signal NaN. ncfcommon is null on 98.9% of rows with null ncfo (no
  cash-flow statement), so the fill mostly supplies real zeros for CF-reporting filers.
  ART (TTM flows) and the assets level at the same filing; the average spans the same
  window. A TTM LEVEL over a level, no year-over-year difference of a flow, so nothing
  smears and no dimension override is needed. Flows and assets are in the same reporting
  currency, so the ratio needs no fxusd gate.
  Raw ratio, no log, no winsorising.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0.0 (no issuance, no buyback, no
  dividend: ncfcommon null or 0 together with ncfdiv == 0).
  What share of the universe does nothing? Spec measurement over all 276 months: the
  exact zero is the modal value at 0.96-4.13% of scored names (median 1.96%), 1,060-2,313
  distinct values on 1,074-2,379 scored names; below the 5% warn and the 10% cliff at
  every month. Dividend non-payers (60% of non-null ncfdiv is exact 0) are not a mass
  point because ncfcommon is non-zero for most of them (14.5% of non-null ncfcommon is
  exact 0).
  Tie handling: none designed; the zero is a real value (a genuine do-nothing firm), kept,
  and the harness averages ranks over ties. Preflight measures the mass point.

DEVIATIONS FROM OSAP:
  - ncfcommon EXCLUDES preferred issuance/redemption (Compustat sstk/prstkc include it).
    This predictor does NOT drop financials, so TARP-era financials 2008-2011 carry
    numerators off by tens of $B (C, JPM, BAC, WFC, GS common-only raises with the
    preferred legs absent). Not corrected.
  - SignalDoc/code discrepancy on dv: the text omits it, the code subtracts it; the code
    is followed. ncfdiv is predominantly common-only while dv is common + preferred
    (included for combined-line filers, excluded where preferred is a separate CF line;
    FNMA/FMCC = 0 against $6-17B/yr preferred dividends); NCI distributions are excluded.
  - Taxes paid on net share settlement and option-exercise flows sit inside ncfcommon.
  - Timing: OSAP reads the fiscal year at datadate + 6 months, held 12 months; here the
    latest filed ART (0-3 months old, refreshed quarterly) with no 6-month annual lag, and
    the year-ago assets by reportperiod (fundamentals_yoy, tolerance 45 days) rather than
    shift(12) on the monthly panel. The window is the trailing four quarters, not the
    fiscal year.
  - Coverage: the first signal months (1998-12..1999-02) are thin (year-ago filings few
    at the snapshot start); assets <= 0 is guarded (a zero gives inf in OSAP).
  - OSAP applies no SIC, ceq or price screen to this predictor; none is applied.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    y = ctx.fundamentals_yoy(["assets", "ncfcommon", "ncfdiv"], years=1)

    ncfcommon = y["ncfcommon"].astype(float).fillna(0.0)      # OSAP zero-fills sstk / prstkc
    ncfdiv = y["ncfdiv"].astype(float).clip(upper=0.0)        # -dv; NaN stays NaN (dv not zero-filled)
    num = ncfcommon + ncfdiv

    avg = 0.5 * (y["assets"].astype(float) + y["assets_lag"].astype(float))
    score = num / avg.where(avg > 0)                          # sign-flip guard on the denominator

    score = score.replace([np.inf, -np.inf], np.nan)
    return score.where(score.abs() <= 1.0)                    # OSAP: |ratio| > 1 -> NaN


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="NetEquityFinance",
    col="f_nef",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: high net equity financing is the short leg
    weight=1.0,
    inputs=("SF1.ncfcommon", "SF1.ncfdiv", "SF1.assets"),
    osap_acronym="NetEquityFinance",
    source="Bradshaw, Richardson, Sloan 2006 (Journal of Accounting and Economics)",
    lookback_months=31,             # latest filing (<=15 months old) plus its year-ago period and tolerance
    # No history_months: no SEP/DAILY price window is read.
    notes=("(ncfcommon.fillna(0) + min(ncfdiv, 0)) / mean(assets, year-ago assets), ART, yoy by "
           "reportperiod; |ratio| > 1 -> NaN; null ncfdiv -> NaN"),
    field_mappings=(
        ("sstk - prstkc (zero-filled)", "SF1.ncfcommon.fillna(0)",
         "NET common-equity flow, inflow-positive; PREFERRED EXCLUDED (Compustat includes it; TARP-era financials off by $B, financials not dropped); null -> 0 as OSAP zero-fill"),
        ("dv (code; SignalDoc text omits it)", "SF1.ncfdiv.clip(upper=0)",
         "outflow-negative so -dv == +ncfdiv; predominantly common-only vs dv common + preferred; null -> NaN (dv is not zero-filled); positive values (0.19%) clipped to 0"),
        ("at, 12-month lag of at", "SF1.assets and assets_lag via fundamentals_yoy",
         "year-ago filing aligned by reportperiod, not shift(12); average guarded > 0"),
        ("|ratio| > 1 -> NaN", "score.where(abs(score) <= 1)", "as OSAP predictor.py"),
        ("time_avail_m", "SF1.datekey (ART)", "TTM flows at filing, quarterly refresh; no 6-month annual lag"),
    ),
)
