# dCPVolSpread — Change in put implied volatility minus change in call implied volatility (An, Ang, Bali, Cakici 2014, JF, Table IIC)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/dCPVolSpread.py` (cached `predictor.py`;
upstream `OptionMetricsVolSurf.R`, `config.py` cached). DATA_SHA 198b281de1a0. Construction only.

## 1. Data availability (verdict: DATA_UNAVAILABLE — recommend `infeasible`)
| OSAP input | Sharadar | status |
|---|---|---|
| `OptionMetricsVolSurf.impl_vol` (30-day, |delta| 50, calls and puts, by `secid`) | none | unavailable |
| `secid` link from `SignalMasterTable` | none | unavailable |
- Checked on THIS snapshot: held tables are ACTIONS, DAILY, DESCRIPTIONS, EVENTS, METRICS, SEP, SF1, SF2, SF3, SF3A, SF3B, SP500, TICKERS. None carries option prices or implied volatility. DESCRIPTIONS has no implied-volatility or option-price indicator; the only "call"/"put" fields are SF3A/SF3B 13F holdings counts (`cllholders`, `putholders`, `cllunits`, `putunits`; quarterly, from 2013-06), which are position counts, not volatilities.
- OSAP missing-item rule: no zero-fill. The predictor keeps only rows with both legs from the vol surface and left-merges onto the master table, so every firm-month without an OptionMetrics surface is NaN; `zero_fill_vars` (CompustatAnnual) does not touch it. The `PATCH_OPTIONM_IV` branch (config) just re-downloads the published 2023-vintage signal; it is not a construction from data we hold.
- No IBES/13F pre-2013/patents/segments/ratings/pensions/xad/emp/ob/ppegt; the blocker is options.

## 2. Variables (exact source names)
`secid, time_avail_m, days, delta, cp_flag, impl_vol`; derived `impl_volC, impl_volP, dVolCall, dVolPut, dCPVolSpread`.

## 3. Formula in words and key lines
Keep the 30-day-maturity, |delta| = 50 surface points. For each firm-month take the call and put implied volatility, difference each over the prior month, and subtract: put-volatility change minus call-volatility change.
```
options = options[(days == 30) & (abs(delta) == 50)]
dVolCall = impl_volC.groupby(secid).diff();  dVolPut = impl_volP.groupby(secid).diff()
dCPVolSpread = dVolPut - dVolCall
```
`diff()` runs over consecutive rows of the secid, not calendar months (a gap makes the change span more than a month).

## 4. Timing / lag
Monthly OptionMetrics values at `time_avail_m` (month-end surface), no lag. No fundamentals: ART/TTM smear not applicable.

## 5. Filters
None in the predictor (SignalDoc Filter blank). Coverage limited to optionable names, from 1996.

## 6. Predicted sign
SignalDoc `Sign = -1.0` (Return -1.68, T-Stat 6.77, EW, LS Quantile 0.1): a rising put-minus-call volatility spread predicts lower returns; LOW dCPVolSpread is the long leg.

## 7. The mass-point question
Continuous difference of differences of volatilities; a do-nothing firm gives 0 only when both implied vols are unchanged to the source's precision. Not measured (no input). Moot.

## 8. History needed (snapshot starts 1998-01)
Two consecutive monthly surfaces per firm; the OptionMetrics sample starts 1996. Not measured.

## 9. OSAP metadata
dCPVolSpread; Acronym2 dImpVolSmile; An, Ang, Bali, Cakici 2014 JF; Cat.Signal Predictor; Cat.Form continuous; Cat.Data Options; Cat.Economic informed trading; Sample 1996-2011; Key Table "Table IIC"; Test port sort; Evidence "t=7 in port sort"; Sign -1.0; Return -1.68; T-Stat 6.77; EW; LS Quantile 0.1; Portfolio Period 1.0; Start Month 12.0; GScholar cites 473. Definition: "Take difference of dVolCall and dVolPut".

## 10. Proposed Sharadar mappings
None: `data_unavailable`. Fields not in the map: `impl_vol`, `secid`, `delta`, `cp_flag` (no Sharadar source).
Recommendation: **infeasible** (reason: needs OptionMetrics implied volatility; no held Sharadar table carries option data; OSAP drops, not zero-fills, missing rows).
