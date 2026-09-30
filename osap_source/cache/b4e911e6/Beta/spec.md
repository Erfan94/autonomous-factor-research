# Beta — CAPM beta (Fama and MacBeth 1973, Table 3A, t(gamma_1))

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/Beta.py` (cached `predictor.py`,
`signaldoc_row.csv`). DATA_SHA 198b281de1a0. field_map statuses are mappings, not proofs, until the
field-checker verifies them on this snapshot. Upstream `monthlyCRSP`, `monthlyFF`, `monthlyMarket`
builders are not cached for this acronym; their content is described from `predictor.py` only.

## 1. Data availability (verdict: APPROX, no missing input; one declared substitution set)

| input (OSAP) | field_map key | Sharadar source | field_map status | note |
|---|---|---|---|---|
| `ret` (monthlyCRSP, stock monthly return) | `crsp.ret` | `ctx.monthly_closeadj(60)` ratio of adjacent business month-ends (SEP.closeadj) | mapped | total return (splits+dividends); NO dlret (`crsp.dlret` unavailable) |
| `ewretd` (monthlyMarket, CRSP equal-weighted market) | none in index (public_sources note: no index series held) | `ctx.monthly_market(60, col="ew")` (harness-built from the market's own name-days) | harness accessor, not a field | EXISTS: data_layer.py `MonthContext.monthly_market`, docstring names Beta (FETCH-02) as its motivating consumer; guards per `market_daily` |
| `rf` (monthlyFF) | none; field_map `public_sources` states rf is NOT in the snapshot | omitted | unavailable | see deviations |
| `permno`/`time_avail_m` row presence | `crsp.smt_row` (only if translator uses has_price_at) | SEP month presence | mapped | history gate |

- Inputs to declare in FactorDef.inputs: `SEP.closeadj`, `DAILY.marketcap` (market series weights/calendar).
- Not used: any Compustat/SF1 field, IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob,
  ppegt. No OSAP zero-fill term exists in Beta.
- Why APPROX and not infeasible: rf is not a Compustat item and no zero-fill is involved; its omission changes
  the regression from (r-rf) on (m-rf) to r on m. rf is slow-moving, so this moves a 60-month slope only
  slightly (field_map `public_sources` makes the same statement for daily windows; for MONTHLY windows rf
  varies over 1999-2021 from ~5%/yr to ~0, so the shift is larger than the daily case and should be
  measured by the translator against an in-harness check, not assumed).
- `ewretd` is reconstructed, not CRSP's: common stock on the universe's exchanges (TICKERS current
  category/exchange), no size/price screen, equal-weighted mean of the same name-days; returns across a
  trading gap and delisting returns are excluded; >+100% / <-80% daily prints are dropped causally.
  Microcap-heavy equal weighting makes the EW series more sensitive to these exclusions than the VW series.

## 2. Variables (exact source names)

`ret`, `rf`, `ewretd`, `time_avail_m`, `permno`. Derived: `retrf = ret - rf`, `ewmktrf = ewretd - rf`.

## 3. Formula

Beta = OLS slope (with intercept) of the stock's monthly excess return on the EW market excess return over a
rolling window of the last 60 monthly observations of that stock, requiring at least 20 valid observations.
```
retrf   = ret - rf ;  ewmktrf = ewretd - rf
retrf.least_squares.rolling_ols(ewmktrf, window_size=60, min_periods=20,
        mode="coefficients", add_intercept=True, null_policy="drop").over("permno")
Beta = coef["ewmktrf"]        # rows with null Beta dropped
```
Window is 60 ROWS of the stock's own monthly history (the row-count window includes the current month t),
not 60 calendar months; with a gap in a stock's listing the OSAP window reaches further back. Translator
equivalent: r = 60 monthly returns ending at t (`monthly_closeadj(60)` has 61 columns), m = `monthly_market(60,
"ew")` (same business month-end index, NaN where fewer than 15 market days or the series' stub 1998-12);
per stock keep months where both are finite; Beta = cov(r, m)/var(m) on those pairs when n >= 20. Raw
returns stand in for excess returns (rf omitted). var(m)=0 cannot occur in practice; guard anyway.

## 4. Timing and lag

- Signal at month-end t uses the return through month t (includes month t); the portfolio earns t+1. No
  fundamental data, so no filing-date or ART/ARQ issue; `dimension` stays default; nothing smears.
- No extra lag applied in OSAP (the return in `time_avail_m` t is that month's CRSP return). Same here: the
  window's last observation is the month ending at the signal date. No look-ahead: both accessors are bounded
  by `signal_asof`.

## 5. Filters (OSAP)

None in the predictor file beyond the 20-observation minimum and the inner merges of CRSP with FF and market
(rf/ewretd present every month). Filter column in SignalDoc is empty. Harness universe/sector ranking apply
on top.

## 6. Predicted sign (SignalDoc)

`Sign = 1.0`: high beta is predicted to earn a HIGH subsequent return (Fama-MacBeth 1973 risk-return
gamma_1 > 0; SignalDoc Cat.Economic `risk`, Cat.Data `Price`, Cat.Form `continuous`). `ascending=True`
(a high raw value is attractive). SignalDoc: Stock Weight EW, Portfolio Period 1, Start Month 6 (sample 1929-1968, T-stat 2.57).
A flipped sign would be a second hypothesis (|t| >= 2.74).

## 7. The mass-point question

Continuous OLS slope: no do-nothing value, no exact ties except among names with identical return
histories (negligible). Shares of names returning exactly the market slope or zero: ~0%. A stock with a
stale/flat price (zero returns for all months) gets Beta = 0 (a mild mass only among illiquid names that
the universe price/dollar-volume screen mostly removes); measure in preflight. Ties: rank average
(harness default); no tie-breaker needed.

## 8. History needed

- OSAP: minimum 20 monthly observations, window up to 60.
- Declare `history_months=20` (gate: a price within 7 days of t-20 months, i.e. 20 monthly returns) and
  `lookback_months=60`. Do NOT declare 60: a 60-month gate would null every name until 2002-12 because SEP
  starts 1997-12-31, which OSAP's 20-observation rule does not require.
- Measured constraints on THIS snapshot (from data_layer, not yet run): DAILY.marketcap starts 1998-12-01,
  so the market series starts 1998-12-02 and `monthly_market` blanks 1998-12 (stub). The first valid market
  month is 1999-01. Hence 20 paired observations exist only from the 2000-08-31 signal (1999-01..2000-08);
  signals 1998-12-31 .. 2000-07-31 (first ~19 of the 276 decision months from 1999-01) are unscorable
  for EVERY name (min_periods), not a defect. The window is full (60 pairs) from 2003-12-31; in
  2000-08..2003-11 the beta rests on 20-59 months (noisier, same as OSAP in its own early years).
  Preflight should report the first scorable month and the coverage ramp; the decision-window coverage bar
  (>= 40%) is judged on the scored months only, so expect the partial-window months to count.

## 9. OSAP metadata

Acronym `Beta`; LongDescription "CAPM beta"; Authors Fama and MacBeth; Year 1973; Journal JPE; Sample
1929-1968; Cat.Signal Predictor; Cat.Economic risk; Cat.Data Price; Cat.Form continuous; Predictability
in OP 2_likely; Signal Rep Quality 1_good; Sign 1.0; T-Stat 2.57; Stock Weight EW; Portfolio Period 1;
Start Month 6; Key Table 3A t(gamma_1); Test univariate reg. Detailed Definition: "Coefficient of a
60-month rolling window regression of monthly stock returns minus the riskfree rate on market return minus
the risk free rate (ewretd - rf). Exclude if estimate based on less than 20 months of returns."

## 10. Proposed Sharadar mapping and deviations

- `ret` -> `monthly_closeadj(60)`: r_k = close_k / close_{k-1} - 1 between adjacent business month-ends;
  a NaN column gives NaN returns for both adjacent months (never chain across a gap). `crsp.ret` mapped.
- `ewretd` -> `ctx.monthly_market(60, col="ew")`. Deviation: harness EW market (Sharadar-native, common
  stock on NYSE/NASDAQ/NYSEMKT per current TICKERS, no DLRET, gap returns excluded) versus CRSP ewretd
  (all NYSE/AMEX/NASDAQ, includes DLRET). Not in field_map index: declare as a harness accessor.
- `rf` -> omitted (raw regression). Deviation, material for monthly windows; no rf series in the snapshot
  and none to be invented. Alternative (not recommended): demean by a constant rf; no.
- Window by rows vs calendar months: use the calendar 60-month span with n >= 20 valid pairs.
- Beta is a stock-market regression: it is unrelated to the harness's hedge beta (market_hedge reads the
  universe VW return, 36m window) but correlates with the sector-relative structure: ranks are within
  sector, so cross-sector beta differences (e.g. utilities vs tech) are removed by construction.
- Fields/items the field-checker must verify on THIS snapshot: `crsp.ret` (closeadj month-end ratio),
  `crsp.smt_row` (if has_price_at is used), availability and first valid month of
  `monthly_market(col="ew")` (expected 1999-01), NaN share of monthly_market months with < 15 market days.
