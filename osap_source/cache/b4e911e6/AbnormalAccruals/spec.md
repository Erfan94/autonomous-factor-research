# AbnormalAccruals — spec (Phase A, fetch batch 01)

Ref b4e911e69678a7424f318617a61d813f54183123. Source: Signals/pyCode/Predictors/ZZ2_AbnormalAccruals_AbnormalAccrualsPercent.py
(no `AbnormalAccruals.py`; ZZ2 script emits both the predictor AbnormalAccruals and the placebo AbnormalAccrualsPercent).
SignalDoc row: Acronym=AbnormalAccruals, Cat.Signal=Predictor, Cat.Economic=accruals, Xie 2001 (AR), Cat.Form continuous, Cat.Data Accounting.

## 1. Data availability — verdict: INFEASIBLE (ppegt)

- `compustat.ppegt` is **unavailable** in field_map_index.yaml (no SF1 field; Sharadar publishes only ppnenet = net PP&E).
  OSAP does NOT zero-fill ppegt (upstream_CompustatAnnual.py `zero_fill_vars` = nopi dvt ob dm dc aco ap intan ao lco lo rect
  invt drc spi gdwl che dp act lct tstkp dvpa scstkc sstk mib txditc ivst; ppegt absent), so the "zero-fill -> approx" exception does not apply.
- ppegt is a regressor (`tempPPE = ppegt / l1_at`) in the per-(fyear, sic2) cross-sectional regression whose residual IS the signal.
  Dropping or replacing it changes the residual for every firm; it is not an optional additive term.
- Recommendation: `infeasible`. Only route around it: ppnenet (`compustat.ppent`, mapped) as a net-for-gross substitute = a different
  regressor (net vs gross PP&E; Sharadar ppnenet exact-zero 5.9% overall, 11.8% in 2021-26, missing indistinguishable from 0). That would be
  an `approx` with a logged construction choice; it is NOT recommended without an explicit decision from the caller.
- Other inputs (all would otherwise be buildable): at, ib, oancf, sale, sic (mapped); fopt, che (approx); act, lct, dlc (mapped); exchcd (approx, inert).

## 2. Variables (exact OSAP source names -> field_map key -> Sharadar)

| OSAP name | field_map key | Sharadar | status in index | role |
|---|---|---|---|---|
| at (and l1_at, prior fiscal year) | compustat.at | SF1.assets | mapped | denominator of every term; level |
| ib | compustat.ib | SF1.netinccmn | mapped | accruals numerator (flow, income before extraordinary) |
| oancf | compustat.oancf | SF1.ncfo | mapped | CFO, flow, inflow-positive |
| fopt | compustat.fopt | SF1.ncfo | approx | fallback CFO only when oancf null; ncfo is AFTER working capital, fopt before; inert in-window (same column is null where oancf is) |
| act, che, lct, dlc (+ l1_ each) | compustat.act / che / lct / dlc | assetsc / cashneq+investmentsc.fillna(0) / liabilitiesc / debtc | mapped / approx / mapped / mapped | fallback CFO only; OSAP zero-fills act che lct dlc, Sharadar act/lct/dlc null ~20% (unclassified balance sheets) |
| sale (and l1_sale) | compustat.sale | SF1.revenue | mapped | tempDelRev numerator (flow) |
| ppegt | compustat.ppegt | none | **unavailable** | tempPPE numerator |
| sic -> sic2 = floor(sic/100) | compustat.sic | TICKERS.siccode (current, not point-in-time; 12.3% of tickers reclassified) | mapped | regression grouping |
| exchcd | crsp.exchcd | TICKERS.exchange (current) | approx | only for "drop NASDAQ (exchcd==3) with fyear<1982": inert on a 1998+ snapshot |
| fyear, datadate | compustat.fyear / compustat.datadate | fiscal year / calendardate | approx / mapped | year cell and availability clock |
| ni | compustat.ni | SF1.netinc | mapped | ONLY the placebo AbnormalAccrualsPercent; not needed for this predictor |

Upstream (a_aCompustat = CompustatAnnual.py, INDL/STD/consolidated annual rows, CCM-linked; SignalMasterTable): permno attached by CCM;
SignalMasterTable keeps shrcd 10/11/12 and exchcd 1/2/3 only (US common on NYSE/AMEX/NASDAQ).

## 3. Formula

Per firm-year t (fiscal years, consecutive; a gap year makes the lag null):
```
tempCFO      = oancf                      if oancf not null
             = fopt - (act-l1_act) + (che-l1_che) + (lct-l1_lct) - (dlc-l1_dlc)   otherwise
tempInvTA    = 1 / l1_at
tempAccruals = (ib - tempCFO) / l1_at
tempDelRev   = (sale - l1_sale) / l1_at
tempPPE      = ppegt / l1_at
```
Winsorise/trim (`winsor2(..., trim=True, cuts=[0.1, 99.9], by=["fyear"])`) the four temp variables at the 0.1/99.9 percentiles within fyear
(trim: extreme observations removed, not clipped). Then OLS by (fyear, sic2):
`tempAccruals ~ 1 + tempInvTA + tempDelRev + tempPPE`, `AbnormalAccruals = residual`. Cells with `_Nobs` (non-null tempAccruals count) < 6
are dropped. First row per (permno, fyear) kept. Expanded to monthly and forward-filled (12-month padding).
Signal = the residual; raw level, not ranked/scaled. Note the SignalDoc text says "average total assets"; the CODE divides by l1_at
(prior-year total assets) -- the code is authority. Placebo AbnormalAccrualsPercent = residual * l1_at / |ni|, out of scope.

## 4. Timing / lag

- OSAP: annual row available at `time_avail_m = datadate month + 6` (6-month lag), held (forward-filled) 12 months until the next annual row.
  No quarterly update inside a fiscal year.
- ART-as-of-filing (datekey) would make the same fiscal year's information available at median +44d, p95 +101d after period end, i.e.
  ~4-5 months earlier than OSAP and would refresh every quarter (TTM) instead of annually: a different signal timing and a different cell
  (calendar-quarter TTM vs fiscal year). The faithful dimension is **ARY** (fiscal-year-end annual), which is what `FactorDef.dimension`
  is sanctioned for; with ARY the harness still controls as-of via datekey.
- Flow items under TTM: ib, oancf, sale are TTM flows on ART; `sale - l1_sale` and `l1_*` require the value 4 quarters earlier (same quarter),
  which is the 4-quarter-lag ART pair, not the prior ARQ. Levels (at, act, che, lct, dlc) are point-in-time so ART==ARQ for them.
  Under ART, tempAccruals/tempDelRev year-over-year differences are rolling (overlapping windows), not annual; not a smear but a change of meaning.
- Cross-section (fyear x sic2) needs peers of the same fiscal year: Compustat fyear convention (FYE Jan-May assigned to the prior year)
  is not reproduced by Sharadar reportperiod year; an approx deviation for non-December filers.

## 5. Filters
- Sample: shrcd 10/11/12 on exchcd 1/2/3 via SignalMasterTable (harness universe is stricter: price>=1, cap/ADV bands).
- Cell size >= 6 valid (non-null, post-trim) observations per (fyear, sic2); trim 0.1/99.9 by fyear across all firms; rows needing l1_at.
- Drop NASDAQ fyear<1982 (inert here). No explicit financials exclusion in OSAP (SIC 6xxx stay in, regressed within their own sic2);
  but oancf/act/lct are unavailable or null for many financials (act/lct null ~20%).

## 6. Predicted sign
SignalDoc `Sign = -1`: higher abnormal accruals -> lower returns (long low, short high). SignalDoc: Return 0.917 %/mo, t=8.43, EW, LS quantile 0.1,
portfolio period 12, start month 6; OP note: original paper lags accounting data by 3 months vs OSAP's 6. Sample 1971-1992.

## 7. Mass-point question
Do-nothing firm: a residual from a cell regression is continuous, so there is no natural mass point; a firm with zero accruals and model-fitted
zero gets a residual ~0 by chance only. Continuity expected, ties negligible (<<1%). Mass points that DO exist: (i) each value repeats
12 consecutive months (annual forward fill) -- a temporal, not cross-sectional, repeat; (ii) firms dropped by trim / small cells have no value
(missing, not 0). Tie handling: ranks average/first; harness sector rank applies. Expected coverage is below the ~95% universe because of
cell-size >=6, winsor trim, and lagged-at requirements (estimate ~70-85% of a US-common universe, to be measured at preflight, not here).

## 8. History
Needs two consecutive fiscal years (t and t-1) of at, sale; ~1 year of breadth before the first usable row. Snapshot SF1 starts 1997Q4 in breadth
(ART 1998 flows ~50% populated); first clean ARY accruals = FY1998 (l1 = FY1997), filed ~Q1 1999 under datekey, so Jan-Mar 1999 months
are thin under as-of-filing and a ~1-year cold start under ART. Regression cells in 1998-1999 are smaller than later years.
history_months: >= 24 (annual lag), plus availability lag.

## 9. OSAP metadata
Acronym AbnormalAccruals | Predictor | Xie 2001 AR | Predictability 1_clear | Rep quality 2_fair | Sample 1971-1992 | Acronym2 AccrAbn |
Key table 3, port sort size adjusted nonstandard | Sign -1 | Return 0.917 | T 8.43 | EW | LS quantile 0.1 | Portfolio period 12 | Start month 6 |
Filter none | GScholar cites 139. Evidence: "t=8 port sort w/ nonstandard data lag".

## 10. Proposed Sharadar mappings (only if the caller overrides `infeasible`)
- at -> assets (ARY level); ib -> netinccmn; oancf -> ncfo; sale -> revenue (ARY flows); sic -> TICKERS.siccode (current; look-ahead for ~1 in 8 tickers).
- fallback CFO (fopt, act, che, lct, dlc): drop the branch, set tempCFO = ncfo; deviation: where ncfo is null (~6% ART) the row is missing
  rather than computed (OSAP's branch only matters pre-1988 for Compustat).
- ppegt -> ppnenet (DEVIATION: net not gross; Sharadar 0-filled; this is the gating deviation, changes the regression).
- Fields not in the map: none; fields unavailable: ppegt only. All statuses must be re-verified on DATA_SHA 198b281de1a0 by the field-checker
  (index `verified_on` is empty for all; every note is from a predecessor pull): compustat.at, ib, oancf, fopt, act, che, lct, dlc, sale, ppegt,
  sic, exchcd, fyear, datadate, ppent (alt).
- Harness notes: residual regression by (fyear, sic2) is cross-sectional maths with trimming -- the factor file cannot do it per the hard
  rules ("no IC/decile maths"); needs a harness helper (group OLS residual) in addition to `FactorDef.dimension='ARY'`.
