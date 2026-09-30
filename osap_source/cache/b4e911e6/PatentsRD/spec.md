# PatentsRD — Patents to R&D expenses (Hirshleifer, Hsu, Li 2013, JFE, Table 9A EMI1)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/PatentsRD.py` (cached `predictor.py`; upstream `upstream_PatentCitations.py`, `upstream_stata_fastxtile.py`). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`. No measurement needed: the verdict turns on field availability.

**VERDICT: data_unavailable (infeasible).** The numerator `npat` (patents granted per year, `PatentDataProcessed` from the patent database) is not published by Sharadar (`field_map_index.yaml`: no patent field; "no patents" is on the unavailable list). The zero-fill rule does NOT rescue it: `predictor.py` does `fillna(0)` on `npat`, but that fills firm-years missing INSIDE the patent panel (the left merge on gvkey/year), not the absence of the panel itself. Dropping the panel makes `npat = 0` for every firm, so `tempPatentsRD = 0/RDcap = 0` for all names with `RDcap > 0` and the signal is one constant: there is no cross-section to rank. Same ruling as the CitationsRD frontier row (numerator is a patent panel; OSAP's fillna(0) fills gaps in that panel, so dropping it makes the signal a constant).
The published predictor is also a binary flag on small firms only (below), which would fail the tie cliff even with data; that is secondary.

## 1. Data availability
| OSAP input | key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `npat` | patent panel (gvkey-year) | none | unavailable | `fillna(0)` on the merge gaps (and `temp.fillna(0)` after the 6-month shift) |
| `xrd` | compustat.xrd | `SF1.rnd` (ART, separate from sgna) | mapped | `fillna(0)` in the predictor (missing R&D -> 0) |
| `sich` | compustat.sich | `TICKERS.siccode` (current) | approx | loaded; the filter uses `sicCRSP` 6000-6999 |
| `ceq` | compustat.ceq | `equity` | approx | `ceq < 0` dropped; missing kept |
| `mve_c`, `exchcd` | SignalMasterTable | `mkt_cap_usd` / exchange (NYSE median cut) | approx | NYSE median breakpoint |
Unavailable: patents (decisive). Others buildable.

## 2. Variables
`permno, gvkey, time_avail_m, mve_c, sicCRSP, exchcd`; `xrd, sich, datadate, ceq` (m_aCompustat); `npat, year` (PatentDataProcessed).

## 3. Formula in words and key lines
Patents in a year divided by depreciated R&D capital: five lagged annual R&D figures (t-2 .. t-6) weighted 1, 0.8, 0.6, 0.4, 0.2. Formed in June only; firms double-sorted on NYSE-median size and terciles of the ratio; the signal is 1 for small / highest tercile, 0 for small / lowest tercile, missing elsewhere; held 12 months.
```
RDcap = xrd_{t-2} + .8 xrd_{t-3} + .6 xrd_{t-4} + .4 xrd_{t-5} + .2 xrd_{t-6}    # June observations, annual steps
tempPatentsRD = npat / RDcap  if RDcap > 0 else NaN
PatentsRD = 1 if sizecat == 1 and maincat == 3 ; 0 if sizecat == 1 and maincat == 1 ; else NaN
```

## 4. Timing / lag convention
June formation; `npat` shifted 6 months then filled; R&D at annual steps via June rows. A flow ratio over a flow-capital: no TTM smear issue, but the June-only / 12-month hold and the 6-year R&D history are not reproducible under a monthly ART read. Moot.

## 5. Filters
Drop obs before 1975; drop the first two observations per gvkey; SIC 6000-6999 dropped; `ceq < 0` dropped; signal only for small-cap (<= NYSE median) names.

## 6. Predicted sign
SignalDoc `Sign = 1.0`; Cat.Economic profitability alt; Cat.Data Other; sample 1982-2008; VW; T-Stat 4.13; Notes: predictability weak in large firms.

## 7. The mass-point question
Without patents: every name scores 0 (100% at one value). With patents (published form): a binary 1/0 over small names in the extreme terciles only; ~two values, a tie share far above the 10% cliff (OScore precedent). Tie handling: none possible.

## 8. History needed (snapshot starts 1998-01)
Six years of R&D before signal: the first full RDcap would be 2004; the patent data itself would also need to reach the window.

## 9. OSAP metadata
PatentsRD; Hirshleifer, Hsu, Li 2013 (JFE); Cat.Signal Predictor; 1_clear / 2_fair; Cat.Form discrete; Acronym2 PatentsRD; Key Table 9A EMI1; Test "LS FF3 style"; LS Quantile 1.0; Portfolio Period 12; Start Month 6.

## 10. Proposed Sharadar mappings with deviations
None. Needed and missing: patent counts (`npat`). Mapped side inputs: xrd -> `rnd`. Fields not in the map: patents (declared unavailable).
Recommendation: `infeasible` (data_unavailable); frontier row with the CitationsRD precedent.
