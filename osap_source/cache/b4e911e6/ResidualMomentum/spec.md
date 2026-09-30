# ResidualMomentum — Momentum based on FF3 residuals (Blitz, Huij and Martens 2011, Table 2B 1M)

OSAP ref b4e911e69678a7424f318617a61d813f54183123. Script emitting it: `Signals/pyCode/Predictors/ZZ1_ResidualMomentum6m_ResidualMomentum.py`
(cached as `predictor.py`; also emits the placebo ResidualMomentum6m, not specced). The SignalDoc row with Cat.Signal == Predictor
(`signaldoc_row.csv`) is the authority. Upstream read: `upstream_CRSPMonthly.py`, `upstream_FamaFrenchMonthly.py`, `legacy_stata.do`.
Measured on THIS snapshot, DATA_SHA 198b281de1a0, harness universe, 276 decision months (signals 1998-12-31..2021-11-30).

## 1. Data availability (verdict: APPROX, constructible; no missing input, no zero-fill)

| input (OSAP) | field_map key | Sharadar source | status |
|---|---|---|---|
| `ret` (monthlyCRSP, incl. delisting return) | `crsp.ret` | `SEP.closeadj` month-end ratio (`ctx.monthly_closeadj`) | mapped; no dlret, 3-dp closeadj grid |
| `mktrf`, `smb`, `hml` (monthlyFF, Ken French) | not in index (`public_sources`) | `ctx.monthly_ff3(n)` mkt/smb/hml (harness rebuild; monthly portfolio-return SMB/HML) | harness accessor; mkt RAW |
| `rf` | not in snapshot | omitted | see section 10 |

Not used: IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob, ppegt, any SF1 level as signal. Declare inputs
`SEP.closeadj`, `DAILY.marketcap`, `SF1.equity`, `SF1.assets`, `SF1.liabilities`, `SF1.taxliabilities` (ff3 build inputs).
Verdict `approx` (factor rebuild, no rf, no delisting return), NOT `data_start`: 223 scorable months (see 8).

## 2. Variables (exact source names)
`permno`, `time_avail_m`, `ret`; `rf`, `mktrf`, `hml`, `smb`; derived `retrf = ret - rf`, `_residuals`, `temp`, `mean11_temp`, `sd11_temp`.

## 3. Formula
For each stock, a ROLLING 36-observation OLS of `retrf` on [const, mktrf, hml, smb] (min_periods 36); `_residuals_m` = the
regression residual of the window's LAST observation (month m, window m-35..m; in-sample, fit includes m). Then
`temp_t = _residuals_{t-1}` (skip the most recent month), and
```
ResidualMomentum_t = mean(temp over 11 obs) / sd(temp over 11 obs, ddof=1)      # min 11 obs, = residuals of months t-11 .. t-1
```
Ratio of the mean to the std of eleven residuals (an information-ratio-like score, not a cumulative return). Raw value, no log.

## 4. Timing / lag
OSAP row t uses returns through month t-1 (month t's own return is skipped; the signal is used for the t+1 return). Mapping: signal at
decision month-end s uses monthly returns s-46 .. s-1 (46 of them: 11 residuals, each from a 36-month window ending s-11 .. s-1), i.e.
closes s-47 .. s-1: `px = ctx.monthly_closeadj(47)` has 48 columns (s-47..s); DROP the last column (month s). Price-only, no filing date:
ART vs ARQ and as-of-filing are irrelevant; no flow item smears. The factor months are causal (June-formed, read only through each month).

## 5. Filters
None in the predictor. SignalDoc Filter `abs(prc)>1`; the harness universe (price >= $1, cap and dollar-volume screens) covers it.

## 6. Predicted sign (SignalDoc)
`Sign = +1.0` -> `ascending=True` (high residual momentum is the long leg). Cat.Economic `momentum`, Cat.Data `Price`, Cat.Form `continuous`.

## 7. The mass-point question
A do-nothing firm (flat price every month) has residual 0 in every window month: mean 0 / sd 0 -> NaN (0/0), dropped, not a value.
No exact tie value otherwise: the ratio is a continuous statistic. Measured on all 223 scorable months: max modal-value share 0.124%
(mean 0.062%), distinct values = scored names, `qcut` yields 10 bins in every scorable month. Tie handling: null on non-finite, else average rank.

## 8. History needed, measured coverage (momentum_partial_windows decision)
- OSAP needs the full 36-row window (min_periods 36) for each of the 11 residuals and min 11 residuals: a window of 46 consecutive
  monthly returns. The FULL-WINDOW rule is OSAP's own here (only calendar gaps differ: OSAP counts rows, this counts months, so a name
  with a missing month is NaN here). Declare `history_months = 47` (`has_price_at(47)`), `lookback_months = 47`.
- Data start: smb/hml exist from July 1999 (first complete monthly label 1999-07-30). The earliest window needs 46 monthly returns
  from 1999-07, so the FIRST scorable signal is 2003-05-30; the 53 leading months (1998-12..2003-04) are NaN for every name.
- Scorable months: 223 of 276 (2003-05-30 .. 2021-11-30) >= `rebalance.min_months` 120. By half (138 signals each): 1st half 85 scorable (2003-05..2010-05), 2nd half 138.
- Coverage of the universe: mean 87.2% over the 223 scorable months (min 78.3% at 2021-11-30, max 92.9%); 70.4% pooled over all 276.
  Scored names per month: min 1,541, median 1,616. Coverage loss = names lacking 47 consecutive month-end prices (recent IPOs).
- Measured with a prototype of section 4 against `ctx.monthly_closeadj` and `ctx.monthly_ff3`, np.linalg.lstsq per rolling window, all 276 months.

## 9. OSAP metadata
Acronym `ResidualMomentum`; Acronym2 MomResid; Authors Blitz, Huij and Martens; Year 2011; Journal JEmpFin; Sample 1930-2009;
Predictability in OP 1_clear; Signal Rep Quality 1_good; Test "LS FF+ alpha" (Table 2B 1M: the 1M is the holding period); Stock
Weight EW; LS Quantile 0.1; Portfolio Period 1; Start Month 12; Filter abs(prc)>1; GScholarCites 346. Detailed Definition: "Run a
rolling regression over 36 months of excess return on mktrf, smb, hml; idiosyncratic return is the one-month lagged residual;
ResidualMomentum is the rolling mean over the past 11 months divided by the rolling std."

## 10. Proposed Sharadar mappings and deviations
- `ret` -> `SEP.closeadj[s]/closeadj[s-1] - 1` on the business month-end grid (`ctx.monthly_closeadj(47)`); no delisting return; NaN month -> name NaN.
- `mktrf/smb/hml` -> `ctx.monthly_ff3(48)` cols mkt/smb/hml re-indexed to the return months; NOT Ken French (NYSE-breakpoint 2x3 on SF1
  book equity + DAILY.marketcap, current-TICKERS exchange, no preferred stock in BE, no delisting return, mkt RAW).
- `rf` omitted: stock return and mkt both RAW. A small deviation, not zero: (r - rf) on (mkt - rf) differs from r on mkt by
  (1-beta)(rf_t - mean rf) inside a window; rf varies about 0.1-0.4%/month vs idiosyncratic sd about 10%/month. State it in the docstring.
- In-sample last-observation residual (each of 11 windows fit including the residual month), exactly as OSAP.
- Full calendar window required (see 8); `ddof = 1` for the sd (pl `rolling_std`); sd = 0 -> NaN.
- Fields not in the index: the ff3 accessor (harness, like IdioVol3F). `crsp.ret` monthly form is mapped in the index.
- Field-checker: only the first complete-factor month of `monthly_ff3` (measured here: 1999-07-30) and `crsp.ret` monthly form.
