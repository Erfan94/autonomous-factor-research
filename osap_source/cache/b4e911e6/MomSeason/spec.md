# MomSeason — Seasonal momentum, years 2-5: average return in the same calendar month over the preceding 2-5 years (Heston and Sadka 2008, JFE, Table 2 "2 Years 2-5 Annual")

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/MomSeason.py` (cached `predictor.py`; upstream `upstream_SignalMasterTable.py`, `upstream_CRSPMonthly.py`, `upstream_stata_replication.py` beside it). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`. Measurements: harness universe, schedule 1999-01 .. 2021-12 (276 decision months, signals 1998-12-31 .. 2021-11-30), on the recorded snapshot.

## 1. Data availability (verdict: FEASIBLE (declared deviations; 228 of 276 decision months scorable, floor 120))

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `ret` (monthly total return incl. delisting return) | `crsp.ret` | SEP `closeadj` month-end ratios (`ctx.at_month_ends("SEP", ["closeadj"], ...)`) | mapped | `ret.fillna(0)` on existing rows, then `stata_multi_lag` (fill_date_gaps, shift): a lag landing in a calendar gap (before listing or a missing month) is NaN and skipped by the mean |
| delisting return (dlret, -0.35 / -0.55 rule in upstream) | `crsp.dlret` | none | unavailable | not reproduced in the past window |
| `permno, time_avail_m`; shrcd 10/11/12, exchcd 1/2/3 | `crsp.shrcd`, `crsp.exchcd` | harness universe | approx | - |
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt; no SF1 input; no filing dates; no ART/ARQ question. closeadj is the total-return price.
- DATA-START ARITHMETIC (exact). Lags 23, ..., 59 (4 returns). The return at lag k is close(BME(t-k)) / close(BME(t-k-1)) - 1, so the deepest close is BME(t-60). SEP's first close is 1997-12-31, so the signal month must be 1997-12 + 60 months or later: first full-window signal 2002-12-31 = decision month 2003-01. The 48 decision months before it (1999-01 onward) are null by construction; 2003-01 .. 2021-12 = **228 scorable** decision months (>= `rebalance.min_months` 120) -> NOT data_start. Confirmed empirically: scored names (>= 10) in exactly 228 of the 276 months, first at signal 2002-12-31.
- OSAP-literal partial windows (skipna mean, not reproduced; coordinator decision `momentum_partial_windows`): the first single-return score would exist from decision 2000-01, 264 months with >= 10 names scored. Already above the floor without it.
- Measured coverage on the scorable months: n scored 1,498-1,738 (median 1,547) of a universe of 1,739-2,312; coverage 74.7%-88.3% (mean 83.5%, median 83.9%); 1,603 of 1,956 (82.0%) at 2002-12-31, 1,728 of 2,312 (74.7%) at 2021-11-30. Coverage is 0 in the 48 leading months. The score needs a trade near BME(t-60) (5 years of history), so it keeps survivors of long listing history.

## 2. Variables (exact source names)
`permno, time_avail_m, ret`; derived `ret_lag23` .. `ret_lag59` (step 12), `retTemp1`, `retTemp2`, `MomSeason`.

## 3. Formula in words and key lines
Arithmetic mean of the 4 monthly returns at lags 23, 35, 47, 59 (all the same calendar month as the predicted month t+1, 24 .. 60 months before it: years 2-5).
```
df["ret"] = df["ret"].fillna(0)
lag_periods = [23, 35, 47, 59]
retTemp1 = rowtotal(lags, missing) ; retTemp2 = rownonmiss(lags)      # NaN only if all lags missing
MomSeason = retTemp1 / retTemp2                                             # mean of the non-missing lags (partial windows scored)
```
Harness form: for each lag k, `ret_k = px[k] / px[k+1] - 1` with px = closeadj at BME(t-k) via `ctx.at_month_ends("SEP", ["closeadj"], [23, 24, 35, 36, ...])` (closes at lags 23,24,35,36,47,48,59,60); a close is used only if > 0; `mean(axis=1, skipna=False)`: the score is NaN unless all 4 returns exist. The mean is over only four returns, so a single extreme month moves a name a lot (cross-sectional winsorisation at 1/99 pct in the harness precedes the rank).

## 4. Timing / lag convention
Signal dated t (business month-end) uses the month-t-k returns for k in (23, 35, 47, 59), and is held in month t+1. `time_avail_m` is the month of the CRSP date, so lag k is the return of month t-k; no filing dates, no flow items, nothing to smear under TTM. ART-as-of-filing is irrelevant (no SF1). Return-window factor: `history_months = lookback_months = 60` (the deepest close).
Overlap with the v0 Momentum leg (`closeadj[t-1]/closeadj[t-12]-1`, return months t-11..t-1): none, the windows are disjoint (lags 23..59 vs 1..11). Lags 23, 35, 47 are exactly the lags MomOffSeason excludes, and lag 59 is also outside its 44 lags, so the two windows are disjoint. Measured cross-sectional Spearman with the 12-1 value on the scorable months: median -0.008, mean -0.005, p10/p90 -0.113/0.108, min/max -0.265/0.299 (228 months).

## 5. Filters
SignalDoc Filter `exchcd%in%c(1,2)` (paper portfolio sort); predictor itself shrcd 10/11/12, exchcd 1/2/3 and no other screen. Here: harness universe only.

## 6. Predicted sign
SignalDoc `Sign = 1.0` (HIGH average same-month return in the past is the long leg); Return 0.67; T-Stat 5.35. Orientation: `ascending=True`.

## 7. The mass-point question
A do-nothing firm (all 4 same-month returns zero) produces exactly 0.0; it is a continuous mean with no default and no signal zero-fill (the `ret.fillna(0)` only fills a missing return on an existing row and is not reproduced). Measured on the scorable months: modal share of the scored cross-section max 0.132% (median 0.065%, at most 2-3 names); distinct values equal n scored in 191 of 228 months and fall short by a tie of two names in the other 37; exact zeros (four zero returns) occurred once in 228 months (one name-month); qcut gives 10 bins in every month. Tie handling: none designed; the guard is a positive close at each end of every return (null otherwise, so blend_ranks renormalises). Partial windows: names with 1-3 of the 4 returns are a mean 10.9% of the any-lag scored set (null here).

## 8. History needed (snapshot starts 1998-01, first close 1997-12-31)
`history_months = lookback_months = 60`. Preflight's data-start warning fires at the first probe month (1998-12) and coverage there is 0 by construction: 48 leading decision months null, 228 scorable. The middle probe month (about 2010-06) falls inside the scorable block.

## 9. OSAP metadata
MomSeason (Acronym2 MomSeason); Heston and Sadka 2008 JFE; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form continuous; Cat.Data Price; Cat.Economic other; Sample 1965-2002; Key Table "2 Years 2-5 Annual"; Test port sort; Sign 1.0; Return 0.67; T-Stat 5.35; EW; LS Quantile 0.1; Portfolio Period 1.0; Start Month 6.0; GScholar cites 442. LongDescription "Return seasonality years 2 to 5". Definition: "Average return in the same month over the preceding 2-5 years." SignalDoc Notes: "Perhaps one should only include this signal from Heston and Sadka.  Certainly one shouldn't have 5 flavors of seasonal momentum, and on top of that 5 flavors of the off-season.  We include all of this to nest HXZ, however.  And technically, all of these strategies are found in the paper."

## 10. Proposed Sharadar mappings with deviations
```
d = ctx.at_month_ends("SEP", ["closeadj"], [23, 24, 35, 36, 47, 48, 59, 60])   # 7-day tolerance
px = d.pivot(index="ID", columns="months_back", values="closeadj"); px = px.where(px > 0)
ret_k = px[k] / px[k+1] - 1 for k in [23, 35, 47, 59]; score = mean over the 4, NaN unless all present
ascending=True ; history_months=60 ; lookback_months=60
```
Deviations: (a) no partial windows (harness history gate, `momentum_partial_windows`); (b) first 48 decision months null (SEP starts 1997-12); (c) no delisting return; (d) a NaN return is NaN here, OSAP fills 0 on an existing row; (e) calendar business month-ends with a 7-day tolerance, not row-based lags; (f) arithmetic mean of monthly returns, as OSAP; (g) coverage 74.7%-88.3% of the universe vs near-complete in OSAP.
Fields not in the map: none.
Recommendation: translate (idiom: factors/candidates/MomOffSeason.py) and preflight.
