# AnalystValue (Frankel-Lee analyst-forecast intrinsic value / price) — spec, Phase A fetch batch 02

Ref b4e911e69678a7424f318617a61d813f54183123. There is no `AnalystValue.py`; the tree has only
`Signals/pyCode/Predictors/ZZ1_AnalystValue_AOP_PredictedFE_IntrinsicValue.py` (grep of tree.txt), which
emits AnalystValue, AOP, PredictedFE and the placebo IntrinsicValue. Cached `predictor.py` is that script.
SignalDoc row: Acronym AnalystValue, Cat.Signal Predictor (cached `signaldoc_row.csv`).
Upstream inputs named in the script: SignalMasterTable, IBES_EPS_Unadj, monthlyCRSP, m_aCompustat.

## 1. Data availability — VERDICT: INFEASIBLE (recommend `infeasible`)

The numerator is a 3-stage residual-income valuation driven by IBES consensus: `feps1` (FY1 mean EPS,
fpi=1, May statpers), `feps2` (FY2 mean EPS, fpi=2) and `LTG` (long-term growth, fpi=0). This snapshot
has no estimates table (task: no IBES, no options; `osap_source/api_schema/` lists ACTIONS, DAILY,
DESCRIPTIONS, EVENTS, FUNDAMENTALS/SF1, FUNDS, HOLDINGS, INSIDERS, METRICS, SP500, STOCKS/SEP, TICKERS).
`field_map_index.yaml` has no IBES/forecast key (grep "ibes": no match). Not zero-fillable: the script's
screen requires `feps1.is_not_null() & feps2.is_not_null()` (rows lacking forecasts are DROPPED, not
filled with 0); `zero_fill_vars` is not involved. A reported-EPS proxy for feps1/feps2 would change the
construct (AnalystValue collapses toward the IntrinsicValue placebo, a function of trailing ROE only). No "approx".

| input | source | map key | status |
|---|---|---|---|
| feps1, feps2, LTG (IBES meanest) | none | none (not in field_map) | UNAVAILABLE |
| tickerIBES (SignalMasterTable link) | none | none (not in field_map) | UNAVAILABLE |
| ceq | SF1.equity | compustat.ceq | approx (no preferred split) |
| ibcom | SF1.netinccmn | compustat.ibcom | mapped |
| dvc | SF1.ncfdiv (outflow; negate) | compustat.dvc | approx |
| at | SF1.assets | compustat.at | mapped |
| sale (SG, used only by PredictedFE) | SF1.revenue | compustat.sale | mapped |
| datadate | SF1.calendardate | compustat.datadate | mapped |
| shrout | DAILY.marketcap*1e6/SEP.close or SF1.sharesbas | crsp.shrout | approx |
| prc | SEP.closeunadj | crsp.prc | mapped |
| mve_permco | DAILY.marketcap (company-level) | crsp.mve_permco | approx |
Status strings are from `field_map_index.yaml` as reset; none is treated as verified on THIS snapshot.
The non-IBES rows are irrelevant to the verdict; the field-checker need not run.

## 2. Variables (exact source names)
feps1, feps2, LTG (IBES); permno, tickerIBES, time_avail_m, prc (SignalMasterTable); shrout (monthlyCRSP);
ceq, ib, ibcom, ni, sale, datadate, dvc, at (m_aCompustat; ib/ni loaded, only ceq, ibcom, dvc, at, sale, datadate used).

## 3. Formula
June observations only (`time_avail_m.month == 6`). Annual signal.
- ceq_ave = (ceq + prior-June ceq)/2; ceq alone for a firm's first row or if the prior June is missing.
- mve_permco = shrout*|prc|; k = dvc/(0.06*at) if ibcom < 0 else dvc/ibcom; ROE = ibcom/ceq_ave.
- FROE1 = feps1*shrout/ceq_ave; ceq1 = ceq*(1+FROE1*(1-k)).
- FROE2 = feps2*shrout/((ceq1+ceq)/2); ceq2 = ceq1*(1+FROE1*(1-k)).
- FROE3 = FROE2 if LTG null else feps2*(1+LTG/100)*shrout/((ceq1+ceq2)/2); ceq3 = ceq2*(1+FROE2*(1-k)).
- r = 0.12 (constant; a literal in the script).
- AnalystValue = [ceq1 + (FROE1-r)/(1+r)*ceq1 + (FROE2-r)/(1+r)^2*ceq2 + (FROE3-r)/(1+r)^2/r*ceq3] / mve_permco
Key line: `(av_term1+av_term2+av_term3+av_term4) / mve_permco  -> AnalystValue`.
Unit note: feps*shrout/ceq needs shrout and ceq on one scale (OSAP's intermediates set this); a port must state it.
Note the script's own oddities: ceq2 uses FROE1 (not FROE2) and the year-3 term divides by (1+r)^2; port as written.

## 4. Timing / lag
Each June row is copied to time_avail_m+0..+11 (held 12 months). IBES May consensus gets a +1 month
shift (usable in June). Accounting data are OSAP's m_aCompustat (6-month-lagged availability); the
`datadate.month >= 6` screen keeps only fiscal years ending June-December. ART-as-of-filing would replace
the 6-month lag with the filing date (earlier, not identical). Flow items (ibcom, dvc, sale) are annual
in OSAP; ART TTM serves them, no ARQ year-over-year difference is formed, so no TTM smear; dvc via ncfdiv is
cash-flow based (approx). SG = sale / sale.shift(60 months), a 5-year ratio taken on the monthly panel
BEFORE the June filter; used only by PredictedFE, not by AnalystValue.

## 5. Filters
ceq > 0 and not null; |ROE| <= 1 (null allowed); |FROE1| <= 1 (null allowed); k <= 1 (null allowed);
datadate month >= 6; feps1 and feps2 not null. SignalDoc Filter: `abs(prc) > 1`. No OSAP size screen.

## 6. Predicted sign
SignalDoc Sign = +1.0 (high analyst value / price -> high return). Long-short quantile 0.2, equal weight,
Portfolio Period 12, Start Month 6. Orientation is OSAP's published sign.

## 7. Mass-point question
Continuous ratio; a do-nothing firm (stale ceq, zero dividend: k=0) still yields a unique value through its
own forecasts and price, so no structural point mass and ~0% exact ties. The issue is coverage and cohort
structure: only firms with both IBES FY1 and FY2 forecasts survive (roughly half of the CRSP/Compustat
universe in OSAP's recent years) and the value changes only once a year, so within-year churn is nil
(month-to-month turnover arises only from universe entry/exit). Ties: average rank.

## 8. History needed
Prior-June ceq (1 year); SG would need 60 months (PredictedFE only). IBES from ~1976 in OSAP. Sharadar SF1
from 1997Q4 would supply the accounting side (first usable June is 1999 against the 1998-01 snapshot start),
but the IBES side does not exist on this snapshot in any year.

## 9. OSAP metadata
Acronym AnalystValue; Frankel and Lee 1998 JAE; Cat.Form continuous; Cat.Data Analyst; Cat.Economic valuation;
Predictability in OP 2_likely; replication quality 2_fair; sample 1975-1993; evidence "p<0.01 in port sort
but nonstandard stats", Key Table 3D Ret12; Stock weight EW; GScholar cites 1739. Notes: "Usually called V_f/P
or V_f in OP." Detailed Definition: value based on a three-stage dividend discount model and analyst forecasts,
scaled by market value. Siblings from the same script: AOP, PredictedFE (same IBES dependency) and placebo
IntrinsicValue (IBES-free, not a predictor).

## 10. Proposed Sharadar mappings
No constructible mapping for the IBES legs (feps1, feps2, LTG, tickerIBES: not in field_map). Non-IBES legs
map per the section 1 table, deviations: ceq = equity includes preferred; dvc = negated ncfdiv (cash-flow,
minor preferred included); shrout via DAILY.marketcap/SEP.close on today's split basis or sharesbas;
datadate = calendardate (report period, not the 6-month-lag availability).
Recommended osap_frontier row: `infeasible`, reason "requires IBES analyst forecasts (feps1, feps2, LTG); no
Sharadar table carries estimates; the script drops missing forecasts (no zero-fill)".
