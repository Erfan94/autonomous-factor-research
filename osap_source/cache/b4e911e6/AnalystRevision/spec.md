# AnalystRevision — EPS forecast revision (Hawkins, Chamberlin and Daniel 1984, Table 10, mean)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/AnalystRevision.py` (cached
`predictor.py`, `signaldoc_row.csv`, `upstream_IBESEPSUnadjusted.py`, `upstream_IBESCRSPLink.py`).
DATA_SHA 198b281de1a0. SignalDoc row (Cat.Signal == Predictor): Cat.Data = Analyst,
Cat.Economic = earnings forecast.

## 1. Data availability (verdict: INFEASIBLE — recommend `infeasible`)

The only signal input is the IBES consensus mean EPS estimate. This snapshot holds no IBES and no
analyst-estimate table (13 tables: SF1, SEP, DAILY, ACTIONS, SF2, SF3/SF3A, EVENTS, TICKERS, ...;
none carries forecasts). No Compustat item is involved, so there is no OSAP zero-fill that could
rescue it, and no proxy is faithful (a time-series change in realised EPS is a different signal).

| input (OSAP) | field_map key | Sharadar | status | note |
|---|---|---|---|---|
| `meanest` (IBES `statsumu_epsus`, fpi = "1", last statpers in month) | none (no `ibes.*` key in `field_map_index.yaml`; grep for ibes/meanest/analyst finds nothing) | none | unavailable | analyst data; not published by Sharadar |
| `tickerIBES` (SignalMasterTable, IBES-CRSP link, `IBESCRSPLink.py` score-filtered) | none | none | unavailable | link table WRDS-only; only needed to reach `meanest` |
| `permno`, `time_avail_m` (SignalMasterTable panel rows) | `crsp.smt_row` | SEP presence, `has_price_at(m, 31)` | mapped (status reset; unverified here) | harness-side only; irrelevant to the verdict |

Nothing further to field-check: the blocking input has no mapping to check. Do not translate; log a
`osap_frontier.yaml` row with reason "IBES consensus EPS forecasts (analyst data) — not in Sharadar
snapshot; no OSAP zero-fill; no estimates table" and do not preflight.

## 2. Variables (exact source names)

`meanest` (mean of analyst 1-year-ahead EPS forecasts, unadjusted for splits), `fpi` (forecast period
indicator; only `"1"` kept), `statpers` (-> `time_avail_m`, month of the statistical period),
`tickerIBES`, `permno`, `time_avail_m`. Columns `numest`, `medest`, `stdev`, `fpedats` are
downloaded but unused.

## 3. Formula

Ratio of this month's consensus FY1 EPS forecast to last month's. Key lines:
```
ibes_df = ibes_df[ibes_df["fpi"] == "1"]                      # 1-year-ahead forecast only
df = SignalMasterTable[["permno","tickerIBES","time_avail_m"]].merge(ibes_df[["tickerIBES","time_avail_m","meanest"]], how="left")
df = df.sort_values(["permno","time_avail_m"])
df["l_meanest"] = df.groupby("permno")["meanest"].shift(1)    # row shift, NOT calendar-month lag
df["AnalystRevision"] = df["meanest"] / df["l_meanest"]
```
No winsorising, no sign guard: a zero or negative `l_meanest` gives inf / sign-flipped ratios
(a loss-making firm whose loss deepens gets a positive ratio). Faithful translation (if data ever
existed) would need to decide how to treat those; OSAP does not.

## 4. Timing / lag convention

`time_avail_m` = month of `statpers`; in `upstream_IBESEPSUnadjusted.py` the last `statpers` of the
month is kept (`drop_duplicates(..., keep="last")`), so the forecast is the mid-month IBES summary
date (third Thursday), available within the month, no extra lag. Shift(1) is a ROW shift on the
panel sorted by permno: if the previous month is missing the ratio uses the last SignalMasterTable
row, which is the preceding calendar month only when the panel is gap-free. Not a fundamentals
signal: ART-as-of-filing and TTM smearing (`dimension=ARQ`) do not apply; no flow items.

## 5. Filters

None in code. SignalDoc `Filter` is empty; `Quantile Filter` empty. Notes: OP longs only the top 20
stocks; OSAP uses full quintiles (`LS Quantile` 0.2), EW, start month 1, portfolio period 1.

## 6. Predicted sign

SignalDoc `Sign` = +1 (upward revisions -> higher returns; long the high ratio).

## 7. The mass-point question

A firm with an unchanged consensus (meanest == l_meanest) yields exactly 1.0; a firm without IBES
coverage or without a prior-month forecast yields NaN (dropped). Consensus means of a small analyst
set are often unchanged month to month, so a material mass point at 1.0 is expected (share not
measurable here — no data); ties at 1.0 would be broken by rank averaging. Moot under infeasibility.

## 8. History needed

OSAP: 1 prior month of consensus. The original sample is 1975–1980, IBES coverage from 1976 (the
summary file is sparse before ~1984). The snapshot starts 1998-01, so history is not the problem;
the missing data is.

## 9. OSAP metadata

Acronym AnalystRevision; authors Hawkins, Chamberlin, Daniel 1984 (FAJ); Predictability in OP
1_clear; Signal Rep Quality 2_fair; Cat.Form continuous; Cat.Data Analyst; Cat.Economic earnings
forecast; Sample 1975–1980; evidence "t=3.2 in long only CAPM alpha" (Table 10 mean); Stock Weight
EW; LS Quantile 0.2; Start Month 1.0; Portfolio Period 1.0. Detailed definition: "keep fpi == 1, last
obs each month. Signal is meanest / last month's meanest." Legacy file `AnalystRevision.do` also exists.

## 10. Proposed Sharadar mappings

None. `meanest` and the IBES-CRSP link have no Sharadar counterpart; no field_map key exists
(no entry to flag "not in the map" beyond the two rows in section 1). Recommendation: `infeasible`
(analyst data unavailable, no zero-fill), a frontier row, no factor file.
