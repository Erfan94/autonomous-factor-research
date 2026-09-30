# PctAcc — Percent operating accruals (Hafzalla, Lundholm, Van Winkle 2011, AR, Table 4A)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/PctAcc.py` (cached `predictor.py`). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`; measurements are scratch (harness universe, recorded snapshot, no factor file, no API read).

**VERDICT: approx** (translate and preflight). The primary formula `(ib - oancf)/|ib|` maps fully; OSAP's balance-sheet FALLBACK (used only when `oancf` is missing) needs `txp`, which Sharadar does not publish and OSAP does not zero-fill, so the fallback is not reproduced. That drops 0.0-1.7% of universe names (median 0.3%) from 1999-12-31 (up to 5.8% in 1999-01..03), measured on 264 of 276 months. Judgment call for the caller: a strict reading of the missing-item rule could call the fallback rows infeasible; they are a small, separable branch and the signal's main branch has no missing item.
Measured (universe, 264 months 1999-12-31..2021-11-30; the first 12 signals 1998-12..1999-11 are thin/transitional): scored 1,697-2,725 names (median 1,837), coverage 84.9-99.6% of the universe (median 97.1%); 1998-12..1999-02 only 51.4-57.2% (ART needs four quarters of history). Distinct values = n scored, modal share 0.037-0.168% (median 0.055%, a handful of names): no mass point, no tie rule needed. ib exactly 0: 0.00-0.11% of the universe; ncfo == ib exactly: <= 0.16%.

## 1. Data availability
| OSAP input | key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `ib` | compustat.ib | `netinc + netincdis` (ART; sign trap: PLUS) | approx | no fill; missing -> NaN |
| `oancf` | compustat.oancf | `ncfo` (TTM flow, inflow-positive; exact-zero 0.055% of non-null, NOT vendor zero-fill) | mapped | not zero-filled: missing -> fallback branch |
| `act`, `che`, `lct`, `dp` (fallback only) | compustat.* | `assetsc`; `cashneq + investmentsc.fillna(0)` (approx); `liabilitiesc`; `depamor` | mapped/approx | zero-filled upstream (`zero_fill_vars`: act, che, lct, dp) |
| `dlc` (fallback only) | compustat.dlc | `debtc` (~20% null = unclassified) | mapped | NOT zero-filled |
| `txp` (fallback only) | compustat.txp | none | unavailable | NOT in `zero_fill_vars`, no `fillna` in predictor.py: a missing txp makes the fallback NaN in OSAP |
Unavailable list (IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob, ppegt): none needed. The only unavailable field is `txp`, used solely inside the fallback.
Unclassified balance sheets are never zero-filled here; the primary branch reads no balance-sheet item, so financials (no act/lct) stay scorable: OSAP has no SIC filter either.

## 2. Variables
`ib, oancf` (primary); `act, che, lct, dlc, txp, dp` and their 12-month lags (fallback); `permno, time_avail_m` from `m_aCompustat`.

## 3. Formula in words and key lines
Percent accruals: income before extraordinary items less operating cash flow, scaled by the absolute value of income; zero income divides by 0.01. Where operating cash flow is missing, accruals come from balance-sheet changes.
```
PctAcc = (ib - oancf)/abs(ib);  if ib == 0: (ib - oancf)/0.01
alt    = (d act - d che) - ((d lct - d dlc) - d txp - dp)        # 12-month changes; only when oancf is NaN
PctAcc = alt/abs(ib) (or /0.01 when ib == 0) where oancf is NaN
```
Sharadar: `ib = netinc + netincdis`, `oancf = ncfo`; `score = (ib - ncfo)/where(ib == 0, 0.01, |ib|)`; `ncfo` null -> NaN (fallback not reproduced); non-finite -> NaN. Raw ratio, no winsorising. Heavy tails by construction (small |ib|): per-month 1st / 99th percentile medians about -42 / +3.3; ranks, not levels, are used.

## 4. Timing / lag convention
OSAP: annual ib and oancf at datadate + 6 months, held 12 months. Sharadar: ART (trailing four quarters) as of filing; numerator and denominator are flows of the SAME trailing year, so the ratio is a level of a ratio: no year-over-year difference, nothing to smear, no `dimension=ARQ`. ART-as-of-filing changes the information date (earnings 1-3 months old at t vs 6-17 months in OSAP) and the update frequency (quarterly vs annual); that is a stated deviation, not a bug. The fallback (year-over-year differences) would need ARQ/yoy alignment; not built.

## 5. Filters
`predictor.py`: none (no SIC, no ceq). SignalDoc Quantile Filter `abs(prc) > 5` (Notes: "Exclude if price less than 5") is portfolio-stage, not in predictor.py, and is not reproduced; the harness price floor is $1 (as for EP's `exchcd == 1`).

## 6. Predicted sign
SignalDoc `Sign = -1.0` (high percent accruals -> low returns): `ascending=False`. Cat.Economic accruals; Cat.Data Accounting; sample 1989-2008; LS Quantile 0.1; EW; T-Stat 3.29 (size-adjusted long-short).

## 7. The mass-point question
A do-nothing firm has no natural value: `ib` and `ncfo` both change every filing. Exact hits: `ncfo == 0` gives exactly +/-1 (ib/|ib|; 0.055% of non-null, a few names); `ib == 0` divides by 0.01 (0.00-0.11% of the universe); `ncfo == ib` gives exactly 0 (<= 0.16%). Measured modal share 0.037-0.168% (median 0.055%): no cliff, no ties to handle. Tie handling: none (continuous). Null (ncfo null, ib null, non-finite) -> NaN so `blend_ranks` renormalises.

## 8. History needed (snapshot starts 1998-01)
ART needs four quarters: coverage 51-57% in 1998-12..1999-02 (ncfo thin), 85-99% from 1999-03; first full-coverage signal 1999-12-31 (84.9%). No return window, `history_months` not needed beyond the ART filing itself. `lookback_months` ~15 (max fundamental age).

## 9. OSAP metadata
PctAcc; Hafzalla, Lundholm, Van Winkle 2011 (The Accounting Review); Cat.Signal Predictor; 1_clear / 1_good; Cat.Form continuous; Acronym2 AccrOper; Key Table 4A; Return 0.97; Portfolio Period 12; Start Month 6. LongDescription "Percent Operating Accruals".

## 10. Proposed Sharadar mappings with deviations
```
f = ctx.fundamentals(["netinc","netincdis","ncfo","fxusd"])                  # ART
ib = f.netinc + f.netincdis                                                  # plus: netincdis sign inverted
score = ((ib - f.ncfo) / ib.abs().where(ib != 0, 0.01)).replace(+-inf, NaN)   # ncfo null -> NaN
ascending=False ; inputs SF1.netinc, SF1.netincdis, SF1.ncfo
```
Deviations: (a) `ib`: netinc is after non-controlling interest, extraordinary items not separable (approx); (b) balance-sheet fallback not reproduced (txp unavailable, not zero-filled): ncfo-null names -> NaN, 0.3% of the universe (median); (c) TTM as of filing instead of annual lagged 6 months; (d) `abs(prc) > 5` not reproduced; (e) `fxusd != 1` (reporting currency, 3.6% of ART rows; ratio is unit-free so NOT gated). Fields not in the map: none.
Recommendation: translate (approx) and preflight.
