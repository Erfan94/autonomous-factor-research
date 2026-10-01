"""
GP - gross profitability: revenue less cost of revenue, over total assets
(high gross profit per dollar of assets = productive, durable franchise).

OSAP: GP, Novy-Marx 2013 (Journal of Financial Economics, Table 2a; SignalDoc
Acronym2 ProfGross). Predicted sign: + (SignalDoc Sign = +1, ascending=True).
Spec: osap_source/cache/b4e911e6/GP/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  ART (trailing four quarters) flows over the same-date asset level, latest filing:
    GP = (revenue - cor) / assets
  Built from the components, not from SF1.gp, so the cor gate below is visible.
  revenue and cor are TTM sums of the same four quarters and assets is a level at
  the same filing, so no year-over-year difference and no ARQ override: the
  dimension stays the ART default (an ARQ quarter would understate the flow ~4x).
  Negative GP (revenue < cor) is kept, as OSAP keeps it. No winsorising, log or
  industry adjustment inside the signal.

SAMPLE RESTRICTIONS INSIDE THE SIGNAL (part of OSAP's definition, NaN output,
not a universe change):
  - Financials: SIC 6000-6999 -> NaN (OSAP: keep if sic < 6000 or sic >= 7000),
    read through ctx.ticker_meta(["siccode"]). That SIC is TODAY's vendor
    classification, not the code in force in the month scored: a look-ahead of the
    same kind the sector ranking carries (DECISIONS D3). A missing SIC is NaN, as
    in OSAP (NaN fails both sides of the test and is dropped).
  - cor == 0 -> NaN. Sharadar zero-fills cost of revenue for filers that report no
    such line; OSAP does NOT zero-fill cogs (a missing cogs drops the row). With
    cor = 0 the score would be revenue / assets, a different quantity that places
    non-reporters high. Field_map ruling vendor_zero_fills names GP.
  - assets > 0 (denominator guard; a zero gives inf, a negative one flips the sign).
  - revenue or cor null -> NaN, never zero-filled (OSAP does not zero-fill revt/cogs).

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Between filings all three inputs
  are fixed, so GP is constant for that firm but firm-specific: a continuous ratio
  of (revenue - cor) to assets, nothing in it moves with price. A tie needs two
  names with identical ratios; a common constant would need revenue == cor, which
  is not a default state. The one default-value source is the vendor zero-fill of
  cor, which would make revenue/assets a block of non-reporters: REMOVED by the
  cor == 0 -> NaN gate (null, renormalised by blend_ranks). Expected modal share
  well under 1% in any month; preflight measures it.
  Tie handling: null (the gate above) and the assets > 0 guard; the harness
  averages ranks over any residual ties.

OVERLAP WITH THE COMPOSITE'S PROFITABILITY LEG (facts only):
  The v0 Profitability leg also contains the term revenue - cor (same SF1 columns,
  same ART dimension). It additionally subtracts sgna + rnd + intexp and divides by
  equity (book), not assets; it applies neither the cor == 0 gate nor the financials
  exclusion. GP subtracts nothing else and divides by assets.

DEVIATIONS FROM OSAP:
  - cogs -> cor (approx): cor is the as-reported cost-of-revenue line and INCLUDES
    D&A for some filers (INTC / MU / TXN class) where Compustat cogs excludes it, so
    GP is lower for those names by at most the embedded D&A over assets. Not
    corrected.
  - cor == 0 -> NaN (vendor zero-fill, above).
  - SIC is the current classification, not point-in-time (above).
  - Timing: OSAP reads the fiscal year ending at datadate, available at datadate + 6
    months and held 12 months; here the latest filed ART (0-3 months old, refreshed
    quarterly) with no 6-month annual lag, and assets is the latest filing's level,
    not fiscal-year-end.
  - revt (code) / sale (SignalDoc text) both map to SF1.revenue.
  - at == 0 keeps inf in OSAP; here dropped by the assets > 0 guard.
  - OSAP's shrcd / price / NYSE-breakpoint filters and VW quintile portfolios are
    the harness's, not reproduced.
  - Coverage: ~46% at signal months 1998-12..1999-02 (ART TTM flows are thin at the
    snapshot start), >= 70% thereafter.
"""

import pandas as pd

from harness.factor_def import FactorDef

_FIELDS = ["revenue", "cor", "assets"]


def _compute(ctx):
    f = ctx.fundamentals(_FIELDS)

    rev = f["revenue"].astype(float)
    cor = f["cor"].astype(float)
    cor = cor.where(cor != 0)                        # vendor zero-fill -> NaN, not a real zero
    assets = f["assets"].astype(float)

    score = (rev - cor) / assets.where(assets > 0)   # null revenue / cor -> NaN

    # OSAP sample screen (NaN, not a universe change): financials by CURRENT SIC.
    sic = pd.to_numeric(ctx.ticker_meta(["siccode"])["siccode"], errors="coerce")
    sic = sic.reindex(score.index)
    nonfin = sic.notna() & ~((sic >= 6000) & (sic < 7000))
    return score.where(nonfin)


FACTOR = FactorDef(
    family="profitability",                # Phase C, 2026-10-01: Cat.Economic "profitability" (decision phase_c_family_partition)
    name="GP",
    col="f_gp",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1
    weight=1.0,
    inputs=("SF1.revenue", "SF1.cor", "SF1.assets", "TICKERS.siccode"),
    osap_acronym="GP",
    source="Novy-Marx 2013 (Journal of Financial Economics)",
    lookback_months=15,             # latest ART filing, capped by max_fundamental_age_months
    # No history_months: no SEP price window is read.
    notes=("(revenue - cor) / assets, ART; cor == 0 -> NaN (vendor zero-fill); assets > 0; "
           "financials (current SIC 6000-6999) and null SIC -> NaN"),
    field_mappings=(
        ("revt (sale in SignalDoc text)", "SF1.revenue", "ART TTM level; null -> NaN (OSAP does not zero-fill)"),
        ("cogs", "SF1.cor", "as reported, embeds D&A for some filers (approx); exact-zero = vendor zero-fill -> NaN (OSAP leaves cogs missing)"),
        ("at", "SF1.assets", "latest ART level, not fiscal-year-end; guarded > 0 (OSAP keeps inf at at == 0)"),
        ("sic < 6000 or sic >= 7000", "TICKERS.siccode", "CURRENT classification (look-ahead like D3 sector); sample screen only; null SIC -> NaN as in OSAP"),
        ("time_avail_m", "SF1.datekey", "filing-date bound, quarterly refresh; no 6-month annual lag"),
    ),
)
