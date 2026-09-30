"""
EarnSupBig — industry earnings surprise of the largest firms, handed to the smaller
firms of the same industry: information about the industry's earnings news diffuses
from big firms to small ones with a lag, so small firms in an industry whose big
firms just surprised positively should earn higher returns.

OSAP: EarnSupBig, Hou 2007, Review of Financial Studies (Key Table AR_i,3).
Predicted sign: + (SignalDoc Sign = +1; high value = long side).
Spec: osap_source/cache/b4e911e6/EarnSupBig/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  E(q)   = SF1.eps at dimension ARQ (single-quarter reported EPS), the last 21
           filings known at the signal (ctx.fundamentals_history, deduplicated on
           reportperiod). Quarters are aligned by reportperiod: a filing k quarters
           before the latest one is the one whose report month is 3k months earlier
           (report date + 10 days, rounded to a month ordinal, +-1 month tolerance
           for 52/53-week calendars). A quarter not found is NaN, never a shifted one.
  G(k)   = E(k) - E(k+4)                        year-over-year EPS change, k = 0..16
  Drift  = mean of G(k+1..k+8), skipping NaN    (OSAP: mean of GrTemp.shift(3,6,..,24))
  ESraw(k) = G(k) - Drift(k)
  SD     = std (ddof = 1, skipping NaN) of ESraw(1..8)
  ES     = ESraw(0) / SD                        NaN where SD is NaN or < 1e-8
  Per (FF48 industry, month): rank the market cap of the industry's scored-panel
  names (rank pct, method average); a name with rank >= 0.7 is BIG. EarnSupBig =
  the mean ES over the BIG names with a valid ES, given to every name in that
  industry that is NOT big; big names are NaN.
  Partial windows score exactly as in OSAP (an SD from two surprises, a Drift from
  one term); this is not a minimum-count rule.
  The "scored panel" is the universe names that hold a fresh ARQ filing (OSAP's
  inner merge of the monthly panel with the quarterly file) with cap > 0 and a
  non-missing FF48 code. A name with no valid ES of its own still receives the
  industry value.
  No surprise is analyst-based; there is no price input besides the cap used to
  split big from small.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? The signal is an (FF48 industry,
  month) CONSTANT: a firm that files nothing still inherits the industry's big-firm
  mean, and every non-big firm of an industry ties exactly with every other one.
  What share of the universe does nothing? Every non-big scored firm is in a tie
  block. A cross-section holds at most about 44 distinct values, and the harness
  then ranks within sector, where an FF48 block can be a large share of a sector.
  The largest blocks are banks (FF48 44), business services (34) and pharma /
  biotech (13); the expected modal share of scored names is ESTIMATED at 6-11%,
  borderline against the 10% hard fail (not measured here; preflight measures it).
  Tie handling: the ties ARE the construction. They are not removed and not broken
  with noise; ranking uses method "average" on exact ties (done by the harness).
  The factor neither floors nor perturbs anything. If preflight rejects the mass
  point, that measured result is the verdict on this construction. The factor-level
  values are exactly-0 only by coincidence (a mean of standardised surprises).

DEVIATIONS FROM OSAP:
  - epspxq -> SF1.eps ARQ. eps is a REPORTED figure (netinccmn-based basic EPS,
    includes discontinued operations and preferred adjustments), nearer Compustat
    epspiq than epspxq (which excludes extraordinary items). It is never rebuilt from
    netinccmn / shareswa (they agree within 0.005 on only ~65-70% of rows).
  - eps is restated to today's split basis on every row (no split jump), on a 0.001
    lattice; the score is a ratio (surprise / SD), so a common rescale cancels.
    ARQ is a single-quarter level (ART is a trailing-four-quarter sum and would
    smear the 12-month difference); FactorDef.dimension = "ARQ" is recorded only.
  - Quarter alignment by reportperiod, not by the 12 / 3 / ... rows of a monthly
    panel; a quarter is known at its SF1 datekey (about 1.5 months after quarter
    end), earlier than OSAP's datadate + 3 months. Amended filings supersede the
    original once filed. Names whose latest filing is older than
    max_fundamental_age_months are not scored.
  - mve_c (per-PERMNO cap) -> ctx.universe["mkt_cap_usd"] (company-level cap). The
    "30% largest" is the top 30% of UNIVERSE members in the FF48 industry, not of
    all of CRSP, so the big set is larger-cap and the small firms scored are the
    mid-caps. Rank threshold >= 0.7 as in OSAP.
  - Industry = FF48 from TICKERS.siccode, TODAY's SIC (not point-in-time; 12-14% of
    names changed SIC since 1998), so a reclassified firm carries its current
    industry in every past month: look-ahead enters the signal value through the
    industry assignment. OSAP uses the CRSP SIC. SICs outside the FF48 table have
    no industry and are dropped, as upstream.
  - group_mean_where is called with min_group = 1 (OSAP has no group-size floor), so
    an industry is scored as long as one big name has a valid ES.
  - Early window: SF1 starts in 1997Q4, so the eight-quarter minimum is first met
    around 1999Q3 and the full 21-quarter window only from ~2003 (8.2% of the
    universe at 1999-12, 48% at 2002-12, 83% at 2008-06); early big-firm means rest on
    thin, noisy standardised values.
  - Coverage is below 70% by construction (big firms are NaN).
  - The harness ranks within sector, so the signal is further blockwise in sector.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef
from harness.industry import ff48, group_mean_where

_N_Q = 21            # quarters E(0)..E(20): G(0..16), ESraw(0..8) -> 8 lagged surprises
_BIG_RANK = 0.7      # OSAP: relrank(mve_c within FF48) >= 0.7


def _quarter_matrix(ctx):
    """ID x quarter-offset (0 = latest filing, k = k quarters earlier) matrix of
    SF1 ARQ eps, aligned by reportperiod. Empty frame if nobody has a filing."""
    h = ctx.fundamentals_history(["eps"], n_periods=_N_Q, dimension="ARQ")
    if h.empty:
        return pd.DataFrame(columns=range(_N_Q), dtype=float)
    rp = pd.to_datetime(h["reportperiod"]) + pd.Timedelta(days=10)
    h = h.assign(m=(rp.dt.year * 12 + rp.dt.month).astype("int64"))
    m0 = h.loc[h["q_back"] == 0].set_index("ID")["m"]
    d = h["ID"].map(m0) - h["m"]
    j = np.rint(d / 3.0)
    err = (d - 3.0 * j).abs()
    keep = (err <= 1) & (j >= 0) & (j < _N_Q)
    h = h.assign(j=j, err=err)[keep]
    h = (h.sort_values(["ID", "j", "err"], kind="mergesort")
          .drop_duplicates(["ID", "j"], keep="first"))
    e = h.assign(j=h["j"].astype(int)).pivot(index="ID", columns="j", values="eps")
    e = e.reindex(columns=range(_N_Q)).astype(float)
    # the set of IDs that hold a fresh ARQ filing (the scored panel), even if eps is NaN
    return e.reindex(m0.index)


def _compute(ctx):
    e = _quarter_matrix(ctx)
    if e.empty:
        return pd.Series(dtype=float)

    g = pd.DataFrame({k: e[k] - e[k + 4] for k in range(_N_Q - 4)})       # G(0..16)
    esraw = {}
    for k in range(9):                                                      # ESraw(0..8)
        drift = g[[k + i for i in range(1, 9)]].mean(axis=1, skipna=True)
        esraw[k] = g[k] - drift
    sd = pd.DataFrame({k: esraw[k] for k in range(1, 9)}).std(axis=1, ddof=1, skipna=True)
    es = esraw[0] / sd.where(sd >= 1e-8)

    cap = ctx.universe["mkt_cap_usd"].astype(float).reindex(e.index)
    sic = ctx.ticker_meta(["siccode"])["siccode"].reindex(e.index)
    ind = ff48(sic)
    ind.index = e.index
    ok = cap.gt(0) & ind.notna()
    if not ok.any():
        return pd.Series(dtype=float)
    cap, ind, es = cap[ok], ind[ok], es[ok]

    rk = cap.groupby(ind).rank(pct=True, method="average")
    big = rk >= _BIG_RANK
    score = group_mean_where(es, ind, big, min_group=1)
    return score.where(~big)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="EarnSupBig",
    col="f_earnsupbig",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: high industry big-firm surprise -> high return
    weight=1.0,
    inputs=("SF1.eps", "TICKERS.siccode", "DAILY.marketcap"),
    osap_acronym="EarnSupBig",
    source="Hou 2007 (Review of Financial Studies)",
    lookback_months=78,             # 21 quarters = 60m back from the latest period + 15m max filing age + ~3m filing lag
    # No history_months: no price window is read.
    dimension="ARQ",                # single-quarter eps level; ART is a 4-quarter sum and would smear the YoY difference
    notes="mean standardised YoY-EPS surprise of the top-30% cap names per FF48 industry, given to the other names",
    field_mappings=(
        ("compustat.epspxq", "SF1.eps (ARQ)",
         "reported basic EPS incl. discontinued ops (nearer epspiq); split-restated; not rebuilt from netinccmn/shareswa"),
        ("quarter alignment", "reportperiod (ctx.fundamentals_history)",
         "by report month +-1, not by panel row; known at SF1 datekey (earlier than datadate+3m); 21 quarters, partial windows score"),
        ("crsp.mve_c", "ctx.universe['mkt_cap_usd']",
         "company-level cap; big = top 30% of UNIVERSE names per FF48, not of all CRSP"),
        ("crsp.siccd (sicCRSP)", "TICKERS.siccode (CURRENT) -> harness.industry.ff48",
         "today's SIC, not point-in-time: look-ahead enters the value via the industry assignment; unmapped SIC dropped"),
        ("industry average", "harness.industry.group_mean_where(min_group=1)",
         "no group-size floor, as OSAP; big names NaN; tie blocks are the construction (no tie-break added)"),
    ),
)
