# ShareRepurchase — spec (fetched fresh; pinned OSAP ref b4e911e6; measured on DATA_SHA 198b281de1a0, 2026-09-30)

## 1. Data availability and verdict
VERDICT: **preflight_failed** (binary signal: 2 distinct values, modal share 50-72%, qcut yields 1-2 bins, vs the
10% / 10-bin cliff). The input mapping alone would be **approx** (see below). Recommend frontier row, not translation.
- Input: prstkc (Compustat annual). `compustat.prstkc` in field_map_index: approx -> SF1.ncfcommon, a NET common-equity
  flow (issuance incl. option exercises minus repurchases), preferred excluded. The gross prstkc (>0 test) is NOT
  reproducible; the closest translation is the net-repurchase indicator ncfcommon < 0.
- OSAP ZERO-FILLS prstkc: upstream CompustatAnnual.py zero_fill_vars (b4e911e6) includes prstkc (and prstkcc, sstk), so
  in OSAP a missing prstkc becomes 0 and the final `df.loc[prstkc.isna()] = nan` line is moot for any firm with an
  annual row: the signal is 0 or 1 for every annual record, never missing. A zero-fill of the optional term would be
  "approx", not a reason for infeasible.

## 2. Variables
m_aCompustat: gvkey, permno, time_avail_m, prstkc (annual, datadate + 6 months availability, each annual record
replicated for 12 monthly rows; upstream_CompustatAnnual.py lines ~215-246).

## 3. Formula
ShareRepurchase = 1 if prstkc > 0 else 0 (prstkc NaN -> NaN in the code, but already filled to 0 upstream).
Key lines: `df["ShareRepurchase"] = ((df["prstkc"] > 0) & df["prstkc"].notna()).astype(int)`.
Detailed Definition: "1 if stock repurchase indicated in cash flow statement (prstkc > 0), 0 if prstkc = 0."
Sharadar analogue: 1 if SF1.ncfcommon < 0 (net common-equity outflow), else 0; dimension ART (TTM; ARY is the YTD form).

## 4. Timing
OSAP: annual item available datadate+6 months, held 12 months (stale by up to 18 months). Harness: ART as of datekey
(median filing lag 44 d, p95 101 d), latest filing <= signal date, <= 15 months old: information arrives earlier than
OSAP's 6-month rule and refreshes quarterly (ART is a TTM flow; a repurchase in any of the last four quarters counts).
Flow item: ART is TTM, no year-over-year difference is taken, so no smearing issue; ncfcommon is net of option-exercise
issuance, so a firm buying back less than it issues scores 0 where Compustat prstkc > 0 would score 1.

## 5. Filters
SignalDoc Filter blank; LS Quantile and Quantile Filter blank. Portfolio Period 12, Start Month 6. None inside the factor.

## 6. Predicted sign
SignalDoc Sign = +1 (repurchasers earn more). ascending=True. Ikenberry, Lakonishok, Vermaelen 1995, JFE, Table 3 "All
firms Year 1"; t = 1.85 (long benchmark portfolio, char adjusted); Predictability in OP 2_likely, Signal Rep Quality
3_distant; Cat.Economic payout indicator; Cat.Form discrete; sample 1980-1990.

## 7. Mass-point question
A do-nothing firm (no repurchase) scores 0. The measurement is the verdict: harness universe, 276 months 1999-01..2021-12,
ncfcommon (ART, PIT), net-repurchase indicator:
- distinct values 2 in every month (continuous ncfcommon is not the signal); modal share of the non-null cross-section
  mean 57.6% (min 50.0%, max 72.3%); qcut bins 1 in almost every month, 2 at best.
- ncfcommon < 0 among non-null: mean 45.1% (27.7-60.3%); exact zero 5.7%; > 0 49.2%. Under OSAP's zero-fill (null -> 0)
  the 1-share is 43.4% (22.4% in the thin 1998-12 month).
- ncfcommon null share of universe: mean 3.95% (0.4-48.1%; 48% at 1998-12, 14.5% at 1999-12, 3.0% at 2003-12, 7.6% at 2021-11).
Tie handling would be a two-group split, not deciles; under the project's decile harness the tie block spans every
decile boundary, so this is a hard preflight fail, not a translation choice. No continuous redefinition is in scope
(ncfcommon/marketcap is a different predictor).

## 8. History
ART ncfcommon null share is 14.5% at 1999-12 and 3.0% at 2003-12 (mean 3.95% over 276 months); thin only at the start. Not binding.
No lookback beyond the latest filing (<= 15 months).

## 9. OSAP metadata
Acronym ShareRepurchase; Predictor; Cat.Form discrete; Cat.Data Accounting; Cat.Economic payout indicator;
Predictability 2_likely; Rep Quality 3_distant; Authors Ikenberry, Lakonishok, Vermaelen; 1995; JFE; Sample 1980-1990;
Return 0.17 (as listed), T-Stat 1.85; Stock Weight EW; Portfolio Period 12; Start Month 6. No upstream beyond
CompustatAnnual (not cached here for this acronym; the same script is cached under RoE/upstream_CompustatAnnual.py).

## 10. Proposed Sharadar mapping and deviations (only if the owner overrides the preflight verdict)
| OSAP | Sharadar | deviation |
|---|---|---|
| prstkc > 0 (gross buyback incl. preferred) | SF1.ncfcommon < 0, ART | net of issuance; preferred excluded; TARP-era financials differ |
| prstkc zero-fill | null ncfcommon -> 0 (mean 3.95% of universe) | matches OSAP's fill; approx |
| datadate+6m, 12-month hold | datekey, ART, <= 15 months | earlier and quarterly |
Fields all in the map index (compustat.prstkc, compustat.prstkcy). No field outside the map.
