# ReturnSkew3F — Idiosyncratic skewness, 3-factor (Bali, Engle and Murray 2015, Table 14.10)

OSAP ref b4e911e69678a7424f318617a61d813f54183123. Emitted by `Signals/pyCode/Predictors/ZZ0_RealizedVol_IdioVol3F_ReturnSkew3F.py`
(cached as `predictor.py`; there is no `ReturnSkew3F.py`); the SignalDoc row with Cat.Signal == Predictor is the authority
(`signaldoc_row.csv`). Same script as IdioVol3F and RealizedVol (separate specs); the ReturnSkew3F step is identical to the reviewed
`factors/candidates/IdioVol3F.py` up to the last aggregation. Upstream read: `upstream_CRSPDaily.py`, `upstream_FamaFrenchDaily.py`.
Measured on THIS snapshot, DATA_SHA 198b281de1a0, harness universe, all 276 decision months.

## 1. Data availability (verdict: APPROX; no missing input, no zero-fill)

| input (OSAP) | field_map key | Sharadar source | status |
|---|---|---|---|
| `ret` (dailyCRSP) | `crsp.ret` daily | `SEP.closeadj[d]/closeadj[d-1] - 1` on the market calendar | mapped; no dlret |
| `mktrf`, `smb`, `hml` (dailyFF) | not in index | `ctx.ff3_daily(days_back)` cols mkt/smb/hml (harness rebuild) | harness accessor; mkt RAW |
| `rf` | not in snapshot | omitted | constant inside one month, absorbed by the intercept |

Declare inputs `SEP.closeadj`, `DAILY.marketcap`, `SF1.equity`, `SF1.assets`, `SF1.liabilities`, `SF1.taxliabilities`. Not used: IBES,
options, 13F, patents, segments, ratings, pensions, xad, emp, ob, ppegt. Verdict `approx` (FF3 rebuild, no dlret); not `data_start`.

## 2. Variables
`permno`, `time_d`, `ret`, `rf`, `mktrf`, `smb`, `hml`; derived `ret = ret - rf`, `time_avail_m`, `_residuals`, `ReturnSkew3F`.

## 3. Formula
Per permno and calendar month, OLS of daily excess return on [const, mktrf, smb, hml] over that month's days (>= 15 valid; Bali-Hovakimian),
then skewness of the residuals: `ReturnSkew3F = pl.col("_residuals").skew()` (polars default `bias=True`, population m3/m2^1.5).
```
df.ret.least_squares.ols(mktrf, smb, hml, mode="residuals", add_intercept=True, null_policy="drop").over([permno, time_avail_m])
   .filter(ret.count().over([permno, time_avail_m]) >= 15)
ReturnSkew3F = _residuals.skew()      # per permno-month, null residuals dropped
```
Raw value. The residual mean is 0 by the intercept, so skew = mean(e^3) / mean(e^2)^1.5.

## 4. Timing / lag
The signal month's own days (known at the t close, earns t+1), no rolling window, no extra lag. Price-only: no filing date; ART/ARQ
irrelevant. The FF3 factors read fundamentals only through the June formation (harness-internal, causal). Translate exactly as IdioVol3F:
`ctx.ff3_daily(days since month start + 1)` restricted to the month, complete rows only; returns on the market calendar; per-missing-pattern `lstsq`.

## 5. Filters
None in the predictor; SignalDoc Filter empty. Harness universe and within-sector ranking apply.

## 6. Predicted sign (SignalDoc)
`Sign = -1.0` -> `ascending=False` (LOW idiosyncratic skewness is the long leg). Cat.Economic `risk`, Cat.Data `Price`, Cat.Form `continuous`.
Notes: OP finds a negative EW and positive VW relation and calls it "difficult to interpret".

## 7. The mass-point question
Do-nothing firm (every daily return exactly 0): residuals exactly 0 -> m2 = 0 -> NaN, not a value; null it, and null any residual
spread <= 1e-12 (floating noise would otherwise manufacture a skew). Measured on the 269 scorable months: max modal-value share 0.115%
(mean 0.066%), distinct values >= 99.9% of scored names, `qcut` 10 bins in every scorable month. Tie handling: null on non-finite, else average rank.

## 8. History needed, measured coverage
- `history_months = 1`, `lookback_months = 2` (as IdioVol3F).
- Data start (factor build): smb/hml exist only from 1999-07-01 (first trading day after the June-1999 formation); complete-factor
  days < 15 before, so signals 1998-12-31..1999-06-30 (7 of 276) are NaN for every name. First scorable signal 1999-07-30
  (2,418 names); 269 scorable months >= `rebalance.min_months` 120. A data-start truncation of 2.5%, not a defect.
- Coverage of universe names with >= 15 valid pairs: mean 99.90% over the 269 scorable months (min 99.26%); scored names min 1,737.
- Measured with the IdioVol3F idiom, population skew of the residuals, all 276 months.

## 9. OSAP metadata
Acronym `ReturnSkew3F`; Acronym2 RetSkew3F; Authors Bali, Engle and Murray; Year 2015; Journal Book; Sample 1963-2012; Predictability in OP
1_clear; Signal Rep Quality 1_good; Test "port sort" (t=4.4, Table 14.10 total); Stock Weight EW; LS Quantile 0.2; Portfolio Period 1;
Start Month 6; Filter empty; GScholarCites 444. Detailed Definition: "Skewness of idiosyncratic returns computed as residuals from
regression of daily excess returns (ret - rf) on Fama-French factors (mktrf, smb, hml) over the previous month. At least 15 non-missing observations."

## 10. Proposed Sharadar mappings and deviations
- `ret` -> `SEP.closeadj` day-over-day on the market calendar (mapped; total return; no delisting return; gap days not chained).
- `mktrf/smb/hml` -> `ctx.ff3_daily` mkt/smb/hml: Sharadar-native 2x3 sort (NYSE breakpoints from CURRENT-TICKERS exchange, BE = equity +
  taxliabilities, no preferred, no dlret, mkt RAW), not Ken French. Not in the index: declare as a harness accessor, as IdioVol3F does.
- `rf` omitted (stock return and factors RAW; intercept absorbs the in-month constant): residuals unchanged up to numerical noise.
- Skew estimator: population `g1` as polars `.skew()`; OSAP's `scipy.skew` import is unused. Observation rule >= 15 valid complete days.
- Exactly-zero residual spread -> NaN (OSAP gives NaN from 0/0 too). The 1997-12 SEP stub month is dropped via `ctx.partial_months("SEP")`.
- Field-checker: first complete-factor month of `ff3_daily` (measured: 1999-07); `crsp.ret` daily already verified. No new key.
