# fgr5yrLag — Long-term EPS growth forecast, lagged (La Porta 1996, JF, Table 3 E{g})

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/fgr5yrLag.py` (cached `predictor.py`,
`upstream_IBESEPSUnadjusted.py`, `signaldoc_row.csv`).

## 1. Data availability — VERDICT: data_unavailable (recommend `infeasible`)

The signal IS an IBES analyst forecast: `ibes.statsumu_epsus`, `fpi == '0'` (long-term growth), `meanest`
renamed `fgr5yr`, joined through `tickerIBES` (SignalMasterTable). There is no fallback and no other
forecast input.
- Sharadar publishes no analyst estimates. Columns of all 13 held tables checked on this snapshot
  (ACTIONS, DAILY, DESCRIPTIONS, EVENTS, METRICS, SEP, SF1, SF2, SF3, SF3A, SF3B, SP500, TICKERS): none is
  a forecast, consensus, estimate or growth expectation. DESCRIPTIONS keyword search (forecast /
  estimate / analyst / long-term growth) finds nothing relevant. EVENTS holds corporate-event codes only;
  METRICS holds price/beta/dividend-yield-forward (a dividend, not an earnings growth forecast).
- No proxy from SF1: realised growth (eps, revenue, netinc) is not an analyst long-term forecast;
  it would be a different signal.
- Missing-item rule: no zero-fill. The predictor requires fgr5yr non-missing (`dropna(subset=required_vars)`
  includes fgr5yr) and emits nothing without it. The upstream Compustat zero_fill_vars list is
  irrelevant. -> `infeasible`.
- Not in field_map_index.yaml (no `ibes.*` key). Field-checker run: not needed.
- Side finding: the Compustat completeness screen uses `dv` while SignalDoc text says `dvp`; moot.

## 2. Variables (exact source names)
IBES: `tickerIBES, time_avail_m (statpers month), fpi, meanest`. Compustat (m_aCompustat): `ceq, ib,
txdi, dv, sale, ni, dp` (presence screen only). SignalMasterTable: `permno, time_avail_m, tickerIBES`.

## 3. Formula
```
ibes     = IBES_EPS_Unadj[fpi == '0'].rename(meanest -> fgr5yr)
df       = m_aCompustat[permno, time_avail_m, ceq, ib, txdi, dv, sale, ni, dp]
           inner-join SignalMasterTable on (permno, time_avail_m) -> tickerIBES
           inner-join ibes on (tickerIBES, time_avail_m)
df       = df.dropna(subset=[ceq, ib, txdi, dv, sale, ni, dp, fgr5yr])
fgr5yrLag(t) = fgr5yr at calendar month t-6 (same permno), via a date-merge
df       = df[month == June]              # keep June rows only
expand each June row to 12 months (June..May) ; drop missing fgr5yrLag
```
In words: the consensus long-term growth forecast from six months before each June (December), carried
forward 12 months (June through the next May).

## 4. Timing
June rows with a December-lagged forecast, forward-filled 12 months: signal refreshes once a year, age
up to 11 months. The lag requires the row at t-6 to survive the same dropna (Compustat presence at t-6).
Not a flow item; ART/ARQ irrelevant.

## 5. Filters
Completeness screen above (joint non-missing of seven Compustat items and fgr5yr). SignalDoc Filter blank.

## 6. Predicted sign
SignalDoc Sign = -1.0 (high long-term growth forecast predicts LOW returns). Cat.Economic: earnings forecast.

## 7. Mass-point question (would-be)
IBES long-term growth is reported in whole/half percent points and analysts cluster at round numbers
(10, 12, 15, 20); `meanest` averages several analysts, but single-analyst names give round values, so ties
would be frequent. Not measurable here (no data).

## 8. History needed
IBES LTG from 1982; Compustat presence at t and t-6. Moot.

## 9. OSAP metadata
Predictor | 1_clear | 1_good | La Porta 1996 JF | continuous | Analyst | earnings forecast | sample 1983-1990 |
Acronym2 EPSForeLTlag | Sign -1 | EW | Portfolio period 3 | Start month 6 | Filter none | t 4.9 (regression,
Table 3 E{g}) | cites 1468. Notes: timing of the lag matters; monthly arithmetic mean used.

## 10. Proposed Sharadar mappings
None for `fgr5yr`. Compustat presence items would map (ceq->equity approx, ib->netinc, txdi, dv, sale->revenue,
dp->depamor) but are screens only; without IBES there is no signal. Recommended frontier row:
`data_unavailable` — "needs IBES long-term growth forecast (fpi 0); no Sharadar table publishes analyst
estimates (13 held tables checked); OSAP does not zero-fill it".
