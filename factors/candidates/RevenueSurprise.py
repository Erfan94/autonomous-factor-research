"""
RevenueSurprise — standardized unexpected quarterly revenue per share: the year-over-year
change in quarterly revenue per share minus its own two-year average change (the drift),
divided by the standard deviation of that unexpected change over the eight previous
quarters. High surprise is predicted to earn HIGHER returns.

OSAP: RevenueSurprise, Jegadeesh and Livnat 2006, Journal of Accounting and Economics
(Table 7 Model 1, SURGE). Predicted sign: + (SignalDoc Sign = +1).
Spec: osap_source/cache/b4e911e6/RevenueSurprise/spec.md

CONSTRUCTION (as translated; every deviation from OSAP stated):
  x_k = SF1.revenue / SF1.shareswa, both read at dimension="ARQ" (revenue is a single-QUARTER
        flow and shareswa the quarter's weighted-average share count, a level; under ART
        revenue is a trailing-four-quarter sum and shareswa is fiscal-year-mixed, so ART would
        smear the year-over-year difference and is never used). Last 21 filings known at the
        signal (ctx.fundamentals_history), placed on a quarter index k = 0 (latest) .. 20 by
        REPORT PERIOD (calendar quarters back from the latest reportperiod), never by as-of
        date or row position. A missing quarter is a NaN at its index.
        shareswa == 0 is a vendor fill and is treated as missing BEFORE dividing; shareswa
        null likewise. revenue == 0 is a true pre-revenue value and is kept (x = 0).
  PER-SHARE BASIS (declared): shareswa is restated to today's split basis on every historical
        row, so revenue/shareswa has no split jumps. It is NOT the as-reported per-share
        level of Compustat revtq/cshprq (which carries spurious split "surprises").
  GrTemp_k = x_k - x_{k+4}                                (k = 0 .. 16)
  Drift_k  = mean(GrTemp_{k+1} .. GrTemp_{k+8})            (skips NaN, as pandas .mean())
  RS_k     = GrTemp_k - Drift_k                            (k = 0 .. 8)
  SD       = std(RS_1 .. RS_8, ddof=1)                     (skips NaN, needs >= 2 values)
  RevenueSurprise = RS_0 / SD;  SD NaN or SD <= 1e-8 -> NaN;  +-inf -> NaN.
  OSAP's own minimum-observation rules are reproduced exactly (skipna partial windows): a
  partial window is scored over whatever lags exist (Drift needs one non-NaN GrTemp lag; SD
  needs two non-NaN RS lags, each of which needs its own GrTemp). The minimum history is 8
  quarters of revenue and shares. A full window is 21 quarters.
  Raw ratio, no winsorising in the factor. ascending=True: HIGH surprise is the long leg
  (SignalDoc Sign = +1).

WINDOW DEPTH (declared): SF1 ARQ history ramps in 1996-97, so a full 21-quarter window exists
  for only about 9% of the universe at 1999-12 (about 50% by 2002-12, about 83% by 2008-06);
  about 80% of the universe has at least 8 quarters at 1999-12, so the partial-window rule
  carries the early months. Coverage is low through the first months of the decision window.

GUARDS:
  - SD > 1e-8 (OSAP's source threshold) and finite; a name with identical revenue per share
    every quarter has GrTemp = 0, RS = 0, SD = 0 and is NaN (not a mass at 0). A name with
    zero revenue in every quarter (pre-revenue cohort) also has SD = 0 and is NaN.
  - Staleness: the latest filing must be at most 110 days old at the signal (mirrors OSAP's
    three-month availability plateau); older -> NaN.
  - Nothing is zero-filled; a null at any index is a NaN that propagates as in OSAP.

THE MASS-POINT QUESTION (answer it here BEFORE running preflight):
  What raw value does a do-nothing firm produce? Identical revenue per share across quarters
  gives SD = 0 and a NaN (dropped by the SD gate), not a value; an all-zero-revenue firm is
  the same. A firm that files nothing new repeats its previous value (a time plateau, not a
  cross-sectional tie). The one exact value is RS_0 = 0 with SD > 0 (a zero-surprise
  quarter): the spec measured a maximum modal-value share of 0.170% of scored names in any
  month (mean 0.065%), exact zeros on 110 name-months over 84 of 276 months, at least 99.89%
  distinct values, and ten qcut bins in every month.
  What share of the universe does nothing? Well under 1%; preflight measures it here.
  Tie handling: null (SD gate, missing revenue, missing or zero shareswa, or warm-up -> NaN, so
  blend_ranks renormalises). No zero-fill, no floor, no sample restriction.

DEVIATIONS FROM OSAP:
  - revtq (Compustat quarterly revenue, financial and foreign formats differ) -> SF1.revenue
    at ARQ; cshprq (quarterly common shares used for per-share) -> SF1.shareswa at ARQ, the
    quarter's weighted-average count, split-restated on every row (see PER-SHARE BASIS).
  - Quarters are aligned by reportperiod, not by OSAP's calendar-month lags 3,6,..,24 on a
    panel expanded three monthly rows per quarter.
  - Staleness: a 110-day latest-filing gate replaces the harness's 15-month tolerance
    (OSAP keeps a quarter for only three months after availability).
  - Restated quarters: the latest datekey on or before the signal is kept per reportperiod,
    which can differ from the Compustat vintage in OSAP.
  - SignalDoc "exclude if price less than 5" is portfolio-stage, not in predictor.py, and is
    not reproduced (universe: price >= $1).
"""

import numpy as np
import pandas as pd

from harness.factor_def import FactorDef

_NQ = 21                 # quarters of revenue per share: x_0 .. x_20
_MAX_FILING_AGE_DAYS = 110
_SD_FLOOR = 1e-8         # OSAP's own SD gate


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
    h = ctx.fundamentals_history(["revenue", "shareswa"], _NQ, dimension="ARQ")
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

    # shareswa == 0 is a vendor fill: missing before dividing. revenue == 0 is a true value.
    shs = h["shareswa"].astype(float)
    h["x"] = h["revenue"].astype(float) / shs.where(shs > 0)

    m = (h.pivot(index="ID", columns="k", values="x")
           .reindex(columns=range(_NQ)).astype(float))
    e = m.to_numpy()
    e = np.where(np.isfinite(e), e, np.nan)

    gr = e[:, 0:17] - e[:, 4:21]                     # GrTemp_k, k = 0..16
    rs = np.full((len(m), 9), np.nan)                # RS_k, k = 0..8
    for k in range(9):
        rs[:, k] = gr[:, k] - _nan_mean(gr[:, k + 1:k + 9])
    sd = _nan_std1(rs[:, 1:9])
    with np.errstate(divide="ignore", invalid="ignore"):
        sig = rs[:, 0] / sd
    sig = np.where(np.isfinite(sd) & (sd > _SD_FLOOR), sig, np.nan)
    sig = np.where(np.isfinite(sig), sig, np.nan)

    out = pd.Series(sig, index=m.index, dtype=float)
    out.index = out.index.astype(str)
    return out.reindex(ctx.ids.astype(str)).set_axis(ctx.ids)


FACTOR = FactorDef(
    # family: LEAVE UNSET (assigned in Phase C).
    name="RevenueSurprise",
    col="f_revenuesurprise",
    compute=_compute,
    ascending=True,                 # SignalDoc Sign = +1: HIGH surprise is attractive (the long leg)
    weight=1.0,
    dimension="ARQ",                # revenue is a single-quarter flow; ART would be a TTM sum and smear the YoY difference
    inputs=("SF1.revenue", "SF1.shareswa"),
    osap_acronym="RevenueSurprise",
    source="Jegadeesh and Livnat 2006 (Journal of Accounting and Economics)",
    lookback_months=67,             # 20 quarters back from the latest period end + the 110-day gate + period-end-to-filing gap
    notes="(dRPS_q - drift) / std of the previous 8 surprises, RPS = SF1.revenue / SF1.shareswa (ARQ, by reportperiod, shareswa 0 -> missing, split-restated basis); skipna partial windows as OSAP; SD gate 1e-8; full 21-quarter window for only ~9% of the universe at 1999-12 (~80% have >= 8 quarters); OVERRIDE: latest ARQ filing <= 110 days old (in place of max_fundamental_age_months 15), OSAP 3-month validity",
    field_mappings=(
        ("compustat.revtq", "SF1.revenue (dimension ARQ)",
         "single-quarter revenue flow (4 ARQ sum = ART within $1 on 96.0% of pairs); financial and foreign formats differ from Compustat revtq; revenue == 0 is a true pre-revenue value, kept; ART would be a TTM sum"),
        ("compustat.cshprq", "SF1.shareswa (dimension ARQ)",
         "quarter weighted-average share count, split-restated to today's basis on every row (revenue/shareswa has no split jumps; not the as-reported per-share level); 0 is a vendor fill -> missing before dividing"),
        ("calendar-month lags 3,6,..,24 on a 3-row quarterly expansion", "quarter index by reportperiod via ctx.fundamentals_history(revenue, shareswa; 21, ARQ)",
         "same quarter a year ago and the eight prior quarters aligned by reportperiod"),
        ("3-month availability plateau", "latest filing <= 110 days old", "replaces the harness 15-month staleness tolerance"),
        ("Filter price < 5 excluded", "not reproduced", "portfolio-stage, not in predictor.py; harness universe is price >= $1"),
    ),
)
