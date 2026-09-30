# XFIN — Net external financing: (sstk - dv - prstkc + dltis - dltr + dlcch) / total assets (Bradshaw, Richardson, Sloan 2006, Table 3)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/XFIN.py` (cached `predictor.py`; upstream `upstream_CompustatAnnual.py` beside it). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`. Measurements: harness universe, ALL 276 decision months (signals 1998-12-31 .. 2021-11-30), recorded snapshot, scratch measurement (no factor file).

## 1. Data availability verdict: APPROX (net flows replace gross ones; preferred excluded). Not infeasible: every term has a Sharadar source and the dlcch zero-fill is OSAP's own.
| OSAP term | Sharadar | status | OSAP missing-value rule |
|---|---|---|---|
| `sstk` - `prstkc` | `SF1.ncfcommon` (NET common-equity flow, inflow-positive; preferred excluded) | `sstk`, `prstkc` approx (net, not gross) | both ZERO-FILLED upstream (`zero_fill_vars`) -> `ncfcommon.fillna(0)` |
| `dv` | `SF1.ncfdiv` (outflow-negative, so `-dv` = `ncfdiv.clip(upper=0)`; mostly common-only) | `dv` approx | NOT zero-filled -> null -> NaN |
| `dltis` - `dltr` + `dlcch` | `SF1.ncfdebt` (NET debt flow incl. the short-term/CP change, issuance-positive) | `dltis`/`dltr` approx (net); `dlcch` unavailable alone but SUBSUMED in `ncfdebt` | `dltis`, `dltr` NOT zero-filled -> null -> NaN; `dlcch` zero-filled by the predictor itself (`fillna(0)`), subsumed here |
| `at` | `SF1.assets` (ART level) | `at` mapped | not filled; `at` null/0 -> NaN |
Gross legs are not recoverable (only the net sums are used by OSAP's formula, so nothing is lost): XFIN's numerator equals the NetEquityFinance numerator plus the NetDebtFinance numerator, i.e. `ncfcommon + ncfdiv + ncfdebt` with OSAP's fills. `dlcch` is in the OSAP sum but NOT in `zero_fill_vars`; the predictor fills it inside predictor.py, which `ncfdebt` reproduces exactly. No IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob, ppegt.
Deviations that keep it approx: ncfcommon/ncfdiv exclude preferred flows (TARP-era financials 2008-2011 off by $B; predictor does not drop financials); ncfdiv is common-only on most filers while `dv` is common + preferred; taxes on net share settlement excluded from ncfcommon; ncfdebt null -> NaN as OSAP (vendor 0-fill of an absent flow is not separable).

## 2. Variables (exact source names)
`m_aCompustat` (annual, monthly-expanded): gvkey, permno, time_avail_m, `sstk`, `dv`, `prstkc`, `dltis`, `dltr`, `dlcch`, `at`.

## 3. Formula
```
dlcch = dlcch.fillna(0)                                               # predictor.py; sstk, prstkc are zero-filled upstream
XFIN  = (sstk - dv - prstkc + dltis - dltr + dlcch) / at              # END-of-year at, NOT average assets; no |ratio| screen; dropna
```
Plainly: net cash raised from shareholders and lenders in the fiscal year (stock sold + debt issued - buybacks - dividends - debt retired), as a fraction of year-end assets. Positive = firm raised external capital.

## 4. Timing / lag
OSAP: annual fiscal-year flows, made available at datadate + 6 months and held 12 months. Harness: `ctx.fundamentals(["ncfcommon","ncfdiv","ncfdebt","assets"])` with the default ART (trailing-four-quarter flows and the level of assets, same filing, `datekey` <= signal). No `dimension=ARQ`: the numerator is a TTM flow over a level, NOT a year-over-year difference of a flow, so nothing smears under TTM and a single quarter's flow over assets would be wrong. The 6-month annual lag is not reproduced (latest filed ART, 0-3 months old, refreshed quarterly). No year-ago filing is needed, unlike NetEquityFinance/NetDebtFinance (they use average assets). Flows and assets share the reporting currency (`fxusd != 1` for 0.05% of the universe), so no fxusd gate.

## 5. Filters
SignalDoc Filter blank; predictor.py applies none (no SIC, ceq, price screen). The harness universe applies. OSAP has no |ratio| > 1 screen here (unlike NetEquityFinance/NetDebtFinance); none applied. Measured share of scored names with |XFIN| > 1: mean 0.26%, max 1.65% per month; the harness's per-month winsorisation (1/99) handles the tails.

## 6. Predicted sign
SignalDoc `Sign = -1.0` (t = 5.7): high net external financing predicts LOW returns. `ascending=False` (high raw is the short leg).

## 7. Mass-point question
Do-nothing firm: no issuance, no buyback, no dividend, no net debt flow gives exactly 0.0 (ncfcommon null -> 0; ncfdiv 0; ncfdebt 0). Measured over ALL 276 months: the exact 0 is the modal value at a mean share 0.20% of scored names, max 0.58% (1999-03), never >= 5% or 10%; distinct values 1,180-2,719 (= scored names less a handful), `qcut` yields 10 bins in every month. The three-way zero is rare because ncfdebt == 0 (15% of non-null) rarely coincides with no equity flow and no dividend. No mass point; no tie design needed; the zero is a real value and kept (harness averages ranks over ties).

## 8. History needed (snapshot starts 1998-01; SF1 from 1997Q4)
No price window, no year-ago filing: `history_months` not needed (no SEP/DAILY read), `lookback_months` ~15 (latest filing within `max_fundamental_age_months`). Scorable decision months: **276 of 276** (n scored >= 1,182 every month). Coverage (scored / universe): median 97.0%, min 51.8% at 1998-12-31, 53.0% (1999-01), 58.5% (1999-02), then 85.4-99.6%; months under 90%: 18 (all 1998-12..2000-11, cash-flow statements missing or null in the first TTM filings); months under 40%: 0. Null shares (median): ncfdiv 3.0%, ncfdebt 2.9%, ncfcommon 3.0% (same rows: no cash-flow statement), assets 0.2%. Treating a null `ncfdiv` as 0 instead of NaN changes coverage by < 0.3 pt and leaves the rank unchanged (Spearman 1.000 every month); follow OSAP (null -> NaN).

## 9. OSAP metadata
Bradshaw, Richardson and Sloan (2006), JAE; Cat.Data Accounting; Cat.Economic external financing; continuous; sample 1971-2000; Acronym2 ExtFinNet; Key Table 3; Test "port sort size adjusted"; EW; LS Quantile 0.1; Portfolio Period 12; Start Month 6; Predictability 1_clear / Signal Rep Quality 1_good; T-stat 5.7; 798 cites. Source `Signals/pyCode/Predictors/XFIN.py`. SignalDoc definition (sstk - dv - prstkc + dltis - dltr, scaled by `at`) omits `dlcch`; the CODE adds it, and the code is followed.

## 10. Proposed Sharadar mappings
```
y = ctx.fundamentals(["ncfcommon","ncfdiv","ncfdebt","assets"])     # ART default, no dimension override
num = y.ncfcommon.astype(float).fillna(0)                         # sstk - prstkc, OSAP zero-fills both
    + y.ncfdiv.astype(float).clip(upper=0)                         # -dv (outflow-negative; NaN stays NaN; positive 0.19% clipped)
    + y.ncfdebt.astype(float)                                      # dltis - dltr + dlcch (net, incl. CP); null -> NaN
XFIN = num / y.assets.where(y.assets > 0);  replace +-inf -> NaN
```
Declare `SF1.ncfcommon`, `SF1.ncfdiv`, `SF1.ncfdebt`, `SF1.assets`; `ascending=False`; no `history_months`; `lookback_months` ~15.
Deviations: net for gross (sstk/prstkc, dltis/dltr); preferred flows excluded; dv vs ncfdiv scope; timing (latest ART instead of the fiscal year at datadate+6 months); trailing four quarters rather than the fiscal year; assets at the same filing (OSAP `at` is year-end, same as here, so the denominator needs no year-ago term). Fields in map: `compustat.sstk`, `compustat.prstkc`, `compustat.dv`, `compustat.dltis`, `compustat.dltr`, `compustat.dlcch`, `compustat.at` (all mapped/approx/unavailable-but-subsumed as above).
