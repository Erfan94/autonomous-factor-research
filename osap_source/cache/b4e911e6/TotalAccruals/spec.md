# TotalAccruals — Total accruals (Richardson, Sloan, Soliman, Tuna 2005, JAE, Table 8A TACC)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Signals/pyCode/Predictors/TotalAccruals.py` (cached `predictor.py`, `signaldoc_row.csv`,
`upstream_CompustatAnnual.py`). Written fresh from source and `field_map_index.yaml` / `field_map.yaml`. DATA_SHA 198b281de1a0.
Measured on the harness universe (`build_universe`, recorded snapshot), all 276 decision months (signals 1998-12-31 .. 2021-11-30), scratch script only, no factor file.

## 1. Data availability — VERDICT: APPROX (every input present; preferred-stock netting lost; `dv` NOT zero-filled by OSAP)
| OSAP input | field_map key | Sharadar (ART) | status | OSAP missing rule |
|---|---|---|---|---|
| `ni` | `compustat.ni` | `netinc` | mapped | not filled: NaN |
| `oancf`, `ivncf`, `fincf` | `compustat.oancf/ivncf/fincf` | `ncfo`, `ncfi`, `ncff` | mapped | not filled: NaN |
| `sstk`, `prstkc` | `compustat.sstk/prstkc` | one column `ncfcommon` (NET common flow, inflow-positive; `sstk - prstkc = ncfcommon`) | approx | both ZERO-FILLED (`zero_fill_vars`) |
| `dv` | `compustat.dv` | `ncfdiv` (outflow-NEGATIVE, mostly common-only) | approx | NOT zero-filled (`dvt` is, `dv` is not): NaN |
| `at` (lag 12 months) | `compustat.at` | `assets` one fiscal year before the latest filing | mapped | not filled: NaN |
- Checked both places: upstream `CompustatAnnual.py` `zero_fill_vars` = [nopi, dvt, ob, dm, dc, aco, ap, intan, ao, lco, lo, rect, invt, drc, spi, gdwl, che, dp, act, lct, tstkp, dvpa, scstkc, sstk, mib, ivao, prstkc, prstkcc, txditc, ivst]. `dv` is absent, so a missing `dv` gives a missing TotalAccruals after 1989. The predictor's own `fillna(0)` creates `temp*` columns for ivao, ivst, dltt, dlc, pstk, sstk, prstkc, dv, but only `tempivao, tempivst, tempdltt, tempdlc, temppstk` are used (by the pre-1990 balance-sheet branch); `tempsstk`, `tempprstkc`, `tempdv` are computed and never referenced. The post-1989 branch reads the raw `dv`, `sstk`, `prstkc`. Therefore on this snapshot's window (1999+) only the cash-flow branch is live and `pstk`/`dltt`/`dlc`/`ivao`/`ivst` (pstk unavailable, ivao/ivst approx) are NOT needed.
- Not used: IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob, ppegt. `ib` is NOT used (`ni`, not `ib`), so the `ib = netinc + netincdis` sign trap does not apply; do not add `netincdis`.
- Why approx, not feasible: Compustat `sstk`/`prstkc`/`dv` include PREFERRED; Sharadar `ncfcommon` excludes preferred and `ncfdiv` includes it only for some filers (field_map `dv`), so preferred flows stay un-netted inside `ncff`. Nothing is unavailable.

## 2. Variables (exact source names)
`permno, time_avail_m, ivao, ivst, dltt, dlc, pstk, sstk, prstkc, dv, act, che, lct, at, lt, ni, oancf, ivncf, fincf`; derived `tempWc, tempNc, tempFi` (balance-sheet branch), `at_lag12`, `TotalAccruals`. Live inputs for 1990+: `ni, oancf, ivncf, fincf, sstk, prstkc, dv, at`.

## 3. Formula in words and key lines
Total accruals by the cash-flow method: net income minus operating, investing and financing cash flow, plus net stock issuance, minus dividends, scaled by the previous year's total assets. Before 1990 (code: `year <= 1989`; SignalDoc text says "before 1988 / starting 1988", code wins) the change in net working capital + net non-current + net financial assets is used instead.
```
df["at_lag12"] = df.groupby("permno")["at"].shift(12)              # monthly rows of annual data: the PRIOR fiscal year's at
late (year > 1989):  TotalAccruals = (ni - (oancf + ivncf + fincf) + (sstk - prstkc - dv)) / at_lag12
early (year <= 1989): ((Wc - Wc_lag12) + (Nc - Nc_lag12) + (Fi - Fi_lag12)) / at_lag12
```
Algebra: `fincf` already contains stock issuance, repurchase and dividends, so `- fincf + sstk - prstkc - dv` leaves minus the DEBT/other financing flows; the published series is replicated as coded. On Sharadar `sstk - prstkc = ncfcommon` and `-dv = ncfdiv` (<= 0), so the numerator is `netinc - (ncfo + ncfi + ncff) + ncfcommon + min(ncfdiv, 0)`.
Relation to the reviewed `PctTotAcc.py`: that factor has the SAME numerator on Sharadar (`prstkcc - sstk` and `dvt` collapse to the same `-ncfcommon` and `-ncfdiv`) and differs only in the denominator (`|ni|` there, lagged total assets here) and in the null rule for `ncfdiv` (filled 0 there, NaN here). Measured on 4 months (2005-06, 2012-11, 2019-06, 2021-11): Spearman of the two scores 0.871-0.898 (1,697-1,828 common names). It is NOT `Accruals.py` (Sloan working-capital accruals from balance-sheet deltas, average assets, dp subtracted): different items entirely.

## 4. Timing / lag convention
OSAP: annual Compustat, each record stamped datadate + 6 months and copied across 12 months (`m_aCompustat`), held 12 months (Portfolio Period 12, Start Month 6). `at_lag12` is the monthly row 12 months back, i.e. the preceding fiscal year's assets (beginning-of-year assets).
Sharadar: `ctx.fundamentals_yoy([...])`, default ART (trailing four quarters, as filed). Flows are ART at the latest filing; the denominator is `assets_lag`, assets at the same fiscal period one year earlier, aligned by reportperiod (tol 45 days), as in `Accruals.py`. The signal refreshes quarterly and is available at datekey, 1-3 months sooner than OSAP's +6 months; a TTM window replaces the fiscal year.
Flow items and TTM smearing: every numerator item is a TTM FLOW over the same window in one ratio, and there is NO year-over-year difference of a flow, so nothing smears under ART; no `dimension=ARQ` needed and no dimension override. (A yoy difference is used only on the balance-sheet `at`, a level.) Cash-flow sign conventions (field_map): `ncfcommon` inflow-positive net, `ncfdiv` outflow-negative (0.0-0.6% of rows positive, clip to 0), `ncfo/ncfi/ncff` native signs. `ib` trap not involved.

## 5. Filters
Predictor: none except `dropna` of the ratio. SignalDoc Filter blank. Here: harness universe only (price >= $1, relative size/dollar-volume screen); financials and utilities are NOT dropped (OSAP has no sample restriction).

## 6. Predicted sign
SignalDoc `Sign = -1.0` (high accruals -> low returns), so `ascending=False`. Cat.Signal Predictor; Cat.Economic "investment alt"; Cat.Data Accounting; Cat.Form continuous; T-Stat 6.38 (mv reg, Table 8A TACC); EW; Sample 1962-2001.

## 7. The mass-point question
A do-nothing firm (all flows zero) gives 0 / at_lag12 = 0, but the cash-flow totals are essentially never all zero, so no value is a mode. Continuous ratio. Measured on all 276 months (scored names): modal value 0.041-0.112% of scored names (median 0.055%); distinct values equal the scored count in every month (1,070-2,439); ten `qcut` bins in every month. `ncfdiv == 0` is 38.9-44.7% in the four probe months but it is one additive term, not the score.
Tie handling: none needed beyond the harness average rank. Null handling: `ncfdiv` null -> NaN (OSAP leaves `dv` missing), `assets_lag <= 0` -> NaN. Tails: |score| > 1 on median 0.72% of scored names (max 6.5%, early months); p1/p99 of a month about -0.50 / +0.61 (median month; 2021-11: -1.48 / +1.94). Rank, never z-score.

## 8. History needed (snapshot starts 1998-01)
ART filing now plus the same period one year earlier; no price window, no `history_months`. Scorable months: **276 of 276** with >= 1,070 scored names; coverage of the universe (scored share) 46.9%, 48.1%, 54.5% at 1998-12 / 1999-01 / 1999-02 (ART needs four quarters and the year-ago filing; null `assets_lag` 51.6% at the start), 83.3-98.6% from 1999-03 (median 96.4% over all months); 3 of 276 months below 80%. Null shares from 1999-03 (min/median/max): netinc 0.34/2.6/14.4%, `ncfdiv` 0.40/3.0/14.5%, `assets_lag` 1.1/3.1/15.1%, ncfo|ncfi|ncff any 0.40/2.9/14.7%. `rebalance.min_months` 120 is met (276).

## 9. OSAP metadata
TotalAccruals (Acronym2 TotalAccruals); Richardson, Sloan, Soliman, Tuna; 2005; Journal of Accounting and Economics; Predictability in OP `1_clear`; Signal Rep Quality `1_good`; Cat.Economic investment alt; Cat.Data Accounting; Cat.Form continuous; Sign -1.0; T-Stat 6.38; EW; Portfolio Period 12; Start Month 6; Filter blank; sample 1962-2001; Key Table "8A TACC"; Test "mv reg"; cites 394. Notes: Table 8 panel A regression with t-stat 6.38.

## 10. Proposed Sharadar mappings with deviations
```
y = ctx.fundamentals_yoy(["netinc","ncfo","ncfi","ncff","ncfcommon","ncfdiv","assets"])     # ART
num = y.netinc - (y.ncfo + y.ncfi + y.ncff) + y.ncfcommon.fillna(0) + y.ncfdiv.clip(upper=0)   # ncfdiv NOT filled (NaN), ncfcommon filled 0
score = num / y.assets_lag.where(y.assets_lag > 0)       # ascending=False; inputs SF1.{netinc,ncfo,ncfi,ncff,ncfcommon,ncfdiv,assets}
```
Deviations: (a) `ncfcommon` excludes preferred issuance/redemption and `ncfdiv` mostly excludes preferred dividends, so preferred flows stay un-netted inside `ncff` (material for financials 2008-11, TARP); (b) net-share-settlement tax and option-exercise flows sit in `ncfcommon`; (c) ART as filed (quarterly refresh) replaces the fiscal year at datadate + 6 months, and `assets_lag` is assets at the period one year before the latest filing (same idea as `at_lag12`); (d) `ncfdiv` null -> NaN rather than 0 to follow OSAP's unfilled `dv` (PctTotAcc fills its `dvt`); (e) the pre-1990 balance-sheet branch is not built (window starts 1999); (f) positive `ncfdiv` clipped to 0; (g) extraordinary-item treatment: `netinc` after NCI, `ni` in Compustat is after extraordinary items, not income before (no `netincdis` term). Fields not in the map: none. Recommendation: translate (approx) and preflight; expect heavy overlap with `PctTotAcc` (family assignment, Phase C).
