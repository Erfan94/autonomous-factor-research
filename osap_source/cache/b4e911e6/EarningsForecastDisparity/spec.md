# EarningsForecastDisparity — long-term vs short-term EPS forecasts (Da and Warachka 2011, JFE, Table 2B)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/EarningsForecastDisparity.py` (cached `predictor.py`, `signaldoc_row.csv`).
Written fresh from the source and `field_map_index.yaml`.

## 1. Data availability — VERDICT: data_unavailable (recommend `infeasible`)

Every input is an IBES analyst-forecast field. IBES / analyst data is not in Sharadar, and OSAP does not zero-fill any of it (missing -> NaN -> dropped).

| OSAP input | origin | Sharadar | OSAP missing-item rule |
|---|---|---|---|
| `meanest` at `fpi == "1"` (mean 1-year-ahead EPS forecast) | IBES_EPS_Unadj | none | NaN -> signal NaN |
| `meanest` at `fpi == "0"` renamed `fgr5yr` (mean long-term growth forecast) | IBES_EPS_Unadj | none | NaN -> signal NaN |
| `fy0a` (IBES-reported actual for the last fiscal year) | IBES_UnadjustedActuals | none | NaN / 0 -> NaN |
| `tickerIBES` link | SignalMasterTable | none | no IBES match -> NaN |

No field_map key exists for any of them (the map holds Compustat and CRSP items only). The numerator `fgr5yr` is a consensus analyst long-term growth
forecast; there is no Sharadar or Compustat analogue. A realised-growth or EPS-change substitute would be a different signal (near-match), not proposed.
Nothing further was measured: the verdict turns on absence of the source, not on coverage.

## 2. Variables (exact source names)
`tickerIBES, fpi, fpedats, statpers, meanest` (IBES_EPS_Unadj); `tickerIBES, time_avail_m, fy0a` (IBES_UnadjustedActuals); `permno, time_avail_m, tickerIBES` (SignalMasterTable).

## 3. Formula in words and key lines
Long-term growth forecast minus 100 times the percent gap between the 1-year-ahead EPS forecast and last year's actual EPS (scaled by |actual|).
```
tempIBESshort = fpi=="1" and fpedats notna and fpedats > statpers + 30 days   # drop stale 1-year forecasts
tempIBESlong  = fpi=="0"  (meanest -> fgr5yr)
tempShort = NaN if fy0a == 0 else 100 * (meanest - fy0a) / abs(fy0a)
EarningsForecastDisparity = fgr5yr - tempShort                                # left joins; rows with NaN dropped
```

## 4. Timing / lag convention
Monthly IBES statistical-period snapshot (`time_avail_m`) joined to SignalMasterTable by IBES ticker and month; no further lag. Not reproducible here (no source).

## 5. Filters
In code: `fpedats` missing or `fpedats <= statpers + 30d` -> short forecast dropped (hence signal NaN); `fy0a == 0` -> NaN. SignalDoc Filter blank.

## 6. Predicted sign
SignalDoc `Sign = -1.0` (high disparity -> low returns); Return 0.48, T-Stat 5.08; Stock Weight EW; LS Quantile 0.2; Portfolio Period 1; Start Month 12; Cat.Form continuous.

## 7. The mass-point question
Not measurable (no source). For the record: a firm with no analyst forecasts produces NaN (not a value); coverage in IBES-based signals is a fraction of the universe by construction.
Ties among scored firms: continuous forecasts, none expected.

## 8. History needed (snapshot starts 1998-01)
Would need IBES history from ~1983 (SampleStart); moot.

## 9. OSAP metadata (SignalDoc)
Acronym EarningsForecastDisparity; Acronym2 LT_ST_EPS; Da and Warachka; 2011; JFE; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 2_fair; Cat.Form continuous;
Cat.Data Analyst; Cat.Economic earnings forecast; SampleStart 1983, End 2006; Key Table "2B Month One"; Test "LS port"; Sign -1.0; Return 0.48; T-Stat 5.08; EW; LS Quantile 0.2.
Definition: "Analyst forecasted 5-year earnings growth (fgr5yr) minus 100 times the difference between mean earnings forecast (meanest) and fiscal year earnings expectations (fy0a) scaled by the absolute value of fy0a. Drop if fpedats is missing or fpedats - statpers < 30".

## 10. Proposed Sharadar mappings
None. All inputs are IBES; recommend `infeasible` (frontier reason: IBES analyst forecasts not in Sharadar; OSAP does not zero-fill them).
