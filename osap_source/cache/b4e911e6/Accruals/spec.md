# Accruals — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: APPROX (constructible; one term unavailable)
Checked against `osap_source/field_map_index.yaml`. Every status is a mapping,
not a proof, on this snapshot (verified_on empty): field-checker to verify each.

| OSAP var | field_map key | Sharadar | index status | role |
|---|---|---|---|---|
| act | compustat.act | SF1.assetsc | mapped | level, t and t-12m |
| che | compustat.che | SF1.cashneq + investmentsc.fillna(0) | approx | level, t and t-12m |
| lct | compustat.lct | SF1.liabilitiesc | mapped | level, t and t-12m |
| dlc | compustat.dlc | SF1.debtc | mapped | level, t and t-12m |
| at | compustat.at | SF1.assets | mapped | level, t and t-12m (denominator) |
| dp | compustat.dp | SF1.depamor | mapped | FLOW (TTM sum on ART), current only |
| txp | compustat.txp | none | UNAVAILABLE | change-in-taxes-payable term |

- **txp is missing.** predictor.py zero-fills it itself (`tempTXP = txp.fillna(0)`;
  txp is NOT in the upstream `zero_fill_vars`), so on Sharadar the Δtxp term is
  dropped. Zero-fill of an optional term: **approx**, not infeasible. The term
  enters as `+Δtxp` (small next to Δlct). Flag in registry: ΔTP omitted.
- che is approx per the index: cashneq + investmentsc overshoots Compustat che for
  captive-finance names (loan receivables in investmentsc). Never cashneq alone.
- Nulls: assetsc/liabilitiesc/debtc ~20% (unclassified balance sheets: 71%
  Financial Services, 20% Real Estate); assets 0.05%; depamor 9.6% ART. OSAP's dlc
  is not zero-filled and banks lack it, so OSAP also loses most financials.
- Early-window caveat: ART TTM flows are ~50% populated for calendardate
  1998Q1-Q3, so depamor (ART) at early-1999 signal dates (latest filing still a
  1998Q1-Q3 period) is half-null; do not read those nulls as zeros (section 7).

## 2. Variables by exact source name (predictor.py)
`m_aCompustat` columns gvkey, permno, time_avail_m, txp, act, che, lct, dlc, at,
dp. Upstream (upstream_CompustatAnnual.py: FUNDA, consol C, INDL, STD, USD): rows
with null at, prcc_c or ni dropped; then act, che, dp, lct (among others) are
**zero-filled**; dlc, at, txp are not. `time_avail_m = datadate + 6 months`,
annual values forward-filled monthly (offsets 0-11), de-duplicated on
(permno, time_avail_m).
## 3. Formula
Sloan (1996) working-capital accruals less depreciation, over average assets:

    tempTXP = txp.fillna(0)
    Accruals = ( (act - act[-12]) - (che - che[-12])
               - ( (lct - lct[-12]) - (dlc - dlc[-12]) - (tempTXP - tempTXP[-12]) )
               - dp ) / ((at + at[-12]) / 2)

`[-12]` = `groupby(permno).shift(12)` on monthly ROWS (a panel gap misaligns it).
dp is the current-year level, not a change. The SignalDoc prose omits the dp
subtraction; the code subtracts it (code is authority).
Sharadar form: `dWC = d(assetsc) - d(cashneq+investmentsc.fillna(0)) -
(d(liabilitiesc) - d(debtc))`; `Accruals = (dWC - depamor_ART) /
((assets_t + assets_{t-12m})/2)`.

## 4. Timing and lag convention
- OSAP: fiscal-year data available datadate + 6m; 12-row lag = prior fiscal year;
  refreshes once a year. Sharadar ART as-of datekey: balance items are the latest
  filed LEVEL (ART == ARQ), refreshing each quarter, up to ~9 months fresher than
  OSAP; the change spans the latest 4 quarters, not the fiscal year.
- Year-ago level: `ctx.fundamentals(fields, lag_months=12)` is the simplest route
  (needs history_months >= 12); it equals "4 quarters ago" only if filing lags are
  stable. Preferred if the API allows: the row with reportperiod one year earlier.
  Translator decides and states it in the docstring.
- Flow item: depamor under ART is a TTM sum of 4 quarters, the right analogue of
  annual dp, and is used as a CURRENT LEVEL (no YoY difference), so no TTM smear.
  Do NOT set `dimension=ARQ`: a single-quarter dp would understate dp about 4x.
  Keep the ART default.
- First months: year-ago balance sheets for signal dates in 1999 come from
  1998 as-of dates; the snapshot ART holds 1997Q4 in breadth, so the first 1-3
  signal months may be thin under lag_months=12. preflight must report first-month
  coverage.
- ASC 842 (2019+): debtc/liabilitiesc may absorb operating-lease liabilities and
  depamor may include ROU amortisation; a one-time level break in the YoY change
  for affected names. Caveat only.
- fxusd cancels (ratio of SF1 fields in reporting currency).
## 5. Filters
- predictor.py applies no price or sample filter. SignalDoc `Filter = abs(prc)>5`
  (EW, LS quantile 0.1) is a portfolio-stage filter in OSAP; do NOT add it to the
  factor (no universe filters in a factor); the harness uses price >= $1.
  Recorded as a deviation from the published portfolio.

## 6. Predicted sign (SignalDoc)
`Sign = -1.0`: high accruals predict low returns. Score = -Accruals (long low).
Sloan 1996; Cat.Signal Predictor; Cat.Economic `accruals`; Cat.Form continuous;
Cat.Data Accounting; sample 1962-1991; Predictability in OP 1_clear; Signal Rep
Quality 1_good; Key Table "6 year t+1"; port sort size adjusted.

## 7. The mass-point question
A do-nothing firm (no change in any balance-sheet item) gets `-dp/at`, a
continuous negative value: no mass point from inactivity. Exact ties need dp == 0
(3.8% of non-null ART depamor) AND all four deltas exactly zero: a near-empty set
of dormant shells; share not measured here, preflight reports the modal-value
share. Ties: average rank (harness concern). Zero-fill hazards:
- Do not zero-fill act/lct/che/dlc/at (OSAP does for act/che/lct/dp): the ~20% null
  block, mostly financials, would collapse onto `-dp/at`. Emit NaN instead.
- dp: OSAP fills dp=0 when null. On Sharadar a null ART depamor (9.6%) would turn
  the score into dWC/avgAT, a discontinuity. Recommended: fill 0 only for
  reportperiod >= 1998Q4 (genuine no-D&A reporters); NaN before (the half-null
  1998Q1-Q3 flows). Log the choice.

## 8. History needed
`history_months = 12` plus filing lag. ART begins 1997Q4; decisions from 1999-01;
thin coverage possible in the first 1-3 months (section 4).

## 9. OSAP metadata
Acronym Accruals; Sloan 1996 (Accounting Review); Cat.Economic accruals; Sign -1;
start month 6; portfolio period 12; EW; LS quantile 0.1; Filter abs(prc)>5.
Source `Signals/pyCode/Predictors/Accruals.py` at
b4e911e69678a7424f318617a61d813f54183123. Cached here: predictor.py,
signaldoc_row.csv, upstream_CompustatAnnual.py, upstream_SignalMasterTable.py,
upstream_save_standardized.py. Output `Accruals.csv [permno, yyyymm, Accruals]`.

## 10. Proposed Sharadar mappings and deviations
1. act -> assetsc (null 20%); NaN instead of OSAP zero-fill.
2. che -> cashneq + investmentsc.fillna(0) (approx); require cashneq non-null.
3. lct -> liabilitiesc. 4. dlc -> debtc (27% exact-zero INPUT among non-null is
   genuine; a delta, so no output mass point).
5. at -> assets, mean of t and t-12m; guard avg > 0.
6. dp -> depamor (ART TTM); null rule in section 7.
7. txp -> UNAVAILABLE; Δtxp term omitted (approx).
8. Score = -Accruals. All reads via MonthContext.fundamentals.
Fields not in field_map: none. Open: year-ago level mechanism, dp null rule.
