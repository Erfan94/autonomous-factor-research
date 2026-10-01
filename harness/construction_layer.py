"""
Phase E — the institutional construction layer (docs/CONSTRUCTION.md r2, D15).

It takes the FINISHED composite's audit frame (the exact Stage 2 family blend,
scored by run_test.score_arm) and describes how a desk would trade it: a
monthly fundamental factor risk model, a closed-form mean-variance target
that is sector-neutral AND market-beta-neutral (D7 item 1; the constraint set
is config `optimiser.constraints`), sized by a confidence-scaled gross budget,
a pipeline of name caps, a no-trade buffer against the drifted held book,
participation caps and a final re-projection, and a cost model charged ex
post on the realised trades, its half-spread read from a harness-built
Corwin-Schultz series (data_layer.load_or_build_cs_spread, D7 item 2), never
from a composite leg. It judges nothing: no leg is added, dropped or
reweighted by a number this module produces (D8).

Every parameter comes from config/construction_layer.yaml (LAYER_CONFIG_PATH)
and nothing is hard-coded here except the names of the audit columns. The
file's hash is LAYER_SHA, stamped on every layer block beside the four stamps;
it is informational, not a gate stamp. The module refuses a composite whose
COMPOSITE_SHA differs from the config's `composite.composite_sha`.

Timing (harness/data_layer.py): month t's row has SIGNAL_ASOF(t), the signal
close, and monthly_ret(t), earned from that close to RET_END(t) (= DATE).
RET_END(t) == SIGNAL_ASOF(t+1), so a book formed at the signal close of t earns
exactly monthly_ret(t). Point-in-time rule (CONSTRUCTION.md §2): every
estimate used at t (factor returns, factor covariance, specific variance,
trailing volatility, the composite IC) is built from months s with
RET_END(s) <= SIGNAL_ASOF(t). Delisting returns (Shumway convention) are
already inside monthly_ret; ret_kind 'partial_delisted_*' marks them.

Weights are fractions of capital. Capital is reset to the AUM level every
month (P&L swept), so the AUM ladder keeps its meaning; the held book at t is
last month's final positions grown by each name's realised return, divided by
the book's end-of-month capital (1 + net return).

numpy / pandas / scipy only.
"""

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy.stats import norm, rankdata

from harness.analytics import (_EPS, DEFAULT_NW_LAGS, _safe_ratio, compute_factor_ranks, compute_ic,
                               family_members, fullwindow_beta, nw_tstat, rank_group_col,
                               universe_market_return)

ROOT = Path(__file__).resolve().parent.parent
LAYER_CONFIG_PATH = ROOT / "config" / "construction_layer.yaml"

UNCLASSIFIED = "Unclassified"
_MISSING_SECTOR = {"", "nan", "none", "null", "unknown", "<na>"}
TIERS = ("MEGA", "MID", "SMALL")
# The audit column each declared half-spread source reads (CONSTRUCTION.md §2).
# `cs_spread` is the harness-built Corwin-Schultz series
# (data_layer.load_or_build_cs_spread), attached to the audit frame by
# attach_spread; it is no composite leg's column (D7 item 2).
SPREAD_COLUMNS = {"corwin_schultz_half": "cs_spread"}
DELISTED_PREFIX = "partial_delisted"
# optimiser.constraints: the declared constraint sets (§5).
CONSTRAINTS = ("sector_beta_neutral", "sector_neutral", "dollar_neutral")


class LayerRefused(RuntimeError):
    """The layer will not run on this input (wrong composite, bad config)."""


# =============================================================================
# Config and stamps
# =============================================================================

def layer_sha(path=LAYER_CONFIG_PATH):
    """sha256 of config/construction_layer.yaml's bytes, first 12 hex."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:12]


def load_layer_config(path=LAYER_CONFIG_PATH):
    with open(path) as f:
        return yaml.safe_load(f)


def check_composite(lcfg, composite_sha):
    """Refuse any composite other than the one the layer config was frozen on."""
    want = str(((lcfg or {}).get("composite") or {}).get("composite_sha", ""))
    if not want or str(composite_sha) != want:
        raise LayerRefused(f"construction layer refused: COMPOSITE_SHA {composite_sha} != the frozen "
                           f"composite_sha {want or '(none)'} in config/construction_layer.yaml. "
                           "The layer runs on the finished composite only (D15).")


def attach_spread(audit, cs, col="cs_spread"):
    """The audit frame with the harness-built Corwin-Schultz spread
    (data_layer.load_or_build_cs_spread: me, ID, cs_spread) on every row,
    matched on (ID, SIGNAL_ASOF == me): the signal month's estimate, known at
    the signal date. A name-month without an estimate stays NaN; half_spreads
    fills it from its tier-month median."""
    key = pd.DataFrame({"ID": cs["ID"].astype(str).to_numpy(), "me": pd.to_datetime(cs["me"]).to_numpy(),
                        col: pd.to_numeric(cs[col], errors="coerce").to_numpy()})
    if key.duplicated(["ID", "me"]).any():
        raise LayerRefused("the spread series has more than one row for an (ID, month)")
    left = pd.DataFrame({"ID": audit["ID"].astype(str).to_numpy(),
                         "me": pd.to_datetime(audit["SIGNAL_ASOF"]).to_numpy()})
    got = left.merge(key, on=["ID", "me"], how="left")[col].to_numpy()
    out = audit.drop(columns=[col], errors="ignore").copy()
    out[col] = got
    return out


# =============================================================================
# Small numerics
# =============================================================================

def normal_scores(x):
    """Van der Waerden scores of a 1-D array (average ranks); NaN stays NaN.
    Same map as analytics.normal_scores: rank/(n+1) -> standard normal quantile."""
    x = np.asarray(x, dtype=float)
    out = np.full(len(x), np.nan)
    ok = np.isfinite(x)
    n = int(ok.sum())
    if n:
        out[ok] = norm.ppf(rankdata(x[ok]) / (n + 1.0))
    return out


def _group_sums(w, groups, n_groups):
    return np.bincount(groups, weights=w, minlength=n_groups)


def _group_median(values, groups, n_groups, valid):
    """Per-group median of values[valid]; NaN where a group has none."""
    out = np.full(n_groups, np.nan)
    if valid.any():
        s = pd.Series(values[valid]).groupby(groups[valid]).median()
        out[s.index.values] = s.values
    return out


def ewma_weights(n, halflife):
    """Weights for n observations ordered oldest..newest; the newest has lag 0."""
    lags = np.arange(n - 1, -1, -1, dtype=float)
    return 0.5 ** (lags / float(halflife))


def ewma_cov(fr, halflife):
    """EWMA covariance of a T x K factor-return history (oldest..newest) that
    may hold NaN (a factor not estimable that month). Each element uses the
    months where both factors exist (pairwise), weights renormalised over
    them; columns are demeaned by their own EWMA mean. The result is
    symmetrised and floored to positive semi-definite."""
    fr = np.asarray(fr, dtype=float)
    T, K = fr.shape
    wt = ewma_weights(T, halflife)
    mask = np.isfinite(fr)
    m = mask.astype(float)
    den_col = (wt[:, None] * m).sum(axis=0)
    mu = np.where(den_col > 0, (wt[:, None] * np.where(mask, fr, 0.0)).sum(axis=0) /
                  np.where(den_col > 0, den_col, 1.0), 0.0)
    fc = np.where(mask, fr - mu, 0.0)
    num = (wt[:, None] * fc).T @ fc
    den = (wt[:, None] * m).T @ m
    cov = np.where(den > 0, num / np.where(den > 0, den, 1.0), 0.0)
    cov = 0.5 * (cov + cov.T)
    vals, vecs = np.linalg.eigh(cov)
    return (vecs * np.clip(vals, 0.0, None)) @ vecs.T


# =============================================================================
# Panel: the audit frame as month slices and ID x month arrays
# =============================================================================

class LayerPanel:
    """The audit frame, sorted by (DATE, ID), with per-month slices and the
    two ID x month matrices the risk model needs (returns, residuals)."""

    def __init__(self, audit, lcfg, metas=None, group_col=None):
        self.group_col = group_col               # the search construction's within-group ranking
        spread_col = SPREAD_COLUMNS.get(str(lcfg["costs"]["half_spread"]))
        if spread_col is None:
            raise LayerRefused(f"unknown costs.half_spread {lcfg['costs']['half_spread']!r}")
        need = ["ID", "DATE", "monthly_ret", "ret_kind", "RET_END", "SIGNAL_ASOF", "liq_tier",
                "sector", "mkt_cap_usd", "adv_usd", "COMPOSITE_SCORE"]
        missing = [c for c in need if c not in audit.columns]
        if missing:
            raise LayerRefused(f"audit frame lacks {missing}")
        if spread_col not in audit.columns:
            raise LayerRefused(f"audit frame lacks the spread column {spread_col!r} (costs.half_spread="
                               f"{lcfg['costs']['half_spread']!r}): attach the harness-built series "
                               "(attach_spread / run_layer(spread=...)); the layer never falls back to the "
                               "half-spread floor for a whole panel")
        cols = need + [spread_col]
        leg_cols = [m["col"] for m in (metas or []) if m["col"] in audit.columns and m["col"] not in cols]
        df = audit[cols + leg_cols].copy()
        for c in ("DATE", "RET_END", "SIGNAL_ASOF"):
            df[c] = pd.to_datetime(df[c])
        df = df.sort_values(["DATE", "ID"], kind="mergesort").reset_index(drop=True)
        self.df = df
        self.spread_col = spread_col
        self.dates = pd.DatetimeIndex(sorted(df["DATE"].unique()))
        self.M = len(self.dates)
        mcode = np.searchsorted(self.dates.values, df["DATE"].values)
        self.offsets = np.searchsorted(mcode, np.arange(self.M + 1))
        first = df.groupby("DATE", sort=True)[["RET_END", "SIGNAL_ASOF"]].first()
        self.ret_end = first["RET_END"].values
        self.signal_asof = first["SIGNAL_ASOF"].values
        if np.any(np.diff(self.ret_end.astype("datetime64[ns]").astype(np.int64)) < 0):
            raise LayerRefused("RET_END is not monotone in DATE; the point-in-time index needs it")
        # months s usable at t: RET_END(s) <= SIGNAL_ASOF(t); since RET_END is
        # monotone, they are positions 0 .. avail_end[t]-1.
        self.avail_end = np.searchsorted(self.ret_end, self.signal_asof, side="right")
        codes, labels = pd.factorize(df["ID"], sort=False)
        self.id_code = codes.astype(np.int64)
        self.id_labels = np.asarray(labels)
        self.N = len(labels)
        self.ret = pd.to_numeric(df["monthly_ret"], errors="coerce").values.astype(float)
        self.delisted = df["ret_kind"].astype(str).str.startswith(DELISTED_PREFIX).values
        tier = df["liq_tier"].astype(str).values
        self.tier = np.full(len(df), len(TIERS), dtype=np.int64)
        for k, t in enumerate(TIERS):
            self.tier[tier == t] = k
        sec = df["sector"].astype(object).where(df["sector"].notna(), UNCLASSIFIED).astype(str).str.strip()
        sec = sec.where(~sec.str.lower().isin(_MISSING_SECTOR), UNCLASSIFIED)
        labels_sorted = sorted(set(sec) - {UNCLASSIFIED}) + [UNCLASSIFIED]
        self.sector_labels = labels_sorted
        self.G = len(labels_sorted)
        self.sector = pd.Categorical(sec, categories=labels_sorted).codes.astype(np.int64)
        self.mcap = pd.to_numeric(df["mkt_cap_usd"], errors="coerce").values.astype(float)
        self.adv = pd.to_numeric(df["adv_usd"], errors="coerce").values.astype(float)
        self.score = pd.to_numeric(df["COMPOSITE_SCORE"], errors="coerce").values.astype(float)
        self.spread = pd.to_numeric(df[spread_col], errors="coerce").values.astype(float)
        # ID x month return matrix (point-in-time slices are taken by column)
        self.RET = np.full((self.N, self.M), np.nan)
        self.RET[self.id_code, mcode] = self.ret
        self.mcode = mcode
        self.metas = [m for m in (metas or []) if m["col"] in df.columns]
        self._fam = None
        # D4's market M: the universe's cap-weighted total monthly_ret (Shumway
        # delisting returns included), one value per panel month.
        self.mkt = universe_market_return(df[["DATE", "monthly_ret", "mkt_cap_usd"]]).reindex(self.dates).to_numpy(float)
        mb = (lcfg.get("optimiser") or {}).get("market_beta") or {}
        self.beta_window = int(mb.get("window_months", 36))
        self.beta_min_obs = int(mb.get("min_obs", 12))
        self._betas = {}

    def market_betas(self, m):
        """(beta, n_own) for month m's universe rows: market_beta_raw filled
        from the name's sector-month median, then the month's median; (None, 0)
        when no name has an estimate (the beta constraint is then dropped that
        month and counted). Memoised."""
        if m not in self._betas:
            raw = market_beta_raw(self, m)
            valid = np.isfinite(raw)
            if not valid.any():
                self._betas[m] = (None, 0)
            else:
                g = self.sector[self.sl(m)]
                med_g = _group_median(raw, g, self.G, valid)
                fill = np.where(np.isfinite(med_g[g]), med_g[g], float(np.median(raw[valid])))
                self._betas[m] = (np.where(valid, raw, fill), int(valid.sum()))
        return self._betas[m]

    def sl(self, m):
        return slice(self.offsets[m], self.offsets[m + 1])

    def sector_leak(self):
        """How much of the universe sits in `Unclassified`, and whether that
        group over-represents delistings. TICKERS.sector is the vendor's
        CURRENT classification, so a dead name may be unclassified today for
        reasons tied to its fate; a delisting share far above the classified
        names' is the signature of that leak (CONSTRUCTION.md §9)."""
        unc = self.sector == self.sector_labels.index(UNCLASSIFIED)
        yrs = pd.DatetimeIndex(self.df["DATE"]).year
        by = pd.Series(unc.astype(float)).groupby(yrs).mean() * 100
        out = {"unclassified_share_pct": float(unc.mean() * 100),
               "unclassified_share_min_year": int(by.idxmin()), "unclassified_share_min_year_pct": float(by.min()),
               "unclassified_share_max_year": int(by.idxmax()), "unclassified_share_max_year_pct": float(by.max()),
               "delisted_share_unclassified_pct": float(self.delisted[unc].mean() * 100) if unc.any() else float("nan"),
               "delisted_share_classified_pct": float(self.delisted[~unc].mean() * 100) if (~unc).any() else float("nan")}
        return out

    def family_scores(self, m):
        """{family: normal score of the family's mean member rank} for month m,
        the same two-level ranks the composite blends (blend_family_ranks)."""
        if not self.metas:
            return {}
        g = self.df.iloc[self.sl(m)]
        ranks = pd.DataFrame(compute_factor_ranks(g, self.metas, group_col=self.group_col), index=g.index)
        out = {}
        for fam, names in family_members(self.metas).items():
            cols = [n for n in names if n in ranks.columns]
            out[fam] = normal_scores(ranks[cols].astype(float).mean(axis=1, skipna=True).values)
        return out


# =============================================================================
# §4 Risk model
# =============================================================================

class RiskMonth:
    __slots__ = ("X", "F", "D", "sigma", "ready", "n_hist", "vol_ok")

    def __init__(self, X, F, D, sigma, ready, n_hist, vol_ok):
        self.X, self.F, self.D, self.sigma = X, F, D, sigma
        self.ready, self.n_hist, self.vol_ok = ready, n_hist, vol_ok


def trailing_vol_raw(P, m, rm):
    """12-month std of monthly_ret over months s <= t-1 (>= min obs), else the
    name's sector median, else the cross-section median. None if no name has
    enough history (the first months of the panel)."""
    sl = P.sl(m)
    ids, g = P.id_code[sl], P.sector[sl]
    a = int(P.avail_end[m])
    L, k = int(rm["trailing_vol_months"]), int(rm["trailing_vol_min_obs"])
    if a <= 0:
        return None
    R = P.RET[ids, max(0, a - L):a]
    obs = np.isfinite(R)
    cnt = obs.sum(axis=1)
    mean = np.where(obs, R, 0.0).sum(axis=1) / np.maximum(cnt, 1)
    ss = np.where(obs, (R - mean[:, None]) ** 2, 0.0).sum(axis=1)
    sd = np.where(cnt >= 2, np.sqrt(ss / np.maximum(cnt - 1, 1)), np.nan)
    valid = (cnt >= k) & np.isfinite(sd)
    if not valid.any():
        return None
    med_g = _group_median(sd, g, P.G, valid)
    overall = float(np.median(sd[valid]))
    fill = np.where(np.isfinite(med_g[g]), med_g[g], overall)
    return np.where(valid, sd, fill)


def market_beta_raw(P, m):
    """Each universe name's trailing market beta at month m: the OLS slope of
    its monthly_ret on M (P.mkt, D4's market: the universe's cap-weighted
    total return) over months s with RET_END(s) <= SIGNAL_ASOF(t), the last
    `optimiser.market_beta.window_months` (36) of them, i.e. t-36..t-1, on the
    months where both exist, needing `min_obs` (12) of them; NaN otherwise.
    This is analytics.trailing_beta's estimate (pairwise-complete covariance
    over variance, variance > 1e-12) vectorised over names; a test holds the
    two equal. Missing estimates are filled by LayerPanel.market_betas."""
    sl = P.sl(m)
    ids = P.id_code[sl]
    n = sl.stop - sl.start
    a = int(P.avail_end[m])
    if a <= 0:
        return np.full(n, np.nan)
    lo = max(0, a - P.beta_window)
    R = P.RET[ids, lo:a]
    x = P.mkt[lo:a]
    ok = np.isfinite(R) & np.isfinite(x)[None, :]
    cnt = ok.sum(axis=1)
    den = np.maximum(cnt, 1)
    mx = np.where(ok, x[None, :], 0.0).sum(axis=1) / den
    my = np.where(ok, R, 0.0).sum(axis=1) / den
    dx = np.where(ok, x[None, :] - mx[:, None], 0.0)
    dy = np.where(ok, R - my[:, None], 0.0)
    dof = np.maximum(cnt - 1, 1)
    cov = (dx * dy).sum(axis=1) / dof
    var = (dx * dx).sum(axis=1) / dof
    good = (cnt >= P.beta_min_obs) & (var > _EPS)
    return np.where(good, cov / np.where(good, var, 1.0), np.nan)


def exposures(P, m, rm):
    """X at month m for every universe name: sector dummies (no intercept),
    size = normal score of log mkt cap, trailing vol = normal score of the
    filled 12m std. Columns: G sectors, then size, then vol."""
    sl = P.sl(m)
    n = sl.stop - sl.start
    X = np.zeros((n, P.G + 2))
    X[np.arange(n), P.sector[sl]] = 1.0
    mc = P.mcap[sl]
    with np.errstate(divide="ignore", invalid="ignore"):
        lmc = np.where(mc > 0, np.log(mc), np.nan)
    X[:, P.G] = np.nan_to_num(normal_scores(lmc), nan=0.0)
    vr = trailing_vol_raw(P, m, rm)
    vol_ok = vr is not None
    if vol_ok:
        X[:, P.G + 1] = np.nan_to_num(normal_scores(vr), nan=0.0)
    return X, vol_ok


def build_risk_model(P, lcfg, log=None):
    """One RiskMonth per panel month. Factor returns at s are a WLS of
    monthly_ret(s) on X(s), weight sqrt(mkt cap) on the squared residual (rows
    scaled by mktcap^(1/4)). The forecast at t uses months s with
    RET_END(s) <= SIGNAL_ASOF(t), the last `factor_cov_window_months` of them."""
    rm = lcfg["risk_model"]
    hl_f, W, min_f = (float(rm["factor_cov_halflife_months"]), int(rm["factor_cov_window_months"]),
                      int(rm["factor_cov_min_months"]))
    hl_s, shrink, min_s = (float(rm["specific_halflife_months"]),
                           float(rm["specific_shrink_to_sector_median"]), int(rm["specific_min_obs"]))
    K = P.G + 2
    fret = np.full((P.M, K), np.nan)
    RES = np.full((P.N, P.M), np.nan)
    out = []
    for m in range(P.M):
        sl = P.sl(m)
        ids, g = P.id_code[sl], P.sector[sl]
        X, vol_ok = exposures(P, m, rm)
        # ---- forecast at m from months < avail_end[m] -----------------------
        a = int(P.avail_end[m])
        lo = max(0, a - W)
        hist = fret[lo:a]
        n_hist = int(np.isfinite(hist).any(axis=1).sum()) if len(hist) else 0
        F = D = sigma = None
        ready = False
        if n_hist >= min_f:
            F = ewma_cov(hist, hl_f)
            E = RES[ids, lo:a]
            obs = np.isfinite(E)
            wt = ewma_weights(E.shape[1], hl_s)
            den = (obs * wt).sum(axis=1)
            v = np.where(den > 0, (np.where(obs, E * E, 0.0) * wt).sum(axis=1) / np.where(den > 0, den, 1.0), np.nan)
            valid = (obs.sum(axis=1) >= min_s) & np.isfinite(v)
            if valid.any():
                med_g = _group_median(v, g, P.G, valid)
                med = np.where(np.isfinite(med_g[g]), med_g[g], float(np.median(v[valid])))
                D = np.where(valid, (1.0 - shrink) * v + shrink * med, med)
                sigma = np.sqrt(np.einsum("ij,jk,ik->i", X, F, X) + D)
                ready = True
        out.append(RiskMonth(X, F, D, sigma, ready, n_hist, vol_ok))
        # ---- factor returns and residuals AT m (used only by later months) ----
        r = P.ret[sl]
        mc = P.mcap[sl]
        ok = np.isfinite(r) & np.isfinite(mc) & (mc > 0)
        if ok.sum() < 2:
            continue
        cols = sorted(set(np.unique(g[ok]).tolist())) + [P.G] + ([P.G + 1] if vol_ok else [])
        sw = mc[ok] ** 0.25
        f, *_ = np.linalg.lstsq(X[ok][:, cols] * sw[:, None], r[ok] * sw, rcond=None)
        fret[m, cols] = f
        RES[ids[ok], m] = r[ok] - X[ok][:, cols] @ f
    if log:
        first = next((i for i, rmo in enumerate(out) if rmo.ready), None)
        log(f"    risk model: {P.G} sector groups ({', '.join(P.sector_labels)}) + size + trailing vol; "
            f"first ready month {P.dates[first].date() if first is not None else 'never'}")
    return out


def ex_ante_var(w, X, F, D):
    """w' (X F X' + D) w, monthly."""
    xw = X.T @ w
    return float(xw @ F @ xw + np.sum(D * w * w))


# =============================================================================
# §5 Optimiser: closed form, sector- and beta-neutral, Woodbury
# =============================================================================

def sigma_inv(V, X, F, D):
    """Sigma^-1 V for Sigma = X F X' + D, by Woodbury without F^-1:
    Sigma^-1 = D^-1 - D^-1 X F (I + X'D^-1 X F)^-1 X' D^-1."""
    V = np.asarray(V, dtype=float)
    Dinv = 1.0 / D
    DV = Dinv[:, None] * V if V.ndim == 2 else Dinv * V
    A = X.T @ (Dinv[:, None] * X)
    Mx = np.eye(F.shape[0]) + A @ F
    inner = F @ np.linalg.solve(Mx, X.T @ DV)
    return DV - (Dinv[:, None] * (X @ inner) if V.ndim == 2 else Dinv * (X @ inner))


def solve_neutral_mv(alpha, X, F, D, C, lam=1.0):
    """argmax alpha'w - (lam/2) w'Sigma w  s.t. C'w = 0, closed form from the KKT
    conditions: w = Sigma^-1 (alpha - C mu) / lam, mu = (C'Sigma^-1 C)^-1 C'Sigma^-1 alpha.
    C is any n x k constraint matrix (sector dummies, plus the beta column).
    A redundant column (beta collinear with the dummies) is solved by least
    squares: the constraints are consistent, so the optimum is the same."""
    y = sigma_inv(alpha, X, F, D)
    Z = sigma_inv(C, X, F, D)
    try:
        mu = np.linalg.solve(C.T @ Z, C.T @ y)
    except np.linalg.LinAlgError:
        mu = np.linalg.lstsq(C.T @ Z, C.T @ y, rcond=None)[0]
    return (y - Z @ mu) / float(lam)


def project_neutral(w, groups, n_groups, free=None):
    """Orthogonal projection onto {sum of w within each group = 0}, moving only
    `free` names (all when None): an equal shift within each group."""
    free = np.ones(len(w), bool) if free is None else free
    r = _group_sums(w, groups, n_groups)
    nf = np.bincount(groups[free], minlength=n_groups)
    shift = np.where(nf > 0, -r / np.maximum(nf, 1), 0.0)
    w = w.copy()
    w[free] += shift[groups[free]]
    return w


class Constraint:
    """The linear constraint A'w = 0 on one month's rows, A = [group dummies |
    extra columns]. `groups` / `n_groups` are the sector groups (one group:
    dollar neutral); `extra` is n x q, q = 1 for the market-beta column
    (optimiser.constraints = sector_beta_neutral), else absent.

    Every step of §5 that imposes the constraint goes through `project`: the
    orthogonal projection onto {A'w = 0} moving only the `free` rows, i.e. the
    minimum-norm change w_f -= A_f (A_f'A_f)^+ A'w. With no extra column it
    is exactly project_neutral's equal shift within each group (the same
    arithmetic, so a sector-only book is unchanged by the generalisation)."""

    def __init__(self, groups, n_groups, extra=None):
        self.groups = np.asarray(groups, dtype=np.int64)
        self.n_groups = int(n_groups)
        E = None if extra is None else np.asarray(extra, dtype=float).reshape(len(self.groups), -1)
        self.extra = E if (E is not None and E.shape[1] > 0) else None

    def subset(self, mask):
        return Constraint(self.groups[mask], self.n_groups, None if self.extra is None else self.extra[mask])

    def residual(self, w):
        """A'w: the group sums, then each extra column's exposure."""
        r = _group_sums(w, self.groups, self.n_groups)
        return r if self.extra is None else np.concatenate([r, self.extra.T @ w])

    def max_resid(self, w):
        return float(np.max(np.abs(self.residual(w)))) if len(w) else 0.0

    def extra_resid(self, w):
        """max |extra'w| (the book's beta exposure under the beta constraint); 0 without one."""
        return float(np.max(np.abs(self.extra.T @ w))) if (self.extra is not None and len(w)) else 0.0

    def matrix(self):
        """Dense A over the groups present in these rows (an empty group is no
        constraint, §9.8), then the extra columns."""
        present = np.unique(self.groups)
        S = (self.groups[:, None] == present[None, :]).astype(float)
        return S if self.extra is None else np.hstack([S, self.extra])

    def bad_rows(self, w, tol):
        """Rows a violated constraint involves: members of a group whose sum
        exceeds tol, and every row when an extra row does."""
        r = self.residual(w)
        if self.extra is not None and np.any(np.abs(r[self.n_groups:]) > tol):
            return np.ones(len(w), bool)
        return (np.abs(r[:self.n_groups]) > tol)[self.groups]

    def with_group_fallback(self, mask):
        """`mask`, except that a group with no row in it takes all its members."""
        n = np.bincount(self.groups[mask], minlength=self.n_groups)
        return np.where(n[self.groups] > 0, mask, True)

    def step(self, w, free):
        """The projection's change of the free rows (zero elsewhere)."""
        free = np.asarray(free, bool)
        G, g = self.n_groups, self.groups
        r = self.residual(w)
        nf = np.bincount(g[free], minlength=G)
        d = np.zeros(len(w))
        if self.extra is None:
            shift = np.where(nf > 0, -r / np.maximum(nf, 1), 0.0)
            d[free] = shift[g[free]]
            return d
        if not free.any():
            return d
        Ef = self.extra[free]
        q = Ef.shape[1]
        SE = np.stack([np.bincount(g[free], weights=Ef[:, j], minlength=G) for j in range(q)], axis=1)
        M = np.zeros((G + q, G + q))
        M[np.arange(G), np.arange(G)] = nf
        M[:G, G:] = SE
        M[G:, :G] = SE.T
        M[G:, G:] = Ef.T @ Ef
        lam = np.linalg.lstsq(M, r, rcond=None)[0]
        d[free] = -(lam[g[free]] + Ef @ lam[G:])
        return d

    def project(self, w, free=None):
        free = np.ones(len(w), bool) if free is None else np.asarray(free, bool)
        if self.extra is None:
            return project_neutral(w, self.groups, self.n_groups, free)
        w = w + self.step(w, free)
        return w + self.step(w, free)          # one refinement pass absorbs the rounding


def apply_name_cap(w, cons, floor, mult, tol, max_iter):
    """Step 2: |w_i| <= max(floor, mult / N_side), N_side the count of names on
    w_i's side of the target. Clip, re-project onto the constraint (a
    Constraint) over the names strictly inside their cap, iterate to tol.
    Returns (w, iters, max cap excess, max constraint residual)."""
    w = np.asarray(w, dtype=float).copy()
    nL, nS = int((w > 0).sum()), int((w < 0).sum())
    capL = max(floor, mult / nL) if nL else floor
    capS = max(floor, mult / nS) if nS else floor

    def caps(x):
        return np.where(x > 0, capL, np.where(x < 0, capS, min(capL, capS)))

    it = 0
    for it in range(1, int(max_iter) + 1):
        c = caps(w)
        w = np.clip(w, -c, c)
        if cons.max_resid(w) <= tol:
            break
        free = np.abs(w) < caps(w) - tol
        w = cons.project(w, free)
        if cons.max_resid(w) > tol:               # a group with every name at its cap
            w = cons.project(w, cons.bad_rows(w, tol))
        if np.max(np.abs(w) - caps(w)) <= tol:
            break
    free = np.abs(w) < caps(w)
    w = cons.project(w, cons.with_group_fallback(free))
    excess = float(max(0.0, np.max(np.abs(w) - caps(w)))) if len(w) else 0.0
    return w, it, excess, cons.max_resid(w)


def buffer_step(target, held, rel, abs_, kappa):
    """Step 3: keep the held weight when |w*_i - w_held_i| <= rel|w*_i| + abs;
    otherwise move a fraction kappa toward w*_i."""
    diff = target - held
    keep = np.abs(diff) <= rel * np.abs(target) + abs_
    return np.where(keep, held, held + kappa * diff), keep


def participation_cap(w, held, capd):
    """Step 4: |dw_i| <= capd_i (= pct * adv * days / AUM). Returns (w, hit)."""
    d = w - held
    hit = np.abs(d) > capd * (1.0 + 1e-12)
    return held + np.clip(d, -capd, capd), hit


def _exact(w, cons, eligible, held=None, capd=None):
    """Remove a residual already inside tolerance exactly (to rounding): a
    projection over the eligible names of each group that still have
    participation headroom (else all eligible, else all members)."""
    g, G = cons.groups, cons.n_groups
    pref = eligible if held is None else eligible & (np.abs(w - held) < capd * (1 - 1e-6))
    n_pref = np.bincount(g[pref], minlength=G)
    n_elig = np.bincount(g[eligible], minlength=G)
    members = np.where(n_pref[g] > 0, pref, np.where(n_elig[g] > 0, eligible, True))
    return cons.project(w, members)


def _neutralise_with_headroom(w, held, capd, cons, eligible, tol, max_iter):
    """Restore the constraint moving eligible names only, and only as far as
    their participation headroom allows (water-filling): project over the
    names with headroom in the direction the projection moves them, clip each
    move to its headroom, repeat. With group constraints only, every name in
    a group moves the same way and this is the equal-shift water-fill. A
    residual no eligible name can absorb is projected over the eligible
    members anyway (the constraint first); those names are counted as
    overrides."""
    w = w.copy()
    for _ in range(int(max_iter)):
        if cons.max_resid(w) <= tol:
            return _exact(w, cons, eligible, held, capd), 0
        d = w - held
        up, dn = capd - d, capd + d
        free = eligible & cons.bad_rows(w, tol) & ((up > 0) | (dn > 0))
        s = np.zeros(len(w))
        for _k in range(4):                       # settle the set of names that can move the needed way
            if not free.any():
                break
            s = cons.step(w, free)
            room = np.where(s > 0, up, dn)
            drop = free & (s != 0) & (room <= 0)
            if not drop.any():
                break
            free = free & ~drop
        room = np.maximum(np.where(s > 0, up, dn), 0.0)
        move = np.where(free, np.sign(s) * np.minimum(np.abs(s), room), 0.0)
        if not np.any(move):
            break
        w = w + move
    if cons.max_resid(w) <= tol:
        return _exact(w, cons, eligible, held, capd), 0
    members = cons.with_group_fallback(eligible) & cons.bad_rows(w, tol)
    w = cons.project(w, members)
    return w, int(members.sum())


def final_reproject(w, held, capd, cons, eligible, gross_cap, tol, max_iter):
    """Step 5: re-project onto the constraint and the gross cap. The names
    moved here have their trades changed; those trades are counted and
    charged like any other. Participation headroom is respected where it can
    be; the constraint wins where it cannot (overrides counted)."""
    for _ in range(int(max_iter)):
        w, _ov = _neutralise_with_headroom(w, held, capd, cons, eligible, tol, max_iter)
        g = float(np.abs(w).sum())
        if g > gross_cap * (1 + 1e-12):
            w = w * (gross_cap / g)
        w, _ = participation_cap(w, held, capd)
        ok_n = cons.max_resid(w) <= tol
        ok_g = float(np.abs(w).sum()) <= gross_cap * (1 + 1e-9)
        if ok_n and ok_g:
            break
    w, _ov = _neutralise_with_headroom(w, held, capd, cons, eligible, tol, max_iter)
    # the budget is a hard bound: a uniform scale keeps every linear constraint at zero
    g = float(np.abs(w).sum())
    if g > gross_cap:
        w = w * (gross_cap / g)
    # names whose FINAL trade exceeds its participation cap because the
    # constraint could not be met otherwise (the constraint first)
    over = np.abs(w - held) > capd * (1 + 1e-9) + 1e-15
    part_excess = float(np.max(np.abs(w - held) - capd)) if len(w) else 0.0
    return w, {"overrides": int(over.sum()), "participation_excess": max(0.0, part_excess),
               "gross": float(np.abs(w).sum())}


# =============================================================================
# §3 Alpha, composite IC and the target book (AUM-independent)
# =============================================================================

def ic_forecast(P, lcfg):
    """IC_t: the trailing mean of the composite's realised monthly rank IC over
    the last `ic_lookback_months` months s with RET_END(s) <= SIGNAL_ASOF(t),
    needing `ic_min_months`; NaN otherwise."""
    a_cfg = lcfg["alpha"]
    L, k = int(a_cfg["ic_lookback_months"]), int(a_cfg["ic_min_months"])
    ic = compute_ic(P.df[["DATE", "COMPOSITE_SCORE", "monthly_ret"]])
    arr = np.full(P.M, np.nan)
    if len(ic):
        pos = np.searchsorted(P.dates.values, pd.DatetimeIndex(ic.index).values)
        arr[pos] = ic["IC"].values
    out = np.full(P.M, np.nan)
    for m in range(P.M):
        a = int(P.avail_end[m])
        h = arr[max(0, a - L):a]
        h = h[np.isfinite(h)]
        if len(h) >= k:
            out[m] = float(h.mean())
    return out, arr


def month_constraint(P, m, constraint):
    """(Constraint, beta, beta_dropped) on month m's universe rows for a
    declared constraint set: `sector_beta_neutral` = the sector groups plus the
    market-beta column (LayerPanel.market_betas, filled), `sector_neutral` =
    the sector groups, `dollar_neutral` = one group. beta is None, and
    beta_dropped True, when the beta constraint is declared but no name has an
    estimate that month (the sector constraint alone then applies)."""
    if constraint not in CONSTRAINTS:
        raise LayerRefused(f"unknown optimiser constraint {constraint!r}; declared: {', '.join(CONSTRAINTS)}")
    sl = P.sl(m)
    n = sl.stop - sl.start
    if constraint == "dollar_neutral":
        return Constraint(np.zeros(n, dtype=np.int64), 1), None, False
    beta = P.market_betas(m)[0] if constraint == "sector_beta_neutral" else None
    dropped = constraint == "sector_beta_neutral" and beta is None
    return Constraint(P.sector[sl], P.G, None if beta is None else beta[:, None]), beta, dropped


def build_target(P, R, m, ic_t, lcfg, constraint=None):
    """Steps 1-2 for month m, on the month's universe rows, under `constraint`
    (default: config optimiser.constraints). Returns a dict with `t` (target, 0
    on unscored names), `flat` and its reason, the gross budget G_t, the
    budget-scaled flag, the month's Constraint (`cons`) and the per-step
    constraint residuals (for tests and the report)."""
    a_cfg, o = lcfg["alpha"], lcfg["optimiser"]
    constraint = str(o["constraints"]) if constraint is None else str(constraint)
    sl = P.sl(m)
    n = sl.stop - sl.start
    rmo = R[m]
    cons, beta, dropped = month_constraint(P, m, constraint)
    res = {"t": np.zeros(n), "flat": True, "reason": "", "G_t": 0.0, "ic_t": ic_t,
           "budget_scaled": False, "groups": cons.groups, "n_groups": cons.n_groups, "cons": cons,
           "beta": beta, "beta_dropped": dropped, "constraint": constraint,
           "eligible": np.zeros(n, bool), "exante_ann_vol": 0.0}
    if not rmo.ready:
        res["reason"] = "no_history_risk"
        return res
    if not np.isfinite(ic_t):
        res["reason"] = "no_history_ic"
        return res
    gross_cap = float(a_cfg["gross_cap"])
    G = gross_cap * float(np.clip(ic_t / float(a_cfg["ic_ref"]), 0.0, 1.0))   # §3 gross budget G_t
    res["G_t"] = G
    res["budget_scaled"] = bool(G < gross_cap)
    if G <= 0:
        res["reason"] = "ic_nonpositive"
        return res
    I = np.isfinite(P.score[sl]) & np.isfinite(rmo.sigma)
    if I.sum() < 2:
        res["reason"] = "no_names"
        return res
    z = normal_scores(P.score[sl][I])
    alpha = z * rmo.sigma[I]
    cI = cons.subset(I)
    X, D = rmo.X[I], rmo.D[I]
    d = solve_neutral_mv(alpha, X, rmo.F, D, cI.matrix())
    var_d = ex_ante_var(d, X, rmo.F, D)
    if not (var_d > 0):
        res["reason"] = "degenerate"
        return res
    g1 = float(np.abs(d).sum())
    if not (g1 > 0):
        res["reason"] = "degenerate"
        return res
    w1 = d * (G / g1)                                  # scaled to the month's gross budget
    w1 = cI.project(w1)                                # exact to rounding
    res["resid_step1"] = cI.max_resid(w1)
    w2, it, excess, resid2 = apply_name_cap(w1, cI, float(o["name_cap_floor"]),
                                            float(o["name_cap_mult"]), float(o["cap_tol"]),
                                            int(o["cap_max_iter"]))
    res.update({"w_step1": w1, "resid_step2": resid2, "name_cap_iters": it, "name_cap_excess": excess,
                "flat": False, "reason": "", "gross_step1": G,
                "exante_ann_vol": float(np.sqrt(12 * ex_ante_var(w2, X, rmo.F, D)))})
    t = np.zeros(n)
    t[I] = w2
    res["t"] = t
    res["eligible"] = I
    return res


# =============================================================================
# §6 Costs and the monthly accounting
# =============================================================================

def half_spreads(spread, tier, lcfg, mode="measured"):
    """Per-name half-spread (fraction). 'measured': CS spread / 2, floored, a
    missing value takes the month's median of its liquidity tier (then the
    month's median, then the floor). 'fixed': the declared tier schedule."""
    c = lcfg["costs"]
    floor = float(c["half_spread_floor_bp"]) / 1e4
    if mode == "fixed":
        sched = c["sensitivity"]["fixed_half_spread_bp"]
        vals = np.array([float(sched[t]) / 1e4 for t in TIERS] + [float(max(sched.values())) / 1e4])
        return vals[tier]
    hs = np.where(np.isfinite(spread), np.maximum(spread / 2.0, floor), np.nan)
    ok = np.isfinite(hs)
    med_t = _group_median(hs, tier, len(TIERS) + 1, ok)
    overall = float(np.median(hs[ok])) if ok.any() else floor
    fill = np.where(np.isfinite(med_t[tier]), med_t[tier], overall)
    return np.where(ok, hs, fill)


def trade_costs(dw, hs, sd, adv, aum, eta):
    """(spread, impact) as fractions of capital for trades dw (fractions of
    capital): |dw| * hs  and  |dw| * eta * sigma_d * sqrt(|dw| * AUM / ADV)."""
    q = np.abs(dw)
    sd = np.nan_to_num(sd, nan=0.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        part = np.where(adv > 0, np.sqrt(q * aum / adv), 0.0)
    return q * hs, q * eta * sd * part


def account_month(w, h, r, delisted, hs, sd, adv, aum, eta, borrow_bp_yr, trade_frac=1.0):
    """One month's accounting on aligned arrays (the month's universe names
    plus any held names that left it, with w = 0). Trades dw = w - h are
    charged; the short book pays borrow (a scalar rate or one per name, bp/yr).

    Execution: the base convention (trade_frac = 1) trades at the signal-date
    close, as Stages 1-3 do, so the whole final book earns monthly_ret(t). The
    execution sensitivity lets the traded dw earn only `trade_frac` of it: the
    book earns sum (h + trade_frac * dw) r. Each name ends the month worth
    w + (h + trade_frac * dw) r; the held weights for next month are that over
    (1 + net), zero for a delisted name (closed to cash at its Shumway return,
    no cost)."""
    r = np.nan_to_num(r, nan=0.0)
    dw = w - h
    sp, im = trade_costs(dw, hs, sd, adv, aum, eta)
    rate = np.broadcast_to(np.asarray(borrow_bp_yr, dtype=float), w.shape)
    borrow_i = rate / 1e4 / 12.0 * np.where(w < 0, -w, 0.0)
    borrow = float(borrow_i.sum())
    contrib = (h + float(trade_frac) * dw) * r
    gross = float(contrib.sum())
    net = gross - float(sp.sum()) - float(im.sum()) - borrow
    h_next = np.where(delisted, 0.0, w + contrib) / (1.0 + net)
    return {"gross": gross, "spread": float(sp.sum()), "impact": float(im.sum()), "borrow": borrow,
            "net": net, "h_next": h_next, "dw": dw, "sp": sp, "im": im, "contrib": contrib,
            "borrow_i": borrow_i}


# =============================================================================
# The book path: one pass over the book months at one AUM
# =============================================================================

def borrow_rates(lcfg, mode="flat"):
    """bp/yr by tier code (MEGA, MID, SMALL, other). 'flat': the declared single
    rate; 'tiered': the sensitivity schedule, any other tier at its largest."""
    c = lcfg["costs"]
    if mode == "tiered":
        sched = c["sensitivity"]["borrow_bp_per_year_by_tier"]
        return np.array([float(sched[t]) for t in TIERS] + [float(max(sched.values()))])
    return np.full(len(TIERS) + 1, float(c["borrow_bp_per_year"]))


def daily_sigma(P, R, m, lcfg):
    """sigma_d = the risk model's monthly sigma / sqrt(21). A name without one
    takes the month's tier median, then the month's median; a month with no
    risk model (not ready) uses the trailing 12m realised std (the vol
    factor's own input, point-in-time) the same way. NaN only if none exists."""
    sl = P.sl(m)
    n = sl.stop - sl.start
    tier = P.tier[sl]
    sig = R[m].sigma if R[m].sigma is not None else None
    if sig is None:
        sig = trailing_vol_raw(P, m, lcfg["risk_model"])
    sd = (np.asarray(sig, dtype=float) / np.sqrt(21.0)) if sig is not None else np.full(n, np.nan)
    ok = np.isfinite(sd)
    if ok.all() or not ok.any():
        return sd
    med_t = _group_median(sd, tier, len(TIERS) + 1, ok)
    fill = np.where(np.isfinite(med_t[tier]), med_t[tier], float(np.median(sd[ok])))
    return np.where(ok, sd, fill)


def run_book(P, R, lcfg, book_months, aum, decide, eta, hs_mode="measured", fam_cache=None,
             borrow_mode="flat", trade_frac=1.0):
    """Walk the book months. `decide(m, held_on_universe)` returns (w, diag):
    the final weights on the month's universe rows. Names held but no longer
    in the universe are sold at the signal date and charged at their last
    known half-spread, sigma and ADV (no participation cap on the exit)."""
    rates = borrow_rates(lcfg, borrow_mode)
    n_t = len(TIERS) + 1
    h = np.zeros(P.N)
    last_hs, last_sd = np.full(P.N, np.nan), np.full(P.N, np.nan)
    last_adv, last_tier = np.full(P.N, np.nan), np.full(P.N, len(TIERS), dtype=np.int64)
    rec = []
    for m in book_months:
        sl = P.sl(m)
        ids, n = P.id_code[sl], sl.stop - sl.start
        rmo = R[m]
        hs = half_spreads(P.spread[sl], P.tier[sl], lcfg, hs_mode)
        sd = daily_sigma(P, R, m, lcfg)
        adv = P.adv[sl]
        last_hs[ids], last_sd[ids], last_adv[ids], last_tier[ids] = hs, sd, adv, P.tier[sl]
        in_u = np.zeros(P.N, bool)
        in_u[ids] = True
        held_ids = np.flatnonzero(h)
        exits = held_ids[~in_u[held_ids]]
        hU = h[ids]
        w, diag = decide(m, hU)
        ne = len(exits)
        W = np.concatenate([w, np.zeros(ne)])
        H = np.concatenate([hU, h[exits]])
        acc = account_month(W, H, np.concatenate([P.ret[sl], np.zeros(ne)]),
                            np.concatenate([P.delisted[sl], np.zeros(ne, bool)]),
                            np.concatenate([hs, last_hs[exits]]), np.concatenate([sd, last_sd[exits]]),
                            np.concatenate([adv, last_adv[exits]]), aum, eta,
                            np.concatenate([rates[P.tier[sl]], rates[last_tier[exits]]]), trade_frac)
        h = np.zeros(P.N)
        h[ids] = acc["h_next"][:n]
        tiers = np.concatenate([P.tier[sl], last_tier[exits]])
        row = {"m": m, "date": P.dates[m], "gross": acc["gross"], "net": acc["net"],
               "spread": acc["spread"], "impact": acc["impact"], "borrow": acc["borrow"],
               "turnover": 0.5 * float(np.abs(acc["dw"]).sum()), "traded": float(np.abs(acc["dw"]).sum()),
               "n_exit_sales": int(ne),
               "book_gross": float(np.abs(w).sum()), "n_long": int((w > 0).sum()), "n_short": int((w < 0).sum()),
               "n_ret_missing": int((~np.isfinite(P.ret[sl]) & (w != 0)).sum()),
               "impact_sigma_missing_trades": int((~np.isfinite(np.concatenate([sd, last_sd[exits]]))
                                                    & (acc["dw"] != 0)).sum())}
        # halted names: opened or increased in a month whose return is a delisting
        newdl = P.delisted[sl] & (np.abs(w) > np.abs(hU) + 1e-15)
        row["new_pos_delisting_n"] = int(newdl.sum())
        row["new_pos_delisting_pnl"] = float(acc["contrib"][:n][newdl].sum())
        row["tier_gross"] = np.bincount(P.tier[sl], weights=acc["contrib"][:n], minlength=n_t)
        row["tier_cost"] = np.bincount(tiers, weights=acc["sp"] + acc["im"], minlength=n_t)
        row["tier_traded"] = np.bincount(tiers, weights=np.abs(acc["dw"]), minlength=n_t)
        row["tier_borrow"] = np.bincount(tiers, weights=acc["borrow_i"], minlength=n_t)
        row["tier_n_long"] = np.bincount(P.tier[sl], weights=(w > 0).astype(float), minlength=n_t)
        row["tier_n_short"] = np.bincount(P.tier[sl], weights=(w < 0).astype(float), minlength=n_t)
        if rmo.ready and np.any(w):
            row["exante_sd"] = float(np.sqrt(max(ex_ante_var(w, rmo.X, rmo.F, rmo.D), 0.0)))
            row["exp_size"] = float(w @ rmo.X[:, P.G])
            row["exp_vol"] = float(w @ rmo.X[:, P.G + 1])
        else:
            row["exante_sd"], row["exp_size"], row["exp_vol"] = np.nan, np.nan, np.nan
        # the book's ex-ante market beta (every row, constrained or not) and M,
        # for the realised beta of the book on the market (summarise)
        bm = P.market_betas(m)[0]
        row["exp_beta"] = float(w @ bm) if (bm is not None and np.any(w)) else np.nan
        row["mkt"] = float(P.mkt[m])
        if fam_cache is not None and np.any(w):
            for fam, z in fam_cache(m).items():
                row[f"exp_family_{fam}"] = float(np.nansum(w * np.nan_to_num(z, nan=0.0)))
        row.update(diag)
        rec.append(row)
    return rec


def layer_decider(P, targets, lcfg, aum, use_buffer=True):
    """The declared pipeline, steps 3-5, on top of the AUM-independent targets
    (steps 1-2). A flat month (no history, or IC_t <= 0) is exactly flat: the
    buffer and the participation cap are bypassed and the liquidation charged."""
    o, a_cfg = lcfg["optimiser"], lcfg["alpha"]
    rel, abs_, kappa = float(o["buffer_rel"]), float(o["buffer_abs"]), float(o["buffer_step"])
    pct, days = float(o["participation_pct"]) / 100.0, float(o["participation_days"])
    tol, max_iter, gross_cap = float(o["cap_tol"]), int(o["cap_max_iter"]), float(a_cfg["gross_cap"])

    def decide(m, hU):
        T = targets[m]
        base = {"flat": bool(T["flat"]), "flat_reason": T["reason"], "budget_scaled": bool(T["budget_scaled"]),
                "G_t": T["G_t"], "ic_t": T["ic_t"], "beta_dropped": bool(T.get("beta_dropped", False))}
        if T["flat"]:
            base.update({"n_participation_hit": 0, "n_traded_pre_cap": 0, "reproj_traded": 0.0,
                         "overrides": 0, "resid_final": 0.0, "resid_beta_final": 0.0, "gross_excess": 0.0})
            return np.zeros(len(hU)), base
        t, cons, elig = T["t"], T["cons"], T["eligible"]
        w3 = buffer_step(t, hU, rel, abs_, kappa)[0] if use_buffer else t.copy()
        sl = P.sl(m)
        adv = P.adv[sl]
        capd = np.where(np.isfinite(adv) & (adv > 0), pct * adv * days / aum, 0.0)
        traded = np.abs(w3 - hU) > 0
        w4, hit = participation_cap(w3, hU, capd)
        w5, info = final_reproject(w4, hU, capd, cons, elig, min(gross_cap, T["G_t"]), tol, max_iter)
        base.update({"n_participation_hit": int((hit & traded).sum()), "n_traded_pre_cap": int(traded.sum()),
                     "reproj_traded": float(np.abs(w5 - w4).sum()), "overrides": info["overrides"],
                     "participation_excess": info["participation_excess"],
                     "resid_final": cons.max_resid(w5), "resid_beta_final": cons.extra_resid(w5),
                     "gross_excess": max(0.0, float(np.abs(w5).sum()) - float(T["G_t"]))})
        return w5, base
    return decide


def reference_decider(P, books):
    """A Stage 3 variant's own book: +1/|L| on the long set, -1/|S| on the short
    set, rebalanced to that every month. A month the variant skipped holds the
    drifted book (no trade)."""
    by_m = {}
    for d, L, S in books:
        m = int(np.searchsorted(P.dates.values, np.datetime64(pd.Timestamp(d))))
        by_m[m] = (L, S)

    def decide(m, hU):
        if m not in by_m:
            return hU.copy(), {"flat": False, "flat_reason": "", "budget_scaled": False, "skipped": 1}
        L, S = by_m[m]
        ids = P.id_labels[P.id_code[P.sl(m)]]
        inL, inS = np.isin(ids, list(L)), np.isin(ids, list(S))
        w = np.zeros(len(ids))
        if inL.any():
            w[inL] = 1.0 / inL.sum()
        if inS.any():
            w[inS] -= 1.0 / inS.sum()
        return w, {"flat": False, "flat_reason": "", "budget_scaled": False, "skipped": 0}
    return decide


# =============================================================================
# §7 Reporting
# =============================================================================

def _series_block(x, lags, prefix):
    x = pd.Series(x).dropna().astype(float)
    out = {f"{prefix}n_months": int(len(x))}
    if len(x) < 2:
        return out
    ann, vol = x.mean() * 12 * 100, x.std() * np.sqrt(12) * 100
    out.update({f"{prefix}ann_return_pct": float(ann), f"{prefix}ann_vol_pct": float(vol),
                f"{prefix}sharpe": float(_safe_ratio(ann, vol)), f"{prefix}tstat_nw": float(nw_tstat(x, lags))})
    return out


def _drawdown(x):
    """MaxDD % of the compounded series (the start is a peak at 1.0), with the
    episode's peak and trough dates, and the worst 12-month compounded return."""
    x = pd.Series(x).dropna().astype(float)
    if len(x) < 2:
        return {}
    cum = (1 + x).cumprod()
    roll = cum.cummax().clip(lower=1.0)
    dd = cum / roll - 1
    trough = dd.idxmin()
    pre = cum.loc[:trough]
    peak = "inception" if pre.max() <= 1.0 else str(pd.Timestamp(pre.idxmax()).date())
    w12 = (1 + x).rolling(12).apply(np.prod, raw=True) - 1
    out = {"maxdd_pct": float(dd.min() * 100), "maxdd_peak": peak, "maxdd_trough": str(pd.Timestamp(trough).date())}
    if w12.notna().any():
        out["worst_12m_pct"] = float(w12.min() * 100)
        out["worst_12m_end"] = str(pd.Timestamp(w12.idxmin()).date())
    return out


def _annual(x):
    x = pd.Series(x).dropna()
    a = x.groupby(x.index.year).apply(lambda v: (1 + v).prod() - 1) * 100
    return ",".join(f"{y}:{v:.1f}" for y, v in a.items())


def _tier_net(d, k):
    g = d["tier_gross"].apply(lambda v: v[k])
    cst = d["tier_cost"].apply(lambda v: v[k]) + d["tier_borrow"].apply(lambda v: v[k])
    return g, cst


def cut_metrics(d, lags, pre, pipeline=True, newpos=True):
    """The headline's field set on the months of ONE cut only (`d` holds just
    those months). Drawdown and worst 12 months compound from the cut's first
    month with a peak floor of 1.0 at the cut start; a cut with gaps (the
    ex-years cut) compounds over its own months in date order, the excluded
    months skipped."""
    out = {}
    n = len(d)
    for kind in ("gross", "net"):
        out.update(_series_block(d[kind], lags, f"{pre}{kind}_"))
    out.update({f"{pre}net_{k}": v for k, v in _drawdown(d["net"]).items()})
    if "mkt" in d.columns:
        out[f"{pre}net_beta_on_market"] = float(fullwindow_beta(d["net"], d["mkt"])) if n else float("nan")
    nanmean = (lambda x: float(x.mean())) if n else (lambda x: float("nan"))
    out[f"{pre}turnover_oneway_pct"] = nanmean(d["turnover"]) * 100
    for k in ("spread", "impact", "borrow"):
        out[f"{pre}cost_{k}_ann_pct"] = nanmean(d[k]) * 12 * 100
    out[f"{pre}cost_total_ann_pct"] = (out[f"{pre}cost_spread_ann_pct"] + out[f"{pre}cost_impact_ann_pct"]
                                       + out[f"{pre}cost_borrow_ann_pct"])
    for k, t in enumerate(TIERS):
        g, cst = _tier_net(d, k) if n else (pd.Series(dtype=float), pd.Series(dtype=float))
        out.update(_series_block(g - cst, lags, f"{pre}tier_{t}_net_"))
    if newpos:
        out[f"{pre}new_positions_delisting_n"] = int(d["new_pos_delisting_n"].sum()) if n else 0
    if pipeline:
        flat = d["flat"].astype(bool) if n else pd.Series(dtype=bool)
        bs = d["budget_scaled"].astype(bool) if n else pd.Series(dtype=bool)
        out[f"{pre}live_months"] = int((~flat).sum())
        out[f"{pre}flat_months"] = int(flat.sum())
        out[f"{pre}budget_scaled_months_live"] = int((bs & ~flat).sum())
        out[f"{pre}budget_scaled_months_flat"] = int((bs & flat).sum())
        out[f"{pre}gross_budget_mean_live"] = float(d.loc[~flat, "G_t"].mean()) if (~flat).any() else float("nan")
        out[f"{pre}participation_hit_share_pct"] = (float(100 * _safe_ratio(d["n_participation_hit"].sum(),
                                                                            d["n_traded_pre_cap"].sum()))
                                                    if n else float("nan"))
    return out


def cut_masks(index, lcfg, oos_start=None):
    """{prefix: boolean mask} of the reported cuts. With a holdout present the
    ex-years cut is in-window only (months < out_of_sample_start), and
    `cut_inwindow_` / `cut_holdout_` split the path at out_of_sample_start."""
    cuts = lcfg["report"]["regime_cuts"]
    yrs = index.year
    ex = [int(y) for y in cuts["ex_years"]]
    lo, hi = [int(y) for y in cuts["window_2011_2020"]]
    hold = (index >= pd.Timestamp(oos_start)) if oos_start is not None else np.zeros(len(index), bool)
    masks = {"cut_exyears_": ~np.isin(yrs, ex) & ~hold, f"cut_{lo}_{hi}_": (yrs >= lo) & (yrs <= hi) & ~hold}
    if oos_start is not None:
        masks["cut_inwindow_"] = ~hold
        masks["cut_holdout_"] = hold
    return masks


def summarise(rec, lcfg, lags=DEFAULT_NW_LAGS, oos_start=None, pipeline=True):
    """Flat dict of the reported metrics for one (row, AUM) path."""
    rep = lcfg["report"]
    df = pd.DataFrame(rec).set_index("date")
    out = {"n_months": int(len(df)), "book_start": str(df.index.min().date()) if len(df) else "NA",
           "book_end": str(df.index.max().date()) if len(df) else "NA"}
    for kind in ("gross", "net"):
        out.update(_series_block(df[kind], lags, f"{kind}_"))
        out.update({f"{kind}_{k}": v for k, v in _drawdown(df[kind]).items()})
        out[f"annual_{kind}_returns_pct"] = _annual(df[kind])
    live = ~df["flat"].astype(bool)
    out["turnover_oneway_pct"] = float(df["turnover"].mean() * 100)
    out["turnover_oneway_pct_live"] = float(df.loc[live, "turnover"].mean() * 100) if live.any() else float("nan")
    for k in ("spread", "impact", "borrow"):
        out[f"cost_{k}_ann_pct"] = float(df[k].mean() * 12 * 100)
    out["cost_total_ann_pct"] = out["cost_spread_ann_pct"] + out["cost_impact_ann_pct"] + out["cost_borrow_ann_pct"]
    out["exit_sales_total"] = int(df["n_exit_sales"].sum())
    out["avg_gross_book"] = float(df.loc[live, "book_gross"].mean()) if live.any() else 0.0
    out["avg_n_long"] = float(df.loc[live, "n_long"].mean()) if live.any() else 0.0
    out["avg_n_short"] = float(df.loc[live, "n_short"].mean()) if live.any() else 0.0
    out["ret_missing_positions"] = int(df["n_ret_missing"].sum())
    # the realised (ex-post) beta of the book on D4's market M: the OLS slope of
    # the monthly return on M over the book months (and over live months only)
    if "mkt" in df.columns:
        for kind in ("gross", "net"):
            out[f"{kind}_beta_on_market"] = float(fullwindow_beta(df[kind], df["mkt"]))
        out["net_beta_on_market_live"] = float(fullwindow_beta(df.loc[live, "net"], df.loc[live, "mkt"]))
    out["impact_sigma_missing_trades"] = int(df["impact_sigma_missing_trades"].sum())
    if "new_positions_delisting" in (rep.get("diagnostics") or []):
        out["new_positions_delisting_n"] = int(df["new_pos_delisting_n"].sum())
        out["new_positions_delisting_pnl_pct"] = float(df["new_pos_delisting_pnl"].mean() * 12 * 100)
    if pipeline:
        out["reproj_share_of_turnover_pct"] = float(100 * _safe_ratio(df["reproj_traded"].sum(), df["traded"].sum()))
        out["participation_hit_share_pct"] = float(100 * _safe_ratio(df["n_participation_hit"].sum(),
                                                                     df["n_traded_pre_cap"].sum()))
        out["participation_overrides"] = int(df["overrides"].sum())
        out["budget_scaled_months"] = int(df["budget_scaled"].sum())
        out["budget_scaled_pct"] = float(100 * df.loc[live, "budget_scaled"].mean()) if live.any() else float("nan")
        out["flat_months"] = int((~live).sum())
        for reason in ("ic_nonpositive", "no_history_risk", "no_history_ic"):
            out[f"flat_months_{reason}"] = int((df["flat_reason"] == reason).sum())
        out["ic_t_mean"] = float(pd.to_numeric(df["ic_t"], errors="coerce").mean())
        out["gross_budget_mean"] = float(df["G_t"].mean())
        out["gross_budget_mean_live"] = float(df.loc[live, "G_t"].mean()) if live.any() else float("nan")
        out["budget_scaled_months_live"] = int((df["budget_scaled"].astype(bool) & live).sum())
        out["budget_scaled_months_flat"] = int((df["budget_scaled"].astype(bool) & ~live).sum())
        out["max_neutrality_residual"] = float(df["resid_final"].max())
        out["max_beta_residual"] = float(df["resid_beta_final"].max()) if "resid_beta_final" in df else 0.0
        out["beta_constraint_dropped_months"] = (int(df["beta_dropped"].astype(bool).sum())
                                                 if "beta_dropped" in df else 0)
        out["gross_budget_max_excess"] = float(df["gross_excess"].max())
        out["months_gross_exceeds_budget"] = int((df["gross_excess"] > 1e-9).sum())
    else:
        out["months_skipped_by_variant"] = int(df.get("skipped", pd.Series(0)).sum())
    # realised exposures (live months)
    for col in [c for c in df.columns if c in ("exp_size", "exp_vol", "exp_beta") or c.startswith("exp_family_")]:
        out[f"{col}_mean"] = float(pd.to_numeric(df.loc[live, col], errors="coerce").mean())
    # risk model: bias statistic and ex-ante vs realised
    T = int(rep["bias_stat_window_months"])
    sd = pd.to_numeric(df["exante_sd"], errors="coerce")
    zb = (df["gross"] / sd).where(live & (sd > 0))
    bias = zb.rolling(T, min_periods=T).std()
    band = np.sqrt(2.0 / T)
    out["bias_stat_mean"] = float(bias.mean()) if bias.notna().any() else float("nan")
    out["bias_stat_in_band_pct"] = (float(100 * ((bias - 1).abs() <= band)[bias.notna()].mean())
                                    if bias.notna().any() else float("nan"))
    out["exante_vol_ann_pct_mean"] = float(sd[live].mean() * np.sqrt(12) * 100) if live.any() else float("nan")
    out["realised_vol_ann_pct_live"] = (float(df.loc[live, "gross"].std() * np.sqrt(12) * 100)
                                        if live.sum() > 1 else float("nan"))
    # by liquidity tier (contributions)
    for k, t in enumerate(TIERS):
        g = df["tier_gross"].apply(lambda v: v[k])
        cst = df["tier_cost"].apply(lambda v: v[k]) + df["tier_borrow"].apply(lambda v: v[k])
        out.update(_series_block(g, lags, f"tier_{t}_gross_"))
        out.update(_series_block(g - cst, lags, f"tier_{t}_net_"))
        out[f"tier_{t}_cost_ann_pct"] = float(cst.mean() * 12 * 100)
        out[f"tier_{t}_turnover_oneway_pct"] = float(0.5 * df["tier_traded"].apply(lambda v: v[k]).mean() * 100)
        out[f"tier_{t}_avg_n_long"] = float(df.loc[live, "tier_n_long"].apply(lambda v: v[k]).mean()) if live.any() else 0.0
        out[f"tier_{t}_avg_n_short"] = float(df.loc[live, "tier_n_short"].apply(lambda v: v[k]).mean()) if live.any() else 0.0
    # regime cuts: each on its own months only
    out["cut_exyears_years"] = ",".join(str(int(y)) for y in rep["regime_cuts"]["ex_years"])
    newpos = "new_positions_delisting" in (rep.get("diagnostics") or [])
    for pre, mk in cut_masks(df.index, lcfg, oos_start).items():
        out.update(cut_metrics(df.loc[mk], lags, pre, pipeline, newpos))
    return out, df


PATH_COLUMNS = ["gross", "net", "spread", "impact", "borrow", "turnover", "book_gross", "G_t", "flat",
                "flat_reason", "budget_scaled", "n_long", "n_short", "exante_sd", "exp_beta", "mkt"]


def write_paths_csv(paths, path):
    """The monthly path of every (row, AUM): one CSV row per (row, AUM, month),
    floats at full precision (%.17g round-trips exactly). Returns the file's
    sha256, first 12 hex (the block's `paths_sha`)."""
    frames = []
    for (row, aum), df in paths.items():
        d = df.reindex(columns=PATH_COLUMNS).copy()
        if "flat_reason" in d:
            d["flat_reason"] = d["flat_reason"].fillna("")
        d.insert(0, "date", pd.DatetimeIndex(df.index).strftime("%Y-%m-%d"))
        d.insert(0, "aum_usd", float(aum))
        d.insert(0, "row", row)
        frames.append(d.reset_index(drop=True))
    out = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=["row", "aum_usd", "date"] + PATH_COLUMNS)
    text = out.to_csv(index=False, float_format="%.17g", lineterminator="\n")
    Path(path).write_bytes(text.encode("utf-8"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def row_specs(lcfg):
    """Every reported row, in report order, from the config alone: the layer,
    the sensitivity re-runs (each eta, the fixed tier half-spread, the
    execution fraction, the tiered borrow), then
    `report.reference_rows` in their declared order."""
    c, rep = lcfg["costs"], lcfg["report"]
    eta0 = float(c["impact_eta"])
    fixed = c["sensitivity"]["fixed_half_spread_bp"]
    con = str(lcfg["optimiser"]["constraints"])
    if con not in CONSTRAINTS:
        raise LayerRefused(f"unknown optimiser.constraints {con!r}; declared: {', '.join(CONSTRAINTS)}")
    lay = dict(kind="layer", constraint=con, buffer=True, eta=eta0, hs="measured", note="",
               borrow="flat", trade_frac=1.0)
    spec = {"layer": dict(lay)}
    for e in c["sensitivity"]["impact_eta"]:
        spec[f"layer_eta_{float(e):g}"] = dict(lay, eta=float(e), note=f"cost sensitivity: impact eta={float(e):g}")
    spec["layer_fixed_tier_spread"] = dict(lay, hs="fixed", note="cost sensitivity: fixed tier half-spread "
                                           + "/".join(f"{t} {float(v):g}bp" for t, v in fixed.items())
                                           + ", understates 1999-2007")
    f = float(c["sensitivity"]["trade_return_fraction"])
    spec["layer_exec_half_month" if f == 0.5 else f"layer_exec_frac_{f:g}"] = dict(
        lay, trade_frac=f, note=f"execution sensitivity: traded dw earns {f:g} of monthly_ret(t) "
                                "(base: trades at the signal-date close, as Stages 1-3)")
    tb = c["sensitivity"]["borrow_bp_per_year_by_tier"]
    spec["layer_tiered_borrow"] = dict(lay, borrow="tiered", note="borrow sensitivity: "
                                       + "/".join(f"{t} {float(v):g}" for t, v in tb.items())
                                       + " bp/yr by liq_tier, other tiers at the largest")
    known = {"layer_no_buffer": dict(lay, buffer=False, note="the layer book with the buffer off"),
             "layer_no_beta_constraint": dict(lay, constraint="sector_neutral",
                                              note="the market-beta constraint off (sector-neutral only)"),
             "layer_dollar_neutral_only": dict(lay, constraint="dollar_neutral",
                                               note="sector and beta neutrality off (dollar-neutral only)"),
             "equal_rank_decile": dict(kind="ref", eta=eta0, hs="measured", borrow="flat", trade_frac=1.0,
                                       note="Stage 3 reference book (D10-D1 equal weight), same cost model"),
             "buffered": dict(kind="ref", eta=eta0, hs="measured", borrow="flat", trade_frac=1.0,
                              note="Stage 3 buffered book, same cost model")}
    for r in rep["reference_rows"]:
        if str(r) not in known:
            raise LayerRefused(f"unknown report.reference_rows entry {r!r}")
        spec[str(r)] = known[str(r)]
    return spec


def aum_tag(aum):
    return f"{aum / 1e6:g}M"


def run_layer(audit, metas, cfg, lcfg, composite_sha, oos_start=None, log=print, rows=None, spread=None):
    """Every row at every AUM. Returns [(row, aum, stats)] in AUM x row_specs()
    order, plus a `meta` dict (layer-level diagnostics). `spread`: the
    harness-built Corwin-Schultz series (data_layer.load_or_build_cs_spread),
    attached to the audit frame here; without it the frame must already carry
    the spread column."""
    from harness import portfolio as PF

    check_composite(lcfg, composite_sha)
    lags = int(cfg["statistics"]["newey_west_lags"])
    c, rep = lcfg["costs"], lcfg["report"]
    if spread is not None:
        audit = attach_spread(audit, spread, SPREAD_COLUMNS[str(c["half_spread"])])
    P = LayerPanel(audit, lcfg, metas, group_col=rank_group_col(cfg))
    log(f"    panel: {P.M} months, {P.N} IDs, {len(P.df)} ID-months; spread column {P.spread_col} "
        f"({100 * float(np.isfinite(P.spread).mean()):.1f}% of ID-months measured)")
    R = build_risk_model(P, lcfg, log=log)
    ic_t, _ = ic_forecast(P, lcfg)
    start = pd.Timestamp(str(lcfg["window"]["book_start"]) + "-01")
    ref_start = pd.Timestamp(str(lcfg["window"]["reference_rows_start"]) + "-01")
    book_months = [m for m in range(P.M) if P.dates[m] >= start]
    ref_months = [m for m in range(P.M) if P.dates[m] >= ref_start]
    spec = row_specs(lcfg)
    run_rows = rows or list(spec)
    default_con = str(lcfg["optimiser"]["constraints"])
    cons_used = {default_con} | {spec[r]["constraint"] for r in run_rows if spec[r]["kind"] == "layer"}
    targets = {k: {m: build_target(P, R, m, ic_t[m], lcfg, k) for m in book_months}
               for k in sorted(cons_used)}
    fam_memo = {}

    def fam_cache(m):
        if m not in fam_memo:
            fam_memo[m] = P.family_scores(m)
        return fam_memo[m]

    eta0 = float(c["impact_eta"])
    books = {}
    ref_rows = [str(r) for r in rep["reference_rows"]]
    for name in ref_rows:
        if name in ("equal_rank_decile", "buffered"):
            bk = []
            getattr(PF, name)(audit, metas, cfg, books=bk)
            books[name] = bk
    leak = P.sector_leak() if "sector_leak" in (rep.get("diagnostics") or []) else {}
    labels = {k: v.pop("note") for k, v in spec.items()}
    out, paths = [], {}
    for aum in [float(a) for a in rep["aum_usd"]]:
        for row in run_rows:
            s = spec[row]
            if s["kind"] == "layer":
                dec = layer_decider(P, targets[s["constraint"]], lcfg, aum, use_buffer=s["buffer"])
                rec = run_book(P, R, lcfg, book_months, aum, dec, s["eta"], s["hs"], fam_cache,
                               s["borrow"], s["trade_frac"])
            else:
                rec = run_book(P, R, lcfg, ref_months, aum, reference_decider(P, books[row]),
                               s["eta"], s["hs"], fam_cache, s["borrow"], s["trade_frac"])
            st, df = summarise(rec, lcfg, lags, oos_start, pipeline=(s["kind"] == "layer"))
            st.update({"row": row, "aum_usd": aum, "impact_eta": s["eta"], "half_spread_mode": s["hs"],
                       "row_note": labels.get(row, ""),
                       "constraint": s.get("constraint", "stage3_equal_weight"),
                       "buffer": str(s.get("buffer", "n/a")), "borrow_mode": s["borrow"],
                       "trade_return_fraction": s["trade_frac"]})
            st.update(leak)
            out.append((row, aum, st))
            paths[(row, aum)] = df
    first_live = next((m for m in book_months if not targets[default_con][m]["flat"]), None)
    own = [P.market_betas(m)[1] / max(P.offsets[m + 1] - P.offsets[m], 1) for m in book_months]
    meta = {"panel_months": P.M, "panel_ids": P.N, "sector_groups": P.G,
            "sector_group_labels": "|".join(P.sector_labels),
            "first_live_month": str(P.dates[first_live].date()) if first_live is not None else "none",
            "risk_first_ready": next((str(P.dates[m].date()) for m in range(P.M) if R[m].ready), "never"),
            "vol_factor_first_month": next((str(P.dates[m].date()) for m in range(P.M) if R[m].vol_ok), "never"),
            "constraints": default_con,
            "market_beta_first_month": next((str(P.dates[m].date()) for m in range(P.M)
                                             if P.market_betas(m)[0] is not None), "never"),
            "market_beta_own_estimate_pct": float(100 * np.mean(own)) if own else float("nan"),
            "spread_measured_pct": float(100 * np.isfinite(P.spread).mean()) if len(P.spread) else float("nan"),
            "paths": paths, **leak}
    return out, meta


def print_layer_table(results, log=print):
    """One compact table per AUM."""
    aums = sorted({a for _, a, _ in results})
    for aum in aums:
        log(f"\n  --- Construction layer at AUM ${aum / 1e9:g}B (net of the cost model; gross in brackets) ---")
        log(f"  {'row':<27}{'net ann%':>9}{'(gross)':>9}{'net SR':>8}{'net t':>7}{'netMaxDD':>9}"
            f"{'turn%':>7}{'cost%':>7}{'nL/nS':>11}{'flat':>5}{'budScl':>7}{'partHit%':>9}{'exAvol':>7}{'bias':>6}"
            f"{'betaPost':>9}")
        for row, a, st in results:
            if a != aum:
                continue
            g = lambda k: st.get(k, float("nan"))  # noqa: E731
            log(f"  {row:<27}{g('net_ann_return_pct'):>9.2f}{g('gross_ann_return_pct'):>9.2f}"
                f"{g('net_sharpe'):>8.2f}{g('net_tstat_nw'):>7.2f}{g('net_maxdd_pct'):>9.1f}"
                f"{g('turnover_oneway_pct'):>7.1f}{g('cost_total_ann_pct'):>7.2f}"
                f"{g('avg_n_long'):>5.0f}/{g('avg_n_short'):<5.0f}{st.get('flat_months', 0):>5}"
                f"{st.get('budget_scaled_months_live', 0):>7}{g('participation_hit_share_pct'):>9.1f}"
                f"{g('exante_vol_ann_pct_mean'):>7.2f}"
                f"{g('bias_stat_mean'):>6.2f}{g('net_beta_on_market'):>9.3f}")
    log("  budScl = live months with the gross budget G_t below the cap; partHit% = share of traded "
        "names whose trade the participation cap cut (layer rows only); betaPost = realised beta of the "
        "net monthly return on the universe's cap-weighted return (D4's M)")
