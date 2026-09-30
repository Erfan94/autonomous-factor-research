"""Cross-sectional regression and trimming helpers for ONE month (or one
stacked panel) of values.

Pure functions on indexed Series/DataFrames: no MonthContext, no dates, no
universe. A factor computes its raw inputs through MonthContext (usually on
ctx.market_context(), because OSAP fits its cross-sectional regressions on
all of CRSP), calls these, then reindexes the result to ctx.ids. Built for
the Intan* residuals (one month's cross-section) and Frontier (a pooled
60-month panel, predict the current month's rows).
"""
import numpy as np
import pandas as pd


def cs_trim(x, lower=1.0, upper=99.0):
    """`x` with values strictly below its `lower` percentile or strictly above
    its `upper` percentile set to NaN (a TRIM, not a winsor: OSAP's
    winsor2(..., trim) drops the tails). Percentiles are taken over the
    non-null values of THIS call only, so applied per month it never uses
    another month's distribution (OSAP's whole-sample cut-offs would be
    look-ahead). NaN stays NaN; an all-null input comes back unchanged."""
    s = pd.Series(x, dtype="float64")
    v = s.dropna()
    if v.empty:
        return s
    lo, hi = np.percentile(v.to_numpy(), [float(lower), float(upper)])
    return s.where((s >= lo) & (s <= hi))


def ols_residual(y, X, fit_mask=None, add_intercept=True, min_obs=30):
    """Residual y - X b of an OLS fit, on y's full index.

    Rows with a null in y or in any column of X are excluded from the fit and
    are NaN in the output. The fit uses only rows where `fit_mask` is True
    (default: every complete row); the residual is returned for EVERY
    complete row, so a pooled fit can score rows outside it (Frontier: fit on
    60 stacked months, keep the current month). Fewer than `min_obs` fitting
    rows, or no more fitting rows than coefficients, gives all NaN.
    Categorical regressors are the caller's job (pd.get_dummies with
    drop_first=True). np.linalg.lstsq, so a rank-deficient X still returns
    the minimum-norm fit and the residual is well defined.
    """
    ys = pd.Series(y, dtype="float64")
    Xf = pd.DataFrame(X).reindex(ys.index).astype("float64")
    out = pd.Series(np.nan, index=ys.index)
    complete = ys.notna() & Xf.notna().all(axis=1)
    if fit_mask is None:
        fit = complete
    else:
        fm = pd.Series(fit_mask).reindex(ys.index)
        fit = complete & fm.astype("object").where(fm.notna(), False).astype(bool)
    A = Xf.to_numpy()
    if add_intercept:
        A = np.column_stack([np.ones(len(A)), A])
    n_fit = int(fit.sum())
    if n_fit < int(min_obs) or n_fit <= A.shape[1]:
        return out
    fv = fit.to_numpy()
    beta, *_ = np.linalg.lstsq(A[fv], ys.to_numpy()[fv], rcond=None)
    cv = complete.to_numpy()
    out.iloc[np.flatnonzero(cv)] = ys.to_numpy()[cv] - A[cv] @ beta
    return out


def ols_coef(y, X, add_intercept=True, min_obs=30, tol=None):
    """OLS coefficients of y on X (and a constant), Stata `regress`-style.

    Returns a Series indexed ["const"] + list(X.columns) ("const" only with
    add_intercept). Rows with a null in y or in any column of X are dropped
    (listwise). COLLINEARITY, deterministic: columns are taken in order, the
    constant first; a column whose residual on the columns already kept has
    norm <= tol x its own norm is OMITTED and gets coefficient 0.0 — the
    EARLIER of two collinear columns keeps the weight (Stata's rmcoll omits
    the later ones; OSAP's asreg_collinear writes 0 for an omitted one). A
    constant column is collinear with the intercept. Default tol =
    eps x max(n, k), OSAP's drop_collinear rank tolerance on unit-norm
    columns. The kept columns are fit by np.linalg.lstsq.
    Fewer than `min_obs` complete rows, or no more rows than kept
    coefficients, gives all NaN. `.attrs`: n_obs (complete rows), dropped
    (omitted column names, in order).
    """
    ys = pd.Series(y, dtype="float64")
    Xf = pd.DataFrame(X).reindex(ys.index).astype("float64")
    names = (["const"] if add_intercept else []) + list(Xf.columns)
    out = pd.Series(np.nan, index=pd.Index(names, dtype=object), dtype="float64")
    complete = (ys.notna() & Xf.notna().all(axis=1)).to_numpy()
    A = Xf.to_numpy()[complete]
    if add_intercept:
        A = np.column_stack([np.ones(len(A)), A])
    yv = ys.to_numpy()[complete]
    n, k = A.shape
    out.attrs = {"n_obs": int(n), "dropped": []}
    if n < int(min_obs) or n == 0:
        return out
    tol = float(np.finfo(float).eps * max(n, k)) if tol is None else float(tol)
    norms = np.linalg.norm(A, axis=0)
    kept, dropped = [], []
    for j in range(k):
        if norms[j] == 0:
            dropped.append(j)
            continue
        col = A[:, j] / norms[j]
        if kept:
            K = A[:, kept] / norms[kept]
            b, *_ = np.linalg.lstsq(K, col, rcond=None)
            col = col - K @ b
        if np.linalg.norm(col) <= tol:
            dropped.append(j)
        else:
            kept.append(j)
    out.attrs["dropped"] = [names[j] for j in dropped]
    if n <= len(kept) or not kept:
        return out
    beta, *_ = np.linalg.lstsq(A[:, kept], yv, rcond=None)
    vals = np.zeros(k)
    vals[kept] = beta
    out[:] = vals
    return out
