"""
XFIN — net external financing: net cash raised from shareholders and lenders in
the year (stock sold + debt issued - buybacks - dividends - debt retired),
scaled by year-end total assets. Firms that raise external capital are
predicted to earn LOWER returns.

OSAP: XFIN, Bradshaw, Richardson and Sloan 2006, Journal of Accounting and
Economics (Table 3). Predicted sign: - (SignalDoc Sign = -1: high net external
financing -> low returns), so ascending=False (HIGH raw is the short leg).
Spec: osap_source/cache/b4e911e6/XFIN/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  The CODE is followed, not the SignalDoc text. predictor.py computes
      (sstk - dv - prstkc + dltis - dltr + dlcch) / at,   dlcch.fillna(0),
  END-of-year assets, no |ratio| screen. The SignalDoc definition
  (sstk - dv - prstkc + dltis - dltr, scaled by at) OMITS dlcch; the code adds
  it, and the code is followed. SF1.ncfdebt is the NET debt flow INCLUDING the
  short-term / commercial-paper change, so the dlcch leg is subsumed in it.
  y = ctx.fundamentals(["ncfcommon", "ncfdiv", "ncfdebt", "assets"]), ART default
  (trailing-four-quarter flows and the assets level of the same filing,
  datekey <= signal):
      num = ncfcommon.fillna(0) + ncfdiv.clip(upper=0) + ncfdebt
      XFIN = num / assets.where(assets > 0)
  Sign conventions (verified against osap_source/field_map.yaml, sstk / dv /
  dltis entries):
    ncfcommon = NET common-equity cash flow, INFLOW-positive (issuance incl.
      option exercise minus repurchase), so sstk - prstkc == ncfcommon (exact for
      the net pair; a gross side alone is not reproducible and only the net
      enters this signal).
    ncfdiv = cash dividends paid, OUTFLOW-NEGATIVE; Compustat dv is positive, so
      -dv == +ncfdiv; a positive ncfdiv (0.19% of ART rows, wrong sign) is
      clipped to 0.
    ncfdebt = NET debt flow, ISSUANCE-positive: dltis - dltr + dlcch.
  Missing-value rules follow OSAP: sstk and prstkc are zero-filled upstream, so a
  null ncfcommon is 0; dv, dltis and dltr are NOT zero-filled, so a null ncfdiv
  or a null ncfdebt leaves the signal NaN (dlcch's own fillna(0) is inside
  ncfdebt). No |ratio| > 1 screen (OSAP has none for XFIN); the harness's
  per-month winsorisation handles the tails.
  The numerator equals the NetEquityFinance numerator plus the NetDebtFinance
  numerator. ART, not ARQ: a TTM flow LEVEL over a level, no year-over-year
  difference of a flow, so nothing smears under TTM and a single quarter's flow
  over assets would be wrong. Flows and assets share the reporting currency, so
  no fxusd gate. No year-ago filing is needed (END-of-year assets, not average).

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Exactly 0.0 (no issuance, no
  buyback, no dividend, no net debt flow: ncfcommon null -> 0, ncfdiv 0, ncfdebt 0).
  What share of the universe does nothing? Spec measurement over all 276 months:
  the exact 0 is the modal value at a mean 0.20% of scored names, max 0.58%
  (1999-03), never >= 5% or 10%; 1,180-2,719 distinct values; 10 qcut bins every
  month. The three-way zero is rare because ncfdebt == 0 (15% of non-null)
  rarely coincides with no equity flow and no dividend. Preflight decides.
  Tie handling: none designed; the zero is a real value (a genuine do-nothing
  firm), kept, and the harness averages ranks over ties. No denominator floor.

DEVIATIONS FROM OSAP:
  - sstk - prstkc -> SF1.ncfcommon.fillna(0): net, not gross; PREFERRED EXCLUDED
    (Compustat sstk/prstkc include it), so TARP-era financials 2008-2011 are off by
    $B (the predictor does not drop financials); taxes on net share settlement
    are excluded from ncfcommon.
  - dv -> SF1.ncfdiv.clip(upper=0): predominantly common-only while dv is common
    + preferred (included for combined-line filers, excluded where preferred is a
    separate CF line); NCI distributions excluded; null -> NaN as OSAP.
  - dltis - dltr + dlcch -> SF1.ncfdebt: net, not gross; the dlcch term and its
    fillna(0) are subsumed; null -> NaN as OSAP (a vendor 0-fill of an absent
    flow is not separable from a true zero).
  - SignalDoc/code discrepancy on dlcch: the SignalDoc text omits it, the code
    adds it; the code is followed (ncfdebt carries it).
  - timing: OSAP reads the fiscal year at datadate + 6 months, held 12 months;
    here the latest filed ART (0-3 months old, refreshed quarterly), trailing
    four quarters rather than the fiscal year, with no 6-month annual lag.
  - at: SF1.assets guarded > 0 (OSAP's at null/0 -> NaN or inf).
  - early window: a null cash-flow statement in the first TTM filings leaves
    coverage 52-59% in 1998-12..1999-02 and under 90% through 2000-11.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    y = ctx.fundamentals(["ncfcommon", "ncfdiv", "ncfdebt", "assets"])

    ncfcommon = y["ncfcommon"].astype(float).fillna(0.0)      # OSAP zero-fills sstk / prstkc
    ncfdiv = y["ncfdiv"].astype(float).clip(upper=0.0)        # -dv; NaN stays NaN (dv not zero-filled)
    ncfdebt = y["ncfdebt"].astype(float)                      # dltis - dltr + dlcch; null -> NaN
    num = ncfcommon + ncfdiv + ncfdebt

    assets = y["assets"].astype(float)
    score = num / assets.where(assets > 0)                    # sign-flip guard on the denominator
    return score.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    family="external_financing",                # Phase C, 2026-10-01: Cat.Economic "external financing" (decision phase_c_family_partition)
    name="XFIN",
    col="f_xfin",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: high net external financing is the short leg
    weight=1.0,
    inputs=("SF1.ncfcommon", "SF1.ncfdiv", "SF1.ncfdebt", "SF1.assets"),
    osap_acronym="XFIN",
    source="Bradshaw, Richardson and Sloan 2006 (Journal of Accounting and Economics)",
    lookback_months=15,             # latest filing (<= max_fundamental_age_months old)
    # No history_months: no SEP/DAILY price window is read.
    notes="(ncfcommon.fillna(0) + min(ncfdiv, 0) + ncfdebt) / assets, ART; null ncfdiv or ncfdebt -> NaN; no |ratio| screen",
    field_mappings=(
        ("sstk - prstkc (zero-filled)", "SF1.ncfcommon.fillna(0)",
         "NET common-equity flow, inflow-positive; PREFERRED EXCLUDED (Compustat includes it; TARP-era financials off by $B, financials not dropped); null -> 0 as OSAP zero-fill"),
        ("dv", "SF1.ncfdiv.clip(upper=0)",
         "outflow-negative so -dv == +ncfdiv; predominantly common-only vs dv common + preferred; null -> NaN (dv not zero-filled); positive values (0.19%) clipped to 0"),
        ("dltis - dltr + dlcch.fillna(0)", "SF1.ncfdebt",
         "NET debt flow incl. the short-term/CP change (dlcch subsumed, its zero-fill with it); issuance-positive; null -> NaN; SignalDoc text omits dlcch, code adds it, code followed"),
        ("at (year-end)", "SF1.assets", "same ART filing as the flows; guarded > 0"),
        ("time_avail_m (datadate + 6 months)", "SF1.datekey (ART)", "TTM flows at filing, quarterly refresh; no 6-month annual lag"),
    ),
)
