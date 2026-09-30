# CitationsRD — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: INFEASIBLE (recommend `infeasible`)
Checked against `osap_source/field_map_index.yaml`.

| OSAP var | source | Sharadar | status | role |
|---|---|---|---|---|
| ncitscale | PatentDataProcessed (NBER Bessen patent files, gvkey-year) | none: no patent or citation table among the 13 held | **unavailable** | NUMERATOR (5-yr sum) |
| xrd | compustat.xrd | SF1.rnd | mapped, verified 2026-09-30 | denominator (5-yr sum of lag-24 series) |
| ceq | compustat.ceq | SF1.equity | approx (includes preferred) | filter ceq >= 0 |
| sicCRSP | crsp.siccd | TICKERS.siccode (current) | approx | drop SIC 6000-6999 |
| mve_c, exchcd | SignalMasterTable | DAILY.marketcap / TICKERS.exchange (current) | mapped / approx | NYSE-median size split |

- The numerator is a third-party patent dataset, not a Compustat item. The rule
  "OSAP zero-fills it, so drop the term and call it approx" does NOT rescue this:
  OSAP's `fillna(0)` (predictor.py `ncitscale_lag6.fillna(0)`; PatentCitations.py
  `df_patents['ncitscale'].fillna(0.0)`) fills GAPS in an observed dataset.
  Here the whole dataset is absent; dropping the term makes
  `sum_ncit = 0` for every firm, so `tempCitationsRD = 0/sum_xrd = 0` for all
  names with xrd > 0. The terciles collapse to one value and the 0/1 signal is
  undefined. There is no signal left to rank.
- Even in OSAP the patent panel ends at 2006 (NBER `cite76_06`, `pat76_06_assg`,
  `Creates balanced panel ... 1976-2006`): after the last citation year the
  numerator is a filled 0. The decision window 1999-2021 is mostly past the data.
- Verdict: **infeasible** (patents/citations; no Sharadar table, no proxy). Never
  substitute patent counts from anywhere else, R&D intensity or any near-match.

## 2. Variables by exact source name (predictor.py)
`SignalMasterTable`: permno, gvkey, time_avail_m, mve_c, sicCRSP, exchcd.
`m_aCompustat`: permno, time_avail_m, xrd, sich, datadate, ceq.
`PatentDataProcessed`: gvkey, year, ncitscale (scaled citations: each citation
to a firm's patents, divided by the year/subcategory mean, summed per gvkey-year;
citations counted only within 5 years of the cited patent's grant year).

## 3. Formula
Annual-style signal formed in JUNE only, then carried 12 months:

    ncitscale = lag6(ncitscale).fillna(0)        # calendar lag 6 months
    xrd_lag   = lag24(xrd).fillna(0)             # calendar lag 24 months
    sum_xrd   = asrol(xrd_lag, 48 months, sum, min 1)   # in June rows only
    sum_ncit  = asrol(ncitscale, 48 months, sum, min 1)
    temp      = sum_ncit / sum_xrd   if sum_xrd > 0 else NaN
    drop first 2 rows per gvkey; drop SIC 6000-6999; drop ceq < 0
    sizecat   = 1 if mve_c <= NYSE median (per June) else 2
    maincat   = fastxtile(temp, by month, n=3)
    CitationsRD = 1 if size 1 & tercile 3 ; 0 if size 1 & tercile 1 ; else NaN
    expand each June row to 12 months (offsets 0..11)

## 4. Timing / lag convention
June formation; xrd lagged 24 months and summed over 48 months (t-3..t-7 window in
the paper), citations lagged 6 months and summed over 48 months. Held through the
next May. The Sharadar ART-as-of-filing change would be moot: no Sharadar
substitute exists for the numerator. rnd is a flow (ART = TTM sum; ARY fiscal-year
flow), so a 48-month sum would use ARY or four ART reads; irrelevant here.

## 5. Filters
Drop pre-1975, <= 2 years in Compustat, financials (SIC 6000s), ceq < 0, sum_xrd
= 0; small-size only (NYSE median), extreme terciles only. SignalDoc Filter blank.

## 6. Predicted sign (SignalDoc)
`Sign = +1.0` (high citations per R&D dollar predicts higher returns). Cat.Form
discrete, Cat.Data Other, Cat.Economic profitability alt; VW, Portfolio Period 12,
Start Month 6; Signal Rep Quality 2_fair.

## 7. The mass-point question
The output is 0/1/NaN by construction: only small firms in tercile 1 or 3 of a
June cross-section receive a value, so roughly (0.5 x 2/3) = 33% of the June
universe is non-null, and about half of those are in each class. A do-nothing firm
(no patents) has sum_ncit = 0, so it is in tercile 1 (value 0) whenever sum_xrd >
0: patent-less R&D spenders are the "short" leg, not noise. In a full-history
Sharadar build, every R&D spender would be in tercile 1 because no citations exist.
Ties: binary, rank by average.

## 8. History needed
Would need 7 years of R&D and citations; snapshot starts 1998-01 (SF1 from 1997Q4),
so the first formable June would be 2005 even with data. Moot.

## 9. OSAP metadata
CitationsRD; Hirschleifer, Hsu and Li (2013, JFE), "Citations to RD expenses";
Key Table 9A EMI2; FF3-style long-short t = 2.6 (return 0.26); sample 1982-2008;
Signal Rep Quality 2_fair; Predictability 1_clear; GScholarCites202509 = 1239.
Source `Signals/pyCode/Predictors/CitationsRD.py` (confirmed in tree.txt; upstream
cached as `upstream_PatentCitations.py`).

## 10. Proposed Sharadar mappings
None for ncitscale (no table, no proxy). The other inputs map (rnd, equity,
siccode) but cannot rescue the signal. Not in field_map_index: ncitscale/patent
data (unavailable, no entry needed). Recommendation: `infeasible`.
