# STreversal — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: FEASIBLE (all inputs mapped; minor declared deviations)
Checked against `osap_source/field_map_index.yaml`. Only CRSP `ret` enters.

| OSAP var | field_map key | Sharadar | status | note |
|---|---|---|---|---|
| ret | crsp.ret | `ctx.monthly_closeadj(1)`: SEP.closeadj(signal) / closeadj(signal - 1 month-end) - 1 | mapped, verified 2026-09-30 | closeadj is split- and dividend-adjusted, so the ratio is a total return |
| dlret (inside ret) | crsp.dlret | none (config delisting proxy) | unavailable | only enters in a delisting month; a name delisted in month t has no month-end t row and is not in the t universe, so it cannot reach the signal |

No IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob or ppegt. OSAP's
only fill is `fill_null(0)` on missing returns (see 7). Recommend: **feasible**.

## 2. Variables by exact source name (predictor.py)
`SignalMasterTable.parquet`: permno, time_avail_m, ret. Upstream (`upstream_CRSPMonthly.py`,
`upstream_SignalMasterTable.py`, cached): `ret = (1+ret)(1+dlret)-1` with dlret defaulted to
-0.35 (NYSE/AMEX) / -0.55 (NASDAQ) for performance delistings, `ret = dlret` when ret is
missing; SignalMasterTable keeps shrcd in {10,11,12}, exchcd in {1,2,3}.

## 3. Formula
Last month's return, used as is:

    STreversal = ret.fill_null(0)          # the return OF month time_avail_m

Key line: `pl.col("ret").fill_null(0).alias("STreversal")`. The row at month t carries the return
earned DURING month t; the portfolio code then holds t+1. So the signal at month-end t is the
return from month-end t-1 to month-end t, known at the signal date.
Sharadar: `p_end / p_start.where(p_start > 0) - 1` with p_end = closeadj at the signal
month-end, p_start = closeadj at the previous business month-end (as the Momentum leg does).

## 4. Timing / lag convention
Window (signal - 1 month-end, signal]. `history_months=1` (harness nulls a name with no
trade near the window start, so a name listed this month is not scored). No fundamentals,
no ART/ARQ, no TTM smear, no as-of-filing effect. Month-end to month-end instead of the
CRSP calendar-month holding-period return: the two coincide when the last trading day of the
month is the business month-end.

## 5. Filters
predictor.py: none. SignalDoc `Filter` blank, `Quantile Filter` blank (LS Quantile 0.1,
EW, Portfolio Period 1, Start Month 6). Harness universe: price >= $1, etc.

## 6. Predicted sign (SignalDoc)
`Sign = -1.0`: last month's winners underperform (Jegadeesh 1990, JF, Table 2 "S1, Jan-Dec",
port sort CAPM alpha; Return 1.99, T-Stat 12.44; Acronym2 Mom1m). `ascending=False` (high
last-month return -> D1). Cat.Economic short-term reversal; Cat.Form continuous; Cat.Data
Price; sample 1934-1987; Signal Rep Quality 1_good; Predictability 1_clear.

## 7. The mass-point question
Do-nothing firm: a stock whose price did not change produces exactly 0.0 (closeadj on a
3-dp grid, so equal month-end prices tie). Measured at 92 of 276 decision months (every third,
1998-12-31 .. 2021-09-30; universe 1,739-2,867):
- exact 0.0: 0.26% mean of scored names (max 1.12% at 1999-06-30); modal value 0.0 in 70 of
  92 months; distinct values ~ n; 10 qcut bins.
- coverage (closeadj non-null at both ends, history gate): 99.8% mean (min 98.9%).
OSAP's `fill_null(0)` turns every MISSING return into 0.0, which would put a larger point
mass at 0 than the true zero-return share; the harness leaves missing as null (renormalised
blend). Tie handling: none in OSAP beyond that fill; average rank. No standing tie rule
warranted; no blocker.

## 8. History needed
Two month-ends of price. SEP starts 1997-12-31, so every decision month (1998-12-31 onward)
scores; coverage 99.5% even at the first month.

## 9. OSAP metadata
Acronym STreversal (Acronym2 Mom1m); Jegadeesh 1990, JF; Key Table "2, S1, Jan-Dec"; Test
"port sort CAPM alpha"; T-Stat 12.44; GScholarCites202509 4115. Detailed Definition: stock
return (ret) over the previous month. Source `Signals/pyCode/Predictors/STreversal.py`.

## 10. Overlap with the v0 composite (factual, from factors/composite.py)
- Momentum leg = closeadj(signal - 1m) / closeadj(signal - 12m) - 1, which deliberately
  skips the most recent month. STreversal = closeadj(signal) / closeadj(signal - 1m) - 1, i.e.
  exactly that skipped month. The windows are adjacent and non-overlapping and share one
  price point (closeadj at signal - 1m: the Momentum end and the STreversal start). Measured
  Spearman of raw STreversal with raw Momentum: mean 0.05 (range -0.38 to 0.46, 92 months).
- Value leg: mean -0.11; Profitability 0.01; Size (log mkt cap) 0.03.

## 11. Proposed Sharadar mappings and deviations
| item | mapping | deviation |
|---|---|---|
| ret | `monthly_closeadj(1)` ratio - 1, `history_months=1` | no delisting return (irrelevant to a name alive at t); month-end ratio |
| fill_null(0) | not reproduced (null stays null) | removes OSAP's artificial zero mass |
| universe/ranks | harness; within sector; deciles | OSAP EW, LS Quantile 0.1 |
Fields all in `field_map_index.yaml` (crsp.ret verified 2026-09-30).
