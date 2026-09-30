# AOP (Analyst Optimism) — spec, Phase A fetch batch 01

Ref b4e911e69678a7424f318617a61d813f54183123. Source: `Signals/pyCode/Predictors/ZZ1_AnalystValue_AOP_PredictedFE_IntrinsicValue.py`
(no `AOP.py` exists; the tree has only this ZZ1 script, which emits AnalystValue, AOP, PredictedFE and the placebo IntrinsicValue).
SignalDoc row: Acronym AOP, Cat.Signal Predictor (cached `signaldoc_row.csv`). Cached `predictor.py` is that ZZ1 script.

## 1. Data availability — VERDICT: INFEASIBLE (recommend `infeasible`)

AOP = (AnalystValue - IntrinsicValue) / |IntrinsicValue|. AnalystValue is built from IBES analyst
consensus: `feps1` (FY1 mean EPS forecast), `feps2` (FY2 mean EPS forecast) and `LTG` (long-term
growth forecast). Sharadar holds no analyst-estimate table: `osap_source/api_schema/` lists only
ACTIONS, DAILY, DESCRIPTIONS, EVENTS, FUNDAMENTALS (SF1), FUNDS, HOLDINGS, INSIDERS, METRICS, SP500,
STOCKS (SEP), TICKERS; `field_map_index.yaml` has no IBES/forecast key (grep: no match for
ibes, meanest, feps, analyst, LTG, forecast, estimate). The signal is not zero-fillable:
the script's screen is `feps1.is_not_null() & feps2.is_not_null()`, so every firm-year without IBES
forecasts is DROPPED, not zero-filled. No reported-EPS proxy stands in for a forecast without
changing the construct (AOP then reduces to a function of historical ROE only). No "approx".
Only the placebo leg IntrinsicValue is constructible (no IBES), and it is not the predictor.

| input | source field | map key | status |
|---|---|---|---|
| feps1, feps2, LTG (IBES meanest, fpi 1/2/0, May statpers) | none | none | UNAVAILABLE (IBES) |
| tickerIBES link | none | none | UNAVAILABLE |
| ceq | SF1.equity | compustat.ceq | approx in index (no preferred split) |
| ibcom | SF1.netinccmn | compustat.ibcom | mapped |
| dvc | SF1.ncfdiv (sign: outflow, negate) | compustat.dvc | approx |
| at | SF1.assets | compustat.at | mapped |
| sale (only for SG, used by PredictedFE, not AOP) | SF1.revenue | compustat.sale | mapped |
| datadate | SF1.calendardate (reportperiod) | compustat.datadate | mapped |
| shrout | DAILY.marketcap*1e6/SEP.close or SF1.sharesbas | crsp.shrout | approx |
| prc | SEP.closeunadj | crsp.prc | mapped |
| mve_permco | DAILY.marketcap | crsp.mve_permco | approx |
| tickerIBES (SignalMasterTable) | none | none | UNAVAILABLE |

Field-checker need only verify the non-IBES rows if the loop overrides the verdict (it should not).

## 2. Variables (source names)
feps1, feps2, LTG (IBES); permno, tickerIBES, prc, shrout (CRSP/SMT); ceq, ibcom, dvc, at, sale, datadate
(m_aCompustat, 12-month-lagged-availability panel).

## 3. Formula
Per firm, June observations only (time_avail_m month == 6):
- ceq_ave = (ceq + prior-June ceq)/2; ceq if first obs or prior missing.
- mve = shrout*|prc|; k = dvc/(0.06*at) if ibcom<0 else dvc/ibcom; ROE = ibcom/ceq_ave.
- FROE1 = feps1*shrout/ceq_ave; ceq1 = ceq*(1+FROE1*(1-k)); ceq1h = ceq*(1+ROE*(1-k)).
- FROE2 = feps2*shrout/((ceq1+ceq)/2); ceq2 = ceq1*(1+FROE1*(1-k)); ceq2h = ceq1h*(1+ROE*(1-k)).
- FROE3 = FROE2 if LTG null else feps2*(1+LTG/100)*shrout/((ceq1+ceq2)/2); ceq3 = ceq2*(1+FROE2*(1-k)).
- r = 0.12 constant.
- AnalystValue = [ceq1 + (FROE1-r)/(1+r)*ceq1 + (FROE2-r)/(1+r)^2*ceq2 + (FROE3-r)/(1+r)^2/r*ceq3] / mve
- IntrinsicValue = [ceq1h + (ROE-r)/(1+r)*ceq1h + (ROE-r)/(1+r)/r*ceq2h] / mve
- AOP = (AnalystValue - IntrinsicValue)/|IntrinsicValue|.
Key lines: `df.with_columns(((AnalystValue - IntrinsicValue)/IntrinsicValue.abs()).alias("AOP"))`.
Unit note: feps1*shrout/ceq assumes shrout and ceq share a scale; OSAP intermediate files set this
(CRSP shrout is thousands, Compustat ceq millions); any port must state one scale.

## 4. Timing / lag
Annual signal held 12 months: each June row is copied to time_avail_m+0..+11. IBES forecasts are
May statpers with an extra +1 month (available June). Accounting data are OSAP's 6-month-lagged
m_aCompustat; screen `datadate.month >= 6` keeps fiscal years ending June-Dec only (a peculiar
subset; Jan-May FYEs are dropped). ART-as-of-filing would replace the OSAP 6-month lag with the
filing date (earlier availability, hence not identical). No quarterly-flow smear: ibcom and dvc are
annual flows, ART TTM would serve, but dvc via ncfdiv is cash-flow based (approx).

## 5. Filters (applied to the June cross-section)
ceq>0 and not null; |ROE|<=1 (null allowed); |FROE1|<=1 (null allowed); k<=1 (null allowed);
datadate month>=6; feps1 and feps2 not null. SignalDoc filter: abs(prc)>1. OSAP rolls no size screen.

## 6. Predicted sign
SignalDoc Sign = -1.0 (high analyst optimism -> low subsequent return). LS quantile 0.2, EW,
6-month start month, 12-month holding period. Orientation is OSAP's published sign.

## 7. Mass-point question
AOP is a continuous ratio; a do-nothing firm (ROE and forecast leg unchanged) produces no
structural point mass. Share of exact ties expected ~0; only k capped by zero dividends (k=0) creates
coincident terms but not coincident AOP. Non-coverage is the issue: only firms with IBES FY1, FY2
forecasts survive (roughly 40-60% of the Compustat/CRSP universe by count in OSAP, recent years),
and the signal exists only for June-formed annual cohorts. Ties: rank average.

## 8. History needed
Needs prior-June ceq (1 year) and IBES from ~1976; Sharadar SF1 from 1997Q4 would supply accounting,
but IBES would not exist in any case. Snapshot starts 1998-01, first June 1999.

## 9. OSAP metadata
Acronym AOP; Frankel and Lee 1998 JAE; Cat.Form continuous; Cat.Data Analyst; Cat.Economic other;
Predictability in OP 2_likely; replication quality 2_fair; sample 1975-1993; evidence p<0.01 in port
sort, nonstandard stats (Table 5C OP Ret36); Stock weight EW; Notes: "Called OP (optimism) in
paper. See AnalystValue."; GScholar cites 1739. Sibling emissions from the same script:
AnalystValue, PredictedFE (same IBES dependency) and the placebo IntrinsicValue.

## 10. Proposed Sharadar mappings
No constructible mapping. Non-IBES legs map per table in section 1 (deviations: ceq=equity incl.
preferred; dvc=negated ncfdiv incl. minor preferred; shrout via DAILY.marketcap/SEP.close on today's
split basis, sharesbas-vs-CRSP-shrout approx). Not in field_map: IBES feps1/feps2/LTG, tickerIBES.
Recommended registry row: osap_frontier `infeasible`, reason "requires IBES analyst forecasts
(feps1, feps2, LTG); no Sharadar table carries estimates; screen drops missing forecasts (no zero-fill)".
