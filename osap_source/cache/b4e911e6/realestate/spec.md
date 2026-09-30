# realestate — Real estate holdings (Tuzel 2010, RFS)

## 1. Data availability — VERDICT: data_unavailable (recommend infeasible)
The numerator and denominator of the primary ratio do not exist in Sharadar, and OSAP does not zero-fill them.
| input | OSAP role | field_map_index | OSAP zero-fill? |
|---|---|---|---|
| fatb (buildings at cost) | re_new numerator | unavailable, no SF1 field | NO (not in CompustatAnnual.py zero_fill_vars) |
| fatl (land at cost) | re_new numerator | unavailable | NO |
| ppegt (gross PP&E) | re_new denominator | unavailable | NO |
| ppenb, ppenls (net buildings / net leases) | fallback numerator | unavailable | NO |
| ppent | fallback denominator + presence gate | mapped -> ppnenet (vendor 0-fill) | no (OSAP leaves NaN) |
| at | count/drop gate | mapped -> assets | - |
| sicCRSP | 2-digit industry | approx -> TICKERS.siccode (current) | - |
zero_fill_vars in upstream_CompustatAnnual.py (nopi dvt ob dm dc aco ap intan ao lco lo rect invt drc spi gdwl che dp act lct tstkp dvpa scstkc sstk mib ivao prstkc prstkcc txditc ivst) contains none of fatb, fatl, ppegt, ppenb, ppenls. The predictor itself has no fillna: a missing term propagates NaN and the row is dropped by `dropna(subset=['realestate'])`. So there is no zero-fill licence. Both branches (re_new and re_old) need unavailable fields; the only held PP&E field is ppnenet (net PP&E total) with no building/land split. SF1 columns checked against data/SNAPSHOT_MANIFEST.yaml: no ppe-gross, buildings, land or lease column. A ppnenet/assets proxy would be a different signal (asset tangibility), not a translation: do not substitute.

## 2. Variables (exact source names)
m_aCompustat: ppenb, ppenls, fatb, fatl, ppegt, ppent, at; SignalMasterTable: sicCRSP.

## 3. Formula
Per firm-month (annual Compustat, available datadate+6 months, held 12 monthly rows):
```
sic2D   = first two chars of str(sicCRSP)
tempN   = count(at) by (sic2D, time_avail_m); keep tempN >= 5
drop at missing; keep rows with ppent OR ppegt non-missing
re_old  = (ppenb + ppenls) / ppent
re_new  = (fatb + fatl) / ppegt
re      = re_new, else re_old where re_new is NaN; +-inf -> NaN
realestate = re - mean(re by sic2D, time_avail_m)
```
Industry-demeaned share of gross PP&E that is buildings+land.

## 4. Timing
OSAP: annual item, datadate + 6 months, forward-filled 12 months. ART-as-of-filing would use the filing date; no flow items (all stocks), so no TTM smear. Moot here (unavailable).

## 5. Filters
Industry cell >= 5 firms per (sic2 , month); at non-missing; ppent or ppegt non-missing. SignalDoc Filter: none.

## 6. Predicted sign
SignalDoc Sign = +1 (high industry-adjusted real-estate share earns higher returns). Tuzel (2010), sample 1971-2005, t=1.8 VW / 1.28 EW; SignalDoc quality 2_likely; port sort 0.2 quantile, VW, annual, start month 6.

## 7. Mass-point question
Not measured (unavailable). For reference: a firm with no buildings/land has re = 0 (fatb/fatl reported 0) and gets the negative of the industry mean, not a common value; firms with missing ppegt fall back to ppenb/ppenls. Under a hypothetical proxy, ppnenet == 0 is a vendor zero-fill (exact zero 5.65% of ART rows overall, 11.8% in 2021-26 per field_map_index), a mass point.

## 8. History needed
None beyond one annual filing; snapshot 1998-01 would suffice. Moot.

## 9. OSAP metadata
Acronym realestate; Cat.Economic = asset composition; Cat.Data = Accounting; Cat.Form continuous; Sample 1971-2005; pinned ref b4e911e6; upstream: osap_source/cache/b4e911e6/realestate/upstream_CompustatAnnual.py.

## 10. Proposed Sharadar mappings
None valid. fatb, fatl, ppegt, ppenb, ppenls: not in map and not in SF1. ppent -> ppnenet (mapped), at -> assets (mapped), sic2D -> TICKERS.siccode via harness.industry.sic_group (known_trap current_sic_signal_values, declared deviation, look-ahead to state) only if a real-estate field existed.
Recommendation: infeasible (data_unavailable: fatb, fatl, ppegt, ppenb, ppenls; OSAP does not zero-fill). Frontier reason wording: "needs Compustat fatb/fatl/ppegt (and ppenb/ppenls fallback); no SF1 field; not zero-filled by OSAP".
