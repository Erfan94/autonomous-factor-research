# FR — Pension funding status (Franzoni and Marin 2006, Table 3B)

OSAP ref b4e911e69678a7424f318617a61d813f54183123 (cache b4e911e6); source `Predictors/ZZ1_FR_FRbook.py`
(emits FR to Predictors/, FRbook to Placebos/; cached `predictor.py` is byte-identical to `ZZ1_FR_FRbook.py`),
upstream `DataDownloads/CompustatPensions.py` (cached `upstream_CompustatPensions.py`). DATA_SHA 198b281de1a0.
SignalDoc row (Cat.Signal == Predictor): Cat.Data = Accounting, Cat.Economic = composite accounting.

## 1. Data availability (verdict: DATA_UNAVAILABLE — recommend `infeasible`)

Every signal input is a Compustat pension-plan item from `COMP.ACO_PNFNDA`. The SF1 schema on this snapshot
(112 columns, read from the parquet) has no pension column of any kind, and `field_map_index.yaml` has no
pension key. `FR.py` has no `fillna(0)`: rows without pension data are dropped by an inner merge, so OSAP
itself does NOT zero-fill the missing items and the missing-item rule gives infeasible. Nothing to measure.

| input (OSAP) | field_map key | Sharadar | status | note |
|---|---|---|---|---|
| `pbnaa` (plan assets, 1980-86) | none | none in SF1 (no plan/pension/obligation column) | unavailable | |
| `pplao`, `pplau` (plan assets, overfunded / underfunded plans) | none | none | unavailable | |
| `pbnvv` (benefit obligation, 1980-86) | none | none | unavailable | |
| `pbpro`, `pbpru` (PBO, overfunded / underfunded plans) | none | none | unavailable | |
| `mve_permco` (company-level market value) | `crsp.mve_permco` | DAILY.marketcap, primary class | approx (field_map) | only the scaler; irrelevant to the verdict |
| `shrcd` (`> 11` nulled) | `crsp.shrcd` | TICKERS.category | approx | current-only classification |
| `gvkey`, `year` link | none | none | n/a | Compustat key; Sharadar joins on ticker |
| `at` (FRbook placebo only) | `compustat.at` | SF1.assets | mapped | not used by FR |

- No proxy is faithful. SF1 carries `accoci`, `liabilities`, `taxassets` etc., but nothing isolates the
  pension-plan fair value of assets or projected benefit obligation; do not substitute.
- **Recommendation: `infeasible`** (class `data_unavailable`). Reason: pension plan assets/PBO absent from
  Sharadar; OSAP does not zero-fill them. Do not translate, do not preflight.

## 2. Variables (exact source names)

`gvkey`, `permno`, `time_avail_m`, `shrcd`, `mve_permco` (SignalMasterTable); `pbnaa`, `pplao`, `pplau`,
`pbnvv`, `pbpro`, `pbpru` (CompustatPensions, keyed `gvkey`, `year`); `at` (FRbook placebo only).

## 3. Formula

FR = (FVPA - PBO) / mve_permco, where FVPA (fair value of plan assets) and PBO depend on the calendar year:
```
FVPA = pbnaa            if 1980 <= year <= 1986
     = pplao + pplau    if 1987 <= year <= 1997
     = pplao            if year >= 1998          (the docstring-style note in SignalDoc writes pplao + pplao: a typo)
PBO  = pbnvv            if 1980 <= year <= 1986
     = pbpro + pbpru    if 1987 <= year <= 1997
     = pbpro            if year >= 1998
FR = (FVPA - PBO) / mve_permco ;  FR = NaN if shrcd > 11
```
In the 1987-97 branch a missing `pplau` or `pbpru` makes the sum NaN (no fill). Raw ratio, no log, no winsorising.

## 4. Timing / lag

`CompustatPensions.py` sets `year = datadate.year + 1` and keeps the first row per gvkey-year, so a plan value
for fiscal year-end in calendar year Y is used for every month of Y+1 (a 12-month-plus lag; between 12 and 23
months stale by month). The merge is on calendar year of `time_avail_m`. `mve_permco` is the current month's
market value (not lagged with the pension data). No ART/ARQ issue: no SF1 item is involved.

## 5. Filters

`shrcd > 11` nulls FR (common stocks only, OSAP `shrcd` 10-11 kept). The SignalDoc definition also says
"exclude if price less than 5"; `ZZ1_FR_FRbook.py` does NOT implement a price screen.

## 6. Predicted sign

SignalDoc `Sign = 1.0` (higher funding status, higher return). Port sort, EW, LS quantile 0.1, quantile filter
NYSE breakpoints, Portfolio Period 12, Start Month 6. Sample 1980-2002, "49 bps long-short", no LS t-stat.
Predictability in OP 2_likely, Signal Rep Quality 2_fair. SignalDoc Notes: non-monotonic, lowest FR clearly worst.

## 7. Mass-point question

Moot for this snapshot (no data). For reference: a firm with no pension plan is not a zero, it is absent
(inner merge drops it), so the scored set is only plan sponsors, a minority of CRSP firms. A sponsor with
fully funded plan gives FR near 0 but rarely exactly 0; no tie block is expected.

## 8. History needed

Sample 1980-2002; FASB 158 (2006) reporting changes are not handled. The snapshot starts 1998-01 and holds no
pension data at any date.

## 9. OSAP metadata

Acronym FR (Acronym2 PensionFunding); Cat.Signal Predictor; Franzoni and Marin, JF 2006; Cat.Form continuous;
Cat.Data Accounting; Cat.Economic composite accounting; Key Table in OP 3B; Test in OP port sort no LS;
sample 1980-2002; GScholar cites (2025-09) 324. Placebo sibling in the same script: FRbook (scaled by `at`).

## 10. Proposed Sharadar mappings / deviations

None. Not in field_map and would need new keys only if a pension table ever became available:
`compustat.pbnaa`, `pplao`, `pplau`, `pbnvv`, `pbpro`, `pbpru`. The same blocker applies to FRbook (placebo).
