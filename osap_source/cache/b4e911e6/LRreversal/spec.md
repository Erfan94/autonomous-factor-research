# LRreversal — Long-run reversal: compounded stock return over months t-36 .. t-13 (De Bondt and Thaler 1985, JF, Table 1 three-year)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/LRreversal.py` (cached `predictor.py`; upstream `upstream_CRSPMonthly.py`, `upstream_SignalMasterTable.py` beside it).
DATA_SHA 198b281de1a0. Written fresh from source and `field_map_index.yaml`.

## 1. Data availability (verdict: FEASIBLE, with a non-fatal data-start caveat: first 25 of 276 decision months are null)

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `ret` (monthly, incl. delisting return) | `crsp.ret` | SEP `closeadj` month-end ratios (`ctx.monthly_closeadj`) | mapped (no delisting return, `crsp.dlret` unavailable) | NaN ret -> 0 inside an existing row; a lag with no row -> NaN, so the whole product is NaN |
| `permno, time_avail_m` (SignalMasterTable, shrcd 10/11/12, exchcd 1/2/3) | `crsp.shrcd`, `crsp.exchcd` | harness universe | approx | - |
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt. No SF1 input, no zero-fill, no ART/ARQ question.
- Data start: SEP/closeadj panel starts 1997-12-31 (SF1 1997Q4). The window needs a close 37 months before the signal, so the first signal with a full window is 2001-01-31.
  Measured: 251 of 276 decision months scorable (2001-01 .. 2021-11); 1998-12 .. 2000-12 (25 months) have coverage 0. The harness floor `min_months` is 120, so this is not a `data_start` failure.

## 2. Variables (exact source names)
`permno, time_avail_m, ret` from SignalMasterTable (CRSP monthly ret with the delisting adjustment: dlret, or -0.35 / -0.55 for performance delistings by exchange, compounded into ret). Derived `ret_lag13 .. ret_lag36`, `LRreversal`.

## 3. Formula in words and key lines
Buy-and-hold return over the 24 months that end 13 months before the signal month, skipping the most recent 12 months (t-12..t).
```
df["ret"] = df["ret"].fillna(0)                                   # NaN return inside an existing row -> 0
for i in range(13, 37): ret_lag{i} = df.groupby("permno")["ret"].shift(i)     # ROW shift; a lag before the firm's first row stays NaN
LRreversal = prod(1 + ret_lag{13..36}) - 1                        # any NaN lag (before listing) -> NaN, no partial windows
```
Endpoint algebra: the product of monthly returns for months t-36 .. t-13 equals closeadj[t-13] / closeadj[t-37] - 1 (month m's return is close[m]/close[m-1]); 24 returns, 25 closes. Harness equivalent: `monthly_closeadj(37)`, columns t-37 and t-13.
Verified on the snapshot: every name with both end closes also had all 25 month-end closes (n_scored == n_full in all 251 months), so the endpoint ratio and the compounded-return form coincide on scored names. No winsorising in the predictor.

## 4. Timing / lag convention
OSAP signal at time_avail_m t uses returns of t-36..t-13 (t-12 .. t skipped, the same skip-convention as the 12-1 Momentum leg); no publication lag. Here: signal at business month-end t, closes at BME t-37 and t-13, earned month t+1.
No filing dates, no flow items, no ART/ARQ smear. The window is disjoint from the v0 Momentum leg's window (t-12..t-1 closes); no shared return month.

## 5. Filters
OSAP: SignalMasterTable filter only (shrcd 10/11/12, exchcd 1/2/3); SignalDoc Filter blank. Here: harness universe (price, cap, ADV screens) chooses which names are scored; the history gate is the 37-month close.

## 6. Predicted sign
SignalDoc `Sign = -1.0` (past 3-year losers earn more); Return 0.105; T-Stat 3.29; Stock Weight EW; LS Quantile blank; Portfolio Period 1.0; Start Month 12.0; Cat.Economic long term reversal; Cat.Data Price. Orientation: `ascending=False` (long LOW past return).

## 7. The mass-point question
Do-nothing firm (no price change over 24 months) produces exactly 0.0; a continuous return, no default value, no zero-fill of the signal.
Measured on the harness universe, 251 scorable months: modal share of the scored cross-section max 0.21% (distinct values min 1,581; n scored 1,582-1,898); no `qcut(10)` collapse. Tie handling: harness average rank; nothing designed.
Coverage of the universe (share with a value): 78.2% at 2001-01, mean 89.6%, max 94.5%, never below 78.2% in a scorable month; 0 in the 25 leading months (mean over all 276 months 81.5%).

## 8. History needed (snapshot starts 1998-01)
37 months of closeadj: `history_months = 37`, `lookback_months = 37`. `has_price_at(37)` equals the scored set (same 78-94.5% share), so the history gate and the value never disagree. Preflight's data-start warning will fire for the first probe month (1998-12); that is the 25-month null block above.

## 9. OSAP metadata
LRreversal (Acronym2 Mom36m); De Bondt and Thaler 1985 JF; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form continuous; Cat.Data Price; Cat.Economic long term reversal;
Sample 1929-1982; Key Table "1 three-year 1 month"; Test "LS port CAPM alpha"; Sign -1.0; Return 0.105; T-Stat 3.29; EW; Portfolio Period 1.0; Start Month 12.0; Filter blank; GScholar cites 13447.
Notes: "Insignificant at 12-month horizon. Many alternative signal designs lead to similar results." Definition: stock return between months t-36 and t-13.

## 10. Proposed Sharadar mappings with deviations
```
px = ctx.monthly_closeadj(37); end = to_bme(asof - 13m); start = to_bme(asof - 37m)        # as _momentum in composite.py does with 1m / 12m
LRreversal = px[end] / px[start].where(px[start] > 0) - 1 ;  ascending=False ; history_months=37 ; lookback_months=37
```
Deviations: (a) no delisting return in the past-return window (OSAP compounds dlret / -0.35 / -0.55 into the month's ret; the harness proxy applies only to forward returns); (b) no NaN -> 0 fill inside the window (a missing close -> NaN; no scored name was affected);
(c) calendar month-end alignment rather than OSAP's row-based `shift(i)`; (d) first 25 decision months null (SEP starts 1997-12); (e) closeadj is total return (splits + dividends), as CRSP ret.
Fields not in the map: none.
