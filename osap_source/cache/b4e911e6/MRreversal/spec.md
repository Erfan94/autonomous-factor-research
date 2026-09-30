# MRreversal — Medium-run reversal: compounded stock return over months t-18 .. t-13 (De Bondt and Thaler 1985, JF, Fig 2 two-year line)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/MRreversal.py` (cached `predictor.py`; upstream `upstream_CRSPMonthly.py`, `upstream_SignalMasterTable.py` beside it). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`. Measured with `harness` build_universe + MonthContext on the frozen snapshot, all 276 decision months.

## 1. Data availability (verdict: FEASIBLE; first 7 of 276 decision months are null, data start only)

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `ret` (monthly, SignalMasterTable, incl. delisting return) | `crsp.ret` | SEP `closeadj` month-end ratio (`ctx.at_month_end("SEP", ["closeadj"], m)`) | mapped (no delisting return) | NaN ret -> 0; a lag with NO row -> 0 too; all six originally missing -> NaN |
| `permno, time_avail_m` (shrcd 10/11/12, exchcd 1/2/3) | `crsp.shrcd`, `crsp.exchcd` | harness universe | approx | - |
- No SF1 input, no ART/ARQ question; none of IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt.
- Data start: SEP closeadj starts 1997-12-31, the window needs a close 19 months before the signal, so the first scorable signal is 1999-07-30. Measured: 269 of 276 months scorable (1999-07-30 .. 2021-11-30); 1998-12 .. 1999-06 (7 months) have 0 coverage. Floor `min_months` 120 not at risk.
- Measured coverage of the universe (scored share, 269 scorable months): mean 94.2%, min 80.4% (2000-08-31), max 98.2%; first scorable month 88.7%. Scored names 1,659-2,379 per month.

## 2. Variables (exact source names)
`permno, time_avail_m, ret` (SignalMasterTable). Derived `ret_lag13 .. ret_lag18` (calendar merge lags), `MRreversal`.

## 3. Formula in words and key lines
Buy-and-hold return over the six months that end 13 months before the signal month (t-18..t-13), skipping t-12..t.
```
ret = ret.fillna(0);  ret_lag{13..18} = ret merged on time_avail_m + k months;  missing lag row -> fillna(0)
MRreversal = prod(1 + ret_lag{13..18}) - 1
MRreversal = NaN if all six lags were ORIGINALLY missing (no row / NaN ret)
```
Endpoint algebra: the six monthly returns of months t-18..t-13 multiply to `closeadj[t-13] / closeadj[t-19] - 1` (six returns, seven closes). Harness equivalent: two `at_month_end` reads (13 and 19), or `monthly_closeadj(19)` columns t-13 and t-19. No winsorising in the predictor.

## 4. Timing / lag convention
OSAP signal at time_avail_m t uses returns of t-18..t-13 (no publication lag); held from t+1. Here: signal at business month-end t, closes at BME t-19 and t-13. No filing dates, no flow items, no ART/ARQ smear. The window lies inside the t-36..t-13 window of LRreversal (same closes at t-13; a construction fact, not a verdict) and is disjoint from the 12-1 Momentum window (t-12..t-1 closes).

## 5. Filters
OSAP: SignalMasterTable filter only (shrcd 10/11/12, exchcd 1/2/3); SignalDoc Filter blank. Here: harness universe (price, cap, ADV screens) picks the scored names; the history gate is `has_price_at(19)`.

## 6. Predicted sign
SignalDoc `Sign = -1.0` (past losers over months t-18..t-13 earn more); Cat.Economic long term reversal; Cat.Form continuous; Cat.Data Price. Orientation: long LOW, `FactorDef(ascending=False)`.

## 7. The mass-point question
Do-nothing firm (no price change over the six months) produces exactly 0.0, a continuous return with no default value; no zero-fill of the signal.
Measured, 269 scorable months: share of the scored cross-section at exactly 0.0 mean 0.07%, max 0.67% (2000-03-31, 16 of 2,379 names); modal share of any value mean 0.12%, max 0.67%; distinct values min 1,658; `qcut(10)` yields 10 bins in every month. No tie handling needed (harness average rank).

## 8. History needed (snapshot starts 1998-01)
19 month-ends of closeadj: `history_months = 19`, `lookback_months = 19`. `has_price_at(19)` equals the scored set by construction. Preflight's data-start warning fires for the first probe month (1998-12): it is the 7-month null block above, not a construction error.

## 9. OSAP metadata
MRreversal (Acronym2 Mom1813); De Bondt and Thaler 1985 JF; Cat.Signal Predictor; Predictability in OP 2_likely; Signal Rep Quality 3_distant; Cat.Form continuous; Cat.Data Price; Cat.Economic long term reversal;
Sample 1933-1980; Key Table "Fig2 two-year line"; Test "LS port nonstandard (plot only)"; Evidence "large ret in similar long-short"; Sign -1.0; Return 0.75; T-Stat blank; Stock Weight EW; LS Quantile 0.2; Portfolio Period 12.0; Start Month 6.0; Filter blank; GScholar cites 13431.
Notes: "We include this to nest MP. Figure 2, two-year line is closest. Table I only shows LRreversal ..." Definition: "Stock return between months t-18 and t-13."

## 10. Proposed Sharadar mappings with deviations
```
p13 = ctx.at_month_end("SEP", ["closeadj"], 13)["closeadj"] ; p19 = ... 19          # as LRreversal uses 13 and 37
MRreversal = p13.where(p13 > 0) / p19.where(p19 > 0) - 1 ; ascending=False ; history_months=19 ; lookback_months=19
```
Deviations: (a) OSAP zero-fills missing months and scores any name with at least one of the six returns present (a window starting after t-19 is scored on the months that exist); here both endpoints are required. Measured: names with a close at t-13 but none at t-19 are 1.9% of the universe on average (max 5.6%), not scored here;
(b) no delisting return in the window (SEP ends at the last trade; `crsp.dlret` unavailable); (c) calendar month-end alignment with 7-day tolerance instead of OSAP's merge lags; (d) closeadj is total return (splits + dividends), as CRSP ret; (e) OSAP's test is equal-weighted with a 0.2 quantile long-short; the harness ranks; (f) first 7 decision months null.
Fields not in the map: none.
