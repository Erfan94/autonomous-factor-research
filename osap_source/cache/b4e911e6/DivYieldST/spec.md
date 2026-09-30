# DivYieldST — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: APPROX on data (ACTIONS dividends + SEP close; `cd1/cd2/cd3` not reproducible); PREFLIGHT-FAIL as a screen (mode 76.0-83.5% of scored names; 4 distinct values)
| OSAP input | Sharadar | status |
|---|---|---|
| CRSP `divamt`, `exdt` | `ACTIONS.value` (action == 'dividend'), `date` = ex-date | field_map `crsp.divamt` approx; values are on TODAY's split basis (AAPL 2014: AAPL 2014-02..11 value 0.1175 x 28 (7:1 in 2014 and 4:1 in 2020) = 3.29 as paid, the same factor as SEP close/closeunadj) |
| `cd1 == 1 & cd2 == 2`, `cd3 in (3,4,5)` | none | NOT reproducible (no distribution or frequency code). Not OSAP-zero-filled. Approx by the DivInit judgement: ACTIONS is cash dividends only; frequency unknown, so treat every payer as quarterly (OSAP's own rule for missing cd3) |
| `prc` (SignalMasterTable) | `SEP.close` (split-adjusted, same basis as ACTIONS.value; `closeunadj` is NOT) | field_map `crsp.prc` mapped; month-end last trading day |
| `ret, retx` (monthlyCRSP) | loaded but unused | n/a |
- Panel rule: universe x ACTIONS (absence of a dividend row = no dividend for a universe member). ID check against SF1 `dps`: DivInit spec section 1 (98.1-99.9% agreement).
- No IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob or ppegt input.

## 2. Variables (predictor.py)
`CRSPdistributions`: permno, cd1, cd2, cd3, divamt, exdt. `SignalMasterTable`: permno, time_avail_m, prc. `monthlyCRSP`: ret, retx (merged, not used).

## 3. Formula
```
dist = cd1==1 & cd2==2 & cd3 in (3,4,5); month(exdt); sum divamt by (permno, cd3, month); keep the lowest cd3 (quarterly first) per permno-month
cd3 = ffill; divamt NaN -> 0;  div12 = rolling 12-month sum of divamt (t-11..t, min_periods=1);  keep rows with div12 > 0
Ediv1 = divamt.shift(2) if cd3 in (3,0,1) or cd3 NaN;  divamt.shift(5) if cd3 == 4;  divamt.shift(11) if cd3 == 5     # (row shifts)
Edy1  = Ediv1 / |prc|
Edy1pos = Edy1 where Edy1 > 0;  DivYieldST = 1..3 (monthly qcut(q=3) of Edy1pos across rows of that month);  = 0 where Edy1 == 0
```
Values {0,1,2,3}: 0 = paid within 12 months but nothing due next month (nothing paid at the lag); 1-3 = tercile of predicted dividend yield among due payers. NaN = no dividend in 12 months (not scored). SignalDoc text says fixed cut points 0.005 / 0.010; the CODE uses monthly terciles of the positives; the code is what OSAP emits. Keep the code's form.

## 4. Timing / lag
OSAP: signal dated t, `prc` at t, dividends through t, used for month t+1. Harness: ACTIONS `date <= signal_asof`; price = the last SEP `close` at or before the month-end. Dividend "2 months ago" = ex-date in calendar month t-2 (aggregate on `date` by month; `ctx.actions` windows by DateOffset). No SF1.

## 5. Filters
None in SignalDoc. Common stock / exchange / price >= $1 / liquidity are harness-side.

## 6. Predicted sign
`Sign = +1.0` (Litzenberger-Ramaswamy 1979 Table 1, t = 6.3 in cross-sectional regressions): higher predicted dividend yield, higher return. `ascending=True`.

## 7. Mass-point question
Do-nothing firm: a recent payer with no payment at the frequency lag gets 0; a non-payer is NaN. Measured on the universe (46 of 276 decision months, every 6th, 1998-12 .. 2021-06 signals; quarterly-for-all; yield on the harness `px_usd`, which may be on a different split basis than ACTIONS so tercile EDGES are indicative, the mode is not):
- scored: 879-1,177 names per month (coverage 35-62% of universe, same payer set as DivSeason).
- value 0: 76.0-83.5% of scored names; values 1, 2, 3 each 5.4-8.0% (about 55-95 names each). Of the whole universe: 0 = 27-52%, NaN (non-payers) = 38-65%, each of 1-3 = 2-5%.
- Preflight hard fails on two counts: mode >= 10% (76-84%) and only 4 distinct values, so `qcut` gives at most 4 bins, never 10. No tie handling produces deciles; the "0" bucket is the large majority.
- Tie handling if overridden: average rank, IC on a 4-level score; D10-D1 not defined.

## 8. History needed (snapshot starts 1998-01; ACTIONS 1997-12 = 19-row stub; SEP from 1997-12-31)
Needs ACTIONS t-11..t (12-month payer test, annual leg shift(11)): first full month 1998-12 = the first decision signal (1999-01). **276** of 276 decision months defined for payers. `lookback_months` = 12; no `history_months`.

## 9. OSAP metadata
Litzenberger and Ramaswamy (1979), JFE; Cat.Data Accounting; Cat.Economic valuation; discrete; sample 1936-1977; Acronym2 DivYieldST; Test "mv reg", Key Table 1; EW; 1_clear / 2_fair; T-stat 6.3. SignalDoc notes the original regression has ~75% zeros, and OSAP "mimics their results" with the discretisation above. Source `Signals/pyCode/Predictors/DivYieldST.py`.

## 10. Proposed Sharadar mappings (only if the owner overrides the preflight verdict)
`divamt_m` = sum of `ACTIONS.value` (`0 < value <= 10*close`) by (ID, calendar month of `date`) via `ctx.actions("dividend", 12)`; payer = any dividend in t-11..t; `Ediv1` = `divamt_m` at t-2 (quarterly for all); `Edy1 = Ediv1 / SEP.close at month-end`; `DivYieldST = 0` if `Edy1 == 0`, else monthly tercile 1-3 of positive `Edy1` (skip terciles if < 3 positives); NaN for non-payers. Declare `ACTIONS.value`, `ACTIONS.action`, `SEP.close`; `lookback_months=12`; `ascending=True`.
Deviations: no `cd1/cd2/cd3` (specials included; monthly payers kept, OSAP drops them; semi-annual/annual payers get the t-2 lag, so most read 0); calendar vs row-based shifts; price on split-adjusted `close` (correct basis match with ACTIONS; OSAP mixes as-paid amounts with the current price). Fields in map: `crsp.divamt`, `crsp.prc`.
