# CBOperProf — Cash-based operating profitability (Ball, Gerakos, Linnainmaa, Nikolaev 2016, JFE, Table 4A)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/CBOperProf.py` (cached
`predictor.py`, `signaldoc_row.csv`). DATA_SHA 198b281de1a0. field_map statuses are mappings, not
proofs, unless `verified_on` is set (only `at`, `ceq`, `mve_permco` are, on this snapshot).

## 1. Data availability (verdict: APPROX; nothing needed is unavailable once OSAP's own zero-fill applies)

| OSAP input | field_map key | Sharadar | status | treatment |
|---|---|---|---|---|
| `revt` | compustat.revt | SF1 `revenue` (ART TTM) | mapped | null 3-7%/yr; exact-zero 4% pooled |
| `cogs` | compustat.cogs | SF1 `cor` | approx | as reported, embeds D&A for ~36% of rows; exact-zero 20.5% (vendor zero-fill) |
| `xsga`,`xrd` | compustat.xsga / xrd | SF1 `sgna` (excludes R&D) | approx / mapped | `xsga - xrd` == `sgna` (section 3) |
| `rect`,`invt`,`ap` | compustat.* | `receivables`,`inventory`,`payables` | mapped | ART levels, null 0.03-0.05% |
| `drc`,`drlt` | compustat.drc / drlt | `deferredrev` (ONE field = drc + drlt) | approx | use once, never twice; 64% of yoy changes are exactly 0 |
| `xpp` | compustat.xpp | none | unavailable | OSAP zero-fills it in the predictor itself -> term dropped, approx |
| `xacc` | compustat.xacc | none | unavailable | same: predictor's own `fillna(0)` -> term dropped, approx |
| `at` | compustat.at | `assets` | mapped, verified 2026-09-30 | denominator, current ART (not lagged) |
| `ceq` | compustat.ceq | `equity` | approx, verified-with-deviation 2026-09-30 | filter only (BM) |
| `mve_permco`,`mve_c` | crsp.mve_permco | `ctx.universe["mkt_cap_usd"]` | approx, verified 2026-09-30 | filter only (BM) |
| `shrcd`,`sicCRSP` | crsp.shrcd / siccd | harness universe; `TICKERS.siccode` (CURRENT) | approx | sample screens only |

- Verdict **approx**. No IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob, ppegt. The rule "infeasible unless OSAP zero-fills it" is met for `xpp` and `xacc` (predictor `fillna(0)`).
- The approximation is real: OSAP fills Compustat MISSING, but `xpp` and `xacc` are reported by a subset
  of Compustat firms, for which `-(dxpp)` and `+(dxacc)` are nonzero in OSAP and absent here. Coverage is
  not measurable from local files (Compustat not held); the translator states this in the docstring.
- Field-checker (not `verified_on`): revenue, cor, sgna, receivables, inventory, payables, deferredrev.
  No `fxusd` gate needed (within-filer `num/assets` is currency-invariant).

## 2. Variables: exactly the source names in the section 1 table; 12-calendar-month lags of
`rect, invt, xpp, drc, drlt, ap, xacc`.

## 3. Formula

```
num = (revt - cogs - (xsga - xrd))
      - (rect - l12.rect) - (invt - l12.invt) - (xpp - l12.xpp)
      + (drc + drlt - l12.drc - l12.drlt) + (ap - l12.ap) + (xacc - l12.xacc)
CBOperProf = num / at        # current-year at, not lagged
```
Operating profit before R&D, moved toward cash by the yoy working-capital changes, scaled by total assets.

**Trap:** Compustat `xsga` INCLUDES R&D, so `xsga - xrd` is SG&A ex-R&D. Sharadar `sgna` already
EXCLUDES R&D (`opex = sgna + rnd + oth`). The Sharadar profit term is `revenue - cor - sgna`; using
`sgna - rnd` would add R&D back twice. `rnd` is not an input.

Sharadar numerator (ART, yoy by reportperiod): `revenue - cor - sgna - d(receivables) - d(inventory)
+ d(deferredrev) + d(payables)`, over `assets`; `xpp`, `xacc` dropped.
`cor` embeds D&A for ~36% of non-financial rows and `sgna` for some (WMT, COST), so the profit term is
SHORT by embedded D&A there (median ~24% of their numerator; 42-47% decile moves). Compustat cogs/xsga
exclude D&A. Carry as approx; do not add `depamor` blindly.

## 4. Timing / lag; what ART-as-of-filing changes
- OSAP: annual `m_aCompustat`, fiscal year available at `datadate + 6 months`, carried 12 months.
  `l12` = row 12 calendar months earlier (prior fiscal year); a missing t-12 row gives NaN.
- Here: `ctx.fundamentals_yoy([...])`: latest ART filing (`datekey <=` signal, within 15 months)
  against the filing for the same period a year earlier, aligned by reportperiod (`tol_days=45`). No
  6-month lag; numerator is 0-3 months old, not 6-17; the change spans the latest four quarters and
  refreshes quarterly. Do not use `fundamentals(lag_months=12)` (wrong quarter ~15% of the time).
- Flow items `revenue`, `cor`, `sgna` enter as the CURRENT TTM LEVEL, no yoy difference: no TTM smear,
  `dimension=ARQ` NOT needed (an ARQ quarter would understate the profit term ~4x). The differenced items (`receivables`,
  `inventory`, `payables`, `deferredrev`) are balance-sheet LEVELS (ART == ARQ same-period 99.95-99.98%),
  so the yoy change is a clean 12-month change. `assets` is the latest ART level.

## 5. Filters (in OSAP's signal code)
`shrcd > 11` -> NaN (drops shrcd 12; moot under the domestic-common harness universe); `mve_c` missing
-> NaN (always present here); `BM = log(ceq/mve_permco)` missing -> NaN, which silently removes every
firm with **ceq < 0** (log of a negative is NaN; ceq == 0 gives -inf and survives); `at` missing -> NaN;
SIC 6000-6999 -> NaN. Sharadar: require `equity > 0`, `mkt_cap_usd > 0`, `assets > 0`; financials via
`ctx.ticker_meta(["siccode"])` (CURRENT code; the sanctioned use for a sample screen; 12-14% of names
changed SIC since 1998). Harness universe filters and OSAP's NYSE breakpoints / VW are not reproduced in the factor.

## 6. Predicted sign
SignalDoc Sign = +1 (high CBOperProf -> higher returns); `ascending=True`. OSAP: 0.47%/mo, t = 3.17,
LS quantile 0.1, NYSE filter, VW, 12-month holding, start month 6.

## 7. Mass-point question
- Do-nothing firm (all four balance-sheet deltas 0; xpp/xacc terms 0 here and in OSAP) scores
  `(revenue - cor - sgna)/assets`: continuous, firm-specific. A constant needs revenue, cor and sgna all
  exactly 0 AND every delta 0. Revenue exact-zero is 4% of ART (pre-revenue cohort, ~11% in 2020-25), but
  there `cor = 0` and `sgna > 0`, a distinct negative value, not a tie. Expected exact-tie share well
  under 1%; preflight measures the modal-value share. Zero DELTAS are common (deferredrev 64%,
  inventory level 46% zero, rect 18%) but only remove terms; the profit term carries the dispersion.
- Ties: guard `assets > 0`; the harness averages ranks over residual ties.
- Null handling (state in docstring): OSAP zero-fills `revt, cogs, xsga`, so a firm with no income
  statement scores a pure working-capital change. Here zero-fill `cor` and `sgna` ONLY when `revenue` is
  non-null in the same ART row; if `revenue` is null (early-1998 TTM gap, ~7% elsewhere) the score is NaN.
  Null `receivables/inventory/payables/deferredrev` (0.03-0.05%) -> 0 (OSAP's fill). A deviation (approx).

## 8. History needed (snapshot starts 1998-01)
No price window, no `history_months`; `lookback_months` ~27 as Accruals. ART TTM flows are ~50% populated 1998Q1-Q3 (levels ~99.9%); year-ago
levels exist from 1997Q4. Year-ago coverage is 47.9% at 1998-12 and 89.2% at 1999-03, so signal months
1999-01 and 1999-02 are thin by construction; expect a coverage dip there.

## 9. OSAP metadata

- `CBOperProf`; Cat.Signal Predictor; Cat.Economic `profitability`; continuous, Accounting; JFE 2016;
  sample 1963-2014; Acronym2 ProfCash; Predictability `1_clear`; replication quality `1_good`; cites 533.
- Code comment: OSAP does NOT lag assets (the 2016 paper does). Keep current `assets`.
- Versus the composite's Profitability leg (OSAP `OperProf`, `factors/composite.py`): OperProf =
  (revenue - cor - (sgna + rnd) - intexp) / equity, R&D and interest deducted, no financials screen,
  TTM level only. CBOperProf = (revenue - cor - sgna + working-capital yoy changes) / assets: R&D added
  back, interest not deducted, cash adjustment, asset denominator, financials and ceq <= 0 removed.
  Shared core `revenue - cor - sgna`; overlap is for Stage 2 residual IC to measure.

## 10. Proposed Sharadar mappings (deviations)

- `revenue` (ART TTM); `cor` and `sgna` zero-filled only when `revenue` is present; null `revenue` -> NaN.
- Profit core `revenue - cor - sgna` (NOT `sgna - rnd`); D&A embedding makes it short for embedders.
- `receivables, inventory, payables, deferredrev` ART yoy deltas via `fundamentals_yoy`, null -> 0;
  `deferredrev` once for drc + drlt. `xpp`, `xacc` dropped (approx).
- `assets > 0` denominator; `equity > 0` and `mkt_cap_usd > 0` stand in for a non-NaN log(BM).
- Financials excluded by current `TICKERS.siccode` 6000-6999; shrcd by the harness universe.

Declared inputs: `SF1.revenue, cor, sgna, receivables, inventory, payables, deferredrev, assets, equity`,
`TICKERS.siccode`. All keys are in the field map. `dimension` default ART.
