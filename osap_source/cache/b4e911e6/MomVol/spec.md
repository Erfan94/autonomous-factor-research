# MomVol — Momentum in high-volume stocks: Mom6m decile, kept only in the top 6-month-average-volume tercile (Lee and Swaminathan 2000, JF, Table 2 "J=6 K=3 V3 R10-R1")

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/MomVol.py` (cached `predictor.py`; upstream `upstream_SignalMasterTable.py`, `upstream_CRSPMonthly.py`, `upstream_asrol.py`, `upstream_stata_replication.py`). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`. Measurements: harness universe, schedule 1999-01 .. 2021-12 (276 decision months), recorded snapshot; 265 months are scorable (see 8).

## 1. Data availability (verdict: PREFLIGHT_FAILED — the data exist; the construction cannot reach the screen's coverage bar and is a categorical mass point)

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `ret` lags 1..5 (Mom6m) | `crsp.ret` | SEP `closeadj` endpoints t-1 / t-6 | mapped | `ret.fillna(0)`; NaN on a calendar gap |
| `vol` (monthly CRSP share volume) | `crsp.vol` | SEP `volume`, summed per calendar month | mapped, split-restated | `vol < 0 -> null`; rolling mean needs >= 5 of 6 months |
| obs number within permno (`_n < 24` dropped) | - | `ctx.has_price_at(23)` | approx | - |
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt; no SF1 input; no filing dates; no ART/ARQ question.
- SEP volume is split-RESTATED to today's basis (field_map `crsp.vol`, known trap `sep_volume_split_restated`): a cross-firm tercile of raw restated shares favours later splitters. As-traded share volume used here = `volume * close / closeunadj`. Not reproduced: CRSP's pre-2004 Nasdaq volume double counting (SEP is consolidated).
- SignalDoc text says "rolling average of the past 6 months of monthly turnover"; the pinned CODE averages raw share `vol` (no shares-outstanding divisor). The code is the authority; turnover would need DAILY.marketcap/close share counts and is a different signal.

## 2. Variables (exact source names)
`permno, time_avail_m, ret` (SignalMasterTable); `vol` (monthlyCRSP); derived `Mom6m`, `temp` (6-month mean vol), `catMom`, `catVol`, `MomVol`, `obs_num`.

## 3. Formula in words and key lines
Mom6m = (1+l1.ret)...(1+l5.ret) - 1 (five monthly returns t-5..t-1, despite the name). `temp` = mean of monthly `vol` over the six calendar months t-5..t (current month included), needs >= 5 non-missing. Each month, over ALL names: `catMom` = qcut(Mom6m, 10) and `catVol` = qcut(temp, 3) (independent sorts). Signal = `catMom` (1..10) where `catVol == 3`, else missing; also missing for the first 23 rows of a permno.
```
df_pd["catMom"] = groupby(time_avail_m)["Mom6m"].transform(qcut(q=10, duplicates="drop") + 1)
df_pd["catVol"] = groupby(time_avail_m)["temp"].transform(qcut(q=3,  duplicates="drop") + 1)
MomVol = catMom  if catVol == 3  else None ;  None if obs_num < 23
```
Harness form (measured): Mom6m = closeadj[t-1]/closeadj[t-6] - 1 (MomOffSeason idiom); monthly as-traded volume = sum of daily `volume*close/closeunadj` by calendar month (the 1997-12 one-day stub excluded, `ctx.partial_months`); `temp` = mean with >= 5 of 6 months; terciles and deciles formed WITHIN THE HARNESS UNIVERSE (not full CRSP); gate `has_price_at(23)`.

## 4. Timing / lag convention
Signal dated t (business month-end), month t volume included, held in month t+1. No filing dates, no flow items, no smear, ART irrelevant. Return-window factor: `history_months = 23` (equals `lookback_months` for the gate; the return/volume windows need only 6). `obs_num < 23` (0-indexed) drops a name's first 23 rows, i.e. needs >= 24 months of listing; approximated by a trade near BME(t-23).
Overlap with the v0 Momentum leg (closeadj[t-1]/closeadj[t-12]-1): Mom6m's window t-5..t-1 lies inside it; the top volume tercile is a subsample, not measured further.

## 5. Filters
SignalDoc Filter `abs(prc)>1, exchcd %in% c(1,2)` (paper sort); the predictor itself has no screen. Here: harness universe only (price >= $1 already in it).

## 6. Predicted sign
SignalDoc `Sign = 1.0` (HIGH momentum decile, within high volume, is the long leg; LS R10-R1); Return 1.55; T-Stat 5.78. Orientation: `ascending=True`.

## 7. The mass-point question (measured over the 265 scorable months)
The signal is a categorical 1..10 label, not a continuous value. There is no "do-nothing" value; instead every score is one of 10 labels.
- Distinct values: 10 in all 265 months. Modal share of the scored cross-section: min 11.0%, median 13.2%, mean 13.7%, max 21.4%; >= 10% in 265 of 265 months, >= 12% in 218, >= 15% in 56. The modal label is decile 1 in 184 months (losers concentrate in high-volume names), decile 10 in 25. Decile sizes (names), scorable months: smallest decile median 47 (min 22), largest median 81 (max 134).
- `qcut(rank(pct), 10, duplicates="drop")` returns 10 bins in 1 month, 9 in 170, 8 in 87, 7 in 7: fewer than ten in 264 of 265 months. preflight's hard rule (mode >= 10% or bins < 10) fails at both probe months that have a cross-section: middle probe 2010-06-30 mode label 1 at 13.4%, 8 bins; last probe 2021-11-30 mode label 4 at 12.2%, 10 bins (mode >= 10%). The first probe (1998-12-31) scores 0 names.
- Tie handling: a tie rule cannot fix it (the ties are the construction). The continuous variant (Mom6m restricted to the top volume tercile) was MEASURED, not proposed: modal share 0.13%-0.54% (median 0.17%), no mass point, but it is a different signal and does not cure coverage.

## 8. History needed and coverage (snapshot starts 1998-01, first close 1997-12-31)
- Leading null months: the gate needs a trade at BME(t-23) >= 1997-12-31, first satisfied at signal 1999-11-30; the 11 decision months 1999-01 .. 1999-11 are null. 265 scorable months (>= `rebalance.min_months` 120); not data_start.
- COVERAGE (the decisive number): names with a 5-of-6-month volume window 94.3%-99.9% of the universe; the top tercile is 31.5%-33.4% (by construction at most one third); after the history gate (median 94.1% pass) scored names are **26.5%-33.0% of the universe (median 32.2%, mean 31.6%) in every scorable month; 0 of 265 months reach the 40% Stage 1 coverage bar**. Scored n median 602 (max 773). No tercile definition can exceed 33.3%.
- Sensitivity (stated, verdict does not turn on it): top-tercile membership from raw split-restated volume instead of as-traded volume overlaps 79.9%-96.1% of names (mean 89.3%).

## 9. OSAP metadata
MomVol (Acronym2 MomVol); Lee and Swaminathan 2000 JF; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form discrete; Cat.Data Price; Cat.Economic momentum; Sample 1965-1995; Key Table "2 J=6 K=3 V3 R10-R1"; Test port sort; Sign 1.0; Return 1.55; T-Stat 5.78; EW; LS Quantile 0.2; Portfolio Period 3.0; Start Month 6.0; GScholar cites 2509. SignalDoc Notes "We use monthly instead of daily volume." Definition: "Define momentum as Mom6m, and volume as the rolling average of the past 6 months of monthly turnover (minimum 5 months). Independent sort stocks into 10 momentum ports and 3 volume ports. Keep if volume is in the top port, and assign signal = momentum port. Drop if less than 2 years on CRSP."

## 10. Proposed Sharadar mappings with deviations
```
Mom6m = closeadj(BME t-1) / closeadj(BME t-6) - 1 ; vol_m = sum over month of volume*close/closeunadj
temp = mean(vol_m, months t-5..t), >= 5 present ; catVol = qcut(temp, 3) ; catMom = qcut(Mom6m, 10) ; score = catMom if catVol==3 ; gate has_price_at(23)
```
Deviations: universe-relative terciles/deciles; as-traded volume; obs_num approximated; first 11 decision months null; no delisting return; no CRSP volume double count. Fields not in the map: none.
Recommendation: **preflight_failed** (frontier row): coverage 26.5%-33.0% in all 265 scorable months (structural ceiling 33.3% < 40%); categorical mass point, modal 11.0%-21.4%, qcut < 10 bins in 264 of 265 months. Not `infeasible` (data exist) and not `data_start`.
