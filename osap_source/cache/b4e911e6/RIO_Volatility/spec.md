# RIO_Volatility — Residual institutional ownership among high-volatility stocks (Nagel 2005, Table 2E)

OSAP ref b4e911e69678a7424f318617a61d813f54183123 (config ref b4e911e6). Emitted by
`Signals/pyCode/Predictors/ZZ1_RIO_MB_RIO_Disp_RIO_Turnover_RIO_Volatility.py` (cached as `predictor.py`; no `RIO_Volatility.py`).
Authority: SignalDoc row with `Cat.Signal == Predictor`. Siblings from the same script: RIO_MB, RIO_Disp, RIO_Turnover. Upstream read:
`upstream_InstitutionalHoldings13F.py`. DATA_SHA 198b281de1a0.

## 1. Data availability (verdict: `data_start` — recommend `infeasible`; it would also fail preflight on two further counts)

| input (OSAP) | Sharadar | status |
|---|---|---|
| `instown_perc` (TR_13F, Thomson s34) | SF3 (investor x ticker x quarter, `units`, `value`) / SF3A `shrunits` | NOT in field_map (no 13F key); 2013-06-30 onward only |
| `mve_c`, `exchcd` (SignalMasterTable) | `DAILY.marketcap` (x1000: OSAP is in $ thousands), TICKERS.exchange | `crsp.me` mapped; `crsp.exchcd` approx |
| `ret` (monthlyCRSP) | SEP closeadj month-end ratio | `crsp.ret` mapped |
| IBES `stdev`, Compustat `at, ceq, txditc`, `vol`, `shrout` | (loaded for the sibling signals) | NOT used by RIO_Volatility |

- 13F holdings exist on the snapshot from 2013-06-30 (SF3 81.2M rows, 2013-06-30..2026-06-30); pre-2013 13F is on the standing
  unavailable list. 13F is the signal's defining input: without it RIO is undefined.
- OSAP zero-fill? The script does set a MISSING `instown_perc` to 0 then floors it at 0.0001 (`temp<.0001 -> .0001`). That fill
  exists for stocks with no 13F match inside the 13F era. Applied to a whole pre-2013 era it makes `RIO = logit(.0001) + 23.66 -
  2.89*ln(mve) + 0.08*ln(mve)^2`, a pure function of market cap: a size sort under the signal's name, not the predictor. Not
  accepted as an `approx`; the missing-item rule stays `infeasible`.

## 2. Variables (exact source names)

`instown_perc`, `mve_c`, `exchcd`, `permno`, `time_avail_m`, `ret`. Used only through the Volatility / RIO branch.

## 3. Formula in words and the key lines

1. Drop NYSE/AMEX-20th-percentile-of-`mve_c` names (`sizecat == 1`, breakpoints from exchcd 1 or 2): "filter below 20th pct NYSE me".
2. `temp = instown_perc/100`; NaN -> 0; cap at .9999; floor at .0001.
   `RIO = ln(temp/(1-temp)) + 23.66 - 2.89*ln(mve_c) + 0.08*ln(mve_c)^2`   (Nagel's size-residual ownership; `mve_c` in $ thousands).
3. `RIOlag = RIO` six calendar months earlier (`l6.RIO`, calendar not positional); `cat_RIO = fastxtile(RIOlag, n=5)` by month.
4. `Volatility` = rolling std of monthly `ret`, 12-month window, min 6 (asrol). `cat_Volatility = fastxtile(Volatility, n=5)`.
5. `RIO_Volatility = cat_RIO` if `cat_Volatility == 5`, else missing. Values are the integers 1..5.

## 4. Timing / lag

OSAP's `time_avail_m` for 13F is the report-quarter month, forward-filled between a stock's reports (no 45-day filing lag). The signal
uses RIO from t-6, so even a point-in-time lag of 45 days (quarter Q usable from Q+45d) is not binding beyond a two-month shift:
the first usable quarter 2013-06-30 (available 2013-08-14) feeds signals from 2014-02-28 under the lag, 2013-12-31 without it. Needs a
new 13F `MonthContext` accessor (harness extension, not factor code). Volatility is price-only. No ART/ARQ issue, no flow item.

## 5. Filters

SignalDoc Filter blank. In-code: the size filter in step 1 (nearly absorbed by the harness entry cut: NYSE 20th percentile enter,
15th exit, on a wider exchange set) and `mve_c` non-missing.

## 6. Predicted sign

`Sign = +1.0`: among the most volatile quintile, high residual institutional ownership predicts HIGH returns (short-sale constraint
story, t = 4.38 conditional sort, Table 2E). `ascending=True`. Cat.Economic `short sale constraints`; Cat.Data `13F`; Cat.Form
`discrete`; EW; Portfolio Period 1; Start Month 12; sample 1980-2003.

## 7. The mass-point question

Output is a 5-level ordinal (1..5) that exists only for the top-volatility quintile, so the signal is structurally a mass point:
each level holds ~1/5 of the scored names, modal share >= ~20% against the harness cliff of 10%, and `qcut(q=10)` can give at most
5 bins (< 10): preflight hard-fails (`MASS POINT`). A do-nothing (no-13F) stock gets RIOlag from the size term alone (above), so the
missing-13F cases would all share the size-determined values. Not measured on RIO itself (no 13F accessor); the ordinal structure is exact.

## 8. History needed and measured counts (snapshot starts 1998-01; `rebalance.min_months` = 120)

- Scorable decision months, counted on the harness schedule (276 months, signals 1998-12-31 .. 2021-11-30): **96** with OSAP's own
  timing (signals 2013-12-31 .. 2021-11-30), **94** with the 45-day point-in-time lag (2014-02-28 .. 2021-11-30). Both < 120:
  Stage 1 would be inconclusive by construction (the DelBreadth rule). Volatility history (12 months, min 6) does not bind.
- Coverage on those months, harness universe (mean ~1,930 names): the Volatility top quintile is 19.67% of the universe (range
  19.16-19.91%; ~380 names, min 355); 98.3% of the universe has a computable Volatility. Stage 1 coverage bar is 40%, so the
  signal sits at ~20% with 13F data at full presence: a second independent failure (measured, 96 months).
- `history_months` ~ 13 (12-month return window) if it were ever built.

## 9. OSAP metadata

Acronym `RIO_Volatility`; LongDescription "Inst Own and Idio Vol"; Authors Nagel; Year 2005; Journal JFE; Cat.Data 13F; Cat.Economic
short sale constraints; Cat.Form discrete; Sign 1.0; Return 1.07; T-Stat 4.38; Key Table 2E; Test "port sort"; Stock Weight EW;
Portfolio Period 1; Start Month 12; Acronym2 RIO_IdioRisk; Predictability 1_clear; Signal Rep Quality 1_good; GScholarCites 1,500.
Detailed Definition: "Follow RIO_MB, except define volatility as the rolling standard deviation of the last 12 months of the stock
return. Let RIO_Disp = lagged RIO quintile if the Volatility quintile == 5".

## 10. Proposed Sharadar mappings and deviations (only if the owner overrides `infeasible`)

- `instown_perc` -> SF3: sum of `units` over investors with `securitytype == SHR` per (ticker, quarter), divided by shares
  outstanding; SF3A `shrunits` as a cross-check. No field_map key exists: field-checker needed (and the DelBreadth frontier row's
  caveats on availability dates and 13F amendments apply). Not in `field_map_index.yaml`.
- `mve_c` -> `DAILY.marketcap` x 1000 (the quadratic term is not scale-invariant: $ thousands in OSAP, $ millions in Sharadar).
- Volatility from `ctx.monthly_closeadj(12)` returns, std ddof 1, min 6 (window `history_months=13`).
- Missing-13F zero-fill (OSAP) to be reported, not reproduced across a whole era.
- Recommendation: `infeasible` (class `data_start`: 94-96 < 120 scorable months; also coverage ~20% < 40% and a 5-level mass point).
