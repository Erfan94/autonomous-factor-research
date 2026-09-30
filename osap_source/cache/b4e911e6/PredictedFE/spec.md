# PredictedFE — Predicted analyst forecast error (Frankel and Lee 1998, JAE, Table 8A "PErr")

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Signals/pyCode/Predictors/ZZ1_AnalystValue_AOP_PredictedFE_IntrinsicValue.py`
(one script emits AnalystValue, AOP, PredictedFE and the placebo IntrinsicValue; cached `predictor.py`, `signaldoc_row.csv`,
`upstream_SignalMasterTable.py`). The SignalDoc row with `Cat.Signal == Predictor` is PredictedFE (filename is not the acronym).
Written fresh from source and `field_map_index.yaml`. DATA_SHA 198b281de1a0. No measurement needed (no constructible path).

## 1. Data availability — VERDICT: DATA_UNAVAILABLE (recommend `infeasible`; class data_unavailable)

Needs IBES analyst forecasts, which no Sharadar table carries (`field_map_index.yaml` has no IBES/estimate key; same finding as the frontier rows for the sibling
outputs AOP and AnalystValue of the same script). What the construction actually needs:

| input | source in `predictor.py` | Sharadar | OSAP missing rule |
|---|---|---|---|
| `feps1` (1-yr-ahead mean EPS, IBES fpi=1, May statement period, `fpedats > statpers + 30d`) | `IBES_EPS_Unadj` | NONE | screen `feps1.is_not_null()` DROPS the firm |
| `feps2` (2-yr-ahead mean EPS, fpi=2, May) | `IBES_EPS_Unadj` | NONE | screen `feps2.is_not_null()` DROPS the firm |
| `LTG` (long-term growth forecast, fpi=0) | `IBES_EPS_Unadj` | NONE | not required by the screen, but see below |
| `FROE1` lagged 12 months (forecast from the prior June) | derived from feps1 | NONE | `FErr` = NaN, firm-year excluded from the regression |
| `ceq, ib/ibcom, ni, sale, dvc, at, datadate`, `shrout`, `prc` | Compustat / CRSP | mapped or approx (ceq approx; dvc approx; shrout approx) | k, ROE: NaN -> not filled |

- The missing-item rule: infeasible unless OSAP zero-fills the item. Checked both places: upstream `CompustatAnnual.py` `zero_fill_vars` (nopi, dvt, ob, dm, dc, aco, ap, intan, ao,
  lco, lo, rect, invt, drc, spi, gdwl, che, dp, act, lct, tstkp, dvpa, scstkc, sstk, mib, ivao, prstkc, prstkcc, txditc, ivst) contains none of the IBES items, and the script has no `fillna` of
  feps1/feps2/LTG. The one apparent rescue, `when(LTG.is_null()).then(FROE2)`, is a SUBSTITUTE for a missing term inside `FROE3` (AnalystValue), not a zero-fill, and does not reach `PredictedFE`: the
  cross-sectional regression uses `rankLTG` and `lagLTG` as regressors (`null_policy="drop"`) and the fitted value `_b_cons + b_SG*rankSG + b_BM*rankBM + b_AOP*rankAOP + b_LTG*rankLTG` is NaN when any rank is NaN.
- `AOP` (analyst optimism = analyst value minus a historical-ROE intrinsic value) is itself a regressor, and is built from feps1, feps2 and LTG, so it is also unavailable.
- Not approximable from SF1: there are no forecasts; a realised-EPS proxy would be a different predictor. Do not substitute.
- Also unavailable in this family: nothing else beyond IBES (no options, 13F, patents, segments, ratings, pensions, xad, emp, ob, ppegt). `ppegt` not used.

## 2. Variables (exact source names)
`tickerIBES, time_avail_m, statpers, fpedats, fpi, meanest` (IBES); `permno, prc, shrout, ceq, ib, ibcom, ni, sale, datadate, dvc, at`; derived `SG, BM, AOP, LTG, FROE1, FErr, rankSG, rankBM, rankAOP, rankLTG, lagSG/BM/AOP/LTG`.

## 3. Formula in words and key lines
Frankel-Lee forecast-error predictor, built once a year in June:
1. June rows only. `SG = sale / sale.shift(60)` (5-year sales growth, 60-row lag on the monthly panel), `BM = ceq / (shrout * abs(prc))`, `k = dvc / ibcom` (or `dvc / (0.06*at)` if ibcom < 0), `ROE = ibcom / ceq_ave`.
2. `FROE1 = feps1 * shrout / ceq_ave`; `FErr = FROE1 (12 months earlier) - ROE`, winsorised 1/99 per month with trimming.
3. Screens: `ceq > 0`, `|ROE| <= 1`, `|FROE1| <= 1`, `k <= 1`, `datadate` month >= 6, `feps1` and `feps2` non-null.
4. Percentile ranks (`relrank`) of SG, BM, AOP, LTG within each June; each rank lagged 12 months.
5. Each June, OLS of `FErr` on the four LAGGED ranks; fitted value = coefficients times the CURRENT ranks. `PredictedFE` is that fitted value, held 12 months (copied to 12 monthly rows).
```
PredictedFE = _b_cons + _b_lagSG*rankSG + _b_lagBM*rankBM + _b_lagAOP*rankAOP + _b_lagLTG*rankLTG
```
SignalDoc Notes: "Very difficult to understand what OP is doing, so we report something close in spirit ... statistically insignificant"; it is a reconstruction, not the paper's exact statistic.

## 4. Timing / lag convention
June formation, one-month forecast-date convention (`time_avail_m + 1 month` on IBES May rows), held 12 months; two year-over-year steps (sale lag 60, FROE1 lag 12, rank lag 12). Moot here: IBES is absent.

## 5. Filters
Section 3 step 3 (ceq > 0, |ROE|, |FROE1|, k, datadate month >= 6, complete forecasts). SignalDoc Filter `abs(prc) > 1`.

## 6. Predicted sign
SignalDoc `Sign = -1.0`; would be `ascending=False`. Cat.Economic earnings forecast, Cat.Data Accounting, Cat.Form continuous, Return/T-Stat blank (univariate regression, nonstandard p-value), sample 1979-1993, EW, Portfolio Period 12, Start Month 6, Key Table 8A PErr.

## 7. The mass-point question
Not measured (no constructible signal). By construction a fitted value of four percentile ranks with yearly-estimated coefficients takes one value per distinct rank combination, so it is continuous with negligible ties; a firm without analyst forecasts has NO value (dropped), not a modal one.

## 8. History needed (snapshot starts 1998-01)
Sales 5 years back, FROE1 and ranks 12 months back, IBES forecasts (1976-). Irrelevant: no IBES in Sharadar, at any date.

## 9. OSAP metadata
PredictedFE (OP name PErr; Acronym2 EPSforeErr); Frankel and Lee; 1998; JAE; Predictability in OP 2_likely; Signal Rep Quality 3_distant; Cat.Economic earnings forecast; Sign -1.0; EW; Start Month 6; Filter `abs(prc) > 1`; Cites 1,739. Detailed Definition: fitted value from cross-sectional regressions of analyst earnings' forecast errors on rankings of 5-year sales growth, book-to-market, AOP, and analyst long-term growth.

## 10. Proposed Sharadar mappings with deviations
None proposed. Missing: `feps1`, `feps2`, `LTG` (IBES EPS forecasts) -> no Sharadar field; no OSAP zero-fill -> INFEASIBLE. Fields not in the map: IBES `meanest` (fpi 0/1/2) and `tickerIBES`; `compustat.ibcom` exists (`netinccmn`). Recommendation: frontier row, class data_unavailable, spec path above. No factor file.
