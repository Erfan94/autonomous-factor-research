# GP — Gross profitability (Novy-Marx 2013, JFE, Table 2a; SignalDoc Acronym2 ProfGross)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Signals/pyCode/Predictors/GP.py` (cached `predictor.py`,
`upstream_CompustatAnnual.py`, `upstream_SignalMasterTable.py`). DATA_SHA 198b281de1a0. Written fresh from the source and
`field_map_index.yaml` / `field_map.yaml`. Measured on the harness universe, 276 signal months 1998-12-31 .. 2021-11-30 (decision window 1999-01..2021-12), ART.

## 1. Data availability (verdict: APPROX, feasible; every input exists in Sharadar)
| OSAP input (`m_aCompustat`) | field_map key | Sharadar | status | OSAP missing-item rule |
|---|---|---|---|---|
| `revt` | `compustat.revt` | SF1 `revenue` ART (TTM sum) | mapped | NaN, not zero-filled |
| `cogs` | `compustat.cogs` | SF1 `cor` ART (TTM sum) | approx (D&A embedded for some filers) | NaN, not zero-filled |
| `at` | `compustat.at` | SF1 `assets` ART (level) | mapped | NaN; at == 0 gives inf, which OSAP keeps |
| `sic` | `compustat.sic` | TICKERS.siccode (CURRENT) | mapped (deviation: current, not point-in-time) | NaN sic -> dropped by the `<6000 or >=7000` test |
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt. No unavailable input and no zero-filled optional term.
- Ruling `vendor_zero_fills`: Sharadar zero-fills `cor` for non-reporters and OSAP does NOT zero-fill `cogs`, so `cor == 0 -> NaN` (the ruling names GP).
  Measured share of universe names with `cor == 0` (non-financial): 2.83% pooled (1.1% at 1998-12, 7.0% max).
- SF1 also carries `gp` (= revenue - cor per DESCRIPTIONS, same zero-fill); build from the components so the `cor` gate is visible.
- MEASURED coverage (pooled n-weighted over 276 months; bar 40%): **74.4%** with the `cor == 0` gate and non-financial filter (per-month mean 74.6%; min 46.0%
  at 1998-12..1999-02 where ART TTM flows are thin, >= 70% from 1999-03; 0 months under 40%, 3 under 60%). Without the `cor` gate 77.2%. Financials (SIC 6000-6999) are
  19.4% of the universe (13.2-22.3%), so ~80.6% is the ceiling; the v0 Profitability leg's coverage for comparison is 93.2%.

## 2. Variables (exact source names)
`revt, cogs, at, sic` (annual Compustat, $ millions), `gvkey, permno, time_avail_m, datadate`.

## 3. Formula
```
keep if sic < 6000 or sic >= 7000          # non-financial; NaN sic fails both and is dropped
GP = (revt - cogs) / at
drop if GP missing
```
Gross profit over total assets. No winsorising, no log, no industry adjustment; `inf` (at == 0) is not filtered in OSAP (`at` exact-zero is 0.01% of rows).

## 4. Timing / lag convention
- OSAP: annual `revt`, `cogs`, `at` from the fiscal year ending at `datadate`, available at datadate + 6 months, held 12 months (latest datadate wins).
- Here: SF1 ART at the latest filing (0-3 months old, cap `max_fundamental_age_months`); `revenue`, `cor` are TTM sums, `assets` a level. Both numerator terms are flows over the
  same four quarters and the denominator is the same-date level: no year-over-year difference, no smear, no `dimension=ARQ` override.
  `fxusd` cancels in the SF1/SF1 ratio. ART-as-of-filing makes the ratio 6-15 months fresher than OSAP's and moves it up to four times a year rather than once.

## 5. Filters
Financial exclusion (above), matched here with `TICKERS.siccode` via `ctx.ticker_meta(["siccode"])`: `nonfin = siccode.notna() & ~((siccode >= 6000) & (siccode < 7000))`
(universe null siccode 0.00% at every probe). SignalDoc `Filter` is empty; the LS is VW quintile 0.2 in OSAP, portfolio-stage, not reproduced.

## 6. Predicted sign
SignalDoc `Sign = +1.0` (high GP -> high future return); `Cat.Form` continuous; `Cat.Economic` profitability; Stock Weight VW; LS Quantile 0.2; Portfolio Period 12; Start Month 6.
Long HIGH GP. `ascending=True`.

## 7. The mass-point question
- A do-nothing firm (no new filing) holds all three inputs fixed, so GP is constant between filings; nothing in GP moves with price. That is a fundamental ratio held between filings, not a
  mass point: ties require identical (revenue - cor)/assets across names.
- MEASURED modal value share of the scored cross-section (with the `cor == 0` gate): 0.07% mean, **0.15% max** over 276 months; 10 qcut bins every month. Without the gate the max is
  **4.30%** (the `cor == 0` names take GP = revenue/assets, a different quantity; not a tie at the decile cliff of 10%, but it places non-reporters high), which is why the gate is part of the construction.
- `at == 0` names: `assets` exact-zero 0.01% of rows; guard `assets > 0` anyway (a zero denominator gives inf, a negative one a sign flip).
- Negative GP (revenue < cor) is kept, as OSAP does. Tie handling: rank average.

## 8. History needed (snapshot starts 1998-01)
One latest filing; no `history_months`, no `lookback_months` beyond the filing-age cap. SF1 ART from 1997Q4; ART revenue/cor coverage is 57% at 1998-12 and 92% from 1999-03
(the flow warm-up), so the first three decision months score ~46% of the universe. Not a gate.

## 9. OSAP metadata (SignalDoc)
Acronym GP; Acronym2 ProfGross; Novy-Marx; 2013; JFE; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form continuous; Cat.Data Accounting;
Cat.Economic profitability; Sample 1963-2010; Key Table 2a; Test port sort; Sign +1.0; Return 0.31; T-Stat 2.49; VW; LS Quantile 0.2; Portfolio Period 12; Start Month 6; no Filter.
Definition: "Revenue (sale) - cost of goods solds (cogs), divided by total assets (at). Drop if financial." SignalDoc Notes: Tab 2a says NYSE breakpoints, the OSAP code is closer with all-stock breakpoints.
The SignalDoc text says `sale`; the code reads `revt`. Both map to SF1 `revenue`.

## 10. Proposed Sharadar mappings and deviations
```
f   = ctx.fundamentals(["revenue", "cor", "assets"])                       # ART
ok  = siccode.notna() & ~((siccode >= 6000) & (siccode < 7000)) & (cor != 0) & (assets > 0)
GP  = ((revenue - cor) / assets).where(ok)                                  # ascending=True; revenue or cor null -> NaN
```
Deviations: (a) `cor` is as-reported cost of revenue and INCLUDES D&A for some filers (INTC/MU/TXN class) where Compustat `cogs` excludes it, so gross profit is lower for those names;
(b) `cor == 0 -> NaN` (vendor zero-fill, ruling); (c) SIC is the CURRENT classification, not point-in-time; (d) ART at filing vs annual at datadate + 6 months; (e) `assets` is the latest filing's
level, not fiscal-year-end; (f) no `fxusd` gate needed (ratio of two SF1 fields); (g) SignalDoc VW quintile portfolios are not reproduced. Fields not in the map: none.
`FactorDef`: ART default, no `history_months`, `family=None` until Phase C.

## 11. Overlap with the v0 Profitability leg (facts only)
- v0 `_profitability` (factors/composite.py, seed from Fama-French RMW): `(revenue - cor - (sgna + rnd + intexp)) / equity`, `equity > 0`, no financials exclusion, family `profitability`.
- Shared: the term `revenue - cor` (same SF1 columns, same ART dimension). Differences: v0 also subtracts `sgna`, `rnd`, `intexp` (missing expense items zero-filled if at least one is
  present); the denominator is `equity` (book), not `assets`; v0 applies neither the `cor == 0` gate nor the SIC 6000-6999 exclusion.
- SignalDoc `Cat.Economic` for GP is `profitability`, the category that seeds the v0 leg's family.
- Measured cross-sectional Spearman of the RAW scores (universe scope, not within-sector ranks) over the names scored by both, 276 months: mean 0.33, median 0.32, range 0.19-0.48,
  about 1,409 co-scored names per month on average (1,022-2,120).
