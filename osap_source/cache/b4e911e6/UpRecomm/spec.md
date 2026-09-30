# UpRecomm — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: DATA_UNAVAILABLE (recommend `infeasible`)
| OSAP input | source | Sharadar | status |
|---|---|---|---|
| `ireccd` (recommendation code), `amaskcd` (analyst id), `anndats` | `IBES_Recommendations` | none | unavailable |
| `tickerIBES` | `SignalMasterTable` (IBES-CRSP link) | none | unavailable |
- Checked on THIS snapshot: the 13 held tables are ACTIONS, DAILY, DESCRIPTIONS, EVENTS, METRICS, SEP, SF1, SF2, SF3, SF3A, SF3B, SP500, TICKERS. No column of any of them matches recommend / rating / analyst / estimate / forecast / target / ibes (only SF1 `eps`, `epsdil`, `epsusd`, `receivables`, which are reported results, not analyst opinions). `field_map_index.yaml` has no entry for `ireccd`, `amaskcd`, `anndats`, `tickerIBES`.
- The signal is a month-over-month change in the cross-analyst mean IBES recommendation code. Nothing else enters: no optional or zero-filled term (OSAP's only fill is structural, see section 7), so dropping an input leaves nothing. SF3/SF3A/SF3B (13F holdings, 2013-06+) and SF2 (insider trades) are not analyst opinions; no proxy.

## 2. Variables (predictor.py)
`IBES_Recommendations`: tickerIBES, amaskcd, anndats, time_avail_m, ireccd. `SignalMasterTable`: permno, tickerIBES, time_avail_m. No upstream file is cached for this acronym (none needed; the IBES download is outside the Sharadar scope).

## 3. Formula in words and key lines
Per analyst and month take the last recommendation code; average across analysts within (tickerIBES, month); flag 1 when this month's mean code is below last row's mean code (IBES: 1 = strong buy .. 5 = sell, so LOWER = better = an upgrade).
```
df = df.groupby(["tickerIBES","amaskcd","time_avail_m"])["ireccd"].last()
df = df.groupby(["tickerIBES","time_avail_m"])["ireccd"].mean()
df["ireccd_lag"] = df.groupby("tickerIBES")["ireccd"].shift(1)        # row-based, not calendar-based
UpRecomm = ((ireccd < ireccd_lag) & ireccd_lag.notna()).astype(int)
df = df.merge(SignalMasterTable, on=["tickerIBES","time_avail_m"], how="inner")
```
Code vs SignalDoc text: they disagree. SignalDoc `Detailed Definition` says "binary variable equal to 1 if mean earnings forecast (meanest) decreased over the past month" (keep fpi = 1) and its Notes say OSAP measures forecast changes where the paper studies recommendation changes; the code is a recommendation UPGRADE flag. Code is the authority for construction. Moot given the verdict.

## 4. Timing / lag convention
OSAP: month-of-announcement IBES aggregates, stamped `time_avail_m`, signal at t used for t+1 (Portfolio Period 1, Start Month 12). Not constructible here, so no harness timing and no ART-as-of-filing question; no flow items.

## 5. Filters
None in SignalDoc (Filter blank). Rows exist only for IBES-covered names (inner join), so a name without coverage is NaN, not 0.

## 6. Predicted sign
SignalDoc `Sign = +1.0` (Barber, Lehavy, McNichols, Trueman 2001 JF, Table 3C, upgrades earn higher returns; event-study t > 8 in a 3-day window; the OSAP monthly portfolio form is nonstandard). Would be `ascending=True`.

## 7. The mass-point question
A do-nothing covered name (mean code unchanged or worse, or no lagged row) = 0. A binary flag: two values at most. The zero mass is the majority of covered names in any month (an upgrade in the mean is a minority event), far above the preflight 10% cliff, and `qcut` yields 2 bins, so even with data it would hard-fail preflight unless redesigned. NOTE that the first row of a name and any name without a lag row gets 0 (the `.astype(int)` turns the NaN comparison into 0), a structural fill; uncovered names are absent (NaN). Not measurable on the snapshot: no data, 0 constructible months.

## 8. History needed (snapshot starts 1998-01)
IBES recommendation history (OSAP sample 1985-1997; the harness window starts 1999-01). Sharadar has none. Usable decision months: **0** of 276 (the 276-month schedule is 1998-12-31 .. 2021-11-30 signals). rebalance.min_months 120 is unreachable.

## 9. OSAP metadata
UpRecomm; Barber, Lehavy, McNichols, Trueman; 2001; Journal of Finance; Predictability in OP `2_likely`; Signal Rep Quality `4_lack_data`; Cat.Signal Predictor; Cat.Form discrete; Cat.Data Analyst; Cat.Economic earnings forecast; Test "event study 3 day nonstandard data"; Key Table "3C, 1 to 2, 2 to 3, etc"; Sample 1985-1997; Sign +1.0; EW; Portfolio Period 1; Start Month 12; Filter blank; GScholar cites 1860. Source `Signals/pyCode/Predictors/UpRecomm.py`.

## 10. Proposed Sharadar mappings
None. Recommend `infeasible` (class data_unavailable): the sole input is an analyst-recommendation vendor table Sharadar does not publish, and OSAP does not zero-fill it.
