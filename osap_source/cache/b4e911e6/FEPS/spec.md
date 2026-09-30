# FEPS — analyst earnings-per-share forecast (Cen, Wei and Zhang 2006, Table 2 Ret0:1)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/FEPS.py` (cached `predictor.py`).
DATA_SHA 198b281de1a0.

## 1. Data availability (verdict: DATA_UNAVAILABLE -> infeasible)

| OSAP input | source | Sharadar | status / OSAP missing rule |
|---|---|---|---|
| `meanest` (mean analyst EPS estimate) with `fpi == "1"` (current fiscal-year forecast) | `IBES_EPS_Unadj.parquet` (IBES unadjusted summary file) | NONE: IBES / analyst data is not in Sharadar (ruling) | unavailable; left merge gives NaN and the signal is NaN, NOT zero-filled |
| `tickerIBES` link | `SignalMasterTable` (IBESCRSPLinkingTable) | none | unavailable |

- The whole signal IS the IBES mean estimate (`FEPS = meanest`). No other term exists to substitute; no SF1/SEP/DAILY
  field carries analyst forecasts (SF1 has GAAP `eps`, `epsdil`, `bvps`, `sps` only; `EVENTS`, `SF3*` are filings
  and holdings). A trailing-EPS stand-in would be a different factor (not a forecast) and is refused.
- OSAP does not zero-fill `meanest`; missing means NaN (the merge is left). Missing-item rule -> `infeasible`.
- Nothing measurable on the snapshot: the input does not exist, so no coverage or mass-point figure.

## 2. Variables (exact source names)

`meanest` (IBES unadjusted mean EPS estimate, fpi == "1"), `tickerIBES`, `permno`, `time_avail_m`
(`IBES_EPS_Unadj` statpers month -> time_avail_m).

## 3. Formula

`FEPS = meanest` (the level of the mean unadjusted FY1 forecast in dollars per share), left-merged to the master table on
`tickerIBES, time_avail_m`, no transformation, no scaling by price. Rows with no IBES match are NaN (not dropped
until `save_predictor`).

## 4. Timing / lag convention

Monthly IBES statistical-period observation keyed to `time_avail_m`; no fundamentals, no annual lag. A level in raw
per-share dollars across firms of any size is not scale-free (the signal is a share-price-like magnitude), which is how
OSAP publishes it.

## 5. Filters

SignalDoc `Filter = abs(prc) > 5` (a portfolio-stage filter, not in `predictor.py`); the harness universe uses price >=
$1 and factors may not filter. Coverage would be IBES-covered firms only.

## 6. Predicted sign

SignalDoc `Sign = +1.0` (high FEPS -> high returns). `Stock Weight EW`,
`LS Quantile 0.1`, `Cat.Form continuous`, `Cat.Data Analyst`, `Cat.Economic profitability`.

## 7. The mass-point question

Not measurable (no input). Analyst forecasts are continuous with round-number clustering (quarter-dollar bins);
a high share at 0.00-0.10 is plausible but unmeasured. Moot: verdict infeasible.

## 8. History needed

Not applicable (OSAP sample 1983-2002).

## 9. OSAP metadata

`Cat.Signal Predictor`, `Cat.Form continuous`, `Cat.Data Analyst`, `Cat.Economic profitability`, Cen, Wei and Zhang 2006
(working paper), sample 1983-2002, `Predictability 1_clear`, `Rep Quality 1_good`, t = 2.66 (port sort, Ret0:1),
`Sign +1`, `Portfolio Period 1`, `Start Month 12`.

## 10. Proposed Sharadar mappings and deviations

None. `meanest` / IBES has no Sharadar counterpart and no `field_map` key. Recommendation: frontier as
`data_unavailable` (analyst estimates not in Sharadar; not zero-filled by OSAP).
