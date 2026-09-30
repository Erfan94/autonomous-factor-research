"""
ChInvIA — industry-adjusted growth of annual capital expenditure. Firms whose
capex grew most relative to their own recent history and to their 2-digit-SIC
peers have over-invested; OSAP predicts they earn lower returns.

OSAP: ChInvIA, Abarbanell and Bushee 1998 (The Accounting Review), Table 2b
RCAPX. Predicted sign: - (SignalDoc Sign = -1; low value = long side).
Spec: osap_source/cache/b4e911e6/ChInvIA/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  capx       = -SF1.capex (dimension ARY, fiscal-year value; Sharadar reports
               capex as a cash outflow, negative).
  l12, l24   = the same fiscal year one and two years earlier, from
               ctx.fundamentals_yoy(["capex"], years=1) and (years=2), aligned
               by reportperiod.
  avg        = 0.5 * (capx_l12 + capx_l24)
  pchcapx    = (capx - avg) / avg            where avg > 0 (both lags present)
  fallback   = (capx - capx_l12) / capx_l12  where pchcapx is null and capx_l12 > 0
               (OSAP's own rule: the one-year form wherever the two-year
               form is missing, including avg == 0).
  ChInvIA    = pchcapx - mean(pchcapx over all listed common stocks sharing the
               firm's 2-digit SIC group that month).
  The industry mean is taken on ctx.market_context() (OSAP averages over the
  whole CRSP x Compustat cross-section, not the screened universe) with
  harness.industry.sic_group(TICKERS.siccode, 2) and group_demean, then
  reindexed to ctx.ids. No winsorising or clipping (none in OSAP).

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? pchcapx = 0 (capex identical
    in all three years), so ChInvIA = -(its SIC2 mean), a per-group constant.
  What share of the universe does nothing? Literally identical capex is about
    0.03% of computable ARY firm-years. The real cluster is capex falling to
    exactly 0 from a positive base: pchcapx = -1 exactly, so ChInvIA is the
    same value within a SIC2-month; measured by the field-checker at 0.0-0.4%
    of the universe, the LOWEST raw value and so the long extreme under
    Sign -1. Preflight measures the modal share.
  Tie handling: remove/null where a denominator is non-positive (avg <= 0 and
    l12 <= 0 -> null, never floored); the small -1 cluster is left to the
    harness's average-rank tie treatment (well under the 10% mass-point bar).

DEVIATIONS FROM OSAP:
  - capx: -SF1.capex, ARY not ART. ART capex is null 46% of firms in 1998 (ARY
    0.5%) and is a TTM sum that equals ARY only at fiscal year-end; ARY matches
    OSAP's annual item and its two prior fiscal years.
  - capx fallback (capx := ppent - ppent_l12 when capx is missing) DROPPED:
    SF1.ppnenet zeros are structural vendor zero-fill (mostly unclassified
    balance sheets) and the fallback is eligible on <= 0.2% of the universe.
    A missing capx stays null.
  - Denominator sign: OSAP nulls only avg == 0 (falling back to the one-year
    form); here avg <= 0 is nulled, then the one-year fallback needs
    capx_l12 > 0. Sharadar positive capex (a sign-inverted outflow) and zero
    bases are 0.8-5.1% of the universe; OSAP would keep negative bases.
  - Lags: fiscal-year alignment by reportperiod (tolerance 45 days) instead of
    OSAP's calendar-month lag of a datadate+6-month replicated series. The new
    year enters at the 10-K filing date (about 3 months after year-end) rather
    than 6 months, so the signal is 2-4 months fresher; OSAP's 6-month annual
    lag is not reproduced. Updates once per firm-year.
  - Early-window coverage: SF1 starts 1997Q4, so the two-lag form exists from
    about 2000; 1999 rests mainly on the one-year fallback. Measured computable
    two-lag share: 24% at 1999-01, 37% at 1999-12, 74% from 2000-12.
  - Industry mean: SIC is TICKERS.siccode, TODAY's classification, not the
    point-in-time CRSP siccd. This is a look-ahead that enters the signal VALUE
    through the industry mean (the D3 kind), not just a sample filter.
    Missing SIC -> null (OSAP groups it as "na"). The harness's group floor of
    5 non-null members yields null where OSAP (no floor) would give 0 for a
    one-firm group. 3-digit codes: sic_group(.., 2) gives the first digit pair
    of the zero-padded 4-digit code; OSAP takes str(sic)[:2]; immaterial
    (68 of 20,829 codes).
  - Currency: capex ratios are currency-invariant within a firm, so non-USD
    reporters need no fxusd gate.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef
from harness.industry import group_demean, sic_group


def _pchcapx(c):
    """Growth of annual capex over the mean of the two prior years, one-year
    form where the two-year form is not admissible. `c` is a MonthContext."""
    y1 = c.fundamentals_yoy(["capex"], years=1, dimension="ARY")
    y2 = c.fundamentals_yoy(["capex"], years=2, dimension="ARY")
    capx = -y1["capex"].astype(float)
    l12 = -y1["capex_lag"].astype(float)
    l24 = -y2["capex_lag"].reindex(y1.index).astype(float)

    avg = 0.5 * (l12 + l24)
    two = (capx - avg) / avg.where(avg > 0)
    one = (capx - l12) / l12.where(l12 > 0)
    return two.where(two.notna(), one)


def _compute(ctx):
    mctx = ctx.market_context()
    pch = _pchcapx(mctx)
    sic = mctx.ticker_meta(["siccode"], scope="market")["siccode"].reindex(pch.index)
    adj = group_demean(pch, sic_group(sic, 2))
    return adj.reindex(ctx.ids)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="ChInvIA",
    col="f_chinvia",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: high capex growth predicts low returns
    weight=1.0,
    inputs=("SF1.capex", "TICKERS.siccode"),
    osap_acronym="ChInvIA",
    source="Abarbanell and Bushee 1998 (The Accounting Review)",
    lookback_months=39,             # 24m (two prior fiscal years) + 15m max filing age
    # No history_months: no SEP price window is read.
    dimension="ARY",                # ART capex is 46% null in 1998 and a TTM sum; annual item wanted
    notes="annual capex growth vs mean of two prior years (one-year fallback), minus market-wide SIC2 mean",
    field_mappings=(
        ("compustat.capx", "-SF1.capex (ARY)",
         "sign flip (Sharadar capex is an outflow); ARY fiscal-year value, filing-date lag not datadate+6m; "
         "avg <= 0 nulled (OSAP nulls avg == 0 only), one-year fallback needs l12 > 0"),
        ("compustat.ppent", "dropped",
         "OSAP capx fallback (ppent - ppent_l12) not reproduced: ppnenet zeros are vendor zero-fill; eligible <= 0.2%"),
        ("crsp.siccd (sicCRSP)", "TICKERS.siccode (CURRENT)",
         "today's classification, not point-in-time; look-ahead enters the signal value via the industry mean (D3 kind); "
         "2-digit via sic_group"),
        ("industry mean", "harness.industry.group_demean on ctx.market_context()",
         "market-wide like OSAP; harness group floor of 5 (OSAP none); missing SIC -> null"),
    ),
)
