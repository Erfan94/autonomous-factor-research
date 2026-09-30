# NumEarnIncrease — Earnings streak length: number of consecutive quarterly year-over-year increases in ibq, up to 8 (Loh and Warachka 2012, Table 4)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/NumEarnIncrease.py` (cached `predictor.py`; upstream `upstream_CompustatQuarterly.py`, `upstream_SignalMasterTable.py` beside it). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`. Measurements: harness universe, 276 decision months (signals 1998-12-31 .. 2021-11-30), recorded snapshot, scratch measurement (no factor file).

## 1. Data availability (verdict: PREFLIGHT_FAILED, mass point by construction; inputs are available, recommend frontier, do not translate)

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `ibq` income before extraordinary items, quarterly | `compustat.ibq` | `SF1.netinccmn`, dimension ARQ (single-quarter flow) | mapped (index); `ib` is remapped to `netinc + netincdis` | not zero-filled (`ibq` is not in the quarterly zero-fill list) |
| `gvkey`/`permno` link, `time_avail_m` | `crsp.smt_row` | harness universe | approx | inner merge |
- `SF1.eps` is NOT involved (OSAP uses `ibq`, not `epspxq`). No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt. The field is available: the verdict comes from the construction, not from data.
- Measured mass point (streak computed exactly as OSAP, on ARQ quarters aligned by reportperiod, `netinccmn`; the same result with `netinc + netincdis`): the value is an integer 0..8, so exactly 9 distinct values in every one of the 276 months. The modal value is 0 in every month: share of scored 34.9% (2010-08-31) to 84.6%, median 52.1%; steady state (2004-2021) median 51.6%, max 70.3%. Probe months (first / middle / last of the schedule, as preflight reads them): 1998-12-31 mode 84.3%, qcut yields 2 bins; 2010-06-30 mode 37.5%, 5 bins; 2021-11-30 mode 44.4%, 6 bins (bins derived from the measured value distribution by `pd.qcut(rank(pct), 10, duplicates="drop")`). Above the 10% cliff in 276 of 276 months; fewer than 10 bins is guaranteed by nine values.
- Scored share of the universe 95.8-99.9% (median 99.3%): coverage is not the problem.
- Nulling the zeros does not rescue it: the next value alone is large (value 1: median 15.0%, 2004+ median 15.5%; values 2..8 fall 9.5%, 6.7%, 5.3%, 3.5%, 2.4%, 1.7%, 1.2% at the median month), so a tie block still spans decile boundaries. Same class as EarnSupBig / MS / MomRev. OSAP's own sort (LS Quantile 0.2, quintiles) sits on the same ties: this is not a Sharadar artefact.
- Recommended frontier reason: "mass point by construction: integer signal 0..8 (9 distinct values); the modal value 0 holds 34.9-84.6% of the scored cross-section (median 52.1%) in all 276 months (steady-state median 51.6%), qcut 2 / 5 / 6 bins at the 1998-12 / 2010-06 / 2021-11 probes; no tie handling exists without replacing the signal".

## 2. Variables (exact source names)
`permno, gvkey, time_avail_m, ibq`; derived `l12_ibq`, `chearn`, `l3_chearn .. l24_chearn` (step 3), `nincr`, `NumEarnIncrease`.

## 3. Formula in words and key lines
`chearn` = current quarterly earnings minus the same quarter a year earlier. The signal is the number of consecutive quarters, ending now, with `chearn > 0`, counted back until a quarter with `chearn <= 0` is hit, capped at 8.
```
chearn = ibq - l12_ibq                                       # calendar 12-month lag inside the monthly-expanded panel
nincr = 0; for n in 1..8 (later n overwrite): nincr = n if chearn, l3_chearn, .., l(3(n-1))_chearn are each (> 0 or NaN) and l(3n)_chearn <= 0
NumEarnIncrease = nincr
```
Quirks that define the mass point, all in OSAP's own code: (i) 0 is overloaded: a current decline (`chearn <= 0`: median 37.3% of scored over 1999-2021, 39.0% in 2004+), an unbroken streak of nine or more increases (no catch-all rule: a streak with no terminator within the 9 quarters stays 0), and a history never terminated by a known `<= 0` (missing is treated as positive but `NaN <= 0` is False, so the chain never stops and the value stays 0). Zeros with `chearn > 0`: median 8.9% of scored (7.4% in 2004+), 2-35% across months (high in 1998-2001 where 13 quarters of ARQ history do not yet exist: full 13-quarter history for 13% of the universe at 1998-12, 41% at 2000-12, 88% from 2003-12); zeros with `chearn` NaN: median 2.9%. (ii) A MISSING `chearn` counts as positive inside the chain. (iii) Exact `chearn == 0` is rare (0.0-0.32% of scored).
SignalDoc-vs-code: Definition "Number of consecutive 4-quarter increases in ibq, up to 8" (Detailed: same); the code is as above.

## 4. Timing / lag convention
OSAP: quarterly data at datadate + 3 months (or the RDQ month if later), carried forward up to 3 months; 3-month lags of `chearn` therefore step one quarter back. Sharadar: ARQ history by reportperiod (`ctx.fundamentals_history(["netinccmn"], n_periods=13, dimension="ARQ")`, aligned at 3-month steps), available from `datekey` (about 45 days after quarter end, so 1-2 months earlier than OSAP's +3 months). The yoy difference is taken between two single-quarter ARQ flows (ARQ is a genuine single-quarter flow: ART == exact rolling four-quarter sum of ARQ), so nothing smears under TTM, but `FactorDef.dimension = "ARQ"` would be REQUIRED for any translation; under the ART default the yoy difference of TTM sums would be a different signal. History: 13 quarters of ibq (chearn at lag 24 needs ibq at lag 36 months).

## 5. Filters
Predictor: none beyond the `gvkey` link and the quarterly merge. SignalDoc Filter `abs(prc)>5` is a portfolio filter, not in `predictor.py`. Here: harness universe.

## 6. Predicted sign
SignalDoc `Sign = 1.0` (longer earnings-increase streak -> higher returns). Orientation `ascending=True`.

## 7. The mass-point question
A do-nothing firm (flat or declining quarterly earnings) gives 0; 34.9-84.6% of the scored cross-section sits there (median 52.1%), 9 distinct values, ten bins impossible. Not repairable by nulling the zeros (value 1 holds about 15%); any tie handling would replace the signal. Hard preflight fail at every probe month (mode >= 10% and qcut < 10 bins).

## 8. History needed (snapshot starts 1998-01)
ARQ history of 13 quarters; SF1 ARQ is thin before 1998 (datekeys from 1993, sparse). Even with all cross-sections scored (95.8-99.9%), the early months are dominated by the non-terminated-chain zero (84.3% at 1998-12). Not the decisive reason: the mass point holds in steady state (2004-2021 median 51.6%).

## 9. OSAP metadata
NumEarnIncrease; Loh and Warachka 2012 (Management Science); Cat.Signal Predictor; Cat.Economic earnings growth; Sample 1987-2009; Sign 1.0; EW; LS Quantile 0.2; Portfolio Period 1.0; Start Month 12.0; Filter `abs(prc)>5`. LongDescription "Earnings streak length". SignalDoc Notes: signal is not exactly in Loh and Warachka (Table 4 suggests it would predict returns); GHZ have it (citing Barth, Elliott and Finn 1999).

## 10. Proposed Sharadar mappings with deviations (for reference only; recommendation is NOT to translate)
```
h = ctx.fundamentals_history(["netinccmn"], n_periods=13, dimension="ARQ")    # align by reportperiod in 3-month steps, +-1 month
chearn_k = e_k - e_{k+4}, k = 0..8 ; streak rule as in section 3, NaN = positive in the chain, NaN <= 0 False
FactorDef(dimension="ARQ", ascending=True, lookback_months=39)
```
Deviations: `ibq` -> `netinccmn` (after preferred dividends, includes discontinued items; `netinc + netincdis` measured, the same mass-point result); quarters aligned by reportperiod, not 3-month calendar lags; filing-date availability rather than datadate + 3 months.
Fields not in the map: none.
Recommendation: preflight_failed (mass point by construction; frontier row). Do not translate.
