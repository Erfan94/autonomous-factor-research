# PriceDelaySlope — Hou-Moskowitz price delay D2: lag-weighted slope ratio (Hou and Moskowitz 2005, RFS, Table 2A "D2 adjusted")

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Signals/pyCode/Predictors/ZZ2_PriceDelaySlope_PriceDelayRsq_PriceDelayTstat.py`
(one script, same regressions as PriceDelayRsq; cached `predictor.py`, `signaldoc_row.csv`, `upstream_CRSPDaily.py`, `upstream_FamaFrenchDaily.py`).
SignalDoc row with `Cat.Signal == Predictor` is PriceDelaySlope. Written fresh from source and `field_map_index.yaml`. DATA_SHA 198b281de1a0.
Conventions reused exactly from `osap_source/cache/b4e911e6/PriceDelayRsq/spec.md` and `factors/candidates/PriceDelayRsq.py`.
Measured: harness universe (`build_universe`), scratch code only, no factor file, 257 full-window signal months 2000-07-31 .. 2021-11-30, recorded snapshot.

## 1. Data availability — VERDICT: APPROX (constructible; same inputs and the same declared deviations as PriceDelayRsq)
| input (OSAP) | field_map key | Sharadar | status |
|---|---|---|---|
| `ret` (dailyCRSP, no dlret) | `crsp.ret` (daily form) | `SEP.closeadj[d]/closeadj[d-1] - 1`, prices reindexed onto the market calendar first | mapped |
| `mktrf` (dailyFF) | none (public-source ruling) | `ctx.market_daily(days_back, col="vw")` raw VW all-stock return, starts 1998-12-02 | harness accessor |
| `rf` (`ret - rf`) | none | omitted (not in the snapshot) | unavailable, near-exact |
- Declare `FactorDef.inputs`: `SEP.closeadj`, `DAILY.marketcap`. No SF1 field. Not used: IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob, ppegt.
- Missing-item rule: only `rf` is missing; OSAP does not zero-fill it (no `fillna` in the predictor; `zero_fill_vars` is an annual-Compustat list). Excess return enters an intercept regression: a near-constant rf is absorbed by the intercept and only its day-to-day variation (~1e-4 vs 1-2% daily stock vol) is lost, so approx, not infeasible. Unlike Rsq, the coefficients (not R-squared ratios) are read, but they are identical to the excess-return coefficients up to that same variation.
- Other deviations: market series is Sharadar-native (not Ken French's); `closeadj` ratio replaces CRSP `ret` (no dlret, 3-decimal grid).

## 2. Variables (exact source names)
`permno, time_d, ret` (CRSP daily); `time_d, mktrf, rf` (dailyFF); derived `mktLag1..mktLag4` (`mktrf.shift(n)` on the FF trading-day calendar, before the merge), `_b_mktrf`, `_b_mktLag1..4` (unrestricted-regression coefficients), `PriceDelaySlope`. `nlag = 4`, `weightscale = 1`.

## 3. Formula in words and key lines
Per stock and June-to-June window regress daily return on the contemporaneous market return and its four lags (OLS, intercept). The delay is the lag-weighted share of the total market loading: later lags count more, the contemporaneous loading is in the denominator only.
```
unrestricted: ret ~ 1 + mktrf + mktLag1..mktLag4                     # polars_ols, SVD, nulls dropped
PriceDelaySlope = (1*b1 + 2*b2 + 3*b3 + 4*b4) / (b0 + b1 + b2 + b3 + b4)      # b0 = coef on mktrf, bk = coef on mktLagk
```
Groups: n >= 26, var(ret) > 0, var(mktrf) > 0, non-null counts >= 26, and LAST obs month == 6. Normalisation is by the sum of market betas, NOT by the number of lags. SignalDoc describes "trim the highest and lowest 1%" and "winsor 10/90" for PriceDelayTstat; NO trim or winsorisation exists in the code (the "Applying winsorization" line only shifts time_avail_m by one month, verified by grep). SignalDoc wording for this row: same ratio, no trim text.

## 4. Timing / lag convention
Identical to PriceDelayRsq. Window (Jun 30 y-1, Jun 30 y]; OSAP stamps July y and forward-fills to June y+1 (within each permno's first..last valid window). Harness: signal month-end t reads the latest COMPLETED June window strictly before t (y = year(t) if month >= 7 else year(t)-1; a June signal still uses the prior window); one value per name per window, held 12 signals, `lookback_months=24`. Price-only: no filing date, no ART/ARQ, no `dimension` override, no flow smearing. No look-ahead (window complete a business month before first use).

## 5. Filters
Predictor filters as in section 3; SignalDoc Filter blank (LS Quantile 0.1, Portfolio Period 12, Start Month 7, EW). Harness universe replaces the all-stock CRSP sample.

## 6. Predicted sign
SignalDoc `Sign = +1.0` (high price delay -> high returns); `ascending=True`. Cat.Economic lead lag, Cat.Data Price, Cat.Form continuous, Return 1.21, T-Stat 7.7, Key Table "2A D2 adjusted", sample 1964-2001, cites 1,370. Rep quality 3_distant; Predictability 2_likely.

## 7. The mass-point question
Continuous ratio of regression coefficients; no natural mode. A do-nothing firm (zero return all window) has zero variance and is dropped, not assigned a value. Measured, 257 months (scored n 1,688-2,588): modal value share 0.04-0.12% (every scored value distinct), ten qcut bins every month, coverage 91.7-99.9% (median 98.3%). No tie handling needed.
Tail shape (the real hazard, not a mass point): the denominator (sum of betas) can be near zero or negative, so the ratio is unbounded. Median month: p1 -6.4, p10 -1.27, p50 0.02, p90 0.77, p99 1.9; |value| > 10 for 0.11-5.3% of scored names (median 1.0%, p1 down to -26.7, p99 up to +23.9); denominator negative for 0.06-9.0% of scored names (median 0.9%), which flips the sign of the ratio for those names. Ranks are insensitive to the magnitude, but a negative-denominator name lands in an arbitrary decile: this is faithful to the OSAP code (no trim), declare it, do not clip. Translator: no winsorise inside the factor (harness duty).
Near-duplicate of PriceDelayTstat: within-month Spearman rank correlation between slope and tstat measured 0.99-1.00 (median 1.00) on the 257 months, because the five market regressors have near-equal standard errors. Expect the later one in the ratchet to have near-zero residual IC.

## 8. History needed (snapshot starts 1998-01) vs `rebalance.min_months` 120
Same as PriceDelayRsq: market series starts 1998-12-02; decision pricedelay_truncated_windows: windows opening before 1998-12-02 are NaN, so signals 1998-12 .. 2000-06 are NaN and 257 full-window months (2000-07 .. 2021-11) are scorable (>= 120). `history_months`: none (`no_history_gate_because`, n >= 26 in-window rule in compute), `lookback_months=24`. Cost ~2 s per month over the universe (257 months ran in ~2 min on a cached panel).

## 9. OSAP metadata
PriceDelaySlope; Hou and Moskowitz; 2005; RFS; Predictability 2_likely; Rep quality 3_distant; Cat.Economic lead lag; Sign +1.0; Return 1.21; T-Stat 7.7; EW; LS Quantile 0.1; Portfolio Period 12; Start Month 7; sample 1964-2001; Key Table 2A D2 adjusted; Test port sort char adjusted. Notes: "see PriceDelayRsq. Called D2 in paper ... Table 2 shows daily vs two-stage weekly makes a huge difference." Acronym2 PriceDelay.

## 10. Proposed Sharadar mappings with deviations
```
cal, m, mLag1..4, window, r: exactly as PriceDelayRsq (market calendar, lags before the cut, n >= 26, var>0, a finite return in June y)
X = [1, m, mLag1..4];  b = OLS(r ~ X)
score = (1*b[L1] + 2*b[L2] + 3*b[L3] + 4*b[L4]) / (b[m] + b[L1] + b[L2] + b[L3] + b[L4]);   NaN if denominator == 0 or non-finite
null windows opening before 1998-12-02 (signals up to 2000-06); ascending=True; inputs SEP.closeadj, DAILY.marketcap
```
Deviations: (a) rf omitted; (b) harness VW market for `mktrf`; (c) closeadj ratio on the market calendar for CRSP `ret`; (d) no forward-fill across a failed window; (e) truncated early windows nulled; (f) "last obs in June" = "a finite return in June y"; (g) harness universe and within-sector ranks replace all-stock CRSP and NYSE-breakpoint sort; (h) no trim/winsor (none in the code). Fields not in the map: only the `market_daily` accessor and omitted `rf`. Recommendation: translate (approx) and preflight; share regression code with PriceDelayRsq/PriceDelayTstat only at source level (one FactorDef per acronym).
