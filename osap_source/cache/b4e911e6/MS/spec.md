# MS — Mohanram G-score: 0-8 count of eight indicators on LOW book-to-market firms (Mohanram 2005, RAS, Table 4A)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/MS.py` (cached `predictor.py`; upstream `upstream_CompustatAnnual.py`, `upstream_CompustatQuarterly.py`, `upstream_SignalMasterTable.py`, `upstream_asrol.py`, `upstream_stata_replication.py`). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`. Measured with a scratch replication on the frozen snapshot (market-scope fundamentals, harness universe), 269 of 276 decision months (the 7 month-ends 1999-05-31, 2002-03-29, 2004-05-31, 2010-05-31, 2013-03-29, 2018-03-30, 2021-05-31 have no DAILY row on the business month-end date, a harness-calendar miss in the scratch lookup, not a data gap).

## 1. Data availability (verdict: PREFLIGHT_FAILED by construction. Inputs are APPROX-constructible, but the score cannot pass the screen's own gates)

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `ceq`, `mve_permco` (BM sample) | `compustat.ceq`, `crsp.mve_permco` | SF1 `equity` ART; DAILY `marketcap` (x 1e6) | approx | rows with ceq <= 0 or mve <= 0 dropped |
| `niq`, `atq`, `saleq` (quarterly) | `compustat.niq/atq/saleq` | SF1 `netinc`, `assets`, `revenue` ARQ | mapped | NaN propagates; Stata `missing = +inf` in the indicator tests (section 3) |
| `oancfy`, `capxy` (YTD -> quarterly by differencing) | `compustat.oancfy`, `compustat.capxy` | SF1 `ncfo`, `capex` ART/ARQ (no YTD needed) | approx | capex sign: Sharadar `capex` is an OUTFLOW (negative); negate |
| `xrdq` | `compustat.xrdq` | SF1 `rnd` (ART/ARQ) | mapped | OSAP `xrdq.fill_null(0)`; Sharadar's own zero-fill matches (63% exact zero) |
| `xad` (annual advertising) | `compustat.xad` | NONE (no SF1 field) | unavailable | OSAP `xad.fill_null(0.0)`: zero-filled by OSAP itself, so approx, not infeasible |
| `fopt`, `wcapch` | `compustat.fopt` (approx, ncfo), `compustat.wcapch` (unavailable) | - | - | used only when `datadate.year <= 1988`: never binds (snapshot 1998+) |
| `sicCRSP` -> sic2D | `crsp.siccd` | TICKERS `siccode` (CURRENT, `current_sic_signal_values`) via `harness.industry.sic_group` | approx | - |
| `ib, dp, at, ni, revt` | - | loaded, NOT used by the pinned code | - | - |
- No IBES/options/13F/patents/segments/ratings/pensions/emp/ob/ppegt. xad absent for EVERY firm: `xadint` is identically 0, its industry median is 0, `m8 = xadint > median` is dead; it adds no information (in my replication the few m8 = 1 cases, 2-65 names per month, are the Stata missing-is-infinite quirk on a null lagged `atq`, not advertising). The score is therefore 0-7 before bucketing instead of 0-8.
- Two independent, measured failures of the screen's own gates (each sufficient):
  (1) DISCRETE SCORE, 6 values: MS takes the values 1..6 (tempMS 6-8 -> 6; 0-1 -> 1). 6 distinct values in ALL 269 months; modal share of the scored cross-section 20.8%-52.9% (mean 25.0%, min 2013-11-29, max 1998-12-31), at or above the 10% cliff in all 269 months; `qcut(10)` cannot return 10 bins from 6 values. No tie handling rescues a six-valued score.
  (2) COVERAGE: OSAP scores only the lowest BM quintile (of all firms with ceq > 0, mve > 0), with >= 3 firms per sic2D in that quintile, so the universe coverage is structurally ~20-35%: 269 months, mean 25.3%, min 13.4% (2021-04-30), max 35.6% (2000-12-29); below the 40% Stage 1 floor in all 269 months. Scored names 297-948 per month (mean 501) of 1,739-2,867.

## 2. Variables (exact source names)
Annual: `at, ceq, ni, oancf, fopt, wcapch, ib, dp, xrd, capx, xad, revt, datadate`; SMT: `mve_permco, sicCRSP`; quarterly: `niq, atq, saleq, oancfy, capxy, xrdq, fqtr, datafqtr`. Derived `BM, sic2D, niqsum, oancfqsum, xrdqsum, capxqsum, atdenom, atdenom2, roa, cfroa, roaq, sg, niVol, revVol, xrdint, capxint, xadint, md_*, m1..m8, tempMS, MS`.

## 3. Formula in words and key lines
Sample: firms with ceq > 0 in the LOWEST quintile of log(ceq/mve_permco) each month (all firms, not the screened universe), then only sic2D-months with >= 3 such firms. Eight 0/1 indicators vs the sic2D MEDIAN of that sample-month, summed.
```
niqsum, xrdqsum, oancfqsum, capxqsum = 4 x mean of the last 12 monthly rows (min 12), quarterly data repeated monthly  (~ TTM sums)
atdenom = (atq + atq.shift(3))/2 ; atdenom2 = atq.shift(3)            # shift = 3 ROWS of the BM-filtered monthly panel
roa = niqsum/atdenom ; cfroa = oancfqsum/atdenom
m1 roa > md_roa ; m2 cfroa > md_cfroa ; m3 oancfqsum > niqsum                                       # profitability, cash flow
niVol = std of roaq=niq/atq over 48 months (min 18) ; revVol = std of sg=saleq/saleq.shift(3)  (48 months, min 18)
m4 niVol < md_niVol ; m5 revVol < md_revVol                                                         # low volatility
m6 xrdqsum/atdenom2 > md ; m7 capxqsum/atdenom2 > md ; m8 xad/atdenom2 > md                         # R&D, capex, advertising intensity
tempMS = m1+...+m8 ; MS = 6 if tempMS in 6..8 ; MS = 1 if tempMS <= 1 ; else tempMS
```
`stata_ineq_pl`: a null operand is +infinity for ">" (a missing roa or atq-lag COUNTS as 1 against a finite median) and for "<" a null left side is False, a null right side True. All eight m's default to 0, so tempMS is never null once a row is in the sample.

## 4. Timing / lag convention
Quarterly items repeated monthly; annual record available datadate + 6 months. The score is computed every month but kept only when `month == (datadate.month + 6) % 12` (the refresh month) and forward-filled within permno otherwise. Quirk: for a JUNE fiscal year-end (datadate month 6) `(6+6) % 12 = 0` never equals a calendar month, so the score is never refreshed and those firms never score. Forward-fill runs over the firm's rows in the sample, so a firm that leaves the BM quintile stops scoring.
Here (scratch): ART TTM for the four-quarter sums, ARQ `assets` at q_back 0 and 1 for atdenom/atdenom2, std over the last 16 ARQ quarters (>= 6) for the volatilities; refresh-month timing NOT replicated (scored every month: an upper bound on coverage). ART smear does not arise (levels and trailing sums, not year-over-year flow differences); ARQ is used for the quarterly ratios only.

## 5. Filters
Sample rules in the code (not a portfolio filter): ceq > 0; lowest BM quintile; sic2D count >= 3. SignalDoc Filter blank. Industry medians are over the BM-quintile sample, not the universe: `ctx.market_context()` names, current siccode (declared look-ahead, D3/HX-2).

## 6. Predicted sign
SignalDoc `Sign = +1.0` (high G-score earns more); Cat.Form discrete; Cat.Economic composite accounting. Orientation: long HIGH, `ascending=True`.

## 7. The mass-point question
A score is a count of indicators. Measured mean cross-sectional share of the universe-scored names at each MS value (269 months): 1: 4.7%, 2: 10.8%, 3: 21.5%, 4: 19.8%, 5: 21.5%, 6: 21.7% (pre-bucket tempMS 0..7: 0.4, 4.3, 10.8, 21.5, 19.8, 21.5, 18.8, 2.9%). The modal value is 3 in 85 months, 6 in 82, 5 in 66, 4 in 36. Modal share 20.8%-52.9% (early months are inflated by thin ARQ history: null niVol/revVol make m4/m5 = 0, 61%/64% null at 1998-12, 3.5-17% in 2003-2019 (every sixth month sampled), 34-57% at 2020-12/2021-06 from recent listings). Ties: unavoidable and large (six tie blocks, four of them ~20%); nothing in the harness can design them away. Do-nothing firm: no constant; indicators depend on medians.

## 8. History needed (snapshot starts 1998-01)
Quarterly history for 48-month volatilities (SF1 1997Q4 start: >= 6 quarters only from about 1999Q2, ART thin in 1998Q1-Q3), annual/ART fundamentals, market cap at the signal. Not binding: MS scores from the first month (1998-12 to 1999-06 measured 31-34% coverage). `lookback_months` 48.

## 9. OSAP metadata
MS (Acronym2 Mscore); Mohanram 2005 RAS; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 2_fair; Cat.Form discrete; Cat.Data Accounting; Cat.Economic composite accounting; Sample 1978-2001;
Key Table 4A; Test "port sort"; Evidence "t=9 in port sort nonstandard data lag"; Sign +1.0; Return 1.575; T-Stat 9.14; Stock Weight EW; LS Quantile blank; Portfolio Period 1.0; Start Month 12.0; Filter blank; GScholar cites 561.
Notes: "OP's signal is really complicated ... complications in data lagging, combining annual and quarterly data, and sample selection". Definition: "MS is only evaluated for low BM firms and comes from combining three signals related to profitability and cash flow, two signals related to income volatility, and three signals related to investment."

## 10. Proposed Sharadar mappings with deviations (for the record; not recommended for translation)
```
ceq -> SF1 equity (ART) ; mve -> DAILY marketcap x 1e6 at the month-end ; BM = log(equity/mve) ; lowest quintile over market_context names ; sic2D = str(int(siccode))[:2]
niq/oancf/xrd/capx TTM -> SF1 netinc, ncfo, rnd, -capex (ART) ; atq -> SF1 assets ARQ q_back 0 and 1 ; roaq, sg, vols from fundamentals_history(ARQ, 16)
xad -> 0 (OSAP fill_null(0)) ; Stata-missing operators reproduced ; MS bucketed 1..6 ; ascending=True
```
Deviations: (a) xad absent, m8 dead (0-7 score); (b) ART/ARQ quarterly history replaces the monthly-repeated quarterly rolling means (std over 16 quarters, >= 6, vs 48 monthly rows, >= 18); (c) `equity` has no preferred split (ceq approx); (d) current siccode; (e) no refresh-month/forward-fill timing and no June-FYE drop; (f) BM quintile from ART equity vs annual ceq; (g) market-scope sample and medians, current-era universe.
Fields not in the map: none (`xad` is in the map as unavailable). Recommendation: frontier as `preflight_failed` with the measured reason (6-valued score, modal share 20.8-52.9%, coverage 13.4-35.6% < 40% in all 269 months); approx on data alone.
