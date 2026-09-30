"""
GrLTNOA — growth in long-term net operating assets net of the accrual part of
that growth: expansion of the operating asset base that is NOT explained by
working-capital accruals is capital-intensive investment, which the market may
price with a lag.

OSAP: GrLTNOA, Fairfield, Whisenant and Yohn 2003 (The Accounting Review),
Tables 5A/5B. Predicted sign: + (SignalDoc Sign = +1, so ascending=True).
Spec: osap_source/cache/b4e911e6/GrLTNOA/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  Report-period-aligned ART filings at the latest period P and P-1y
  (ctx.fundamentals_yoy, years=1):
    LTNOA(d) = rect + invt + ppent + intan + ao - ap - lo           (aco = lco = 0)
    ltnoa(d) = LTNOA(d) / at(d)
    accrual  = ( d rect + d invt - d ap - dp ) / ((at + at_lag) / 2)
    GrLTNOA  = ltnoa(P) - ltnoa(P-1y) - accrual
  with rect = receivables, invt = inventory, ppent = ppnenet,
  intan = intangibles, ap = payables, at = assets, dp = depamor (ART TTM),
  ao = assetsnc - ppnenet - intangibles - investmentsnc,
  lo = liabilitiesnc - debtnc. Raw value is GrLTNOA; ascending=True makes a
  HIGH value the long side.
  ROUTE A (coordinator decision): OSAP's aco (other current operating assets)
  and lco (other current liabilities) have no SF1 field and OSAP itself
  zero-fills both, so both are dropped (0 for every firm) from the levels AND
  from the accrual numerator; they are NOT rebuilt from the assetsc /
  liabilitiesc identities. Only the working-capital items rect, invt, ap enter
  the accrual; ppent, intan, ao, lo enter only through the level change.
  dp is a FLOW (ART trailing four quarters) used once at the current date, not
  differenced; dimension stays the ART default (a single-quarter ARQ dp over an
  annual-scale base would understate the accrual about 4x).

NULL HANDLING:
  - rect, invt, ap, intan are zero-filled as OSAP does, but ONLY on a filing
    whose total assets are reported (a null on a populated balance sheet is a
    real absent item; an empty row stays NaN). ppnenet is not zero-filled
    (OSAP forward-fills it, never zero-fills it); a null leaves the date, and
    the score, NaN.
  - ao and lo come from the classified non-current block. Where assetsnc
    (or liabilitiesnc) is null the row is an unclassified balance sheet
    (financials and REITs, ~20% of rows): ao (lo) is NaN and so is the score.
    These nulls are NEVER zero-filled. investmentsnc is zero-filled only on a
    row whose assetsnc is reported, debtnc only on a row whose liabilitiesnc is
    reported (a null there is a real absent item).
  - dp is zero-filled (as OSAP does) only on a filing whose revenue is
    populated; a null dp on an unpopulated early ART row stays NaN.
  - Every year-ago filing is NEVER zero-filled: a name with no known filing for
    the year-ago period is NaN, not a zero change.
  - at > 0 is required at both dates and the average (at <= 0 is a sign flip or
    inf in OSAP, NaN here).
  - Signal months 1999-01 and 1999-02 are partial by construction (the earliest
    year-ago period is 1997Q4 and early ART rows are thin).

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? A firm with every balance
  item unchanged has zero level change and zero working-capital change, so
  GrLTNOA = dp / avg(at), which is > 0 and varies with dp and at: a point mass
  only if dp is also exactly 0 (Sharadar dp is exact zero on 1.3-2.3% of
  filings, and those firms also need unchanged balance sheets), i.e. effectively
  nobody. The exact value 0 arises only from a firm with no change at all and
  no depreciation.
  What share of the universe does nothing? Spec-measured modal-value share of
  the scored cross-section 0.05-0.11% at 7 probe months with every value
  distinct to the last observation; preflight measures the modal-value share.
  Tie handling: null. GrLTNOA is set to NaN where it is exactly 0.0 (only the
  no-change, no-depreciation firm; the 0 is a placeholder, not a measurement),
  and the blend renormalises. The standing level-0-at-both-ends rule does not
  otherwise bite: the levels are ratios over at > 0, and NOA exactly 0 at both
  dates has no population.

DEVIATIONS FROM OSAP:
  - Algebra: ao = assetsnc - ppnenet - intangibles - investmentsnc, so ppnenet and
    intangibles cancel inside ltnoa; they matter only through NaN propagation (a null
    ppnenet nulls the row, as a null ppent would in OSAP's sum). The intan zero-fill and
    the ppnenet caveats therefore do not move any value.
  - aco, lco: dropped (Route A), 0 for every firm. OSAP's zero is only the
    missing case; real values are ~3% / ~9% of assets (medians), so the level
    and the accrual both differ from the literal Compustat construction,
    because the accrual differences aco and lco directly.
  - ao: assetsnc - ppnenet - intangibles - investmentsnc. assetsnc is total
    non-current assets, not Compustat other-assets; the residual holds other
    non-current operating assets and whatever long-term items SF1 does not
    split out.
  - lo: liabilitiesnc - debtnc (liabilitiesnc contains long-term debt, >= debtnc
    on 99.8% of rows); residual is non-current deferred taxes and leases.
  - Unclassified balance sheets (assetsnc / liabilitiesnc null, ~20% of rows,
    91% financials and REITs) are NaN, whereas OSAP keeps them with zero-filled
    ao / lo / aco / lco. Coverage is therefore ~77%, not OSAP's.
  - ppent: ppnenet; Sharadar stores 0 when not reported. ASC 842 (FY2019+)
    puts right-of-use assets in ppnenet / other assets while lease liabilities
    sit in debtnc, cancelling in lo: a one-off jump in NOA for lessees across
    the adoption year. Caveat only.
  - Timing: OSAP reads the fiscal year at datadate + 6 months, refreshed
    annually; here the latest filed ART level (refreshed quarterly) against the
    same period one year earlier. The change spans the latest four quarters.
  - OSAP's portfolio-stage Filter abs(prc) > 5 is not reproduced (the harness
    universe owns it). at > 0 is a guard OSAP does not apply.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef

_LEVELS = ["receivables", "inventory", "ppnenet", "intangibles", "payables",
           "assetsnc", "investmentsnc", "liabilitiesnc", "debtnc", "assets"]


def _parts(y, suffix):
    """Return (LTNOA numerator, rect, invt, ap, assets) at one balance-sheet date.
    aco and lco are dropped (Route A)."""
    def col(name):
        return y[name + suffix].astype(float)

    reported = col("assets").notna()
    nc_assets = col("assetsnc").notna()
    nc_liab = col("liabilitiesnc").notna()

    def zf(name, gate):   # zero-fill a real absent item only inside a populated block
        s = col(name)
        return s.where(s.notna() | ~gate, 0.0)

    rect = zf("receivables", reported)
    invt = zf("inventory", reported)
    ap = zf("payables", reported)
    intan = zf("intangibles", reported)
    ao = col("assetsnc") - col("ppnenet") - intan - zf("investmentsnc", nc_assets)
    lo = col("liabilitiesnc") - zf("debtnc", nc_liab)
    ltnoa = rect + invt + col("ppnenet") + intan + ao - ap - lo
    return ltnoa, rect, invt, ap, col("assets")


def _compute(ctx):
    y = ctx.fundamentals_yoy(_LEVELS + ["depamor", "revenue"], years=1)

    n0, rect0, invt0, ap0, at0 = _parts(y, "")
    n1, rect1, invt1, ap1, at1 = _parts(y, "_lag")

    at0 = at0.where(at0 > 0)
    at1 = at1.where(at1 > 0)
    avg_at = (at0 + at1) / 2.0

    # dp: flow at the current date, zero-filled only on a filing with revenue populated
    dp = y["depamor"].astype(float)
    dp = dp.where(dp.notna() | y["revenue"].isna(), 0.0)

    d_ltnoa = n0 / at0 - n1 / at1
    accrual = ((rect0 - rect1) + (invt0 - invt1) - (ap0 - ap1) - dp) / avg_at.where(avg_at > 0)

    g = d_ltnoa - accrual
    g = g.replace([np.inf, -np.inf], np.nan)
    return g


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="GrLTNOA",
    col="f_grltnoa",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: high growth in LT NOA is the long side
    weight=1.0,
    inputs=("SF1.receivables", "SF1.inventory", "SF1.ppnenet", "SF1.intangibles",
            "SF1.payables", "SF1.assetsnc", "SF1.investmentsnc", "SF1.liabilitiesnc",
            "SF1.debtnc", "SF1.assets", "SF1.depamor", "SF1.revenue"),
    osap_acronym="GrLTNOA",
    source="Fairfield, Whisenant and Yohn 2003 (The Accounting Review)",
    lookback_months=33,             # latest filing (<=15m old) + 12 + 45d period tolerance + ~4m report-period-to-filing lag (honest figure ~32.5, rounded up)
    # No history_months: no SEP price window is read; the year-ago levels come
    # from fundamentals_yoy (report-period aligned).
    notes="d(LTNOA/at) - (d rect + d invt - d ap - dp)/avg at; aco and lco dropped (Route A); ART, yoy by reportperiod",
    field_mappings=(
        ("rect, invt, ap", "SF1.receivables, SF1.inventory, SF1.payables", "1:1; null zero-filled (as OSAP) only on a filing with assets reported"),
        ("ppent", "SF1.ppnenet", "Sharadar stores 0 when not reported (OSAP ffills null); null stays NaN; ASC 842 level break 2019+"),
        ("intan", "SF1.intangibles", "1:1; exact zero is OSAP's zero-fill equivalent; null zero-filled only on a filing with assets reported"),
        ("aco", "none", "no SF1 field; OSAP zero-fills it; dropped (0 for every firm) in levels and accrual, Route A"),
        ("lco", "none", "no SF1 field; OSAP zero-fills it; dropped (0 for every firm) in levels and accrual, Route A"),
        ("ao", "SF1.assetsnc - SF1.ppnenet - SF1.intangibles - SF1.investmentsnc", "approx; assetsnc is total non-current assets; investmentsnc null zero-filled only where assetsnc is reported; unclassified balance sheets (~20%) stay NaN"),
        ("lo", "SF1.liabilitiesnc - SF1.debtnc", "approx; debtnc null zero-filled only where liabilitiesnc is reported; unclassified balance sheets (~20%) stay NaN, unlike OSAP's zero-filled lo; residual is non-current deferred taxes"),
        ("at", "SF1.assets", "1:1; at > 0 required at both dates and the average (OSAP has no guard)"),
        ("dp", "SF1.depamor", "ART TTM flow used once at the current date; null zero-filled only on a filing with revenue populated"),
        ("time_avail_m", "SF1.datekey", "filing-date bound, quarterly refresh, report-period-aligned year-ago filing; no 6-month annual lag"),
    ),
)
