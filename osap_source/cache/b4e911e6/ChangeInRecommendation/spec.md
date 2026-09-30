# ChangeInRecommendation — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: INFEASIBLE (recommend `infeasible`)
The entire signal is the IBES analyst recommendation code `ireccd` (Jegadeesh et al. 2004,
Table 3C). This snapshot holds no IBES, no estimates and no recommendations table: SF1, SEP, DAILY,
ACTIONS, EVENTS (code 22 from 2004-08), SF2 (2008), SF3/SF3A (2013-06), TICKERS, SP500, METRICS,
DESCRIPTIONS; none carries analyst ratings. `field_map_index.yaml` and `field_map.yaml` have no
`ibes.*` / `ireccd` key. OSAP does NOT zero-fill it: a firm-month without a recommendation is
absent from the output (dropna on ChangeInRecommendation), so there is no fill that would rescue
a term. No faithful proxy: SF3 institutional holdings start 2013-06 against a 1999 window, EVENTS
are corporate events, price momentum is a different variable. Do not translate; log an
`osap_frontier.yaml` row: "IBES analyst recommendations (ibes.recddet ireccd) not published by
Sharadar".
SignalDoc itself grades the signal `Signal Rep Quality = 4_lack_data`: OSAP's own IBES recs begin
in 1993 and its sample is short.

| input (OSAP) | field_map key | Sharadar | status |
|---|---|---|---|
| `ireccd`, `amaskcd`, `anndats` (ibes.recddet; upstream_IBESRecommendations.py) | none | none | unavailable |
| `tickerIBES` (SignalMasterTable IBES-CRSP link) | none | none | unavailable (WRDS link) |
| `permno`, `time_avail_m` (panel rows) | crsp.smt_row | SEP presence | mapped, harness-side, irrelevant |

## 2. Variables by exact source name (predictor.py)
IBES_Recommendations.parquet: tickerIBES, amaskcd, anndats, time_avail_m, ireccd (1 strong buy ..
5 sell). SignalMasterTable: permno, tickerIBES, time_avail_m (inner join).

## 3. Formula (documented for completeness)
    per (tickerIBES, amaskcd, time_avail_m): ireccd = last non-missing
    per (tickerIBES, time_avail_m):          ireccd = mean across analysts
    opscore = 6 - ireccd                      # higher = better
    opscore_lag = groupby(tickerIBES).shift(1)   # previous ROW, not previous calendar month
    ChangeInRecommendation = opscore - opscore_lag  (NaN if lag missing)
No additional transformation; output rows only where the change exists and a permno matches.

## 4. Timing / lag convention
Monthly, one-month change in the mean consensus score; `shift(1)` is row-based, so a firm-month
gap (no recommendation in a month) makes the difference span more than one month. Sharadar has no
analog; ART-as-of-filing is irrelevant (no SF1 input, no flow item).

## 5. Filters
predictor.py: none; SignalDoc `Filter` empty; `Quantile Filter` 0.2.

## 6. Predicted sign (SignalDoc)
`Sign = +1.0`: upgrades predict higher returns. Cat.Signal Predictor; Cat.Economic `recommendation`;
Cat.Form continuous; Cat.Data Analyst; Jegadeesh, Kim, Krische, Lee 2004 (JF); sample 1985-1998;
Predictability in OP 1_clear; Rep Quality 4_lack_data; Key Table "3C", "LS nonstandard data";
OSAP Return 0.225, EW, LS quantile 0.2, Portfolio Period 1, Start Month 12. Notes: OSAP's IBES recs
start 1993; OP is binary, OSAP follows the mean-change construction.

## 7. The mass-point question
Not measurable here. In IBES the mean-of-analyst change is exactly 0 for any firm with no rating
change, and coverage is concentrated in larger firms; the share at exactly 0 would be large (most
covered firm-months). Moot for this snapshot.

## 8. History needed
Not applicable (no data). Were the data available: one prior month of recommendations; the
snapshot price side starts 1998-01, OSAP's IBES recommendations start 1993.

## 9. OSAP metadata
Acronym ChangeInRecommendation (Acronym2 ChRecomm); Sign +1; EW; LS quantile 0.2; portfolio period
1; start month 12. Source `Signals/pyCode/Predictors/ChangeInRecommendation.py` (legacy
`ChangeInRecommendation.do`, download `M_IBES_Recommendations.do`) at
b4e911e69678a7424f318617a61d813f54183123; output `ChangeInRecommendation.csv [permno, yyyymm,
ChangeInRecommendation]`. Cached: predictor.py, signaldoc_row.csv, upstream_IBESRecommendations.py.
SignalDoc definition: "keep last ireccd each month, then average across analysts for each
firm-month. Define opscore as 6-ireccd. Signal is opscore - last month's opscore."

## 10. Proposed Sharadar mappings and deviations
None: no mapping exists. Verdict `infeasible`; frontier row reason: "IBES analyst recommendation
(ireccd) not published by Sharadar; no OSAP zero-fill; no proxy". Fields not in field_map:
ibes.ireccd, ibes.amaskcd, ibes.tickerIBES (unavailable, not to be added as mapped).
