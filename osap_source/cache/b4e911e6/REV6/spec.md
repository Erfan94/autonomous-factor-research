# REV6 — Earnings forecast revisions (Chan, Jegadeesh and Lakonishok 1996, JF, Table 7)

OSAP ref b4e911e69678a7424f318617a61d813f54183123 (cache b4e911e6); source `Signals/pyCode/Predictors/REV6.py` (cached
`predictor.py`, `signaldoc_row.csv`, `upstream_IBESEPSUnadjusted.py`). SignalDoc row (Cat.Signal == Predictor):
Cat.Data = Analyst, Cat.Economic = earnings forecast, Predictability 1_clear, Quality 1_good. DATA_SHA 198b281de1a0.

## 1. Data availability (verdict: DATA_UNAVAILABLE -> recommend `infeasible`)

| input (OSAP) | Sharadar | status |
|---|---|---|
| `meanest` (IBES summary history, `fpi == "1"`, unadjusted; WRDS `ibes.statsum_epsus`) | none | unavailable |
| `statpers`, `fpedats` (IBES forecast dates, used for the stale-estimate fill-forward) | none | unavailable |
| `tickerIBES` (IBES-to-CRSP link in SignalMasterTable) | none | unavailable |
| `prc` (SignalMasterTable, lagged one month) | SEP.closeunadj (`crsp.prc`) | mapped |

- Sharadar holds no analyst estimate, forecast, consensus or revision item. Checked on this snapshot: the DESCRIPTIONS table
  (every indicator of SF1/SEP/DAILY/METRICS/SF2/SF3*/EVENTS/ACTIONS/TICKERS/SP500) has no row mentioning estimate, forecast,
  analyst, consensus or dispersion (a text search over title and description returned only `roic` and the ACTIONTYPES
  `exchangefrom/exchangeto` rows, both false hits). SF1 `epsusd`/`eps` are REPORTED actuals, not expectations.
- field_map_index.yaml has no IBES key. Standing unavailable: ibes.
- **No zero-fill rescue.** REV6 is `sum(tempRev_0..tempRev_6, skipna=False)`: NaN if ANY of the seven monthly revisions is NaN.
  The script fills nothing with zero (the only fill is a conditional carry-forward of an existing `meanest` when `fpedats`
  matches the prior month and the 30-day validity flag is missing). A missing estimate yields a missing signal, never a neutral one.
- Recommendation: **infeasible** (data_unavailable: IBES mean EPS estimates). No substitute: a price- or earnings-surprise proxy
  (SUE, earnings momentum) is a different predictor, not a translation.
- Not measured: no input exists on the snapshot, so no coverage or mass-point number can be computed for REV6.

## 2. Variables (exact source names)

IBES_EPS_Unadj.parquet: `tickerIBES`, `time_avail_m`, `fpi`, `fpedats`, `statpers`, `meanest`. SignalMasterTable.parquet:
`permno`, `tickerIBES`, `time_avail_m`, `prc`. Intermediates `tmp`, `meanest_lag1`, `fpedats_lag1`, `prc_lag1`, `tempRev`.
Upstream `IBESEPSUnadjusted.py` keeps one row per (tickerIBES, fpi, month) (last `statpers`), `fpi in {0,1,2,6}`, drops missing `meanest`.

## 3. Formula

Analyst revision is the change in the mean next-quarter earnings forecast (`fpi == "1"`, the first fiscal period), month over
month, scaled by last month's price, summed over seven months (t-6 .. t):
```
ibes = ibes[fpi == "1"]
tmp  = 1 if (fpedats not null and fpedats > statpers + 30 days)           # forecast period still far from its end
meanest = meanest_lag1 where tmp is NaN and fpedats == fpedats_lag1 and meanest_lag1 not null   # stale-fill
tempRev = (meanest - meanest_lag1) / abs(prc_lag1)        # lags are row shifts by permno (position, not calendar)
REV6    = tempRev + l1.tempRev + ... + l6.tempRev         # skipna=False: NaN if any of the 7 terms is NaN
```
Note: the merge puts `meanest` on the master table by (tickerIBES, time_avail_m); a month without an IBES row yields NaN and
breaks the window, so a stock needs seven consecutive months of estimate data (eight months of `meanest`).

## 4. Timing / lag convention

`time_avail_m` is the month of the IBES statistical period (`statpers`, third Thursday of the month); prc is the month-end
price of the prior month. No extra publication lag in OSAP. No SF1/ART/ARQ input, so the ART-as-of-filing and TTM-smearing
questions do not arise.

## 5. Filters

SignalDoc Filter blank; the script applies none beyond `fpi == "1"` and a non-missing estimate. The paper's sample is 1977-1992.

## 6. Predicted sign

`Sign = +1.0` (T-Stat 4.07, Table 7 regressions, "mv reg"; Table 5 portfolio returns are without t-stats). SignalDoc note: only
monthly rebalancing works in portfolio sorts (Portfolio Period 1, Start Month 12, EW). Upward revisions predict higher returns.

## 7. The mass-point question

Not measurable on Sharadar (input absent). Structurally: a firm with no analyst revision over seven months produces an exact
0 (every `meanest` unchanged) - a mass point at zero whose share is plausibly large among thinly covered stocks, since IBES
mean estimates move only when an analyst revises, and revisions cluster around earnings dates. Where there is coverage the
value is continuous (price-scaled). Missing coverage is NaN, not 0. Ties: average rank would be required for the zero block.

## 8. History needed

OSAP sample 1977-1992; IBES summary data runs from 1976. Seven months of estimates plus one price lag; nothing in the
snapshot (starts 1998-01) can supply them.

## 9. OSAP metadata

Acronym REV6 (Acronym2 EPSrevise), Chan, Jegadeesh and Lakonishok 1996, Journal of Finance, "Earnings forecast revisions",
Cat.Form continuous, Cat.Data Analyst, Cat.Economic earnings forecast, SampleStartYear 1977, SampleEndYear 1992, Key Table 7
R6, Test mv reg, Stock Weight EW, Portfolio Period 1, Start Month 12, GScholarCites 3322. Output column `REV6`.

## 10. Proposed Sharadar mappings

None. `meanest`, `statpers`, `fpedats`, `tickerIBES`: no Sharadar field (data_unavailable; no IBES key in field_map_index.yaml).
Only `prc` (SEP.closeunadj, mapped) would exist. Frontier row suggestion: `infeasible` - "IBES mean EPS estimate history
(analyst revisions) not in Sharadar; REV6 is NaN if any of 7 monthly estimate changes is missing (no zero-fill)".
