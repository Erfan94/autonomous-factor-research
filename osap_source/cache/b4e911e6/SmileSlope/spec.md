# SmileSlope — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: DATA_UNAVAILABLE (infeasible)
| OSAP input | Sharadar | status |
|---|---|---|
| `OptionMetricsVolSurf` `impl_vol` (vsurfd daily volatility surface; `days`, `delta`, `cp_flag`) | none | UNAVAILABLE: options implied volatility |
| `secid` (OptionMetrics id, from SignalMasterTable) | none | UNAVAILABLE |
| `permno, time_avail_m` (SignalMasterTable) | SEP presence x universe | mapped / harness-side |
- Checked: the 13 held tables (ACTIONS, DAILY, DESCRIPTIONS, EVENTS, METRICS, SEP, SF1, SF2, SF3, SF3A, SF3B, SP500, TICKERS) carry no column naming
  implied volatility, delta, skew or option (column-name scan of every parquet; only `volume`/`divyield`-type hits, none options). `field_map_index.yaml` has
  no options entry. SF2 is insider transactions, SF3* are 13F holdings: neither is option data.
- Missing-item rule: OSAP does NOT zero-fill the item. `Predictors/SmileSlope.py` left-merges the surface onto the master table and keeps
  `SmileSlope.notna()` rows only, so a firm without options is absent, not 0. No fill exists to justify `approx`. **Recommend `infeasible` (data_unavailable).**
- The `PATCH_OPTIONM_IV` branch (config) loads the 2023 vintage of the signal from `openassetpricing`: still OptionMetrics-derived, no Sharadar route.
- Not measured: nothing to measure on the snapshot (no input exists). Measured on: n/a.

## 2. Variables (exact source names)
`OptionMetricsVolSurf.csv`: `secid, time_avail_m, days, delta, cp_flag, impl_vol`; `SignalMasterTable`: `permno, time_avail_m, secid`.

## 3. Formula
```
df = surface[(days == 30) & (abs(delta) == 50)][secid, time_avail_m, cp_flag, impl_vol]
pivot(index=[secid,time_avail_m], columns=cp_flag, values=impl_vol, aggfunc="first")
SmileSlope = P - C          # put implied vol minus call implied vol, 30-day, 50-delta
merge onto SignalMasterTable on (secid, time_avail_m), keep SmileSlope.notna()
```
SignalDoc: "keep last observation each month" of the daily surface (prep upstream; `OptionMetricsVolSurf.csv` is month-end last obs).

## 4. Timing / lag
Month-end observation of the surface labelled `time_avail_m` (no further lag in the predictor). No SF1 input: ART/ARQ and TTM smearing do not apply.

## 5. Filters
SignalDoc `Filter` empty. Population is whatever firms have a 30-day 50-delta put AND call on the month-end surface (optionable names only).

## 6. Predicted sign
`Sign = -1.0` (Yan 2011: steeper smile = higher put than call IV predicts LOWER returns). Orientation for a factor would be negative.

## 7. Mass-point question
Continuous (difference of two implied vols), no do-nothing mode expected in OSAP. Moot here: no data.

## 8. History needed
OSAP sample 1996-2005 paper, surface from 1996-01. Moot: the snapshot has no options table at any date.

## 9. OSAP metadata
Yan (2011), JFE; Cat.Data Options; Cat.Economic optionrisk; continuous; Acronym2 OSmirkCP; sample 1996-2005; Key Table 5A (port sort); EW; LS Quantile 0.2;
Portfolio Period 1, Start Month 12; 1_clear / 1_good. SignalDoc Detailed Definition: OptionMetrics daily vsurfd, last obs each month, delta = +-0.50,
days = 30, signal = put IV minus call IV. Source `Signals/pyCode/Predictors/SmileSlope.py`.

## 10. Proposed Sharadar mappings
None. No Sharadar field carries option-implied volatility; a realized-vol or skewness proxy would be a different signal. Fields not in the map:
`optionmetrics.impl_vol`, `optionmetrics.secid` (no `field_map_index.yaml` entry; unavailable by the table scan above).
