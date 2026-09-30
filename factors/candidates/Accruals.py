"""
Accruals — working-capital accruals less depreciation, scaled by average assets
(high accruals = earnings carried by non-cash items, which reverse).

OSAP: Accruals, Sloan 1996 (The Accounting Review). Predicted sign: - (high
accruals predict low returns; SignalDoc Sign = -1, so ascending=False).
Spec: osap_source/cache/b4e911e6/Accruals/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  Latest known ART filing and the filing for the same fiscal period one year
  earlier, aligned by reportperiod (ctx.fundamentals_yoy):
    d(x)  = x_latest - x_yearago
    che   = cashneq + investmentsc.fillna(0)            (approx, see below)
    dWC   = d(assetsc) - d(che) - ( d(liabilitiesc) - d(debtc) )
    Accruals = (dWC - depamor_ART) / ((assets_latest + assets_yearago) / 2)
  The OSAP term -(d(txp)) inside the bracket is dropped (no SF1 field).
  Raw value is Accruals; ascending=False makes a LOW value the long side.
  depamor is the ART trailing-four-quarter sum, a FLOW, used as a current level
  with no year-over-year difference, the analogue of annual dp. dimension stays
  the ART default: a single-quarter depamor (ARQ) would understate dp about 4x.

NULL HANDLING:
  - assetsc / liabilitiesc / debtc are null on ~20% of rows (unclassified
    balance sheets, mostly financials and REITs). They are NEVER zero-filled
    (OSAP zero-fills act, lct, che, dp); those names stay NaN. Without this the
    whole block would collapse onto -dp/avg-assets. OSAP's own dlc is not
    zero-filled, so OSAP also loses most financials.
  - che: investmentsc.fillna(0) is a declaration only (numerically "cashneq
    where investmentsc is absent"); a null cashneq leaves che, hence the
    score, NaN.
  - depamor: OSAP fills dp = 0 when missing. Here a null ART depamor is read as
    zero ONLY when the SAME filing row carries the other trailing-four-quarter
    flows (revenue, netinc, ncfo non-null), i.e. the filer reported a full TTM
    but no D&A add-back. Where those flows are also missing, the row is the
    early-1998 TTM-flow gap (ART needs four quarters of history, SF1 starts
    1998) and the score stays NaN rather than becoming a spuriously dWC-only
    value. Sample effect: signal months 1999-01..02 are thin by construction.
  - year-ago levels: fundamentals_yoy (reportperiod within 45 days of latest
    minus one year); a name with no such filing is NaN, never a zero change.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? -depamor / avg assets: a
  continuous negative number, not a constant, because dp is subtracted as a
  level. An exact tie needs depamor == 0 (about 2-4% of non-null ART) AND all
  four balance-sheet deltas exactly zero (plus a zero-filled depamor): a near-
  empty set of dormant shells. A both-years-zero delta does not create a tie
  by itself because dp and avg assets still differ by firm.
  What share of the universe does nothing? Expected well under 1%; preflight
  measures the modal-value share.
  Tie handling: none needed beyond guarding the denominator (avg assets > 0);
  the harness averages ranks over any residual ties.

DEVIATIONS FROM OSAP:
  - txp: no SF1 field. OSAP itself does tempTXP = txp.fillna(0), so the
    Delta-txp term is dropped (approx); it is small next to d(lct).
  - act/lct/dlc/at -> assetsc/liabilitiesc/debtc/assets; the null unclassified
    block stays NaN where OSAP zero-fills act and lct.
  - che -> cashneq + investmentsc.fillna(0): investmentsc also holds current
    financing receivables of captive-finance filers (overstates che there) and
    the unclassified block is understated (che = cashneq).
  - dp zero-fill restricted to rows whose other TTM flows are present.
  - Timing: OSAP reads the fiscal year available at datadate + 6 months and
    refreshes annually; here the latest filed ART level (refreshed quarterly)
    against the same period a year earlier. The change spans four quarters,
    not the fiscal year.
  - OSAP's portfolio-stage Filter abs(prc) > 5 is not reproduced (harness
    universe owns it).
  - ASC 842 (2019+): debtc / liabilitiesc / depamor may absorb lease items, a
    one-time level break for affected names. Caveat only.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef

_FIELDS = ["assetsc", "cashneq", "investmentsc", "liabilitiesc", "debtc", "assets",
           "depamor", "revenue", "netinc", "ncfo"]


def _compute(ctx):
    y = ctx.fundamentals_yoy(_FIELDS)

    def che(suffix):
        return (y["cashneq" + suffix].astype(float)
                + y["investmentsc" + suffix].astype(float).fillna(0.0))

    d_act = y["assetsc"].astype(float) - y["assetsc_lag"].astype(float)
    d_che = che("") - che("_lag")
    d_lct = y["liabilitiesc"].astype(float) - y["liabilitiesc_lag"].astype(float)
    d_dlc = y["debtc"].astype(float) - y["debtc_lag"].astype(float)
    d_wc = d_act - d_che - (d_lct - d_dlc)

    # dp: zero-fill a null TTM depamor only when the same row's other TTM flows exist
    dp = y["depamor"].astype(float)
    flows_present = (y["revenue"].notna() & y["netinc"].notna() & y["ncfo"].notna())
    dp = dp.where(dp.notna() | ~flows_present, 0.0)

    avg_at = (y["assets"].astype(float) + y["assets_lag"].astype(float)) / 2.0
    return (d_wc - dp) / avg_at.where(avg_at > 0)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="Accruals",
    col="f_accruals",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: high accruals underperform
    weight=1.0,
    inputs=("SF1.assetsc", "SF1.cashneq", "SF1.investmentsc", "SF1.liabilitiesc",
            "SF1.debtc", "SF1.assets", "SF1.depamor", "SF1.revenue", "SF1.netinc",
            "SF1.ncfo"),
    osap_acronym="Accruals",
    source="Sloan 1996 (The Accounting Review)",
    lookback_months=27,             # latest filing (<=15m old) vs the same period ~12m before it
    # No history_months: no SEP price window is read; the year-ago levels come
    # from fundamentals_yoy (report-period aligned), not a 12-month price lag.
    notes="(d act - d che - (d lct - d dlc) - dp) / avg assets, ART, yoy by reportperiod; no txp term",
    field_mappings=(
        ("act", "SF1.assetsc", "null ~20% (unclassified balance sheets) stays NaN; OSAP zero-fills act"),
        ("che", "SF1.cashneq + SF1.investmentsc.fillna(0)", "approx: overstates che for captive-finance filers, understates for the unclassified block"),
        ("lct", "SF1.liabilitiesc", "null ~20% stays NaN; OSAP zero-fills lct"),
        ("dlc", "SF1.debtc", "null ~20% stays NaN (as in OSAP, which does not zero-fill dlc)"),
        ("at", "SF1.assets", "mean of latest and same-period year-ago ART filing (reportperiod-aligned), not a 12-row shift"),
        ("dp", "SF1.depamor", "ART TTM flow as a level; null read as 0 only when revenue, netinc, ncfo of the same row are present; else NaN (early-1998 TTM gap)"),
        ("txp", "none", "no SF1 field; OSAP itself zero-fills txp, so the d(txp) term is dropped"),
        ("time_avail_m", "SF1.datekey", "filing-date bound, quarterly refresh; no 6-month annual lag"),
    ),
)
