"""
OPLeverage - operating leverage: SG&A plus cost of revenue over total assets (a
firm whose operating cost base is large relative to its asset base carries high
operating leverage).

OSAP: OPLeverage, Novy-Marx 2011 (Review of Finance, Table III panel b; SignalDoc
Acronym2 OperLeverage). Predicted sign: + (SignalDoc Sign = +1, ascending=True).
Spec: osap_source/cache/b4e911e6/OPLeverage/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  ART (trailing four quarters) flows over the same-date asset level, latest filing:
    xsga       = sgna.fillna(0) + rnd.fillna(0)
    OPLeverage = (xsga + cor) / assets
  Compustat xsga includes R&D; Sharadar sgna excludes it, so rnd is added back
  (rnd is vendor-zero-filled, a true zero when absent). OSAP's predictor zero-fills
  xsga itself (tempxsga), so a null or zero sgna contributes 0 here with no gate.
  cogs is NOT zero-filled by OSAP: cor null -> NaN, and cor == 0 (vendor zero-fill)
  -> NaN. The three inputs are a within-period ratio (TTM flows over a same-date
  level), no year-over-year difference: the dimension stays the ART default (an ARQ
  quarter would understate the flow ~4x). No winsorising, log or industry
  adjustment inside the signal; no sample screen (SignalDoc Filter is empty,
  financials stay in).

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Between filings all inputs are
  fixed, so the ratio is constant for that firm but firm-specific and price
  independent: a continuous (sgna + rnd + cor)/assets. A tie needs identical ratios
  across names. The one manufactured default is the vendor zero-fill of cor, which
  would score (sgna + rnd)/assets for non-reporters: REMOVED by the cor == 0 -> NaN
  gate.
  What share of the universe does nothing? Spec measured a modal-value share of the
  scored cross-section of 0.06% mean, 0.13% max over 276 months (distinct values ==
  n scored, 1,172-2,416; 10 bins every month). cor == 0 is 10.7% of the universe
  (5.8-15.0%) and is gated; sgna null 3.6% and sgna == 0 4.3% are zero-filled as OSAP
  does, and still produce a value (cor/assets + rnd/assets), not a common constant.
  Tie handling: null (cor == 0 / null -> NaN; assets <= 0 -> NaN); the harness
  averages ranks over any residual ties.

OVERLAP: none declared with the v0 legs beyond the shared SF1 columns; the ratio is
(sgna + rnd + cor)/assets, a cost-to-assets level (no revenue term).

DEVIATIONS FROM OSAP:
  - cogs -> cor (approx): cor is as-reported cost of revenue and INCLUDES D&A for
    some filers where Compustat cogs excludes it; sgna likewise. The score is
    higher by the embedded D&A over assets for those filers (spec: median 0.034 of
    assets on >= 90%-embedded rows against a median level 0.673; rank rho
    0.999 / 0.999 / 0.995 at 1999 / 2008 / 2020, ~10% of names move a decile). Not
    corrected.
  - xsga -> sgna + rnd (approx): Compustat xsga includes R&D, sgna does not.
  - cor == 0 -> NaN (vendor zero-fill; OSAP does not fill cogs).
  - sgna null or exactly 0 is zero-filled, as OSAP's own tempxsga does (no gate).
  - at == 0 gives inf in OSAP and is kept there; here assets > 0 guards the
    denominator (zero -> NaN, negative would flip the sign).
  - OSAP's upstream drop of annual rows with null at / prcc_c / ni is not
    reproduced.
  - Timing: OSAP reads the annual record at datadate + 6 months and holds it 12
    months; here the latest filed ART (0-3 months old, refreshed quarterly), no
    6-month annual lag, assets the latest filing's level.
  - Coverage ~51% at signal months 1998-12..1999-02 (ART TTM warm-up), >= 75%
    thereafter (spec-measured pooled 85.4%).
  - OSAP's EW quintile portfolios are the harness's, not reproduced.
"""


from harness.factor_def import FactorDef

_FIELDS = ["cor", "sgna", "rnd", "assets"]


def _compute(ctx):
    f = ctx.fundamentals(_FIELDS)

    xsga = f["sgna"].astype(float).fillna(0.0) + f["rnd"].astype(float).fillna(0.0)
    cor = f["cor"].astype(float)
    cor = cor.where(cor != 0)                        # vendor zero-fill -> NaN; null stays NaN
    assets = f["assets"].astype(float)

    return (xsga + cor) / assets.where(assets > 0)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="OPLeverage",
    col="f_opleverage",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: HIGH operating leverage is the long side
    weight=1.0,
    inputs=("SF1.cor", "SF1.sgna", "SF1.rnd", "SF1.assets"),
    osap_acronym="OPLeverage",
    source="Novy-Marx 2011 (Review of Finance)",
    lookback_months=15,             # latest ART filing, capped by max_fundamental_age_months
    # No history_months: no SEP price window is read.
    notes=("(sgna.fillna(0) + rnd.fillna(0) + cor) / assets, ART; cor == 0 -> NaN (vendor zero-fill); "
           "xsga zero-filled as OSAP; assets > 0; no sample screen"),
    field_mappings=(
        ("xsga", "SF1.sgna + SF1.rnd (ART TTM)",
         "approx: sgna excludes R&D (rnd added back, true zero when absent) and embeds D&A for some filers (score higher by it); null/zero sgna -> 0 as OSAP's tempxsga"),
        ("cogs", "SF1.cor (ART TTM)",
         "as reported, embeds D&A for some filers (approx); exact zero = vendor zero-fill -> NaN; null -> NaN (OSAP does not fill cogs)"),
        ("at", "SF1.assets", "latest ART level, not fiscal-year-end; guarded > 0 (OSAP keeps inf at at == 0)"),
        ("time_avail_m", "SF1.datekey", "filing-date bound, quarterly refresh; no 6-month annual lag"),
    ),
)
