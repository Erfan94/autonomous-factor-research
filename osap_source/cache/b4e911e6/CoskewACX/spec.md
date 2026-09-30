# CoskewACX — Coskewness from daily returns (Ang, Chen and Xing 2006, RFS, Table 8B)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/CoskewACX.py` (cached `predictor.py`,
`signaldoc_row.csv`). Upstream `dailyCRSP` / `dailyFF` builders are not cached; described from `predictor.py`.
DATA_SHA 198b281de1a0. field_map statuses are mappings, not proofs, until the field-checker verifies them.

## 1. Data availability — VERDICT: APPROX (every input constructible; declared substitutions; no zero-fill term)

| input (OSAP) | field_map key | Sharadar source | status | note |
|---|---|---|---|---|
| `ret` (dailyCRSP daily total return) | `crsp.ret` (daily form) | `SEP.closeadj[d]/closeadj[d-1]-1` on consecutive market trading days (`ctx.daily("SEP",["closeadj"],days_back)`) | mapped | total return; NO dlret; 3-dp closeadj grid quantises sub-$0.50 prices (universe price >= $1 limits this); no-trade days carry the price (return 0) |
| `mktrf + rf` (dailyFF) -> `mkt` | none; `public_sources` ruling | `ctx.market_daily(days_back)` raw VW market (SEP.closeadj + DAILY.marketcap) | harness accessor | `mktrf + rf` IS the raw total market return, so the harness series is the right object; it is a reconstruction (common stock NYSE/NASDAQ/NYSEMKT per current TICKERS, prior-day cap weights, causal bad-print guards, no dlret, gap returns excluded), not Ken French's |
| `rf` | none (not in snapshot) | omitted | unavailable | used only inside `ln(1+x) - ln(1+rf)`; the signal DE-MEANS both series over the window, so a constant rf cancels exactly; rf's day-to-day variation (~1e-4) is immaterial against 1-2% daily stock vol |

- Declare `FactorDef.inputs`: `SEP.closeadj`, `DAILY.marketcap`.
- Not used: any SF1 field, IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob, ppegt.
- Why APPROX not feasible: market series is a Sharadar-native reconstruction; rf omitted (near-exact); no DLRET; and
  the OSAP window starts 1962 so a full window always exists (see section 8).

## 2. Variables (exact source names)
`ret`, `mktrf`, `rf` (daily), `permno`, `time_d`; derived `mkt = mktrf + rf`, log excess returns `ret`, `mkt`.

## 3. Formula
Per stock and per 12-CALENDAR-MONTH window ending in month T (all days from the first day of month T-11 through the
last day of month T; a window exists only if the stock has a row in month T). On days where both are present:
```
mkt = ln(1+mkt) - ln(1+rf);   ret = ln(1+ret) - ln(1+rf)          # continuous excess returns
r~ = ret - mean(ret over the stock's window days);  m~ = mkt - mean(mkt over the SAME days)
CoskewACX = mean(r~ * m~^2) / ( sqrt(mean(r~^2)) * mean(m~^2) )   # population (1/n) moments, no df correction
```
Observation filter: `nobs` (non-null days) must be within 5 of `max_nobs`, the maximum `nobs` across all stocks
sharing that window label; in practice max_nobs = number of market trading days in the window, so a stock needs
n_valid >= N_market_days - 5. No absolute minimum. Translator equivalent: r from consecutive SEP rows over the window
days, m = `ctx.market_daily(...)` filtered to (BME(t-12), t]; both windows use the same dates; N = count of market
days in the window. Non-finite result (mean(r~^2) == 0, e.g. a stale name) -> NaN, never inf.

## 4. Timing and lag
Signal at month-end t uses returns through t (window includes the signal month); held over t+1. No extra lag (OSAP
`time_avail_m` = T). Price-only: no filing date, no ART/ARQ issue, `dimension` default, nothing smears. No look-ahead:
`daily` and `market_daily` are bounded by `signal_asof`.

## 5. Filters
OSAP predictor file: only the `max_nobs - nobs <= 5` rule and `ret`/`mktrf`/`rf` non-null after the inner FF merge.
SignalDoc Filter: `shrcd<=11, exchcd==1` (portfolio step: common stock, NYSE only), LS Quantile 0.2, EW. NYSE-only is not
reproducible (TICKERS.exchange is current-only) and is superseded by the harness universe (deviation; quintile -> decile).

## 6. Predicted sign (SignalDoc)
`Sign = -1.0`: high coskewness predicts LOW subsequent return; `ascending=False` (low raw value attractive). Cat.Economic
`risk`, Cat.Data `Price`, Cat.Form `continuous`. Sample 1963-2001, T-Stat 2.76, Return 0.28 (% per month, EW quintile LS),
Key Table 8B, test "port sort". A flipped sign is a second hypothesis (|t| >= 2.74).

## 7. The mass-point question
Continuous ratio of sample moments: a do-nothing firm (no price change ever in the window) has mean(r~^2) = 0 -> 0/0 ->
NaN, not a value; such names drop out (NaN guard). Names with very many zero-return days (illiquid) still get a finite,
non-degenerate value. Exact ties: ~0%; stale/zero-return share among universe names with n_valid >= N-5 and price >= $1
is small (<1%, to be measured in preflight). Ties: rank average (harness default).

## 8. History needed
- Window: 12 months (~252 trading days). Declare `history_months=12`, `lookback_months=12`.
- Measured constraints: `market_daily` starts 1998-12-02 (DAILY.marketcap 1998-12-01, a data limit); SEP starts
  1997-12-31. A window ending at signal 1999-12-31 is (1998-12-31, 1999-12-31] and is fully covered; signals
  1999-01..1999-11 have a PARTIAL market window (20-230 days). OSAP always has a full year, and the N-5 rule alone
  would admit a 21-day window (a third moment on 21 days is noise). PROPOSED: null the signal unless the market
  window holds >= 230 days (translator's pass through `ctx.market_daily(days_back, min_days=230)`), so the first
  scorable signal is 1999-12 and ~11 of the 276 decision months (4%) are unscorable for every name. A declared
  deviation; preflight must report the first scorable month.
- Coverage after that: share of universe names with n_valid >= N-5 (excludes <1y listings, long halts); estimate
  85-95%, measure in preflight.

## 9. OSAP metadata
Acronym CoskewACX; LongDescription "Coskewness using daily returns"; Authors Ang, Chen and Xing; Year 2006; Journal RFS;
Sample 1963-2001; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Signal Predictor; Cat.Economic risk;
Cat.Data Price; Cat.Form continuous; Sign -1.0; Return 0.28; T-Stat 2.76; Key Table 8B; Test port sort; Stock Weight EW;
LS Quantile 0.2; Portfolio Period 1; Start Month 12; Filter `shrcd<=11, exchcd==1`. Notes: used mainly as a control in the
paper; ACX use de-meaned returns rather than CAPM residuals, daily data, equal weighting. Detailed Definition: sample
counterpart of E[r~ m~^2]/(SD[r~] SD[m~]^2), past year of daily data, NYSE CRSP VW index, continuously compounded.

## 10. Proposed Sharadar mappings and deviations
- `ret` -> daily `SEP.closeadj` ratio on consecutive rows (`crsp.ret`, mapped). Deviation: no dlret; gap handling as SEP
  rows, not CRSP.
- `mkt` (mktrf + rf) -> `ctx.market_daily(days_back)` VW raw. Not in the field index: a harness accessor. Deviation:
  reconstruction, not CRSP/FF; OSAP's code uses the FF all-stock market although the SignalDoc text says NYSE VW.
- `rf` -> omitted (cancels under de-meaning). Deviation near-zero for this signal.
- Log returns kept: `ln(closeadj_d/closeadj_{d-1})` and `ln(1+mkt)` (no rf subtraction).
- Window = calendar 12 months with the market window held to the same dates; `max_nobs` -> N market days in window.
- Partial-window gate (section 8). `dimension` default. Fields not in the field map: none besides the harness accessor.
- Expect very high overlap with `Coskewness` (same moment ratio, monthly 60m vs daily 12m) and a link to beta/idio-vol:
  a Phase C / Stage 2 point, not a construction one.
