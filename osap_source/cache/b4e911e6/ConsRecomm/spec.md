# ConsRecomm — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: INFEASIBLE (recommend `infeasible`)
Checked against `osap_source/field_map_index.yaml`.

| OSAP var | source | Sharadar | status | role |
|---|---|---|---|---|
| ireccd | IBES_Recommendations (ibes.recddet, per analyst amaskcd, anndats) | none: no IBES / estimates / recommendations table in the snapshot | **unavailable** | the only signal input |
| tickerIBES | SignalMasterTable (IBES-CRSP link) | none | unavailable | permno join |

- The whole signal is the cross-analyst mean of IBES recommendation codes.
  Nothing else enters. There is no zero-fill or optional term to drop
  (predictor.py has no `fillna`), so the approx route does not exist.
- Sharadar products held (SF1, SEP, DAILY, ACTIONS, EVENTS, TICKERS, SF2 insiders
  from 2008, SF3/SF3A 13F from 2013-06) carry no analyst recommendations. SF2
  insider trades, 13F holdings and EVENTS (8-K item codes) are not recommendation
  proxies; no near-match is to be substituted.
- Verdict: **infeasible** (IBES recommendations not published by Sharadar).

## 2. Variables by exact source name (predictor.py)
`IBES_Recommendations`: tickerIBES, amaskcd (analyst code), anndats (announcement
date), time_avail_m, ireccd (1 = strong buy ... 5 = sell). Upstream
(`upstream_IBESRecommendations.py`, cached): ibes.recddet with usfirm = '1';
non-numeric or missing ireccd dropped; `time_avail_m = month(anndats)`.
`SignalMasterTable`: permno, time_avail_m, tickerIBES (link; one IBES ticker may
match several permnos).

## 3. Formula
    per (ticker, analyst, month): ireccd = last value by anndats
    per (ticker, month): ireccd = mean over analysts
    ConsRecomm = 1 if ireccd > 3 ; 0 if ireccd <= 1.5 ; else NaN
    inner merge on (tickerIBES, time_avail_m) with SignalMasterTable

Only analysts who issued a recommendation IN that calendar month contribute: no
carry-forward of an older rating. A firm-month with no fresh recommendation has no
row at all.

## 4. Timing / lag convention
Same-month: a recommendation announced any day in month t enters the month-t
value (no extra lag in the predictor; portfolio code applies the usual one-month
forward hold). Fundamental ART-as-of-filing is irrelevant: no SF1 input.

## 5. Filters
None in predictor.py; SignalDoc Filter blank. Only firms with at least one
recommendation in the month (coverage thin pre-1993, sparse for small caps).

## 6. Predicted sign (SignalDoc)
`Sign = -1.0`: ConsRecomm = 1 (mean rating worse than hold, i.e. "sell") predicts
low returns; score would be -ConsRecomm. Cat.Form discrete, Cat.Data Analyst,
Cat.Economic recommendation; VW, LS Quantile 0.2, Portfolio Period 1, Start Month
6; Signal Rep Quality 4_lack_data; Predictability in OP 2_likely.

## 7. The mass-point question
Output is binary {0, 1} on a thin subset: only firms with mean ireccd > 3 (sells,
a few percent of covered firm-months historically) or <= 1.5 (strong buys, a
larger minority). The middle of the rating distribution (1.5 < ireccd <= 3, the
typical covered firm) is NaN, so the do-nothing "hold-ish" firm is unscored, not
tied. Precise shares are unmeasurable here (data absent). Ties: two-point signal,
average ranks, deciles collapse to two. Moot.

## 8. History needed
Monthly, no lookback. Irrelevant: no data. OSAP's own sample is 1993 onward.

## 9. OSAP metadata
ConsRecomm; Barber, Lehavy, McNichols and Trueman (2001, JF), "Consensus
Recommendation"; Key Table 3A (daily rebalancing; OSAP uses Table 6C definitions);
port sort nonstandard data, t = 3.197 (return 0.79); sample 1985-1997; Signal Rep
Quality 4_lack_data; GScholarCites202509 = 1859. OSAP note: its data begin 1993,
so the published sample cannot be replicated. Source
`Signals/pyCode/Predictors/ConsRecomm.py` (confirmed in tree.txt; upstream cached
as `upstream_IBESRecommendations.py`).

## 10. Proposed Sharadar mappings
None. ireccd / tickerIBES have no Sharadar counterpart; not in field_map_index as
a constructible field. Recommendation: `infeasible` (IBES recommendations).
