# ShareIss5Y — spec (fetched fresh; pinned OSAP ref b4e911e6; measured on DATA_SHA 198b281de1a0, 2026-09-30)

## 1. Data availability and verdict
VERDICT: **approx**, with a data-start caveat: 43 months (1999-01..2002-06) sit below 40% coverage; first >= 40% at 2002-07;
233 of 276 months are above the bar (270 have >= 10 scored names). No input unavailable; no zero-fill.
Preflight expected: pass with two warnings (first probe month 1998-12 scores 0 names; lookback 80m reaches before the panel start).
- Inputs: shrout (CRSP monthly), cfacshr (CRSP monthly) -> one Sharadar route: SF1.sharesbas, dimension ARQ.
- `crsp.shrout` in field_map_index: approx (company-level, all-class count; filing-date cadence; SPLIT-RESTATED to
  today's basis on every historical row). `crsp.cfacshr` is NOT in the map index: its job (split adjustment) is done
  by the restated sharesbas itself, so no separate field is read. Flag for field-checker only as "covered by shrout".
- Split neutrality VERIFIED on this snapshot (ARQ sharesbas at t-5 vs t-65, raw SF1): AAPL (7:1 + 4:1 inside the window)
  ratio-1 = -0.108; NVDA (4:1, 10:1) +0.167; C (1:10 reverse) +0.047; TSLA (5:1, 3:1) +0.438. A ratio of two
  readings on the same route is split-neutral; never pair sharesbas with closeunadj (known trap).
- OSAP zero-fills: none. Missing shrout/cfacshr at either end -> NaN, row dropped (dropna on the final signal).

## 2. Variables (exact source names)
ShareIss5Y.py: permno, time_avail_m (SignalMasterTable); monthlyCRSP: shrout, cfacshr.
temp = shrout * cfacshr (adjusted shares; the SignalDoc text says "shrout/cfacshr", the CODE multiplies).

## 3. Formula
Adjusted share count 5 months ago minus 65 months ago, over the 65-month-ago count:
  ShareIss5Y = (temp[t-5] - temp[t-65]) / temp[t-65]
Key lines: `time_lag5 = time_avail_m - DateOffset(months=5)`, `time_lag65 = ... months=65`, exact-month left merges on
(permno, lagged month), so a firm needs a row at BOTH t-5 and t-65 and the window is 60 months ending 5 months
before t (the 5-month gap is OSAP's own skip: "t-5..t" in Daniel-Titman notation).
Sharadar: (sharesbas_ARQ@(t-5) - sharesbas_ARQ@(t-65)) / sharesbas_ARQ@(t-65), each = latest filing with
datekey <= that business month-end (ctx.fundamentals_at_month_ends(["sharesbas"], [5, 65], dimension="ARQ")).

## 4. Timing / lag
OSAP value at month t uses CRSP rows at t-5 and t-65 (no fundamentals lag; shrout updates at corporate events).
Harness: the signal is observed at the business month-end before rebalance and is PIT by filing date (datekey), so
ART-vs-ARQ does not arise for a level; ARQ is the right dimension (quarterly cadence, reaches back further than ART).
Share counts step at filing dates, so the t-5 and t-65 readings are up to ~3 months stale vs CRSP monthly shrout.
No flow item, no TTM smearing. FactorDef: dimension="ARQ"; history_months need not gate on a price (this is not a
return window); lookback_months ~ 65 + 15 (latest ARQ filing up to 15 months old at the t-65 end) = 80.

## 5. Filters
SignalDoc Filter: none. OSAP portfolio stage: Portfolio Period 12, Start Month 6 (annual-style holding; the harness
is monthly). Harness universe only. Nothing is restricted inside the factor.

## 6. Predicted sign
SignalDoc Sign = -1 (heavy issuers earn less). ascending=False (LOW ShareIss5Y = long leg).
Daniel and Titman 2006, JF; t = 4.39 univariate regression; Cat.Economic = external financing; sample 1968-2003.
SignalDoc note: OSAP studies this indirectly; closest studied object is iota (includes dividends).

## 7. Mass-point question
Do-nothing firm (no share change over the 60 months) = exactly 0.0. Measured on the harness universe over 270 months
with >= 10 scored names (1999-06 .. 2021-12): exact-zero share mean 0.27%, max 1.67%; modal-value share of the
cross-section mean 0.29%, max 3.45% (a 29-name month); within +-1% of zero mean 5.4% (3.6-8.3%). qcut yields 10 bins
in all 270 months. Distinct values ~1,350 mean. NOT a mass point. Tie handling: average rank; nothing floored.
Heavy right tail (median over months: p1 -0.34, p50 +0.05, p99 +4.5), handled by the harness 1/99 winsorise.

## 8. History needed and scorable months (snapshot starts 1998-01; SEP 1997-12; SF1 min datekey 1990-06)
Needs sharesbas known at the t-65 month-end. SF1 ARQ is thin before ~1998, so early months are thin by data, not by rule:
coverage of the harness universe: 1999-12 8.9% (239 names), 2000-12 13.1%, 2001-12 30.8%, 2002-12 49.1%,
2003-12 79.6%, 2007-04 83.8%, 2015-08 79.0%, 2021-11 74.3% (mean over 270 scored months 71.6%; ~70% over all 276).
Months with >= 10 scored names: 270 of 276 (first 1999-06). Months with coverage >= 40%: 233 (first 2002-07),
>= 79%: 201 (first 2003-12). All exceed rebalance.min_months 120 whichever convention is applied; the 1999-2002
months are survivors-with-early-SF1 and are a small, biased sample. If a price-history gate (has_price_at(65)) were
declared it would null everything before 2003-06 (SEP starts 1997-12) - do NOT declare one; ARQ sharesbas needs no price.
The t-5 end is known for 98.5% of names (min 91.4%); the t-65 end binds.

## 9. OSAP metadata
Acronym ShareIss5Y (Acronym2 ShareIs1); Cat.Signal Predictor; Cat.Form continuous; Cat.Data Accounting;
Cat.Economic external financing; Predictability in OP 1_clear; Signal Rep Quality 2_fair; Authors Daniel and Titman;
Year 2006; Journal JF; SampleStart 1968, End 2003; Stock Weight EW; LS Quantile blank; Start Month 6; Return blank.
Upstream cached: upstream_CRSPMonthly.py (shrout, cfacshr straight from crsp.msf), upstream_SignalMasterTable.py.

## 10. Proposed Sharadar mappings and deviations
| OSAP | Sharadar | deviation |
|---|---|---|
| shrout*cfacshr @ t-5, t-65 | SF1.sharesbas ARQ @ business month-end t-5, t-65 | company-level (all classes), filing-date steps, split-restated to today's basis (ratio is split-neutral) |
| exact-month CRSP row required | latest ARQ filing <= month-end (<= 15 months old) | no gap requirement; carried forward between filings |
| permno | permaticker via harness | multi-class firms: one company-level count on the primary ticker |
Fields not in the map index: crsp.cfacshr (see section 1).
Route B (DAILY.marketcap*1e6/SEP.close) agrees with ARQ sharesbas on 99.6-99.7% of members within 1% but starts 2003-12 for
a 65-month ratio (DAILY from 1998-12), so use route A only; never mix routes across the two ends.
