"""
IntanCFP — the "intangible return" on cash-flow-to-price: the residual of the five-year
stock return after regressing it, each month across the market, on the
five-year-lagged cash-flow-to-market-equity (CFP) ratio and on (change in the ratio + the five-year
return). A high residual (return not explained by the change in the ratio)
is predicted to precede LOW returns (long-term-reversal type).

OSAP: IntanCFP, Daniel and Titman 2006, Journal of Finance ("Market reactions
to tangible and intangible information", Table 4). Predicted sign: -
(SignalDoc Sign = -1; long LOW IntanCFP).
Spec: osap_source/cache/b4e911e6/IntanCFP/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  All inputs are read at market scope (every listed common stock that traded
  in the lag's month), at lags k in {0, 60} months (business month-ends, 7-day
  price tolerance):
    ME_k   = SEP.close_k x SF1.sharesbas_k  (latest ARY filing known at month-end k)
             close and sharesbas are both on today's split basis; sharesbas is
             never paired with closeunadj; ME_k = NaN unless close > 0 and
             sharesbas > 0 and SF1.fxusd_k == 1
    num_k  = (ib_k + dp_k), ib = SF1.netinc + SF1.netincdis  (PLUS: known_trap
             sf1_netincdis_sign_inverted), dp = SF1.depamor.fillna(0)  (ARY)
    X_k    = CFP_k = (ib_k + dp_k) / ME_k  (a level, may be negative; no log,
             no positivity requirement: loss makers are scored as OSAP does)
    Ret60  = SEP.closeadj_0 / SEP.closeadj_60 - 1  (simple total return, closeadj > 0 both ends)
    Ret60 is TRIMMED each month with harness.crosssection.cs_trim at the
    1st / 99th percentile of THAT month's market-scope values (values outside
    become NaN and leave the regression). X is not trimmed (as OSAP).
    XRet   = X_0 - X_60 + Ret60
  Each month: OLS  Ret60 ~ const + X_60 + XRet  on the market-scope names with
  all three present, via harness.crosssection.ols_residual (min 30 fit rows);
  IntanCFP is the residual. The fit sample is the whole listed market (as OSAP fits
  on all CRSP-Compustat firms); only universe IDs are scored (the result is
  reindexed to ctx.ids).
  dimension="ARY" (coordinator decision intan_flows_dimension): the flow
  numerator is OSAP's annual Compustat item. ARY is a level at each filing, so
  X_0 - X_60 is a five-year difference of two annual levels: no four-quarter
  smear. ARQ is never used (a single quarter would be a quarter-sized numerator).
  history_months=60, lookback_months=75 (60-month window + an annual filing up
  to 15 months old, the config cap, at the t-60 month-end).

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? None: a firm with unchanged
  fundamentals and price still gets -(a + b1 X_60 + b2 XRet) plus its return
  term, a continuous residual with no constant.
  What share of the universe does nothing? Not applicable as a tie; the spec
  measured a modal share of 0.06-0.07% (one name) and 10 qcut bins in every
  sampled month. Preflight to confirm.
  Tie handling: null (ME <= 0 or missing, netinc or netincdis missing, fxusd != 1
  at either end, closeadj <= 0, or a trimmed Ret60
  -> NaN, so blend_ranks renormalises). No floor, no sample restriction
  beyond the regression's own listwise deletion.
  Zero-fill: depamor is zero-filled ONLY on rows where a filing exists (OSAP's
  own zero_fill_vars includes dp; a missing depamor there is a real zero). The
  fill is applied on the long frame BEFORE the wide pivot so that a missing
  filing (no row) stays NaN. netinc / netincdis are not zero-filled (OSAP does
  not zero-fill ib).

DEVIATIONS FROM OSAP:
  - SIGNALDOC DISCREPANCY: the SignalDoc definition says (net income (ni) + dp);
    the OSAP CODE uses (ib + dp). The code is the authority; ib is translated.
  - ib -> SF1.netinc + SF1.netincdis (ARY): income after non-controlling interest,
    extraordinary items not separable (approx). netincdis enters with a PLUS
    (known_trap sf1_netincdis_sign_inverted). netinccmn is NOT used (it is
    ibcom, after preferred dividends).
  - dp -> SF1.depamor (ARY), zero-filled where a filing row exists (OSAP rule).
  - ME = SEP.close x SF1.sharesbas without SF1.sharefactor (as IntanBM, EP,
    CompEquIss): for the few multi-class names whose sharefactor is not 1, ME
    and hence X_60 and dX are mis-scaled.
  - mve_permco (company cap, months t and t-60) -> SEP.close x SF1.sharesbas
    at each end (company-level share count on the primary ticker x the
    ticker's price), NOT DAILY.marketcap, whose history starts 1998-12 and
    would empty the first 60 signal months. Share counts step at filing dates.
  - tempRet60's 1/99 trim: OSAP's winsor2 trims over the WHOLE pooled panel
    (all months, future included: a look-ahead); here it is per month,
    market-scope, over names with a valid Ret60.
  - Fundamentals as known by datekey (annual ARY filing carried until the next
    one, at most 15 months), not annual file plus 6 months.
  - Non-USD filers (SF1.fxusd != 1 at either end) are set missing: the flow is
    in the reporting currency while price is USD (sf1_reporting_currency; same
    gate as IntanBM). This removes such names from the regression sample too.
  - Cumulative return is the calendar closeadj ratio at two month-ends; OSAP
    cumprods over merged rows (NaN ret -> 0). No delisting return.
  - SignalDoc filter abs(prc)>5 not reproduced in the factor; the harness universe
    is price >= $1.
  - A regression needs a price and filing at t-60 here (60 calendar months),
    OSAP a row exactly 60 months back. Decision months before about 2002-12 are
    empty (t-60 before the SEP/SF1 start); the first scorable signal is
    2002-12-31, with thin coverage until 2004-03.
  - The unstable, untrimmed-regressor fit is reproduced as stated (OSAP trims
    only the return): a few extreme ratios can dominate some months' fit.
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
    fd = ctx.fundamentals_at_month_ends(["netinc", "netincdis", "depamor", "sharesbas", "fxusd"], [0, 60],
                                        dimension="ARY", scope="market")
    if px.empty or fd.empty:
        return pd.Series(np.nan, index=ctx.ids)
    # OSAP zero-fills dp: fill only on existing filing rows (before the pivot), so
    # an absent filing stays NaN. ib = netinc + netincdis (netincdis sign: PLUS).
    fd = fd.assign(num=(fd["netinc"] + fd["netincdis"]) + fd["depamor"].fillna(0.0))

    close, adj = _wide(px, "close"), _wide(px, "closeadj")
    num, sh, fx = _wide(fd, "num"), _wide(fd, "sharesbas"), _wide(fd, "fxusd")

    x = {}
    for k in (0, 60):
        c, s, n, f = _at(close, k), _at(sh, k), _at(num, k), _at(fx, k)
        me = (c * s).where((c > 0) & (s > 0) & (f == 1.0))
        x[k] = n / me                      # level; NaN where ME or the flow is missing

    a0, a60 = _at(adj, 0), _at(adj, 60)
    ret60 = a0.where(a0 > 0) / a60.where(a60 > 0) - 1.0
    ret60 = cs_trim(ret60.replace([np.inf, -np.inf], np.nan), 1.0, 99.0)

    idx = ret60.index.union(x[0].index).union(x[60].index)
    y = ret60.reindex(idx)
    x0, x60 = x[0].reindex(idx), x[60].reindex(idx)
    X = pd.DataFrame({"x60": x60, "xret": x0 - x60 + y})
    X = X.replace([np.inf, -np.inf], np.nan)
    resid = ols_residual(y, X, min_obs=30)
    return resid.reindex(ctx.ids)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="IntanCFP",
    col="f_intancfp",
    compute=_compute,
    ascending=False,                # SignalDoc Sign = -1: LOW intangible return is attractive
    weight=1.0,
    inputs=("SEP.close", "SEP.closeadj", "SF1.netinc", "SF1.netincdis", "SF1.depamor", "SF1.sharesbas", "SF1.fxusd"),
    osap_acronym="IntanCFP",
    source="Daniel and Titman 2006 (Journal of Finance)",
    dimension="ARY",                # OSAP's annual flow items (also passed explicitly in _compute)
    lookback_months=75,             # 60-month window + latest ARY filing up to 15 months old at the t-60 end
    history_months=60,              # 60-month return window
    notes="residual of monthly market-scope OLS: Ret60 ~ 1 + CFP(t-60) + (CFP(t) - CFP(t-60) + Ret60); CFP = (netinc + netincdis + depamor.fillna(0)) (ARY) / (close x sharesbas); code (ib + dp), not SignalDoc ni + dp; Ret60 trimmed 1/99 per month; sign -1",
    field_mappings=(
        ("compustat.ib", "SF1.netinc + SF1.netincdis (ARY)", "approx: after NCI, extraordinary items not separable; PLUS sign (known_trap sf1_netincdis_sign_inverted); netinccmn not used; SignalDoc says ni, code uses ib"),
        ("compustat.dp", "SF1.depamor.fillna(0) (ARY)", "OSAP zero-fills dp (zero_fill_vars); applied only on existing filing rows"),
        ("crsp.mve_permco (months t and t-60)", "SEP.close x SF1.sharesbas (ARY) at each end",
         "company-level cap, share count steps at filing dates; both on today's split basis; not DAILY.marketcap (history starts 1998-12)"),
        ("crsp.ret cumprod over 60 months", "SEP.closeadj_t / SEP.closeadj_t-60 - 1",
         "month-end ratio, total return; no delisting return; 7-day tolerance"),
        ("winsor2(tempRet60, trim, 1/99) pooled over the whole panel", "harness.crosssection.cs_trim per month",
         "OSAP's pooled trim uses future months (look-ahead); trimmed per month over market-scope names with a valid Ret60"),
        ("all CRSP-Compustat regression sample", "market-scope accessors, ols_residual, min 30 rows",
         "fit over every listed common stock alive at each lag; only universe IDs scored"),
        ("currency", "SF1.fxusd == 1 gate at both ends",
         "flow is in reporting currency, price in USD; non-USD filers set missing"),
        ("Filter abs(prc)>5 ", "not reproduced", "harness universe is price >= $1"),
    ),
)
