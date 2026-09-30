# retConglomerate — Conglomerate return (Cohen and Lou 2012, JFE)

## 1. Data availability — VERDICT: data_unavailable (recommend infeasible)
The signal is built from Compustat business-segment sales by SIC (CompustatSegments: stype OPSEG/BUSSEG, sics1, sales) and a CCM gvkey-permno link table. Sharadar has no segment data.
Held tables (data/SNAPSHOT_MANIFEST.yaml): ACTIONS, DAILY, DESCRIPTIONS, EVENTS, METRICS, SEP, SF1, SF2, SF3, SF3A, SF3B, SP500, TICKERS. SF1 columns (revenue, assets, etc.) are consolidated firm totals only; no segment/geographic/product breakdown, no segment SIC. TICKERS has one current siccode/sicindustry per firm, not a segment list. EVENTS carries event codes only. Checked: no table or column mentions segments.
OSAP zero-fill: the predictor does not fillna or zero-fill; firms without segment rows are dropped by the inner merges (`dropna(subset=['Conglomerate'])`, merge with tempCS). No licence to proceed without segments. Also needs the CCM link (gvkey-permno with link dates): no Sharadar equivalent (TICKERS has permaticker only).

## 2. Variables (exact source names)
CompustatSegments: gvkey, datadate, stype, sics1, sales. a_aCompustat: gvkey, permno, sale (as saleACS), fyear. CCMLinkingTable: gvkey, permno, timeLinkStart_d, timeLinkEnd_d. monthlyCRSP: permno, time_avail_m, ret.

## 3. Formula
```
segments: keep stype in (OPSEG, BUSSEG), sales >= 0 and non-missing
sic2D = first 2 digits of sics1; sum sales by (gvkey, sic2D, datadate)
merge annual sale (saleACS >= 0) on (gvkey, fyear=year(datadate))
tempNInd = number of sic2D rows per (gvkey, datadate)
segment share = sales / saleACS; keep rows with share > 0.8 (note: row-level, not firm-level coverage)
Conglomerate = 0 if tempNInd == 1 else 1 (if share > 0.8)
stand-alone (Conglomerate==0) firms -> permno via CCM (link valid on datadate) -> sic2D, fyear
industry_ret(sic2D, month) = equal-weighted mean CRSP ret of stand-alone firms with fyear == calendar year(month)
conglomerates: for each (permno, sic2D, sales, fyear) merge industry_ret on sic2D, keep fyear == year(month)
tempweight = sales / sum(sales by permno, month)
retConglomerate = sum(weight * industry_ret)   # sales-weighted stand-alone industry return
```
## 4. Timing
The code matches segment rows to returns by fyear == calendar year of the return month, so the segment structure of fiscal year y is paired with months of calendar year y (annual segment data, contemporaneous with the year's returns; the code itself applies no further lag). The signal is the weighted industry return of that month. Annual segment data; no ART/ARQ issue. Moot here.

## 5. Filters
OPSEG/BUSSEG only; sales >= 0; segment share > 0.8 of annual sale; SignalDoc Filter abs(prc)>5 (portfolio stage, not in predictor.py).

## 6. Predicted sign
SignalDoc Sign = +1 (high conglomerate return -> higher next-month return; LS quantile 0.1, EW, monthly, t=5.5 sort; sample 1977-2009, Cat.Economic = lead lag, Cat.Data = Price).

## 7. Mass-point question
Not measured (unavailable). The value is a weighted mean of industry returns, continuous; firms not classified as conglomerates are NaN (not 0), so a do-nothing firm is missing rather than tied. Only firms classified as conglomerates (>1 sic2 segment with a row-level share > 0.8) get a value, so coverage would be well below the whole universe: a coverage-floor (40%) risk in any case (not measured).

## 8. History needed
1 month of returns plus a segment-year; snapshot 1998-01 start would suffice. Moot.

## 9. OSAP metadata
Acronym retConglomerate; Acronym2 RetConglomerate; Cat.Economic = lead lag; Cat.Data = Price; Cat.Form continuous; Sample 1977-2009; pinned ref b4e911e6; upstream: osap_source/cache/b4e911e6/retConglomerate/upstream_CompustatBusinessSegments.py.

## 10. Proposed Sharadar mappings
None. segments (sics1, sales by stype): not in map, not in any held table. CCM link: none. ret -> SEP (mapped, harness returns), sale -> revenue (mapped) would be fine but irrelevant.
Recommendation: infeasible (data_unavailable: Compustat business segments and CCM link; not zero-filled by OSAP). Frontier reason wording: "needs Compustat segment sales by SIC (OPSEG/BUSSEG); no Sharadar table has segments".
