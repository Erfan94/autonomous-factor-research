"""
Herf — industry sales concentration: the three-year average of the Herfindahl index of
firm sales within the firm's SIC industry. Low concentration (competitive industries)
is the long side.

OSAP: Herf, Hou and Robinson 2006, Journal of Finance (Table 2, firm-level raw).
Predicted sign: - (SignalDoc Sign = -1: a LOW Herf is the long side; ascending=False,
the raw value is NOT negated here).
Spec: osap_source/cache/b4e911e6/Herf/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  Market scope (every listed common stock, no price/size/liquidity screen: OSAP sums over
  all of CRSP, not over the harness universe), for each of the 36 month-ends s = 0..35
  (s = 0 is the signal month):
    rev[i,s]      = SF1.revenue / SF1.fxusd   (ART, USD: cross-firm sums need one currency)
    indsale[k,s]  = sum over firms with SIC4 == k and a non-null rev[i,s]
    tempHerf[k,s] = sum over those firms of (rev[i,s]/indsale[k,s])^2
  Firm value = mean of tempHerf[SIC4 of the firm, s] over the lags s in 0..35 at which the
  firm traded, at least 12 valid lags (OSAP asrol, 36 x 1 month, min 12). Every firm of an
  industry receives the industry's value whether or not it reports revenue itself; only
  universe names are scored. NaN if the firm's SIC is missing, or if SIC // 100 == 49
  (OSAP: SIC starting "49"; the dated pre-1983 exclusions never bind after 1998).
  Grouping is on the integer TICKERS.siccode (SIC4), as the pinned code does (its sic3D
  variable is str(sic)[:4], the full four digits, despite the name); never a string slice
  of the float. Negative revenue is kept, as OSAP keeps it; an industry with a
  zero or non-finite total is skipped (as HerfBE; the share is squared, so a negative
  total cannot flip its sign).
  Raw level, no log, no winsorising (harness ranks within sector).
  Early months are UNMASKED: lags before 1999-03 enter the mean although ART revenue is
  then populated for only 29-73% of listed names (industry sums over part of the firms
  overstate concentration); the 36-month mean dilutes this and masked vs unmasked agree at
  Spearman 0.96 (2000-02) and 1.00 from 2003-12. Masking would leave 13 decision months empty.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? The concept does not apply: Herf is an
  INDUSTRY attribute, so every firm in a SIC4 with the same 36-month presence shares one
  value. The mass points are industry blocks, not stale defaults.
  What share of the universe sits on one value? Spec measured, cross-section at 9 probe
  months, a modal-value share of 4.3-7.4% (largest SIC4 5.1-8.2% of scored names), below
  the 10% cliff, with qcut still giving 10 bins; Herf == 1 (sole revenue reporter in its
  SIC4) is 0.19% (1999-01) to 1.44% (2021-11). Preflight re-measures it.
  WITHIN SECTOR (ranks are formed among sector peers) one SIC4 dominates several sectors:
  in Real Estate, SIC 6798 (REITs) is ~84-93% of the scored names (93.3% 1999-06, 92.3%
  2003-12, 90.5% 2015-06, 84.1% 2021-11), so within-sector ranking gives that sector
  almost no information (104-164 scored names, ~5-7% of the universe); Energy SIC 1311 is
  37-47% and Healthcare SIC 2834 28-43% of their sectors. The 6798 value also sits at the
  low end of the pooled cross-section. This is stated, not worked around: the values are
  real, and no tie handling (null, remove, floor) is applied.
  Tie handling: none beyond the average rank the harness applies; the standing rule (level
  0 at both ends -> NaN) does not apply to a level.

DEVIATIONS FROM OSAP:
  - OSAP quirk not reproduced: an SIC4-month whose firms have no (or only zero) sales gets
    tempHerf = 0 in OSAP through pandas' empty sum, which lands on the long side; here that
    lag is dropped from the firm's 36-month mean.
  - Industry code: TICKERS.siccode is today's classification, applied to all history; OSAP's
    sicCRSP is point-in-time (12.3% of tickers changed SIC since 1998). Look-ahead through
    reclassified firms.
  - Market scope: Sharadar common stock (category Domestic Common Stock*) on NYSE/NASDAQ/
    NYSEMKT; there is no separate shrcd, so OSAP's shrcd > 11 -> NaN (share class 12) is
    not reproduced and those names are scored.
  - Revenue: ART TTM as filed by each month-end (mixed fiscal windows across firms within a
    month, refreshed quarterly) vs OSAP's annual sale at datadate + 6 months; converted to USD
    with revenue/fxusd; no extra reporting lag.
  - Firm presence at lag s: a universe name counts at s if it has a price within 7 days of
    that business month-end (ctx.has_price_at), for OSAP's "has a SignalMasterTable row that
    month". The industry sums themselves use the names listed at each lag that have an ART
    filing at that month-end.
  - Early-1998/1999 industry sums are partial (see UNMASKED above).
  - SIC4 groups are formed from TICKERS only (one row per permaticker), so a firm with a null
    siccode (<1% of market scope) is not in any sum.
  - OSAP's annual June rebalance and any price filter are not reproduced (harness-owned).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef

_WINDOW = 36      # calendar months in OSAP's asrol window (lags 0..35)
_MIN_VALID = 12   # OSAP asrol minimum observations


def _temp_herf(ctx):
    """Series indexed by (months_back, SIC4): sum of squared revenue shares, market scope."""
    mk = ctx.fundamentals_at_month_ends(["revenue", "fxusd"], range(_WINDOW), scope="market")
    if mk.empty:
        return None
    sic = pd.to_numeric(ctx.ticker_meta(["siccode"], scope="market")["siccode"], errors="coerce")
    fx = mk["fxusd"].astype(float)
    mk = mk.assign(rev=mk["revenue"].astype(float) / fx.where(fx > 0),   # USD before any cross-firm sum
                   sic=mk["ID"].map(sic)).dropna(subset=["rev", "sic"])
    if mk.empty:
        return None
    key = [mk["months_back"].to_numpy(), mk["sic"].to_numpy()]
    tot = mk.groupby(key)["rev"].transform("sum")
    ok = (tot != 0) & np.isfinite(tot)                  # a zero total has no shares
    mk = mk[ok]
    share2 = (mk["rev"] / tot[ok]) ** 2
    return share2.groupby([mk["months_back"].to_numpy(), mk["sic"].to_numpy()]).sum()


def _compute(ctx):
    sic = pd.to_numeric(ctx.ticker_meta(["siccode"])["siccode"], errors="coerce")   # universe IDs
    out = pd.Series(np.nan, index=ctx.ids)
    temp = _temp_herf(ctx)
    if temp is None:
        return out

    cols = {}
    for s in range(_WINDOW):
        try:
            ts = temp.xs(s, level=0)
        except KeyError:
            continue
        vals = sic.map(ts)
        cols[s] = vals.where(ctx.has_price_at(s).reindex(ctx.ids).fillna(False).astype(bool))
    if not cols:
        return out
    panel = pd.DataFrame(cols)
    herf = panel.mean(axis=1).where(panel.notna().sum(axis=1) >= _MIN_VALID)
    herf = herf.where(sic.notna() & ((sic // 100) != 49))     # regulated utilities (SIC 49xx)
    return herf.reindex(ctx.ids)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="Herf",
    col="f_herf",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: a LOW Herfindahl (competitive industry) is the long side
    weight=1.0,
    inputs=("SF1.revenue", "SF1.fxusd", "TICKERS.siccode"),
    osap_acronym="Herf",
    source="Hou and Robinson 2006 (Journal of Finance)",
    lookback_months=51,             # 36 month-ends, each filing up to 15 months stale (as HerfAsset/HerfBE)
    notes="36-month mean of the market-scope SIC4 sales Herfindahl (revenue/fxusd), min 12; 49xx NaN; early months unmasked",
    field_mappings=(
        ("compustat.sale", "SF1.revenue / SF1.fxusd (ART, market scope)",
         "USD before the cross-firm sum; ART mixed fiscal windows refreshed quarterly vs OSAP annual sale; early-1998 sums partial (unmasked)"),
        ("crsp.sicCRSP", "TICKERS.siccode (integer SIC4)",
         "CURRENT classification applied to all history (12.3% of tickers changed SIC since 1998); grouped on SIC4 as the pinned code does"),
        ("crsp.shrcd", "TICKERS.category (market scope)",
         "no separate share code; shrcd 12 (scored-out in OSAP) is scored here"),
        ("crsp.exchcd", "TICKERS.exchange (market scope)", "NYSE/NASDAQ/NYSEMKT common stock"),
        ("asrol 36m min 12", "36 month-end lags, >= 12 valid",
         "firm presence at a lag via has_price_at (7-day tolerance)"),
    ),
)
