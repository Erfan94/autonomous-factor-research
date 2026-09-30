"""
Canonical factor analytics and the standard report.

PURE pandas/numpy/scipy: no I/O, no vendor code, no module-level side effects.
`tests/` exercises the maths on synthetic panels; `harness/run_test.py`
imports the same bytes for every real run and stamps HARNESS_SHA into every
result block, so "the tests pass" and "the run used the tested code" are one
statement whenever the stamp on a result matches the repo.

---------------------------------------------------------------------------
What changed from the predecessor searches, and why (research/LESSONS.md)
---------------------------------------------------------------------------
The first predecessor selected factors on a portfolio construction: five point bars on the
deltas of an equal-weight rank blend's D10-D1 Sharpe, IC, ICIR and MaxDD.
Fifteen of sixteen information-adding rungs failed the Sharpe bar, and the
bars were absolute numbers while the marginal weight of a new leg shrank as
1/(N+1). This harness separates the two questions:

  * Is the signal informative, and is that information NOT already in the
    composite?  -> Stage 1 / Stage 2, construction-invariant, with Newey-West
    t-statistics rather than point deltas.
  * How should the accepted legs be turned into a portfolio? -> Stage 3
    (harness/portfolio.py), run on the accepted composite only, never used
    to accept or reject a candidate.

Three deliberate conventions:

  * IC is the Spearman correlation of the CONTINUOUS score with the forward
    return (an earlier search used the decile bucket, which discards within-decile order).
  * Every t-statistic on a monthly series is Newey-West with
    `statistics.newey_west_lags` lags (config), so autocorrelated IC or LS
    series do not inflate significance.
  * No cost is charged anywhere; turnover is printed so a reader can price it.
  * Ranks are formed WITHIN SECTOR (config `ranking`) before the family blend,
    with a thin-sector fallback to the cross-section rank.
  * The headline long-short is HEDGED to the universe's own cap-weighted
    return with an ex-ante trailing beta (config `market_hedge`); the raw
    series and the beta are reported beside it on every block.
  * Date-free regime diagnostics (Sharpe ex the k best long-short years, a
    bull/bear split on the ex-ante market state) are printed on every block
    and every Stage 2 rung. They are never bars.

A fenced machine-readable block is appended AFTER the report. factor-evaluator
parses ONLY what sits between its fences.
"""

import numpy as np
import pandas as pd
from scipy.stats import spearmanr


RESULT_BEGIN = "--- BEGIN RESULT BLOCK ---"
RESULT_END = "--- END RESULT BLOCK ---"

# Minimum cross-section sizes. NOT free parameters — changing one changes every
# number downstream of it.
MIN_OBS_RANK = 10
MIN_OBS_IC = 10
MIN_OBS_BUCKET_IC = 30
MIN_OBS_BUCKET_LS = 50
MIN_OBS_GROUP_RANK = 10      # a sector-month with fewer scored names ranks on the cross-section

# Share of IC-bearing months that must ALSO yield a long-short before the LS
# statistics may describe the window (a fat tie block collapses pd.qcut).
MIN_LS_MONTH_COVERAGE = 0.90

_EPS = 1e-12

DEFAULT_NW_LAGS = 3
DECAY_HORIZONS = (1, 2, 3, 6, 12)


def _safe_ratio(num, den):
    if den is None or np.isnan(den) or abs(den) < _EPS:
        return float("nan")
    return num / den


# =============================================================================
# Statistics helpers
# =============================================================================

def nw_tstat(x, lags=DEFAULT_NW_LAGS):
    """Newey-West (Bartlett kernel) t-statistic of the mean of a monthly series.
    lags=0 is the plain t-stat. NaN on fewer than two observations or a
    degenerate long-run variance."""
    x = pd.Series(x).dropna().astype(float).values
    n = len(x)
    if n < 2:
        return float("nan")
    e = x - x.mean()
    s = float((e * e).sum())
    for lag in range(1, int(lags) + 1):
        if lag >= n:
            break
        w = 1.0 - lag / (lags + 1.0)
        s += 2.0 * w * float((e[lag:] * e[:-lag]).sum())
    lrv = s / n
    if lrv <= _EPS:
        return float("nan")
    return float(x.mean() / np.sqrt(lrv / n))


def ols_nw(y, X, lags=DEFAULT_NW_LAGS):
    """OLS of y on X (2-D, include the constant yourself) with Newey-West
    standard errors. Returns dict(coef, tstat, r2, n, resid)."""
    y = np.asarray(y, dtype=float)
    X = np.asarray(X, dtype=float)
    n, k = X.shape
    if n <= k:
        return {"coef": np.full(k, np.nan), "tstat": np.full(k, np.nan),
                "r2": float("nan"), "n": n, "resid": np.full(n, np.nan)}
    XtX_inv = np.linalg.pinv(X.T @ X)
    beta = XtX_inv @ X.T @ y
    e = y - X @ beta
    S = (X * e[:, None]).T @ (X * e[:, None])
    for lag in range(1, int(lags) + 1):
        if lag >= n:
            break
        w = 1.0 - lag / (lags + 1.0)
        G = (X[lag:] * e[lag:, None]).T @ (X[:-lag] * e[:-lag, None])
        S += w * (G + G.T)
    V = XtX_inv @ S @ XtX_inv
    se = np.sqrt(np.clip(np.diag(V), 0, None))
    t = np.array([_safe_ratio(b, s) for b, s in zip(beta, se)])
    tss = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - float((e ** 2).sum()) / tss if tss > _EPS else float("nan")
    return {"coef": beta, "tstat": t, "r2": r2, "n": n, "resid": e}


def ic_halves(ic):
    """Mean IC in the first and second half of the sample (by month count)."""
    ic = pd.Series(ic).dropna()
    n = len(ic)
    if n < 4:
        return float("nan"), float("nan"), n // 2, n - n // 2
    h = n // 2
    return float(ic.iloc[:h].mean()), float(ic.iloc[h:].mean()), h, n - h


def net_of_cost(ls_ann_return_pct, ls_ann_vol_pct, turnover_d10_pct, turnover_d1_pct,
                one_way_cost_bps):
    """After-cost annual return and Sharpe of a D10-D1 book.

    Each month a fraction t10 of the long book and t1 of the short book is
    replaced; replacing a name costs one sale and one purchase at the one-way
    cost. Drag per month (as a fraction of book) = 2 * c * (t10 + t1)."""
    c = float(one_way_cost_bps) / 1e4
    t10 = float(turnover_d10_pct) / 100.0 if turnover_d10_pct == turnover_d10_pct else 0.0
    t1 = float(turnover_d1_pct) / 100.0 if turnover_d1_pct == turnover_d1_pct else 0.0
    drag_ann_pct = 12.0 * 2.0 * c * (t10 + t1) * 100.0
    net_ret = float(ls_ann_return_pct) - drag_ann_pct
    net_sharpe = _safe_ratio(net_ret, float(ls_ann_vol_pct))
    return {"ls_cost_drag_ann_pct": drag_ann_pct, "ls_net_ann_return_pct": net_ret,
            "ls_net_sharpe": float(net_sharpe)}


# =============================================================================
# Per-factor ranks and blending
# =============================================================================

def rank_one_factor(df, col, ascending=True, winsorize=True,
                    lo_q=0.01, hi_q=0.99, min_obs=MIN_OBS_RANK,
                    group_col=None, min_group_obs=MIN_OBS_GROUP_RANK):
    """Percentile-rank one factor within one month's cross-section.
    HIGH RANK = ATTRACTIVE = decile 10. All-NaN below `min_obs` non-nulls.

    With `group_col` (the search construction: config `ranking.group_field`,
    the universe frame's sector) the rank is taken WITHIN each group of the
    month, after winsorising on the whole cross-section. A group with fewer
    than `min_group_obs` scored names falls back to the cross-section rank
    for its names, so a thin sector never gets a ten-name decile of its own;
    a missing group label is its own group."""
    if col not in df.columns:
        return pd.Series(np.nan, index=df.index, dtype=float)
    x = pd.to_numeric(df[col], errors="coerce")
    if x.notna().sum() < min_obs:
        return pd.Series(np.nan, index=df.index, dtype=float)
    if winsorize:
        lo, hi = x.quantile([lo_q, hi_q])
        x = x.clip(lo, hi)
    overall = x.rank(pct=True, method="average", ascending=ascending)
    if group_col is None or group_col not in df.columns:
        return overall
    g = df[group_col].astype(object).where(df[group_col].notna(), "__none__")
    n_in_group = x.notna().astype(float).groupby(g).transform("sum")
    within = x.groupby(g).rank(pct=True, method="average", ascending=ascending)
    return within.where(n_in_group >= min_group_obs, overall)


def compute_factor_ranks(df, metas, group_col=None):
    return {m["name"]: rank_one_factor(df, m["col"], ascending=m["ascending"],
                                       winsorize=m["winsorize"], group_col=group_col)
            for m in metas}


def blend_ranks(ranks_df, weights):
    """Weighted-average percentile ranks. Weights renormalise over the legs a
    row actually has; a gap is never filled with a neutral 0.5 (that would
    pull every incomplete name to the middle and manufacture a coverage tilt).
    All-NaN only where a row has no available leg at all."""
    cols = [c for c in weights if c in ranks_df.columns and weights[c] > 0]
    if not cols:
        return pd.Series(np.nan, index=ranks_df.index, dtype=float)
    w = pd.Series({c: float(weights[c]) for c in cols})
    vals = ranks_df[cols].astype(float)
    avail_w = vals.notna().multiply(w, axis=1)
    total_avail_w = avail_w.sum(axis=1).replace(0, np.nan)
    weighted_sum = vals.fillna(0.0).multiply(w, axis=1).sum(axis=1)
    return weighted_sum / total_avail_w


def family_members(metas):
    """family -> [leg names], in meta order. A single meta without a family is
    its own family (a Stage 1 candidate is scored alone). Two or more metas
    must each declare a family: the search construction is defined on
    families, and a leg without one has no weight."""
    groups = {}
    for m in metas:
        fam = m.get("family")
        if fam is None:
            if len(metas) != 1:
                raise ValueError(f"{m['name']} declares no family; a blend of {len(metas)} legs "
                                 "needs one per leg (assign it before Stage 2)")
            fam = m["name"]
        groups.setdefault(fam, []).append(m["name"])
    return groups


def family_weights(metas):
    """The SEARCH construction, as flat per-leg weights: 1/F to each family,
    split equally among the family's legs. A pre-committed construction with
    no free parameter; a new leg dilutes only its own family."""
    groups = family_members(metas)
    n_fam = len(groups)
    return {name: 1.0 / (n_fam * len(names)) for names in groups.values() for name in names}


def blend_family_ranks(ranks_df, metas):
    """Two-level rank blend: the mean of the AVAILABLE member ranks within
    each family, then the mean across the families that have a score. Both
    levels renormalise over what a row actually has, so a name missing one
    member of a four-leg family still gets that family's full weight; the
    flat weights of family_weights() would hand the gap to the other
    families. Never 0.5-filled. NaN only where no leg at all is available."""
    groups = family_members(metas)
    fam_scores = {}
    for fam, names in groups.items():
        cols = [n for n in names if n in ranks_df.columns]
        if cols:
            fam_scores[fam] = ranks_df[cols].astype(float).mean(axis=1, skipna=True)
    if not fam_scores:
        return pd.Series(np.nan, index=ranks_df.index, dtype=float)
    return pd.DataFrame(fam_scores).mean(axis=1, skipna=True)


def cut_deciles(score, n_deciles=10):
    """Decile labels 1..n from a score Series; NA where the score is NA or the
    cross-section is too thin. Cut per month, never pooled."""
    out = pd.Series(pd.NA, index=score.index, dtype="Int64")
    valid = score.notna()
    if valid.sum() < n_deciles:
        return out
    raw = pd.qcut(score[valid], q=n_deciles, labels=False, duplicates="drop")
    out[valid] = (raw + 1).astype("Int64")
    return out


def assign_composite_decile(df, metas, weights=None, n_deciles=10, group_col=None):
    """Add COMPOSITE_SCORE and DECILE for ONE month's cross-section.
    weights=None is the search construction (blend_family_ranks); an explicit
    weight dict is a Stage 3 construction variant's own flat blend.
    group_col: rank each leg within this column's groups (config `ranking`)."""
    df = df.copy()
    ranks_df = pd.DataFrame(compute_factor_ranks(df, metas, group_col=group_col), index=df.index)
    df["COMPOSITE_SCORE"] = (blend_family_ranks(ranks_df, metas) if weights is None
                             else blend_ranks(ranks_df, weights))
    df["DECILE"] = cut_deciles(df["COMPOSITE_SCORE"], n_deciles)
    return df


# =============================================================================
# IC / turnover
# =============================================================================

def _spearman(a, b):
    try:
        rho, _ = spearmanr(a, b)
    except Exception:
        return float("nan")
    return float(rho) if rho == rho else float("nan")


def compute_ic(audit_df, score_col="COMPOSITE_SCORE"):
    """Monthly cross-sectional Spearman IC of the continuous score with the
    realised forward return. Frame indexed by DATE with IC and N."""
    df = audit_df[["DATE", score_col, "monthly_ret"]].dropna().copy()
    df["DATE"] = pd.to_datetime(df["DATE"])
    records = []
    for dt, grp in df.groupby("DATE"):
        if len(grp) < MIN_OBS_IC:
            continue
        rho = _spearman(grp[score_col], grp["monthly_ret"])
        if rho == rho:
            records.append({"DATE": dt, "IC": rho, "N": len(grp)})
    if not records:
        return pd.DataFrame(columns=["DATE", "IC", "N"]).set_index("DATE")
    return pd.DataFrame(records).set_index("DATE").sort_index()


def compute_ic_decay(audit_df, horizons=DECAY_HORIZONS, score_col="COMPOSITE_SCORE"):
    """Mean IC of the month-t score against the return earned h months LATER
    (h=0 is the headline IC). A signal whose h=1 IC is near zero is a
    one-month bet with the turnover to match; one that holds IC to h=6 is
    cheap to trade. Returns {h: mean_ic}."""
    df = audit_df[["ID", "DATE", score_col, "monthly_ret"]].copy()
    df["DATE"] = pd.to_datetime(df["DATE"])
    df = df.dropna(subset=[score_col])
    if df.empty:
        return {h: float("nan") for h in horizons}
    ret_w = df.pivot_table(index="ID", columns="DATE", values="monthly_ret", aggfunc="first")
    sc_w = df.pivot_table(index="ID", columns="DATE", values=score_col, aggfunc="first")
    dates = sorted(ret_w.columns)
    out = {}
    for h in horizons:
        vals = []
        for i in range(len(dates) - h):
            s = sc_w[dates[i]] if dates[i] in sc_w.columns else None
            r = ret_w[dates[i + h]]
            if s is None:
                continue
            al = pd.concat([s, r], axis=1).dropna()
            if len(al) < MIN_OBS_IC:
                continue
            rho = _spearman(al.iloc[:, 0], al.iloc[:, 1])
            if rho == rho:
                vals.append(rho)
        out[h] = float(np.mean(vals)) if vals else float("nan")
    return out


def compute_turnover(audit_df):
    """Average month-over-month name turnover in the top and bottom deciles (%)."""
    df = audit_df[["ID", "DATE", "DECILE"]].dropna(subset=["DECILE"]).copy()
    df["DATE"] = pd.to_datetime(df["DATE"])
    dates = sorted(df["DATE"].unique())
    d10_rec, d1_rec = [], []
    top = int(df["DECILE"].max()) if len(df) else 10
    prev10 = prev1 = None
    for dt in dates:
        cur = df[df["DATE"] == dt]
        c10 = set(cur.loc[cur["DECILE"] == top, "ID"])
        c1 = set(cur.loc[cur["DECILE"] == 1, "ID"])
        if prev10 is not None:
            if prev10:
                d10_rec.append(len(prev10 - c10) / len(prev10))
            if prev1:
                d1_rec.append(len(prev1 - c1) / len(prev1))
        prev10, prev1 = c10, c1
    return {"d10": float(np.mean(d10_rec)) * 100 if d10_rec else float("nan"),
            "d1": float(np.mean(d1_rec)) * 100 if d1_rec else float("nan")}


# =============================================================================
# Marginal-information tests (Stage 2) — construction-invariant
# =============================================================================

def normal_scores(rank_pct):
    """Van der Waerden scores: percentile rank -> standard normal quantile.
    Ranks are uniform, so a linear projection of one rank on another is
    S-shaped in the tails and leaves a monotone residual that is not
    information; on normal scores the projection of one signal on another is
    linear where the signals are, and the residual is what it claims to be."""
    from scipy.stats import norm
    r = pd.Series(rank_pct).astype(float)
    n = int(r.notna().sum())
    if n == 0:
        return r
    return pd.Series(norm.ppf((r * n) / (n + 1.0)), index=r.index)


def standalone_ic_series(audit_df, cand_meta, group_col=None):
    """Per month: Spearman IC of the candidate's oriented rank with the forward
    return, on the SAME frame the residual test uses. The denominator of
    `resid_ic_share` (HD-001): residual IC over the candidate's own IC, so the
    share reads as the fraction of the candidate's information the base legs
    do not already carry."""
    if cand_meta["col"] not in audit_df.columns:
        return pd.DataFrame(columns=["DATE", "IC", "N"]).set_index("DATE")
    extra = [group_col] if group_col and group_col in audit_df.columns else []
    df = audit_df[["DATE", "monthly_ret", cand_meta["col"]] + extra].copy()
    df["DATE"] = pd.to_datetime(df["DATE"])
    recs = []
    for dt, g in df.groupby("DATE"):
        r = rank_one_factor(g, cand_meta["col"], ascending=cand_meta["ascending"],
                            winsorize=cand_meta["winsorize"], group_col=group_col)
        ok = r.notna() & g["monthly_ret"].notna()
        if ok.sum() < MIN_OBS_IC:
            continue
        rho = _spearman(r[ok].values, g.loc[ok, "monthly_ret"].values)
        if rho == rho:
            recs.append({"DATE": dt, "IC": rho, "N": int(ok.sum())})
    if not recs:
        return pd.DataFrame(columns=["DATE", "IC", "N"]).set_index("DATE")
    return pd.DataFrame(recs).set_index("DATE").sort_index()


def residual_ic_series(audit_df, base_metas, cand_meta, group_col=None):
    """Per month: the candidate's normal-scored rank regressed on the base
    legs' normal-scored ranks (missing leg -> 0, the cross-sectional mean);
    the residual's Spearman IC with the forward return. This is the
    information the candidate carries that NO linear combination of the
    existing legs carries, independent of how the legs are weighted."""
    cols = [cand_meta["col"]] + [m["col"] for m in base_metas]
    extra = [group_col] if group_col and group_col in audit_df.columns else []
    df = audit_df[["DATE", "monthly_ret"] + [c for c in cols if c in audit_df.columns] + extra].copy()
    df["DATE"] = pd.to_datetime(df["DATE"])
    recs = []
    for dt, g in df.groupby("DATE"):
        y = normal_scores(rank_one_factor(g, cand_meta["col"], ascending=cand_meta["ascending"],
                                          winsorize=cand_meta["winsorize"], group_col=group_col))
        ok = y.notna() & g["monthly_ret"].notna()
        if ok.sum() < MIN_OBS_IC:
            continue
        Xs = []
        for m in base_metas:
            r = normal_scores(rank_one_factor(g, m["col"], ascending=m["ascending"], winsorize=m["winsorize"],
                                              group_col=group_col))
            Xs.append(r.fillna(0.0))
        X = np.column_stack([np.ones(int(ok.sum()))] + [x[ok].values for x in Xs]) \
            if Xs else np.ones((int(ok.sum()), 1))
        yv = y[ok].values
        beta = np.linalg.pinv(X.T @ X) @ X.T @ yv
        resid = yv - X @ beta
        rho = _spearman(resid, g.loc[ok, "monthly_ret"].values)
        if rho == rho:
            recs.append({"DATE": dt, "IC": rho, "N": int(ok.sum())})
    if not recs:
        return pd.DataFrame(columns=["DATE", "IC", "N"]).set_index("DATE")
    return pd.DataFrame(recs).set_index("DATE").sort_index()


def spanning_test(cand_ls, base_ls, lags=DEFAULT_NW_LAGS):
    """Candidate solo LS regressed on the base composite LS. The intercept is
    the return the candidate earns that the base cannot explain; its NW t is
    a DIAGNOSTIC on every rung, not a bar. R2 is the redundancy diagnostic."""
    al = pd.concat([pd.Series(cand_ls).rename("c"), pd.Series(base_ls).rename("b")], axis=1).dropna()
    n = len(al)
    if n < 12:
        return {"spanning_alpha_monthly": float("nan"), "spanning_alpha_ann_pct": float("nan"),
                "spanning_alpha_tstat_nw": float("nan"), "spanning_beta": float("nan"),
                "spanning_r2": float("nan"), "corr_to_composite": float("nan"), "spanning_n": n}
    X = np.column_stack([np.ones(n), al["b"].values])
    r = ols_nw(al["c"].values, X, lags)
    return {"spanning_alpha_monthly": float(r["coef"][0]),
            "spanning_alpha_ann_pct": float(r["coef"][0] * 12 * 100),
            "spanning_alpha_tstat_nw": float(r["tstat"][0]),
            "spanning_beta": float(r["coef"][1]), "spanning_r2": float(r["r2"]),
            "corr_to_composite": float(al["c"].corr(al["b"])), "spanning_n": n}


def paired_delta(base_series, cand_series, lags=DEFAULT_NW_LAGS):
    """Mean and NW t of (candidate-arm - base-arm) over the months both cover."""
    al = pd.concat([pd.Series(base_series).rename("b"), pd.Series(cand_series).rename("c")],
                   axis=1).dropna()
    if len(al) < 2:
        return float("nan"), float("nan"), len(al)
    d = al["c"] - al["b"]
    return float(d.mean()), float(nw_tstat(d, lags)), len(al)


# =============================================================================
# Config readers shared by the runner and Stage 3 (pure; a missing section
# means "off", so a synthetic test config behaves like the raw predecessor)
# =============================================================================

def rank_group_col(cfg):
    """config ranking.group_field when ranking.within_group is on, else None."""
    r = (cfg or {}).get("ranking") or {}
    return r.get("group_field") if r.get("within_group") else None


def hedge_params(cfg):
    """{beta_window_months, beta_min_months} when market_hedge.enabled, else None."""
    h = (cfg or {}).get("market_hedge") or {}
    if not h.get("enabled"):
        return None
    return {"beta_window_months": int(h["beta_window_months"]), "beta_min_months": int(h["beta_min_months"])}


def regime_params(cfg):
    d = (cfg or {}).get("diagnostics") or {}
    return {"ex_regime_top_years": int(d.get("ex_regime_top_years", 3)),
            "market_state_lookback_months": int(d.get("market_state_lookback_months", 12))}


# =============================================================================
# Market hedge (ex-ante trailing beta) and date-free regime diagnostics
# =============================================================================

def universe_market_return(audit_df, weight_col="mkt_cap_usd"):
    """Per DATE, the cap-weighted mean forward return of the names in the audit
    frame: the market proxy the hedge and the diagnostics read. It is the
    harness universe's own return over the holding month, not an index, so a
    result never depends on a series the snapshot does not hold."""
    if audit_df is None or len(audit_df) == 0 or "monthly_ret" not in audit_df.columns:
        return pd.Series(dtype=float)
    cols = ["DATE", "monthly_ret"] + ([weight_col] if weight_col in audit_df.columns else [])
    d = audit_df[cols].dropna(subset=["monthly_ret"]).copy()
    if d.empty:
        return pd.Series(dtype=float)
    d["DATE"] = pd.to_datetime(d["DATE"])
    if weight_col in d.columns:
        w = pd.to_numeric(d[weight_col], errors="coerce").clip(lower=0.0).fillna(0.0)
    else:
        w = pd.Series(1.0, index=d.index)
    num = (d["monthly_ret"].astype(float) * w).groupby(d["DATE"]).sum()
    den = w.groupby(d["DATE"]).sum().replace(0.0, np.nan)
    return (num / den).sort_index()


def trailing_beta(ls, mkt, window=36, min_months=12):
    """beta_t of the long-short on the market from months t-window .. t-1 ONLY
    (ex ante). 0.0 (no hedge) where fewer than `min_months` prior months exist,
    so the first year of a series runs unhedged rather than on a two-month
    estimate."""
    y = pd.Series(ls).astype(float).sort_index()
    al = pd.concat([y.rename("y"), pd.Series(mkt).astype(float).rename("x")], axis=1).sort_index()
    ok = al["y"].notna() & al["x"].notna()
    yy, xx = al["y"].where(ok), al["x"].where(ok)
    cov = yy.rolling(int(window), min_periods=int(min_months)).cov(xx)
    var = xx.rolling(int(window), min_periods=int(min_months)).var()
    beta = (cov / var.where(var > _EPS)).shift(1)
    return beta.reindex(y.index).fillna(0.0)


def hedge_long_short(ls, mkt, window=36, min_months=12):
    """(hedged, beta): ls_t - beta_t * mkt_t with the ex-ante trailing beta. A
    month with no market return is left unhedged."""
    y = pd.Series(ls).astype(float).sort_index()
    beta = trailing_beta(y, mkt, window, min_months)
    m = pd.Series(mkt).astype(float).reindex(y.index).fillna(0.0)
    return (y - beta * m), beta


def fullwindow_beta(ls, mkt):
    """In-sample OLS slope of the raw long-short on the market over the months
    both cover. A diagnostic of what the book WAS, printed beside the ex-ante
    beta that the hedge actually used."""
    al = pd.concat([pd.Series(ls).astype(float).rename("y"),
                    pd.Series(mkt).astype(float).rename("x")], axis=1).dropna()
    if len(al) < 3 or al["x"].var() <= _EPS:
        return float("nan")
    return float(al["y"].cov(al["x"]) / al["x"].var())


def market_state(mkt, lookback=12):
    """'bear' where the market's compounded return over the `lookback` months
    ending at t-1 is negative, else 'bull'; NaN until the lookback exists."""
    m = pd.Series(mkt).astype(float).sort_index()
    trailing = ((1.0 + m).rolling(int(lookback), min_periods=int(lookback))
                .apply(np.prod, raw=True).shift(1) - 1.0)
    state = pd.Series(np.where(trailing < 0, "bear", "bull"), index=m.index, dtype=object)
    return state.where(trailing.notna())


def regime_diagnostics(ls, mkt=None, top_years=3, lookback=12):
    """Date-free concentration diagnostics of a long-short series. Never a bar.
      ls_sharpe_ex_top_years   Sharpe with the `top_years` best calendar years removed
      ls_top_years             those years, in calendar order
      ls_top_years_share_pct   the share of the summed monthly LS return they carry
      ls_sharpe_bear / _bull   Sharpe in months whose ex-ante market state is bear / bull
    The rule names no date, so a version measured on another window is read
    the same way."""
    out = {"ls_sharpe_ex_top_years": float("nan"), "ls_top_years": "", "ls_top_years_share_pct": float("nan"),
           "ls_sharpe_bear": float("nan"), "ls_sharpe_bull": float("nan"), "n_bear_months": 0, "n_bull_months": 0}
    s = pd.Series(ls).dropna().astype(float).sort_index()
    if len(s) < 24 or not isinstance(s.index, pd.DatetimeIndex):
        return out
    ann = (1.0 + s).groupby(s.index.year).prod() - 1.0
    top = [int(y) for y in ann.sort_values(ascending=False).index[:int(top_years)]]
    rest = s[~s.index.year.isin(top)]
    if len(rest) >= 12:
        out["ls_sharpe_ex_top_years"] = ls_stats_of(rest)[0]
    out["ls_top_years"] = ",".join(str(y) for y in sorted(top))
    tot = float(s.sum())
    out["ls_top_years_share_pct"] = (float(100.0 * s[s.index.year.isin(top)].sum() / tot)
                                     if abs(tot) > _EPS else float("nan"))
    if mkt is not None and len(pd.Series(mkt).dropna()):
        st = market_state(mkt, lookback).reindex(s.index)
        for lab in ("bear", "bull"):
            sub = s[st == lab]
            out[f"n_{lab}_months"] = int(len(sub))
            if len(sub) >= 12:
                out[f"ls_sharpe_{lab}"] = ls_stats_of(sub)[0]
    return out


def _cut_stats(ls_h, ls_r, ic, beta, oos_start, nw_lags=DEFAULT_NW_LAGS):
    """Every LS/IC statistic on the two cuts of a series at `oos_start`:
    before it (cut_inwindow_*) and from it (cut_holdout_*). The hedge beta is
    whatever the continuous series used, so the holdout's first months are
    hedged on the in-window history rather than on nothing."""
    b = pd.Timestamp(oos_start)
    keys = ("ic_mean", "ic_tstat_nw", "ls_sharpe", "ls_ann_return_pct", "ls_ann_vol_pct", "ls_maxdd_pct",
            "ls_tstat_nw", "ls_hit_rate_pct", "ls_raw_sharpe", "ls_raw_ann_return_pct", "ls_beta_mean")
    out = {}
    for pre, before in (("cut_inwindow_", True), ("cut_holdout_", False)):
        def cut(x):
            x = pd.Series(x)
            idx = pd.to_datetime(x.index)
            return x[(idx < b) if before else (idx >= b)]
        h, r, i, be = cut(ls_h).dropna(), cut(ls_r).dropna(), cut(ic).dropna(), cut(beta)
        out[pre + "n_months"] = int(len(h))
        if len(h) < 2 or len(i) < 2:
            for k in keys:
                out[pre + k] = float("nan")
            continue
        sh, dd = ls_stats_of(h)
        rsh, _ = ls_stats_of(r)
        out.update({pre + "ic_mean": float(i.mean()), pre + "ic_tstat_nw": float(nw_tstat(i, nw_lags)),
                    pre + "ls_sharpe": sh, pre + "ls_ann_return_pct": float(h.mean() * 1200),
                    pre + "ls_ann_vol_pct": float(h.std() * np.sqrt(12) * 100), pre + "ls_maxdd_pct": dd,
                    pre + "ls_tstat_nw": float(nw_tstat(h, nw_lags)),
                    pre + "ls_hit_rate_pct": float((h > 0).mean() * 100),
                    pre + "ls_raw_sharpe": rsh, pre + "ls_raw_ann_return_pct": float(r.mean() * 1200),
                    pre + "ls_beta_mean": float(be.reindex(h.index).mean())})
    return out


# =============================================================================
# The standard report
# =============================================================================

def print_summary(title, factor_monthly, count_monthly, ic_df, audit_df,
                  nw_lags=DEFAULT_NW_LAGS, decay=True, hedge=None, regime=None, oos_start=None,
                  market=None):
    """Print the standard report and RETURN the stats it printed. The result
    block is built from this dict, so it cannot drift from the report.

    hedge      {beta_window_months, beta_min_months}: the headline long-short
               is the market-hedged series (ex-ante trailing beta on the
               universe's cap-weighted return, `universe_market_return`); the
               raw series and the beta are reported beside it. None = raw.
    regime     {ex_regime_top_years, market_state_lookback_months}: the
               date-free diagnostics; defaults 3 / 12 when None.
    oos_start  a date: every LS/IC statistic is also reported on the two cuts
               before / from it (cut_inwindow_* / cut_holdout_*), the hedge
               beta estimated continuously across the boundary.
    market     an explicit market series (tests); otherwise derived from
               audit_df."""
    decile_cols = [f"D{i}" for i in range(1, 11) if f"D{i}" in factor_monthly.columns]
    count_cols = [f"N_D{i}" for i in range(1, 11) if f"N_D{i}" in count_monthly.columns]
    avg_returns = factor_monthly[decile_cols].mean()
    avg_counts = count_monthly[count_cols].mean().rename(lambda c: c.replace("N_", ""))
    summary = pd.DataFrame({"Avg Monthly Return (%)": (avg_returns * 100).round(3),
                            "Avg N Companies": avg_counts.round(0)})

    ls_raw = factor_monthly["LS"].astype(float)
    ls_raw.index = pd.to_datetime(ls_raw.index)
    want_mkt = bool(hedge) or regime is not None or oos_start is not None
    mkt = market if market is not None else (universe_market_return(audit_df) if want_mkt
                                             else pd.Series(dtype=float))
    if hedge:
        hw, hm = int(hedge["beta_window_months"]), int(hedge["beta_min_months"])
        ls_hedged, beta = hedge_long_short(ls_raw, mkt, hw, hm)
        ls_series = ls_hedged.dropna()
    else:
        hw = hm = 0
        beta = pd.Series(0.0, index=ls_raw.index)
        ls_series = ls_raw.dropna()
    ls_raw = ls_raw.dropna()
    if len(ls_series) < 2:
        print("WARNING: insufficient LS data.")
        return None
    ls_n_months = int(len(ls_series))
    ls_n_months_missing = int(len(factor_monthly) - ls_n_months)

    ls_mean, ls_std = ls_series.mean(), ls_series.std()
    ls_tstat = _safe_ratio(ls_mean, ls_std / len(ls_series) ** 0.5)
    ls_tstat_nw = nw_tstat(ls_series, nw_lags)
    summary.loc["LS (D10−D1)", "Avg Monthly Return (%)"] = round(ls_mean * 100, 3)
    summary.loc["LS (D10−D1)", "Avg N Companies"] = pd.NA
    summary.loc["LS (D10−D1)", "t-stat"] = round(ls_tstat, 4)

    ic = ic_df["IC"].astype(float)
    mean_ic, std_ic = ic.mean(), ic.std()
    icir = _safe_ratio(mean_ic, std_ic)
    ic_tstat = _safe_ratio(mean_ic, std_ic / len(ic) ** 0.5)
    ic_tstat_nw = nw_tstat(ic, nw_lags)
    pct_pos = (ic > 0).mean() * 100
    h1, h2, n1, n2 = ic_halves(ic)

    ls_ann_ret = ls_mean * 12
    ls_ann_vol = ls_std * np.sqrt(12)
    ls_sharpe = _safe_ratio(ls_ann_ret, ls_ann_vol)
    ls_n_hit = int((ls_series > 0).sum())
    ls_hit_rate = (ls_series > 0).mean() * 100
    cum_ls = (1 + ls_series).cumprod()
    roll_max = cum_ls.cummax().clip(lower=1.0)
    ls_max_dd = ((cum_ls - roll_max) / roll_max).min()
    ls_calmar = _safe_ratio(ls_ann_ret, abs(ls_max_dd))
    turnover = compute_turnover(audit_df)

    raw_sharpe, raw_dd = ls_stats_of(ls_raw)
    raw_ann, raw_vol = float(ls_raw.mean() * 12 * 100), float(ls_raw.std() * np.sqrt(12) * 100)
    beta_on = beta.reindex(ls_series.index).fillna(0.0)
    beta_full = fullwindow_beta(ls_raw, mkt) if len(mkt) else float("nan")
    hedged_months = int((beta_on != 0.0).sum())
    rp = regime or {}
    top_k = int(rp.get("ex_regime_top_years", 3))
    look = int(rp.get("market_state_lookback_months", 12))
    reg = regime_diagnostics(ls_series, mkt if len(mkt) else None, top_k, look)
    cuts = _cut_stats(ls_series, ls_raw, ic, beta_on, oos_start, nw_lags) if oos_start else {}

    mkt_proxy = factor_monthly[decile_cols].mean(axis=1)
    down_mask = mkt_proxy < -0.03
    ls_down_mkt = ls_series[down_mask].mean() * 100 if down_mask.sum() > 0 else float("nan")
    n_down_months = int(down_mask.sum())

    ic_annual = ic.resample("YE").agg(["mean", "std"])
    ic_annual.index = ic_annual.index.year
    ic_annual.columns = ["Mean IC", "Std IC"]
    ic_annual["ICIR"] = (ic_annual["Mean IC"] / ic_annual["Std IC"]).round(4)
    ic_annual["Mean IC"] = ic_annual["Mean IC"].round(4)
    ic_annual["Std IC"] = ic_annual["Std IC"].round(4)
    ls_annual = (ls_series.resample("YE").apply(lambda x: (1 + x).prod() - 1)
                 .rename("LS Ann. Ret (%)") * 100).round(2)
    ls_annual.index = ls_annual.index.year

    dec = compute_ic_decay(audit_df) if decay else {}

    sep = "=" * 70
    print(f"\n{sep}\n  {title}\n  D1 = worst | D10 = best | LS = D10 − D1\n{sep}")
    print(summary[["Avg Monthly Return (%)", "Avg N Companies", "t-stat"]].to_string())
    print(f"\n  --- IC Summary (Spearman, continuous score) ---")
    print(f"  Mean IC   : {mean_ic:.4f}")
    print(f"  Std IC    : {std_ic:.4f}")
    print(f"  ICIR      : {icir:.4f}")
    print(f"  t-stat    : {ic_tstat:.4f}   (Newey-West {nw_lags} lags: {ic_tstat_nw:.4f})")
    print(f"  % Positive: {pct_pos:.1f}%")
    print(f"  Halves    : first {n1}m {h1:+.4f} | second {n2}m {h2:+.4f}")
    print(f"  Months    : {len(ic)}")
    if dec:
        print("  Decay     : " + "  ".join(f"h{h}={v:+.4f}" for h, v in dec.items()))
    print(f"\n  --- LS Portfolio Economics (equal-weight D10−D1, gross) ---")
    print(f"  Ann. Return     : {ls_ann_ret * 100:.2f}%")
    print(f"  Ann. Volatility : {ls_ann_vol * 100:.2f}%")
    print(f"  Sharpe Ratio    : {ls_sharpe:.4f}   (LS t NW: {ls_tstat_nw:.2f})")
    print(f"  Max Drawdown    : {ls_max_dd * 100:.2f}%")
    print(f"  Calmar Ratio    : {ls_calmar:.4f}")
    print(f"  Hit Rate        : {ls_hit_rate:.1f}%  ({ls_n_hit}/{len(ls_series)} months)")
    print(f"  LS Months       : {ls_n_months} of {len(factor_monthly)} "
          f"({ls_n_months_missing} with no D10−D1)")
    if ls_n_months_missing:
        print(f"  ** WARNING: {ls_n_months_missing} month(s) produced fewer than "
              f"{len(decile_cols)} deciles; every LS statistic is computed on "
              f"{ls_n_months} months, NOT {len(factor_monthly)}. A tie block in the raw "
              "factor is the usual cause and it also coarsens the IC.")
    print(f"  Avg D10 Turnover: {turnover['d10']:.1f}% per month")
    print(f"  Avg D1  Turnover: {turnover['d1']:.1f}% per month")
    print(f"  LS in Down Mkt  : {ls_down_mkt:.2f}%  (avg over {n_down_months} months where mkt < -3%)")
    print(f"\n  --- Market hedge (ex-ante trailing beta on the universe's cap-weighted return) ---")
    if hedge:
        print(f"  Hedge           : ON — window {hw}m, min {hm}m; {hedged_months} of {len(ls_series)} months "
              "hedged (beta = 0 before the minimum history). Every LS figure above is the HEDGED series.")
    else:
        print("  Hedge           : OFF — the LS figures above are the raw D10−D1")
    print(f"  Raw LS          : {raw_ann:.2f}%/yr  vol {raw_vol:.2f}%  Sharpe {raw_sharpe:.4f}  MaxDD {raw_dd:.2f}%")
    print(f"  Beta            : trailing mean {beta_on.mean():+.3f}  last {beta_on.iloc[-1]:+.3f}  "
          f"full-window OLS of the raw LS {beta_full:+.3f}")
    print(f"\n  --- Regime diagnostics (date-free; never a bar) ---")
    print(f"  Sharpe ex top-{top_k} LS years : {reg['ls_sharpe_ex_top_years']:.4f}  "
          f"(years {reg['ls_top_years'] or '-'}; they carry {reg['ls_top_years_share_pct']:.0f}% of the summed LS return)")
    print(f"  Sharpe by market state    : bear {reg['ls_sharpe_bear']:.4f} ({reg['n_bear_months']} m)  "
          f"bull {reg['ls_sharpe_bull']:.4f} ({reg['n_bull_months']} m)   "
          f"(state = sign of the trailing {look}m market return, ex ante)")
    if cuts:
        print(f"\n  --- Cuts at {oos_start} (hedge beta estimated continuously across the boundary) ---")
        print(f"  {'':<12}{'months':>7}{'IC':>9}{'IC t NW':>9}{'Sharpe':>8}{'ann%':>8}{'MaxDD':>8}{'raw Sh':>8}{'beta':>7}")
        for pre, lab in (("cut_inwindow_", "in-window"), ("cut_holdout_", "holdout")):
            print(f"  {lab:<12}{cuts[pre + 'n_months']:>7}{cuts[pre + 'ic_mean']:>9.4f}{cuts[pre + 'ic_tstat_nw']:>9.2f}"
                  f"{cuts[pre + 'ls_sharpe']:>8.3f}{cuts[pre + 'ls_ann_return_pct']:>8.2f}{cuts[pre + 'ls_maxdd_pct']:>8.1f}"
                  f"{cuts[pre + 'ls_raw_sharpe']:>8.3f}{cuts[pre + 'ls_beta_mean']:>7.2f}")
    print(f"\n  --- Annual IC ---")
    print(ic_annual.to_string())
    print(f"\n  --- Annual LS Return (%) ---")
    print(ls_annual.to_string())

    stats = {
        "ic_mean": float(mean_ic), "ic_std": float(std_ic), "icir": float(icir),
        "ic_tstat": float(ic_tstat), "ic_tstat_nw": float(ic_tstat_nw),
        "ic_pct_positive": float(pct_pos), "n_months": int(len(ic)),
        "ic_half1_mean": h1, "ic_half2_mean": h2,
        "ic_half_min": float(min(h1, h2)) if (h1 == h1 and h2 == h2) else float("nan"),
        "ls_mean_monthly": float(ls_mean), "ls_tstat": float(ls_tstat),
        "ls_tstat_nw": float(ls_tstat_nw),
        "ls_ann_return_pct": float(ls_ann_ret * 100), "ls_ann_vol_pct": float(ls_ann_vol * 100),
        "ls_sharpe": float(ls_sharpe), "ls_maxdd_pct": float(ls_max_dd * 100),
        "ls_calmar": float(ls_calmar), "ls_hit_rate_pct": float(ls_hit_rate),
        "ls_n_months": ls_n_months, "ls_n_months_missing": ls_n_months_missing,
        "turnover_d10_pct": turnover["d10"], "turnover_d1_pct": turnover["d1"],
        "ls_down_mkt_pct": float(ls_down_mkt) if n_down_months else float("nan"),
        "n_down_months": n_down_months,
        "avg_names_per_decile": float(avg_counts.mean()),
        "decile_avg_ret_pct": ",".join(f"{v * 100:.3f}" for v in avg_returns.values),
        "ls_series": ls_series, "ic_series": ic,
        "ls_raw_ann_return_pct": raw_ann, "ls_raw_ann_vol_pct": raw_vol,
        "ls_raw_sharpe": float(raw_sharpe), "ls_raw_maxdd_pct": float(raw_dd),
        "ls_beta_mean": float(beta_on.mean()), "ls_beta_last": float(beta_on.iloc[-1]),
        "ls_beta_fullwindow": float(beta_full), "ls_hedged_months": hedged_months,
        "hedge_on": str(bool(hedge)),
        "ls_raw_series": ls_raw, "ls_beta_series": beta_on,
        **reg, **cuts,
    }
    for h, v in dec.items():
        stats[f"ic_decay_h{h}"] = float(v)
    return stats


# =============================================================================
# Per-(region x liq_tier) diagnostics — is the edge investable?
# =============================================================================

def compute_bucket_diagnostics(audit_df):
    df = audit_df.dropna(subset=["COMPOSITE_SCORE", "monthly_ret", "region", "liq_tier"]).copy()
    df["DATE"] = pd.to_datetime(df["DATE"])
    rows = []
    groups = list(df.groupby(["region", "liq_tier"], dropna=True))
    groups.append((("ALL", "ALL"), df))
    for (region, tier), grp in groups:
        ic_per_month, ls_per_month, n_per_month = [], [], []
        for dt, sub in grp.groupby("DATE"):
            n = len(sub)
            if n < MIN_OBS_BUCKET_IC:
                continue
            rho = _spearman(sub["COMPOSITE_SCORE"], sub["monthly_ret"])
            if rho == rho:
                ic_per_month.append(rho)
            if n >= MIN_OBS_BUCKET_LS:
                try:
                    d = pd.qcut(sub["COMPOSITE_SCORE"], 10, labels=False, duplicates="drop")
                    if d.notna().any():
                        d10 = sub.loc[d == d.max(), "monthly_ret"].mean()
                        d1 = sub.loc[d == d.min(), "monthly_ret"].mean()
                        if pd.notna(d10) and pd.notna(d1):
                            ls_per_month.append(d10 - d1)
                except Exception:
                    pass
            n_per_month.append(n)
        if not ic_per_month:
            continue
        ic_arr = np.array(ic_per_month)
        mean_ic = float(np.nanmean(ic_arr))
        std_ic = float(np.nanstd(ic_arr, ddof=1)) if len(ic_arr) > 1 else np.nan
        icir = _safe_ratio(mean_ic, std_ic)
        ic_tstat = _safe_ratio(mean_ic, std_ic / np.sqrt(len(ic_arr)))
        pct_pos = float((ic_arr > 0).mean() * 100)
        if ls_per_month:
            ls_arr = np.array(ls_per_month)
            ls_mean_m = float(np.nanmean(ls_arr))
            ls_std_m = float(np.nanstd(ls_arr, ddof=1)) if len(ls_arr) > 1 else np.nan
            ls_ann_ret = ls_mean_m * 12 * 100
            ls_ann_vol = ls_std_m * np.sqrt(12) * 100 if ls_std_m else np.nan
            ls_sharpe = _safe_ratio(ls_ann_ret, ls_ann_vol)
            cum_ls = (1 + pd.Series(ls_arr)).cumprod()
            roll_max = cum_ls.cummax().clip(lower=1.0)
            ls_max_dd = float(((cum_ls - roll_max) / roll_max).min() * 100)
            hit_rate = float((ls_arr > 0).mean() * 100)
        else:
            ls_ann_ret = ls_ann_vol = ls_sharpe = ls_max_dd = hit_rate = np.nan
        rows.append({
            "region": region, "tier": tier, "months": len(ic_arr), "ls_months": len(ls_per_month),
            "avg_N": int(np.mean(n_per_month)) if n_per_month else 0,
            "mean_IC": round(mean_ic, 4),
            "ICIR": round(icir, 4) if not np.isnan(icir) else np.nan,
            "IC_tstat": round(ic_tstat, 2) if not np.isnan(ic_tstat) else np.nan,
            "%_pos": round(pct_pos, 1),
            "LS_ann_%": round(ls_ann_ret, 2) if not np.isnan(ls_ann_ret) else np.nan,
            "LS_vol_%": round(ls_ann_vol, 2) if not np.isnan(ls_ann_vol) else np.nan,
            "LS_Sharpe": round(ls_sharpe, 3) if not np.isnan(ls_sharpe) else np.nan,
            "LS_MaxDD_%": round(ls_max_dd, 2) if not np.isnan(ls_max_dd) else np.nan,
            "LS_hit_%": round(hit_rate, 1) if not np.isnan(hit_rate) else np.nan,
        })
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    region_order = region_sort_order(out["region"])
    tier_order = ["MEGA", "MID", "SMALL", "ALL"]
    out["region"] = pd.Categorical(out["region"], region_order, ordered=True)
    out["tier"] = pd.Categorical(out["tier"], tier_order, ordered=True)
    return out.sort_values(["region", "tier"]).reset_index(drop=True)


_LEGACY_REGION_ORDER = ["NA", "EUR_DM", "JP", "APAC_DM", "EM"]


def region_sort_order(regions):
    seen = [r for r in pd.unique(pd.Series(regions).astype(str)) if r != "ALL"]
    legacy = [r for r in _LEGACY_REGION_ORDER if r in seen]
    rest = sorted(r for r in seen if r not in _LEGACY_REGION_ORDER)
    return legacy + rest + ["ALL"]


def print_bucket_diagnostics(bucket_df):
    if bucket_df.empty:
        print("  (insufficient data in any bucket)")
        return
    print("\n  IC + LS economics by (region × tier)")
    print("  -- LS uses bucket-internal deciles (D10−D1 within bucket), RAW (unhedged) --\n")
    print(bucket_df.to_string(index=False))
    for kpi in ["ICIR", "LS_Sharpe", "LS_ann_%", "avg_N"]:
        try:
            pv = bucket_df.pivot(index="region", columns="tier", values=kpi)
            pv = pv.reindex(index=region_sort_order(bucket_df["region"]))
            pv = pv.reindex(columns=["MEGA", "MID", "SMALL", "ALL"])
            print(f"\n  {kpi} pivot:")
            print(pv.round(3).to_string())
        except Exception:
            pass


def tier_scalars(bucket_df):
    """The capacity numbers, flattened for the block: IC and Sharpe per tier,
    and the liquid-tier (MEGA+MID) share of the ALL Sharpe."""
    out = {}
    if bucket_df is None or bucket_df.empty:
        return out
    for _, r in bucket_df.iterrows():
        t = str(r["tier"])
        if str(r["region"]) == "ALL" and t == "ALL":
            continue
        out[f"tier_{t}_ic_mean"] = float(r["mean_IC"])
        out[f"tier_{t}_ls_sharpe"] = float(r["LS_Sharpe"]) if r["LS_Sharpe"] == r["LS_Sharpe"] else float("nan")
        out[f"tier_{t}_avg_n"] = int(r["avg_N"])
    return out


# =============================================================================
# Survivorship
# =============================================================================

def survivorship_check(audit_df):
    """Share of early-year names absent in the final year. A universe built
    from today's membership shows ~0% here; a point-in-time one shows a lot."""
    df = audit_df.dropna(subset=["region"]).copy()
    df["YEAR"] = pd.to_datetime(df["DATE"]).dt.year
    sample_years = [y for y in (1999, 2003, 2008, 2015, 2020, 2025) if y in df["YEAR"].values]
    if not sample_years:
        print("  (no overlap with sample years)")
        return float("nan")
    last_year = df["YEAR"].max()
    ids_last = set(df.loc[df["YEAR"] == last_year, "ID"].unique())
    print(f"\n  Names appearing in year-Y but ABSENT in {last_year}")
    print(f"  (= delisted/merged/acquired — confirms NO survivorship bias)\n")
    print(f"  {'Year':>6}  {'Total IDs':>10}  {'Gone by ' + str(last_year):>16}  {'%':>6}")
    print(f"  {'-'*6}  {'-'*10}  {'-'*16}  {'-'*6}")
    max_pct = 0.0
    for y in sample_years:
        if y == last_year:
            continue
        ids_y = set(df.loc[df["YEAR"] == y, "ID"].unique())
        gone = ids_y - ids_last
        pct = len(gone) / len(ids_y) * 100 if ids_y else 0
        max_pct = max(max_pct, pct)
        print(f"  {y:>6}  {len(ids_y):>10,d}  {len(gone):>16,d}  {pct:>5.1f}%")
    print(f"\n  >5% gone confirms delisted names ARE retained at historical dates.")
    print(f"  (a universe accidentally built from TODAY's tickers would show ~0%)")
    return max_pct


def render_progress(done, total, reb_dt, start_time, stage="Backtest"):
    import time
    elapsed = time.time() - start_time
    avg_sec = elapsed / max(done, 1)
    remaining = avg_sec * (total - done)
    pct = done / total
    filled = int(30 * pct)
    bar = "█" * filled + "░" * (30 - filled)
    eta_str = (f"{int(remaining // 60)}m {int(remaining % 60)}s left" if done < total else "done")
    return (f"[{bar}] {done}/{total}  {pd.to_datetime(reb_dt).strftime('%b %Y')}  "
            f"({pct * 100:.0f}%)  {stage} — {eta_str}    ")


# =============================================================================
# Result block
# =============================================================================

def _fmt(v):
    if v is None:
        return "NA"
    if isinstance(v, float):
        if np.isnan(v):
            return "NA"
        return f"{v:.6f}"
    return str(v)


SERIES_KEYS = {"ls_series", "ic_series", "resid_ic_series", "ls_raw_series", "ls_beta_series"}


def emit_result_block(fields):
    """Render the fenced `key: value` block. One flat namespace, greppable."""
    lines = [RESULT_BEGIN]
    for k, v in fields.items():
        if k in SERIES_KEYS:
            continue
        lines.append(f"{k}: {_fmt(v)}")
    lines.append(RESULT_END)
    return "\n".join(lines)


STRING_KEYS = {
    "stage", "factor", "harness_sha", "config_sha", "composite_sha", "universe_sha",
    "data_sha", "snapshot_id", "eval_start", "eval_end", "include_holdout",
    "batch_members", "ratchet_base_legs", "ratchet_accepted_before", "ratchet_decision",
    "arm_months_aligned", "dimension_overrides", "history_gates", "leg_coverage_worst_leg",
    "leg_coverage_worst_sector", "decile_avg_ret_pct", "variant", "composite_legs",
    "composite_version", "construction_weights", "ls_top_years", "hedge_on", "holdout_only",
    # construction layer (Phase E): a 12-hex LAYER_SHA of digits would parse as a float
    "layer_sha", "row", "row_note", "constraint", "half_spread_mode", "holdout_only",
    "layer_book_start", "sector_group_labels", "borrow_mode", "paths_sha",
}


def parse_result_block(text):
    if text.count(RESULT_BEGIN) != 1 or text.count(RESULT_END) != 1:
        raise ValueError(
            f"Expected exactly one {RESULT_BEGIN} / {RESULT_END} pair; found "
            f"{text.count(RESULT_BEGIN)} / {text.count(RESULT_END)}. Truncated file, or a "
            "multi-block file — use parse_result_blocks().")
    body = text.split(RESULT_BEGIN, 1)[1].split(RESULT_END, 1)[0]
    out = {}
    for raw in body.splitlines():
        line = raw.strip()
        if not line or ":" not in line:
            continue
        k, v = line.split(":", 1)
        k, v = k.strip(), v.strip()
        if v == "NA" or v == "":
            out[k] = None
            continue
        if k in STRING_KEYS:
            out[k] = v
            continue
        try:
            out[k] = float(v)
        except ValueError:
            out[k] = v
    if not out:
        raise ValueError("Result block is empty.")
    return out


def parse_result_blocks(text):
    """Every block in a result file, in order. Refuses a truncated file, a
    duplicated factor, and a batch whose block count disagrees with batch_size."""
    n_begin, n_end = text.count(RESULT_BEGIN), text.count(RESULT_END)
    if n_begin == 0 or n_begin != n_end:
        raise ValueError(f"Found {n_begin} {RESULT_BEGIN} and {n_end} {RESULT_END}. "
                         "The result file is truncated or malformed — do not parse it.")
    blocks, rest = [], text
    for _ in range(n_begin):
        _, rest = rest.split(RESULT_BEGIN, 1)
        body, rest = rest.split(RESULT_END, 1)
        blocks.append(parse_result_block(RESULT_BEGIN + body + RESULT_END))
    names = [(b.get("factor"), b.get("variant")) for b in blocks]
    if len(set(names)) != len(names):
        raise ValueError(f"Two result blocks claim the same factor/variant: {names}.")
    sizes = {b.get("batch_size") for b in blocks if b.get("batch_size") is not None}
    if len(sizes) > 1:
        raise ValueError(f"Result blocks disagree on batch_size: {sizes}.")
    if sizes:
        declared = int(next(iter(sizes)))
        if declared != len(blocks):
            raise ValueError(f"The run declared a batch of {declared} but the file holds "
                             f"{len(blocks)} result blocks. Members are missing.")
    return blocks


# =============================================================================
# Validation
# =============================================================================

REQUIRED_STAGE1_KEYS = [
    "stage", "factor", "harness_sha", "config_sha", "data_sha",
    "ic_mean", "icir", "ic_tstat", "ic_tstat_nw", "ic_half_min", "ls_sharpe",
    "ls_ann_return_pct", "coverage_pct", "avg_names_per_decile", "n_months",
    "ls_n_months", "eval_start", "eval_end",
    "ls_beta_mean", "ls_raw_sharpe",        # the regime Sharpe is NA on a short sample, so it is printed, not required
]

REQUIRED_STAGE2_KEYS = [
    "stage", "factor", "harness_sha", "config_sha", "data_sha",
    "base_ic_mean", "base_ls_sharpe", "cand_ic_mean", "cand_ls_sharpe",
    "resid_ic_mean", "resid_ic_tstat_nw", "spanning_alpha_tstat_nw", "spanning_r2",
    "paired_delta_ic_mean", "paired_delta_ic_tstat", "paired_delta_ls_mean",
    "paired_delta_ls_tstat", "delta_ls_sharpe",
    "corr_to_composite", "n_months", "eval_start", "eval_end",
    "base_ls_beta_mean", "cand_ls_beta_mean",
]

REQUIRED_STAGE3_KEYS = [
    "stage", "factor", "variant", "harness_sha", "config_sha", "data_sha", "composite_sha",
    "ls_sharpe", "ls_maxdd_pct", "ls_ann_return_pct", "n_months", "ls_beta_mean",
]


REQUIRED_LAYER_KEYS = [
    "stage", "factor", "variant", "row", "aum_usd", "harness_sha", "config_sha", "data_sha",
    "composite_sha", "layer_sha", "n_months", "gross_ann_return_pct", "net_ann_return_pct",
    "net_sharpe", "eval_start", "eval_end",
]


def ls_month_floor(n_months, min_months):
    floor = int(min_months or 0)
    if n_months:
        floor = max(floor, int(MIN_LS_MONTH_COVERAGE * float(n_months)))
    return floor


def validate_results(parsed, expected_harness_sha, expected_config_sha, config,
                     expected_data_sha=None):
    """Sanity-check a parsed block. Returns warning strings; empty = trustworthy."""
    warnings = []
    stage = str(parsed.get("stage"))
    if stage not in ("1", "2", "3", "baseline", "E"):
        warnings.append(f"Unrecognised stage marker: {stage!r}")
    required = {"2": REQUIRED_STAGE2_KEYS, "3": REQUIRED_STAGE3_KEYS,
                "E": REQUIRED_LAYER_KEYS}.get(stage, REQUIRED_STAGE1_KEYS)
    for key in required:
        if key not in parsed or parsed[key] is None:
            warnings.append(f"Missing required field: {key}")

    got_h = parsed.get("harness_sha")
    if got_h and expected_harness_sha and got_h != expected_harness_sha:
        warnings.append(f"HARNESS MISMATCH: result harness {got_h}, repo {expected_harness_sha}. "
                        "Not comparable to rows on the current harness. Do not log it.")
    got_c = parsed.get("config_sha")
    if got_c and expected_config_sha and got_c != expected_config_sha:
        warnings.append(f"CONFIG MISMATCH: result config {got_c}, repo {expected_config_sha}. "
                        "Do not compare it against current thresholds.")
    got_d = parsed.get("data_sha")
    if got_d and expected_data_sha and got_d != expected_data_sha:
        warnings.append(f"DATA MISMATCH: result snapshot {got_d}, repo {expected_data_sha}. "
                        "A refreshed snapshot is a re-baseline. Do not log it.")

    oos_start = str(config.get("dates", {}).get("out_of_sample_start", ""))
    eval_end = parsed.get("eval_end")
    if oos_start and isinstance(eval_end, str) and eval_end >= oos_start:
        warnings.append(f"OUT-OF-SAMPLE BREACH: eval_end ({eval_end}) reaches into the reserved "
                        f"window from {oos_start}. Not usable for a decision.")

    for key in ("ic_mean", "icir", "base_ic_mean", "cand_ic_mean", "resid_ic_mean"):
        v = parsed.get(key)
        if isinstance(v, float) and not -1.0 <= v <= 1.0:
            warnings.append(f"{key}={v} is outside [-1, 1]")
    corr = parsed.get("corr_to_composite")
    if isinstance(corr, float) and not -1.0 <= corr <= 1.0:
        warnings.append(f"corr_to_composite={corr} is outside [-1, 1]")
    n_names = parsed.get("avg_names_per_decile")
    if isinstance(n_names, float) and n_names <= 0:
        warnings.append("avg_names_per_decile is zero or negative — check the pull")

    n_months = parsed.get("n_months")
    min_months = config.get("rebalance", {}).get("min_months", 0)
    if isinstance(n_months, float) and n_months < min_months:
        warnings.append(f"Only {int(n_months)} usable months (minimum {min_months}). INCONCLUSIVE, "
                        "not a rejection — a thin sample is a coverage problem.")
    ls_n_months = parsed.get("ls_n_months")
    if isinstance(ls_n_months, float):
        floor = ls_month_floor(n_months, min_months)
        if ls_n_months < floor:
            warnings.append(f"DECILE COLLAPSE: long-short exists in only {int(ls_n_months)} of "
                            f"{int(n_months) if n_months else '?'} months (floor {floor}). Every LS "
                            "statistic describes a subsample nobody chose; usual cause a tie block. "
                            "INCONCLUSIVE — fix the tie handling and re-run.")
        missing = parsed.get("ls_n_months_missing")
        if isinstance(missing, float) and missing > 0 and ls_n_months >= floor:
            warnings.append(f"PARTIAL DECILE COLLAPSE: {int(missing)} month(s) produced fewer than 10 "
                            "deciles. Read the per-decile Avg N before any bar.")
    cov = parsed.get("coverage_pct")
    if isinstance(cov, float) and cov >= 99.9999 and stage not in ("baseline", "3", "E"):
        warnings.append(f"COVERAGE IS {cov:.6f}% — implausibly complete for a lagged signal. Suspect "
                        "a filled value (0.0) where a null belongs: that manufactures a mass point.")
    if isinstance(cov, float) and cov < 20.0:
        warnings.append(f"Coverage is only {cov:.1f}% of universe-months — the result describes a "
                        "small, non-random subset of the stated universe.")
    for key in ("icir", "base_icir", "cand_icir"):
        v = parsed.get(key)
        if isinstance(v, float) and abs(v) > 5.0:
            warnings.append(f"{key}={v:.3g} is not a plausible monthly ICIR — the IC dispersion "
                            "collapsed; check the run rather than the factor.")
    surv = parsed.get("survivorship_max_gone_pct")
    if isinstance(surv, float) and surv < 5.0:
        warnings.append(f"Survivorship check shows only {surv:.1f}% of early-year names gone by the "
                        "final year. The universe is probably NOT point-in-time.")
    return warnings


# =============================================================================
# Threshold evaluation — the pre-committed bars
# =============================================================================

def stage1_checks(values, thresholds, ls_floor=None):
    """The Stage 1 bars as (name, value, bound, direction) from a flat dict of
    stats. Shared by the runner (which has the stats) and the evaluator (which
    has the parsed block), so the two cannot drift."""
    t = thresholds
    checks = [
        ("ic_mean", values.get("ic_mean"), t["min_ic_mean"], "ge"),
        ("ic_tstat_nw", values.get("ic_tstat_nw"), t["min_ic_tstat_nw"], "ge"),
        ("ic_half_min", values.get("ic_half_min"), t["min_ic_half_mean"], "ge"),
        ("ls_ann_return_pct", values.get("ls_ann_return_pct"),
         t["min_ls_ann_return_pct"], "ge"),
        ("coverage_pct", values.get("coverage_pct"), t["min_coverage_pct"], "ge"),
        ("avg_names_per_decile", values.get("avg_names_per_decile"),
         t["min_avg_names_per_decile"], "ge"),
    ]
    if ls_floor is not None:
        checks.append(("ls_n_months", values.get("ls_n_months"), ls_floor, "ge"))
    return checks


def check_stage1(parsed, thresholds, min_ls_months=None):
    floor = None
    if min_ls_months is not None:
        floor = ls_month_floor(parsed.get("n_months"), min_ls_months)
    return _run_checks(stage1_checks(parsed, thresholds, floor))


def stage2_checks(values, thresholds):
    """Two bars, BOTH must hold:
      resid_ic_tstat_nw       the candidate carries information no linear
                              combination of the existing legs carries
                              (stock level, construction-free). STRICTLY
                              greater than the bound (comparator "gt").
      paired_delta_ls_tstat   guard: after the candidate joins its family,
                              the family blend's gross long-short return
                              must not fall SIGNIFICANTLY (bound negative).
    The paired composite-dIC (with vs without the candidate), the spanning
    alpha, R2, Sharpe and MaxDD deltas are DIAGNOSTICS printed on every
    rung, never bars: a one-leg change to a many-family blend is too small
    for a paired test to resolve on a ~276-month sample, so a dIC bar would
    reject on power, not on information."""
    t = thresholds
    return [
        ("resid_ic_tstat_nw", values.get("resid_ic_tstat_nw"), t["min_resid_ic_tstat_nw"], "gt"),
        ("paired_delta_ls_tstat", values.get("paired_delta_ls_tstat"),
         t["min_paired_delta_ls_tstat"], "ge"),
    ]


def check_stage2(parsed, thresholds):
    return _run_checks(stage2_checks(parsed, thresholds))


def _run_checks(checks):
    details, passed = [], True
    for name, value, bound, direction in checks:
        if value is None or (isinstance(value, float) and np.isnan(value)):
            details.append({"check": name, "value": None, "bound": bound,
                            "direction": direction, "result": "MISSING"})
            passed = False
            continue
        ok = {"ge": value >= bound, "gt": value > bound, "le": value <= bound,
              "lt": value < bound}[direction]
        details.append({"check": name, "value": float(value), "bound": bound,
                        "direction": direction, "result": "PASS" if ok else "FAIL"})
        passed = passed and ok
    return passed, details


# =============================================================================
# Per-leg coverage — which legs a name is ACTUALLY scored on
# =============================================================================

def compute_leg_coverage(audit_df, metas, sector_col="sector"):
    cols = [m["col"] for m in metas if m["col"] in audit_df.columns]
    out = {"overall": pd.Series(dtype=float), "by_sector": pd.DataFrame(),
           "legs_per_name": {}, "worst": (None, float("nan"))}
    if not cols or len(audit_df) == 0:
        return out
    present = audit_df[cols].notna()
    out["overall"] = (100.0 * present.mean()).sort_values()
    out["worst"] = (out["overall"].index[0], float(out["overall"].iloc[0]))
    n_legs = present.sum(axis=1)
    scored = audit_df["COMPOSITE_SCORE"].notna() if "COMPOSITE_SCORE" in audit_df else None
    n_legs_scored = n_legs[scored] if scored is not None else n_legs
    out["legs_per_name"] = {
        "n_legs_total": len(cols),
        "mean_legs": float(n_legs_scored.mean()) if len(n_legs_scored) else float("nan"),
        "pct_full": float(100.0 * (n_legs_scored == len(cols)).mean()) if len(n_legs_scored) else float("nan"),
        "pct_half_or_less": float(100.0 * (n_legs_scored <= len(cols) / 2.0).mean()) if len(n_legs_scored) else float("nan"),
    }
    if sector_col in audit_df.columns:
        by = 100.0 * audit_df.groupby(sector_col)[cols].apply(lambda g: g.notna().mean())
        out["by_sector"] = by.reindex(by.mean(axis=1).sort_values().index)
    return out


def leg_coverage_scalars(cov):
    worst_leg, worst_pct = cov.get("worst", (None, float("nan")))
    lp = cov.get("legs_per_name", {})
    fields = {"leg_coverage_worst_leg": worst_leg, "leg_coverage_worst_pct": worst_pct,
              "leg_coverage_mean_legs": lp.get("mean_legs"),
              "leg_coverage_pct_full": lp.get("pct_full"),
              "leg_coverage_pct_half_or_less": lp.get("pct_half_or_less")}
    by = cov.get("by_sector")
    if by is not None and len(by):
        fields["leg_coverage_worst_sector"] = str(by.mean(axis=1).idxmin())
        fields["leg_coverage_worst_sector_mean_pct"] = float(by.mean(axis=1).min())
    return fields


# =============================================================================
# Arm alignment — the two arms of a rung must be compared on the same months
# =============================================================================

def ls_stats_of(ls):
    """(sharpe, maxdd_pct) by the same formulas print_summary uses."""
    ls = pd.Series(ls).dropna().astype(float)
    if len(ls) < 2:
        return float("nan"), float("nan")
    mean, std = ls.mean(), ls.std()
    sharpe = float(_safe_ratio(mean * 12, std * np.sqrt(12)))
    cum = (1 + ls).cumprod()
    roll = cum.cummax().clip(lower=1.0)
    return sharpe, float(((cum - roll) / roll).min() * 100)


def align_arms(base_stats, cand_stats, lags=DEFAULT_NW_LAGS):
    """Composite-level deltas over the months BOTH arms covered, plus the
    paired tests. A silent month gap between arms once produced a plausible
    wrong delta in an earlier search; the fields say what was compared."""
    out = {}
    b_ic, c_ic = base_stats["ic_series"], cand_stats["ic_series"]
    b_ls, c_ls = base_stats["ls_series"], cand_stats["ls_series"]
    common_ic = b_ic.index.intersection(c_ic.index)
    common_ls = b_ls.index.intersection(c_ls.index)
    only = (set(b_ic.index) ^ set(c_ic.index)) | (set(b_ls.index) ^ set(c_ls.index))
    m, t, n = paired_delta(b_ic.loc[common_ic], c_ic.loc[common_ic], lags)
    out.update(paired_delta_ic_mean=m, paired_delta_ic_tstat=t, arm_n_common_ic=n)
    bs, bdd = ls_stats_of(b_ls.loc[common_ls])
    cs, cdd = ls_stats_of(c_ls.loc[common_ls])
    lm, lt, ln = paired_delta(b_ls.loc[common_ls], c_ls.loc[common_ls], lags)
    out.update(delta_ls_sharpe=cs - bs, maxdd_worsening_pct=abs(cdd) - abs(bdd),
               paired_delta_ls_mean=lm, paired_delta_ls_tstat=lt, arm_n_common_ls=ln,
               delta_icir=float(_safe_ratio(c_ic.loc[common_ic].mean(), c_ic.loc[common_ic].std())
                                - _safe_ratio(b_ic.loc[common_ic].mean(), b_ic.loc[common_ic].std())),
               arm_months_aligned=str(not only))
    if only:
        out["arm_months_unmatched"] = ",".join(pd.Timestamp(x).strftime("%Y-%m-%d") for x in sorted(only))
        print("\n  !! ARM MONTH MISMATCH — the arms did not cover the same months; every "
              "delta is on the intersection.")
    return out
