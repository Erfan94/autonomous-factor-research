# VolumeTrend — Volume trend: rolling 60-month OLS slope of monthly volume on time, scaled by the 60-month mean volume (Haugen and Baker 1996, Table 1)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/VolumeTrend.py` (cached `predictor.py`; upstream `upstream_CRSPMonthly.py` beside it). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`. Measurements: harness universe, 11 probe decision months spread over 1998-12-31 .. 2021-11-30 (of 276), recorded snapshot, scratch measurement (no factor file).

## 1. Data availability verdict: APPROX (constructible; deviations from the split and trim handling)
| OSAP input | Sharadar | status |
|---|---|---|
| `vol` (CRSP monthly share volume, as traded) | monthly sum of `SEP.volume x SEP.close / SEP.closeunadj` (as traded) | `crsp.vol` mapped-with-deviation; SEP.volume is split-RESTATED |
No IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob, ppegt; no SF1. OSAP zero-fills nothing.
The signal is a SCALE-FREE ratio (slope / mean volume), so the restated basis causes no cross-firm look-ahead (a later-split factor multiplies slope and mean alike and cancels). Only a split INSIDE the window changes the answer: as-traded volume (OSAP, CRSP vol is unadjusted) has a step at the split; restated volume does not. Measured Spearman restated vs as-traded: 0.88 (2003-12), 0.88 (2008-12), 0.92 (2016-12), 0.94 (2021-11); 34.0 / 28.4 / 10.3 / 5.3% of universe names have a split in the 60-month window; 1.000 among non-splitters. Recommendation: as-traded (faithful to CRSP's unadjusted vol, field-map-endorsed `volume*close/closeunadj`); the restated series is the clean alternative if the coordinator prefers no split steps.

## 2. Variables
`monthlyCRSP`: permno, time_avail_m, `vol`. Derived: `time_numeric = (year-1960)*12 + month - 1`.

## 3. Formula
```
betaVolTrend = rolling_ols(vol ~ intercept + time_numeric, window_size=60, min_periods=30, null_policy="drop").coef[time_numeric]   # ROW window per permno
meanX        = asrol(vol, mean, window=60 calendar months, min_samples=30)
VolumeTrend  = betaVolTrend / meanX
winsor2(VolumeTrend, cut(1 99), trim)      # POOLED over all permno-months of the full sample; values outside the 1st/99th pct are set to missing
```
Plainly: the monthly-volume time-trend slope over the past 5 years (>= 30 observed months), as a fraction of average volume: a growth rate of trading activity.

## 4. Timing / lag
Month-t value, signal dated t, return t+1 (no 6-month lag in predictor.py). Harness: 60 calendar months ending at the signal month-end (month t included). `ctx.daily("SEP", ["close","closeunadj","volume"], ~1850)`; the loaded frame is ~1.2M rows at the 2020s probes and ran in 2-3 s per month. Drop the 1997-12 stub with `ctx.partial_months("SEP")`. Stray SEP weekend/holiday rows: 0 in the universe scope at all probes. No SF1, no ART/ARQ.
The pooled full-sample trim is look-ahead in level but only trims tails; the harness already winsorises 1/99 per month (`rebalance.winsorize_pctl`), which is not the same operation (winsorise keeps the tail names at the cap; OSAP drops them). Recommend: no trim in the factor (document it); the harness's per-month winsorisation applies.

## 5. Filters
SignalDoc Filter is blank. The harness universe applies.

## 6. Predicted sign
SignalDoc `Sign = -1.0` (t = 3.0, mv reg, nonstandard): a rising volume trend predicts LOW returns. `ascending=False`.

## 7. Mass-point question
Do-nothing firm: constant monthly volume gives slope 0; no trading at all gives meanX = 0, which is NaN (0/0). Measured at the 9 probes with scorable months under the min-30 rule: modal share of scored names 0.051-0.062%, distinct values = scored names (1,619-1,963), measured exact-zero slope: 0 names and meanX == 0: 0 names at all 11 probes, `qcut` 10 bins. Continuous, no mass point. Tie handling: none needed; set NaN where meanX <= 0.

## 8. History needed (snapshot starts 1998-01; SEP from 1997-12-31)
Usable months start 1998-01 (1997-12 stub dropped). Decision month d uses signal d-1 (decision 1999-01 = signal 1998-12-31, index 0).
| rule | first scorable signal | unscorable decision months | scorable of 276 |
|---|---|---|---|
| OSAP min 30 of 60 (proposed exception, faithful) | 2000-06 | 18 (1999-01..2000-06) | **258** |
| full 60-month window (DEFAULT, `momentum_partial_windows`: history_months = full window) | 2002-12 | 48 (1999-01..2002-12) | **228** |
Universe coverage measured: min-30 rule 0.0% at 1998-12/1999-12, 81.7% (2000-12), 87.2% (2001-12), 94.3% (2003-12), 91.6% (2006-12), 94.9% (2008-12), 93.0% (2012-12), 92.8% (2016-12), 87.3% (2020-12), 84.6% (2021-11). Full-60: 0.0% (2001-12), 83.0% (2003-12), 85.7%, 85.5%, 88.4%, 81.6%, 78.7%, 75.0% (2021-11). Both clear `rebalance.min_months` 120 and the 40% coverage bar. DEFAULT under the recorded decision `momentum_partial_windows`: full window, `history_months=59`, `lookback_months=61`, 228 of 276 months, names with 30-59 months NaN (declared deviation from OSAP's min-30 rule). PROPOSED EXCEPTION for the coordinator to rule on: OSAP states the min-30 floor explicitly (not a skipna accident), so the faithful version is `history_months=29`, 258 months. The coordinator decides. The OSAP window is 60 ROWS (regression) and 60 calendar months (mean); here both are the 60 calendar months. Name the choice in the docstring.

## 9. OSAP metadata
Haugen and Baker (1996), JFE; Cat.Data Trading; Cat.Economic volume; continuous; sample 1979-1993; Acronym2 VolumeTrend; Key Table 1 "trading volume trend"; Test "mv reg nonstandard" (mean coefficient across 90 regressions); EW; LS Quantile 0.2; Portfolio Period 12; Start Month 6; Predictability 2_likely / Signal Rep Quality 2_fair; T-stat 3.0; 1,647 cites. Source `Signals/pyCode/Predictors/VolumeTrend.py`.

## 10. Proposed Sharadar mappings
```
d = ctx.daily("SEP", ["close","closeunadj","volume"], ~1850); drop the 1997-12 stub
d = d[d.closeunadj > 0]                                           # guard: bad row -> dropped
d["sh"] = d.volume * d.close / d.closeunadj                       # as-traded shares
m = d.groupby(["ID", month]).sh.sum()   # 0 is an observation; a missing month is not
x = year*12 + month (calendar index);  window months t-59..t, need count >= 30 (or 60)
slope = cov(x, sh)/var(x) per ID (vectorised group sums);  VolumeTrend = slope / mean(sh);  where(meanX > 0)
```
Declare `SEP.close`, `SEP.closeunadj`, `SEP.volume`; `ascending=False`; `history_months=59` (default; 29 under the min-30 exception); `lookback_months=61`.
Reconstruction tail: massive reverse-splitters (close/closeunadj > 100) are 4-30 names per probe (<= 1.5% of ~2,000); their restated volume is < 1 share on 0-27% of close/closeunadj > 100 rows and 9-50% of > 1000 rows (see the VolSD spec for the full measurement), which can put spurious low-volume months into the regression for those few names. Not material to the verdict.
Deviations: (a) restated volume rebuilt to as-traded (closeunadj only as the undo ratio). (b) consolidated SEP volume vs CRSP exchange volume (NASDAQ dealer double count pre-2004; scale-free ratio, but the trend of the double-counted series differs around 2004). (c) calendar windows; OSAP's regression window is 60 panel rows. (d) pooled 1/99 trim dropped. (e) OLS x is the calendar month index, as in OSAP. Fields: `crsp.vol`, `crsp.prc` (both in the map).
