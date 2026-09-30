# sfe — Earnings forecast to price (Elgers, Lo and Pfeiffer 2001, AR)

## 1. Data availability — VERDICT: data_unavailable (recommend infeasible)
The numerator is the IBES median analyst EPS forecast for the next fiscal year, and the coverage split uses IBES numest. Sharadar publishes no analyst estimates.
Held tables (data/SNAPSHOT_MANIFEST.yaml): ACTIONS, DAILY, DESCRIPTIONS, EVENTS, METRICS, SEP, SF1, SF2, SF3, SF3A, SF3B, SP500, TICKERS. SF1 eps / epsdil are REPORTED results, not forecasts; METRICS has dividend yield forward, price, beta and return fields, no EPS estimate (pe1 / ps1 in SF1 are valuation ratios on trailing reported data, not analyst forecasts). No IBES link (tickerIBES) either.
OSAP zero-fill: none. The predictor inner-merges IBES (`smt.merge(ibes, how="inner")`); firms without a forecast are simply absent. No licence to proceed.
Other inputs (would be available): prc -> SEP close; datadate (December FYE only) -> SF1 reportperiod month.

## 2. Variables (exact source names)
IBES_EPS_Unadj (ibes.statsumu_epsus): fpi, statpers, fpedats, time_avail_m, tickerIBES, medest, numest. SignalMasterTable: permno, time_avail_m, tickerIBES, prc. m_aCompustat: permno, time_avail_m, datadate.

## 3. Formula
```
ibes = fpi == "1" (next fiscal year), statpers in March, fpedats > statpers + 90 days
prc_time = ibes.time_avail_m - 3 months  (stock price as of December)
merge SMT (tickerIBES, prc_time) -> prc;  merge m_aCompustat on (permno, time_avail_m) -> datadate
keep datadate month == 12 (December fiscal year ends only)
tempcoverage = qcut(numest, 2) within each month; keep lower half (below-median coverage)
sfe = medest / |prc|
hold each March value for 12 months (month offsets 0..11)
```
March consensus EPS over December price: forecast earnings yield, for low-coverage December-FYE firms.

## 4. Timing
Formed in March, held 12 months (annual rebalance; SignalDoc Portfolio Period 12, Start Month 3). IBES statistical period = monthly; datadate is the Compustat fiscal year end. ART-as-of-filing is irrelevant to the forecast; only the December-FYE test would use it. Moot.

## 5. Filters
December FYE only; fpi=1 with forecast horizon > 90 days; bottom half of numest each month; SignalDoc Filter abs(prc)>1.

## 6. Predicted sign
SignalDoc Sign = +1 (high forecast EP earns higher returns; LS 0.1, EW, annual, t=4.99 size-adjusted; sample 1982-1998; Cat.Economic = valuation, Cat.Data = Analyst; quality 2_fair; SignalDoc note: size adjustment and coverage are extremely important).

## 7. Mass-point question
Not measured (unavailable). medest/prc is continuous; do-nothing firms (no forecast) are absent, not tied. The December-FYE and lower-half-numest restrictions would leave only a minority of the universe scored, formed once a year (not measured).

## 8. History needed
One March forecast; a 12-month hold. Snapshot 1998-01 start would suffice. Moot.

## 9. OSAP metadata
Acronym sfe; Acronym2 EPforecast; Cat.Economic = valuation; Cat.Data = Analyst; Cat.Form continuous; Sample 1982-1998; pinned ref b4e911e6; upstream: osap_source/cache/b4e911e6/sfe/upstream_IBESEPSUnadjusted.py (WRDS ibes.statsumu_epsus).

## 10. Proposed Sharadar mappings
None valid. medest, numest, fpi, fpedats, tickerIBES: not in the map and not in any held table (IBES is on the project infeasible list). Do not substitute trailing eps or pe1. prc -> SEP close (mapped, not split-adjusted issues per close_is_split_adjusted trap).
Recommendation: infeasible (data_unavailable: IBES EPS forecasts; not zero-filled by OSAP). Frontier reason wording: "needs IBES median next-year EPS forecast and analyst count; Sharadar has no estimates".
