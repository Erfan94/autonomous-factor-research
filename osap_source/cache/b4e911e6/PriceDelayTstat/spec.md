# PriceDelayTstat — Hou-Moskowitz price delay D3: lag-weighted t-statistic ratio (Hou and Moskowitz 2005, RFS, Table 2A "D3 adjusted")

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Signals/pyCode/Predictors/ZZ2_PriceDelaySlope_PriceDelayRsq_PriceDelayTstat.py`
(one script, same regressions as PriceDelayRsq and PriceDelaySlope; cached `predictor.py`, `signaldoc_row.csv`, `upstream_CRSPDaily.py`, `upstream_FamaFrenchDaily.py`).
SignalDoc row with `Cat.Signal == Predictor` is PriceDelayTstat. Written fresh from source and `field_map_index.yaml`. DATA_SHA 198b281de1a0.
Conventions reused exactly from `osap_source/cache/b4e911e6/PriceDelayRsq/spec.md` and `factors/candidates/PriceDelayRsq.py`.
Measured: harness universe (`build_universe`), scratch code only, no factor file, 257 full-window signal months 2000-07-31 .. 2021-11-30, recorded snapshot.

## 1. Data availability — VERDICT: APPROX (constructible; same inputs and the same declared deviations as PriceDelayRsq)
| input (OSAP) | field_map key | Sharadar | status |
|---|---|---|---|
| `ret` (dailyCRSP, no dlret) | `crsp.ret` (daily form) | `SEP.closeadj[d]/closeadj[d-1] - 1`, prices reindexed onto the market calendar first | mapped |
| `mktrf` (dailyFF) | none (public-source ruling) | `ctx.market_daily(days_back, col="vw")` raw VW all-stock return, starts 1998-12-02 | harness accessor |
| `rf` (`ret - rf`) | none | omitted (not in the snapshot) | unavailable, near-exact |
- Declare `FactorDef.inputs`: `SEP.closeadj`, `DAILY.marketcap`. No SF1 field. Not used: IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob, ppegt.
- Missing-item rule: only `rf` is missing; OSAP does not zero-fill it. A near-constant rf is absorbed by the intercept; it changes the residual variance only through its day-to-day variation, which moves each t-stat by a negligible amount. Declared deviation, approx not infeasible.
- Other deviations: Sharadar-native market series; `closeadj` ratio replaces CRSP `ret`.

## 2. Variables (exact source names)
`permno, time_d, ret`; `time_d, mktrf, rf`; derived `mktLag1..mktLag4`, `_t_mktrf`, `_t_mktLag1..4` (t-values of the unrestricted regression, `t_values` list order [mktrf, mktLag1..4, const]), `PriceDelayTstat`. `nlag = 4`, `weightscale = 1`.

## 3. Formula in words and key lines
Same regression as PriceDelaySlope; the ratio is taken on t-statistics instead of coefficients.
```
unrestricted: ret ~ 1 + mktrf + mktLag1..mktLag4                              # OLS, SVD, nulls dropped
PriceDelayTstat = (1*t1 + 2*t2 + 3*t3 + 4*t4) / (t0 + t1 + t2 + t3 + t4)       # t0 = t of mktrf, tk = t of mktLagk
```
Groups: n >= 26, var(ret) > 0, var(mktrf) > 0, non-null counts >= 26, LAST obs month == 6. The t-statistics are the plain OLS ones (classical SE, n-6 degrees of freedom), not Newey-West. SignalDoc says trim the highest and lowest 1% of coefficients, SEs and t-stats and winsorise at 10 and 90 percent each month: NONE of that is in the code (the "Applying winsorization" print only shifts time_avail_m by one month, verified by grep). The code is the authority; translate without trimming.

## 4. Timing / lag convention
Identical to PriceDelayRsq: window (Jun 30 y-1, Jun 30 y], stamped July y, held to June y+1; harness signal t reads the latest completed June window strictly before t (June signals use the previous window); `lookback_months=24`. Price-only, no filing date, no ART/ARQ, no `dimension` override, no smearing. No look-ahead.

## 5. Filters
As section 3; SignalDoc Filter blank (LS Quantile 0.1, Portfolio Period 12, Start Month 7, EW). Harness universe replaces the all-stock CRSP sample.

## 6. Predicted sign
SignalDoc `Sign = +1.0`; `ascending=True`. Cat.Economic lead lag, Cat.Data Price, Cat.Form continuous, Return 1.1, T-Stat 7.39, Key Table "2A D3 adjusted", sample 1964-2001, cites 1,370. Rep quality 3_distant; Predictability 2_likely.

## 7. The mass-point question
Continuous; no natural mode; a do-nothing firm has zero variance and is dropped (no value). Measured on 257 months (scored n 1,688-2,588): modal value share 0.04-0.12%, all scored values distinct, ten qcut bins every month, coverage 91.7-99.9% (median 98.3%; identical scored set to PriceDelaySlope). No tie handling needed.
Tails: the denominator (sum of t-stats) can be near zero or negative. Median month p1 -6.7, p10 -1.30, p50 0.02, p90 0.78, p99 1.9; |value| > 10 for 0.11-5.3% of names (median 0.96%); denominator negative for 0.06-9.0% (median 0.84%). Faithful to the code (no trim); declare, do not clip.
Near-duplicate of PriceDelaySlope: within-month Spearman rank correlation 0.99-1.00 (median 1.00) on the 257 months (the five market regressors have near-equal standard errors, so the t-ratio is essentially the beta-ratio). If both are in the ratchet, the second faces an almost fully spanned leg.

## 8. History needed (snapshot starts 1998-01) vs `rebalance.min_months` 120
Decision pricedelay_truncated_windows: windows opening before 1998-12-02 are NaN; signals 1998-12 .. 2000-06 NaN; 257 full-window months scorable (>= 120). No fixed-lag `history_months` (n >= 26 rule in compute; `no_history_gate_because`), `lookback_months=24`.

## 9. OSAP metadata
PriceDelayTstat; Hou and Moskowitz; 2005; RFS; Predictability 2_likely; Rep quality 3_distant; Cat.Economic lead lag; Sign +1.0; Return 1.1; T-Stat 7.39; EW; LS Quantile 0.1; Portfolio Period 12; Start Month 7; sample 1964-2001; Key Table 2A D3 adjusted; Test port sort char adjusted. Notes: "see PriceDelayRsq. Called D3 in paper." Acronym2 PriceDelayAdj.

## 10. Proposed Sharadar mappings with deviations
```
cal, m, mLag1..4, window, r: exactly as PriceDelayRsq
X = [1, m, mLag1..4];  b = (X'X)^-1 X'r;  s2 = RSS/(n-6);  t_k = b_k / sqrt(s2 * [(X'X)^-1]_kk)        # classical OLS t
score = (1*t[L1] + 2*t[L2] + 3*t[L3] + 4*t[L4]) / (t[m] + t[L1] + t[L2] + t[L3] + t[L4]);  NaN if denominator == 0 or non-finite
null windows opening before 1998-12-02 (signals up to 2000-06); ascending=True; inputs SEP.closeadj, DAILY.marketcap
```
Deviations: (a) rf omitted; (b) harness VW market; (c) closeadj ratio on the market calendar; (d) no forward-fill across a failed window; (e) truncated early windows nulled; (f) "last obs in June" = "finite return in June y"; (g) harness universe / within-sector ranks replace all-stock CRSP and NYSE-breakpoint sort; (h) no trim/winsor (SignalDoc text describes one, the code has none). Fields not in the map: `market_daily` accessor, omitted `rf`. Recommendation: translate (approx), preflight; flag the near-duplication with PriceDelaySlope to the reviewer.

## Addendum 2026-09-30 — history gate
The translation declares history_months=13 (hard rule for return-window factors; alpha_review batch18 critical on PriceDelayRsq), not no_history_gate_because as section 8 above suggests: names without a trade 13 months before the signal are NaN where OSAP would score them on >= 26 days.
