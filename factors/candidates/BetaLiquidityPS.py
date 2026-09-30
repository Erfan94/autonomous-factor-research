"""
BetaLiquidityPS — Pastor-Stambaugh liquidity beta: the loading of a stock's
monthly return on the aggregate liquidity innovation, controlling for the
market, HML and SMB, over a rolling five-year window. A stock whose return
co-moves with market liquidity shocks may earn a liquidity-risk premium.

OSAP: BetaLiquidityPS, Pastor and Stambaugh 2003 (Journal of Political
Economy). Predicted sign: + (SignalDoc Sign = 1.0; high liquidity beta on the
long side, so ascending=True).
Spec: osap_source/cache/b4e911e6/BetaLiquidityPS/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  y  = monthly return r_m = closeadj(BME m) / closeadj(BME m-1) - 1 from
       ctx.monthly_closeadj(60) (61 month-ends -> 60 returns; a missing
       month-end nulls the two adjacent returns).
  X  = [ps_innov, mkt, hml, smb] on the same 60 month-ends, from
       ctx.monthly_ps_innov(60) and ctx.monthly_ff3(60)[["mkt","hml","smb"]].
  Per stock: OLS with intercept of y on X over the months where y and all four
  regressors are finite; needs >= 36 such months and a full-rank design, else
  null. Signal = the coefficient on ps_innov (partialled on mkt, hml, smb).
  Solved for all stocks at once as batched weighted normal equations on
  per-stock demeaned, column-standardised regressors (ps_innov is ~1e-5 in
  scale); the coefficient is scaled back to ps_innov units. Only the value at
  the signal month is needed; no cross-month state.
  ps_innov is first non-null 2001-02 (25 of 276 months null) and smb/hml start
  1999-07, so the 36-observation rule first binds at the 2004-01 signal:
  signals 1999-01 .. 2003-12 (about 60 of 276 months) are unscorable for every
  name by the data, not a defect. The window holds 36-59 valid ps months until
  ~2006-01 (noisier early coefficients, as in OSAP's early years).

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? A continuous regression
  coefficient has no do-nothing value. A stock with a constant return over its
  window (stale price) gives a degenerate regression (zero y variance / rank
  loss), which is NaN here, not 0.
  What share of the universe does nothing? Expected ~0%: the price and
  dollar-volume screens remove stale names, and monthly zero returns are
  0.24-0.68% of universe stock-months. Preflight to measure the mode share.
  Tie handling: null. A singular design or y with no variance is nulled, never
  floored; `blend_ranks` renormalises over the legs that remain.

DEVIATIONS FROM OSAP:
  - ps_innov is a harness REBUILD, not Pastor's published series (WRDS
    ff.liq_ps): NYSE/AMEX common stock priced $5-$1000, exchange as of t-1,
    daily per-stock gamma on dollar volume, value-scaled mean change, AR
    residual on an EXPANDING fit (causal, default refit=False); current
    TICKERS category; no delisting or gap returns; daily r < -80% / > +100%
    and no-trade days dropped. Correlation with PS's own series is unknown
    (no reference file held). Scale differs by a positive constant (rank-neutral
    for the coefficient).
  - rf: not held. y is raw return (not excess) and mkt is the RAW cap-weighted
    market (not Mkt-RF); the (1 - b_mkt) x rf_t term falls into the error. rf
    is slow-moving and nearly uncorrelated with ps_innov, so the ps coefficient
    is far less affected than a market beta would be; not assumed, left for a
    preflight diagnostic to bound.
  - smb / hml rebuilt from SEP/SF1 (2x3 June sorts, NYSE breakpoints from
    CURRENT TICKERS exchange, BE = equity + taxliabilities, no preferred,
    no delisting returns), French-style monthly compounding; start 1999-07.
  - y from SEP.closeadj adjacent-month-end ratio: total return on today's
    adjustment basis; no delisting return (OSAP's crsp.ret likewise).
  - Window is the 60 business-month-end grid ending at t, not the stock's last
    60 CRSP rows: a gap reduces n instead of stretching the window.
  - OSAP's abs(prc) > 5 filter is a portfolio-level screen and is not applied;
    the harness universe (price >= $1, cap and dollar-volume screens) governs.
    Scored names are not exchange-restricted (only the liquidity series is
    NYSE/AMEX).
  - history_months=36: a name needs a price 36 months back, matching the
    36-observation minimum (not 60, which OSAP does not require).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef

_WINDOW = 60
_MIN_OBS = 36
_MAX_COND = 1e8          # cond of the correlation-form normal matrix (X cond ~1e4)


def _compute(ctx):
    px = ctx.monthly_closeadj(_WINDOW)
    if px is None or px.shape[1] < _MIN_OBS + 1:
        return pd.Series(dtype=float)
    px = px.astype(float).where(lambda d: d > 0)
    ret = px.iloc[:, 1:].to_numpy() / px.iloc[:, :-1].to_numpy() - 1.0
    months = pd.DatetimeIndex(px.columns[1:])
    y = pd.DataFrame(ret, index=px.index, columns=months)
    y = y.where(np.isfinite(y))

    ps = ctx.monthly_ps_innov(_WINDOW)
    ff = ctx.monthly_ff3(_WINDOW)
    X = pd.DataFrame({"ps": ps.astype(float),
                      "mkt": ff["mkt"].astype(float),
                      "hml": ff["hml"].astype(float),
                      "smb": ff["smb"].astype(float)}).reindex(months)
    xok = X.notna().all(axis=1).to_numpy()
    if xok.sum() < _MIN_OBS:
        return pd.Series(dtype=float)          # unscorable month: ps_innov / ff3 too short

    Xv = X.to_numpy()[xok]                      # T x 4
    Y = y.to_numpy()[:, xok]                    # N x T
    W = np.isfinite(Y).astype(float)            # complete-row mask per stock
    Y = np.where(W > 0, Y, 0.0)
    n = W.sum(axis=1)
    keep = n >= _MIN_OBS
    if not keep.any():
        return pd.Series(dtype=float)
    Y, W, n = Y[keep], W[keep], n[keep]
    ids = y.index[keep]

    # standardise each regressor column (conditioning only), keep scales
    sd = Xv.std(axis=0, ddof=0)
    sd = np.where(sd > 0, sd, np.nan)
    Xs = (Xv - Xv.mean(axis=0)) / sd            # T x 4

    # per-stock weighted means, demeaned normal equations
    xbar = (W @ Xs) / n[:, None]                # N x 4
    ybar = (W * Y).sum(axis=1) / n
    xc = (Xs[None, :, :] - xbar[:, None, :]) * W[:, :, None]   # N x T x 4 (masked)
    yc = (Y - ybar[:, None]) * W                # N x T (masked)
    Sxx = np.einsum("nti,ntj->nij", xc, xc)     # N x 4 x 4
    Sxy = np.einsum("nti,nt->ni", xc, yc)
    Syy = (yc * yc).sum(axis=1)

    d = np.sqrt(np.einsum("nii->ni", Sxx))      # correlation-form normalisation
    good = np.isfinite(d).all(axis=1) & (d > 0).all(axis=1) & (Syy > 0)
    out = pd.Series(np.nan, index=ids, dtype=float)
    if not good.any():
        return out
    idx = np.where(good)[0]
    R = Sxx[idx] / (d[idx][:, :, None] * d[idx][:, None, :])
    ok = np.isfinite(R).all(axis=(1, 2))
    idx, R = idx[ok], R[ok]
    cond = np.linalg.cond(R)
    ok = np.isfinite(cond) & (cond < _MAX_COND)
    idx, R = idx[ok], R[ok]
    if len(idx) == 0:
        return out
    rhs = Sxy[idx] / d[idx]
    beta_n = np.linalg.solve(R, rhs[:, :, None])[:, :, 0] / d[idx]   # on standardised X
    beta_ps = beta_n[:, 0] / sd[0]                                   # back to ps_innov units
    beta_ps = np.where(np.isfinite(beta_ps), beta_ps, np.nan)
    out.iloc[idx] = beta_ps
    return out.dropna()


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="BetaLiquidityPS",
    col="f_betaliqps",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: high liquidity beta on the long side
    weight=1.0,
    inputs=("SEP.closeadj", "SEP.close", "SEP.volume", "SEP.closeunadj",
            "DAILY.marketcap", "ACTIONS.contraname",
            "SF1.equity", "SF1.assets", "SF1.liabilities", "SF1.taxliabilities"),
    osap_acronym="BetaLiquidityPS",
    source="Pastor and Stambaugh 2003 (Journal of Political Economy)",
    lookback_months=60,             # the 60-month rolling regression window
    history_months=36,              # >= 36 observations required in the window
    notes="ps_innov coefficient of a 60m OLS of raw ret on [ps_innov, mkt, hml, smb], >=36 rows; rebuilt ps_innov/ff3, no rf; unscorable before 2004-01",
    field_mappings=(
        ("crsp.ret", "SEP.closeadj adjacent month-end ratio",
         "total return on today's adjustment basis; no delisting return; raw (not excess of rf)"),
        ("ff.liq_ps ps_innov", "MonthContext.monthly_ps_innov(60) (harness rebuild)",
         "NOT Pastor's published series: NYSE/AMEX $5-$1000 daily-gamma rebuild, expanding AR fit, no delisting/gap returns; first non-null 2001-02; no field_map key"),
        ("ff.mktrf", "MonthContext.monthly_ff3(60)['mkt']",
         "RAW cap-weighted market, not Mkt-RF; starts 1998-12 (first month null)"),
        ("ff.smb, ff.hml", "MonthContext.monthly_ff3(60)['smb','hml'] (harness rebuild)",
         "2x3 June sorts, NYSE breakpoints from current TICKERS exchange, BE = equity + taxliabilities (no preferred), no delisting returns; start 1999-07"),
        ("ff.rf", "none",
         "not in the snapshot; y and mkt are raw, rf falls into the error term"),
        ("Filter abs(prc)>5", "harness universe (price >= $1)",
         "not applied in the factor; portfolio-level screen in OSAP's paper replication"),
    ),
)
