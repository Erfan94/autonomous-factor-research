# PS — Piotroski F-score (Piotroski 2000, Table 3A), restricted to the highest book-to-market quintile

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/PS.py` (cached `predictor.py`; upstream `upstream_CompustatAnnual.py`, `upstream_SignalMasterTable.py`). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`; measurements are scratch (harness universe, recorded snapshot, no factor file).

**VERDICT: preflight_failed** (every input maps, approx; the signal fails the mass-point cliff and the coverage bar by construction, and no substitution rescues it).
Measured on all 276 decision months (signals 1998-12-31 .. 2021-11-30; 264 of them from 1999-12-31 with the first three ART filings complete, identical conclusions):
- OSAP's own sample (F-score only in the top BM quintile of ALL listed common stocks, cut read on `market_context()`): 6-9 distinct values, modal share 20.0-40.7% (median 26.8%), >= 10% in 276/276 months, scored 29-119 names (median 76) = 1.4-6.1% of the universe (median 3.8%), coverage >= 40% in 0/276.
- Top quintile taken inside the harness universe instead: 7-10 distinct, modal 20.7-35.9% (median 26.8%), >= 10% in 276/276, coverage 5.6-15.2% (median 10.1%), 0/276 months >= 40%.
- NO BM restriction at all (unrestricted 0..9 F-score, classified balance sheets): 8-10 distinct, modal 23.2-31.7% (median 27.0%), >= 10% in 276/276; coverage 40.9-82.5% (median 78.4%). So dropping the BM filter passes coverage but never the tie cliff, and would be a different signal (the published test is the high-BM subset); not substituted.
- Pooled F-score histogram in the OSAP sample (264 months): 1: 0.8%, 2: 4.2%, 3: 12.7%, 4: 19.5%, 5: 24.1%, 6: 22.4%, 7: 12.3%, 8: 3.6%, 9: 0.3%; value 0 absent. `qcut` cannot give 10 bins from <= 10 integers.
Precedent: MS and NumEarnIncrease (small-integer scores) were excluded as mass points.

## 1. Data availability (every input, from `field_map_index.yaml`)
| OSAP input | key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `fopt` (filled by `oancf`) | compustat.fopt | `ncfo` (after working capital; concept differs) | approx | `fopt.fillna(oancf)` only; missing -> PS NaN |
| `oancf` | compustat.oancf | `ncfo` | mapped | no fill |
| `ib` | compustat.ib | `netinc + netincdis` (PLUS: sign trap) | approx | missing -> PS NaN |
| `at` | compustat.at | `assets` | mapped | missing -> PS NaN |
| `dltt` | compustat.dltt | `debtnc` (ASC 842 leases included from FY2019; 19% null = unclassified) | approx | NOT zero-filled -> PS NaN |
| `act`, `lct` | compustat.act/lct | `assetsc`, `liabilitiesc` (~19% null, unclassified) | mapped | act and lct ARE zero-filled upstream (`zero_fill_vars`) |
| `txt`, `xint`, `sale` | compustat.* | `taxexp`, `intexp`, `revenue` | mapped | `sale` missing -> NaN; txt/xint missing -> tempebit NaN |
| `shrout` (CRSP) | crsp.shrout | `SF1.sharesbas` (split-restated both ends) | approx | missing -> PS NaN |
| `ceq`, `mve_permco` | compustat.ceq, crsp.mve_permco | `equity`; `DAILY.marketcap*1e6` (company-level) at t | approx | `ceq <= 0` -> BM NaN |
Unavailable inputs (IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob, ppegt): none. Not infeasible on data.
Null-share on the universe (264 months): act, lct, dltt each ~19% (median 18.9%); `debtnc` null while `debtc` present <= 0.3%. Zero-fill: unclassified balance sheets are NOT zero-filled here, so a null act or lct is NaN, whereas OSAP's act and lct are 0 (act/lct = 0/0 -> NaN -> counted as "improved", see 3). With OSAP's own 8-field gate 76.9-82.6% of the universe has data (median 78.4%) from 1999-12; classified gate identical to 3 decimals inside the BM sample.

## 2. Variables
`permno, time_avail_m, fopt, oancf, ib, at, dltt, act, lct, txt, xint, sale, ceq` (m_aCompustat, annual, available datadate + 6 months); `mve_permco` (SignalMasterTable); `shrout` (monthlyCRSP); 12-month lags of ib, at, dltt, act, lct, sale, shrout via `stata_multi_lag` after `fill_date_gaps`.

## 3. Formula in words and key lines
Nine 0/1 tests summed (0..9): positive ib; positive cash flow; ROA (ib/at) up vs a year ago; cash flow > ib; dltt/at down; current ratio act/lct up; gross-margin test; asset turnover sale/at up; shares not up. Missing if any of fopt, ib, at, dltt, sale, act, tempebit, shrout is missing. Kept only when `BM = log(ceq/mve_permco)` is in quintile 5 of that month's cross-section (`qcut` over every stock in the merged file with ceq > 0: all exchanges, financials included).
```
handle_stata_edges: +-inf -> NaN; NaN -> +inf     # Stata: missing counts as larger than any number
p3,p6,p7,p8 = metric > 0 ; p5 = metric < 0 ; p9 = (l12_shrout - shrout) >= 0
p7 metric = tempebit/sale - tempebit/l12_sale     # tempebit (= ib+txt+xint) is NOT lagged: sign of p7 = (tempebit>0 and sale fell) or (tempebit<0 and sale rose)
```
Quirks to carry: (a) missing year-ago values (NaN -> +inf) give p3, p6, p7, p8, p9 a free point (p5 no); measured 3.1-4.9% (IQR) of the classified gate lack some lag, median 3.8%, 43.7% in the first months; (b) `fopt.fillna(oancf)`; (c) p7 is an artefact of the un-lagged numerator; (d) act/lct zero-fill makes p6 a free point for unclassified names in OSAP, NaN here.

## 4. Timing / lag convention
OSAP: annual values at datadate + 6 months, held 12 months; BM uses `mve_permco` at t (un-lagged). Sharadar: ART as of filing, year-ago by `fundamentals_yoy` (report-period aligned). ART vs ART four quarters earlier is a clean annual difference of two disjoint TTM windows, so ib/at, sale/at, tempebit/sale do not smear and no `dimension=ARQ` is needed; `assets`, `assetsc`, `liabilitiesc`, `debtnc`, `sharesbas` are latest-quarter levels. The score changes quarterly (vs annually in OSAP). ASC 842 break: `debtnc` step in FY2019-20 for lessees corrupts p5 (leverage "down") in those filings.

## 5. Filters
In `predictor.py`: the BM top-quintile gate (above). SignalDoc Filter empty. Not SIC-filtered (financials are in OSAP's sample; Sharadar leaves them null on act/lct/debtnc, which is why financial high-BM names drop: the classified gate removes ~half of the universe's top BM quintile, 187 of 364 names median).

## 6. Predicted sign
SignalDoc `Sign = 1.0` (high F-score -> high returns); `ascending=True` if ever translated. SignalDoc: Cat.Economic composite accounting, sample 1976-1996, LS Quantile 0.1, Portfolio Period 1, Start Month 12, Stock Weight VW.

## 7. The mass-point question
A do-nothing firm has no meaning for a count; the mass is structural: an integer 0..9 with mode at 5 or 6 (modal share 20-41% in the BM sample). Ties are the signal, not a rare event: modal share >= 10% in 276/276 months (above), qcut bins < 10. There is no tie rule (remove / null / floor) that leaves ten deciles; the preflight hard-fail fires in every month.

## 8. History needed (snapshot starts 1998-01)
One year-ago filing (ART report-period aligned): first scorable signal is 1999-12-31 at full coverage; ART is thin before 1999-03 (51-57% of the universe has any ncfo). Not binding relative to the failure above.

## 9. OSAP metadata
PS; Piotroski 2000 (JAR); Cat.Signal Predictor; predictability 1_clear, rep quality 2_fair; Cat.Form continuous; Cat.Data Accounting; Acronym2 Pscore; Key Table 3A; Test "port sort"; T-Stat 5.594 (nonstandard data lag). Notes: VW, portfolio period 1 to approximate OSAP's compounding and 4-month lag.

## 10. Proposed Sharadar mappings with deviations
Not proposed for translation. Were it built: fopt -> `ncfo` (concept: after working capital; sign disagrees with a funds-from-operations proxy on 14.4% of rows), dltt -> `debtnc` gated on `debtc.notna()` (ASC 842), shrout -> `sharesbas` (p9 needs a year-ago count on the same split basis: both restated), ib -> `netinc + netincdis`, BM quintile on `ctx.market_context()` (a cross-sectional cut inside a factor is decile maths: a harness matter). Fields not in the map: none.
Recommendation: `preflight_failed` (mass point + coverage by construction), class as MS / NumEarnIncrease.
