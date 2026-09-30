"""
EarningsSurprise — standardized unexpected quarterly EPS: the year-over-year change in
quarterly EPS minus its own two-year average change (the drift), divided by the standard
deviation of that unexpected change over the eight previous quarters. High surprise is
predicted to earn HIGHER returns.

OSAP: EarningsSurprise, Foster, Olsen and Shevlin 1984, The Accounting Review (Table 4,
days +1 to +60). Predicted sign: + (SignalDoc Sign = +1).
Spec: osap_source/cache/b4e911e6/EarningsSurprise/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  eps_k = SF1.eps at dimension="ARQ" (a single-QUARTER reported level, NOT the trailing
          four-quarter sum; read explicitly at ARQ and FactorDef.dimension="ARQ"), for
          the last 21 filings known at the signal (ctx.fundamentals_history), placed on
          a quarter index k = 0 (latest) .. 20 by REPORT PERIOD (calendar quarters back
          from the latest reportperiod), never by as-of date or row position. A missing
          quarter is a NaN at its index. eps is a reported figure (never rebuilt from
          netinccmn / shareswa) and is restated to today's split basis on every
          historical row, so all quarters of a name share one scale and the ratio
          ES/SD cancels it.
  GrTemp_k = eps_k - eps_{k+4}                            (k = 0 .. 16)
  Drift_k  = mean(GrTemp_{k+1} .. GrTemp_{k+8})            (skips NaN, as pandas .mean())
  ES_k     = GrTemp_k - Drift_k                            (k = 0 .. 8)
  SD       = std(ES_1 .. ES_8, ddof=1)                     (skips NaN, needs >= 2 values)
  EarningsSurprise = ES_0 / SD;  SD NaN or SD <= 1e-10 -> NaN;  +-inf -> NaN.
  OSAP's own minimum-observation rules are reproduced exactly: a partial window is scored
  over whatever lags exist (Drift needs one non-NaN GrTemp lag; SD needs two non-NaN ES
  lags, each of which needs its own GrTemp). The minimum history is 8 quarters of eps. A
  full window is 21 quarters.
  Raw ratio, no winsorising in the factor. ascending=True: HIGH surprise is the long leg.

GUARDS:
  - SD > 1e-10 and finite; a name with identical EPS every quarter has GrTemp = 0, ES = 0,
    SD = 0 and is NaN (not a mass at 0).
  - Staleness: the latest filing must be at most 110 days old at the signal (mirrors OSAP's
    three-month availability plateau); older -> NaN.
  - eps is never zero-filled; a null eps at any index is a NaN that propagates as in OSAP.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Identical EPS across quarters gives
  SD = 0 and a NaN (dropped by the SD gate), not a value. A firm that files nothing new
  repeats its previous value (a time plateau, not a cross-sectional tie). The one exact
  value is ES_0 = 0 with SD > 0 (a zero-surprise quarter): the spec measured 0.00-0.5% of
  scored names and a modal share of 0.05-0.16% with thousands of distinct values.
  What share of the universe does nothing? Well under 1%; preflight measures it here.
  Tie handling: null (SD gate, missing eps or warm-up -> NaN, so blend_ranks
  renormalises). No zero-fill, no floor, no sample restriction.

DEVIATIONS FROM OSAP:
  - epspxq (basic EPS EXCLUDING extraordinary items, as first reported) -> SF1.eps
    (netinccmn-based basic EPS including discontinued operations and preferred
    adjustments, reported figure); the surprise is on net rather than continuing EPS.
  - eps is on today's split basis in every vintage row; OSAP's raw epspxq carries spurious
    split "surprises" that are absent here. The scale cancels in ES/SD.
  - Quarters are aligned by reportperiod, not by OSAP's calendar-month lags on a panel
    expanded three monthly rows per quarter.
  - Staleness: a 110-day latest-filing gate replaces the harness's 15-month tolerance
    (OSAP keeps a quarter for only three months after availability).
  - Restated quarters: the latest datekey on or before the signal is kept per
    reportperiod, which can differ from first-print eps in OSAP's Compustat snapshot.
  - SignalDoc Filter abs(prc)>5 is portfolio-stage, not in predictor.py, and is not
    reproduced (universe: price >= $1). Coverage is low in the first months of the
    window (warm-up of 8+ quarters on a snapshot whose SF1 history is thin before 1998).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef

_NQ = 21                 # quarters of eps: eps_0 .. eps_20
_MAX_FILING_AGE_DAYS = 110


def _nan_mean(a):
    cnt = np.sum(np.isfinite(a), axis=1)
    tot = np.nansum(np.where(np.isfinite(a), a, 0.0), axis=1)
    return np.where(cnt > 0, tot / np.maximum(cnt, 1), np.nan)


def _nan_std1(a):
    """Row-wise std with ddof=1 over finite entries, NaN when fewer than 2."""
    fin = np.isfinite(a)
    cnt = fin.sum(axis=1)
    x = np.where(fin, a, 0.0)
    mean = x.sum(axis=1) / np.maximum(cnt, 1)
    dev = np.where(fin, a - mean[:, None], 0.0)
    var = (dev ** 2).sum(axis=1) / np.maximum(cnt - 1, 1)
    return np.where(cnt >= 2, np.sqrt(var), np.nan)


def _compute(ctx):
    h = ctx.fundamentals_history(["eps"], _NQ, dimension="ARQ")
    if h.empty:
        return pd.Series(dtype=float)
    h = h.copy()
    h["ID"] = h["ID"].astype(str)

    latest = h[h["q_back"] == 0].set_index("ID")
    fresh = latest["datekey"] >= (ctx.signal_asof - pd.Timedelta(days=_MAX_FILING_AGE_DAYS))
    latest = latest[fresh]
    h = h[h["ID"].isin(latest.index)]
    if h.empty:
        return pd.Series(dtype=float)

    rp0 = h["ID"].map(latest["reportperiod"])
    rp = pd.to_datetime(h["reportperiod"])
    months = (rp0.dt.year - rp.dt.year) * 12 + (rp0.dt.month - rp.dt.month)
    h["k"] = np.rint(months / 3.0).astype(int)
    h = h[(h["k"] >= 0) & (h["k"] < _NQ)]
    h = h.sort_values(["ID", "k", "q_back"], kind="mergesort").drop_duplicates(["ID", "k"], keep="first")

    m = (h.pivot(index="ID", columns="k", values="eps")
           .reindex(columns=range(_NQ)).astype(float))
    e = m.to_numpy()

    gr = e[:, 0:17] - e[:, 4:21]                     # GrTemp_k, k = 0..16
    es = np.full((len(m), 9), np.nan)                # ES_k, k = 0..8
    for k in range(9):
        es[:, k] = gr[:, k] - _nan_mean(gr[:, k + 1:k + 9])
    sd = _nan_std1(es[:, 1:9])
    with np.errstate(divide="ignore", invalid="ignore"):
        sig = es[:, 0] / sd
    sig = np.where(np.isfinite(sd) & (sd > 1e-10), sig, np.nan)
    sig = np.where(np.isfinite(sig), sig, np.nan)

    out = pd.Series(sig, index=m.index, dtype=float)
    out.index = out.index.astype(str)
    return out.reindex(ctx.ids.astype(str)).set_axis(ctx.ids)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="EarningsSurprise",
    col="f_earningssurprise",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: HIGH surprise is attractive (the long leg)
    weight=1.0,
    dimension="ARQ",                # eps is a single-quarter level; ART would be a TTM sum and smear the YoY difference
    inputs=("SF1.eps",),
    osap_acronym="EarningsSurprise",
    source="Foster, Olsen and Shevlin 1984 (The Accounting Review)",
    lookback_months=64,             # 20 quarters back from the latest filing + the 110-day gate
    notes="(dEPS_q - drift) / std of the previous 8 surprises; SF1.eps ARQ by reportperiod; skipna partial windows as OSAP",
    field_mappings=(
        ("compustat.epspxq", "SF1.eps (dimension ARQ)",
         "reported basic EPS incl. discontinued operations (netinccmn-based), not excluding extraordinary items; split-restated to today's basis on every row (scale cancels in ES/SD); ARQ single-quarter level, never ART"),
        ("calendar-month lags 3,6,..,24 on a 3-row quarterly expansion", "quarter index by reportperiod via ctx.fundamentals_history(eps, 21, ARQ)",
         "same quarter a year ago and the eight prior quarters aligned by reportperiod"),
        ("3-month availability plateau", "latest filing <= 110 days old", "replaces the harness 15-month staleness tolerance"),
        ("Filter abs(prc)>5", "not reproduced", "portfolio-stage, not in predictor.py; harness universe is price >= $1"),
    ),
)
