# MomOffSeason11YrPlus — Off-season reversal, years 11-15: average return over the other-month lags 120..178 excluding the same calendar month (Heston and Sadka 2008, JFE, Table 2 Years 11-15 Nonannual)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/MomOffSeason11YrPlus.py` (cached `predictor.py`; upstream `upstream_SignalMasterTable.py`, `upstream_CRSPMonthly.py`, `upstream_stata_replication.py` beside it). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`. Sibling idiom: MomOffSeason (years 2-5), same code with `years_range` changed.

## 1. Data availability (verdict: data_start: only 109 of 276 decision months can score (first 2012-12), below rebalance.min_months = 120)

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `ret` (monthly total return incl. delisting return) | `crsp.ret` | SEP `closeadj` month-end ratios (`ctx.at_month_ends("SEP", ["closeadj"], range(120, 180))`) | mapped | `fill_date_gaps` then `fillna(0)`: a missing month inside a firm's life is 0; a lag BEFORE the first row is NaN and skipped by the mean |
| delisting return (dlret) | `crsp.dlret` | none | unavailable | not reproduced in the past window |
| `permno, time_avail_m`; shrcd 10/11/12, exchcd 1/2/3 | `crsp.shrcd`, `crsp.exchcd` | harness universe | approx | - |
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt; no SF1 input; no filing dates; no ART/ARQ question. closeadj is the total-return price.
- Data-start arithmetic: the largest lag used is 178 (lag 179 is excluded), which needs the close at BME(t-179) (ret_lag178 = close(t-178) / close(t-179) - 1). SEP's first month-end close is 1997-12-31 (panel months[0] confirmed). First full-window signal 2012-11-30 = decision month 2012-12.
  COUNT: of the 276 decision months (signals 1998-12-31 .. 2021-11-30), 167 are null by construction and **109 can score**, against `rebalance.min_months` = 120 (config/test_config.yaml): < 120, so data_start (shortfall 11 months).
  Measured on the harness universe (full-window rule, scorable months only): if the window were scorable: n scored 1,048-1,207 (median 1,117) over those 109 months; coverage 51.9%-61.3% of the universe (mean 58.6%); 1,050 of 1,746 at 2012-11-30, 1,200 of 2,312 at 2021-11-30. Coverage is 0 in the 167 leading months.
- Pooled `coverage_pct` over all 276 months (harness rule, run_test.py line 337) would be 22.5%, below the 40% bar, independent of the 109 < 120 shortfall.
- OSAP-literal (skipna) scoring would need only lag 120 (close t-121): first decision month 2008-02, 167 months; not reproduced (coordinator decision momentum_partial_windows).

## 2. Variables (exact source names)
`permno, time_avail_m, ret`; derived `ret_lag120..178` (55 lags, five same-calendar-month lags 131, 143, 155, 167, 179 dropped), `MomOffSeason11YrPlus`.

## 3. Formula in words and key lines
Arithmetic mean of 55 monthly returns: lags 120..178 excluding every lag with (lag + 1) % 12 == 0 (the same calendar month as the predicted month t+1). Lag 119 lies in the previous year block and is outside the range; the range end 180 is exclusive so lag 179 (excluded anyway) is the last tested.
```
years_range = [11, 15]
lag_start = (11-1)*12 = 120 ; lag_end = 15*12 = 180
off_season_lags = [lag for lag in range(lag_start, lag_end) if (lag + 1) % 12 != 0]     # 55 lags
df["MomOffSeason11YrPlus"] = df[lag_cols].mean(axis=1)                                                    # pandas skipna
```
Harness form: ret_k = px[BME(t-k)] / px[BME(t-k-1)] - 1 for the 55 lags, mean of the 55, NaN unless all 55 exist. The 60 month-end closes BME(t-120) .. BME(t-179) are read (the window's interior closes all matter because each month enters as its own return).
PARTIAL WINDOWS: OSAP's `mean(axis=1)` skips NaN, so a firm with any one lag is scored. Not reproduced: `history_months = 179` and `skipna=False` (coordinator decision `momentum_partial_windows`); a deviation, stated so the translator chooses knowingly.

## 4. Timing / lag convention
Signal dated t uses returns of months t-178..t-120 (minus same-calendar-month lags), holding t+1. No filing dates, no flow items, no ART/ARQ.
Overlap with the v0 Momentum leg (closeadj[t-1]/closeadj[t-12]-1, return months t-11..t-1): none: windows are disjoint (lags 120..178 vs 1..11). Not measured (the variant is data_start).

## 5. Filters
SignalDoc Filter `exchcd%in%c(1,2)` (paper sort); predictor itself shrcd 10/11/12, exchcd 1/2/3. Here: harness universe only.

## 6. Predicted sign
SignalDoc `Sign = -1.0` (LOW off-season average return is the long leg); Return 0.19; T-Stat 1.77. Orientation: `ascending=False`.

## 7. The mass-point question
A do-nothing firm (55 zero returns) produces exactly 0.0; continuous mean, no default, no signal zero-fill. Measured modal share of the scored cross-section: max 0.095% (median 0.090%); distinct values = n scored (min 1,048); distinct == n scored, which implies a full 10-bin qcut (qcut itself not run). Tie handling: none designed.

## 8. History needed (snapshot starts 1998-01; first SEP close 1997-12-31)
`history_months = 179`, `lookback_months = 179`. Preflight's data-start warning fires (lookback reaches before the panel start at the first probe month); the null block above is a data-start block, not a construction error. If translated despite data_start, the Stage 1 LS/IC months would be 109 (< 120, inconclusive rather than rejected).

## 9. OSAP metadata
MomOffSeason11YrPlus (Acronym2 MomOffSeason11YrPlus); Heston and Sadka 2008 JFE; Cat.Signal Predictor; Predictability in OP 2_likely; Signal Rep Quality 1_good; Cat.Form continuous; Cat.Data Price; Cat.Economic other; Sample 1965-2002; Key Table "2 Years 11-15 annual"; Test port sort; Sign -1.0; Return 0.19; T-Stat 1.77; EW; LS Quantile 0.1; Portfolio Period 1.0; Start Month 6.0; GScholar cites 441. LongDescription "Off season reversal years 11 to 15". Definition: "Average return in other months over the preceding 11-15 years." SignalDoc/code discrepancy: the row's Key Table reads "2 Years 11-15 annual" while the predictor header and the code (same-calendar-month lags dropped) are nonannual; this spec follows the code for construction and quotes the row for metadata. SignalDoc evidence note: "t=1.8 in port sort, but similar strats do better".

## 10. Proposed Sharadar mappings with deviations
```
d = ctx.at_month_ends("SEP", ["closeadj"], range(120, 180)); px = pivot(ID x months_back); px = px.where(px > 0)
ret_k = px[k] / px[k+1] - 1 for the 55 lags ; MomOffSeason11YrPlus = mean of the 55, NaN unless all present
ascending=False ; history_months=179 ; lookback_months=179
```
Deviations: (a) no partial windows; (b) 167 leading decision months null (SEP starts 1997-12); (c) no delisting return; (d) NaN interior close -> NaN, not 0; (e) calendar business month-ends with 7-day tolerance; (f) mean of 55 returns, not an endpoint ratio; (g) coverage 51.9%-61.3% of the universe in the scorable months vs near-complete in OSAP. Cross-check: the at_month_ends idiom and a direct month-end panel read agree to 0.0 at three probe months (06YrPlus; n 1,307/1,321/1,365, no mismatched names).
Fields not in the map: none.
