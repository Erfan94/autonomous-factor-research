"""
ResidualMomentum — momentum in Fama-French three-factor residuals: the
information-ratio-like mean / standard deviation of the eleven most recent
(skip-month) in-sample residuals of rolling 36-month FF3 regressions; stocks
with HIGH residual momentum are predicted to earn HIGHER returns.

OSAP: ResidualMomentum, Blitz, Huij and Martens 2011, Journal of Empirical
Finance (Table 2B, 1M). Predicted sign: + (SignalDoc Sign = +1).
Spec: osap_source/cache/b4e911e6/ResidualMomentum/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  Returns: r_m = SEP.closeadj_m / SEP.closeadj_{m-1} - 1 on the business
    month-end grid. px = ctx.monthly_closeadj(47) has 48 columns (s-47 .. s);
    the LAST column (the signal month s itself) is DROPPED, leaving 47 closes
    s-47 .. s-1 and 46 monthly returns for months s-46 .. s-1.
  Factors: X_m = [1, mkt_m, smb_m, hml_m] from ctx.monthly_ff3 (the harness's
    Sharadar-native Fama-French rebuild), re-indexed to the return months.
  Rolling regression: for each of the 11 window ends e = s-11 .. s-1, OLS of
    r on X over the 36 months e-35 .. e (OSAP: min_periods 36, full window),
    and the residual of the window's LAST observation e (in-sample: the fit
    includes e), as OSAP's l1._residuals. These eleven residuals are the
    residuals of months s-11 .. s-1 (month s itself skipped, as OSAP's
    temp = _residuals lagged one month).
  ResidualMomentum = mean(eleven residuals) / sd(eleven residuals, ddof = 1),
    OSAP's rolling mean / rolling std (min 11 observations). Raw value.
  A name needs all 46 monthly returns finite (full calendar window): OSAP
    counts rows, this counts months, so a name with a missing month is NaN
    here. All 46 factor months must also be finite.
  Price-only: no filing date, no ART/ARQ choice.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? 0/0 -> NaN: a firm with a
  flat price in every window month has residual 0 in every month, mean 0 and
  sd 0; it is set NaN, not a value. Every other name is a continuous ratio
  of two statistics; no exact tie value exists.
  What share of the universe does nothing? ~0%: the spec measured the largest
  modal-value share at 0.124% (mean 0.062%) over the 223 scorable months,
  distinct values = scored names, and 10 qcut bins in every scorable month.
  Preflight decides.
  Tie handling: null. Any non-finite ratio, and any sd <= 1e-12, is set NaN
  and blend_ranks renormalises.

DEVIATIONS FROM OSAP:
  - rf omitted (the snapshot holds no risk-free rate). The stock return and
    mkt are both RAW, so r on mkt replaces (r - rf) on (mkt - rf). Not zero:
    inside a window the two differ by (1 - beta)(rf_t - mean rf), with rf
    varying about 0.1-0.4% a month against an idiosyncratic sd near 10% a
    month. Small, declared.
  - mktrf / smb / hml: ctx.monthly_ff3, the harness rebuild (NYSE-breakpoint
    2x3 sorts on SF1 book equity and DAILY.marketcap; CURRENT TICKERS
    exchange for the breakpoints; BE = equity + taxliabilities with no
    preferred stock; no delisting returns; mkt RAW; monthly SMB / HML from
    compounded portfolio returns), not Ken French's series.
  - ret: SEP closeadj month-end ratio (total return, no delisting return;
    closeadj is on a 3-decimal grid) replaces CRSP monthly ret incl. dlret.
  - full calendar window required (see above).
  - data start TRUNCATION: smb / hml exist only from July 1999 (first complete
    monthly label 1999-07-30), and the earliest window needs 46 monthly
    returns from then, so the FIRST scorable signal is 2003-05-30; every
    signal before it (the 53 leading months 1998-12 .. 2003-04) is NaN for
    every name. A data-start fact of the harness's factor build, not a defect:
    223 of 276 decision months are scorable.
  - sd = 0 (or <= 1e-12) set NaN (0/0 in OSAP).
  - history_months = 47 (a price 47 months back) and lookback_months = 47.
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef

_WIN = 36                   # OSAP: rolling window of 36 observations (min_periods 36)
_NRES = 11                  # OSAP: rolling mean / std over 11 residuals (min 11)
_NRET = _WIN + _NRES - 1    # 46 monthly returns: months s-46 .. s-1
_SD_FLOOR = 1e-12


def _compute(ctx):
    nan = pd.Series(np.nan, index=ctx.ids)

    px = ctx.monthly_closeadj(_NRET + 1)                 # s-47 .. s (48 columns)
    if px is None or px.shape[1] < _NRET + 2:
        return nan
    px = px.astype(float).where(lambda d: d > 0).iloc[:, :-1]    # DROP month s: s-47 .. s-1
    months = pd.DatetimeIndex(px.columns[1:])            # return months s-46 .. s-1
    with np.errstate(divide="ignore", invalid="ignore"):
        Y = px.iloc[:, 1:].to_numpy() / px.iloc[:, :-1].to_numpy() - 1.0      # N x 46
    Y = np.where(np.isfinite(Y), Y, np.nan)

    ff = ctx.monthly_ff3(_NRET + 2)                      # s-47 .. s business month-ends
    if ff is None or len(ff) == 0:
        return nan
    ff = ff.astype(float)
    ff.index = pd.DatetimeIndex(ff.index)
    F = ff.reindex(months)[["mkt", "smb", "hml"]].to_numpy()
    if not np.isfinite(F).all():
        return nan                                        # factor data start: every name NaN
    X = np.column_stack([np.ones(len(months)), F])       # 46 x 4

    full = np.isfinite(Y).all(axis=1)                    # full calendar window
    if not full.any():
        return nan
    Yf = Y[full]                                          # n x 46

    resid = np.empty((Yf.shape[0], _NRES))
    for k in range(_NRES):
        lo, hi = k, k + _WIN                              # window ends at return index hi-1 = 35+k
        Xw = X[lo:hi]
        Yw = Yf[:, lo:hi].T                               # 36 x n
        beta, *_ = np.linalg.lstsq(Xw, Yw, rcond=None)
        resid[:, k] = Yw[-1] - Xw[-1] @ beta[:, :]        # in-sample residual of the window's last month

    mean = resid.mean(axis=1)
    sd = resid.std(axis=1, ddof=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        val = mean / sd
    val = np.where(np.isfinite(val) & (sd > _SD_FLOOR), val, np.nan)

    out = pd.Series(np.nan, index=px.index, dtype=float)
    out[full] = val
    return out.reindex(ctx.ids)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="ResidualMomentum",
    col="f_resmom",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: HIGH residual momentum is attractive
    weight=1.0,
    inputs=("SEP.closeadj", "DAILY.marketcap", "SF1.equity", "SF1.assets",
            "SF1.liabilities", "SF1.taxliabilities"),
    osap_acronym="ResidualMomentum",
    source="Blitz, Huij and Martens 2011 (Journal of Empirical Finance)",
    lookback_months=47,             # 47 month-end closes s-47 .. s-1 (month s dropped)
    history_months=47,              # return-window signal: a price 47 months back
    notes="mean/sd(ddof=1) of the 11 in-sample FF3 residuals of rolling 36m regressions, months s-11..s-1 (s skipped); no rf; NaN before 2003-05",
    field_mappings=(
        ("crsp.ret (monthly)", "SEP.closeadj month-end ratio (ctx.monthly_closeadj(47), last column dropped)",
         "total return, no delisting return; 3-decimal closeadj grid; a missing month makes the name NaN"),
        ("ff.mktrf, ff.smb, ff.hml", "MonthContext.monthly_ff3: mkt, smb, hml (harness rebuild)",
         "Sharadar-native 2x3 sort (SF1 equity + taxliabilities, DAILY.marketcap, current-TICKERS exchange), "
         "no delisting returns, mkt RAW; not in the field_map index (harness accessor)"),
        ("ff.rf", "omitted (not in the snapshot)",
         "r on mkt replaces (r - rf) on (mkt - rf); differs by (1-beta)(rf_t - mean rf) in a window, small against ~10% monthly idiosyncratic sd"),
        ("ff.smb / ff.hml start + 46-month window", "first complete-factor month 1999-07; first scorable signal 2003-05-30",
         "signals before 2003-05-30 are NaN for every name (data-start truncation, 53 of 276 months)"),
        ("rolling 36m OLS, residual of last obs; mean/std over 11", "lstsq per window end s-11..s-1, ddof=1 sd",
         "OSAP's in-sample residual, min_periods 36 and min 11 reproduced; calendar (not row) window; sd <= 1e-12 set NaN"),
    ),
)
