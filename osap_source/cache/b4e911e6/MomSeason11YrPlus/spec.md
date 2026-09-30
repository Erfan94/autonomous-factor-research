# MomSeason11YrPlus — Seasonal momentum, years 11-15: average return in the same calendar month over the preceding 11-15 years (Heston and Sadka 2008, JFE, Table 2 "2 Years 11-15 nonannual")

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/MomSeason11YrPlus.py` (cached `predictor.py`; upstream `upstream_SignalMasterTable.py`, `upstream_CRSPMonthly.py`, `upstream_stata_replication.py` beside it). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`. Measurements: harness universe, schedule 1999-01 .. 2021-12 (276 decision months, signals 1998-12-31 .. 2021-11-30), on the recorded snapshot.

## 1. Data availability (verdict: DATA_START (108 of 276 decision months scorable < rebalance.min_months 120))

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `ret` (monthly total return incl. delisting return) | `crsp.ret` | SEP `closeadj` month-end ratios (`ctx.at_month_ends("SEP", ["closeadj"], ...)`) | mapped | `ret.fillna(0)` on existing rows, then `stata_multi_lag` (fill_date_gaps, shift): a lag landing in a calendar gap (before listing or a missing month) is NaN and skipped by the mean |
| delisting return (dlret, -0.35 / -0.55 rule in upstream) | `crsp.dlret` | none | unavailable | not reproduced in the past window |
| `permno, time_avail_m`; shrcd 10/11/12, exchcd 1/2/3 | `crsp.shrcd`, `crsp.exchcd` | harness universe | approx | - |
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt; no SF1 input; no filing dates; no ART/ARQ question. closeadj is the total-return price.
- DATA-START ARITHMETIC (exact). Lags 131, ..., 179 (5 returns). The return at lag k is close(BME(t-k)) / close(BME(t-k-1)) - 1, so the deepest close is BME(t-180). SEP's first close is 1997-12-31, so the signal month must be 1997-12 + 180 months or later: first full-window signal 2012-12-31 = decision month 2013-01. The 168 decision months before it (1999-01 onward) are null by construction; 2013-01 .. 2021-12 = **108 scorable** decision months (< `rebalance.min_months` 120) -> classify `data_start` (do not screen; report as inconclusive/data_start). Confirmed empirically: scored names (>= 10) in exactly 108 of the 276 months, first at signal 2012-12-31.
- OSAP-literal partial windows (skipna mean, not reproduced; coordinator decision `momentum_partial_windows`): the first single-return score would exist from decision 2009-01, 156 months with >= 10 names scored, so this variant would clear the 120 floor only under partial-window scoring, which is declared out of scope.
- Measured coverage on the scorable months: n scored 1,044-1,202 (median 1,115) of a universe of 1,740-2,312; coverage 51.8%-61.1% (mean 58.4%, median 58.9%); 1,046 of 1,740 (60.1%) at 2012-12-31, 1,197 of 2,312 (51.8%) at 2021-11-30. Coverage is 0 in the 168 leading months. The score needs a trade near BME(t-180) (15 years of history), so it keeps survivors of long listing history.

## 2. Variables (exact source names)
`permno, time_avail_m, ret`; derived `ret_lag131` .. `ret_lag179` (step 12), `retTemp1`, `retTemp2`, `MomSeason11YrPlus`.

## 3. Formula in words and key lines
Arithmetic mean of the 5 monthly returns at lags 131, 143, 155, 167, 179 (all the same calendar month as the predicted month t+1, 132 .. 180 months before it: years 11-15).
```
df["ret"] = df["ret"].fillna(0)
lag_periods = list(range(131, 181, 12))          # 131, 143, 155, 167, 179
retTemp1 = rowtotal(lags, missing) ; retTemp2 = rownonmiss(lags)      # NaN only if all lags missing
MomSeason11YrPlus = retTemp1 / retTemp2                                             # mean of the non-missing lags (partial windows scored)
```
Harness form: for each lag k, `ret_k = px[k] / px[k+1] - 1` with px = closeadj at BME(t-k) via `ctx.at_month_ends("SEP", ["closeadj"], [131, 132, 143, 144, ...])` (closes at lags 131,132,143,144,155,156,167,168,179,180); a close is used only if > 0; `mean(axis=1, skipna=False)`: the score is NaN unless all 5 returns exist. 

## 4. Timing / lag convention
Signal dated t (business month-end) uses the month-t-k returns for k in (131, 143, 155, 167, 179), and is held in month t+1. `time_avail_m` is the month of the CRSP date, so lag k is the return of month t-k; no filing dates, no flow items, nothing to smear under TTM. ART-as-of-filing is irrelevant (no SF1). Return-window factor: `history_months = lookback_months = 180` (the deepest close).
Overlap with the v0 Momentum leg (`closeadj[t-1]/closeadj[t-12]-1`, return months t-11..t-1): none, the windows are disjoint (lags 131..179 vs 1..11). Measured cross-sectional Spearman with the 12-1 value on the scorable months: median -0.006, mean -0.005, p10/p90 -0.095/0.090, min/max -0.239/0.348 (108 months).

## 5. Filters
SignalDoc Filter `exchcd%in%c(1,2)` (paper portfolio sort); predictor itself shrcd 10/11/12, exchcd 1/2/3 and no other screen. Here: harness universe only.

## 6. Predicted sign
SignalDoc `Sign = 1.0` (HIGH average same-month return in the past is the long leg); Return 0.66; T-Stat 6.43. Orientation: `ascending=True`.

## 7. The mass-point question
A do-nothing firm (all 5 same-month returns zero) produces exactly 0.0; it is a continuous mean with no default and no signal zero-fill (the `ret.fillna(0)` only fills a missing return on an existing row and is not reproduced). Measured on the scorable months: modal share max 0.096% (median 0.090%, i.e. one name); distinct values equal n scored in all 108 months; no exact zero; qcut gives 10 bins in every month. Tie handling: none designed; the guard is a positive close at each end of every return (null otherwise, so blend_ranks renormalises). Partial windows: names with 1-4 of the 5 returns are a mean 11.8% of the any-lag scored set (null here).

## 8. History needed (snapshot starts 1998-01, first close 1997-12-31)
`history_months = lookback_months = 180`. Preflight's data-start warning fires at the first probe month (1998-12) and coverage there is 0 by construction: 168 leading decision months null, 108 scorable. Preflight probe months (first, middle, last of the schedule) would show 0 coverage at two of three probes; the variant is not to be screened.

## 9. OSAP metadata
MomSeason11YrPlus (Acronym2 MomSeason11YrPlus); Heston and Sadka 2008 JFE; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form continuous; Cat.Data Price; Cat.Economic other; Sample 1965-2002; Key Table "2 Years 11-15 nonannual"; Test port sort; Sign 1.0; Return 0.66; T-Stat 6.43; EW; LS Quantile 0.1; Portfolio Period 1.0; Start Month 6.0; GScholar cites 442. LongDescription "Return seasonality years 11 to 15". Definition: "Average return in the same month over the preceding 11-15 years." 

## 10. Proposed Sharadar mappings with deviations
```
d = ctx.at_month_ends("SEP", ["closeadj"], [131, 132, 143, 144, 155, 156, 167, 168, 179, 180])   # 7-day tolerance
px = d.pivot(index="ID", columns="months_back", values="closeadj"); px = px.where(px > 0)
ret_k = px[k] / px[k+1] - 1 for k in [131, 143, 155, 167, 179]; score = mean over the 5, NaN unless all present
ascending=True ; history_months=180 ; lookback_months=180
```
Deviations: (a) no partial windows (harness history gate, `momentum_partial_windows`); (b) first 168 decision months null (SEP starts 1997-12); (c) no delisting return; (d) a NaN return is NaN here, OSAP fills 0 on an existing row; (e) calendar business month-ends with a 7-day tolerance, not row-based lags; (f) arithmetic mean of monthly returns, as OSAP; (g) coverage 51.8%-61.1% of the universe vs near-complete in OSAP.
Fields not in the map: none.
Recommendation: data_start. Do not write a factor file for screening; log as frontier (data_start, 108 scorable months < 120).
