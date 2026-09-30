# ForecastDispersion — EPS forecast dispersion (Diether, Malloy and Scherbina 2002, Table 2)

OSAP ref b4e911e69678a7424f318617a61d813f54183123 (cache b4e911e6); source `Predictors/ForecastDispersion.py`
(cached `predictor.py`, `signaldoc_row.csv`, `upstream_IBESEPSUnadjusted.py` = the IBES download it reads).
DATA_SHA 198b281de1a0. SignalDoc row (Cat.Signal == Predictor): Cat.Data = Analyst, Cat.Economic = volatility.

## 1. Data availability (verdict: DATA_UNAVAILABLE — recommend `infeasible`)

The only signal inputs are IBES summary statistics (`stdev`, `meanest`). The snapshot holds 13 tables
(SF1, SEP, DAILY, ACTIONS, SF2, SF3/SF3A/SF3B, EVENTS, METRICS, TICKERS, DESCRIPTIONS, SP500); none carries
analyst forecasts (column scan of SF1, METRICS, EVENTS, SF2, SF3, DESCRIPTIONS, ACTIONS for est/forecast/
analyst/disp names finds only SF1 `eps`, `epsdil`, `epsusd`, which are REPORTED EPS). `field_map_index.yaml` has
no `ibes.*` key. No zero-fill exists in the script (`stdev / abs(meanest)` of a left-joined, often missing
pair), so OSAP does not zero-fill the missing item: infeasible. Nothing to measure.

| input (OSAP) | field_map key | Sharadar | status | note |
|---|---|---|---|---|
| `stdev` (std dev of analyst FY1 EPS forecasts, IBES `statsumu_epsus`) | none | none | unavailable | analyst data, not published |
| `meanest` (mean FY1 EPS forecast) | none | none | unavailable | same |
| `fpi`, `fpedats` (forecast period / end date) | none | none | unavailable | filter fields, same table |
| `tickerIBES` (IBES-CRSP link, `IBESCRSPLink.py`) | none | none | unavailable | WRDS link table; Sharadar has no IBES ticker |
| `permno`, `time_avail_m` | `crsp.smt_row` | SEP presence | mapped | panel rows only |

- Not rescuable: realised-EPS dispersion over time, or the cross-sectional spread of SF1 `eps`, is a different
  signal (earnings volatility), not forecast disagreement; do NOT substitute under this name.
- **Recommendation: `infeasible`** (class `data_unavailable`). Reason: analyst EPS forecast dispersion
  (IBES) is not in the Sharadar snapshot; no OSAP zero-fill. Do not translate, do not preflight.

## 2. Variables (exact source names)

`permno`, `time_avail_m`, `tickerIBES` (SignalMasterTable); `fpi`, `fpedats`, `stdev`, `meanest`
(`IBES_EPS_Unadj.parquet`, built by `IBESEPSUnadjusted.py` from IBES unadjusted summary, `measure = EPS`).

## 3. Formula

```
ibes = IBES_EPS_Unadj[fpi == "1"  &  fpedats.notna()]
df = SignalMasterTable[permno, time_avail_m, tickerIBES].merge(ibes[tickerIBES, time_avail_m, stdev, meanest], how="left")
ForecastDispersion = stdev / abs(meanest)
```
Raw ratio (forecast standard deviation scaled by absolute mean forecast); no log, no winsorising.
`abs(meanest)` blows up as the consensus approaches zero (near-zero-EPS firms give very large values).
Upstream keeps the last statistical period (`statpers`) per ticker-fpi-month and drops rows with missing `meanest`.

## 4. Timing / lag

Month `time_avail_m` = month of IBES `statpers`; stamped month m, portfolio earns m+1 (no extra lag). The
IBES rows are unadjusted; no split adjustment step in this script. Not applicable: SF1 ART/ARQ issues.

## 5. Filters

Code: `fpi == "1"` (1-year-ahead) and non-null `fpedats` only. SignalDoc's Detailed Definition additionally says
"fpedats > statpers + 30" (forecast period ends more than 30 days after the statistics date); that condition is
NOT in `ForecastDispersion.py` and not in the cached upstream download, so treat it as documentation only.

## 6. Predicted sign

SignalDoc `Sign = -1.0` (higher dispersion, lower return). Port sort, EW, LS quantile 0.2, Portfolio Period 1,
Start Month 6; sample 1976-2000; t = 2.88 in port sort; Predictability in OP 1_clear, Signal Rep Quality 1_good.

## 7. Mass-point question

Moot for this snapshot. For reference: `stdev` is 0 when all analysts agree; it is presumably missing when
numest = 1 (not checkable here), so a do-nothing firm is NaN (not scored), not 0. Exact zeros (unanimous analysts) would be the only tie block; IBES coverage of a small-cap-inclusive
universe is well under 100% (a dispersion needs several analysts), so the 40% coverage floor could also bind.
Both are conjecture: no IBES data is held to measure.

## 8. History needed

Sample 1976-2000. Nothing in the snapshot (1998-01 start) stands in for any month.

## 9. OSAP metadata

Acronym ForecastDispersion (Acronym2 EPSDisp); Cat.Signal Predictor; Diether, Malloy and Scherbina, JF 2002;
Cat.Form continuous; Cat.Data Analyst; Cat.Economic volatility; Key Table in OP 2; Test port sort; sample
1976-2000; GScholar cites (2025-09) 2775. Sibling reading the same IBES unadjusted file: AnalystRevision.

## 10. Proposed Sharadar mappings / deviations

None. Not in field_map and would need new keys if IBES were ever supplied: `ibes.stdev`, `ibes.meanest`,
`ibes.fpi`, `ibes.fpedats`, IBES-ticker to permaticker crosswalk.
