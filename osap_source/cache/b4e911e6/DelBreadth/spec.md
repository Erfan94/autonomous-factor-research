# DelBreadth — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: INFEASIBLE FOR SCREENING (recommend `infeasible`; constructible but < min_months)
13F holdings exist on the snapshot only from 2013-06-30 (SF3 / SF3A, 53 quarter-ends to 2026-06-30),
so in the decision window 1999-01 .. 2021-12 the signal has at most **97-99 of 276 months**
(see section 8). `rebalance.min_months` is 120: **cannot be met** -> Stage 1 is inconclusive by
construction, never a verdict on the signal. No inherited-status caveat: there is NO field_map
key for 13F (`SF3A.shrholders`, `SF3.investorid` are not in the map; needs field-checker if the
owner chooses to proceed). The signal is OSAP's 13F (Thomson s34) build; pre-2013 13F is on the
standing-unavailable list.

| OSAP input | Sharadar | status |
|---|---|---|
| `dbreadth` (TR_13F, Thomson s34 + CRSP MSENAMES) | SF3 (investorid x ticker x date, SHR rows) / SF3A `shrholders` | not in field_map; 2013-06-30+ only |
| `exchcd`, `mve_c` (SignalMasterTable) | universe (TICKERS.exchange, `mkt_cap_usd`) | mapped; harness-side |
| 13F pre-2013 | none | unavailable |

## 2. Variables (predictor.py + upstream)
`dbreadth` (TR_13F.parquet, from `upstream_tr13f_pmg_edit.sas`), `exchcd`, `mve_c`, `permno`, `time_avail_m`.
Not a Compustat signal: no zero-fill applies.

## 3. Formula (SAS lines 157-181, x100 at line 214)
Per permno and quarter-end rdate (Lehavy-Sloan 2008):
```
DBREADTH = ((NumOwners_t - NewInst_t) - (NumOwners_{t-1} - OldInst_{t-1})) / NumInst_{t-1}
```
- NumOwners = # 13F managers holding the stock (shares_adj > 0); NewInst_t = holders that are a
  manager's first report or after a gap (did not report in t-1); OldInst_{t-1} = holders whose
  manager did not report in t; NumInst_{t-1} = TOTAL # of 13F filers in t-1 (all stocks).
  Numerator = change in holders among CONTINUING filers. First quarter per permno = NaN.
- Then (predictor.py): DelBreadth = dbreadth; NaN if `mve_c` < NYSE (exchcd == 1) 20th
  percentile of `mve_c` that month.
- Sharadar routes: (a) exact, from SF3: per (ticker, quarter) the investorids with SHR rows;
  per-quarter filer set = distinct investorid across all tickers; First/Last flags by
  consecutive-quarter membership (a manager missing in a quarter breaks the run). SF3 holds 81.2M
  rows. (b) proxy, SF3A: (shrholders_t - shrholders_{t-1}) / N_filers_{t-1}; drops the continuing-filer
  adjustment (filer entry/exit moves the count). Checked on AAPL only: SF3A `shrholders` differs from distinct SHR investorids in SF3 by at most 2 over all 53 quarters (1860 vs 1862 at 2013-06-30, exact from 2025). Recommend (a).
- Edge effects: first quarter 2013-06-30 is NaN (no t-1; all its filers flag First_Report);
  thresholds on shares_adj > 0 have no analogue in SF3 (value/units > 0 only).

## 4. Timing / lag
- OSAP: `time_avail_m` = month of rdate (quarter end, NO filing lag), forward-filled (`tsfill`) between
  a permno's first and last rdate, so each quarter's value covers 3 months. That is look-ahead
  against the 45-day 13F deadline.
- Sharadar: SF3 / SF3A carry only `date` (period end), no filing or availability date. PIT here:
  quarter Q usable for signals as-of >= Q + 45 days (conservative: Q dated 2013-09-30 -> 2013-11-29
  month-end signal -> decision month 2013-12). Each value is held ~3 months (three near-identical
  cross-sections per quarter; low turnover). Needs a harness 13F accessor on MonthContext: none exists
  (harness extension, not factor code). Also restatement: values are as of the snapshot pull
  (13F amendments not dated); flag.
- Not a fundamentals flow: no ART/ARQ issue.

## 5. Filters
SignalDoc Filter blank; predictor rule above (drop below NYSE 20th pct of `mve_c`). The harness universe
ENTERS at NYSE 20th pct of cap (leaves below the 15th), so the OSAP filter is nearly absorbed
(NYSE-only percentile in both; the band only adds members between the 15th and 20th).

## 6. Predicted sign
`Sign = 1.0`: rising breadth of ownership predicts higher returns (Chen-Hong-Stein, t = 3.96 port sort,
size-adjusted, Table 4A 1 quarter). No flip.

## 7. Mass-point question
Continuous ratio (count change / filer total). Do-nothing (no change among continuing holders) = 0.
Measured on SF3A proxy, names with >= 50 holders at t-1 (123,235 name-quarters 2013Q3-2021Q4): exact
zero change in shrholders 3.7% (quarterly range 2.1-5.0%); among >= 200 holders 2.0%. Exact-SF3 form zero share: not measured (proxy figure only). Raw SF3A `shrholders == 0` is 36% of rows pooled but those are
non-universe names (median 2 holders pooled); universe members hold in the hundreds. Ties: average rank;
no decile collapse expected.

## 8. History needed (decision months with data, snapshot starts 1998-01)
- Quarters in window: 2013-06-30 .. 2021-12-31 = 35 quarter-ends (SF3A). First dbreadth 2013-09-30.
- With the 45-day lag: decision months 2013-12 .. 2021-12 = **97** (last usable quarter 2021-09-30).
- Without lag (OSAP-faithful forward-fill): 2013-10 .. 2021-12 = **99**; an upper bound of 103 if the 2013-06
  quarter counted (it cannot: no t-1).
- min_months = 120 -> **cannot be met** (97-99 < 120) under either convention. Stage 1 result would be
  "inconclusive, not rejected". Even the full 13F era through 2026 cannot be used (holdout 2022+ is spent once).
- No `history_months` (no return window); needs SF3 quarter t-1.

## 9. OSAP metadata
Chen, Hong and Stein (2002), JFE; Cat.Data 13F; Cat.Economic ownership; continuous; sample 1979-1998;
Acronym2 DelBreadth; Portfolio Period 3, Start Month 6; EW; LS quantile 0.1; Test port sort size adjusted
(Table 4A, 1 quarter); `Predictability in OP` 1_clear, `Signal Rep Quality` 1_good. Source
`Predictors/DelBreadth.py`; upstream `InstitutionalHoldings13F.py`, `tr13f_pmg_edit.sas` cached.

## 10. Proposed Sharadar mappings
None proposed for Stage 1 (blocked by min_months). If pursued: route (a) via SF3 (`investorid`, `ticker`,
`securitytype == "SHR"`, `date`) with a 45-day lag; flagged NOT IN field_map: `SF3A.shrholders`,
`SF3.investorid`; also no ticker-to-permno crosswalk needed (ticker-keyed). Frontier row: `infeasible`
— "13F from 2013-06-30 only: max 97-99 decision months < rebalance.min_months 120".
