# ChForecastAccrual — Change in forecast and accrual (Barth and Hutton 2004)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/ChForecastAccrual.py` (cached
`predictor.py`, `signaldoc_row.csv`). DATA_SHA 198b281de1a0. SignalDoc row (Cat.Signal == Predictor):
Cat.Data = Analyst, Cat.Economic = earnings forecast, Cat.Form = discrete, Journal RAS,
sample 1981-1996. Upstream IBES download read from the cached
`../AnalystRevision/upstream_IBESEPSUnadjusted.py` (same ref); not re-fetched.

## 1. Data availability (verdict: INFEASIBLE — recommend `infeasible`)

The signal is a sign-of-change in the IBES consensus mean EPS forecast, gated by an accruals
median split. The forecast term is the signal's only non-zero output; without it every row is NaN.
This snapshot holds no IBES and no analyst-estimate table (13 tables; none carries forecasts).
OSAP does NOT zero-fill `meanest`: a missing forecast leaves the signal NaN (masks require
`meanest.notna()`). No proxy is faithful (a realised-EPS change is a different signal).

| input (OSAP) | field_map key | Sharadar | status | note |
|---|---|---|---|---|
| `meanest` (IBES `statsumu_epsus`, fpi = "1", statpers month) | none (no `ibes.*` key in `field_map_index.yaml`; grep ibes/meanest finds nothing) | none | UNAVAILABLE | analyst data; blocking |
| `tickerIBES` (SignalMasterTable, IBES-CRSP link) | none | none | unavailable | only needed to reach `meanest` |
| `act` | `compustat.act` | `assetsc` | mapped (verified 2026-09-30) | null ~20% (unclassified BS rows) |
| `che` | `compustat.che` | `cashneq + investmentsc.fillna(0)` | approx (verified 2026-09-30) | |
| `lct` | `compustat.lct` | `liabilitiesc` | mapped (verified 2026-09-30) | |
| `dlc` | `compustat.dlc` | `debtc` | mapped (verified 2026-09-30) | |
| `txp` | `compustat.txp` | none | UNAVAILABLE | no SF1 field. OSAP does not zero-fill `txp` (upstream CompustatAnnual zero-fills act/che/dp/lct but not dlc/at/txp) and this script uses raw `txp` with no fillna, so a missing `txp` makes the gate NaN in OSAP; a Sharadar `txp = 0` would be a deviation (approx of the gate only) |
| `at` | `compustat.at` | `assets` | mapped (verified 2026-09-30) | |

Two independent blockers: (a) `meanest` (no data, no OSAP zero-fill); (b) `txp` (unavailable; a
`txp = 0` substitution would be an approx of the gate only). (a) alone is decisive.
Do not field-check, translate or preflight. Log an `osap_frontier.yaml` row with reason
"IBES consensus EPS forecasts (analyst data) — not in Sharadar snapshot; no OSAP zero-fill;
no estimates table; also txp unavailable".

## 2. Variables (exact source names)
From `m_aCompustat`: `act, che, lct, dlc, txp, at` (annual, forward-filled monthly, available
datadate + 6m; de-duplicated on permno/time_avail_m). From IBES `IBES_EPS_Unadj`: `meanest` with
`fpi == "1"` (1-year-ahead EPS), joined via `tickerIBES` (SignalMasterTable) on `time_avail_m`.

## 3. Formula
    tempAccruals = ((act-act[-12]) - (che-che[-12]) - ((lct-lct[-12]) - (dlc-dlc[-12]) - (txp-txp[-12])))
                   / ((at + at[-12]) / 2)            # NaN if denominator == 0 or inf
    tempsort     = qcut(tempAccruals, 2) by month over ALL rows of the firm-month panel (1 = low, 2 = high)
    meanest_l    = meanest shifted 1 ROW within permno   # a panel gap misaligns it (prior row, not prior month)
    ChForecastAccrual = 1 if meanest > meanest_l; 0 if meanest < meanest_l; NaN if equal or either missing
    ChForecastAccrual = NaN where tempsort == 1 (lower half of accruals)
Output: rows with non-NaN value only. Sloan accruals WITHOUT the dp term here (differs from OSAP `Accruals`).
Sharadar form (were it feasible): same, with `txp` unavailable.

## 4. Timing / lag
Accruals refresh once a year (annual fiscal data, +6m); the forecast term refreshes monthly, so the
signal is driven by the monthly forecast direction within the high-accrual half. Under Sharadar ART
the balance items are latest-filed levels (ART == ARQ for a level), quarterly refresh, up to ~9
months fresher than OSAP; the 12-month change spans 4 quarters. No flow item is differenced
(balance-sheet levels only), so no TTM smear and no `dimension=ARQ` issue. IBES `statpers` month
stamps the estimate; OSAP treats it as available in the same month (`time_avail_m = statpers` month).
Moot given infeasibility.

## 5. Filters
predictor.py applies none. SignalDoc `Filter` is empty; `Stock Weight = EW`, no quantile filter,
`Portfolio Period = 12`, `Start Month = 6`. The accruals upper-half gate is part of the signal.

## 6. Predicted sign (SignalDoc)
`Sign = 1.0`: long = forecast increase (1) in the high-accrual half, short = forecast decrease (0).
Return 1.0, T-Stat 2.375 (SignalDoc, published). Predictability in OP 1_clear; Signal Rep Quality
1_good. Notes: "OP basically does a double sort on accruals and revisions"; detailed definition:
within upper half of Accruals distribution, 1 if mean earnings estimate increased vs previous month,
0 if decreased.

## 7. The mass-point question
The output is binary {0, 1} (a two-point distribution), by construction. A do-nothing firm (forecast
unchanged, or no coverage, or lower-half accruals) gets NaN, not a value. Among scored names the
split is roughly even between up and down revisions, but the scored set is a fraction of the universe:
high-accrual half (~50%) x IBES coverage x a strictly changed forecast (only a minority of monthly
consensus changes are exactly zero, but large share of firms lack coverage). Not measured: no IBES
data. If it were built, decile ranks would collapse to two tied groups; Stage 1 deciles and
>= 30 names per decile would fail on ties, and the tie-handling (average rank) gives two rank values.

## 8. History needed
Accruals: 12-month lag of five balance items (at least 12 months). Forecast: prior month only. OSAP
sample 1981-1996; IBES starts 1976. Snapshot starts 1998-01; irrelevant given infeasibility.

## 9. OSAP metadata
Acronym ChForecastAccrual; Acronym2 ChFAccrual; Authors Barth and Hutton; Year 2004; Journal RAS;
LongDescription "Change in Forecast and Accrual"; Cat.Form discrete; Cat.Data Analyst;
Cat.Economic earnings forecast; SampleStartYear 1981, SampleEndYear 1996; Evidence Summary
"p-val < 0.001 in port sort"; Key Table 3B (also 3A); Test in OP port sort; Sign 1.0;
Return 1.0; T-Stat 2.375; Stock Weight EW; LS Quantile and Quantile Filter blank;
Portfolio Period 12; Start Month 6; GScholarCites202509 394. Source file tree line 536
(`Signals/pyCode/Predictors/ChForecastAccrual.py`).

## 10. Proposed Sharadar mappings / deviations
None proposed. No Sharadar table publishes analyst forecasts; the EVENTS table (8-K item codes)
and SF1 realised `eps` are not forecast proxies and would define a different signal. Fields not in
the map: `ibes.meanest`, `ibes.tickerIBES` (absent entirely); `compustat.txp` is in the map as
`unavailable`. Recommendation: `infeasible` (reason: IBES forecasts absent, no OSAP zero-fill).
