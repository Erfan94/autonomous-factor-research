# MomSeason06YrPlus — Seasonal momentum, years 6-10: average return in the same calendar month over the preceding 6-10 years (Heston and Sadka 2008, JFE, Table 2 "2 Years 6-10 Annual")

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/MomSeason06YrPlus.py` (cached `predictor.py`; upstream `upstream_SignalMasterTable.py`, `upstream_CRSPMonthly.py`, `upstream_stata_replication.py` beside it). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`. Measurements: harness universe, schedule 1999-01 .. 2021-12 (276 decision months, signals 1998-12-31 .. 2021-11-30), on the recorded snapshot.

## 1. Data availability (verdict: FEASIBLE (declared deviations; 168 of 276 decision months scorable, floor 120))

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `ret` (monthly total return incl. delisting return) | `crsp.ret` | SEP `closeadj` month-end ratios (`ctx.at_month_ends("SEP", ["closeadj"], ...)`) | mapped | `ret.fillna(0)` on existing rows, then `stata_multi_lag` (fill_date_gaps, shift): a lag landing in a calendar gap (before listing or a missing month) is NaN and skipped by the mean |
| delisting return (dlret, -0.35 / -0.55 rule in upstream) | `crsp.dlret` | none | unavailable | not reproduced in the past window |
| `permno, time_avail_m`; shrcd 10/11/12, exchcd 1/2/3 | `crsp.shrcd`, `crsp.exchcd` | harness universe | approx | - |
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt; no SF1 input; no filing dates; no ART/ARQ question. closeadj is the total-return price.
- DATA-START ARITHMETIC (exact). Lags 71, ..., 119 (5 returns). The return at lag k is close(BME(t-k)) / close(BME(t-k-1)) - 1, so the deepest close is BME(t-120). SEP's first close is 1997-12-31, so the signal month must be 1997-12 + 120 months or later: first full-window signal 2007-12-31 = decision month 2008-01. The 108 decision months before it (1999-01 onward) are null by construction; 2008-01 .. 2021-12 = **168 scorable** decision months (>= `rebalance.min_months` 120) -> NOT data_start. Confirmed empirically: scored names (>= 10) in exactly 168 of the 276 months, first at signal 2007-12-31.
- OSAP-literal partial windows (skipna mean, not reproduced; coordinator decision `momentum_partial_windows`): the first single-return score would exist from decision 2004-01, 216 months with >= 10 names scored. Already above the floor without it.
- Measured coverage on the scorable months: n scored 1,238-1,379 (median 1,302) of a universe of 1,739-2,312; coverage 58.8%-74.4% (mean 69.7%, median 70.4%); 1,301 of 1,898 (68.5%) at 2007-12-31, 1,360 of 2,312 (58.8%) at 2021-11-30. Coverage is 0 in the 108 leading months. The score needs a trade near BME(t-120) (10 years of history), so it keeps survivors of long listing history.

## 2. Variables (exact source names)
`permno, time_avail_m, ret`; derived `ret_lag71` .. `ret_lag119` (step 12), `retTemp1`, `retTemp2`, `MomSeason06YrPlus`.

## 3. Formula in words and key lines
Arithmetic mean of the 5 monthly returns at lags 71, 83, 95, 107, 119 (all the same calendar month as the predicted month t+1, 72 .. 120 months before it: years 6-10).
```
df["ret"] = df["ret"].fillna(0)
lag_periods = list(range(71, 121, 12))          # 71, 83, 95, 107, 119
retTemp1 = rowtotal(lags, missing) ; retTemp2 = rownonmiss(lags)      # NaN only if all lags missing
MomSeason06YrPlus = retTemp1 / retTemp2                                             # mean of the non-missing lags (partial windows scored)
```
Harness form: for each lag k, `ret_k = px[k] / px[k+1] - 1` with px = closeadj at BME(t-k) via `ctx.at_month_ends("SEP", ["closeadj"], [71, 72, 83, 84, ...])` (closes at lags 71,72,83,84,95,96,107,108,119,120); a close is used only if > 0; `mean(axis=1, skipna=False)`: the score is NaN unless all 5 returns exist. 

## 4. Timing / lag convention
Signal dated t (business month-end) uses the month-t-k returns for k in (71, 83, 95, 107, 119), and is held in month t+1. `time_avail_m` is the month of the CRSP date, so lag k is the return of month t-k; no filing dates, no flow items, nothing to smear under TTM. ART-as-of-filing is irrelevant (no SF1). Return-window factor: `history_months = lookback_months = 120` (the deepest close).
Overlap with the v0 Momentum leg (`closeadj[t-1]/closeadj[t-12]-1`, return months t-11..t-1): none, the windows are disjoint (lags 71..119 vs 1..11). Measured cross-sectional Spearman with the 12-1 value on the scorable months: median -0.015, mean -0.015, p10/p90 -0.106/0.089, min/max -0.227/0.205 (168 months).

## 5. Filters
SignalDoc Filter `exchcd%in%c(1,2)` (paper portfolio sort); predictor itself shrcd 10/11/12, exchcd 1/2/3 and no other screen. Here: harness universe only.

## 6. Predicted sign
SignalDoc `Sign = 1.0` (HIGH average same-month return in the past is the long leg); Return 0.68; T-Stat 6.15. Orientation: `ascending=True`.

## 7. The mass-point question
A do-nothing firm (all 5 same-month returns zero) produces exactly 0.0; it is a continuous mean with no default and no signal zero-fill (the `ret.fillna(0)` only fills a missing return on an existing row and is not reproduced). Measured on the scorable months: modal share max 0.081% (median 0.077%, i.e. one name); distinct values equal n scored in all 168 months; no exact zero in any month; qcut gives 10 bins in every month. Tie handling: none designed; the guard is a positive close at each end of every return (null otherwise, so blend_ranks renormalises). Partial windows: names with 1-4 of the 5 returns are a mean 12.9% of the any-lag scored set (null here).

## 8. History needed (snapshot starts 1998-01, first close 1997-12-31)
`history_months = lookback_months = 120`. Preflight's data-start warning fires at the first probe month (1998-12) and coverage there is 0 by construction: 108 leading decision months null, 168 scorable. The middle probe month (about 2010-06) falls inside the scorable block.

## 9. OSAP metadata
MomSeason06YrPlus (Acronym2 MomSeason06YrPlus); Heston and Sadka 2008 JFE; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form continuous; Cat.Data Price; Cat.Economic other; Sample 1965-2002; Key Table "2 Years 6-10 Annual"; Test port sort; Sign 1.0; Return 0.68; T-Stat 6.15; EW; LS Quantile 0.1; Portfolio Period 1.0; Start Month 6.0; GScholar cites 442. LongDescription "Return seasonality years 6 to 10". Definition: "Average return in the same month over the preceding 6-10 years." 

## 10. Proposed Sharadar mappings with deviations
```
d = ctx.at_month_ends("SEP", ["closeadj"], [71, 72, 83, 84, 95, 96, 107, 108, 119, 120])   # 7-day tolerance
px = d.pivot(index="ID", columns="months_back", values="closeadj"); px = px.where(px > 0)
ret_k = px[k] / px[k+1] - 1 for k in [71, 83, 95, 107, 119]; score = mean over the 5, NaN unless all present
ascending=True ; history_months=120 ; lookback_months=120
```
Deviations: (a) no partial windows (harness history gate, `momentum_partial_windows`); (b) first 108 decision months null (SEP starts 1997-12); (c) no delisting return; (d) a NaN return is NaN here, OSAP fills 0 on an existing row; (e) calendar business month-ends with a 7-day tolerance, not row-based lags; (f) arithmetic mean of monthly returns, as OSAP; (g) coverage 58.8%-74.4% of the universe vs near-complete in OSAP.
Fields not in the map: none.
Recommendation: translate (idiom: factors/candidates/MomOffSeason.py) and preflight.
