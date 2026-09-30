"""
OperProfRD - R&D-adjusted operating profitability: revenue less cost of revenue
less SG&A (excluding R&D), over total assets.

OSAP: OperProfRD, Ball, Gerakos, Linnainmaa and Nikolaev 2016 (Journal of Financial
Economics, Table 4A). Predicted sign: + (SignalDoc Sign = +1, ascending=True).
Spec: osap_source/cache/b4e911e6/OperProfRD/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  OSAP code: OperProfRD = (revt - cogs - xsga + xrd.fillna(0)) / at.
  Compustat xsga INCLUDES R&D, so "- xsga + xrd" leaves SG&A excluding R&D. In
  Sharadar sgna already EXCLUDES R&D: with xsga = sgna + rnd the rnd terms cancel
  exactly (-(sgna + rnd) + rnd = -sgna), so
    OperProfRD = (revenue - cor - sgna) / assets
  (spec-measured max |difference| between the two forms is 0 over all scored names
  and months). rnd is therefore not an input here, and its vendor zero-fill is moot.
  ART (trailing four quarters) flows over the same-date asset level, latest filing:
  a within-period ratio, no year-over-year difference, dimension stays ART (an ARQ
  quarter would understate the flow ~4x). Negative profit is kept, as OSAP keeps it.
  No winsorising, log or industry adjustment inside the signal.

SAMPLE RESTRICTIONS INSIDE THE SIGNAL (part of OSAP's definition, NaN output, not a
universe change):
  - Financials: SIC 6000-6999 -> NaN (OSAP: not (6000 <= sicCRSP < 7000)), read
    through ctx.ticker_meta(["siccode"]). That SIC is TODAY's vendor classification,
    not the code in force in the month scored (known trap current_sic_signal_values):
    a look-ahead of the same kind the sector ranking carries (DECISIONS D3). A
    missing SIC is NaN.
  - equity must be non-null and assets non-null (OSAP keeps only ceq and at
    non-null); here assets > 0 also guards the denominator (a zero gives inf in OSAP,
    a negative flips the sign). equity is used only as a non-null test.
  - revenue, cor, sgna null -> NaN, never zero-filled (OSAP zero-fills none of revt,
    cogs, xsga; the SignalDoc wording differs, the code is followed).
  - cor == 0 -> NaN and sgna == 0 -> NaN: Sharadar zero-fills absent lines, OSAP does
    not, and a zero would turn the numerator into revenue less the other line.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Between filings all inputs are fixed,
  so the ratio is constant for that firm but firm-specific and price independent: a
  continuous (revenue - cor - sgna)/assets. A tie needs identical ratios across names.
  The manufactured defaults are the vendor zero-fills of cor and sgna (a
  revenue-only-type numerator placed at one level): REMOVED by the two zero gates
  (null, renormalised by blend_ranks).
  What share of the universe does nothing? Spec measured a modal-value share of the
  scored cross-section of 0.07% mean, 0.16% max over 276 months (distinct values == n
  scored, 974-2,106; 10 bins every month); coverage 70.7% pooled, financials ~19.6%
  of the universe being the ceiling.
  Tie handling: null (zero cor / zero sgna / financials / assets <= 0 -> NaN); the
  harness averages ranks over any residual ties.

OVERLAP WITH THE COMPOSITE'S PROFITABILITY LEG (facts only):
  The v0 Profitability leg is (revenue - cor - (sgna + rnd + intexp)) / equity. Shared
  core: revenue - cor - sgna (same SF1 columns, same ART dimension). Differences: v0
  also subtracts rnd and intexp and divides by book equity, not assets; v0 has no
  cor == 0 or sgna == 0 gate and no financials exclusion. SignalDoc Cat.Economic for
  this signal is profitability, the v0 leg's category.

DEVIATIONS FROM OSAP:
  - cogs -> cor, xsga -> sgna (+ rnd, cancelled) (approx): cor and sgna are as
    reported and EMBED D&A for some filers where Compustat cogs / xsga exclude it, so
    the numerator is lower by the embedded amount (field_map xsga note: >= 90%
    embedded on ~36% of rows, median embedded/assets 0.034 on those, about 24% of
    their numerator; rank rho 0.968 / 0.956 / 0.949 at 1999 / 2008 / 2020, 45-52% of
    names change decile). Not corrected.
  - cor == 0 -> NaN and sgna == 0 -> NaN (vendor zero-fills; OSAP fills neither).
  - rnd cancels: no R&D input and no xrd zero-fill.
  - SIC is the current classification, not point-in-time (above). equity includes
    preferred (immaterial as a non-null test).
  - Timing: OSAP reads the annual record at datadate + 6 months and holds it 12
    months; here the latest filed ART (0-3 months old, refreshed quarterly), no
    6-month annual lag, assets the latest filing's level. The paper lags the
    denominator; OSAP and this file do not.
  - OSAP's shrcd <= 11 and mve_c non-null are the universe's; VW NYSE-breakpoint
    deciles are the harness's, not reproduced.
  - Coverage ~43% at signal month 1998-12, ~63% mean in 1999, 70-73% from 2001 (ART
    TTM flows are thin at the snapshot start).
"""

import pandas as pd

from harness.factor_def import FactorDef

_FIELDS = ["revenue", "cor", "sgna", "assets", "equity"]


def _compute(ctx):
    f = ctx.fundamentals(_FIELDS)

    rev = f["revenue"].astype(float)
    cor = f["cor"].astype(float)
    cor = cor.where(cor != 0)                        # vendor zero-fill -> NaN, not a real zero
    sgna = f["sgna"].astype(float)
    sgna = sgna.where(sgna != 0)                     # vendor zero-fill -> NaN, not a real zero
    assets = f["assets"].astype(float)

    # rnd cancels: (revt - cogs - (sgna + rnd) + rnd) == revenue - cor - sgna
    score = (rev - cor - sgna) / assets.where(assets > 0)   # null revenue / cor / sgna -> NaN
    score = score.where(f["equity"].notna())                # OSAP: ceq non-null

    # OSAP sample screen (NaN, not a universe change): financials by CURRENT SIC.
    sic = pd.to_numeric(ctx.ticker_meta(["siccode"])["siccode"], errors="coerce")
    sic = sic.reindex(score.index)
    nonfin = sic.notna() & ~((sic >= 6000) & (sic < 7000))
    return score.where(nonfin)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="OperProfRD",
    col="f_operprofrd",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: HIGH R&D-adjusted profitability is the long side
    weight=1.0,
    inputs=("SF1.revenue", "SF1.cor", "SF1.sgna", "SF1.assets", "SF1.equity", "TICKERS.siccode"),
    osap_acronym="OperProfRD",
    source="Ball, Gerakos, Linnainmaa and Nikolaev 2016 (Journal of Financial Economics)",
    lookback_months=15,             # latest ART filing, capped by max_fundamental_age_months
    # No history_months: no SEP price window is read.
    notes=("(revenue - cor - sgna) / assets, ART; rnd cancels (sgna excludes R&D); cor == 0 and sgna == 0 -> NaN; "
           "equity non-null; assets > 0; financials (current SIC 6000-6999) and null SIC -> NaN"),
    field_mappings=(
        ("revt", "SF1.revenue (ART TTM)", "null -> NaN (OSAP does not zero-fill)"),
        ("cogs", "SF1.cor (ART TTM)", "as reported, embeds D&A for some filers (approx, numerator lower); exact zero = vendor zero-fill -> NaN"),
        ("xsga, xrd", "SF1.sgna (ART TTM); rnd cancelled",
         "approx: Compustat xsga includes R&D and the code adds xrd back; sgna excludes R&D so -(sgna + rnd) + rnd = -sgna, rnd not read; sgna embeds D&A for some filers; sgna == 0 -> NaN"),
        ("at", "SF1.assets", "latest ART level, not fiscal-year-end; guarded > 0 (OSAP keeps inf at at == 0)"),
        ("ceq", "SF1.equity", "non-null test only; equity includes preferred (immaterial)"),
        ("sicCRSP 6000-6999", "TICKERS.siccode", "CURRENT classification (look-ahead like D3 sector); sample screen only; null SIC -> NaN"),
        ("time_avail_m", "SF1.datekey", "filing-date bound, quarterly refresh; no 6-month annual lag"),
    ),
)
