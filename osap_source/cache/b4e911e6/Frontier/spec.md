# Frontier — Efficient frontier index (Nguyen and Swanson 2009, JFQA, Table 4A Spread; SignalDoc Acronym2 EffFrontier)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Signals/pyCode/Predictors/Frontier.py` (cached `predictor.py`,
`upstream_CompustatAnnual_zerofill_excerpt.py`, `upstream_CRSPMonthly_mve_excerpt.py`, `upstream_legacy_stata.do`).
DATA_SHA 198b281de1a0. Written fresh from the source and `field_map_index.yaml` / `field_map.yaml`. Measured on the harness universe,
276 signal months 1998-12-31 .. 2021-11-30 (the decision window 1999-01..2021-12), `build_universe` + `MonthContext`, ART.

## 1. Data availability (verdict: PREFLIGHT_FAILED on coverage under the rulings in force; mechanics feasible)
| OSAP input (`m_aCompustat`/SMT) | field_map key | Sharadar | status | OSAP missing-item rule |
|---|---|---|---|---|
| `ceq` | `compustat.ceq` | SF1 `equity` ART | approx (incl. preferred) | NaN; `log(ceq)` and final filter need ceq > 0 |
| `dltt` | `compustat.dltt` | SF1 `debtnc` ART | approx (ASC 842 leases in) | NaN, not zero-filled |
| `at`, `sale` | `compustat.at`, `.sale` | SF1 `assets`, `revenue` (ART TTM) | mapped | NaN; ratio NaN if denominator 0 or NaN |
| `capx` | `compustat.capx` | SF1 `-capex` (outflow sign) | mapped | NaN, not zero-filled |
| `xrd` | `compustat.xrd` | SF1 `rnd` | mapped, vendor zero-fill | NOT zero-filled: non-reporters drop out |
| `xad` | `compustat.xad` | none | UNAVAILABLE | ZERO-FILLED by Frontier itself (`df["xad"].fillna(0)`; also `xad0` upstream) |
| `ppent` | `compustat.ppent` | SF1 `ppnenet` | mapped (vendor 0 = missing) | NaN (OSAP forward-fills, never zero-fills) |
| `ebitda` | `compustat.ebitda` | SF1 `opinc + depamor` | approx (remapped) | NaN, not zero-filled |
| `mve_permco` | `crsp.mve_permco` | DAILY.marketcap x1e6 = `mkt_cap_usd` | approx | SMT row required |
| `sicCRSP` -> FF48 | `crsp.siccd` | TICKERS.siccode (CURRENT) via `harness.industry.ff48` | approx | no FF48 -> row dropped |

- No IBES/options/13F/patents/segments/ratings/pensions/ob/emp/ppegt. `xad` is unavailable but OSAP zero-fills it inside the predictor, so the
  missing-item rule allows it (approx, not infeasible): with xad = 0 for every firm, `tempAdv = 0/sale = 0` is a constant regressor and drops out of the fit.
- **The binding item is `xrd`.** Ruling in force (`compustat.xrd` map entry, names Frontier): a bare `xrd/sale` regressor drops Compustat non-reporters, so
  treat `rnd == 0` as missing (genuine reported zeros are dropped too; the two cannot be separated).
- MEASURED coverage of the scored set (Stage 1 pools audit rows over months; bar `min_coverage_pct` 40):
  | construction | pooled coverage (n-weighted, 276 mo) | per-month mean | per-month min / max | months >= 40% |
  |---|---|---|---|---|
  | faithful: `rnd != 0` AND all other gates (sale, at != 0, equity > 0, debtnc, capex, opinc+depamor, ppnenet non-null) | **30.07%** | 30.0% | 14.5 / 38.5 | **0 of 276** |
  | `rnd != 0` gate alone | 31.9% | 31.8% | 17.1 / 41.4 | 4 |
  | rnd == 0 KEPT as 0 (deviation from OSAP), all other gates | 74.4% | 74.6% | 40.0 / 79.8 | 276 |
  | same, without the debtnc gate | 92.2% | 92.6% | 50.3 / 96.8 | 276 |
  - Share of non-null ART `rnd` that is exactly 0 in the universe: 67.0% mean (56.6-70.7%). `debtc` and `debtnc` both non-null (the gate as measured): 81.1% mean (78.3-85.8%).
    `equity > 0`: 96.4%. `revenue` non-null and nonzero: 95.9% mean (57.2% at 1998-12, 92% from 1999-03). `capex`/`opinc+depamor` non-null 96.1% (52% at 1998-12).
- Recommendation under the ruling in force: **preflight_failed / coverage floor** (0 of 276 months reach 40%, best month 38.5%). The keep-as-0 variant
  clears the floor but is a different signal (R&D-less firms enter the regression with `tempRD = 0`), not OSAP's; it is recorded here only so a later
  overturn of the `xrd` ruling has its number. Mechanics are not the obstacle: the harness supports the pooled regression (`market_context()`,
  `fundamentals_at_month_ends(scope="market")`; its docstring names Frontier).

## 2. Variables (exact source names)
`permno, time_avail_m, mve_permco, sicCRSP` (SignalMasterTable); `at, ceq, dltt, capx, sale, xrd, xad, ppent, ebitda` (`m_aCompustat`, $ millions).

## 3. Formula (the code, not the SignalDoc text, is the authority)
```
YtempBM   = log(mve_permco)                      # dependent variable is log MARKET VALUE (name says BM); legacy .do used mve_c
tempBook  = log(ceq);  tempLTDebt = dltt/at;  tempCapx = capx/sale;  tempRD = xrd/sale
tempAdv   = xad/sale (xad filled with 0);  tempPPE = ppent/at;  tempEBIT = ebitda/at     # denominators 0 or NaN -> NaN
tempFF48  = sicff(sicCRSP, 48);  drop rows with no FF48
for each calendar month t:
    train = rows with time_avail in (t-60, t], all of YtempBM and the 7 regressors non-null        # rolling 60 months, pooled
    OLS(YtempBM ~ 7 regressors + 48 FF48 dummies + const) on train (sklearn LinearRegression, needs >= 3 rows)
    predict for the month-t rows with the 7 regressors non-null
Frontier = -(YtempBM - logmefit_NS)             # minus the residual of log market value
drop if ceq missing or ceq <= 0
```
High Frontier = market value below what the fundamentals-and-industry fit predicts. No winsorising, no standardising.

## 4. Timing / lag convention
- OSAP: annual items available at datadate + 6 months, each annual row replicated for 12 months; `mve_permco` is month t. The pooled 60-month window
  therefore holds each firm-year up to 12 times with different market values. Prediction month t uses the same month's cross-section.
- Here: ART at the latest filing (0-3 months old) and month-end `mkt_cap_usd`; one row per firm-month. Every regressor is a ratio of levels or TTM flows
  (capex, revenue, opinc + depamor are ART TTM sums; assets, equity, debtnc, ppnenet are levels): no year-over-year difference, no smear, no
  `dimension=ARQ` override. The pooled training rows must each use the filing known at THEIR month-end (`fundamentals_at_month_ends`).

## 5. Filters
SignalDoc `Filter` "exchcd in 1,2,3, shrcd <= 11" is the SMT sample (universe here). `ceq > 0` and FF48 non-null are in the code. No price or size screen.

## 6. Predicted sign
SignalDoc `Sign = +1.0`; `Cat.Form` continuous; `Cat.Economic` valuation; Stock Weight EW; LS Quantile 0.1. Long HIGH Frontier. `ascending=True`.

## 7. The mass-point question
A do-nothing firm holds its regressors between filings but `mve_permco` changes monthly, so Frontier changes monthly; the fitted value also moves
as the window rolls. No stale-value mass point; exact ties are not expected (continuous residual). The mass point is structural at the INPUT: 67% of the
universe has `rnd == 0` and (faithful rule) drops out rather than tying. Not measured as a mode (the regression was not run); expected mode share ~0%.
Tie handling: rank average. The constant `tempAdv` column makes the design rank-deficient; the fit must use a minimum-norm/pseudo-inverse solve.

## 8. History needed (snapshot starts 1998-01)
60 months of market-scope rows. Measured pooled gated rows in the training window: 11,363 (13 lags) at 1998-12, 20,655 (19 lags) at 1999-06,
107,755 (60 lags) at 2003-12, 87,995 at 2010-12, 74,846 at 2021-11 (market scope, faithful gates); current-month gated names 897 / 1,800 / 1,646 / 1,319 / 1,389.
OSAP fits on whatever window exists (>= 3 rows), so 1999-2002 is a short-window approximation, not a gate. Lags before SF1 1997Q4 / SEP 1997-12 are empty.
If built: `history_months` would need the market-scope window; per-month compute 0.1-3 s for the data pull plus one ~100k x 56 least-squares solve.

## 9. OSAP metadata (SignalDoc)
Acronym Frontier; Acronym2 EffFrontier; Nguyen and Swanson; 2009; JFQA; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good;
Cat.Form continuous; Cat.Data Accounting; Cat.Economic valuation; Sample 1980-2003; Key Table 4A Spread; Test port sort; Sign +1.0; Return 0.96; T-Stat 4.86;
EW; LS Quantile 0.1; Portfolio Period 12; Start Month 6; Filter `exchcd%in%c(1,2,3),shrcd<=11`. Definition: residual of log(BM) on log(ceq), dltt/at, capx/sale,
xrd/sale, xad/sale, ppent/at, ebitda/at and FF48 dummies, 60-month rolling.

## 10. Proposed Sharadar mappings and deviations (only if the `xrd` ruling is overturned or the variant is chosen)
```
Y  = log(mkt_cap_usd)                      ceq -> log(equity) (equity > 0)        dltt -> debtnc (null -> NaN; NOT a debtc gate, which is for SF1.debt users)
at -> assets; sale -> revenue; capx -> -capex; xrd -> rnd (faithful: rnd == 0 -> NaN); xad -> 0 (constant column); ppent -> ppnenet; ebitda -> opinc + depamor
FF48 -> harness.industry.ff48(TICKERS.siccode);  pooled market-scope OLS over t-59..t, pinv solve;  Frontier = -(Y - fitted)
```
Deviations: (a) `xad` always 0 (no effect on the fit); (b) `rnd == 0` treated as missing - drops genuine zero reporters; (c) `-capex` sign flip; (d) `ebitda` =
opinc + depamor is top-down EBITDA, SF1.ebitda (bottom-up) rank rho ~0.94-0.96 with it, the choice matters for a regressor; (e) `equity` includes preferred;
(f) `debtnc` includes ASC 842 operating leases from FY2019 (a level shift within the pooled window) and is null on ~20% (unclassified balance sheets, never zero-filled);
(g) `ppnenet` zero = missing, OSAP drops never-reported names, here kept at 0; (h) FF48 from CURRENT siccode (12-14% reclassified), 99.47% of market names mapped;
(i) `mkt_cap_usd` company-level at the primary's price; (j) no 6-month annual lag, no 12x replication weighting; (k) market-scope cross-section and pool, not the harness
universe. Fields not in the map: none. `FactorDef`: ART default, `family=None` until Phase C.
