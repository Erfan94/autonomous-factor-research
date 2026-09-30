# BetaTailRisk — Tail risk beta (Kelly and Jiang 2014, RFS, Table 4A EW)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/BetaTailRisk.py` (cached `predictor.py`,
`signaldoc_row.csv`, `upstream_CRSPDaily.py`, `upstream_CRSPMonthly.py`). DATA_SHA 198b281de1a0.

## 1. Data availability (verdict: APPROX; no missing input, no zero-fill; one market series rebuilt by the harness)

| input (OSAP) | field_map key | Sharadar source | status | note |
|---|---|---|---|---|
| `dailyCRSP.ret` (all CRSP firms, every share code/exchange) | `crsp.ret` (daily form) | harness-built `MonthContext.monthly_tailex` (pools SEP.closeadj day-over-day returns of market constituents) | mapped, verified_on 2026-09-30 | the pool is common stock on NYSE/NASDAQ/NYSEMKT, not all of CRSP |
| `monthlyCRSP.ret` (monthly stock return, incl. dlret) | `crsp.ret` (monthly form), `crsp.dlret` | `ctx.monthly_closeadj(120)` ratio of adjacent business month-ends | mapped; `crsp.dlret` unavailable | no delisting return (config returns.delisting proxy applies at the harness forward-return level only) |
| `monthlyCRSP.shrcd` (<= 11) | `crsp.shrcd` | universe (TICKERS category Domestic Common Stock*) | approx | harness universe already restricts to US common |
| `TailRisk` monthly factor (tailex) | NOT in field_map or the index (no key) | `MonthContext.monthly_tailex(months_back)`, data_layer.py lines ~1502-1600, 2953 | harness accessor, not a field | EXISTS; its docstring names BetaTailRisk as the consumer; causal (rows after signal_asof cut before reindex) |

- No Compustat/SF1, IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob, ppegt. No OSAP zero-fill.
- Why APPROX, not infeasible: every term is reconstructable from SEP. Declared deviations (accessor docstring, block
  comment at data_layer.py ~930-1095): (a) tail pool is listed-exchange common stock, not all of CRSP; (b) the market
  builder's bad-print guard drops daily r < -80% (measured by the harness author on DATA_SHA 52402f7d1f9c,
  1999-2022: |tailex - tailex_unguarded| mean 0.0008, max 0.0057, corr 0.9999; tailex std 0.059); (c) no delisting
  returns; (d) zero-volume days dropped from the pool (the next traded day's two-day return kept); (e) no price
  screen in the pool, as OSAP. The 72-obs/120-month regression on monthly stock returns is rank-robust to these.
- Declare `FactorDef.inputs`: `SEP.closeadj`, `SEP.volume` (tailex needs volume>0), `DAILY.marketcap` is NOT needed
  (tailex needs no DAILY row; data_layer comment "tailex needs no DAILY row, so it starts with SEP (1998-01)").
  The accessor docstring asks for `SEP.closeadj` and `SEP.volume` only.

## 2. Variables (exact source names)

`ret` (monthly stock return, monthlyCRSP), `tailex` (monthly, TailRisk.parquet; built from daily `ret`),
`retp5` (monthly 5th percentile of the pooled daily returns), `time_avail_m`, `shrcd`. Output column `BetaTailRisk`.

## 3. Formula

Part 1 (market-wide series; one number per month, same for every stock):
- `retp5_m` = 5th percentile of ALL pooled daily returns of month m, `quantile(0.05, interpolation="lower")`.
- keep daily obs with `ret <= retp5_m`; `tailex_m = mean( log(ret / retp5_m) )` over those obs.
Part 2 (per stock): rolling OLS of the stock's monthly `ret` on `tailex` WITH intercept, 120-row window, min 72
non-null pairs (`null_policy="drop"`), `BetaTailRisk` = slope on `tailex`:

    ret.least_squares.rolling_ols(tailex, window_size=120, min_periods=72, mode="coefficients",
                                  add_intercept=True, null_policy="drop").over("permno")
    BetaTailRisk = coef["tailex"];  filter: BetaTailRisk not null & shrcd <= 11

Harness form: `tx = ctx.monthly_tailex(120)`; stock returns from `ctx.monthly_closeadj(120)` (121 month-ends -> 120
returns, aligned on month-end; tailex_m uses calendar-month days, the return uses (BME(m-1), BME(m)], same span up to
weekends). Per stock: pairs where both finite, n >= 72, var(tailex over the pairs) > 0; slope = cov/var (vectorised
across names, pairwise-complete). NaN below 72 pairs; never floor.

## 4. Timing / lag

- OSAP: signal at month t uses the month-t return and month-t tailex (contemporaneous, no lag in this file); the
  value is the row for `time_avail_m = t`, traded into t+1. The harness signal_asof is the last trading day of month
  t, so month t is complete and the window ends at t: same convention. No publication lag; no SF1 input, so ART-as-of-
  filing and ARQ/TTM smearing are irrelevant.
- Do NOT use `ctx.partial_months` data: the signal month is complete by construction; a month with < 15 pooled days
  (TAIL_MIN_DAYS) or 1997-12 is NaN in tailex (pair simply dropped).

## 5. Filters

OSAP code: `shrcd <= 11`, non-null beta, (SignalDoc Filter `abs(prc)>5`, "Exclude if price less than 5" — NOT in the
.py; the code applies shrcd only). Harness universe (price >= $1, cap/ADV bands, US common) sits outside the factor;
the price > 5 filter in the SignalDoc is not reproduced (the universe decides). Note in docstring.

## 6. Predicted sign (SignalDoc)

`Sign = 1.0`: high BetaTailRisk is the long side. Return 0.33, T-Stat 2.48, Test `port sort`, Stock Weight EW, LS
Quantile 0.2, Portfolio Period 1, Start Month 12, Sample 1963-2010, Cat.Signal Predictor, Cat.Economic `risk`, Cat.Data
Price, Cat.Form continuous, Predictability in OP `1_clear`, Signal Rep Quality `1_good`. Orient by SignalDoc Sign
as written; a flipped-sign screen is a second hypothesis (|t| >= 2.74). Note: tailex rises in market tail events, so
the regression slope's scale is per unit of a positive series (intercept absorbs the mean); orientation is not
re-derived from the paper.

## 7. The mass-point question

- Raw values continuous (OLS slope). Do-nothing firm: constant closeadj -> every monthly ret = 0 -> slope exactly 0.0
  (a mass point at 0 for such names only). In this universe (price >= $1, cap >= NYSE 20th pctile, traded) a 72+ month
  run of zero monthly returns is essentially nonexistent: expected share 0%. Preflight to measure mode% and distinct.
- Cross-sectional dependence, not ties: tailex is one common series and the window is 120 months, so betas move
  slowly and adjacent months' values are close to identical (high persistence; turnover is low). Ties in floats: none.
- NaN share: a name with < 72 valid monthly returns in its last 120 months (recent IPO) is NaN (see 8).

## 8. History needed (snapshot starts 1998-01)

- `history_months = 72` (min pairs), `lookback_months = 120` (window). The pool has tailex from 1998-01 (1997-12 blank);
  the 72nd valid month is 2003-12. Stock side: SEP starts 1997-12-31, so the first return is 1998-01 and a name
  needs 72 monthly returns: first scorable signal month 2003-12-31 for names listed from 1997-12. Decision months
  1999-01 .. 2003-11 (59 of 276, ~21%) are data-null; the window is also short (72-119 months) until 2007-12.
  Early-window coverage is a data fact, not a factor fault; preflight reports coverage by year and the ~79% sample share.
- Name needs a trade at BME(t-119) only if the translator demands a full window; OSAP needs 72 valid, not a full one:
  do NOT require `has_price_at(120)` (that would push the first scorable month to 2008-01). Gate on the count of
  valid pairs instead (history_months=72 gate via has_price_at(72) is acceptable).
- Stage 1 bars: coverage >= 40% is per-month average over the window; with ~21% null months the mean must still
  clear 40% on the scored months — preflight measures.

## 9. OSAP metadata

Acronym BetaTailRisk; Kelly and Jiang 2014 RFS, "Tail risk and asset prices"; LongDescription "Tail risk beta";
Key Table `4A EW`; Sample 1963-2010; Portfolio Period 1; Start Month 12; GScholarCites202509 1020. Detailed
Definition: 5th percentile of daily returns across firms each month; tailEX = mean log(ret / p5) over returns below;
BetaTailRisk = 120-month rolling regression coefficient of firm return on tailEX; exclude price < 5 or shrcd > 11.
Legacy Stata: Signals/LegacyStataCode/Predictors/BetaTailRisk.do.

## 10. Proposed Sharadar mappings and deviations

| OSAP | Sharadar | deviation |
|---|---|---|
| `ret` monthly | `ctx.monthly_closeadj(120)` month-end ratio (split+dividend adjusted) | no dlret; last-row month gaps give NaN, not a carried price |
| `tailex` | `ctx.monthly_tailex(120)` | listed-exchange common-stock pool; r < -80% guard; zero-volume days out; 1998-01 start |
| rolling OLS window 120 rows, min 72 | numpy over the 120 month-end columns, pairwise complete, n>=72 | OSAP windows by ROWS (a gap month in a stock's CRSP history shortens calendar span); harness windows by calendar months |
| intercept | fitted (slope = cov/var) | none |
| `shrcd <= 11`, price > 5 (SignalDoc only) | harness universe | price > 5 not applied |
| sector rank / hedge / filters | harness | none |

Flags: no field_map key for `tailex` (declare in docstring); no `dlret`; inputs `SEP.closeadj`, `SEP.volume`.
Translator must call `ctx.monthly_tailex` and `ctx.monthly_closeadj` only, with `history_months` and `lookback_months`.
