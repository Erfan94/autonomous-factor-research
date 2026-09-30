# Mom6m — Six-month momentum: compounded return over months t-5..t-1, skipping the current month (Jegadeesh and Titman 1993, JF, Table 1A K=3 row 6)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/Mom6m.py` (cached `predictor.py`; upstream `upstream_SignalMasterTable.py`, `upstream_CRSPMonthly.py`, `upstream_stata_replication.py` beside it). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`.

## 1. Data availability (verdict: FEASIBLE, all inputs mapped; no data-start loss)

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `ret` (monthly total return incl. delisting return) | `crsp.ret` | SEP `closeadj` month-end ratio (`ctx.monthly_closeadj(6)`) | mapped | NaN ret -> 0 (`fillna(0)`) BEFORE the lags; a calendar gap row (missing month) creates a NaN lag, so the product is NaN |
| delisting return (upstream: dlret, or -0.35 / -0.55 for performance delistings, compounded into ret) | `crsp.dlret` | none | unavailable | no delisting return in the past-return window here (harness delisting proxy applies only to forward returns) |
| `permno, time_avail_m`; shrcd 10/11/12, exchcd 1/2/3 | `crsp.shrcd`, `crsp.exchcd` | harness universe | approx | - |
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt; no SF1 input; no zero-filled optional term; no filing dates. closeadj is the total-return price.
- Data start: needs closes 6 month-ends back; SEP starts 1997-12-31, so the first decision month (1999-01, signal 1998-12-31) is scorable.
  Measured on the harness universe, all 276 decision months (1999-01 .. 2021-12; universe 1,739-2,867 names, mean 1,965): scored names 1,716-2,663 every month, coverage 91.3%-99.9% (mean 98.3%). Floor `min_months` 120 met with 276.

## 2. Variables (exact source names)
`permno, time_avail_m, ret` from SignalMasterTable; derived `ret_lag1 .. ret_lag5`, `Mom6m`. No other column.

## 3. Formula in words and key lines
Buy-and-hold return over the five months t-5..t-1; the current month t is skipped (OSAP note: the paper skips a week, OSAP skips the month). Despite the name it is five monthly returns.
```
df["ret"] = df["ret"].fillna(0)
df = stata_multi_lag(df, "permno", "time_avail_m", "ret", [1, 2, 3, 4, 5])      # fills calendar gaps first -> NaN lag
df["Mom6m"] = (1+ret_lag1)*(1+ret_lag2)*(1+ret_lag3)*(1+ret_lag4)*(1+ret_lag5) - 1
```
Endpoint algebra: the product of the month-end-to-month-end returns of months t-5..t-1 equals closeadj[t-1] / closeadj[t-6] - 1 (5 returns, 6 closes). Harness equivalent: `px = ctx.monthly_closeadj(6)`, columns BME(t-1) and BME(t-6) (the same shape as `_momentum` in composite.py with 1m / 12m). No winsorising in the predictor. No partial windows: a firm with fewer than five prior rows is NaN.

## 4. Timing / lag convention
Signal dated t uses returns through t-1 (month t not used); the harness holds t+1 (signal at the business month-end, return of the following month). No filing dates, no flow items, no ART/ARQ smear. `partial_months` is irrelevant: month-end closes are point reads and 1997-12-31 is a valid close, no daily aggregation.
Overlap with the v0 Momentum leg (factors/composite.py `_momentum`: closeadj[t-1]/closeadj[t-12]-1, return months t-11..t-1, history_months 12): the Mom6m window (t-5..t-1) lies entirely inside it, five of its eleven months. Measured cross-sectional Spearman between Mom6m and that 12-1 value on the harness universe, 276 months: median 0.64, mean 0.63, p10/p90 0.50/0.76, min 0.02 (2009-08).

## 5. Filters
OSAP SignalMasterTable: shrcd 10/11/12, exchcd 1/2/3. SignalDoc Filter blank; Quantile Filter blank. Here: harness universe only.

## 6. Predicted sign
SignalDoc `Sign = +1.0` (past winners earn more); Return 0.84; T-Stat 2.44. Orientation: `ascending=True` (long HIGH).

## 7. The mass-point question
Do-nothing firm (no price change over 5 months) produces exactly 0.0 from a continuous return, no default value, no signal zero-fill.
Measured on the harness universe, 276 months: modal share of the scored cross-section max 0.35% (median 0.11%); distinct values min 1,712 of 1,716-2,663 scored; no `qcut(10)` collapse. Tie handling: none designed; the harness average rank covers the few exact ties. Only guard: closeadj > 0 at both ends (else NaN).

## 8. History needed (snapshot starts 1998-01)
6 month-end closes: `history_months = 6`, `lookback_months = 6`. The 6-month lookback from the first signal (1998-12-31) reaches 1998-06-30, inside the panel; no data-start warning expected.

## 9. OSAP metadata
Mom6m (Acronym2 Mom6m); Jegadeesh and Titman 1993 JF; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form continuous; Cat.Data Price; Cat.Economic momentum; Sample 1964-1989; Key Table "1A K=3 row 6"; Test port sort; Sign +1.0; Return 0.84; T-Stat 2.44; EW; LS Quantile 0.1; Portfolio Period 3.0 (three-month hold; the harness holds one month); Start Month 6.0; GScholar cites 17,341. Definition: "Stock return between months t-6 and t-1".

## 10. Proposed Sharadar mappings with deviations
```
px = ctx.monthly_closeadj(6); end = to_bme(asof - 1m); start = to_bme(asof - 6m)
Mom6m = px[end] / px[start].where(px[start] > 0) - 1 ;  ascending=True ; history_months=6 ; lookback_months=6
```
Deviations: (a) no delisting return in the window; (b) closeadj endpoints are calendar business month-ends with a 7-day tolerance, not row-based `shift(i)`; (c) a missing close is NaN (OSAP zero-fills a NaN ret inside an existing row, NaNs a missing row); (d) total-return price rather than compounded CRSP ret; (e) one-month hold vs Portfolio Period 3.
Fields not in the map: none.
