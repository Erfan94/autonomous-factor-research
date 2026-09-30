"""
CompEquIss — five-year log growth in market value of equity minus the
five-year buy-and-hold return. The residual is the part of market-cap growth
not explained by the stock's own return, i.e. net equity issuance (positive)
or repurchase (negative) over five years; heavy issuers are predicted to earn
LOWER returns, so the long leg is LOW CompEquIss.

OSAP: CompEquIss, Daniel and Titman 2006, Journal of Finance ("Market
reactions to tangible and intangible information"; composite equity
issuance). Predicted sign: - (SignalDoc Sign = -1: high value, low return).
Spec: osap_source/cache/b4e911e6/CompEquIss/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  Route A (one route at BOTH ends):
    ME_t     = SEP.close_t    x SF1.sharesbas(ARQ, latest filing known at t)
    ME_t-60  = SEP.close_t-60 x SF1.sharesbas(ARQ, latest filing known at the
               t-60 business month-end)
    both prices via ctx.at_month_end("SEP", ...) (last trade on or before the
    business month-end, 7-day tolerance), both share counts via
    ctx.fundamentals_at_month_ends(["sharesbas"], [0, 60], dimension="ARQ").
  BH = SEP.closeadj_t / SEP.closeadj_t-60 - 1, a SIMPLE total return read at
    the same two trade dates as the prices (closeadj includes dividends).
  CompEquIss = log(ME_t / ME_t-60) - BH.
  This is OSAP's formula exactly: a LOG growth minus a SIMPLE return. The
  signal therefore equals log(share ratio) - [R - log(1+R)], with
  R - log(1+R) ~ R^2/2 >= 0, so it carries the five-year return's convexity
  as well as issuance. Replicated, not corrected.
  ME > 0 and closeadj > 0 at both ends are required; else NaN.
  Price basis: sharesbas is split-restated to TODAY's basis, SEP.close is
  split-adjusted to the same basis, so close x sharesbas is consistent at any
  date (it matches DAILY.marketcap within 1% on 97.5-99.7% of the universe).
  sharesbas is NEVER paired with closeunadj (known trap
  sf1_share_counts_split_restated). The ME ratio is also invariant to the
  common split factor, so using the same basis at both ends is what matters.
  history_months=60: the harness nulls names without a price within 7 days of
  the month-end 60 months back (return window).

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? There is no single value:
  a firm with unchanged shares gets -(R - log(1+R)), a smooth function of its
  five-year return R.
  What share of the universe does nothing? Not applicable as a tie; the
  checker measured a modal share of 0.07% (2008-12). Preflight to confirm.
  Tie handling: null (ME or price <= 0 or missing at either end -> NaN, so
  blend_ranks renormalises). No zero-fill, no floor, no sample restriction.

DEVIATIONS FROM OSAP:
  - mve_c = |prc| x shrout per PERMNO in CRSP; here company-level market
    cap (close of the ticker x SF1 cover-page share count, all classes), so
    dual-class issuance is measured at the company level. The five-year
    RATIO of a company-level cap is what a multi-class firm's issuance means.
  - share counts step at SF1 filing dates (ARQ datekey), not monthly as CRSP
    shrout; the issuance piece is quarterly-stepwise.
  - dlret: no delisting return enters BH (none in Sharadar). A name alive at
    t has no delisting in its window, so this touches only survivor
    composition.
  - SignalDoc filter abs(prc)>5 (OSAP portfolio stage) not reproduced; the
    harness universe is price >= $1.
  - coverage: Route A needs an SF1 filing known at the t-60 end. Earliest SF1
    datekey is 1993-12-22 but coverage is thin until 1998; Route A first
    scores 2002-12 (~50% of the universe), ~79% from 2003-06. Decision months
    1999-01..2002-11 are empty by construction.
  - OSAP's calendar-exact 60-month lag is replaced by the business
    month-end 60 months back with a 7-day tolerance (same rule as the harness
    history gate).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef


def _compute(ctx):
    p0 = ctx.at_month_end("SEP", ["close", "closeadj"], 0)
    p60 = ctx.at_month_end("SEP", ["close", "closeadj"], 60)

    sh = ctx.fundamentals_at_month_ends(["sharesbas"], [0, 60], dimension="ARQ")
    sh = sh.pivot_table(index="ID", columns="months_back", values="sharesbas", aggfunc="last")
    sh0 = sh[0].astype(float).reindex(ctx.ids) if 0 in sh.columns else pd.Series(np.nan, index=ctx.ids)
    sh60 = sh[60].astype(float).reindex(ctx.ids) if 60 in sh.columns else pd.Series(np.nan, index=ctx.ids)

    c0 = p0["close"].astype(float).reindex(ctx.ids)
    c60 = p60["close"].astype(float).reindex(ctx.ids)
    a0 = p0["closeadj"].astype(float).reindex(ctx.ids)
    a60 = p60["closeadj"].astype(float).reindex(ctx.ids)

    me0 = (c0 * sh0).where((c0 > 0) & (sh0 > 0))
    me60 = (c60 * sh60).where((c60 > 0) & (sh60 > 0))
    bh = a0 / a60.where(a60 > 0) - 1.0      # simple total return, as OSAP

    growth = np.log(me0 / me60.where(me60 > 0))
    out = growth - bh.where(a0 > 0)
    return out.replace([np.inf, -np.inf], np.nan)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="CompEquIss",
    col="f_compequiss",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: LOW CompEquIss (net repurchasers) is attractive
    weight=1.0,
    inputs=("SEP.close", "SEP.closeadj", "SF1.sharesbas"),
    osap_acronym="CompEquIss",
    source="Daniel and Titman 2006 (Journal of Finance)",
    lookback_months=75,             # 60-month window + latest ARQ filing up to 15 months old at the t-60 end
    history_months=60,              # 60-month return window
    notes="log(ME_t/ME_t-60) - simple 60m closeadj return; ME = SEP.close x ARQ sharesbas; sign -1",
    field_mappings=(
        ("crsp.mve_c (|prc| x shrout)", "SEP.close x SF1.sharesbas (ARQ) at t and t-60 (Route A)",
         "company-level cap, share count steps at filing dates; sharesbas is split-restated to today's basis so paired with split-adjusted SEP.close, never closeunadj"),
        ("crsp.ret (tempIdx cumprod, dlret-adjusted)", "SEP.closeadj_t / SEP.closeadj_t-60 - 1",
         "month-end ratio, total return; no delisting return; simple return subtracted from a log growth as in OSAP"),
        ("calendar-exact 60-month lag", "ctx.at_month_end(..., 60), 7-day tolerance",
         "business month-end 60 months back; same rule as the history gate"),
        ("Filter abs(prc)>5", "not reproduced", "harness universe is price >= $1"),
        ("coverage start", "first valid month 2002-12", "sharesbas known at the t-60 end: ~50% of universe 2002-12, ~79% from 2003-06; 1999-01..2002-11 empty"),
    ),
)
