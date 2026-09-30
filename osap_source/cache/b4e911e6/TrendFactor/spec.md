# TrendFactor — Trend factor (Han, Zhou, Zhu 2016, JFE, Table 1)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Signals/pyCode/Predictors/TrendFactor.py` (cached `predictor.py`, `signaldoc_row.csv`,
`upstream_CRSPDaily.py`, `upstream_SignalMasterTable.py`). Written fresh; DATA_SHA 198b281de1a0.
Measured on the harness universe (`build_universe`, recorded snapshot), all 276 schedule months (signals 1998-12-31 .. 2021-11-30), scratch scripts only, no factor file.

## 1. Data availability — VERDICT: APPROX (every input present; the harness already owns the market-wide coefficient series; left-censoring by the SEP start)
| OSAP input | source | Sharadar | status |
|---|---|---|---|
| `prc`, `cfacpr` -> P = abs(prc)/cfacpr | dailyCRSP | `SEP.close` (split-adjusted, no dividend adjustment) | mapped (crsp.prc) |
| `ret` (month-ahead fRet) | SignalMasterTable | month-end `SEP.closeadj` ratio (total return), no delisting return | mapped (crsp.ret) / `crsp.dlret` unavailable |
| `exchcd` 1,2,3; `shrcd` 10,11 | SignalMasterTable | `TICKERS.exchange` (CURRENT), category Domestic Common (CURRENT) | approx |
| `abs(prc) >= 5` | SignalMasterTable | `SEP.closeunadj` >= 5 | mapped |
| `mve_c`, NYSE 10th percentile | SignalMasterTable | `DAILY.marketcap` (company level, $M); NYSE breakpoint from TICKERS exchange | approx |
- No OSAP zero-fill anywhere (the predictor has no `fillna`; a name missing any of the 11 moving averages gets NULL, "not zero": `N_MA_used == 11`). Not used: IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob, ppegt.
- Harness support exists and is tested at the data layer: `MonthContext.trend_ma_signals(scope="universe")` returns A_3 .. A_1000 (mean of the last L `SEP.close` rows / the month's last close; partial windows allowed, OSAP `min_samples=1`) for the universe names; `MonthContext.monthly_trend_coefs(months_back=1, which="ebar")` returns EBeta_L (+ `const`, `n_obs`, `n_betas`, `ma_full`, `ebar_full`). The factor is then `sum_L ebar_L x A_L`, NO intercept (harness/data_layer.py `build_trend_monthly`, `TREND_LAGS`). Fields to declare: `SEP.close`, `SEP.closeadj`, `SEP.closeunadj`, `SEP.volume`, `DAILY.marketcap`, `ACTIONS.contraname`. The coefficient series is a MARKET series (fit on all listed common stock, not the harness universe), built once and cached (first build on this snapshot 245 s; `data/cache/trend_monthly_40d56782a216.parquet`, written by this fetch as a cache file).

## 2. Variables (predictor.py)
Daily: `permno, time_d, prc, cfacpr` -> `P`, row counter `time_temp`, `A_L` for L in (3, 5, 10, 20, 50, 100, 200, 400, 600, 800, 1000). Monthly: `permno, time_avail_m, ret, prc, exchcd, shrcd, mve_c`, `qu10`, `fRet`, `_b_A_L`, `EBeta_L`; output `TrendFactor`.

## 3. Formula in words and key lines
1. For each stock, moving average of the split-adjusted price over the last L TRADING ROWS (row index `time_temp`, not calendar days; `asrol` min_samples=1 so a young stock gets a partial window), at the last row of each month, divided by that row's price: A_L = MA_L / P.
2. Each month s, cross-sectional OLS of next-month return on the eleven A_L (plus a constant) over the sample: exchcd in 1,2,3; shrcd in 10,11; abs(prc) >= 5; mve_c >= the NYSE 10th percentile that month. fRet(s) is the return of month s+1 of a name that is ALSO in the filtered sample at s+1 (lead taken after filtering). Collinear columns are dropped (Stata-like).
3. EBeta_L(t) = mean of the slopes of the 12 months before t (`shift(1)`, `rolling_mean(12, min_samples=1)`), which uses regressions whose dependent variable (month t's return) is known at t.
4. TrendFactor(i,t) = sum over L of EBeta_L(t) x A_L(i,t) (the regression's expected return without the intercept); null unless all eleven A_L are present.
```
temp_beta: EBeta_L = pl.col(f"_b_A_{L}").shift(1).rolling_mean(window_size=12, min_samples=1)
TrendFactor = sum(EBeta_MA), filter N_MA_used == 11
```
Filters are at the SIGNAL stage: only names passing the regression-sample filter carry a value (OSAP note: imposed here to run the regressions on the correct sample). Code and SignalDoc agree ("paper section 2.1 and 2.2").

## 4. Timing / lag convention
OSAP: month-end moving averages at `time_avail_m`, the signal at t predicts return of t+1, Portfolio Period 1, Start Month 6 (SignalDoc). The harness reads the signal at the prior business month-end and holds one month, so `trend_ma_signals` at the signal date and `ebar` at the same date (row t known at BME(t)) are exactly the OSAP timing. No fundamentals, hence no ART-as-of-filing and no flow-smear question. Not used: `dimension`.
`SEP.close` is restated to today's split basis; A_L is a ratio of the same series so the common rescale cancels. No delisting returns: a name that dies inside the month earns its return to its last trade.

## 5. Filters
Predictor: the regression-sample filters above are imposed at the signal stage (a name below $5 or below the NYSE 10th size percentile has no OSAP value). SignalDoc Filter column blank; the filters sit in the Notes. Here the harness universe (price >= $1, relative size/dollar-volume screen) scores the coefficients' own sample-independent A_L for every universe name, including names between $1 and $5 that OSAP leaves blank (deviation, declared). The regression sample itself is inside the coefficient builder with OSAP's filters.

## 6. Predicted sign
SignalDoc `Sign = +1.0`, `ascending=True`. Cat.Economic momentum; Cat.Data Price; Cat.Form continuous; T-Stat 15.0 (port sort, Table 1); Return 1.63; EW; LS Quantile 0.2; sample 1930-2014.

## 7. The mass-point question
A do-nothing firm has no mass value: the score is a continuous linear function of eleven ratios, distinct per name. Measured on the 275 scored months: modal value 0.035-0.058% of scored names (median 0.053%); distinct values equal the scored count (1,739-2,867); ten `qcut` bins in every month. Partial-window names (fewer than L rows) repeat nothing because the prices differ. Tie handling: none needed beyond average rank.
Structural feature, not a tie: the cross-sectional rank is monotone in a month-specific, slowly-moving linear combination of price-to-moving-average ratios (levels ~0.59 in 1999-01, ~0.18 in 2010-06, ~0.24 in 2021-11 with a very tight within-month range: p1-p99 about 0.26-0.38 in 2002-12), so the score is tightly clustered within a month and is a pure price-path momentum/reversal mix; rank-based and within-sector treatments are appropriate.

## 8. History needed (snapshot starts 1998-01)
SEP starts 1997-12-31, `DAILY.marketcap` (the NYSE size cut) starts 1998-12-01. `TREND_DAYS_BACK = 1800` calendar days (~1,240 rows) are read per signal for A_1000; `lookback_months` about 60. OSAP allows partial windows (min_samples=1), so the factor needs NO minimum price history: `history_months` should be small or none, not 48+ (a name with 300 rows is scored with short-window A_600..A_1000, exactly as OSAP).
Measured (coefficient frame over 333 fit months, 1999-01 .. 2026-09; harness schedule signals 1998-12-31 .. 2021-11-30):
- 1998-12-31 signal: no coefficients (first fit month 1998-12, first beta 1999-01): unscorable. **275 of 276** schedule months have a non-null `ebar`; universe coverage 100% on each (min 1,739 names scored, median 1,890).
- Left-censoring: A_1000 is only complete from 2001-12-31 (n_cal 1005). Before that the long-lag columns are collinear or near-collinear (n_dropped 3 in 1999-01 .. 1999-03, 2 in 2000-01, 1 in 2001-01, 0 from 2002-01); `ebar_full` (all 12 betas on uncensored windows) is first true at the **2002-12-31** signal. **228 months** (2002-12-31 .. 2021-11-30) are uncensored; **47 months** (1999-01-29 .. 2002-11-29, first resting on ONE beta, `n_betas` 1 .. 11) are scorable but censored, and in them 13.8-100% of universe names also carry partial windows (under 1000 rows); in uncensored months 7.2-21.8% (median 12.9%) do (genuine young names).
- `rebalance.min_months` 120: 228 (option b, score only `ebar_full`) and 275 (option a, score all) both pass. Option (b) drops the 47 months whose coefficients are data-start artefacts (a 1999-2002 stretch of near-collinear regressions) and keeps 228 months from 2002-12; option (a) keeps 275. The factor chooses and declares it; the harness accessor documents both. Regression sample size `n_obs` per fit month: min 2,230, median 2,611, max 3,854 (mve_c >= the NYSE 10th pctile, price >= $5, listed exchange).

## 9. OSAP metadata
TrendFactor (Acronym2 TrendFactor); Han, Zhou, Zhu; 2016; Journal of Financial Economics; Predictability in OP `1_clear`; Signal Rep Quality `1_good`; Cat.Economic momentum; Cat.Data Price; Cat.Form continuous; Key Table 1; Test "port sort"; Sign +1.0; Return 1.63; T-Stat 15.0; EW; LS Quantile 0.2; Portfolio Period 1; Start Month 6; sample 1930-2014; Detailed Definition "See paper section 2.1 and 2.2"; cites 208.

## 10. Proposed Sharadar mappings with deviations
```
ebar = ctx.monthly_trend_coefs(1).iloc[0]            # const, A_3..A_1000, ebar_full, n_betas
if option (b) and not ebar["ebar_full"]: return NaN  # 228 months
ma = ctx.trend_ma_signals()                          # A_3..A_1000 for universe names, close = SEP.close
score = (ma[A_cols] * ebar[A_cols]).sum(axis=1, min_count=11)       # no intercept; ascending=True
```
inputs `SEP.close`, `SEP.closeadj`, `SEP.closeunadj`, `SEP.volume`, `DAILY.marketcap`, `ACTIONS.contraname`. Deviations (harness, data_layer.py block comment): (a) exchange in force per the Pastor-Stambaugh-style rule and CURRENT category for share codes 10/11; (b) size = `DAILY.marketcap` per permaticker, not CRSP `mve_c` per permno; (c) no delisting returns; (d) raw `closeadj` monthly returns with no guard; (e) SEP no-trade rows in place of CRSP bid/ask midpoints; (f) data-start censoring as above; (g) pandas linear quantile for the NYSE cut; (h) the harness scores universe names between $1 and $5 that OSAP leaves blank; (i) `SEP.close` moving averages are over SEP rows including no-trade rows.
Fields not in the map: none for the price inputs; `SEP.close/closeadj/closeunadj` and `DAILY.marketcap` are mapped (crsp.prc, crsp.ret, crsp.me); `ACTIONS.contraname` is the exchange-move helper declared by the accessor. Recommendation: translate (approx), option (b) preferred for a clean screen (228 months, all far above 120), and preflight at the first/middle/last probe months (the first probe month 1998-12-31 is unscorable by construction).
