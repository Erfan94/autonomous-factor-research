# PriceDelayRsq — Price delay, R-squared measure D1 (Hou and Moskowitz 2005, RFS, Table 2B "one year daily")

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Signals/pyCode/Predictors/ZZ2_PriceDelaySlope_PriceDelayRsq_PriceDelayTstat.py`
(one script emits PriceDelaySlope (D2), PriceDelayRsq (D1), PriceDelayTstat (D3); cached `predictor.py`, `signaldoc_row.csv`, `upstream_CRSPDaily.py`,
`upstream_FamaFrenchDaily.py`). The SignalDoc row with `Cat.Signal == Predictor` is PriceDelayRsq. Written fresh from source and `field_map_index.yaml`. DATA_SHA 198b281de1a0.
Measured on the harness universe (`build_universe`), all 276 decision months (signals 1998-12-31 .. 2021-11-30), recorded snapshot, scratch regression code only, no factor file.

## 1. Data availability — VERDICT: APPROX (constructible from SEP daily + the harness market series; first full window ends 1999-06 after the market series start 1998-12-02)

| input (OSAP) | field_map key | Sharadar | status |
|---|---|---|---|
| `ret` (dailyCRSP `dsf.ret`, no dlret) | `crsp.ret` (daily form) | `SEP.closeadj[d]/closeadj[d-1] - 1`, prices reindexed onto the market calendar first (CoskewACX idiom: `factors/candidates/CoskewACX.py`) | mapped |
| `mktrf` (dailyFF `ff.factors_daily`) | none (public-source ruling) | `ctx.market_daily(days_back, col="vw")` raw VW all-stock return (SEP.closeadj + DAILY.marketcap), starts 1998-12-02 | harness accessor |
| `rf` (daily risk-free; `ret - rf`) | none | omitted (not in the snapshot) | unavailable, near-exact |
- Declare `FactorDef.inputs`: `SEP.closeadj`, `DAILY.marketcap`. No SF1 field. Not used: IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob, ppegt.
- Missing-item rule: only `rf` is missing; it is not zero-filled by OSAP (no `fillna` in the predictor; `zero_fill_vars` is an annual-Compustat list, irrelevant). It enters as `ret - rf` in an intercept regression, so a near-constant rf is absorbed by the intercept in both R-squareds and only its day-to-day variation (~1e-4 vs 1-2% daily stock volatility) is lost: declared deviation, hence approx, not infeasible.
- Other deviations: market series is a Sharadar-native reconstruction (common stock on NYSE/NASDAQ/NYSEMKT, prior-day cap weights, bad-print guards, no delisting returns, gap returns and >+100% days excluded), not Ken French's; `closeadj` ratio replaces CRSP `ret` (total return, no dlret, 3-decimal grid).

## 2. Variables (exact source names)
`permno, time_d, ret` (CRSP daily); `time_d, mktrf, rf` (dailyFF); derived `mktLag1..mktLag4` (`mktrf.shift(n)` on the FF TRADING-DAY calendar, before the merge), `R2Restricted`, `_R2`, `PriceDelayRsq`.

## 3. Formula in words and key lines
For each stock and each 12-month window (Jul 1 of year y-1 .. Jun 30 of year y): regress daily excess stock return on the contemporaneous market excess return alone (restricted), and on the contemporaneous plus four lagged market returns (unrestricted), both with intercept. The delay is the share of explained variance that comes from the lags.
```
df["ret"] = ret - rf ;  groups = (June bucket of time_d, permno)        # bucket = June of year(month + 6mo)
keep groups: n >= 26, var(ret) > 0, var(mktrf) > 0, non-null counts >= 26, and LAST obs month == 6 (June)
R2Restricted = R2(ret ~ mktrf);  _R2 = R2(ret ~ mktrf + mktLag1..4)           # OLS, intercept, SVD, nulls dropped
PriceDelayRsq = 1 - R2Restricted / _R2                                        # in [0, 1] (nested models)
time_avail_m = June bucket + 1 month (July);  value forward-filled inside each permno's first..last computed month
```
SignalDoc Detailed Definition agrees ("D1 ... 1 - Rsq restricted / Rsq unrestricted"). Code-only details: lags are taken on the market trading-day calendar; firms with stale or constant returns are dropped by the variance test; PriceDelaySlope/Tstat are sibling outputs, not this signal.

## 4. Timing / lag convention
OSAP: window ends Jun 30 of y; Hou-Moskowitz skip one month, so the value is stamped July y and held through the following June (signal at month-end t predicts t+1). Harness terms: signals Jul(y) .. Jun(y+1) read the window (Jun 30 y-1, Jun 30 y]; the June(y) signal still uses the PREVIOUS window (ending June y-1). The value changes once a year; a June signal reaches back 24 months (`lookback_months=24`).
Price-only: no filing date, no ART/ARQ, `dimension` default, no flow smearing. No look-ahead: the window is complete a full business month before its first use.
Forward-fill: OSAP carries a value across a year whose window fails the rules, but only between a firm's first and last valid window (the grid stops at the last valid July, so a firm that delists mid-year has no value after that July). The translation does NOT carry: the score is NaN when the current window fails (conservative; the coverage cost is bounded by the 91.7-99.9% measured without carry).

## 5. Filters
Predictor: groups need n >= 26, non-zero variance in ret and mktrf, last observation in June; `ret` and `mktrf` non-null after the inner FF merge. SignalDoc Filter blank. Daily CRSP has no shrcd/price screen; the universe is applied afterwards. Here: harness universe only (price >= $1, relative size/dollar-volume screen).

## 6. Predicted sign
SignalDoc `Sign = +1.0` (high price delay -> high returns); `ascending=True`. Cat.Economic lead lag, Cat.Data Price, Cat.Form continuous, T-Stat 3.4 (char-adjusted port sort), Return 0.31, Key Table "2B one year daily", sample 1964-2001, EW, LS Quantile 0.1, Portfolio Period 1, Start Month 7.

## 7. The mass-point question
Continuous ratio of two R-squareds; bounded below by 0 because the models are nested. A do-nothing firm (zero return all window) has zero variance and is dropped (no value), not assigned a mode. Measured on the 257 full-window months: modal value share 0.04-0.12% of scored names, distinct values 1,688-2,588 (scored n); qcut yields ten bins. No tie handling needed. Distribution (median month): median 0.055, p10 0.014, p90 0.216.
Thin-window names: the n >= 26 rule is the only observation floor, so a short-history name scores on as few as 26 days; 2.3% (median month, max 9.3%) of scored names have fewer than 200 observations. Translator may keep OSAP's rule (as here) or add a declared floor; none is in the source.

## 8. History needed (snapshot starts 1998-01) — count of scorable months against `rebalance.min_months` 120
`market_daily` starts 1998-12-02, so the window ending June 1999 (Jul 1998-Jun 1999) holds only 145 market days, and the window ending June 1998 has none.
- Unscorable (no market window): 7 months, signals 1998-12 .. 1999-06.
- Truncated window (Jul 1998-Jun 1999 window, 145 market days instead of ~252, used by signals 1999-07 .. 2000-06): 12 months. Not OSAP's construct (its window is always full). Proposed: apply the CoskewACX coordinator ruling and null them.
- Full windows (market days 247-254): signals 2000-07 .. 2021-11 = 257 months (first signal 2000-07-31). Permissive alternative: 269 months. Both clear `min_months` 120 (257 >= 120 with margin).
- Coverage (share of the month's universe scored): 257 full-window months 91.7-99.9%, median 98.3%, scored 1,688-2,588 names; the 12 truncated months 86.0-97.8%.
- `history_months` is a translator decision: OSAP's real gate is n >= 26 in-window days with a June row; `history_months=24` over-gates (requires a trade 24 months back) and 13 under-gates; the in-compute rule is the faithful one, with `history_months` only as the harness-required declaration.
- Compute cost: one regression pair per name per window; the value is constant for 12 signals, so cache per window year (measured ~2 s per window over all listed names).

## 9. OSAP metadata
PriceDelayRsq; Hou and Moskowitz; 2005; Review of Financial Studies; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Economic lead lag; Sign +1.0; Return 0.31; T-Stat 3.4; EW; LS Quantile 0.1; Portfolio Period 1; Start Month 7; sample 1964-2001; Key Table 2B one year daily; Test port sort char adjusted. Notes: "Called D1 in paper. Our primary delay measure, we use the daily stock level version. OP focuses on complicated two-stage portfolio-based version." Cites 1,376.

## 10. Proposed Sharadar mappings with deviations
```
cal = market_daily(days_back, "vw").index;  px = SEP.closeadj pivot reindexed to cal;  r = px/px.shift(1) - 1   # simple return, previous MARKET day
m, mLag1..4 = mkt_ret and its shifts on cal (lags taken on the market calendar, BEFORE cutting to the window)
window = (Jun 30 y-1, Jun 30 y], y = signal.year if signal.month >= 7 else signal.year - 1        # the value is one year-constant
per name: rows with finite r and finite m, mLag1..4;  n >= 26; var(r) > 0; var(m) > 0; a finite return in June y
PriceDelayRsq = 1 - R2(r ~ m) / R2(r ~ m + mLag1..4)           # OLS with intercept; NaN if R2u <= 0; ascending=True
null the score when the window opens before the market series (signals 1999-07 .. 2000-06, CoskewACX ruling); inputs SEP.closeadj, DAILY.marketcap
```
Deviations: (a) `rf` omitted (absorbed by the intercept when near-constant); (b) harness VW market (no dlret, gap returns, >+100% days) for FF `mktrf`; (c) `closeadj` ratio on the market calendar for CRSP `ret` (no dlret; no return across a missing row); (d) no forward-fill across a failed window; (e) truncated 1999 window nulled (257 vs 269 scorable months);
(f) "last obs in June" becomes "a finite return in June"; (g) harness universe replaces the all-stock daily CRSP sample and the NYSE-breakpoint decile sort. Fields not in the map: none besides the `market_daily` accessor and omitted `rf`. Sibling outputs PriceDelaySlope and PriceDelayTstat share the regressions; each is its own acronym.
Recommendation: translate (approx) and preflight; declare `lookback_months=24` and the `history_months` choice in the docstring.
