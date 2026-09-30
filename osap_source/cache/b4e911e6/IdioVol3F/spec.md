# IdioVol3F — Idiosyncratic risk, 3 factor (Ang, Hodrick, Xing, Zhang 2006, Table 7B)

OSAP ref b4e911e69678a7424f318617a61d813f54183123. Emitted by `Signals/pyCode/Predictors/ZZ0_RealizedVol_IdioVol3F_ReturnSkew3F.py`
(cached as `predictor.py`; there is no `IdioVol3F.py`); the SignalDoc row with Cat.Signal == Predictor is the authority
(`signaldoc_row.csv`). The same script also emits RealizedVol and ReturnSkew3F (sibling acronyms, specced separately). Upstream read:
`upstream_CRSPDaily.py`, `upstream_FamaFrenchDaily.py`. DATA_SHA 198b281de1a0. field_map statuses are mappings, not proofs.

## 1. Data availability (verdict: APPROX; no missing input, no zero-fill)

| input (OSAP) | field_map key | Sharadar source | status | note |
|---|---|---|---|---|
| `ret` (dailyCRSP) | `crsp.ret` | `SEP.closeadj[d]/closeadj[d-1] - 1` on the market calendar | mapped | total return, no dlret; closeadj 3-dp grid quantises back-adjusted prices < $0.50 |
| `mktrf`, `smb`, `hml` (dailyFF, Ken French) | none in index; field_map `public_sources` | `ctx.ff3_daily(days_back)` columns mkt, smb, hml | harness accessor, not a field | Sharadar-native FF3 rebuild (NYSE-breakpoint 2x3 on SF1 book equity + DAILY.marketcap); mkt is RAW |
| `rf` (dailyFF) | none; `public_sources`: rf NOT in snapshot | omitted | unavailable | immaterial here, see below |

- Declare inputs: `SEP.closeadj`, `DAILY.marketcap`, `SF1.equity`, `SF1.assets`, `SF1.liabilities`, `SF1.taxliabilities` (ff3_daily docstring).
- Not used: any Compustat/SF1 level as signal, IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob, ppegt.
- Why APPROX: the factor returns are the harness's reconstruction, not Ken French's (current-TICKERS exchange for NYSE breakpoints,
  BE = equity + taxliabilities with no preferred stock, no delisting returns, raw mkt). The rf omission by itself is immaterial:
  within one calendar month rf is effectively constant, so the regression intercept absorbs it (r - rf on mktrf = r on mkt up to
  a constant) and the residual standard deviation is unchanged. Not `data_start`: the only truncation is 7 early months (see 8).
- Recommendation: `feasible as approx`.

## 2. Variables (exact source names)

`ret`, `rf`, `mktrf`, `smb`, `hml`, `time_d`, `permno`; derived `time_avail_m` = calendar month of `time_d`, `ret = ret - rf`.

## 3. Formula

For each permno and calendar month: OLS of daily excess return on [const, mktrf, smb, hml] over that month's trading days;
IdioVol3F = sample standard deviation (ddof = 1, pl `.std()`, no k-parameter dof correction) of the residuals.
```
df.ret.least_squares.ols(mktrf, smb, hml, mode="residuals", add_intercept=True, null_policy="drop").over([permno, time_avail_m])
   .filter(ret.count().over([permno, time_avail_m]) >= 15)       # Bali-Hovakimian 2009 minimum
IdioVol3F = _residuals.std()     # per permno-month; rows with null residuals dropped
```
Raw value, no log, no scaling. The month's value is computed from that month's own days only (no rolling window).

## 4. Timing / lag

Signal month t uses days of month t (known at the t close), portfolio earns t+1; OSAP applies no extra lag. No SF1 item as signal,
so `dimension` is default and nothing smears; ART-as-of-filing is irrelevant. The FF3 factors read only fundamentals through the
June formation (harness-internal, causal). Translator: `ff = ctx.ff3_daily(40)` restricted to the signal's calendar month, stock
returns from `ctx.daily("SEP", ["closeadj"], ...)` reindexed to the market calendar (no return across a missing row).

## 5. Filters

None in the predictor (inner merge of CRSP with FF on date; >= 15 non-null daily returns). SignalDoc Filter is empty. The harness
universe and within-sector ranking apply on top.

## 6. Predicted sign (SignalDoc)

`Sign = -1.0`: high idiosyncratic volatility earns LOW subsequent returns (Ang et al. 2006). `ascending=False`. Cat.Economic
`volatility`, Cat.Data `Price`, Cat.Form `continuous`; Stock Weight VW, LS quantile 0.2, Portfolio Period 1, Start Month 6;
sample 1963-2000, t = 3.1 (port sort FF3 alpha, Table 7B); Predictability in OP 1_clear, Signal Rep Quality 1_good.

## 7. The mass-point question

A do-nothing (zero-return, illiquid) name has a near-zero residual std, not a shared value: one exactly-flat month gives residual 0
for every day (std = 0). Measured on THIS snapshot, all 276 decision months, harness universe (prototype = steps in 3 with the
harness ff3_daily, `masspoint_stats`): max modal value share 0.115% of the scored cross-section (mean 0.066%), distinct values >= 99.94% of
scored names, `qcut` yields 10 bins in every scorable month. No mass point, no tie design needed (average rank). Not measured as
exactly-zero-std share separately; it is inside the modal share above (<= 0.115%).

## 8. History needed, measured coverage

- OSAP: 15 daily observations inside the month. Declare `history_months=1` (a price within 7 days of the prior month-end) and
  `lookback_months=2` (the calendar month read is within ~40 days of the signal).
- smb/hml exist only from the first trading day after the June-1999 formation, so the first complete-factor month is July 1999.
  Measured: signals 1998-12-31 .. 1999-06-30 (7 of 276) are unscorable for every name (0 complete factor days); the first scorable
  signal is 1999-07-30 (2,418 scored of the universe). A data-start truncation of 2.5% of decision months, not a defect.
- Coverage of universe names with >= 15 valid pairs: 97.4% mean over all 276 months; 99.9% mean (min 99.3% at 2000-02-29) over the
  269 scorable months. Scored names per month: min 1,737, median 1,887.
- Measured on THIS snapshot, DATA_SHA 198b281de1a0, all 276 decision months (1999-01..2021-12, signals 1998-12-31..2021-11-30), harness universe.

## 9. OSAP metadata

Acronym `IdioVol3F`; LongDescription "Idiosyncratic risk (3 factor)"; Authors Ang et al.; Year 2006; Journal JF; Sample 1963-2000;
Cat.Signal Predictor; Cat.Economic volatility; Cat.Data Price; Cat.Form continuous; Sign -1.0; Return 1.06; T-Stat 3.1; Key Table 7B;
Test "port sort FF3 alpha"; Stock Weight VW; LS Quantile 0.2; Portfolio Period 1; Start Month 6; GScholarCites 6,323. Detailed
Definition: "Standard deviation of residuals from Fama-French three factor regressions using the past month of daily data. Value weighted".

## 10. Proposed Sharadar mappings and deviations

- `ret` -> `SEP.closeadj` day-over-day (`crsp.ret` mapped; total return, no delisting return; gap days not chained).
- `mktrf/smb/hml` -> `ctx.ff3_daily` mkt/smb/hml (harness-built; not in field_map index: declare as a harness accessor and state the
  FF3-rebuild deviations listed in 1). Both regressors and the stock return are RAW (rf omitted; constant within the month).
- Window: days of the signal's calendar month; >= 15 complete (return, mkt, smb, hml) days, else NaN.
- Residual std ddof = 1 with intercept and 3 slopes, as polars `.std()` of the residual column (not sqrt(SSE/(n-4))).
- Fields the field-checker must confirm on THIS snapshot: `crsp.ret` (daily form), and first complete-factor month of `ff3_daily`
  (measured here: 1999-07). No new field_map key required.
