"""
HerfBE — industry concentration by book equity: the three-year average of the Herfindahl
index of firm book equity within the firm's SIC industry. Low concentration (a
competitive industry) is the long side.

OSAP: HerfBE, Hou and Robinson 2006, Journal of Finance (Table 2, H(Equity)).
Predicted sign: - (SignalDoc Sign = -1: a LOW HerfBE is the long side; ascending=False,
the raw value is NOT negated here).
Spec: osap_source/cache/b4e911e6/HerfBE/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  Market scope (every listed common stock, no price/size/liquidity screen: OSAP sums over
  all of CRSP, not over the harness universe), for each of the 36 month-ends s = 0..35
  (s = 0 is the signal month):
    be[i,s]       = (SF1.equity + SF1.taxliabilities.fillna(0)) / SF1.fxusd   (ART, USD)
                    a firm needs a non-null SF1.equity; NO floor, negative book equity stays
    indequity[k,s]= sum of be over firms with SIC4 == k and a non-null be[i,s]
    tempHerf[k,s] = sum over those firms of (be[i,s]/indequity[k,s])^2
  Firm value = mean of tempHerf[SIC4 of the firm, s] over the lags s in 0..35 at which the
  firm traded, at least 12 valid lags (OSAP asrol, 36 x 1 month, min 12). Every firm of an
  industry receives the industry's value whether or not it reports equity itself; only
  universe names are scored. NaN if the firm's SIC is missing, or if SIC // 100 == 49
  (OSAP: SIC starting "49"; the dated pre-1983 exclusions never bind after 1998).
  Grouping is on the integer TICKERS.siccode through harness.industry.sic_group(sic, 4),
  as the pinned code does (its sic3D variable is str(sic)[:4], the full four digits,
  despite the name). Raw level, no log, no winsorising (the harness ranks within sector).
  No SF1 lag beyond the filing date.
  NEGATIVE BOOK EQUITY IS REPRODUCED, NOT FIXED. OSAP does not floor it: a negative-equity
  firm, or an industry whose summed equity is small or negative, gives shares outside
  [0, 1] and H > 1 (unbounded above; spec: H > 1 on about 2.3% of scored rows, at most
  5.3% of a month). The share is SQUARED, so a negative industry total does not flip the
  sign of the result, and the only denominator skipped is an exactly zero (or non-finite)
  industry total, where the ratio is undefined. These rows rank at the top of the
  cross-section (a tail, not a mass point).
  Early months are UNMASKED: lags before the ART panel is full enter the mean with
  industry sums over the part of the listed names that have a filing; the 36-month mean
  dilutes this.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? The concept does not apply: HerfBE is an
  INDUSTRY attribute, so every firm in a SIC4 with the same 36-month listing history
  shares one value. The mass points are industry blocks, not stale defaults. A sole
  reporter in its SIC4 is exactly 1.0 (about 0.9% of scored names).
  What share of the universe sits on one value? Spec measured on the harness universe,
  all 276 signal months: modal-value share of the cross-section median 5.9%, max 7.7%,
  0 months at or above the 10% cliff, 10 qcut bins every month, median 430 distinct values.
  The largest block is SIC 6798 (REITs), 94 names (2008-12) to 136 (2021-11). Preflight
  re-measures it.
  WITHIN SECTOR (ranks are formed among sector peers) the ties concentrate: in Real Estate
  ~82-92% of names share the one SIC 6798 value (92% 2008-12, 86% 2013-12, 82% 2021-11),
  in Energy ~39-44% (SIC 1311) share one, Healthcare 26-30%, Technology 18-22%, Financial
  Services 18-21%, Communication Services 13-23%; Utilities has 1-2 names (the < 10-name
  fallback to the cross-section rank applies, and 49xx is nulled anyway). Within-sector
  ranking therefore gives the Real Estate and Energy sectors little information. This is
  stated, not worked around: the values are real, and no tie handling (null, remove,
  floor) is applied.
  Tie handling: none beyond the average rank the harness applies.

DEVIATIONS FROM OSAP:
  - OSAP quirk not reproduced: an SIC4-month whose firms have no (or only zero) sales gets
    tempHerf = 0 in OSAP through pandas' empty sum, which lands on the long side; here that
    lag is dropped from the firm's 36-month mean.
  - Book equity: OSAP tempBE = seq (fallback ceq + preferred, then at - lt) + txditc -
    preferred (pstk, else pstkrv, else pstkl). Sharadar has no preferred-stock line, so
    SF1.equity + SF1.taxliabilities.fillna(0) is used and PREFERRED IS NOT REMOVED (per the
    book_equity_preferred_terms ruling this makes the predictor approximate): a firm with
    large preferred stock is overstated in its industry's equity. SF1.equity is one line
    including preferred, so it plays seq; the ceq/at-lt fallbacks are dropped (equity null
    0.05%). SF1.taxliabilities stands in for txditc (a generic tax-liability line, not
    deferred taxes and investment tax credit; the vendor zero-fills about 51% of it).
  - Industry code: TICKERS.siccode is today's classification, applied to all history; OSAP's
    sicCRSP is point-in-time (12.3% of tickers changed SIC since 1998). It enters the
    signal VALUE (industry grouping and the 49xx exclusion): look-ahead through
    reclassified firms.
  - Market scope: Sharadar common stock (category Domestic Common Stock*) on NYSE/NASDAQ/
    NYSEMKT; there is no separate shrcd, so OSAP's shrcd > 11 -> NaN (share class 12) is
    not reproduced and those names are scored.
  - Timing: SF1 ART levels as known at each month-end by filing date, vs OSAP's annual
    data at datadate + 6 months forward-filled; converted to USD with be/fxusd; filings
    appear 2-4 months earlier than OSAP's rule. No extra lag.
  - Row presence at lag s: a firm counts in an industry sum at s if it traded that month
    (market-scope listing rule) AND has a filing <= 15 months old with non-null equity;
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
    """Series indexed by (months_back, SIC4): sum of squared book-equity shares, market scope."""
    mk = ctx.fundamentals_at_month_ends(["equity", "taxliabilities", "fxusd"], range(_WINDOW),
                                        scope="market")
    if mk.empty:
        return None
    sic = sic_group(ctx.ticker_meta(["siccode"], scope="market")["siccode"], 4)
    fx = mk["fxusd"].astype(float)
    be = mk["equity"].astype(float) + mk["taxliabilities"].astype(float).fillna(0.0)
    # null equity stays null (be is NaN); no floor on negative book equity
    mk = mk.assign(val=be / fx.where(fx > 0),            # USD before any cross-firm sum
                   sic=mk["ID"].map(sic)).dropna(subset=["val", "sic"])
    if mk.empty:
        return None
    grp = [mk["months_back"].to_numpy(), mk["sic"].to_numpy()]
    tot = mk.groupby(grp)["val"].transform("sum")
    keep = np.isfinite(tot) & (tot != 0)                # squared share: a negative total does not flip the sign; zero is undefined
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
    name="HerfBE",
    col="f_herfbe",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: a LOW equity Herfindahl (competitive industry) is the long side
    weight=1.0,
    inputs=("SF1.equity", "SF1.taxliabilities", "SF1.fxusd", "TICKERS.siccode"),
    osap_acronym="HerfBE",
    source="Hou and Robinson 2006 (Journal of Finance)",
    lookback_months=51,             # 36 month-ends, each filing up to 15 months stale
    notes="36-month mean of the market-scope SIC4 book-equity Herfindahl, BE = equity + taxliabilities (preferred not removed), no floor; 49xx NaN; current SIC",
    field_mappings=(
        ("compustat.seq (+ ceq/at-lt fallbacks)", "SF1.equity (ART, market scope)",
         "one equity line including preferred; fallback chain dropped (equity null 0.05%); USD via fxusd before the cross-firm sum"),
        ("compustat.pstk/pstkrv/pstkl", "none (unavailable)",
         "preferred stock NOT subtracted (book_equity_preferred_terms ruling: approx); a large-preferred firm's equity is overstated"),
        ("compustat.txditc", "SF1.taxliabilities.fillna(0)",
         "generic tax-liability line, not deferred taxes + ITC; vendor zero-fills ~51% of it"),
        ("tempBE unfloored", "be not floored",
         "negative book equity reproduced; H > 1 on ~2% of rows as in OSAP; only a zero industry total is skipped"),
        ("crsp.sicCRSP", "TICKERS.siccode via sic_group(., 4)",
         "CURRENT classification applied to all history (12.3% of tickers changed SIC since 1998); SIC4 grouping as the pinned code does, not SIC3"),
        ("crsp.shrcd", "TICKERS.category (market scope)",
         "no separate share code; shrcd 12 (scored-out in OSAP) is scored here"),
        ("crsp.smt_row / m_aCompustat row", "listed at lag AND filing <= 15 months old",
         "OSAP needs a Compustat record; here a non-null equity filing in age"),
        ("asrol 36m min 12", "36 month-end lags, >= 12 valid",
         "firm presence at a lag via has_price_at (7-day tolerance)"),
        ("regulated-industry NaN", "SIC // 100 == 49 only",
         "the dated 4011/4210/4213/4512/4812/4813 exclusions end <= 1982, outside the window"),
    ),
)
