# dVolCall — Change in call implied volatility (An, Ang, Bali, Cakici 2014, JF, Table IIA)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/dVolCall.py` (cached `predictor.py`,
`upstream_OptionMetricsVolSurf.R`, `upstream_config.py`, `signaldoc_row.csv`).

## 1. Data availability — VERDICT: data_unavailable (recommend `infeasible`)

The only input is OptionMetrics' volatility surface (`optionm.vsurfd*`: `impl_volatility` by secid,
cp_flag, delta, days, date), plus the secid-permno link in SignalMasterTable. Sharadar does not publish
option prices, option volume or implied volatility in any of the 13 held tables.
- Columns of all 13 tables checked on this snapshot (ACTIONS, DAILY, DESCRIPTIONS, EVENTS, METRICS, SEP,
  SF1, SF2, SF3, SF3A, SF3B, SP500, TICKERS): none is an implied volatility, option price, option volume
  or open interest. DESCRIPTIONS keyword search (implied / volatil / option / forecast / estimate) hits
  only SF1 `sbcomp`/`ncfcommon`/`roic`, SF2 option-exercise fields (`dateexercisable`,
  `priceexercisable`, `expirationdate`: insider derivative filings) and SF3 `securitytype`.
- SF3A `cllholders/cllunits/cllvalue/putholders/putunits/putvalue` are quarterly 13F option HOLDINGS
  by institutions: a different object, a different frequency, not a 30-day 50-delta implied vol. Not a proxy.
- No realised-volatility stand-in: the signal is a difference of a forward-looking option-market
  quantity; substituting SEP return volatility would be a different hypothesis, not this predictor.
- Missing-item rule: OSAP does NOT zero-fill or otherwise substitute impl_vol. In the predictor
  `fillna` is absent; `upstream_CompustatAnnual.py zero_fill_vars` is Compustat-only and irrelevant. A firm
  without a surface observation gets NaN. Nothing to approximate -> `infeasible`.
- Not in field_map_index.yaml (no `optionm.*` key, no `crsp.secid` key). Field-checker run: not needed.
- Upstream note: `upstream_config.py` sets PATCH_OPTIONM_IV = True, so OSAP's own pipeline reads a
  2023-vintage published column instead of rebuilding from the surface; the construction below is the
  documented one.

## 2. Variables (exact source names)
`secid, time_avail_m, days, delta, cp_flag, impl_vol` from `OptionMetricsVolSurf.csv` (last daily obs of
each month per secid/cp_flag/delta/days, `date` month-end-stamped); `permno, time_avail_m, secid` from
SignalMasterTable.

## 3. Formula
Keep `days == 30` and `abs(delta) == 50` and `cp_flag == "C"`. Sort by secid, time_avail_m.
```
l1_impl_vol = groupby(secid).shift(1)              # previous ROW, not previous calendar month
dVolCall        = impl_vol - l1_impl_vol                 # first difference of call implied vol
```
Left-merged onto the SignalMasterTable by (secid, time_avail_m). No winsorising, no other filter.
Note the shift is over the firm's retained rows: a gap month (no surface obs) makes the "change"
span several months.

## 4. Timing
Month-end surface observation for month t is used for month t (time_avail_m = that month). Not a
flow item; no ART/ARQ issue; no fundamentals involved.

## 5. Filters
None in the predictor; SignalDoc Filter blank. Coverage is limited to optionable names with a surface
(OptionMetrics sample starts 1996).

## 6. Predicted sign
SignalDoc Sign = 1.0 (high call-vol change predicts HIGH returns). Cat.Economic: informed trading. Predictability in OP: 1_clear.

## 7. Mass-point question (would-be)
A do-nothing firm has impl_vol unchanged, difference 0 exactly; OptionMetrics interpolated surface
values are continuous, so exact-zero ties should be rare (stale/carried surfaces the exception). Not
measurable here: no data. Moot given the availability verdict.

## 8. History needed
Two consecutive month-end surface points. OptionMetrics sample 1996-2011 in the paper; snapshot is
irrelevant since no data exists.

## 9. OSAP metadata
Predictor | 1_clear | 1_good | An, Ang, Bali, Cakici 2014 JF | continuous | Options | informed trading |
sample 1996-2011 | Acronym2 dImpVolCall | Sign 1.0 | EW | LS quantile 0.1 | Portfolio period 1 | Start month 12 |
Filter none | Return 1.09, t 3.45 (port sort, Table IIA) | cites 473.

## 10. Proposed Sharadar mappings
None. `impl_vol` has no Sharadar counterpart; no factor file should be written.
Recommended frontier row: `data_unavailable` — "needs OptionMetrics implied-volatility surface (30d, 50-delta
call); no Sharadar table publishes option prices/IV (13 held tables checked); OSAP does not zero-fill it".
