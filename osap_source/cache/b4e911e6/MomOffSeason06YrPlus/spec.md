# MomOffSeason06YrPlus — Off-season reversal, years 6-10: average return over the other-month lags 60..118 excluding the same calendar month (Heston and Sadka 2008, JFE, Table 2 Years 6-10 Nonannual)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/MomOffSeason06YrPlus.py` (cached `predictor.py`; upstream `upstream_SignalMasterTable.py`, `upstream_CRSPMonthly.py`, `upstream_stata_replication.py` beside it). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`. Sibling idiom: MomOffSeason (years 2-5), same code with `years_range` changed.

## 1. Data availability (verdict: FEASIBLE with a data-start truncation: 107 leading decision months null, 169 of 276 scorable (>= 120), not data_start)

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `ret` (monthly total return incl. delisting return) | `crsp.ret` | SEP `closeadj` month-end ratios (`ctx.at_month_ends("SEP", ["closeadj"], range(60, 120))`) | mapped | `fill_date_gaps` then `fillna(0)`: a missing month inside a firm's life is 0; a lag BEFORE the first row is NaN and skipped by the mean |
| delisting return (dlret) | `crsp.dlret` | none | unavailable | not reproduced in the past window |
| `permno, time_avail_m`; shrcd 10/11/12, exchcd 1/2/3 | `crsp.shrcd`, `crsp.exchcd` | harness universe | approx | - |
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt; no SF1 input; no filing dates; no ART/ARQ question. closeadj is the total-return price.
- Data-start arithmetic: the largest lag used is 118 (lag 119 is excluded), which needs the close at BME(t-119) (ret_lag118 = close(t-118) / close(t-119) - 1). SEP's first month-end close is 1997-12-31 (panel months[0] confirmed). First full-window signal 2007-11-30 = decision month 2007-12.
  COUNT: of the 276 decision months (signals 1998-12-31 .. 2021-11-30), 107 are null by construction and **169 can score**, against `rebalance.min_months` = 120 (config/test_config.yaml): >= 120, so NOT data_start.
  Measured on the harness universe (full-window rule, scorable months only): n scored 1,241-1,383 (median 1,308) over those 169 months; coverage 59.0%-74.7% of the universe (mean 69.9%); 1,307 of 1,895 at 2007-11-30, 1,321 of 1,922 at 2014-11-28, 1,365 of 2,312 at 2021-11-30. Coverage is 0 in the 107 leading months.
- STAGE 1 CONSEQUENCES of the 107-month null block (from `harness/run_test.py` line 337 and `analytics.ic_halves`): `coverage_pct` is pooled over ALL universe-months of the audit, scored or not; recomputed here from the same counts it is 40.6% (sum scored / sum universe over 276 months), barely above the 40% bar, against 59-75% in the scorable months alone. The IC halves split the VALID-IC months by count (84 / 85), so the boundary falls at about 2014-12 and neither half is starved; the first half is entirely 2007-12..2014-11.
- OSAP-literal (skipna) scoring would need only lag 60 (close t-61): first decision month 2003-02, 227 months; not reproduced.

## 2. Variables (exact source names)
`permno, time_avail_m, ret`; derived `ret_lag60..118` (55 lags, five same-calendar-month lags 71, 83, 95, 107, 119 dropped), `MomOffSeason06YrPlus`.

## 3. Formula in words and key lines
Arithmetic mean of 55 monthly returns: lags 60..118 excluding every lag with (lag + 1) % 12 == 0 (the same calendar month as the predicted month t+1). Lag 59 lies in the previous year block and is outside the range; the range end 120 is exclusive so lag 119 (excluded anyway) is the last tested.
```
years_range = [6, 10]
lag_start = (6-1)*12 = 60 ; lag_end = 10*12 = 120
off_season_lags = [lag for lag in range(lag_start, lag_end) if (lag + 1) % 12 != 0]     # 55 lags
df["MomOffSeason06YrPlus"] = df[lag_cols].mean(axis=1)                                                    # pandas skipna
```
Harness form: ret_k = px[BME(t-k)] / px[BME(t-k-1)] - 1 for the 55 lags, mean of the 55, NaN unless all 55 exist. The 60 month-end closes BME(t-60) .. BME(t-119) are read (the window's interior closes all matter because each month enters as its own return).
PARTIAL WINDOWS: OSAP's `mean(axis=1)` skips NaN, so a firm with any one lag is scored. Not reproduced: `history_months = 119` and `skipna=False` (coordinator decision `momentum_partial_windows`); a deviation, stated so the translator chooses knowingly.

## 4. Timing / lag convention
Signal dated t uses returns of months t-118..t-60 (minus same-calendar-month lags), holding t+1. No filing dates, no flow items, no ART/ARQ.
Overlap with the v0 Momentum leg (closeadj[t-1]/closeadj[t-12]-1, return months t-11..t-1): none: windows are disjoint (lags 60..118 vs 1..11). Measured cross-sectional Spearman with the 12-1 value over the 169 scorable months: median -0.03, mean -0.03, p10/p90 -0.14/0.08, min -0.19, max 0.18.

## 5. Filters
SignalDoc Filter `exchcd%in%c(1,2)` (paper sort); predictor itself shrcd 10/11/12, exchcd 1/2/3. Here: harness universe only.

## 6. Predicted sign
SignalDoc `Sign = -1.0` (LOW off-season average return is the long leg); Return 0.55; T-Stat 4.62. Orientation: `ascending=False`.

## 7. The mass-point question
A do-nothing firm (55 zero returns) produces exactly 0.0; continuous mean, no default, no signal zero-fill. Measured modal share of the scored cross-section: max 0.081% (median 0.076%); distinct values = n scored (min 1,241); distinct == n scored (no ties beyond singletons), which implies a full 10-bin qcut (qcut itself not run). Tie handling: none designed.

## 8. History needed (snapshot starts 1998-01; first SEP close 1997-12-31)
`history_months = 119`, `lookback_months = 119`. Preflight's data-start warning fires (lookback reaches before the panel start at the first probe month); the null block above is a data-start block, not a construction error.

## 9. OSAP metadata
MomOffSeason06YrPlus (Acronym2 MomOffSeason6YrPlus); Heston and Sadka 2008 JFE; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form continuous; Cat.Data Price; Cat.Economic other; Sample 1965-2002; Key Table "2 Years 6-10 Nonannual"; Test port sort; Sign -1.0; Return 0.55; T-Stat 4.62; EW; LS Quantile 0.1; Portfolio Period 1.0; Start Month 6.0; GScholar cites 442. LongDescription "Off season reversal years 6 to 10". Definition: "Average return in other months over the preceding 6-10 years." SignalDoc evidence note: "t=4.6 in port sort".

## 10. Proposed Sharadar mappings with deviations
```
d = ctx.at_month_ends("SEP", ["closeadj"], range(60, 120)); px = pivot(ID x months_back); px = px.where(px > 0)
ret_k = px[k] / px[k+1] - 1 for the 55 lags ; MomOffSeason06YrPlus = mean of the 55, NaN unless all present
ascending=False ; history_months=119 ; lookback_months=119
```
Deviations: (a) no partial windows; (b) 107 leading decision months null (SEP starts 1997-12); (c) no delisting return; (d) NaN interior close -> NaN, not 0; (e) calendar business month-ends with 7-day tolerance; (f) mean of 55 returns, not an endpoint ratio; (g) coverage 59.0%-74.7% of the universe in the scorable months vs near-complete in OSAP. Cross-check: the at_month_ends idiom and a direct month-end panel read agree to 0.0 at three probe months (06YrPlus; n 1,307/1,321/1,365, no mismatched names).
Fields not in the map: none.
