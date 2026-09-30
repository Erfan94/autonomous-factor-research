# cfp — Operating cash flow to price (Desai, Rajgopal, Venkatachalam 2004, The Accounting Review, Table 2E R1)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/cfp.py` (cached `predictor.py`; upstream
`upstream_CompustatAnnual.py`, `upstream_SignalMasterTable.py`). DATA_SHA 198b281de1a0. Construction only.
Measured on the harness universe (build_universe + MonthContext, recorded snapshot), ALL 276 decision months
(signal 1998-12-31 .. 2021-11-30), SF1 ART as-of filing.

## 1. Data availability (verdict: APPROX — primary branch fully available; fallback branch not reproducible)
| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `oancf` (primary numerator) | `compustat.oancf` | `ncfo` (ART TTM flow, inflow-positive) | mapped | not zero-filled; NaN -> falls to fallback |
| `mve_permco` | `crsp.mve_permco` | `ctx.universe["mkt_cap_usd"]` (DAILY.marketcap, company-level) | approx | `==0` -> NaN |
| `ib` (fallback only) | `compustat.ib` | `netinc + netincdis` (sign trap: PLUS) | approx | not zero-filled |
| `act, che, lct, dp` (fallback only) | act/che/dp/lct | `assetsc`, `cashneq+investmentsc.fillna(0)`, `depamor`, `liabilitiesc` | mapped/approx | ZERO-FILLED (`zero_fill_vars`) |
| `dlc` (fallback only) | `compustat.dlc` | `debtc` | mapped | NOT zero-filled |
| `txp` (fallback only) | `compustat.txp` | none | **unavailable** | NOT zero-filled |
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt.
- THE MISSING-ITEM RULE: `txp` (taxes payable) has no SF1 field and OSAP does not zero-fill it (`zero_fill_vars` = nopi, dvt, ob, dm, dc, aco, ap, intan, ao, lco, lo, rect, invt, drc, spi, gdwl, che, dp, act, lct, tstkp, dvpa, scstkc, sstk, mib, ivao, prstkc, prstkcc, txditc, ivst). Read strictly that would be `infeasible`; it is NOT, because txp feeds only the FALLBACK (used where `oancf` is null) and, in OSAP itself, a null txp or dlc at either date makes accrual_level, and hence the fallback cfp, NaN. So dropping the fallback changes OSAP's value only on rows with oancf null AND txp, dlc, ib all present at t and t-12 (Compustat oancf is expected to be populated for essentially all fiscal years in the window; not checkable without Compustat). RUNNER'S CALL: `approx`; the strict-rule reading is flagged here for the caller. Not measurable (no Compustat) how many OSAP rows take the fallback.
- Measured ncfo null among universe names with an ART filing (all 276 months): median 2.7%, mean 3.6%; 47.6% at 1998-12, 46.3% 1999-01, 40.6% 1999-02 (ART needs four quarters of SF1 history, SF1 from 1997Q4), then 12.6% 1999-12, 9.9% 2000, 5.2% 2001, 1.0-3.2% 2003-2020, 5.8% 2021. `ncfo` null = cash-flow statement not reported, never 0 (field_map): NOT zero-filled here.
- fxusd: `ncfo` is in the reporting currency, cap in USD. `fxusd != 1` on <= 0.06% of universe names (median 0.05%): gate `fxusd == 1`, else NaN (same choice as CF).

## 2. Variables (exact source names)
`oancf`, `ib`, `act, che, lct, dlc, txp, dp` (annual Compustat, $ millions), `mve_permco` (SignalMasterTable, month t), `permno`, `time_avail_m`.

## 3. Formula in words and key lines
Operating cash flow over market value of equity. If `oancf` is missing, replace the numerator with income before extraordinary items less balance-sheet accruals (year-over-year changes).
```
accrual_level = ((act-l12.act) - (che-l12.che)) - ((lct-l12.lct) - (dlc-l12.dlc) - (txp-l12.txp) - dp)
cfp = (ib - accrual_level) / mve_permco                 # fallback; mve_permco == 0 -> NaN
cfp = oancf / mve_permco   where oancf.notna()          # overrides the fallback
```
Lags are 12 calendar months on the monthly panel (annual rows repeated 12 months, dedup keep-first); rows with no lag row are NaN. Right side of a merge with the SignalMasterTable (`inner` on Compustat match).
Harness: `f = ctx.fundamentals(["ncfo","fxusd"])`; `cfp = ncfo.where(fxusd == 1) / mkt_cap_usd.where(mkt_cap_usd > 0)`; ncfo NaN -> NaN (fallback not built).

## 4. Timing / lag
OSAP: fiscal-year `oancf` available `datadate + 6 months`, held 12 months (numerator 6-17 months stale); denominator month-t `mve_permco`, unlagged. Here: latest ART filing with `datekey <= signal`, within 15 months; numerator a TTM sum to the latest quarter (0-3 months old); no 6-month lag reproduced (field_map yoy ruling). Flow used as a LEVEL ratio (no year-over-year difference in the primary branch), so no ARQ override and no TTM smear; ncfo is a flow, never a level (ART == sum of 4 ARQ, != ARQ). The fallback branch would have needed the year-ago filing via `fundamentals_yoy`; it is not built. Early window: ART coverage of ncfo is thin at the first three signals (table above); `dimension="ARY"` (fiscal-year flow, OSAP's basis) is available as a sanctioned fallback but the 40% bar is cleared under ART.

## 5. Filters
None in the predictor; SignalDoc `Filter` and `Quantile Filter` blank. Harness universe only.

## 6. Predicted sign
SignalDoc `Sign = 1.0` (Return 1.275, T-Stat 2.77, port sort, EW, LS Quantile 0.2): high cash-flow-to-price earns high returns; long D10, `ascending=True`. No flip.

## 7. The mass-point question
Continuous ratio: a do-nothing firm (no new filing) keeps `ncfo` fixed, but `mkt_cap_usd` moves every month, so cfp moves. No default value, no signal zero-fill of oancf. Exact-zero cfp needs ncfo == 0 (0.055% of non-null, field_map). Measured over 276 months on the scored cross-section: exact-zero share median 0.053%, max 0.114%; modal-value share median 0.054%, max 0.118% (at most 2-3 names); distinct values equal n scored; qcut 10 bins in 276 of 276 months. Scored n min 1,182 (1998-12), median 1,840, max 2,728. Ties: none needed (harness average). `mkt_cap_usd <= 0` -> NaN.

## 8. History needed (snapshot starts 1998-01)
One latest filing plus month-end cap; no return window, no `history_months`; `lookback_months` 15. Coverage of the universe (cfp scored): min 51.8% (1998-12-31), 53.0% (1999-01), 58.5% (1999-02), 85.3% (1999-12), median 97.1%, mean 96.0%, max 99.5%; 0 of 276 months below 40%; from 1999-03 min 85.3%. Filed-universe share (any ART filing) min 97.2%, median 99.8%.

## 9. OSAP metadata
cfp; Acronym2 CFOper2Price; Desai, Rajgopal, Venkatachalam 2004 AR; Cat.Signal Predictor; Cat.Form continuous; Cat.Data Accounting; Cat.Economic valuation; Sample 1973-1997; Key Table "2E R1"; Test port sort; Evidence "t=2.77 in port sort"; Predictability 1_clear; Rep Quality 1_good; Sign 1.0; Return 1.275; T-Stat 2.77; EW; LS Quantile 0.2; Portfolio Period 12; Start Month 6; GScholar cites 649. Definition: operating cash flow (oancf) divided by market value of equity; if missing, ib less the accrual level (Δact - Δche - Δlct + Δdlc + Δtxp + dp, as coded).

## 10. Proposed Sharadar mappings with deviations
```
oancf -> SF1.ncfo (ART, mapped)        mve_permco -> ctx.universe["mkt_cap_usd"] (approx)        gate fxusd == 1
cfp = ncfo / mkt_cap_usd.where(mkt_cap_usd > 0); ncfo NaN -> NaN; ascending=True; lookback 15; inputs SF1.ncfo, SF1.fxusd, DAILY.marketcap
```
Deviations: (a) fallback (ib - accrual_level) NOT built: txp unavailable and not zero-filled by OSAP; ncfo-null names are NaN (universe by year 1.0%-5.8% from 2001; thin at the 1999-2000 start); (b) TTM to latest quarter vs fiscal year, no 6-month lag; (c) mve_permco -> DAILY marketcap at the primary ticker's price x all-class sharesbas (few-% level error on <= 2% of names); (d) fxusd != 1 names NaN (<= 0.06%); (e) ncfo is cash from operations as reported by Sharadar: as Compustat oancf; (f) `ib` in the dropped fallback would be `netinc + netincdis` (sign trap: PLUS), not netinccmn. Fields not in the map: none beyond txp (above).
Recommendation: **approx** — translate and preflight (expect coverage 52-59% at the first three probes, not a hard fail).
