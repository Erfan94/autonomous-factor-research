# OptionVolume1 — Option to stock volume (Johnson and So 2012, JFE, Table 2A; SignalDoc Acronym2 OptVol)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Signals/pyCode/Predictors/ZZ1_OptionVolume1_OptionVolume2.py` (emits OptionVolume1 and OptionVolume2; cached as `predictor.py`;
`upstream_OptionMetricsVolume.R`, `upstream_OptionMetricsCRSPLink.py`). The SignalDoc row (Acronym OptionVolume1, Cat.Signal Predictor) is the authority, not the filename.
DATA_SHA 198b281de1a0. Written fresh from the source and `field_map_index.yaml`.

## 1. Data availability (VERDICT: DATA_UNAVAILABLE; recommend `infeasible`)
| OSAP input | origin | Sharadar | status |
|---|---|---|---|
| `optvolume_js12` (daily option contract volume summed to month, all puts and calls, Johnson-So maturity filters) | OptionMetrics `opprcd*` via WRDS (`OptionMetricsVolume.R`), linked by `secid` (`OptionMetricsCRSPLink`) | NONE | unavailable |
| `vol` (monthly CRSP share volume) | CRSP | SEP `volume` (daily, split-restated) | mapped |
| `prc`, `shrcd`, `secid` | SignalMasterTable | universe / TICKERS | n/a |
- The numerator is an options-exchange volume series. All 13 held Sharadar tables were checked by column name (manifest and parquet schema): ACTIONS, DAILY, DESCRIPTIONS, EVENTS, METRICS, SEP, SF1, SF2, SF3, SF3A, SF3B, SP500, TICKERS.
  None carries option trading volume, open interest, implied volatility or any options-exchange quantity. Near misses, none usable: SF3A/SF3B `putholders/putunits/putvalue` (and `cll*`) are 13F
  institutional HOLDINGS of call/put positions, quarterly, SF3A from 2013-06-30; SF2 is insider Form 4 transactions (incl. derivative securities); METRICS/DAILY/SEP `volume` is stock volume.
  The denominator exists; the numerator does not.
- Missing-item rule: OSAP does NOT zero-fill the option volume. `CompustatAnnual.zero_fill_vars` is irrelevant (an OptionMetrics series, not Compustat), and the predictor sets the signal to NaN
  when `optvolume_js12` or `vol` is missing (`df["OptionVolume1"] = optvolume_js12 / vol`; NaN if either lagged value is missing). So nothing is zero-filled and a missing numerator leaves no score: infeasible.
- Nothing to measure (no input series, no coverage, no mass point). Recommend `infeasible` (data_unavailable), reason: OptionMetrics option volume is not in any held Sharadar table.

## 2. Variables (exact source names)
`optvolume_js12` (OptionMetricsVolume.csv: `secid, date`, summed by `secid, time_avail_m`), `vol` (monthlyCRSP), `secid`, `prc`, `shrcd` (SignalMasterTable), `permno`, `time_avail_m`.

## 3. Formula
```
optvol_m       = sum over days in month of optvolume_js12 by secid          # put + call volume, time-to-expiration filters applied in the R prep script
OptionVolume1  = optvol_m / vol                                             # monthly option volume over monthly stock volume
OptionVolume1  = NaN if the previous month's optvol_m or vol is missing
```
(OptionVolume2 = OptionVolume1 / mean of its six prior values, same script.) The paper works in weekly data; OSAP aggregates monthly.

## 4. Timing / lag convention
Monthly, same month: option and stock volume of month t, no lag; the NaN rule requires month t-1 values to exist. Portfolio Period 1, Start Month 12. Not reproducible here in any timing.

## 5. Filters
SignalDoc Filter: `abs(prc) > 1, shrcd <= 11`; the text adds exclusion when option or stock volume for the previous month is missing. The code applies only the previous-month NaN rule (no price or share-code screen in `predictor.py`).

## 6. Predicted sign
SignalDoc `Sign = -1.0` (high option-to-stock volume -> low future return). `Cat.Form` continuous; `Cat.Data` Options; `Cat.Economic` volume. Stock Weight EW; LS Quantile 0.2.

## 7. The mass-point question
Not applicable (no series can be built). In OSAP, a stock without listed options has NaN (not 0): a do-nothing firm is absent, not a mass point; the scored set is optionable names only (a minority of the universe).

## 8. History needed (snapshot starts 1998-01)
OSAP sample 1996-2010 (OptionMetrics starts 1996). Moot: the series is unavailable in any year.

## 9. OSAP metadata (SignalDoc)
Acronym OptionVolume1; Acronym2 OptVol; Johnson and So; 2012; JFE; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 2_fair; Cat.Form continuous; Cat.Data Options; Cat.Economic volume;
Sample 1996-2010; Key Table 2A (O/S); Test port sort CAPM alpha nonstandard; Sign -1.0; Return 0.916; T-Stat 3.45; EW; LS Quantile 0.2; Portfolio Period 1; Start Month 12; Filter abs(prc)>1, shrcd<=11; GScholarCites 460.
Notes: OP is weekly and sorts deciles, then longs 9+10 and shorts 1+2. Definition: "Total monthly option volume (volume) over all puts and calls, divided by monthly stock trading volume (vol)."

## 10. Proposed Sharadar mappings and deviations
None. No translation: `optvolume_js12` has no Sharadar equivalent and no defensible proxy (SEP/METRICS stock volume is the denominator, not the numerator; SF3A/SF3B put/call holdings are quarterly 13F positions,
a different quantity). Fields not in the map: `optvolume_js12` (OptionMetrics). Classification row for the frontier: `data_unavailable` (options).
