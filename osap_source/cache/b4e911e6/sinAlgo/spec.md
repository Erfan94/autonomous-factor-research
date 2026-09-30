# sinAlgo — Sin stock indicator (Hong and Kacperczyk 2009, Table 4A/4B first row; Acronym2 SinStock)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/sinAlgo.py` (cached `predictor.py`; upstream `CompustatBusinessSegments.py`, `sicff.py` beside it). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`. Measurements: harness universe (`build_universe`), ALL 276 decision months 1999-01..2021-12, recorded snapshot, scratch script (no factor file).

## 1. Data availability verdict: DATA_UNAVAILABLE (recommend infeasible); measured secondary: PREFLIGHT_FAILED (coverage, mass point, names per decile)
| OSAP input | Sharadar | status |
|---|---|---|
| `CompustatSegments` (`sics1`, `naicsh`) | none | UNAVAILABLE (segments). Drives the segment leg, the gaming leg's segment side and the historical backfill |
| `m_aCompustat.naicsh` (firm-level NAICS, gaming codes 7132, 71312, 713210, 71329, 713290, 72112, 721120) | none | `compustat.naicsh` UNAVAILABLE in `field_map_index.yaml` |
| `SignalMasterTable.sicCRSP` | `TICKERS.siccode` | `crsp.siccd` approx: CURRENT classification, not point-in-time (known_trap `current_sic_signal_values`; ~12-14% of names reclassified since 1998) |
| `shrcd > 11` exclusion | TICKERS.category | approx (universe already US common) |
No IBES/options/13F/patents/ratings/pensions/xad/emp/ob/ppegt. The missing inputs are NOT zero-filled by OSAP: `sinSeg*` and `sinStockGaming` are NaN when absent and simply drop out of an OR. That is not a zero-fill of a value, it silently changes who gets a 1. Missing-item rule: infeasible.

## 2. Variables
`segments`: gvkey, sics1, naicsh, datadate. `SignalMasterTable`: permno, gvkey, time_avail_m, sicCRSP, shrcd. `m_aCompustat`: naicsh. `sicff` FF48 mapping (harness.industry.ff48 is the verbatim copy).

## 3. Formula
```
sinStockTobacco = 1 if 2100<=sicCRSP<=2199 (year>=1965)      sinStockBeer = 1 if 2080<=sicCRSP<=2085
sinStockGaming  = 1 if naicsh in {7132,71312,713210,71329,713290,72112,721120}
sinSeg*         = same three tests on Compustat SEGMENT sics1/naicsh, collapsed to gvkey-year (max)
sinAlgo = 1 if sinStockAny | sinSegAny | (first-year segment backfill, year >= 1965) | beer-segment backfill | (gaming backfill pre-1965)
sinAlgo = 0 if FF48 in {2 Food, 3 Soda, 7 Fun, 43 Meals} ("ComparableStock") and sinAlgo is still NaN
sinAlgo = NaN otherwise; NaN if shrcd > 11
```
Three-valued: 1 (sin), 0 (comparison group), NaN (everyone else, i.e. ~95% of a broad universe).

## 4. Timing
Monthly, SignalMasterTable rows; no fundamentals lag beyond m_aCompustat's (for naicsh). The indicator is applied "to the entire history and future of the identified firm" (SignalDoc): the segment flag is back-filled, so it is itself a look-ahead. On Sharadar the SIC leg would be a current code read at every past month (look-ahead by construction, declared under `current_sic_signal_values`). No flow items; no ART/ARQ question.

## 5. Filters
Comparison-group membership (FF48 2,3,7,43) is part of the signal definition; shrcd <= 11. SignalDoc `Filter` blank.

## 6. Predicted sign
SignalDoc Sign = +1 (sin stocks earn more); Return 0.3, T-Stat 2.0, "LS nonstandard"; Predictability 2_likely, Rep Quality 2_fair. Would be `ascending=True`.

## 7. Mass-point question (MEASURED, all 276 months, SIC-only construction)
Only the SIC terms can be built: tobacco SIC 2100-2199 and beer SIC 2080-2085 from `TICKERS.siccode`, comparison group FF48 {2,3,7,43} via `harness.industry.ff48`. The gaming leg (NAICS) and every segment leg are omitted, so the count of 1s below is a LOWER bound.
- Scored names per month (1 or 0): min 90, median 104, max 128, against a universe of 1,739-2,867. Coverage 3.9-6.2% (median 5.4%). The ceiling is the FF48 {2,3,7,43} denominator, not the missing gaming names, so adding them would not lift it.
- Sin = 1: 11-15 names (median 13). Comparison = 0: 76-114 (median 91). Modal value 0, mode share 83.9-90.0% (median 87.3%) of the scored names; distinct values 2; qcut yields 2 bins, not 10.
- A do-nothing firm produces 0. n1 is below 30 in every month (276 of 276), so a D10 of ones has 11-15 names; names per decile is ~9-13 against the bar of 30; coverage 3.9-6.2% against the bar of 40%.
- Sign-contamination: gaming-like SIC (7011 hotels-casinos, 7990, 7993, 7997, 7999) names in the universe number 15-30 per month and all fall in FF48 group 7 or 43, so without the NAICS gaming flag they are scored 0 (comparison) rather than 1 (sin): the opposite class.
- Tie handling: none possible; a binary flag has two values. Same shape as the excluded binary flags DivInit, IndIPO, Spinoff.

## 8. History needed
None for a flag; SEP stub irrelevant. Snapshot coverage from 1998-12 (all 276 months scored, at 3.9-6.2%).

## 9. OSAP metadata
Hong and Kacperczyk (2009), JFE; Cat.Data Other; Cat.Economic other; discrete; sample 1926-2006; Key Table 4A 1965-2006 first row, 4B 1926-2006 first row; EW; Portfolio Period 1; Start Month 6; 3,655 cites. Notes: follows OP, Compustat segment data plus NAICS; sinAlgo = 0 for "comparable stocks" (FF48 2, 3, 7, 43).

## 10. Proposed Sharadar mappings
None recommended. A SIC-only build (`TICKERS.siccode` via `harness.industry.ff48`, current SIC, declared look-ahead) exists but drops the segment and NAICS-gaming terms, mislabels gaming firms as comparison, and fails coverage (<=6.2%), mass point (mode 84-90%, 2 bins) and names-per-decile (~10) in every month. Verdict: infeasible (data_unavailable: segments, naicsh), measured preflight_failed.
