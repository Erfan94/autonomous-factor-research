# RevenueSurprise — Standardized revenue-per-share surprise (Jegadeesh and Livnat 2006, JAE, Table 7 Model 1 SURGE)

OSAP ref b4e911e69678a7424f318617a61d813f54183123. `Signals/pyCode/Predictors/RevenueSurprise.py` (cached as `predictor.py`); the SignalDoc
row with Cat.Signal == Predictor is the authority (`signaldoc_row.csv`). Upstream read: `upstream_CompustatQuarterly.py`,
`upstream_SignalMasterTable.py`. Measured on THIS snapshot, DATA_SHA 198b281de1a0, harness universe, all 276 decision months.

## 1. Data availability (verdict: APPROX; NO IBES; no zero-fill of an optional term)
| input (OSAP) | field_map key | Sharadar source | status |
|---|---|---|---|
| `revtq` (m_QCompustat) | `compustat.revtq` | `SF1.revenue`, `dimension="ARQ"` (single-QUARTER flow; 4 ARQ sum = ART revenue) | mapped via `compustat.revt` verified 2026-09-30 (ARQ null 3.44%, exact-zero 5.74% of rows); `revtq` entry itself `verified_on` empty |
| `cshprq` (m_QCompustat) | `compustat.cshprq` | `SF1.shareswa`, `dimension="ARQ"` (quarter weighted average, a level) | mapped, `verified_on` empty on THIS snapshot (prior-snapshot probe: null 0.05%, zero 0.13% = vendor fill, treat as missing) |
| `gvkey`, `permno`, `time_avail_m` (SignalMasterTable) | n/a | harness universe IDs, PIT by `datekey` | n/a |
The predictor reads NO I/B/E/S: revenue per share is Compustat `revtq/cshprq`, the "surprise" is a seasonal-difference drift model (like
EarningsSurprise), not an analyst surprise. Not used: IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob, ppegt.
Why `approx`, not `feasible`: financial/foreign-format `revtq` vs SF1 `revenue`; `shareswa` vs Compustat `cshprq`; SF1 restated-quarter
vintage; portfolio-stage price filter not reproduced. No input is missing and nothing is zero-filled; OSAP's skipna partial windows are reproduced.

## 2. Variables
`revtq`, `cshprq` (quarterly, per gvkey); derived `revps`, `revps_l12`, `GrTemp`, `grtemp_lag{3..24}`, `Drift`, `RevenueSurprise`, `rs_lag{3..24}`, `SD`.

## 3. Formula
```
revps      = revtq / cshprq
GrTemp     = revps - revps(12 months ago)                      # year-over-year change in revenue per share
Drift      = mean(GrTemp lagged 3,6,...,24 months)              # 8 lags, pandas .mean() skips NaN (needs >= 1)
RS         = revps - revps_l12 - Drift  = GrTemp - Drift
SD         = std(RS lagged 3,6,...,24 months, ddof=1)          # 8 lags, skips NaN (needs >= 2)
RevenueSurprise = RS / SD ;  inf -> NaN ; keep only SD not NaN and SD > 1e-8
```
Raw ratio, no winsorising. Quarter index k (0 = latest quarter): `GrTemp_k = revps_k - revps_{k+4}` (k = 0..16); `Drift_k = mean(GrTemp_{k+1..k+8})`;
`ES_k = GrTemp_k - Drift_k` (k = 0..8); `SD = std(ES_1..ES_8, ddof=1)`; signal = `ES_0 / SD`. The monthly lags 3..24 of OSAP's 3-row quarterly
expansion are quarters 1..8. Identical structure to the reviewed `factors/candidates/EarningsSurprise.py`: reuse its ARQ-by-reportperiod idiom.

## 4. Timing / lag; ARQ vs ART
`ctx.fundamentals_history(["revenue","shareswa"], 21, dimension="ARQ")`, quarters placed on k = 0..20 by REPORT PERIOD (calendar quarters
back from the latest `reportperiod`), PIT by `datekey <= signal_asof`, amended quarter = latest datekey. `FactorDef.dimension = "ARQ"` is
MANDATORY: under ART `revenue` is a trailing-4-quarter SUM and the year-over-year difference smears four quarters (the TTM smear trap; ART==ARQ-sum
within $1 on 96.0% of pairs); `shareswa` at ART is fiscal-year-mixed. Both columns at ARQ. Staleness: OSAP keeps a quarter only three months past its
availability; EarningsSurprise gated the latest filing at 110 days. Measured effect on this factor: the gate is the cause of the February dips
(latest 10-Q filed about 2-14 Nov, 110 days before 28 Feb); a 135-day gate lifts mean coverage 87.6% -> 89.3% and cuts months under 40% from 4 to 3.
Recommend 110 days for consistency with EarningsSurprise; state the choice as an OVERRIDE of `max_fundamental_age_months` 15.

## 5. Filters
SignalDoc Filter column empty; the Detailed Definition says "Exclude if price less than 5" (portfolio stage, NOT in `predictor.py`). Not reproduced;
universe is price >= $1. A scored row needs SD > 1e-8; a name with identical revenue per share every quarter is dropped as NaN.

## 6. Predicted sign (SignalDoc)
`Sign = +1.0` -> `ascending=True` (high surprise is the long leg). Cat.Economic `sales growth`, Cat.Data `Accounting`, Cat.Form `continuous`.
Signal Rep Quality 2_fair (t>2.6 in many event studies; no t-stats).

## 7. The mass-point question
Do-nothing firm (revenue per share unchanged every quarter): GrTemp = 0, ES = 0, SD = 0 -> NaN by the SD gate, not a mass at 0. A firm with
exactly zero revenue for all quarters (pre-revenue cohort; ARQ exact-zero 5.74% of rows) also has SD = 0 -> NaN. The one exact value is ES_0 = 0
with SD > 0 (a zero-surprise quarter). Measured, 276 months: max modal-value share 0.170% (2015-08-31, three names at exactly 0.0; mean 0.065%), exact zeros
110 name-months over 84 months, distinct values >= 99.89% of scored names, `qcut` yields 10 bins in every month. Heavy tails (max |signal| 643 at
1999-12-31) are a rank non-issue. Tie handling: null on SD gate, missing, warm-up; else average rank; no zero-fill, no floor.

## 8. History needed, measured coverage
- `lookback_months` = 67 as EarningsSurprise (21 quarters back + the 110-day gate + period-end-to-filing gap); no `history_months` (fundamentals, not a return window).
- Minimum history 8 quarters of revenue and shares (ES_1, ES_2 each need a GrTemp and a Drift lag); a full window is 21 quarters. SF1 datekeys start 1993-12-22,
  so the warm-up binds only in the first 15 months.
- Coverage of universe (110-day gate): mean 87.6% over 276 months (first-15-months 32.7%-49.6%; 1998-12-31 35.0%, 1999-02-26 32.7% minimum, 1999-03-31 41.4%);
  from 2000-03 on mean 90.2%, min 38.9% (2005-02-28; 2006-02-28 also under 60%; February gate effect); 4 of 276 months under 40%
  (1998-12, 1999-01, 1999-02, 2005-02). Scored names min 741, median 1,734. All 276 months carry scores (no data-start truncation).
- Measured with a prototype of section 3/4 against `ctx.fundamentals_history(dimension="ARQ")`, all 276 months.

## 9. OSAP metadata
Acronym `RevenueSurprise`; Acronym2 RevSurprise; Authors Jegadeesh and Livnat; Year 2006; Journal JAE; Sample 1987-2003; Predictability in OP 1_clear;
Signal Rep Quality 2_fair; Test "event study regression 6 months" (Table 7 Model 1 SURGE); Stock Weight EW; LS Quantile 0.2; Portfolio Period 1; Start Month 6;
GScholarCites 506. Detailed Definition: "revenue per share = quarterly revenue (revtq) / quarterly common shares (cshprq). RevenueSurprise is the 4-quarter change
in revenue per share minus the average 4-quarter change over the previous 2 years, scaled by its standard deviation over the previous 2 years. Exclude if price less than 5."

## 10. Proposed Sharadar mappings and deviations
- `revtq` -> `SF1.revenue` ARQ (single-quarter flow, reporting currency; universe fx = 1 on ~99.9%, so no USD conversion needed, ratio scale cancels per name).
- `cshprq` -> `SF1.shareswa` ARQ, 0 or null -> missing (vendor zero-fill); split-restated to today's basis on every row, so `revenue/shareswa` has no split jumps
  (the verified note: median k = -0.001 on 7,441 splits); OSAP's raw Compustat `cshprq` is as-first-reported (spurious split "surprises" there, absent here).
- Quarters aligned by `reportperiod` (index k), not by OSAP's calendar-month lags on a three-row quarterly expansion.
- Restated quarters: latest `datekey` on or before the signal per `reportperiod` (can differ from OSAP's Compustat vintage).
- SD gate 1e-8 as in OSAP's source (not EarningsSurprise's 1e-10).
- Staleness: latest ARQ filing <= 110 days old (override, see 4). Price >= 5 filter not reproduced (harness price >= $1).
- Declare `FactorDef.dimension="ARQ"`, inputs `SF1.revenue`, `SF1.shareswa`. Fields not in the index: none (`revtq`, `cshprq` are mapped).
- Field-checker: `compustat.cshprq` (shareswa ARQ) and `compustat.revtq` (revenue ARQ) carry empty `verified_on` in the index: confirm on THIS snapshot (the prototype here scored 276 months from them: coverage above, but that is not a field verification).
