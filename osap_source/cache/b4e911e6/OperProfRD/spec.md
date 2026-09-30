# OperProfRD — Operating profitability, R&D adjusted (Ball et al. 2016, JFE, Table 4A; SignalDoc Acronym2 OperProfRD)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Signals/pyCode/Predictors/OperProfRD.py` (cached `predictor.py`; no upstream copies cached).
DATA_SHA 198b281de1a0. Written fresh from the source and `field_map_index.yaml` / `field_map.yaml`. Measured on the harness universe, 276 signal months
1998-12-31 .. 2021-11-30 (decision window 1999-01..2021-12), ART.

## 1. Data availability (verdict: APPROX, feasible; every input exists in Sharadar)
| OSAP input (`m_aCompustat`) | field_map key | Sharadar | status | OSAP missing-item rule |
|---|---|---|---|---|
| `revt` | `compustat.revt` | SF1 `revenue` (ART TTM) | mapped | NaN, not filled |
| `cogs` | `compustat.cogs` | SF1 `cor` (ART TTM) | approx (D&A embedded for some filers) | NaN, not filled |
| `xsga` | `compustat.xsga` | SF1 `sgna` + `rnd` (ART TTM) | approx (D&A embedded; sgna excludes R&D) | NaN, not filled |
| `xrd` | `compustat.xrd` | SF1 `rnd` (ART TTM) | mapped | zero-filled by the predictor (`tempXRD = xrd.fillna(0)`) |
| `at`, `ceq` | `compustat.at`, `compustat.ceq` | SF1 `assets`, `equity` (ART levels) | mapped / approx (equity includes preferred) | only tested non-null |
| `sicCRSP`, `shrcd`, `mve_c` | `crsp.siccd`, `crsp.shrcd`, `crsp.me` | TICKERS.siccode (current), universe, DAILY.marketcap | approx (current SIC) | filters |
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt. No unavailable input.
- SignalDoc text says "Replace all variables in the numerator with 0 if they are missing"; the CODE fills only xrd. The code is the authority and is followed: `revt`, `cogs`, `xsga` null -> NaN
  (CompustatAnnual `zero_fill_vars` contains none of them). Hence `cor == 0 -> NaN` (ruling `vendor_zero_fills`) and `sgna == 0 -> NaN` (decision grsaletogroverhead_xsga) both apply.
- MEASURED (harness universe, 276 months; bar 40%): coverage **70.7%** pooled n-weighted (mean 71.0%, min 42.7% at 1998-12, 64.5% min from 1999-03, **0 months < 40%**). Financials (SIC 6000-6999) are
  19.6% of the universe (13.2-22.3%), ceiling ~80.4%; before the SIC and `equity` screens the gated numerator is non-null for 81.7% of the universe.

## 2. Variables (exact source names)
`xrd, revt, cogs, xsga, at, ceq` (annual Compustat, $ millions); SignalMasterTable `exchcd, sicCRSP, mve_c, shrcd`; `gvkey, permno, time_avail_m`.

## 3. Formula
```
tempXRD    = xrd.fillna(0)
OperProfRD = (revt - cogs - xsga + tempXRD) / at
keep if shrcd <= 11 & mve_c notnull & ceq notnull & at notnull & not (6000 <= sicCRSP < 7000); drop if OperProfRD missing
```
Compustat `xsga` INCLUDES R&D, so `- xsga + xrd` leaves SG&A excluding R&D: operating profit before R&D expense, over total assets. No winsorising, no industry adjustment.
In Sharadar, `sgna` already excludes R&D, so with xsga = sgna + rnd the `rnd` terms CANCEL: OperProfRD = (revenue - cor - sgna) / assets. MEASURED: max |difference| between the two forms is 0 over all scored
names and months, so `rnd` is not an input and its vendor zero-fill is moot (rnd > 0 for 41.4% of scored names, 37-50%/month).

## 4. Timing / lag convention
- OSAP: annual values at `datadate + 6 months`, held until the next record (Portfolio Period 12, Start Month 6). SignalDoc Notes: the paper lags the denominator, the JFE version does not, OSAP does not lag it.
- Here: SF1 ART at the latest filing (0-3 months old). Numerator flows are TTM sums and `assets` a same-date level: no year-over-year difference, no smear, no `dimension=ARQ` override.
  ART-as-of-filing makes the ratio 6-15 months fresher than OSAP's and moves it up to four times a year.

## 5. Filters
Exclude SIC 6000-6999 (OSAP uses `sicCRSP`, time-varying; here `TICKERS.siccode`, the CURRENT classification; universe null siccode 0.0%, measured). `shrcd <= 11` is the universe
(Domestic Common Stock); `mve_c` non-null holds for every universe member; `ceq` (equity) and `at` must be non-null (0.05% null, immaterial). Also `assets > 0` (a zero denominator gives inf in OSAP).
SignalDoc `Filter` is empty; the LS is VW decile with NYSE breakpoints (Stock Weight VW, LS Quantile 0.1) in OSAP, portfolio-stage, not reproduced.

## 6. Predicted sign
SignalDoc `Sign = +1.0` (high R&D-adjusted profitability -> high future return). `Cat.Form` continuous; `Cat.Economic` profitability; `Cat.Data` Accounting. Long HIGH: `ascending=True`.

## 7. The mass-point question
- A do-nothing firm holds all inputs fixed between filings: the ratio is constant and price-independent, not a mass point. Ties need identical (revenue - cor - sgna)/assets across names.
- MEASURED modal-value share of the scored cross-section: **0.07% mean, 0.16% max** over 276 months; distinct values == n scored (mean 1,390; range 974-2,106); 10 bins every month.
- Zero `sgna` or zero `cor` (vendor zero-fills) would make revenue-only numerators; both are gated to NaN, so the do-nothing row is excluded rather than placed at a level.
- Tie handling: rank average. Negative profit kept (as OSAP).

## 8. History needed (snapshot starts 1998-01)
One latest filing; no `history_months`. ART coverage 42.7% at 1998-12, 62.8% mean in 1999, 70-73% from 2001: data-start thin, not a gate.

## 9. OSAP metadata (SignalDoc)
Acronym OperProfRD; Ball et al.; 2016; JFE; Cat.Signal Predictor; Predictability in OP 2_likely; Signal Rep Quality 1_good; Cat.Form continuous; Cat.Data Accounting; Cat.Economic profitability;
Sample 1963-2014; Key Table 4A Oper PRof; Test port sort; Sign +1.0; Return 0.29; T-Stat 1.84; VW; LS Quantile 0.1; Quantile Filter NYSE; Portfolio Period 12; Start Month 6; GScholarCites 533.
Definition: "Revenue (revt) minus cost (cogs) - (administrative expenses (xsga) - R&D expenses (xrd)), all divided by total assets (at) in year t."

## 10. Proposed Sharadar mappings and deviations
```
f   = ctx.fundamentals(["revenue", "cor", "sgna", "assets", "equity"])            # ART; rnd cancels, not read
fin = ctx.ticker_meta(["siccode"])["siccode"]; nonfin = fin.notna() & ~((fin >= 6000) & (fin < 7000))
ok  = nonfin & f.equity.notna() & (f.assets > 0) & (f.cor != 0) & f.sgna.notna() & (f.sgna != 0)
OperProfRD = ((f.revenue - f.cor - f.sgna) / f.assets).where(ok)                    # ascending=True
```
Deviations: (a) D&A is EMBEDDED in `cor`/`sgna` for some filers (Compustat excludes it): the numerator is LOWER by the embedded amount (field_map xsga note: >=90% embedded on ~36% of rows, median
emb/assets 0.034 on those = ~24% of their numerator; rank rho vs the add-back version 0.968 / 0.956 / 0.949 at 1999/2008/2020, 45-52% of names change decile) - the main reason for approx;
(b) `cor == 0 -> NaN`, `sgna == 0 -> NaN` (vendor zero-fills; OSAP fills neither); (c) `rnd` cancels, so no R&D input; (d) SIC is current, not point-in-time; `equity` includes preferred (immaterial as a non-null test);
(e) ART at filing vs annual at datadate + 6 months; (f) SignalDoc VW NYSE-breakpoint deciles not reproduced. Fields not in the map: none. `FactorDef`: ART default, no `history_months`, `family=None` until Phase C.

## 11. Overlap with the v0 Profitability leg (facts only)
- v0 `_profitability` (factors/composite.py, seed from Fama-French RMW): `(revenue - cor - (sgna + rnd + intexp)) / equity`, family `profitability`. Shared core: `revenue - cor - sgna` (same SF1 columns, ART).
  Differences: v0 also subtracts `rnd` and `intexp` and divides by book `equity`, not `assets`; v0 has no `cor == 0` gate and no financials exclusion. SignalDoc `Cat.Economic` is `profitability`, the v0 leg's category.
