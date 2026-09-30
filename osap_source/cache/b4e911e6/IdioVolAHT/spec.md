# IdioVolAHT — Idiosyncratic risk (Ali, Hwang, Trombley 2003, Table 4)

OSAP ref b4e911e69678a7424f318617a61d813f54183123. Source `Signals/pyCode/Predictors/ZZ2_IdioVolAHT.py` (cached `predictor.py`; there is
no `IdioVolAHT.py`); SignalDoc row with Cat.Signal == Predictor in `signaldoc_row.csv`. Upstream: `upstream_CRSPDaily.py`,
`upstream_FamaFrenchDaily.py`. DATA_SHA 198b281de1a0. field_map statuses are mappings, not proofs.

## 1. Data availability (verdict: APPROX; no missing input, no zero-fill)

| input (OSAP) | field_map key | Sharadar source | status | note |
|---|---|---|---|---|
| `ret` (dailyCRSP) | `crsp.ret` | `SEP.closeadj[d]/closeadj[d-1] - 1` on the market calendar | mapped | total return, no dlret; closeadj 3-dp grid quantises back-adjusted prices < $0.50 |
| `mktrf` (dailyFF) | none in index; field_map `public_sources` | `ctx.market_daily(days_back, col="vw")` | harness accessor | RAW value-weighted common-stock market of the harness, not Ken French; series starts 1998-12-02 |
| `rf` (dailyFF) | none; `public_sources`: rf NOT in snapshot | omitted | unavailable | immaterial for a residual std, see below |

- Declare inputs: `SEP.closeadj`, `DAILY.marketcap`. Only a CAPM market factor is used (no smb/hml, so no SF1 input).
- Not used: any Compustat/SF1 item, IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob, ppegt.
- Why APPROX: market series is the harness's CRSP-like rebuild (no delisting returns, gap returns and >+100% / <-80% prints
  excluded) and rf is omitted. The rf omission shifts the intercept by rf*(1 - beta) and, through slow drift of daily rf over a
  252-day window (~5%/yr to ~0 across 1999-2021), adds a tiny within-window trend to the residual; for a residual STANDARD
  DEVIATION this is negligible, weaker a statement than for a single month but still negligible.
- Recommendation: `feasible as approx`.

## 2. Variables (exact source names)

`ret`, `rf`, `mktrf`, `time_d`, `permno`; derived `time_temp` (row counter per permno), `time_avail_m` (calendar month of `time_d`).

## 3. Formula

```
df = dailyCRSP join dailyFF on time_d;  ret = ret - rf
df = df.filter(ret not null and mktrf not null);  sort [permno, time_d];  time_temp = running row number per permno
rolling OLS ret ~ const + mktrf, window_size=252 ROWS, min_samples=100, per permno  -> rmse
   rmse = sqrt( SSE / (n_eff - 2) ),   n_eff = valid rows in the window (asreg_polars, dof = n - k, k = 2)
IdioVolAHT = last non-missing rmse within each permno-month   (gcollapse lastnm)
```
The window is the last 252 VALID ROWS of the stock's own history (null ret / mktrf rows dropped first), not 252 trading days: a
gappy name reaches further back. Translator equivalent: fetch ~420 calendar days (measured window enough for 252 rows), keep the
market-calendar days where both stock return and market return are finite, take the LAST 252 such pairs at the signal date, require
n >= 100, rmse = sqrt(SSE/(n-2)). The month's value is the estimate on the month's last trading day = the signal date.

## 4. Timing / lag

Signal month t is the estimate at the last trading day of t (data through the t close), held t+1; no extra lag. No SF1 item, so no
`dimension`/ART/ARQ issue and nothing smears. SignalDoc: start month 6, portfolio period 36 (Table 4 regressions use a long hold);
the harness holds one month as for every candidate.

## 5. Filters

None in the predictor beyond the 100-observation minimum and the inner merge with FF. SignalDoc Filter empty; Notes say the
paper's dependent variable is a size-adjusted return and that the result is "really buried" (mv regression, not a portfolio sort).

## 6. Predicted sign (SignalDoc)

`Sign = -1.0`: high idiosyncratic volatility earns LOW subsequent returns (t = 2.699 in mv reg). `ascending=False`.
Cat.Economic `volatility`, Cat.Data `Price`, Cat.Form `continuous`; Stock Weight VW; Sample 1976-1997.

## 7. The mass-point question

Continuous rmse; a do-nothing (perfectly flat) name gives rmse = 0 only if every return in 252 rows is exactly 0 and the intercept fit
is exact, which the universe price / dollar-volume screens remove. Measured on THIS snapshot, all 276 decision months, harness universe
(prototype of the formula above, `masspoint_stats`): max modal value share 0.115% of scored names (mean 0.056%), distinct values >=
99.94% of scored names, `qcut` yields 10 bins in every scorable month. No mass point; ties by average rank, no design needed.

## 8. History needed, measured coverage

- OSAP: at least 100 valid daily rows; full window 252. Declare `history_months=5` (about 100 trading days: the has_price_at gate) and
  `lookback_months=14`. Do NOT declare 12: the 100-row minimum, not a full year, is OSAP's rule.
- The market series starts 1998-12-02, so a window cannot hold 100 paired rows until spring 1999. Measured (median paired rows of universe
  names): 20 at 1998-12-31, 39, 58, 81, then 102 at 1999-04-30; the window is full (252, median) from 1999-12-31. Signals 1998-12-31 ..
  1999-03-31 (4 of 276) are unscorable for every name. From 1999-04 to 1999-11 the estimate rests on 102-250 rows (noisier, not OSAP's
  full window, but inside OSAP's own 100-row rule).
- Coverage of universe names scored: 97.2% mean over all 276 months; 98.7% mean over the 272 scorable months (min 93.6% at 1999-12-31;
  by year 1999 94.9%, 2000 95.4%, 2001-2020 98.5-99.6%, 2021 97.3%). Scored names per month: min 1,722, median 1,872.
- Measured on THIS snapshot, DATA_SHA 198b281de1a0, 276 decision months (signals 1998-12-31..2021-11-30).

## 9. OSAP metadata

Acronym `IdioVolAHT`; LongDescription "Idiosyncratic risk (AHT)"; Authors Ali, Hwang, and Trombley; Year 2003; Journal JFE; Sample
1976-1997; Cat.Signal Predictor; Cat.Economic volatility; Cat.Data Price; Cat.Form continuous; Sign -1.0; T-Stat 2.699; Key Table "4
Ivolatility^-1"; Test reg; Stock Weight VW; Portfolio Period 36; Start Month 6; Predictability in OP 1_clear; Signal Rep Quality 1_good;
GScholarCites 748. Detailed Definition: "Standard deviation of residuals from CAPM regressions using the past year of daily data.
Require at least 100 non-missing observations."

## 10. Proposed Sharadar mappings and deviations

- `ret` -> `SEP.closeadj` day-over-day on the `market_daily` calendar (`crsp.ret` mapped; nothing chained across a missing row).
- `mktrf` -> `ctx.market_daily(420, col="vw")` (harness accessor, not in field_map index). Deviation: Sharadar-native VW market with
  the `market_daily` guards instead of CRSP VW minus rf.
- `rf` -> omitted (negligible for residual std, see 1). Window: last 252 valid (return, market) rows, n >= 100; dof n - 2.
- Fields the field-checker must confirm: `crsp.ret` daily form; first valid market day (1998-12-02, measured).
  No new field_map key required.
