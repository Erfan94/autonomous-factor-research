"""
CBOperProf — cash-based operating profitability: operating profit before R&D,
moved toward cash by the year-over-year working-capital changes, over total
assets (high cash profitability = durable, cheap-to-fund earnings).

OSAP: CBOperProf, Ball, Gerakos, Linnainmaa & Nikolaev 2016 (Journal of
Financial Economics). Predicted sign: + (SignalDoc Sign = +1, ascending=True).
Spec: osap_source/cache/b4e911e6/CBOperProf/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  Latest known ART filing and the filing for the same fiscal period one year
  earlier, aligned by reportperiod (ctx.fundamentals_yoy). d(x) = x - x_yearago.
    core = revenue - cor - sgna                 (TTM flows, current level)
    num  = core - d(receivables) - d(inventory) + d(deferredrev) + d(payables)
    CBOperProf = num / assets                   (assets: latest ART level, NOT lagged)
  sgna already EXCLUDES R&D in Sharadar (opex = sgna + rnd + oth), and OSAP's
  xsga - xrd is SG&A ex-R&D, so the two coincide: rnd is not an input and is
  never subtracted or added (subtracting it would double count R&D).
  deferredrev is total deferred revenue (= Compustat drc + drlt): it enters once.
  The OSAP terms -(d xpp) and +(d xacc) are dropped: no SF1 field, and OSAP
  itself zero-fills both in the predictor (approx, see DEVIATIONS).
  The flows revenue / cor / sgna enter as the ART trailing-four-quarter level
  with no year-over-year difference (the analogue of annual revt, cogs, xsga);
  dimension stays the ART default, since an ARQ quarter would understate the
  profit term about 4x. The differenced items are balance-sheet levels, so
  their yoy change is a clean 12-month change.

SAMPLE RESTRICTIONS INSIDE THE SIGNAL (part of OSAP's definition, NaN output,
not a universe change):
  - Financials: SIC 6000-6999 -> NaN, read through ctx.ticker_meta(["siccode"]).
    That SIC is TODAY's vendor classification, not the code in force in the
    month being scored: a look-ahead of the same kind the sector ranking
    carries (DECISIONS D3). 12-14% of names changed SIC since 1998; a missing
    SIC is not treated as financial.
  - Non-positive book equity: OSAP's BM = log(ceq/mve) is NaN for ceq < 0, which
    silently drops those firms. Here equity > 0 and mkt_cap_usd > 0 stand in for
    a non-NaN log(BM); equity == 0 (log = -inf in OSAP, which survives) is also
    dropped, a negligible difference. The BM value itself is not used.
  - assets > 0 (denominator guard).

NULL HANDLING:
  - revenue null (early-1998 TTM-flow gap, ~7% elsewhere) -> NaN. OSAP zero-fills
    revt, cogs and xsga; here cor and sgna are zero-filled ONLY when revenue is
    present in the same ART row, so a missing income statement never becomes a
    pure working-capital change. cor is exact-zero on ~20% of ART rows (vendor
    zero-fill), kept as reported.
  - receivables / inventory / payables / deferredrev: a null level in either the
    latest or the year-ago filing gives a zero change for that term. DEVIATION:
    OSAP zero-fills the LEVEL and then differences, giving -level when only the
    current value is null; nulls are 0.03-0.05% of rows. No year-ago filing at all
    (reportperiod_lag missing) -> NaN, never a zero change.
  - Coverage: 48-55% at signal months 1999-01..02 (year-ago and TTM-flow levels
    do not exist yet at the snapshot start), about 87% from 1999-03.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? (revenue - cor - sgna) / assets
  with all four deltas zero: continuous and firm-specific, not a constant. A
  constant needs revenue, cor and sgna all exactly 0 and every delta 0. Pre-
  revenue shells have revenue = cor = 0 but sgna > 0, a distinct negative value.
  Zero deltas are common (deferredrev ~64%, inventory ~46% zero level, rect ~18%)
  but only remove terms; the profit core carries the dispersion.
  What share of the universe does nothing? Expected well under 1% in any month;
  preflight measures the modal-value share.
  Tie handling: none needed beyond guarding assets > 0 (and the NaN restrictions
  above); the harness averages ranks over any residual ties.

DEVIATIONS FROM OSAP:
  - xpp, xacc: no SF1 field; both terms dropped. They are reported by a subset of
    Compustat firms, where OSAP's -(d xpp) + (d xacc) are nonzero and absent
    here (approx; not measurable locally).
  - cogs -> cor: as reported; cor embeds D&A for ~36% of ART rows (and sgna for
    some filers), which makes the profit core short by the embedded D&A there,
    where Compustat cogs / xsga exclude it. Not corrected.
  - xsga - xrd -> sgna (equal, see CONSTRUCTION); drc + drlt -> deferredrev once.
  - Timing: OSAP reads the fiscal year available at datadate + 6 months and
    refreshes annually; here the latest filed ART level (refreshed quarterly)
    against the same period a year earlier, no 6-month lag.
  - ceq < 0 and BM filter -> equity > 0 and mkt_cap_usd > 0 (see above).
  - SIC is current, not point-in-time (see above). OSAP's shrcd > 11 screen and
    price / NYSE breakpoint filters are the harness universe's, not reproduced.

VERSUS THE COMPOSITE'S PROFITABILITY LEG (OperProf):
  OperProf = (revenue - cor - (sgna + rnd) - intexp) / equity: R&D and interest
  deducted, equity denominator, TTM level only, financials kept. CBOperProf adds
  R&D back, ignores interest, adds the cash (working-capital) adjustment, scales
  by assets, and removes financials and ceq <= 0; the shared core is
  revenue - cor - sgna, and their overlap is left to the Stage 2 residual IC.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef

_LEVELS = ["receivables", "inventory", "payables", "deferredrev"]
_FIELDS = ["revenue", "cor", "sgna", "assets", "equity"] + _LEVELS


def _delta(y, col):
    """Yoy change of a balance-sheet level; null in either leg -> 0 change (a DEVIATION:
    OSAP zero-fills the LEVEL, so a null current level with a present year-ago level
    gives -level there; nulls are 0.03-0.05% of rows)."""
    d = y[col].astype(float) - y[col + "_lag"].astype(float)
    return d.fillna(0.0)


def _compute(ctx):
    y = ctx.fundamentals_yoy(_FIELDS)

    rev = y["revenue"].astype(float)
    cor = y["cor"].astype(float).fillna(0.0)
    sga = y["sgna"].astype(float).fillna(0.0)
    core = (rev - cor - sga).where(rev.notna())      # null revenue -> NaN, not zero-filled

    num = (core
           - _delta(y, "receivables")
           - _delta(y, "inventory")
           + _delta(y, "deferredrev")
           + _delta(y, "payables"))
    num = num.where(y["reportperiod_lag"].notna())   # no year-ago filing -> NaN

    assets = y["assets"].astype(float)
    score = num / assets.where(assets > 0)

    # OSAP sample screens (NaN, not a universe change): financials, ceq <= 0 / no mve.
    sic = pd.to_numeric(ctx.ticker_meta(["siccode"])["siccode"], errors="coerce")
    sic = sic.reindex(score.index)
    financial = (sic >= 6000) & (sic <= 6999)
    equity = y["equity"].astype(float)
    mcap = ctx.universe["mkt_cap_usd"].astype(float).reindex(score.index)
    keep = (~financial) & (equity > 0) & (mcap > 0)
    return score.where(keep)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="CBOperProf",
    col="f_cbop",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1
    weight=1.0,
    inputs=("SF1.revenue", "SF1.cor", "SF1.sgna", "SF1.receivables", "SF1.inventory",
            "SF1.payables", "SF1.deferredrev", "SF1.assets", "SF1.equity",
            "TICKERS.siccode", "DAILY.marketcap"),
    osap_acronym="CBOperProf",
    source="Ball, Gerakos, Linnainmaa & Nikolaev 2016 (Journal of Financial Economics)",
    lookback_months=27,             # latest filing (<=15m old) vs the same period ~12m before it
    # No history_months: no SEP price window is read; year-ago levels come from
    # fundamentals_yoy (report-period aligned).
    notes=("(revenue - cor - sgna - d rect - d invt + d deferredrev + d ap) / assets, ART, "
           "yoy by reportperiod; financials (current SIC) and equity <= 0 -> NaN; no xpp/xacc"),
    field_mappings=(
        ("revt", "SF1.revenue", "ART TTM level; null -> NaN (OSAP zero-fills)"),
        ("cogs", "SF1.cor", "as reported, embeds D&A for ~36% of rows; exact-zero ~20% (vendor fill); zero-filled only when revenue present"),
        ("xsga - xrd", "SF1.sgna", "sgna already excludes rnd (== xsga - xrd); rnd NOT an input; zero-filled only when revenue present"),
        ("rect, invt, ap", "SF1.receivables, inventory, payables", "yoy change by reportperiod (fundamentals_yoy); null in either leg -> 0 change (deviation: OSAP fills the level, giving -level)"),
        ("drc + drlt", "SF1.deferredrev", "one field = drc + drlt, used once; yoy change, null -> 0"),
        ("xpp, xacc", "none", "no SF1 field; OSAP itself zero-fills both; terms dropped (approx)"),
        ("at", "SF1.assets", "latest ART level, not lagged (as in OSAP code); guarded > 0"),
        ("ceq, mve_permco (BM filter)", "SF1.equity, universe.mkt_cap_usd", "filter only: equity > 0 and mkt_cap_usd > 0 stand in for non-NaN log(BM)"),
        ("sicCRSP 6000-6999", "TICKERS.siccode", "CURRENT classification (look-ahead like D3 sector); sample screen only; missing SIC kept"),
        ("time_avail_m", "SF1.datekey", "filing-date bound, quarterly refresh; no 6-month annual lag"),
    ),
)
