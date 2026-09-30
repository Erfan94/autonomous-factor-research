# DownRecomm — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: INFEASIBLE (recommend `infeasible`)
| OSAP input | source | Sharadar | status |
|---|---|---|---|
| `ireccd` (recommendation code), `amaskcd` (analyst), `anndats` | `IBES_Recommendations` | none: no IBES / estimates / recommendations table in the snapshot | unavailable |
| `tickerIBES` | `SignalMasterTable` (IBES-CRSP link) | none | unavailable |
- The signal is a month-over-month change in the cross-analyst mean IBES recommendation. Nothing else enters; there is no optional or zero-filled term to drop, so dropping leaves nothing. No IBES, options, 13F (pre-2013), patents, segments, ratings, pensions, xad, emp, ob or ppegt input is substituted and no proxy exists (SF3/SF3A holdings are 2013-06+ and are not analyst opinions).

## 2. Variables (predictor.py)
`IBES_Recommendations`: tickerIBES, amaskcd, anndats, time_avail_m, ireccd. `SignalMasterTable`: permno, tickerIBES, time_avail_m.

## 3. Formula
```
per (tickerIBES, amaskcd, month): ireccd = last;  per (tickerIBES, month): ireccd = mean across analysts
ireccd_lag = ireccd.shift(1) (row-based, per tickerIBES)
DownRecomm = (ireccd > ireccd_lag) & ireccd_lag.notna()     # 1 if the mean code rose vs the previous row, else 0
inner-join SignalMasterTable on (tickerIBES, time_avail_m)
```
In IBES a HIGHER code is worse (1 strong buy .. 5 sell), so `>` flags a downgrade; the code comment says "improvements". SignalDoc's Detailed Definition describes something else (binary on the mean next-quarter EPS forecast `meanest`, fpi = 1) and Notes say OSAP follows a related paper for forecasts; definition, comments and code disagree. Moot given the verdict.

## 4. Timing / lag
OSAP: month-of-announcement IBES aggregates, signal at t used for t+1 (Portfolio Period 1, Start Month 12). Not constructible here, so no harness timing is proposed.

## 5. Filters
None in SignalDoc. Rows exist only for covered names (inner join), so an absent name is NaN, not 0.

## 6. Predicted sign
`Sign = -1.0` (Barber, Lehavy, McNichols, Trueman 2001 JF, Table 3C: downgrades earn lower returns; event-study t > 8 in a 3-day window, the OSAP portfolio form is monthly). Would be `ascending=False`.

## 7. Mass-point question
A do-nothing covered firm (mean code unchanged or improved) = 0. A binary flag; share of ones not measurable here (no data). Structurally a change in a monthly mean over a few analysts is non-zero for most covered names, so the flag would be a large fraction at each value, and binary values hit the preflight mode >= 10% and < 10 `qcut` bins hard-fail regardless. Coverage would also be partial (analyst-covered names only).

## 8. History needed
IBES recommendation history (OSAP sample 1985-1997). Sharadar has none. Usable decision months: **0** of 276.

## 9. OSAP metadata
Barber, Lehavy, McNichols and Trueman (2001), JF; Cat.Data Analyst; Cat.Economic earnings forecast (SignalDoc); Cat.Form discrete; sample 1985-1997; Acronym2 DownRecomm; Predictability "2_likely"; Signal Rep Quality "4_lack_data"; Test "event study 3 day nonstandard data"; Key Table "3C, 2 to 1, 3 to 2, etc."; Sign -1.0; EW; Portfolio Period 1, Start Month 12. Source `Signals/pyCode/Predictors/DownRecomm.py`.

## 10. Proposed Sharadar mappings
None. `field_map_index.yaml` has no entry for `ireccd`, `amaskcd`, `anndats`, `tickerIBES` (grep: 0 hits). Recommend `infeasible`: the sole input is an unavailable vendor table (analyst recommendations) and OSAP does not zero-fill it.
