# RDAbility — R&D ability (Cohen, Diether and Malloy 2013 RFS, Table 2A Spread)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Signals/pyCode/Predictors/RDAbility.py` (cached `predictor.py`,
`upstream_CompustatAnnual.py`). DATA_SHA 198b281de1a0 (the snapshot the numbers below were measured on).

## 1. Data availability — VERDICT: preflight_failed (coverage by construction); data itself is approx, not unavailable

| input (OSAP) | field_map key | Sharadar | status |
|---|---|---|---|
| `xrd` (annual R&D) | `compustat.xrd` | SF1 `rnd`, ARY | mapped (verified 2026-09-30); VENDOR ZERO-FILLED: null 0.06% of 173,591 ARY rows, `rnd == 0` on 63.5% of non-null |
| `sale` | `compustat.sale` | SF1 `revenue`, ARY | mapped |
| `fyear`, `datadate`, `time_avail_m` | `compustat.datadate` | SF1 `reportperiod`, `datekey` | mapped |

- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt input. OSAP does NOT zero-fill `xrd` here (`xrd` is not in
  `zero_fill_vars`; the predictor has no `fillna` on it): a missing `xrd` year drops the regression pair. SF1 cannot tell "missing" from
  "zero", so the regression sample and the half-non-zero test are approximated (measured below: no material effect on coverage).
- Coverage, not data, decides: the published variable exists only for the top R&D-intensity tercile (see 5). Measured coverage is 3.0% mean.

## 2. Variables (exact source names)
`gvkey, permno, time_avail_m, fyear, datadate, xrd, sale` from `a_aCompustat`. Temp: `tempXRD, tempSale, tempY, tempX, tempXLag, tempNonZero, tempMean, tempRD, tempRDQuant`.

## 3. Formula (words + key lines)
Per firm, rows sorted by fyear (row-based shifts, no calendar gap fill): negative `xrd`/`sale` -> missing;
`tempY = log(sale_t / sale_{t-1})` (both > 0); `tempX = log(1 + xrd/sale)` (xrd, sale non-null, sale > 0).
For n = 1..5: regress `tempY` on `tempXLag = tempX.shift(n)` with intercept, rolling 8 fiscal-year rows, `min_periods=6`, null pairs dropped, and
>= 6 valid pairs in the window; keep the slope `gammaAbility_n` only if the rolling mean of `tempXLag > 0` over 8 rows (min 6) is >= 0.5.
`RDAbility = concat_list(gamma_1..gamma_5).list.mean()` (polars `list.mean` IGNORES nulls: any one surviving lag gives a value).
Then: `tempRD = xrd/sale` (xrd > 0, sale > 0); `tempRDQuant = qcut(tempRD, 3)` within `time_avail_m` over ALL firms in the file;
`RDAbility = NaN` unless tercile == 3 and `xrd > 0`.
Key lines: `.least_squares.rolling_ols(pl.col("tempXLag"), window_size=8, min_periods=6, ...)`; `if tempRDQuant != 3 -> None`.

## 4. Timing / lag
OSAP: annual record at `datadate + 6 months`, held 12 monthly copies (`time_avail_m` expanded 0..11). SF1: ARY at `datekey` (as-of-filing, 2-3 months fresher).
Flow items (sale, rnd) are fiscal-year flows: use `dimension="ARY"` (the sanctioned deviation); ART would mis-window the 8-year regression, ARQ smears.
The per-ID row series (fyear order) must be built from ARY rows deduplicated on `reportperiod`.

## 5. Filters
In the code: R&D tercile 3 of `xrd/sale` (cross-section of all Compustat-linked firms in the month), `xrd > 0`. SignalDoc Filter `abs(prc)>5` is a portfolio
filter, not in the code. Harness universe applies on top.

## 6. Predicted sign (SignalDoc)
`Sign = +1.0` (`ascending=True`). Cat.Economic `other`, Cat.Form continuous, Cat.Data Accounting; Sample 1980-2009; T-stat 2.61; Return 1.35; EW; LS quantile 0.2; Predictability `1_clear`.

## 7. The mass-point question
Continuous slope average; no mass point by construction (a firm that does nothing has no R&D, so `xrd <= 0` -> NaN, not a tie value). Mass point is not the failure;
COVERAGE is. Modal share was not the decision variable; the scored set is <= 99 names.

## 8. History needed and MEASURED coverage (harness universe, all 276 decision months 1998-12..2021-11; measured by re-implementing the section 3 rules per firm on ARY rows)
Terciles formed on the market scope (every listed common stock with an ARY row known, tolerance 15 months), scored share = % of the universe.
- Universe names with latest ARY `rnd > 0`: mean 32.5% (27.3-42.6%). In the top `rnd/revenue` tercile: mean 6.9% (4.6-15.1%).
- Scored RDAbility (faithful history rules, `rnd == 0` treated as a real zero, variant A): mean 3.04%, max 5.50%; `rnd == 0` treated as MISSING (variant B): mean 3.03%, max 5.48%.
  Scored names per month: mean 57, max 99 (variant A; B 98). Months at >= 40% coverage: 0 of 276. Months with >= 300 scored names (30 per decile): 0 of 276.
- History: SF1 ARY rows start 1992-1997 (few before FY1996; 886 FY1995 rows, 2,467 FY1996). First scorable month 2001-06-29; months with any score 246 of 276
  (>= rebalance.min_months 120 is met, so the data start is not the blocker). Lag-5 gamma first exists 2004-12-31; the full five-lag mean matters little because one lag suffices.
  Probe months: 2004-12 scored 71 (A) / 70 (B) of 1,916; 2008-12 72 / 72 of 1,794; 2012-12 80 / 78 of 1,740; 2021-11 61 / 60 of 2,312.
- Measurement conventions: row-based shifts in fiscal-year order (as OSAP); one ARY row per `reportperiod`, availability at its first `datekey`; the 8-row window, >= 6 valid pairs and >= 50% non-zero tests applied per lag.
- The harness bars (coverage >= 40%, >= 30 names per decile = 300 scored) cannot be met under any tie/fill choice: the top-tercile + 8-year-history rule is the signal.

## 9. OSAP metadata
Acronym `RDAbility`; Cohen, Diether, Malloy, RFS 2013 ("Misvaluing Innovation"); Key Table 2A Spread; Portfolio Period 1; Start Month 6; LS Quantile 0.2; EW; GScholar cites 543.
Detailed Definition: regress log sales growth on log(1+xrd/sale) in 5 bivariate regressions with lags 1..5; 8-year window, >= 6 observations; >= half non-zero R&D; RDAbility = mean of the five coefficients;
missing unless in the top tercile of xrd/sale and xrd positive.

## 10. Proposed Sharadar mappings and deviations (only if the coverage bar were ever waived)
- `xrd -> SF1.rnd` (ARY); `sale -> SF1.revenue` (ARY); deviation: `rnd == 0` indistinguishable from not reported (63.5% of non-null are 0); treat `rnd <= 0` as missing in `tempX` (variant B, matches Compustat's usual null) and as zero in `tempNonZero`.
- Terciles on the market scope (`ctx.market_context()`), not the universe; OLS slope per firm per lag from an ARY fiscal-year history (`fundamentals_history(..., 13, dimension="ARY")`).
- Not in the map: none. Recommend `preflight_failed` (coverage 3.0% mean, 0 of 276 months at 40%, <= 99 names per month). No file to translate.
