# MomOffSeason — Off-season long-term reversal: average return over years 2-5, excluding same-calendar-month lags (Heston and Sadka 2008, JFE, Table 2 Years 2-5 Nonannual)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/MomOffSeason.py` (cached `predictor.py`; upstream `upstream_SignalMasterTable.py`, `upstream_CRSPMonthly.py`, `upstream_stata_replication.py` beside it). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`.

## 1. Data availability (verdict: FEASIBLE with a data-start truncation: 47 leading decision months null, 229 of 276 scorable; not data_start, floor is 120)

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `ret` (monthly total return incl. delisting return) | `crsp.ret` | SEP `closeadj` month-end ratios (`ctx.monthly_closeadj(59)`) | mapped | `fill_date_gaps` then `fillna(0)`: a missing month inside a firm's life is 0; a lag BEFORE the first row is NaN and skipped by the mean |
| delisting return (dlret, -0.35 / -0.55 rule in upstream) | `crsp.dlret` | none | unavailable | not reproduced in the past window |
| `permno, time_avail_m`; shrcd 10/11/12, exchcd 1/2/3 | `crsp.shrcd`, `crsp.exchcd` | harness universe | approx | - |
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt; no SF1 input; no filing dates; no ART/ARQ question. closeadj is the total-return price.
- Data start arithmetic: the largest lag used is 58 (lag 59 is excluded), which needs the close at BME(t-59). SEP's first close is 1997-12-31, so the first full-window signal is 2002-11-29 = decision month 2002-12. Decision months 1999-01 .. 2002-11 = 47 null by construction; 2002-12 .. 2021-12 = 229 scorable >= `rebalance.min_months` 120, so NOT `data_start`.
  Measured on the harness universe: full-window scored names 1,503-1,741 over those 229 months, coverage 75.0%-88.4% of the universe (mean 83.8%; 1,609 of 1,965 at 2002-11-29, 1,534 of 1,794 at 2008-12-31, 1,733 of 2,312 at 2021-11-30). Coverage is 0 in the 47 leading months.

## 2. Variables (exact source names)
`permno, time_avail_m, ret`; derived `ret_lag12..22, 24..34, 36..46, 48..58`, `MomOffSeason`.

## 3. Formula in words and key lines
Arithmetic mean of 44 monthly returns: lags 12..58 excluding lags 23, 35, 47 (the same calendar month as the predicted month t+1; lag 11 lies in year 1 and is outside the range).
```
lag_start = (2-1)*12 = 12 ; lag_end = 5*12 = 60
off_season_lags = [lag for lag in range(12, 60) if (lag + 1) % 12 != 0]     # 12..22, 24..34, 36..46, 48..58 = 44 lags (59 also dropped)
df["MomOffSeason"] = df[lag_cols].mean(axis=1)                                 # pandas skipna
```
Harness form: `px = ctx.monthly_closeadj(59)`; ret_k = px[BME(t-k)] / px[BME(t-k-1)] - 1 for the 44 lags, which use every close BME(t-59) .. BME(t-12); mean of the 44.
PARTIAL WINDOWS (OSAP-literal): `mean(axis=1)` skips NaN, so a firm listed 14 months ago is scored from lag 12-13 alone. On the harness universe, OSAP-literal scoring would start at decision 1999-02 (275 months with 10 or more scored names), and names with some but not all 44 returns are a mean 28% of the any-lag scored set (median 14%, p75 16%; 100% in the earliest months when only one or two lags exist). The harness gate `history_months = 59` nulls all of them: a deviation, stated so the translator chooses knowingly.

## 4. Timing / lag convention
Signal dated t uses returns of months t-58..t-12 (minus same-calendar-month lags), holding t+1. No filing dates, no flow items. `partial_months` irrelevant (point reads).
Overlap with the v0 Momentum leg (composite.py `_momentum`, return months t-11..t-1): none, the windows are disjoint (lags 12..58 vs 1..11). Measured cross-sectional Spearman with that 12-1 value over the 229 scorable months: median 0.03, mean 0.01, p10/p90 -0.21/0.17, min -0.47 (2010-02).

## 5. Filters
SignalDoc Filter `exchcd%in%c(1,2)` (paper portfolio sort); predictor itself shrcd 10/11/12, exchcd 1/2/3. Here: harness universe only.

## 6. Predicted sign
SignalDoc `Sign = -1.0` (long-term reversal: LOW off-season average return is the long leg); Return 1.25; T-Stat 5.6. Orientation: `ascending=False`.

## 7. The mass-point question
Do-nothing firm (44 zero returns) produces exactly 0.0; continuous, no default, no signal zero-fill.
Measured, 229 scorable months: modal share of the scored cross-section max 0.13% (median 0.06%); distinct values = n scored (min 1,503); no `qcut(10)` collapse. Tie handling: none designed.

## 8. History needed (snapshot starts 1998-01)
`history_months = 59`, `lookback_months = 59`. Preflight's data-start warning WILL fire for the first probe month (1998-12): lookback reaches 1993-12 before the panel start 1997-12. That is the 47-month null block above, not a construction error. The first-probe coverage is 0 by construction.

## 9. OSAP metadata
MomOffSeason (Acronym2 MomOffSeason); Heston and Sadka 2008 JFE; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form continuous; Cat.Data Price; Cat.Economic other; Sample 1965-2002; Key Table "2 Years 2-5 Nonannual"; Test port sort; Sign -1.0; Return 1.25; T-Stat 5.6; EW; LS Quantile 0.1; Portfolio Period 1.0; Start Month 6.0; GScholar cites 442. LongDescription "Off season long-term reversal". Definition: "Average return in other months over the preceding 2-5 years."

## 10. Proposed Sharadar mappings with deviations
```
px = ctx.monthly_closeadj(59); cols = BME(t-59) .. BME(t-12) (48 closes)
ret = px[cols[1:]] / px[cols[:-1]] - 1 ; drop months t-23, t-35, t-47 ; MomOffSeason = mean of the 44, NaN unless all 44 present
ascending=False ; history_months=59 ; lookback_months=59
```
Deviations: (a) no partial windows (harness history gate); (b) first 47 decision months null (SEP starts 1997-12); (c) no delisting return; (d) NaN interior close -> NaN, not 0; (e) calendar business month-ends with 7-day tolerance; (f) mean of 44 returns, not an endpoint ratio; (g) coverage 75-88% of the universe vs near-complete in OSAP (names with under five years of history are dropped).
Fields not in the map: none.
