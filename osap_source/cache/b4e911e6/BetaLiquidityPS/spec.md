# BetaLiquidityPS — Pastor-Stambaugh liquidity beta (Pastor and Stambaugh 2003, Table 4A CAPM 10-1)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/BetaLiquidityPS.py` (cached
`predictor.py`, `signaldoc_row.csv`, `LiquidityFactor_download.py` = the WRDS `ff.liq_ps` pull). DATA_SHA
198b281de1a0. field_map statuses are mappings, not proofs, until the field-checker verifies them.

## 1. Data availability (verdict: APPROX; no missing input, but two market-wide monthly series are REBUILT)

| input (OSAP) | source in OSAP | Sharadar / harness | status | note |
|---|---|---|---|---|
| `ret` (monthlyCRSP) | CRSP monthly | `ctx.monthly_closeadj(60)` adjacent-month-end ratio (SEP.closeadj) | mapped (`crsp.ret`, verified 2026-09-30) | total return; no dlret |
| `ps_innov` (monthlyLiquidity) | WRDS `ff.liq_ps` = Pastor's published file | `ctx.monthly_ps_innov(60)` = `build_ps_innov_monthly` | harness REBUILD, not in field_map | NOT PS's series; see deviations |
| `mktrf`, `smb`, `hml` (monthlyFF) | WRDS `ff.factors_monthly` | `ctx.monthly_ff3(60)` columns mkt, smb, hml (`build_ff3_daily`) | harness REBUILD | `mkt` is RAW, not Mkt-RF |
| `rf` (monthlyFF) | WRDS | none held | unavailable | omitted; see deviations |
| `permno`/`time_avail_m` | CRSP | SEP presence | mapped | history gate only |

- Why APPROX, not infeasible: no Compustat item is missing and no zero-fill is involved; the PS series and the
  French factors are rebuilt by the harness from SEP/DAILY/ACTIONS/SF1 (data_layer.py block comments; the PS block
  names BetaLiquidityPS as a consumer). They approximate the published series, hence approx.
- No IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob, ppegt, Compustat input.
- Inputs to declare in FactorDef.inputs (from the accessors' docstrings): `SEP.closeadj`, `SEP.close`,
  `SEP.volume`, `SEP.closeunadj`, `DAILY.marketcap`, `ACTIONS.contraname` (ps_innov); `SF1.equity`,
  `SF1.assets`, `SF1.liabilities`, `SF1.taxliabilities` (ff3 book equity, ARY). Field-checker: confirm the harness
  accessors' own inputs are the verified ones; there is no new field_map key, flag the ps/ff3 series as harness rows.
- Machinery (read, not run): `monthly_ps_innov`, `monthly_ff3`, `monthly_market` exist in `harness/data_layer.py`
  and are wired in `run_test.py` (`set_ps_loader`); preflight must confirm the caches build on this DATA_SHA.

## 2. Variables (exact source names)

`ret`, `rf`, `mktrf`, `hml`, `smb`, `ps_innov`, `time_avail_m`, `permno`. Derived `retrf = ret - rf`.

## 3. Formula

Per stock, a rolling 60-ROW OLS with intercept of the monthly excess return on four regressors; the coefficient on
`ps_innov` is the signal; rows with any null dropped; window needs >= 36 non-null observations.
```
df = crsp.join(ff, on="time_avail_m", how="inner").join(liquidity, on="time_avail_m", how="left")
retrf = ret - rf
retrf.least_squares.rolling_ols(ps_innov, mktrf, hml, smb, window_size=60, min_periods=36,
        mode="coefficients", add_intercept=True, null_policy="drop").over("permno")
BetaLiquidityPS = coef["ps_innov"]      # null rows dropped
```
Window is the stock's last 60 own monthly rows INCLUDING month t (60 calendar months in a gap-free listing; OSAP
reaches further back after a gap, the translator uses the 60 business month-ends ending at t). Multivariate:
all four regressors enter jointly, so the ps coefficient is partialled on mkt, hml, smb (not a univariate beta).
Translator equivalent: r = 60 returns from `monthly_closeadj(60)` (61 columns); X = `monthly_ps_innov(60)`,
`monthly_ff3(60)[["mkt","hml","smb"]]` on the same 60 month-ends; per stock keep months where y and all four
X are finite; require n >= 36 and a full-rank design, else NaN.

## 4. Timing and lag

- Signal at month-end t includes month t's return and month t's ps_innov (both known at BME(t)); the portfolio
  earns t+1. No fundamentals enter the signal, so no ART/ARQ or filing-date question for the predictor itself
  (ff3 book equity is ARY, datekey <= the June formation date). Nothing smears.
- Causality of the rebuilt ps_innov: the default series (`refit=False`) uses an EXPANDING AR fit; each month's
  value reads nothing after its own month (tested in harness). `refit=True` re-fits once through the signal month and
  returns PS's full-sample shape as of t, also causal, costlier per signal. Recommend the default; the translator
  may note refit=True as a sensitivity. Both give the same last value.

## 5. Filters

None in the predictor file beyond the 36-observation minimum and the inner merges. SignalDoc Filter column:
`abs(prc)>5` (a portfolio-level screen in the paper replication, not code in BetaLiquidityPS.py). Do NOT implement it
in the factor (no filters in a factor); the harness universe (price >= $1, NYSE 20th cap pct, ADV) applies.
Declare the $5 screen as a deviation of the harness universe.

## 6. Predicted sign (SignalDoc)

`Sign = 1.0`: high liquidity beta predicts a HIGH subsequent return (liquidity-risk premium; Cat.Economic
`liquidity`, Cat.Data `Price`, Cat.Form `continuous`; sample 1968-1999, t = 2.54 in VW CAPM alpha). Stock weight VW,
LS quantile 0.1. `ascending=True`. A flipped sign is a second hypothesis (|t| >= 2.74).

## 7. The mass-point question

Continuous regression coefficient. No do-nothing value; a name with an identical return history has an identical
beta (negligible). A stock whose monthly return is constant (stale price) over the window gets a coefficient near
0 (the regression is degenerate; guard with the full-rank test); the universe's price and dollar-volume screens
remove most such names, expected share ~0%. Measure in preflight. Ties: average rank, no tie-breaker.

## 8. History needed (snapshot starts 1998-01)

- OSAP: window 60 rows, minimum 36 non-null. Declare `history_months=60` would null everything until 2002-12;
  do not gate on 60. Gate on the ps_innov/ff availability instead and let the >= 36 rule bind.
- Constraint chain on THIS snapshot (from data_layer comments, NOT yet run; preflight to confirm): DAILY.marketcap
  starts 1998-12 so the market series starts 1998-12-02 and `monthly_market`/ff3 blank 1998-12; `m_t` (a t-1 cap) is
  first defined 1999-01, dgamma 1999-02, the lagged regressor 1999-03, and `ps_innov` needs 24 regression months
  (PS_MIN_MONTHS), so the first ps_innov is ~2001-02. smb/hml start after the June-1999 formation (July 1999),
  which is earlier than ps_innov, so not binding.
- Hence 36 non-null ps_innov months in a window first exist at the ~2004-01 signal. Signals 1999-01 .. ~2003-12 (about
  60 of the 276 decision months, ~22%) are unscorable for EVERY name, not a defect. Expect the coverage and
  LS-months floors to be measured on scored months only; preflight must report the first scorable month and the ramp.
  Until ~2006-01 the window holds 36-59 valid ps months (same noisier ramp as OSAP's early years).
## 9. Deviations to declare (what the translator must put in the docstring)

1. `ps_innov` is a rebuild: NYSE/AMEX common stock priced $5-$1000, exchange as of t-1 (`PS_EXCHANGE_RULE="retro"`),
   daily per-stock gamma on dollar volume in $M, m_t-scaled mean change, AR residual (lagged dgamma, lagged scaled gamma_hat) on an EXPANDING window,
   scale ~2e-5 (a positive constant: ranks unchanged). Residual autocorrelation 0.13 (harness comment). Category is
   TICKERS' current category; no delisting returns, no gap returns, daily r < -80% / > +100% and no-trade days
   dropped, r_m the harness's raw VW market. Correlation with PS's own series is unknown (no reference file held).
2. No rf: y = raw `ret`, mkt = raw VW market. Substituting raw for excess moves `(1-b_mkt) x rf_t` into the error.
   rf is slow-moving and ps_innov is nearly uncorrelated with it, so the ps coefficient is far less affected than a
   market beta would be; small, but rf varied ~5%/yr to ~0 over 1999-2021, so the translator should bound it in a
   preflight diagnostic rather than assume.
3. smb/hml rebuilt (2x3 June sorts, NYSE breakpoints from CURRENT TICKERS exchange, BE = equity + taxliabilities,
   no preferred, no delisting returns); monthly smb/hml are portfolio-compounded, French-style.
4. Window is the business-month-end grid, not CRSP rows (missing months reduce n, not stretch the window).
5. `abs(prc)>5` not applied; scored names are not exchange-restricted (only the liquidity series is NYSE/AMEX).

## 10. OSAP metadata

Acronym `BetaLiquidityPS`; "Pastor-Stambaugh liquidity beta"; Pastor and Stambaugh 2003, JPE; Predictor, continuous,
Price, Cat.Economic liquidity; OP 1_clear, rep quality 1_good; sample 1968-1999; Key Table 4A CAPM 10-1 (port sort
CAPM alpha); Sign 1.0; Return 0.5333; T-Stat 2.54; VW; LS Quantile 0.1; Portfolio Period 12; Start Month 12;
Filter `abs(prc)>5`. Definition: monthly excess return on Pastor's innovations, 60-month window, >= 36 observations.
## 11. Proposed mappings and flags

- y `monthly_closeadj(60)` returns; X `monthly_ps_innov(60)` + `monthly_ff3(60)` mkt/hml/smb; per-stock masks
  (n >= 36, full rank); vectorise over names. Not in field_map: the ps and ff3 series (harness accessors, no key)
  and `rf` (unavailable, omitted). Field-checker verifies only the accessors' underlying SEP/DAILY/ACTIONS/SF1 keys.
