# betaVIX — Systematic volatility: loading on daily VIX changes (Ang, Hodrick, Xing, Zhang 2006, JF, Table 1A)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/ZZ2_betaVIX.py` (cached `predictor.py`;
upstream `VIX.py` cached as `upstream_VIX.py`). DATA_SHA 198b281de1a0. Construction only.

## 1. Data availability (verdict: DATA_UNAVAILABLE — recommend `infeasible`)
| OSAP input | Sharadar | status |
|---|---|---|
| `dailyCRSP.ret` | SEP closeadj day-over-day (`crsp.ret`) | mapped |
| `dailyFF.mktrf`, `rf` | `MonthContext.market_daily` (raw VW market, built from SEP/DAILY); rf NOT in snapshot | approx (rf absent, ~0-2bp/day) |
| `d_vix.dVIX` (daily change in the CBOE volatility index, FRED VXOCLS to 2021-09-22, VIXCLS after) | **no held table** | unavailable |
- The VIX is the signal's defining regressor, not a cosmetic input. Checked on THIS snapshot: TICKERS lists `^VIX` ("CBOE VOLATILITY INDEX", category IDX) and ~90 VIX-linked ETPs, but every one sits under table `SFP` (Sharadar Fund Prices), which is mapped but NOT held (manifest holds ACTIONS, DAILY, DESCRIPTIONS, EVENTS, METRICS, SEP, SF1, SF2, SF3, SF3A, SF3B, SP500, TICKERS). 0 of the 9,930 SFP tickers are present in SEP (20,993 tickers); SEP/DAILY carry no VIX, VXX, SPY or index series. METRICS holds only beta1y/beta5y and price statistics; DESCRIPTIONS has no implied-volatility field. No held table substitutes.
- OSAP missing-item rule: OSAP does not zero-fill dVIX; the inner join on `d_vix` drops every day without a VIX change, and the regression needs >= 15 non-missing days of 20. No zero-fill, so the rule gives `infeasible`.
- Route if ever wanted: adding SFP (for `^VIX`) moves DATA_SHA (stop-and-ask 3). Even then the series differs: OSAP uses VXO (S&P 100) through 2021-09-22 and VIX afterwards; `^VIX` is the S&P 500 index (history depth from 1998 unverified, not fetched).
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt.

## 2. Variables (exact source names)
`ret`, `rf`, `mktrf`, `dVIX`, derived `ret_excess = ret - rf`, `betaVIX`.

## 3. Formula in words and key lines
Per stock, on a rolling 20-trading-day window of daily data, regress excess return on the market excess return and the daily change in the VIX (intercept included); betaVIX is the VIX coefficient, taken at the last day of each month.
```
ret_excess ~ 1 + mktrf + dVIX   # rolling_ols, window_size=20, min_periods=15, null_policy="drop", over permno
betaVIX = last non-null coefficient on dVIX in the calendar month
```
Days enter only where ret, rf, mktrf and dVIX are all present (inner joins).

## 4. Timing / lag
Daily data up to month end, no lag; `time_avail_m` = the month of the last regression day. No fundamentals: ART-as-of-filing and TTM smear do not apply.

## 5. Filters
None in the predictor; SignalDoc Filter blank. Harness universe only.

## 6. Predicted sign
SignalDoc `Sign = -1.0` (Return 1.04, T-Stat 3.9, VW, LS Quantile 0.2): stocks with high (positive) VIX beta earn lower returns, so LOW betaVIX is the long leg (`ascending=False`).

## 7. The mass-point question
Continuous OLS coefficient, no default value; a do-nothing firm (zero return on all days) gives coefficient 0 only if its whole window is flat. Not measured (no dVIX series). Expected tie share tiny except for illiquid names with flat windows; moot while the input is unavailable.

## 8. History needed (snapshot starts 1998-01)
20 trading days of SEP plus dVIX; SEP from 1997-12 would suffice for the first 1999 signal, but dVIX is not held. Not measured.

## 9. OSAP metadata
betaVIX; Ang et al. 2006 JF; Cat.Signal Predictor; Cat.Form continuous; Cat.Data Price; Cat.Economic volatility; Sample 1986-2000; Key Table "1A"; Test port sort; Evidence "t=3.9 in port sort"; Sign -1.0; Return 1.04; T-Stat 3.9; VW; LS Quantile 0.2; Portfolio Period 1.0; Start Month 6.0; Notes "Tab I has port sorts"; GScholar cites 6,323. Definition: "Coefficient on daily change in the VIX of a 1-month rolling window regression of daily stock excess returns on market return and the daily change in the CBOE S&P 100 volatility index (downloaded from FRED). Require at least 15 non-missing observations."

## 10. Proposed Sharadar mappings
None proposed: `data_unavailable`. The stock side (closeadj daily returns, harness market_daily) exists; the VIX side has no held source. Fields not in the map: `dVIX` / `^VIX` (TICKERS only; SFP prices not held).
Recommendation: **infeasible** (reason: CBOE VIX series not in any held Sharadar table; OSAP drops, not zero-fills, missing dVIX).
