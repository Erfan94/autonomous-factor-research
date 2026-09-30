# OptionVolume2 — Abnormal option volume (Johnson and So 2012 JFE, Table 2A)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/ZZ1_OptionVolume1_OptionVolume2.py`
(cached `predictor.py`, `upstream_OptionMetricsVolume.R`, `upstream_OptionMetricsCRSPLink.py`). The SignalDoc
row (`Cat.Signal == Predictor`) is the authority; the filename is a `ZZ1_*` script that emits both
OptionVolume1 and OptionVolume2. DATA_SHA 198b281de1a0 (snapshot as recorded 2026-09-30).

## 1. Data availability — VERDICT: data_unavailable (recommend `infeasible`)

| input (OSAP) | source | Sharadar | status |
|---|---|---|---|
| `optvolume_js12` (daily OptionMetrics option volume, expiries 5..~35 trading days out, cp_flag != NaN, volume > 0) | OptionMetrics `opprcd<year>` via WRDS | none | UNAVAILABLE |
| `secid` (OptionMetrics id, linked to permno) | `wrdsapps_link_crsp_optionm.opcrsphist` | none | UNAVAILABLE |
| `vol` (CRSP monthly stock volume) | CRSP | SEP.volume (daily, summable) | mapped (`crsp.vol`) |
| `prc`, `shrcd` (filters) | SignalMasterTable | SEP close / TICKERS.category | mapped / approx |

- Checked all 13 held tables by column name (SF1 112, SF2 23, SF3 6, SF3A 29, SF3B 29, SEP 10, DAILY 10,
  METRICS 22, TICKERS 28, ACTIONS 7, EVENTS 3, DESCRIPTIONS 7, SP500 7): no option-volume, option-price, implied-vol,
  open-interest or OptionMetrics-id column. The only `put*` hits are `putholders/putunits/putvalue` (SF3A) and
  `putholdings/putunits/putvalue` (SF3B): 13F institutional put POSITIONS (quarterly, stock-holder reported), not
  traded option volume. They are not a substitute and none is offered.
- No zero-fill rescue: the predictor has NO `fillna` on either option volume or stock volume and CompustatAnnual
  is not involved. A missing `optvolume_js12` makes OptionVolume1 NaN, which makes OptionVolume2 NaN.
  The signal's defining input is absent for every firm, so the signal is undefined for 100% of the universe.
- Measured: nothing computable (0% coverage by construction); no probe months run.

## 2. Variables (exact source names)

`permno`, `time_avail_m`, `secid`, `prc`, `shrcd` (SignalMasterTable); `vol` (monthlyCRSP); `optvolume_js12`
(OptionMetricsVolume.csv, daily, summed to monthly by secid).

## 3. Formula

```
optvolm[secid, m]  = sum over days in m of optvolume_js12
OptionVolume1      = optvolume_js12 / vol                      # option-to-stock volume ratio, month m
OptionVolume1      = NaN if lag1(optvolume_js12) or lag1(vol) is NaN
tempMean           = mean of OptionVolume1 lags 1..6 (row-wise, skips NaN; NaN only if all six are NaN)
OptionVolume2      = OptionVolume1 / tempMean                  # abnormal option volume
```

## 4. Timing / lag

Monthly, current-month volumes divided by the prior-6-month mean; no annual lag. The original paper is weekly
deciles (longs 9+10, shorts 1+2); OSAP aggregates to months. Not reproducible here in any case.

## 5. Filters

SignalDoc Filter: `abs(prc) > 1, shrcd <= 11`. SignalMasterTable also keeps shrcd 10-12 and exchcd 1-3.

## 6. Predicted sign

SignalDoc `Sign = -1.0` (high abnormal option volume predicts LOW returns -> `ascending=False` had it been built).
`Cat.Economic` = volume; `Cat.Data` = Options; Predictability in OP `2_likely`, quality `2_fair`; LS quantile 0.2,
EW, sample 1996-2010.

## 7. The mass-point question

Moot (no data). For reference, a firm with a stable ratio gives OptionVolume2 ~ 1; a firm with no option volume in
a month yields NaN (division by a missing/zero-volume numerator is NaN, not 0), so there is no zero cluster.

## 8. History needed

Seven months of OptionMetrics volume (1 + 6 lags). OptionMetrics starts 1996; irrelevant because the data are absent.

## 9. OSAP metadata

Acronym OptionVolume2; Acronym2 OptVolGr; Johnson and So, JFE 2012; LongDescription "Based off of OptionVolume1.
OptionVolume2 = OptionVolume1 / average of OptionVolume1 from months t-6 to t-1"; Portfolio Period 1, Start Month 6;
GScholar cites 457; OSAP T-stat 2.45 (port sort CAPM alpha, nonstandard).

## 10. Proposed Sharadar mappings

None. `optvolume_js12` and `secid` have no Sharadar counterpart; not in `field_map_index.yaml` as a key
(options are listed as unavailable class in the project rules). Recommend `infeasible` -> `osap_frontier.yaml`
reason: "option volume (OptionMetrics) not in any of the 13 held Sharadar tables; no OSAP zero-fill".
