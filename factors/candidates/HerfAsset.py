"""
HerfAsset — industry concentration by assets: the three-year average of the Herfindahl
index of firm total assets within the firm's SIC industry. Low concentration (a
competitive industry) is the long side.

OSAP: HerfAsset, Hou and Robinson 2006, Journal of Finance (Table 2, H(Assets)).
Predicted sign: - (SignalDoc Sign = -1: a LOW HerfAsset is the long side; ascending=False,
the raw value is NOT negated here).
Spec: osap_source/cache/b4e911e6/HerfAsset/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  Market scope (every listed common stock, no price/size/liquidity screen: OSAP sums over
  all of CRSP, not over the harness universe), for each of the 36 month-ends s = 0..35
  (s = 0 is the signal month):
    at[i,s]       = SF1.assets / SF1.fxusd   (ART, USD: cross-firm sums need one currency)
    indasset[k,s] = sum over firms with SIC4 == k and a non-null at[i,s]
    tempHerf[k,s] = sum over those firms of (at[i,s]/indasset[k,s])^2
  Firm value = mean of tempHerf[SIC4 of the firm, s] over the lags s in 0..35 at which the
  firm traded, at least 12 valid lags (OSAP asrol, 36 x 1 month, min 12). Every firm of an
  industry receives the industry's value whether or not it reports assets itself; only
  universe names are scored. NaN if the firm's SIC is missing, or if SIC // 100 == 49
  (OSAP: SIC starting "49"; the dated pre-1983 exclusions never bind after 1998).
  Grouping is on the integer TICKERS.siccode through harness.industry.sic_group(sic, 4),
  as the pinned code does (its sic3D variable is str(sic)[:4], the full four digits,
  despite the name). An industry whose total is not positive is skipped (assets are
  non-negative, so this only removes an all-zero industry). Raw level, no log, no
  winsorising (the harness ranks within sector). No SF1 lag beyond the filing date.
  Early months are UNMASKED: lags before the ART panel is full enter the mean with
  industry sums over the part of the listed names that have a filing; the 36-month mean
  dilutes this.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? The concept does not apply: HerfAsset is
  an INDUSTRY attribute, so every firm in a SIC4 with the same 36-month listing history
  shares one value. The mass points are industry blocks, not stale defaults. A sole
  reporter in its SIC4 is exactly 1.0 (0.87% of scored names).
  What share of the universe sits on one value? Spec measured on the harness universe,
  all 276 signal months: modal-value share of the cross-section median 5.9%, max 7.7%,
  0 months at or above the 10% cliff, 10 qcut bins every month, median 430 distinct values.
  The largest block is SIC 6798 (REITs), 88 names (2008-12) to 133 (2021-11). Preflight
  re-measures it.
  WITHIN SECTOR (ranks are formed among sector peers) the ties concentrate: in Real Estate
  ~82-86% of names share the one SIC 6798 value, in Energy ~37-43% (SIC 1311) share one,
  Healthcare 24-31%, Financial Services 18-21%, Technology 16-22%, Communication Services
  14-21%; Utilities has 1-2 names (the < 10-name fallback to the cross-section rank
  applies, and 49xx is nulled anyway). Within-sector ranking therefore gives the Real
  Estate and Energy sectors little information. This is stated, not worked around: the
  values are real, and no tie handling (null, remove, floor) is applied.
  Tie handling: none beyond the average rank the harness applies; H never exceeds 1 here
  (assets are non-negative), so there is no sign-flip pathology.

DEVIATIONS FROM OSAP:
  - Industry code: TICKERS.siccode is today's classification, applied to all history; OSAP's
    sicCRSP is point-in-time (12.3% of tickers changed SIC since 1998). It enters the
    signal VALUE (industry grouping and the 49xx exclusion): look-ahead through
    reclassified firms.
  - Market scope: Sharadar common stock (category Domestic Common Stock*) on NYSE/NASDAQ/
    NYSEMKT; there is no separate shrcd, so OSAP's shrcd > 11 -> NaN (share class 12) is
    not reproduced and those names are scored.
  - Assets: SF1.assets (ART, level) as known at each month-end by filing date, vs OSAP's
    annual at at datadate + 6 months forward-filled; converted to USD with assets/fxusd;
    filings therefore appear 2-4 months earlier than OSAP's rule. No extra lag.
  - Row presence at lag s: a firm counts in an industry sum at s if it traded that month
    (market-scope listing rule) AND has a filing <= 15 months old with non-null assets;
    OSAP needs a SignalMasterTable row and an m_aCompustat row. A universe name is counted
    in its own 36-month mean at s only if it has a price within 7 days of that month-end
    (ctx.has_price_at).
  - SIC4 groups are formed from TICKERS only (one row per permaticker): a firm with a null
    siccode (<1% of market scope) is in no sum.
  - OSAP's annual June rebalance and any price filter are not reproduced (harness-owned).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef
from harness.industry import sic_group

_WINDOW = 36      # calendar months in OSAP's asrol window (lags 0..35)
_MIN_VALID = 12   # OSAP asrol minimum observations


def _temp_herf(ctx):
    """Series indexed by (months_back, SIC4): sum of squared asset shares, market scope."""
    mk = ctx.fundamentals_at_month_ends(["assets", "fxusd"], range(_WINDOW), scope="market")
    if mk.empty:
        return None
    sic = sic_group(ctx.ticker_meta(["siccode"], scope="market")["siccode"], 4)
    fx = mk["fxusd"].astype(float)
    mk = mk.assign(val=mk["assets"].astype(float) / fx.where(fx > 0),   # USD before any cross-firm sum
                   sic=mk["ID"].map(sic)).dropna(subset=["val", "sic"])
    if mk.empty:
        return None
    grp = [mk["months_back"].to_numpy(), mk["sic"].to_numpy()]
    tot = mk.groupby(grp)["val"].transform("sum")
    keep = tot > 0                                      # an industry total <= 0 would flip the share
    mk, tot = mk[keep], tot[keep]
    share2 = (mk["val"] / tot) ** 2
    return share2.groupby([mk["months_back"].to_numpy(), mk["sic"].to_numpy()]).sum()


def _compute(ctx):
    sic = sic_group(ctx.ticker_meta(["siccode"])["siccode"], 4)      # universe IDs
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
    name="HerfAsset",
    col="f_herfasset",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: a LOW asset Herfindahl (competitive industry) is the long side
    weight=1.0,
    inputs=("SF1.assets", "SF1.fxusd", "TICKERS.siccode"),
    osap_acronym="HerfAsset",
    source="Hou and Robinson 2006 (Journal of Finance)",
    lookback_months=51,             # 36 month-ends, each filing up to 15 months stale
    notes="36-month mean of the market-scope SIC4 assets Herfindahl (assets/fxusd), min 12; 49xx NaN; current SIC",
    field_mappings=(
        ("compustat.at", "SF1.assets / SF1.fxusd (ART, market scope)",
         "filing-date availability at each month-end vs OSAP annual at datadate + 6m; USD before the cross-firm sum; level"),
        ("crsp.sicCRSP", "TICKERS.siccode via sic_group(., 4)",
         "CURRENT classification applied to all history (12.3% of tickers changed SIC since 1998); SIC4 grouping as the pinned code does, not SIC3"),
        ("crsp.shrcd", "TICKERS.category (market scope)",
         "no separate share code; shrcd 12 (scored-out in OSAP) is scored here"),
        ("crsp.smt_row / m_aCompustat row", "listed at lag AND filing <= 15 months old",
         "OSAP needs a Compustat record; here a non-null assets filing in age"),
        ("asrol 36m min 12", "36 month-end lags, >= 12 valid",
         "firm presence at a lag via has_price_at (7-day tolerance)"),
        ("regulated-industry NaN", "SIC // 100 == 49 only",
         "the dated 4011/4210/4213/4512/4812/4813 exclusions end <= 1982, outside the window"),
    ),
)
