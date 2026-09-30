# ReturnSkew — Return skewness (Bali, Engle and Murray 2015, Table 14.10)

OSAP ref b4e911e69678a7424f318617a61d813f54183123. `Signals/pyCode/Predictors/ReturnSkew.py` (cached as `predictor.py`); the
SignalDoc row with Cat.Signal == Predictor is the authority (`signaldoc_row.csv`). Upstream read: `upstream_CRSPDaily.py`.
Distinct from ReturnSkew3F (residual skew, separate spec) and from the placebos ReturnSkewCAPM / ReturnSkewQF.
Measured on THIS snapshot, DATA_SHA 198b281de1a0, harness universe, all 276 decision months (signals 1998-12-31..2021-11-30).

## 1. Data availability (verdict: FEASIBLE as approx; no missing input, no zero-fill, no factor inputs)

| input (OSAP) | field_map key | Sharadar source | status |
|---|---|---|---|
| `ret` (dailyCRSP) | `crsp.ret` (daily form) | `SEP.closeadj[d]/closeadj[d-1] - 1` on the market calendar | mapped; total return, no delisting return, 3-dp closeadj grid |

Only `SEP.closeadj` is read (market calendar from `ctx.market_daily`, no factor table). Not used: IBES, options, 13F, patents, segments,
ratings, pensions, xad, emp, ob, ppegt. Verdict `approx`: the only deviations are the return definition (no dlret) and the valid-day count.

## 2. Variables
`permno`, `time_d`, `ret`; derived `time_avail_m = truncate(time_d, month)`, `ndays = len()`, `ReturnSkew = ret.skew()`.

## 3. Formula
Per permno and calendar month: `ReturnSkew = pl.col("ret").skew()` (polars default `bias=True`: population skewness m3 / m2^1.5, nulls
ignored), kept only where `ndays >= 15` (`pl.len()` counts ALL rows, null returns included). Raw value, no log.
```
predictors = crsp.group_by([permno, time_avail_m]).agg([pl.len().alias("ndays"), pl.col("ret").skew().alias("ReturnSkew")])
predictors.filter(pl.col("ndays") >= 15)
```
Translation: `g1 = mean((r-mean)^3) / mean((r-mean)^2)^1.5` over the month's valid daily returns (NOT the sample-adjusted G1; with n varying 15-23 the
two are a monotone rescale per n but not across names, so use population g1 as OSAP does). Zero variance -> 0/0 -> NaN.

## 4. Timing / lag
The month's own days: signal month t uses month t's trading days (known at the t close), earning t+1; no extra lag (OSAP
"over previous month" = the month ending at the signal). Price-only: no filing date, ART/ARQ irrelevant. Reuse the reviewed
`factors/candidates/IdioVol3F.py` idiom: calendar from `ctx.market_daily(45, col="vw")`, `ctx.daily("SEP", ["closeadj"], 45)` pivoted
on ID, reindexed to the market calendar BEFORE the lag (no return across a missing row), restricted to days in the signal's calendar
month; `ctx.partial_months("SEP")` guard (1997-12 stub, never reached).

## 5. Filters
None in the predictor; SignalDoc Filter is empty. The harness universe (price >= $1, cap/dollar-volume, within-sector ranks) applies.

## 6. Predicted sign (SignalDoc)
`Sign = -1.0` -> `ascending=False` (LOW skewness is the long leg). Cat.Economic `risk`, Cat.Data `Price`, Cat.Form `continuous`.
Notes column: OP finds a negative EW and a positive VW relation and calls the result "difficult to interpret".

## 7. The mass-point question
A do-nothing firm (flat closeadj all month, every daily return 0) has m2 = 0 -> skew NaN, not a value: nulled. No other exact value:
the skewness of 15-23 returns is continuous. Measured on all 276 months: max modal-value share 0.115% (mean 0.065%), distinct values
>= 99.94% of scored names (scored n min 1,737), `qcut` gives 10 bins every month. Tie handling: null on non-finite, else average rank.

## 8. History needed, measured coverage
- `history_months = 1` (return-window signal: a price at t-1 month), `lookback_months = 2` (the month read plus the prior close; 45 calendar days).
- No factor-data start: scorable in EVERY one of the 276 months, first signal 1998-12-31 (market_daily starts 1998-12-02, so Dec-1998
  loses the 12-01 return but keeps about 20 valid days >= 15; measured coverage 99.8% there).
- Coverage of universe names with >= 15 valid daily returns: mean 99.90% (min 99.26%, max 100%); scored names min 1,737.
- Measured with a prototype of section 4 (population skew per name, >= 15 valid returns) on all 276 months.

## 9. OSAP metadata
Acronym `ReturnSkew`; Acronym2 RetSkew; Authors Bali, Engle and Murray; Year 2015; Journal Book; Sample 1963-2012; Predictability in OP 1_clear;
Signal Rep Quality 1_good; Test "port sort" (t=4 in port sort, Table 14.10 total); Stock Weight EW; LS Quantile 0.2; Portfolio Period 1;
Start Month 6; Filter empty; GScholarCites 444. Detailed Definition: "Skewness of daily returns (ret) over previous month."

## 10. Proposed Sharadar mappings and deviations
- `ret` -> `SEP.closeadj` ratio to the previous market-calendar day (`crsp.ret` daily form, mapped); no delisting return; gap days not chained.
- Observation rule: >= 15 valid (finite) returns in the month. OSAP counts rows incl. null returns (`pl.len()`); names with null CRSP returns on
  listing days can differ by a day or two. Stated as a deviation; immaterial at coverage 99.9%.
- Skew estimator: population (biased) skewness exactly as polars `.skew()`; zero variance -> NaN.
- No factor accessor, no rf, no fundamentals. Inputs to declare: `SEP.closeadj` (and whatever `ctx.market_daily` requires: `DAILY.marketcap`).
- Field-checker: `crsp.ret` daily form already verified in the index (2026-09-30); nothing new.
