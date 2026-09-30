# ChNAnalyst — Decline in Analyst Coverage (Scherbina 2008, Table 2 alpha return diff)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/ChNAnalyst.py` (cached
`predictor.py`, `signaldoc_row.csv`, `upstream_IBESEPSUnadjusted.py` = the IBES download it reads).
DATA_SHA 198b281de1a0. SignalDoc row (Cat.Signal == Predictor): Cat.Data = Analyst,
Cat.Economic = earnings event, Cat.Form = discrete (binary), sample 1982-2005.

## 1. Data availability (verdict: INFEASIBLE — recommend `infeasible`)

The entire signal is the IBES analyst COUNT (`numest`). This snapshot holds no IBES and no estimates
table (SF1, SEP, DAILY, ACTIONS, EVENTS, SF2 from 2008, SF3/SF3A from 2013-06, TICKERS, ...; none
carries analyst counts or forecasts). `field_map_index.yaml` has no `ibes.*` / `numest` key. OSAP does
NOT zero-fill it: `ChNAnalyst` is set NaN unless both `numest` and its 3-month lag exist, so there is
no zero-fill rescue. No faithful proxy exists (news/EVENTS, institutional holdings from SF3 from
2013-06, or volume are different variables; SF3 starts 2013-06 against a 1999 window).

| input (OSAP) | field_map key | Sharadar | status | note |
|---|---|---|---|---|
| `numest` (IBES `statsumu_epsus`, fpi = "1", last `statpers` of month) | none | none | unavailable | analyst coverage count; not published by Sharadar |
| `fpedats`, `statpers` (validity test, only used to patch `meanest`) | none | none | unavailable | IBES summary fields |
| `tickerIBES` (SignalMasterTable, IBES-CRSP link) | none | none | unavailable | link table WRDS-only |
| `mve_c` (SignalMasterTable market value, size-quintile filter) | `crsp.me` | DAILY.marketcap (MILLIONS USD) | mapped | only used for the size filter; irrelevant to the verdict |
| `permno`, `time_avail_m` (panel rows) | `crsp.smt_row` | SEP presence, `has_price_at(m, 31)` | mapped | harness-side |

Do not translate; log an `osap_frontier.yaml` row with reason "IBES analyst coverage count (numest) —
analyst data not in Sharadar snapshot; no OSAP zero-fill; no estimates table" and do not preflight.
Nothing to field-check: the blocking input has no mapping.

## 2. Variables (exact source names)

`numest`, `meanest`, `fpi` (only `"1"` kept), `statpers`, `fpedats`, `tickerIBES`, `mve_c`, `permno`,
`time_avail_m`. Only `numest` reaches the signal; `meanest` is patched (see below) but then dropped.

## 3. Formula

Binary: 1 if the number of analysts on the FY1 EPS forecast fell versus three months ago, 0 if it
did not fall; NaN otherwise. Restricted to the smallest two size quintiles. Key lines:
```
ibes_df = ibes_df[ibes_df["fpi"] == "1"]
# tmp/meanest patch block: modifies meanest only; numest is untouched, so it is dead code for this signal
df = SignalMasterTable[["permno","time_avail_m","tickerIBES","mve_c"]].merge(temp_ibes, on=["tickerIBES","time_avail_m"], how="left")
df = stata_multi_lag(df, "permno", "time_avail_m", "numest", [3])      # calendar-month lag 3, NaN if that month absent
df.loc[(numest < numest_l3) & numest_l3.notna(), "ChNAnalyst"] = 1
df.loc[(numest >= numest_l3) & numest.notna(), "ChNAnalyst"] = 0
df.loc[1987-07 <= time_avail_m <= 1987-09, "ChNAnalyst"] = NaN        # IBES data-quality months
df["tempqsize"] = groupby(time_avail_m)["mve_c"].transform(qcut(q=5, duplicates="drop") + 1)
df = df[df["tempqsize"] <= 2]
```
Note: the quintiles are over ALL SignalMasterTable firms that month (CRSP-wide), including firms with
no IBES record, so "bottom two quintiles" is of the full CRSP universe, not of covered firms.

## 4. Timing / lag convention

`time_avail_m` = month of `statpers` (last IBES summary date of the month, mid-month), no extra lag. The
3-month lag is a calendar lag; a missing month gives NaN. Not a fundamentals signal: ART-as-of-filing
and TTM smearing (`dimension=ARQ`) do not apply; no flow items.

## 5. Filters

In code: bottom two market-cap quintiles (see section 3); Jul-Sep 1987 set missing. SignalDoc
`Filter`: `abs(prc) > 5` (not in the code). Note: `Notes` say OP Table 2 shows t = 0.3 for all
stocks and t > 3 only for size quintiles 1-2, hence the size restriction. SignalDoc `Stock Weight`
VW, `Start Month` 12, `Portfolio Period` 1.

## 6. Predicted sign

SignalDoc `Sign` = -1 (a decline in coverage, value 1, predicts LOWER returns). OSAP orientation:
long the 0 group, short the 1 group; with a binary variable the harness's D10-D1 is degenerate (below).

## 7. Mass-point question

The signal has exactly two values, so the decile sort collapses to two tie groups. A do-nothing
firm (unchanged analyst count) scores 0, as does any firm whose count rose, so the 0 group is the
large majority of scored firm-months (not measurable here without IBES; expectation, not a
measurement: well over half, since counts are flat or rising over most 3-month windows). The
1 group is a minority. Every decile-based ranking would be a tie-rank; a 0/1 tie needs an explicit
two-bucket rule. Coverage is further limited to firms with IBES coverage (NaN, not 0, for
uncovered firms) and to the smallest two size quintiles, where coverage is sparsest.

## 8. History needed

OSAP sample 1982-2005; needs `numest` at t and t-3, so 3 months of history. IBES is unavailable in
the snapshot at every date, so the availability of history (snapshot starts 1998-01) is moot.

## 9. OSAP metadata

Acronym ChNAnalyst; Authors Scherbina; Year 2008; Journal ROF; Cat.Form discrete; Cat.Data Analyst;
Cat.Economic earnings event; sample 1982-2005; Sign -1; LS Quantile and Quantile Filter empty;
Test in OP: port sort FF3 alpha; Key Table in OP: 2 alphas return diff; Predictability in OP
1_clear; Signal Rep Quality 1_good. Legacy source `Signals/LegacyStataCode/Predictors/ChNAnalyst.do`.

## 10. Proposed Sharadar mappings

None: `numest` has no Sharadar counterpart. Only `mve_c` -> `DAILY.marketcap` (millions; `crsp.me`)
would map, and it is needed only for the size filter. No field not already in the map is involved
beyond the unmapped IBES fields. Recommend `infeasible` and record in `osap_frontier.yaml`.
