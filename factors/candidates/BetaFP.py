"""
BetaFP — Frazzini-Pedersen beta: the correlation of 3-day stock and market
returns over five years times the ratio of one-year daily volatilities.

OSAP: BetaFP, Frazzini and Pedersen 2014 (Journal of Financial Economics).
Predicted sign: + (SignalDoc Sign = 1.0, high BetaFP on the long side).
Spec: osap_source/cache/b4e911e6/BetaFP/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  Stock log return  l_t = log(SEP.closeadj_t / SEP.closeadj_{t-1}) on the
  stock's own previous row. Market log return m_t = log1p(market_daily "vw")
  on the same dates (rows kept only on market trading days). Then, at the
  signal date, over the stock's OWN rows:
    sigma_i = std(l) over the last 252 rows (>= 120 valid), sigma_m = std(m)
              over the same 252 rows (>= 120 valid);
    Ri3 = l + l[-1 row] + l[-2 rows], Rm3 likewise (overlapping 3-day sums);
    over the last 1260 rows (>= 500 valid pairs):
      corr = (mean(Ri3*Rm3) - mean(Ri3)*mean(Rm3)) / (std(Ri3) * std(Rm3))
    BetaFP = sqrt(corr^2) * sigma_i / sigma_m   (>= 0 by construction: a
    negatively correlated stock gets a positive value, as in OSAP).
  Only the last value is needed, so each month is computed from the trailing
  rows with no cross-month state. The market series starts 1998-12-02, so
  ctx.market_daily is called with min_days=500: months before about 2000-11
  return an empty market and are UNSCORABLE (null), never thin. The harness
  history gate (history_months=24) does not bind before then; the data does.
  About 8% of decision months (1999-01 .. ~2000-10) are data-null, and
  2000-11 .. 2001 coverage is below the steady state.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? sigma_i = 0 and a constant
  Ri3 give 0/0, so NaN, not 0. No value sits at 0 or at any single number.
  What share of the universe does nothing? ~0%; stale pricing lowers the
  vol but leaves a continuous value. The null share is the recent-IPO tail
  (< 500 valid 3-day rows, about 24 months) and the pre-2000-11 market gap.
  Tie handling: null. sd <= 0 or a non-finite value is nulled, never
  floored; `blend_ranks` renormalises over the legs that remain.

DEVIATIONS FROM OSAP:
  - crsp.ret -> SEP.closeadj day-over-day ratio on the stock's own previous
    row. Total return on today's adjustment basis; no delisting return (OSAP
    uses ret only here); stock returns untrimmed, as in OSAP. A row with
    closeadj <= 0 or null is dropped before the ratio is taken.
  - mktrf -> MonthContext.market_daily (raw all-stock cap-weighted, prior-day
    weights, causal bad-print guards, no dlret, trading-gap returns excluded),
    not Ken French's excess return. rf is not in the snapshot; OSAP's stock
    side is raw total return and its market side is excess, so this differs
    from OSAP by rf (a near-constant of ~0-2bp/day) in sigma_m and corr.
  - The market returns are constrained to 1998-12-02 onward (see above).
  - The value is the one at signal_asof (last trading day of the month), which
    is OSAP's "last finite BetaFP of the month" for a name trading that day.
    A name whose last row is earlier is scored on its own last window.
  - Windows count the stock's own rows; rolling moments are computed over the
    trailing window of its rows only at the signal date (std ddof=1, covariance
    from population moments, as OSAP).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef

_DAYS_BACK = 1900          # ~1260 trading rows plus the two shifted rows
_W_CORR = 1260
_MIN_CORR = 500
_W_VOL = 252
_MIN_VOL = 120
_MIN_MKT_DAYS = 500


def _compute(ctx):
    mkt = ctx.market_daily(_DAYS_BACK, min_days=_MIN_MKT_DAYS)
    if mkt is None or len(mkt) == 0:
        return pd.Series(dtype=float)          # unscorable month: market too short
    mkt = mkt.astype(float)
    mkt = mkt[np.isfinite(mkt) & (mkt > -1.0)]
    lm = np.log1p(mkt)
    lm.index = pd.DatetimeIndex(lm.index)

    d = ctx.daily("SEP", ["closeadj"], _DAYS_BACK)
    if d is None or len(d) == 0:
        return pd.Series(dtype=float)
    d = d[["ID", "date", "closeadj"]].copy()
    d["closeadj"] = d["closeadj"].astype(float)
    d = d[d["closeadj"] > 0]
    d = d.sort_values(["ID", "date"], kind="mergesort").reset_index(drop=True)

    g = d.groupby("ID", sort=False)
    d["l"] = np.log(d["closeadj"] / g["closeadj"].shift(1))     # own previous row
    d = d[d["date"].isin(lm.index)].copy()                      # inner join with market dates
    d["m"] = d["date"].map(lm).astype(float)
    d.loc[~np.isfinite(d["l"]), "l"] = np.nan

    g = d.groupby("ID", sort=False)
    d["ti"] = d["l"] + g["l"].shift(1) + g["l"].shift(2)        # row shifts within the stock
    d["tm"] = d["m"] + g["m"].shift(1) + g["m"].shift(2)

    # 252-row vol window
    v = d.groupby("ID", sort=False).tail(_W_VOL)
    gv = v.groupby("ID", sort=False)
    n_l = gv["l"].count()
    n_m = gv["m"].count()
    sd_i = gv["l"].std(ddof=1).where(n_l >= _MIN_VOL)
    sd_m = gv["m"].std(ddof=1).where(n_m >= _MIN_VOL)

    # 1260-row window of overlapping 3-day sums (pairs valid together)
    w = d.groupby("ID", sort=False).tail(_W_CORR)
    ok = np.isfinite(w["ti"]) & np.isfinite(w["tm"])
    w = w.loc[ok, ["ID", "ti", "tm"]].copy()
    w["ii"] = w["ti"] * w["ti"]
    w["mm"] = w["tm"] * w["tm"]
    w["im"] = w["ti"] * w["tm"]
    s = w.groupby("ID", sort=False).agg(
        n=("ti", "size"), si=("ti", "sum"), sm=("tm", "sum"),
        sii=("ii", "sum"), smm=("mm", "sum"), sim=("im", "sum"),
    )
    s = s[s["n"] >= _MIN_CORR]
    n = s["n"].astype(float)
    mi, mm_ = s["si"] / n, s["sm"] / n
    cov = s["sim"] / n - mi * mm_
    var_i = (s["sii"] - n * mi * mi) / (n - 1.0)
    var_m = (s["smm"] - n * mm_ * mm_) / (n - 1.0)
    sd_i3 = np.sqrt(var_i.where(var_i > 0))
    sd_m3 = np.sqrt(var_m.where(var_m > 0))
    r2 = (cov / (sd_i3 * sd_m3)) ** 2

    ratio = sd_i.where(sd_i > 0) / sd_m.where(sd_m > 0)
    out = np.sqrt(r2.abs()) * ratio.reindex(r2.index)
    out = out.replace([np.inf, -np.inf], np.nan).dropna()
    return out.astype(float)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="BetaFP",
    col="f_betafp",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: high BetaFP on the long side
    weight=1.0,
    inputs=("SEP.closeadj", "DAILY.marketcap"),
    osap_acronym="BetaFP",
    source="Frazzini and Pedersen 2014 (Journal of Financial Economics)",
    lookback_months=60,             # the 1260-row (5-year) correlation window
    history_months=24,              # >= 500 valid overlapping 3-day rows
    notes="sqrt(R2 of 3-day log returns, 1260 rows) x sd252(stock) / sd252(market); raw market, no rf; unscorable before ~2000-11",
    field_mappings=(
        ("crsp.ret", "SEP.closeadj day-over-day ratio",
         "log return on the stock's own previous row; no delisting return; today's adjustment basis; stock returns untrimmed as in OSAP"),
        ("ff.mktrf", "MonthContext.market_daily('vw')",
         "raw all-stock cap-weighted return, not Fama-French excess; starts 1998-12-02, min_days=500 so months before ~2000-11 are null"),
        ("ff.rf", "none",
         "not in the snapshot; OSAP stock side is raw so only the market side differs by rf (~0-2bp/day)"),
    ),
)
