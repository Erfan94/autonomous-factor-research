"""A synthetic audit frame shaped like run_test.score_arm's output, for the
construction-layer tests and the runtime estimate. Monthly schedule as in
data_layer: DATE == RET_END(t) == SIGNAL_ASOF(t+1). Each name loads on the
market with its own beta (drawn from a separate stream, so the rest of the
frame's draws are unchanged), and the frame carries `cs_spread`, the column
the harness-built Corwin-Schultz series fills in a real run (attach_spread);
the SpreadProxy leg is an ordinary synthetic leg, not the cost model's input."""
import numpy as np
import pandas as pd

from harness.analytics import assign_composite_decile

SECTORS = ["Basic Materials", "Communication Services", "Consumer Cyclical", "Consumer Defensive",
           "Energy", "Financial Services", "Healthcare", "Industrials", "Real Estate",
           "Technology", "Utilities"]
METAS = [{"name": "A", "col": "f_a", "ascending": True, "winsorize": True, "weight": 1.0, "family": "fa"},
         {"name": "B", "col": "f_b", "ascending": True, "winsorize": True, "weight": 1.0, "family": "fb"},
         {"name": "SpreadProxy", "col": "f_bidaskspreadflip", "ascending": False, "winsorize": True,
          "weight": 1.0, "family": "trading_activity"}]


def make_audit(n_names=300, n_months=48, start="1999-01-01", seed=0, churn=0.02, delist=0.002,
               signal=0.02):
    rng = np.random.default_rng(seed)
    mkt_beta = np.random.default_rng(seed + 7919).uniform(0.4, 1.6, n_names * 3)
    dates = pd.date_range(start, periods=n_months, freq="BME")
    sig_asof = [dates[0] - pd.offsets.BMonthEnd(1)] + list(dates[:-1])
    pool = n_names * 3
    sector = np.array(SECTORS + [None])[rng.integers(0, len(SECTORS) + 1, pool)]
    beta_size = rng.normal(size=pool)
    mcap = np.exp(rng.normal(21, 1.5, pool))
    vol = np.exp(rng.normal(np.log(0.09), 0.35, pool))
    a = rng.normal(size=pool)
    b = rng.normal(size=pool)
    live = np.zeros(pool, bool)
    live[:n_names] = True
    nxt = n_names
    frames = []
    for t, d in enumerate(dates):
        # churn: some names leave, fresh names enter
        leave = live & (rng.random(pool) < churn)
        live &= ~leave
        k = int(leave.sum())
        if nxt + k <= pool:
            live[nxt:nxt + k] = True
            nxt += k
        idx = np.flatnonzero(live)
        n = len(idx)
        a[idx] = 0.8 * a[idx] + 0.6 * rng.normal(size=n)
        b[idx] = 0.8 * b[idx] + 0.6 * rng.normal(size=n)
        mkt = rng.normal(0.008, 0.045)
        fsize = rng.normal(0, 0.02)
        ret = mkt * mkt_beta[idx] + fsize * beta_size[idx] + signal * a[idx] + vol[idx] * rng.normal(size=n)
        kind = np.array(["full"] * n, dtype=object)
        dl = rng.random(n) < delist
        kind[dl] = "partial_delisted_performance"
        ret[dl] = (1 + ret[dl]) * 0.7 - 1
        spread = np.exp(rng.normal(np.log(0.004), 0.6, n))
        spread[rng.random(n) < 0.01] = np.nan               # ~1% unmeasured (the real series: 0.06%)
        adv = mcap[idx] * np.exp(rng.normal(np.log(0.004), 0.5, n))
        pct = pd.Series(adv).rank(pct=True).values * 100
        tier = np.where(pct >= 80, "MEGA", np.where(pct >= 50, "MID", "SMALL"))
        df = pd.DataFrame({"ID": [f"S{i:05d}" for i in idx], "DATE": d, "monthly_ret": ret, "ret_kind": kind,
                           "RET_START": d - pd.offsets.BMonthBegin(1), "RET_END": d,
                           "SIGNAL_ASOF": sig_asof[t], "region": "US", "liq_tier": tier,
                           "sector": sector[idx], "industry_group": "x",
                           "mkt_cap_usd": mcap[idx], "adv_usd": adv,
                           "f_a": a[idx], "f_b": b[idx], "f_bidaskspreadflip": spread, "cs_spread": spread})
        frames.append(assign_composite_decile(df, METAS, None, 10))
        # delisted names leave for good
        live[idx[dl]] = False
        mcap[idx] *= np.exp(ret * 0.5)
    return pd.concat(frames, ignore_index=True)
