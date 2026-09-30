"""
IntanBM — the "intangible return" on book-to-market: the residual of the
five-year stock return after regressing it, each month across the market, on
the five-year-lagged log book-to-market and on (change in log BM + the
five-year return). A high residual (return not explained by the change in
BM) is predicted to precede LOW returns (long-term-reversal type).

OSAP: IntanBM, Daniel and Titman 2006, Journal of Finance ("Market reactions
to tangible and intangible information", Table 4). Predicted sign: -
(SignalDoc Sign = -1; long LOW IntanBM).
Spec: osap_source/cache/b4e911e6/IntanBM/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  All inputs are read at market scope (every listed common stock that traded
  in the lag's month), at lags k in {0, 60} months (business month-ends, 7-day
  price tolerance):
    ME_k   = SEP.close_k x SF1.sharesbas_k  (latest ART filing known at month-end k)
             close and sharesbas are both on today's split basis; sharesbas is
             never paired with closeunadj.
    BE_k   = SF1.equity_k  (latest ART filing known at k)
    BM_k   = log(BE_k / ME_k), NaN unless BE_k > 0 and ME_k > 0
    Ret60  = SEP.closeadj_0 / SEP.closeadj_60 - 1  (simple total return, closeadj > 0 both ends)
    Ret60 is TRIMMED each month with harness.crosssection.cs_trim at the
    1st / 99th percentile of THAT month's market-scope values (values outside
    become NaN and leave the regression).
    BMRet  = BM_0 - BM_60 + Ret60
  Each month: OLS  Ret60 ~ const + BM_60 + BMRet  on the market-scope names
  with all three present, via harness.crosssection.ols_residual (min 30 fit
  rows); IntanBM is the residual. The fit sample is the whole listed market
  (as OSAP fits on all CRSP-Compustat firms); only universe IDs are scored
  (the result is reindexed to ctx.ids).
  history_months=60, lookback_months=75 (60-month window + an ART filing up to
  15 months old at the t-60 month-end).

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? None: a firm with unchanged
  book equity and price still gets -(a + b1 BM_60 + b2 BMRet) plus its return
  term, a continuous residual with no constant.
  What share of the universe does nothing? Not applicable as a tie; the spec
  measured a modal share of 0.064-0.072% (one name) and 10 qcut bins in every
  sampled month. Preflight to confirm.
  Tie handling: null (BE or ME <= 0 or missing at either end, closeadj <= 0,
  a trimmed Ret60, or a non-USD reporting currency -> NaN, so blend_ranks
  renormalises). No zero-fill, no floor, no sample restriction beyond the
  regression's own listwise deletion.

DEVIATIONS FROM OSAP:
  - ME = SEP.close x SF1.sharesbas without SF1.sharefactor (as EP and CompEquIss):
    for the few multi-class names whose sharefactor is not 1 (e.g. BRK-type, 8.75
    in 1999 falling to 1.6) ME and hence BM_60 and dBM are mis-scaled.
  - ceq -> SF1.equity (ART): preferred stock is not removed (Sharadar has no
    preferred field; book_equity_preferred_terms ruling), approx. ART equity
    is a level (ART == ARQ on the same reportperiod): no smear, no dimension
    override.
  - mve_permco (company cap, months t and t-60) -> SEP.close x SF1.sharesbas
    at each end (company-level share count on the primary ticker x the
    ticker's price), NOT DAILY.marketcap, whose history starts 1998-12 and
    would empty the first 60 signal months. Share counts step at filing dates.
  - tempRet60's 1/99 trim: OSAP's winsor2 trims over the WHOLE pooled panel
    (all months, future included: a look-ahead); here it is per month,
    market-scope, over names with a valid Ret60 (not only Compustat-linked
    names).
  - Fundamentals as known by datekey (quarterly refresh), not the annual file
    plus 6 months; BM_0 therefore uses the latest filing, BM_60 the filing
    known five years earlier.
  - Non-USD filers (SF1.fxusd != 1 at either end) are set missing: SF1 equity
    is in the reporting currency while price is USD and sharesbas may not
    match the listing (sf1_reporting_currency; same gate as AM / BMdec). This
    removes such names from the regression sample too.
  - Cumulative return is the calendar closeadj ratio at two month-ends; OSAP
    cumprods over merged rows (breaking at months without a Compustat link,
    NaN ret -> 0). No delisting return (Sharadar has none).
  - SignalDoc filter abs(prc)>5 (portfolio stage) not reproduced; the harness
    universe is price >= $1.
  - A regression needs a price and filing at t-60 here (60 calendar
    months), OSAP a row exactly 60 months back. First scorable decision month
    depends on SF1 at t-60 (sharesbas known from ~1997Q4 filings; thin until
    1998): decision months up to about 2002-11 are expected empty or thin.
"""

import numpy as np
import pandas as pd

from harness.crosssection import cs_trim, ols_residual
from harness.factor_def import FactorDef


def _wide(df, col):
    return df.pivot_table(index="ID", columns="months_back", values=col, aggfunc="last")


def _at(w, k):
    return w[k].astype(float) if k in w.columns else pd.Series(dtype="float64")


def _compute(ctx):
    px = ctx.at_month_ends("SEP", ["close", "closeadj"], [0, 60], scope="market")
    fd = ctx.fundamentals_at_month_ends(["equity", "sharesbas", "fxusd"], [0, 60], scope="market")
    if px.empty or fd.empty:
        return pd.Series(np.nan, index=ctx.ids)

    close, adj = _wide(px, "close"), _wide(px, "closeadj")
    eq, sh, fx = _wide(fd, "equity"), _wide(fd, "sharesbas"), _wide(fd, "fxusd")

    bm = {}
    for k in (0, 60):
        c, s, e, x = _at(close, k), _at(sh, k), _at(eq, k), _at(fx, k)
        me = (c * s).where((c > 0) & (s > 0))
        be = e.where((e > 0) & (x == 1.0))
        bm[k] = np.log(be / me)              # NaN unless both positive and USD

    a0, a60 = _at(adj, 0), _at(adj, 60)
    ret60 = a0.where(a0 > 0) / a60.where(a60 > 0) - 1.0
    ret60 = cs_trim(ret60.replace([np.inf, -np.inf], np.nan), 1.0, 99.0)

    idx = ret60.index.union(bm[0].index).union(bm[60].index)
    y = ret60.reindex(idx)
    bm0, bm60 = bm[0].reindex(idx), bm[60].reindex(idx)
    X = pd.DataFrame({"bm60": bm60, "bmret": bm0 - bm60 + y})
    X = X.replace([np.inf, -np.inf], np.nan)
    resid = ols_residual(y, X, min_obs=30)
    return resid.reindex(ctx.ids)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="IntanBM",
    col="f_intanbm",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: LOW intangible return is attractive
    weight=1.0,
    inputs=("SEP.close", "SEP.closeadj", "SF1.equity", "SF1.sharesbas", "SF1.fxusd"),
    osap_acronym="IntanBM",
    source="Daniel and Titman 2006 (Journal of Finance)",
    lookback_months=75,             # 60-month window + latest ART filing up to 15 months old at the t-60 end
    history_months=60,              # 60-month return window
    notes="residual of monthly market-scope OLS: Ret60 ~ 1 + logBM(t-60) + (logBM(t) - logBM(t-60) + Ret60); Ret60 trimmed 1/99 per month; sign -1",
    field_mappings=(
        ("compustat.ceq", "SF1.equity (ART)",
         "preferred stock not removed (no SF1 preferred field; book_equity_preferred_terms ruling); as known by datekey at each month-end"),
        ("crsp.mve_permco (months t and t-60)", "SEP.close x SF1.sharesbas (ART) at each end",
         "company-level cap, share count steps at filing dates; both on today's split basis; not DAILY.marketcap (history starts 1998-12)"),
        ("crsp.ret cumprod over 60 months", "SEP.closeadj_t / SEP.closeadj_t-60 - 1",
         "month-end ratio, total return; no delisting return; 7-day tolerance"),
        ("winsor2(tempRet60, trim, 1/99) pooled over the whole panel", "harness.crosssection.cs_trim per month",
         "OSAP's pooled trim uses future months (look-ahead); trimmed per month over market-scope names with a valid Ret60"),
        ("all CRSP-Compustat regression sample", "market-scope accessors, ols_residual, min 30 rows",
         "fit over every listed common stock alive at each lag; only universe IDs scored"),
        ("currency", "SF1.fxusd == 1 gate at both ends",
         "equity is in reporting currency, price in USD; non-USD filers set missing"),
        ("Filter abs(prc)>5", "not reproduced", "harness universe is price >= $1"),
    ),
)
