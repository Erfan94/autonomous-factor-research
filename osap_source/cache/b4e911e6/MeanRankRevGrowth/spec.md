# MeanRankRevGrowth — Weighted mean of five annual revenue-growth ranks (Lakonishok, Shleifer and Vishny 1994, JF, Table 6 panel 2)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/MeanRankRevGrowth.py` (cached `predictor.py`; upstream `upstream_CompustatAnnual.py`, `upstream_SignalMasterTable.py`). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`. Measured with harness build_universe + MonthContext (market-scope ranks), 216 months 2003-12..2021-11 plus 60 leading months checked.

## 1. Data availability (verdict: APPROX; constructible, first scorable signal 2003-12-31, 216 of 276 decision months score, 213 of them with coverage >= 40%)

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `revt` (annual total revenue, m_aCompustat, available datadate + 6 months, carried 12 months) | `compustat.revt` | SF1 `revenue`, ART (TTM) at each lag month-end | mapped | not zero-filled: revt <= 0 or missing -> growth NaN -> rank NaN |
| `permno, gvkey, time_avail_m` | - | harness ID | - | - |
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt; no price input. Not infeasible, not data_start failure: the history need (72 months of revenue) cuts 60 leading months but leaves 216 scorable; floor `min_months` 120 is met.
- Why APPROX: annual step-function revt replaced by the quarterly-refreshed TTM level; ranks over the market scope with current-era population; no NASDAQ exclusion (SignalDoc portfolio filter, not in predictor.py); thin SF1 at t-60..t-72 early on.

## 2. Variables (exact source names)
`revt, gvkey, permno, time_avail_m`. Derived `temp` (log growth), `tempRank`, `tempRank_lag12 .. _lag60`.

## 3. Formula in words and key lines
Each month, for every firm with revenue > 0 now and 12 months ago, growth = log(revt_t) - log(revt_t-12); firms are ranked that month from HIGHEST growth (rank 1) to lowest. The signal is the 5,4,3,2,1 weighted average of the firm's rank 12, 24, 36, 48 and 60 months ago.
```
temp      = log(revt) - log(revt_lag12)   only if revt > 0 and revt_lag12 > 0 (calendar merge 12 months back)
sort by (time_avail_m, temp DESCENDING) ; tempRank = row number within the month (1 = highest growth), defined only where temp is non-null
tempRank_lag{12,24,36,48,60} = tempRank of the same permno at time_avail_m - 12k (calendar merge)
MeanRankRevGrowth = (5*L12 + 4*L24 + 3*L36 + 2*L48 + 1*L60) / 15      # any missing lag -> NaN, no partial windows
```
Ranks are RAW ordinal numbers 1..N (not percentiles), where N is that month's number of firms with valid growth, over ALL firms in m_aCompustat with a permno (not only the screened universe); ties in `temp` get arbitrary unique numbers (unstable sort).

## 4. Timing / lag convention
OSAP: annual data known datadate + 6 months; revt_t vs revt_t-12 is the growth of one fiscal year, constant within a fiscal year's 12 months and stepping once a year; lags 12..60 are the growth ranks of the past five annual steps. Here: `ctx.market_context().fundamentals_at_month_ends(["revenue"], [12,24,36,48,60,72], scope="market")` (ART as known by `datekey` at each business month-end); growth at month s = log(rev_s / rev_s-12), ranked over market-scope names listed that month; ranks at s = t-12k, k = 1..5. Signal at month-end t, earned t+1.
Flow item, but NO smear: ART at s and at s-12 are two non-overlapping trailing-four-quarter sums, a true year-over-year growth, refreshed every quarter (not an annual step). Default `dimension` ART is proposed; `dimension="ARY"` mimics OSAP's annual cadence (still PIT by `datekey`) and is the faithful alternative; ARQ must NOT be used (a single quarter vs the same quarter a year ago is a different signal and ART/ARQ year differences smear, known trap `art_is_a_sum_for_flows_and_a_level_for_stocks`).

## 5. Filters
Predictor file: none beyond the validity mask (revt > 0 at both dates). SignalDoc Filter `exchcd %in% c(1,2)` ("Exclude NASDAQ stocks") is a portfolio-level filter, NOT in predictor.py, NOT applied inside a factor; the harness universe (NYSE/NASDAQ/NYSEMKT, cap and ADV screens) decides. Stated deviation.

## 6. Predicted sign — READ CAREFULLY
SignalDoc `Sign = +1.0` on the rank NUMBER. Rank 1 = HIGHEST growth (`gsort -temp`), so a HIGH MeanRankRevGrowth = persistently LOW revenue growth (the contrarian value side) and is the LONG leg: `FactorDef(ascending=True)` on the raw mean rank. The SignalDoc wording "rank firms by revenue growth" invites the opposite orientation; follow the code. Cat.Economic sales growth.

## 7. The mass-point question
Do-nothing firm (flat revenue year on year): temp = 0 exactly, a mid-table rank; nothing is zero-filled. The mean of five ordinal ranks takes thousands of distinct values per month. Measured on the harness universe, 216 scorable months (2003-12-31 .. 2021-11-30): modal share of any value mean 0.17%, max 0.32%; distinct values 715 (2003-12) .. 1,529 per month; `qcut(10)` yields 10 bins in every scorable month. Tie handling: none needed.

## 8. History needed (snapshot starts 1998-01)
Revenue observations at t, t-12 ... t-72 (growth at t-60 needs revenue at t-72), i.e. 6 annual-spaced ART readings; `fundamentals_at_month_ends` lags [12,24,36,48,60,72]. SF1 starts 1997Q4 (filed ~1998-03) and ART is thin in 1998Q1-Q3, so the first signal with a filled t-72 reading is 2003-12-31.
Measured universe coverage (all five ranks present): 0% for every signal 1998-12 .. 2003-11 (60 months; probe: 2003-06 0%, 2003-11 0%); 36.0% 2003-12, 36.9% 2004-01, 37.5% 2004-02 (the three months below the 40% bar); 63-65% 2004-03/04; 47.3-53.2% 2004-05 .. 2005-02 (ART at t-72 = 1998-03..1998-11 still thin); 67.2-80.7% from 2005-03 (min 2021-11); 2005-2021 annual means 68.7-77.9%; overall mean 73.8% on the 214 months 2004-02..2021-11; 213 of 216 scorable months >= 40%. Coverage of the single latest growth rank (lag 12) alone: 80.2-94.7%, mean 89.6% (the gap to 74% is the all-five-lags rule). Scored names 721-1,575.
Early-period distortion: the raw rank scale differs by lag in the same month (2003-12: rank at lag 12 runs to 5,185, at lag 60 only to 1,734 because few firms had two readings); the mean rank then overweights the recent lags for that month. Shrinks through 2005 (2004-06: 5,111 vs 2,623; 2005-03: 5,083 vs 5,382).

## 9. OSAP metadata
MeanRankRevGrowth (Acronym2 RevGrowth); Lakonishok, Shleifer and Vishny 1994 JF; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 2_fair; Cat.Form continuous; Cat.Data Accounting; Cat.Economic sales growth;
Sample 1968-1990; Key Table "6 panel 2"; Test "LS port"; Evidence "t=4.5 in double sort"; Sign +1.0; Return and T-Stat blank; Stock Weight EW; LS Quantile 0.2; Portfolio Period 12.0; Start Month 6.0; Filter `exchcd%in%c(1,2)`; GScholar cites 7664.
Notes: "Lots of supporting results, but not exactly what we do. Tab 6 panel 2 finds t=4.5 using 3x3 sort with CF and LS corners." Definition: weighted mean (5,4,3,2,1)/15 of the growth ranks at t-1..t-5 years, excluding NASDAQ stocks.

## 10. Proposed Sharadar mappings with deviations
```
f = ctx.market_context().fundamentals_at_month_ends(["revenue"], [12,24,36,48,60,72], scope="market")   # ART; dimension="ARY" optional
for k in 1..5: g_k = log(rev[12k]) - log(rev[12k+12]) where both > 0 ; R_k = g_k.rank(ascending=False, method="first") over market names that month ; reindex to ctx.ids
score = (5 R_1 + 4 R_2 + 3 R_3 + 2 R_4 + R_5) / 15   (all five present) ; ascending=True ; lookback_months=72 ; no SEP input, no history gate
```
Deviations: (a) ART quarterly-refreshed TTM revenue vs OSAP's annual record stepping once a year (ARY closer); (b) `revenue` (revt) is raw USD: log differences are currency-blind within one firm (no cross-firm sum), no fxusd needed; (c) ranks over the market scope (every listed common stock that traded that month, `market_constituent_ids`) instead of all m_aCompustat permnos: a different N per month and no delisted-before-linking firms; (d) raw ordinal ranks as OSAP, with `method="first"` (OSAP's tie order is arbitrary too); (e) no NASDAQ exclusion (SignalDoc filter); (f) 60 leading null months and 3 months under 40% coverage; (g) a growth rank uses the firm's revenue at the lag month-end as known then by `datekey` (restatements after that date are not seen); OSAP uses the as-restated-at-download annual figures; (h) the harness ranks the score within sector afterwards (D3).
Fields not in the map: none (`revenue` mapped, verified 2026-09-30).
