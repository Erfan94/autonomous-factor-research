"""
PctTotAcc — percent total accruals: net income not accounted for by operating,
investing and financing cash flow, net equity issuance and dividends, scaled by
ABSOLUTE net income; high accruals are predicted to earn lower returns.

OSAP: PctTotAcc, Hafzalla, Lundholm and Van Winkle 2011, The Accounting Review
(Table 5A). Predicted sign: - (SignalDoc Sign = -1).
Spec: osap_source/cache/b4e911e6/PctTotAcc/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  OSAP: (ni - (prstkcc - sstk + dvt + oancf + fincf + ivncf)) / abs(ni)
  Sharadar, SF1 ART (trailing four quarters, as filed), one ctx.fundamentals call:
      ni            = netinc                    null -> NaN   (OSAP: not zero-filled)
      oancf         = ncfo                      null -> NaN   (not zero-filled)
      fincf         = ncff                      null -> NaN   (not zero-filled)
      ivncf         = ncfi                      null -> NaN   (not zero-filled)
      prstkcc-sstk  = -ncfcommon  (fillna(0))   OSAP zero-fills both prstkcc and sstk
      dvt           = -min(ncfdiv, 0)  (fillna(0))   OSAP zero-fills dvt
  Sign conventions (field_map): ncfcommon is the NET common-equity flow,
  inflow-positive (issuance minus repurchase), so prstkcc - sstk = -ncfcommon;
  ncfdiv is cash dividends paid, outflow-NEGATIVE, so dvt = -ncfdiv; the 0.0-0.6%
  of rows with a positive ncfdiv are the wrong sign and are clipped to 0.
      numerator   = ni - (prstkcc_minus_sstk + dvt + oancf + fincf + ivncf)
      denominator = abs(ni), NaN where ni == 0
      score       = numerator / denominator
  The numerator is taken as coded in OSAP, which adds net repurchase and dividends
  on top of fincf although fincf already contains them; it is replicated as coded.
  The absolute value means a loss-making firm is not sign-flipped (by design of
  the OSAP ratio), so the "den > 0" guard is applied to abs(ni), not to ni.
  ART (TTM) is the right dimension: all six inputs are TTM flows of the same
  window in one ratio, there is no year-over-year difference of a flow, nothing
  smears; no dimension override.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? 0 / abs(ni), but ni == 0 is NaN
  here and the cash-flow totals are essentially never all zero, so no value is a
  mode. Continuous ratio of flows.
  What share of the universe does nothing? Spec measurement on 276 months: modal
  value share of scored names 0.04-0.17% (median 0.05%), 1,171-2,725 distinct
  values, ten qcut bins everywhere; ni == 0 is 0.00-0.09% of the universe.
  Tie handling: null. ni == 0 gives NaN and blend_ranks renormalises; average
  rank for the rest. Tiny |ni| denominators give |score| > 10 on 1.8-8.1% of
  scored names: rank (and the harness winsorisation), never z-score.

DEVIATIONS FROM OSAP:
  - Preferred-stock netting: Compustat sstk, prstkcc and dvt include preferred
    issuance/redemption and preferred dividends, and those are netted inside
    fincf. Sharadar ncfcommon excludes preferred and ncfdiv is mostly
    common-only, so preferred flows stay un-netted inside ncff. The algebra
    (ncff already contains ncfcommon and ncfdiv) leaves
    ni - (ncfo + ncfi + ncff - ncfcommon - ncfdiv); the preferred leg is the
    difference from OSAP (material for financials in 2008-11, TARP).
  - Net-share-settlement tax and option-exercise flows sit inside ncfcommon.
  - ART (trailing four quarters, known at datekey) replaces the fiscal year at
    datadate + 6 months, so the signal refreshes quarterly and is available
    earlier than OSAP's stamp.
  - ni == 0 -> NaN (OSAP gives inf).
  - Financials and utilities are not dropped (OSAP has no sample restriction).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    f = ctx.fundamentals(["netinc", "ncfcommon", "ncfdiv", "ncfo", "ncff", "ncfi"])
    ni = f["netinc"].astype(float)
    oancf = f["ncfo"].astype(float)
    fincf = f["ncff"].astype(float)
    ivncf = f["ncfi"].astype(float)
    # OSAP zero-fills prstkcc, sstk and dvt; ni, oancf, fincf, ivncf are not filled.
    net_rep = -f["ncfcommon"].astype(float).fillna(0.0)          # prstkcc - sstk
    dvt = -(f["ncfdiv"].astype(float).fillna(0.0).clip(upper=0.0))   # >= 0
    num = ni - (net_rep + dvt + oancf + fincf + ivncf)
    den = ni.abs()
    return num / den.where(den > 0)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="PctTotAcc",
    col="f_pcttotacc",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: HIGH accruals earn LOWER returns
    weight=1.0,
    inputs=("SF1.netinc", "SF1.ncfcommon", "SF1.ncfdiv", "SF1.ncfo", "SF1.ncff", "SF1.ncfi"),
    osap_acronym="PctTotAcc",
    source="Hafzalla, Lundholm and Van Winkle 2011 (The Accounting Review)",
    lookback_months=15,             # one ART filing, age-limited
    notes="(ni - (prstkcc - sstk + dvt + oancf + fincf + ivncf)) / |ni|, SF1 ART; ni == 0 NaN; preferred flows un-netted in ncff",
    field_mappings=(
        ("compustat.ni", "SF1.netinc (ART)", "null -> NaN as OSAP; after NCI"),
        ("compustat.prstkcc - compustat.sstk", "-SF1.ncfcommon (ART), null -> 0",
         "NET common-equity flow, preferred excluded; OSAP zero-fills both terms"),
        ("compustat.dvt", "-min(SF1.ncfdiv, 0) (ART), null -> 0",
         "outflow-negative sign flipped; positive rows clipped; mostly common-only dividends; OSAP zero-fills dvt"),
        ("compustat.oancf", "SF1.ncfo (ART)", "null -> NaN as OSAP"),
        ("compustat.fincf", "SF1.ncff (ART)",
         "preferred issuance/redemption and preferred dividends are NOT netted out of ncff, unlike Compustat fincf netting; null -> NaN as OSAP"),
        ("compustat.ivncf", "SF1.ncfi (ART)", "null -> NaN as OSAP"),
        ("abs(ni) == 0 -> inf", "NaN", "zero-net-income firms unscored instead of inf"),
        ("fiscal year at datadate + 6 months", "ART as of datekey", "TTM as filed, refreshed quarterly, available earlier"),
    ),
)
