"""
Stage 3 — portfolio construction on the ACCEPTED composite.

Stage 1 and Stage 2 decide which signals carry information. This module
decides nothing about a candidate: it takes the live composite's audit frame
and reports what a set of pre-declared constructions make of it, gross and
after cost, overall and by liquidity tier. Its output goes on the manifest
beside the search construction's numbers so the model is described the way a
desk would trade it, not only the way the search measured it.

Every variant is point-in-time: a weight, a leverage or a book membership at
month t uses information up to the signal date of month t and nothing later.
Every variant's long-short is then HEDGED exactly as the search construction
is (config `market_hedge`: ex-ante trailing beta on the universe's
cap-weighted return), and reported with its raw series and beta beside it.
Variants are listed in config (`construction.variants`); the list and every
parameter move CONFIG_SHA.

  equal_rank_decile   the search construction: the FAMILY blend (1/F across
                      families, equal within, two-level and renormalised —
                      harness.analytics.blend_family_ranks), D10 minus D1,
                      equal-weight names. The reference.
  tier_neutral        deciles cut WITHIN each liquidity tier, the long-short
                      averaged across tiers. Removes the small-cap tilt that
                      an all-universe decile carries; the capacity-aware view.
  icir_weighted       legs weighted by their trailing ICIR (window and floor
                      from config), estimated on months strictly before t,
                      FLAT across legs (a family carries the weight of its
                      members' ICIRs). Equal weights until the window is
                      long enough. Unshrunk by design: a diagnostic of how
                      much a naive learned weighting would move the result.
  buffered            hysteresis: a name enters the long book in the top
                      decile and stays while it remains in the top
                      `buffer_pct`; mirror for the short book. Turnover control.
  vol_targeted        the reference long-short scaled to a target volatility
                      using trailing realised vol, leverage capped.
"""

import numpy as np
import pandas as pd

from harness.analytics import (MIN_OBS_BUCKET_LS, DEFAULT_NW_LAGS, _safe_ratio, blend_ranks,
                               compute_factor_ranks, cut_deciles, fullwindow_beta, hedge_long_short,
                               hedge_params, ls_stats_of, nw_tstat, rank_group_col, rank_one_factor,
                               regime_diagnostics, regime_params, universe_market_return)


# =============================================================================
# Shared: statistics of a long-short series with book turnover
# =============================================================================

def ls_summary(ls, turnover_long_pct, turnover_short_pct, nw_lags=DEFAULT_NW_LAGS):
    """GROSS statistics of a long-short series plus the book turnover that a
    reader would need to price it. No cost is charged anywhere in this
    project; implementability is reported, never decided on."""
    ls = pd.Series(ls).dropna().astype(float)
    n = int(len(ls))
    if n < 2:
        return {"n_months": n}
    mean, std = ls.mean(), ls.std()
    ann_ret, ann_vol = mean * 12 * 100, std * np.sqrt(12) * 100
    sharpe = float(_safe_ratio(ann_ret, ann_vol))
    cum = (1 + ls).cumprod()
    roll = cum.cummax().clip(lower=1.0)
    maxdd = float(((cum - roll) / roll).min() * 100)
    out = {"n_months": n, "ls_ann_return_pct": float(ann_ret), "ls_ann_vol_pct": float(ann_vol),
           "ls_sharpe": sharpe, "ls_tstat_nw": float(nw_tstat(ls, nw_lags)),
           "ls_maxdd_pct": maxdd, "ls_calmar": float(_safe_ratio(ann_ret, abs(maxdd))),
           "ls_hit_rate_pct": float((ls > 0).mean() * 100),
           "turnover_long_pct": float(turnover_long_pct), "turnover_short_pct": float(turnover_short_pct)}
    worst12 = (1 + ls).rolling(12).apply(np.prod, raw=True) - 1
    out["worst_12m_pct"] = float(worst12.min() * 100) if worst12.notna().any() else float("nan")
    # Annual returns as a compact string, for the summary and the manifest.
    ann = ls.resample("YE").apply(lambda x: (1 + x).prod() - 1) * 100
    out["annual_returns_pct"] = ",".join(f"{y}:{v:.1f}" for y, v in zip(ann.index.year, ann.values))
    out["ls_series"] = ls
    return out


def _book_turnover(books):
    """Mean fraction of a book replaced month over month. `books` is a list of
    (date, set_of_ids) in date order."""
    rec = []
    for (d0, b0), (d1, b1) in zip(books[:-1], books[1:]):
        if b0:
            rec.append(len(b0 - b1) / len(b0))
    return float(np.mean(rec)) * 100 if rec else float("nan")


def _by_month(audit):
    df = audit.copy()
    df["DATE"] = pd.to_datetime(df["DATE"])
    return [(d, g) for d, g in df.groupby("DATE", sort=True)]


# =============================================================================
# Variants
# =============================================================================

def equal_rank_decile(audit, metas, cfg, books=None):
    """`books`, when a list, receives (date, long_ids, short_ids) for every month
    the series has: the per-month book, so the construction layer can charge
    the same cost model on this variant's own trades. Numbers are unchanged."""
    n_dec = int(cfg["rebalance"]["n_deciles"])
    ls, longs, shorts = [], [], []
    for d, g in _by_month(audit):
        g = g.dropna(subset=["DECILE", "monthly_ret"])
        top, bot = g[g["DECILE"] == n_dec], g[g["DECILE"] == 1]
        if len(top) == 0 or len(bot) == 0:
            continue
        ls.append((d, top["monthly_ret"].mean() - bot["monthly_ret"].mean()))
        longs.append((d, set(top["ID"]))); shorts.append((d, set(bot["ID"])))
        if books is not None:
            books.append((d, set(top["ID"]), set(bot["ID"])))
    s = pd.Series(dict(ls)).sort_index()
    return s, _book_turnover(longs), _book_turnover(shorts), "family blend"


def tier_neutral(audit, metas, cfg):
    n_dec = int(cfg["rebalance"]["n_deciles"])
    ls, longs, shorts = [], [], []
    for d, g in _by_month(audit):
        g = g.dropna(subset=["COMPOSITE_SCORE", "monthly_ret", "liq_tier"])
        parts, L, S = [], set(), set()
        for tier, sub in g.groupby("liq_tier"):
            if len(sub) < MIN_OBS_BUCKET_LS:
                continue
            dec = cut_deciles(sub["COMPOSITE_SCORE"], n_dec)
            top, bot = sub[dec == dec.max()], sub[dec == dec.min()]
            if len(top) and len(bot) and dec.max() != dec.min():
                parts.append(top["monthly_ret"].mean() - bot["monthly_ret"].mean())
                L |= set(top["ID"]); S |= set(bot["ID"])
        if parts:
            ls.append((d, float(np.mean(parts))))
            longs.append((d, L)); shorts.append((d, S))
    s = pd.Series(dict(ls)).sort_index()
    return s, _book_turnover(longs), _book_turnover(shorts), "family blend, tier-neutral"


def icir_weighted(audit, metas, cfg):
    c = cfg["construction"]
    L, min_m = int(c["icir_lookback_months"]), int(c["icir_min_months"])
    n_dec = int(cfg["rebalance"]["n_deciles"])
    months = _by_month(audit)
    # Per-leg IC series, computed once. Leg rank vs forward return, per month.
    leg_ic = {m["name"]: [] for m in metas}
    ranks_by_month = []
    for d, g in months:
        r = compute_factor_ranks(g, metas, group_col=rank_group_col(cfg))
        ranks_by_month.append((d, g, pd.DataFrame(r, index=g.index)))
        for m in metas:
            al = pd.concat([r[m["name"]], g["monthly_ret"]], axis=1).dropna()
            leg_ic[m["name"]].append(al.iloc[:, 0].corr(al.iloc[:, 1], method="spearman")
                                     if len(al) >= 10 else np.nan)
    ic_df = pd.DataFrame(leg_ic, index=[d for d, _, _ in ranks_by_month])
    ls, longs, shorts, wlog = [], [], [], []
    for i, (d, g, rdf) in enumerate(ranks_by_month):
        hist = ic_df.iloc[max(0, i - L):i]          # strictly before month i
        if len(hist.dropna(how="all")) >= min_m:
            w = (hist.mean() / hist.std()).clip(lower=0.0).fillna(0.0)
            if w.sum() <= 0:
                w = pd.Series(1.0, index=ic_df.columns)
        else:
            w = pd.Series(1.0, index=ic_df.columns)
        w = w / w.sum()
        wlog.append(w)
        score = blend_ranks(rdf, w.to_dict())
        dec = cut_deciles(score, n_dec)
        ok = g["monthly_ret"].notna()
        top, bot = g[(dec == n_dec) & ok], g[(dec == 1) & ok]
        if len(top) and len(bot):
            ls.append((d, top["monthly_ret"].mean() - bot["monthly_ret"].mean()))
            longs.append((d, set(top["ID"]))); shorts.append((d, set(bot["ID"])))
    s = pd.Series(dict(ls)).sort_index()
    avg_w = pd.concat(wlog, axis=1).mean(axis=1) if wlog else pd.Series(dtype=float)
    desc = ";".join(f"{k}={v:.3f}" for k, v in avg_w.items())
    return s, _book_turnover(longs), _book_turnover(shorts), desc


def buffered(audit, metas, cfg, books=None):
    """`books` as in equal_rank_decile: (date, long_ids, short_ids) per month."""
    c = cfg["construction"]
    n_dec = int(cfg["rebalance"]["n_deciles"])
    enter = 1.0 - 1.0 / n_dec                 # top decile enters
    stay = 1.0 - float(c["buffer_pct"]) / 100.0
    ls, longs, shorts = [], [], []
    L, S = set(), set()
    for d, g in _by_month(audit):
        g = g.dropna(subset=["COMPOSITE_SCORE", "monthly_ret"])
        if len(g) < n_dec * 5:
            continue
        p = g["COMPOSITE_SCORE"].rank(pct=True, method="average")
        ids = g["ID"]
        top_enter, top_stay = set(ids[p >= enter]), set(ids[p >= stay])
        bot_enter, bot_stay = set(ids[p <= 1 - enter]), set(ids[p <= 1 - stay])
        L = (L & top_stay) | top_enter
        S = (S & bot_stay) | bot_enter
        rl = g[ids.isin(L)]["monthly_ret"].mean()
        rs = g[ids.isin(S)]["monthly_ret"].mean()
        if pd.notna(rl) and pd.notna(rs):
            ls.append((d, rl - rs))
            longs.append((d, set(L))); shorts.append((d, set(S)))
            if books is not None:
                books.append((d, set(L), set(S)))
        # names that left the universe leave the book
        L, S = L & set(ids), S & set(ids)
    s = pd.Series(dict(ls)).sort_index()
    return s, _book_turnover(longs), _book_turnover(shorts), f"buffer {c['buffer_pct']}%"


def vol_targeted(audit, metas, cfg, reference=None):
    c = cfg["construction"]
    target = float(c["vol_target_pct"]) / 100.0
    L, cap = int(c["vol_lookback_months"]), float(c["max_leverage"])
    ref, tl, ts, _ = reference if reference is not None else equal_rank_decile(audit, metas, cfg)
    ref = ref.sort_index()
    realised = ref.shift(1).rolling(L, min_periods=max(6, L // 2)).std() * np.sqrt(12)
    lev = (target / realised).clip(upper=cap).fillna(1.0)
    s = ref * lev
    # turnover scales with the book; leverage changes add a small amount ignored here
    return s, tl, ts, f"target {c['vol_target_pct']}% vol, cap {cap}x, mean lev {lev.mean():.2f}"


VARIANTS = {
    "equal_rank_decile": equal_rank_decile,
    "tier_neutral": tier_neutral,
    "icir_weighted": icir_weighted,
    "buffered": buffered,
    "vol_targeted": vol_targeted,
}


def run_construction(audit, metas, cfg, log=print):
    """Run every configured variant; return [(variant, stats_dict)]."""
    c = cfg["construction"]
    lags = int(cfg["statistics"]["newey_west_lags"])
    hedge, reg = hedge_params(cfg), regime_params(cfg)
    mkt = universe_market_return(audit)
    out, reference = [], None
    for name in c["variants"]:
        fn = VARIANTS[name]
        if name == "vol_targeted":
            s, tl, ts, desc = fn(audit, metas, cfg, reference)
        else:
            s, tl, ts, desc = fn(audit, metas, cfg)
        if name == "equal_rank_decile":
            reference = (s, tl, ts, desc)          # raw: vol targeting scales the raw book
        s = pd.Series(s).astype(float)
        if hedge and len(s):
            sh, beta = hedge_long_short(s, mkt, hedge["beta_window_months"], hedge["beta_min_months"])
        else:
            sh, beta = s, pd.Series(0.0, index=s.index)
        st = ls_summary(sh, tl, ts, lags)
        st["construction_weights"] = desc
        if st.get("n_months", 0) >= 2:
            raw_sharpe, raw_dd = ls_stats_of(s)
            st.update({"ls_raw_sharpe": float(raw_sharpe), "ls_raw_ann_return_pct": float(s.mean() * 1200),
                       "ls_raw_maxdd_pct": float(raw_dd),
                       "ls_beta_mean": float(beta.reindex(sh.dropna().index).mean()),
                       "ls_beta_fullwindow": float(fullwindow_beta(s, mkt)) if len(mkt) else float("nan"),
                       "hedge_on": str(bool(hedge))})
            st.update(regime_diagnostics(sh, mkt if len(mkt) else None,
                                         reg["ex_regime_top_years"], reg["market_state_lookback_months"]))
        out.append((name, st))
    log("\n  --- Stage 3: portfolio construction on the composite (GROSS, "
        + ("hedged; raw Sharpe and beta beside" if hedge else "raw") + ") ---")
    log(f"  {'variant':<20}{'Sharpe':>8}{'LS t NW':>9}{'ann%':>8}{'vol%':>7}{'MaxDD':>8}{'worst12m':>10}{'turn L/S':>12}"
        f"{'months':>8}{'raw Sh':>8}{'beta':>7}{'exReg':>7}")
    for name, st in out:
        if st.get("n_months", 0) < 2:
            log(f"  {name:<20}  (no months)")
            continue
        log(f"  {name:<20}{st['ls_sharpe']:>8.3f}{st['ls_tstat_nw']:>9.2f}{st['ls_ann_return_pct']:>8.2f}"
            f"{st['ls_ann_vol_pct']:>7.2f}{st['ls_maxdd_pct']:>8.1f}{st['worst_12m_pct']:>10.1f}"
            f"{st['turnover_long_pct']:>6.1f}/{st['turnover_short_pct']:<5.1f}{st['n_months']:>8}"
            f"{st['ls_raw_sharpe']:>8.3f}{st['ls_beta_fullwindow']:>+7.2f}{st['ls_sharpe_ex_top_years']:>7.2f}")
    for name, st in out:
        if st.get("construction_weights"):
            log(f"    {name}: {st['construction_weights']}")
    return out
