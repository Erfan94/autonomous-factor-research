"""
ChAssetTurnover — change in sales over average net operating assets (a rise
in asset turnover signals improving operating efficiency / sales growth not
yet priced).

OSAP: ChAssetTurnover, Soliman 2008 (The Accounting Review), Table 7 Model 1
DeltaATO. Predicted sign: + (SignalDoc Sign = +1, so ascending=True).
Spec: osap_source/cache/b4e911e6/ChAssetTurnover/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  Report-period-aligned ART filings at three balance-sheet dates (latest P,
  P-1y, P-2y; ctx.fundamentals_yoy with years=1 and years=2) and sale at two:
    NOA(d) = receivables + inventory + ppnenet + intangibles
             - payables - lo,                lo = liabilitiesnc - debtnc
    AT(P)   = revenue(P)   / ((NOA(P)   + NOA(P-1y)) / 2)
    AT(P-1) = revenue(P-1y)/ ((NOA(P-1y) + NOA(P-2y)) / 2)
    ChAT    = AT(P) - AT(P-1)
  Raw value is ChAT; ascending=True makes a HIGH change the long side.
  NOA is an operating net-asset base (operating assets less operating
  liabilities), not total assets; OSAP's comment "total assets" is misleading.
  ROUTE A (coordinator decision): OSAP's aco (other current operating assets)
  and lco (other current liabilities) have no SF1 field and OSAP itself
  zero-fills both, so those two terms are dropped (0 for every firm); they are
  NOT rebuilt from the assetsc / liabilitiesc identities.
  Guards: AT is defined only over a strictly positive average NOA; a negative
  AT (negative revenue) is NaN, as in OSAP (AT < 0 -> NaN). Null revenue is NaN,
  never a zero.
  revenue is the ART trailing-four-quarter sum, a FLOW used as a level at each
  of two dates exactly four quarters apart: the two TTM windows do not overlap,
  so AT(P) - AT(P-1) is a clean annual change. dimension stays the ART default
  (a single-quarter ARQ revenue over an annual-scale base would understate AT
  about 4x).

NULL HANDLING:
  - rect, invt, ap, intangibles are zero-filled as OSAP does, but ONLY on a
    filing whose total assets are reported (a null on a populated balance sheet
    is a real absent item; an empty row stays NaN). ppnenet is not zero-filled
    (OSAP forward-fills it, never zero-fills); a null ppnenet leaves that date
    and hence the score NaN. Sharadar itself stores 0 for a not-reported ppnenet.
  - lo: liabilitiesnc and debtnc are each fillna(0) (OSAP zero-fills lo). The
    unclassified balance sheets (financials, REITs; ~20% of rows) carry a null
    liabilitiesnc, so lo = 0 and their NOA reduces to rect + invt + ppnenet +
    intangibles - payables: a noisier base kept, as OSAP keeps financials.
  - revenue, and every year-ago filing, is NEVER zero-filled: a name with no
    known filing for a required date is NaN, not a zero change.
  - Signal months 1999-01 .. ~2000-02 are empty by construction: P-2y needs
    the 1997Q4 period and the earliest held period is 1997Q4.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? A firm with unchanged sales
  AND unchanged balance sheet at all three dates would give 0, but the
  average-base denominator moves with any balance change: essentially no
  operating firm. The real mass point is the zero-revenue firm: revenue = 0 at
  both P and P-1y gives AT = 0 twice and ChAT = exactly 0 (and -0.0 over a
  negative base in OSAP).
  What share of the universe does nothing? Exact-zero revenue is ~0.3-2% of
  the universe by year (both years zero is a subset, rising over time);
  preflight measures the modal-value share.
  Tie handling: null (the blend renormalises). ChAT is set to NaN where revenue
  is exactly zero at both dates: a firm with no sales has no turnover to
  change, the 0 is a placeholder and not a measurement. Zero revenue at only
  one date is kept (a real turnover change, -AT(P-1) or +AT(P)). Zero revenue
  over a negative or zero base is NaN through the positive-base guard.

DEVIATIONS FROM OSAP:
  - aco, lco: dropped (Route A), 0 for every firm. OSAP's zero is only the
    missing case; real values are non-zero for most industrials, so NOA is
    biased (aco and lco each several % of assets) and more bases are small or
    negative.
  - lo: liabilitiesnc - debtnc (liabilitiesnc contains long-term debt, >=
    debtnc on 99.8% of rows); residual is non-current deferred taxes.
  - lo on unclassified balance sheets: on ~1.3% of the unclassified-balance-sheet
    rows debtnc is populated while liabilitiesnc is null, so lo = 0 - debtnc =
    -debtnc and NOA is inflated by the long-term debt (OSAP's lo would be 0 or
    the classified residual). Kept, not corrected in code.
  - ppent: ppnenet; Sharadar fills 0 for not-reported. A never-reported name
    is dropped by OSAP and kept here. ASC 842 (FY2019+) may move ROU assets
    into ppnenet: a level break in 2019-2021, caveat only.
  - AT requires a strictly positive average base (OSAP lets a zero base give
    inf); both-years-zero-revenue ChAT is NaN (OSAP gives 0).
  - Timing: OSAP reads the fiscal year at datadate + 6 months, refreshed
    annually; here the latest filed ART level (refreshed quarterly) against
    the same periods one and two years earlier. The change spans four quarters,
    not the fiscal year.
  - OSAP's portfolio-stage Filter abs(prc) > 5 is not reproduced (the harness
    universe owns it).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef

_LEVELS = ["receivables", "inventory", "ppnenet", "intangibles", "payables",
           "liabilitiesnc", "debtnc", "assets"]


def _noa(y, suffix):
    """Net operating assets at one balance-sheet date (aco and lco dropped)."""
    def col(name):
        return y[name + suffix].astype(float)

    reported = col("assets").notna()

    def zf(name):   # OSAP zero-fills; only on a filing with a populated balance sheet
        s = col(name)
        return s.where(s.notna() | ~reported, 0.0)

    lo = col("liabilitiesnc").fillna(0.0) - col("debtnc").fillna(0.0)
    return (zf("receivables") + zf("inventory") + col("ppnenet")
            + zf("intangibles") - zf("payables") - lo)


def _compute(ctx):
    y1 = ctx.fundamentals_yoy(_LEVELS + ["revenue"], years=1)
    y2 = ctx.fundamentals_yoy(_LEVELS, years=2)

    noa0 = _noa(y1, "")
    noa1 = _noa(y1, "_lag")
    noa2 = _noa(y2, "_lag")
    sale0 = y1["revenue"].astype(float)
    sale1 = y1["revenue_lag"].astype(float)

    base0 = (noa0 + noa1) / 2.0
    base1 = (noa1 + noa2) / 2.0
    at0 = sale0 / base0.where(base0 > 0)
    at1 = sale1 / base1.where(base1 > 0)
    at0 = at0.where(at0 >= 0)       # OSAP: AT < 0 -> NaN
    at1 = at1.where(at1 >= 0)

    chat = at0 - at1
    # zero revenue at both dates: ChAT = 0 is a placeholder, not a measurement
    both_zero = (sale0 == 0) & (sale1 == 0)
    return chat.where(~both_zero).replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="ChAssetTurnover",
    col="f_chat",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: a rise in turnover outperforms
    weight=1.0,
    inputs=("SF1.receivables", "SF1.inventory", "SF1.ppnenet", "SF1.intangibles",
            "SF1.payables", "SF1.liabilitiesnc", "SF1.debtnc", "SF1.assets",
            "SF1.revenue"),
    osap_acronym="ChAssetTurnover",
    source="Soliman 2008 (The Accounting Review)",
    lookback_months=44,             # latest filing (<=15m old) + 2 fiscal years back + 45d period tolerance + ~4m report-period-to-filing lag (honest figure ~43.5, rounded up)
    # No history_months: no SEP price window is read; year-ago levels come from
    # fundamentals_yoy (report-period aligned).
    notes="d( revenue / avg NOA ), NOA = rect+invt+ppe+intan-ap-lo, aco and lco dropped; ART, yoy by reportperiod",
    field_mappings=(
        ("rect, invt, ap", "SF1.receivables, SF1.inventory, SF1.payables", "1:1; null zero-filled (as OSAP) only on a filing with assets reported"),
        ("ppent", "SF1.ppnenet", "Sharadar stores 0 when not reported (OSAP ffills null); null stays NaN; ASC 842 level break 2019+"),
        ("intan", "SF1.intangibles", "1:1; ~34% exact zero is OSAP's zero-fill equivalent, fine inside a sum"),
        ("aco", "none", "no SF1 field; OSAP zero-fills it; dropped (0 for every firm), Route A"),
        ("lco", "none", "no SF1 field; OSAP zero-fills it; dropped (0 for every firm), Route A"),
        ("lo", "SF1.liabilitiesnc - SF1.debtnc", "both fillna(0) (OSAP zero-fills lo); unclassified balance sheets (~20%, null liabilitiesnc) get lo = 0; residual is non-current deferred taxes"),
        ("sale", "SF1.revenue", "ART TTM flow at two dates four quarters apart (windows do not overlap); null is NaN"),
        ("AT guard", "avg NOA > 0", "OSAP lets a zero base give inf; both-years-zero-revenue ChAT is NaN (OSAP: 0)"),
        ("time_avail_m", "SF1.datekey", "filing-date bound, quarterly refresh, three report-period-aligned dates; no 6-month annual lag"),
    ),
)
