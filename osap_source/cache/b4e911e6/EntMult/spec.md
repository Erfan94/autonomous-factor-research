# EntMult — enterprise multiple (Loughran and Wellman 2011, JFQA, Table 3B)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/EntMult.py` (cached `predictor.py`, `upstream_CompustatAnnual.py`, `upstream_SignalMasterTable.py`, `upstream_CRSPMonthly.py`).
Written fresh from the source and `field_map_index.yaml`. Map statuses are mappings, not proofs; the numbers in 5/7 were measured on THIS snapshot (DATA_SHA 198b281de1a0) with a scratch replica over the harness universe, not the harness preflight.

## 1. Data availability — VERDICT: APPROX, feasible (no unavailable input that OSAP does not itself zero-fill)

| OSAP input | field_map key | Sharadar | map status | OSAP missing-item rule |
|---|---|---|---|---|
| `mve_permco` (company market value, month t, SMT) | `crsp.mve_permco` | `ctx.universe["mkt_cap_usd"]` (DAILY.marketcap, company-level, x1e6 at panel build) | approx | SMT row required (inner merge) |
| `dltt` (long-term debt) | `compustat.dltt` | SF1 `debt` (with `dlc`; see `compustat.dltt_plus_dlc`), NOT `debtnc` alone | dltt approx (ASC 842), dltt_plus_dlc mapped | NOT zero-filled: NaN -> EntMult NaN |
| `dlc` (debt in current liabilities) | `compustat.dlc` | inside SF1 `debt` (debtc is the component/gate) | mapped | NOT zero-filled: NaN -> NaN |
| `dc` (convertible debt; the SignalDoc text says "deferred charges", the code builds it from dcvt/dcpstk) | `compustat.dc` | none (unavailable) | unavailable | ZERO-FILLED by OSAP (`zero_fill_vars`) -> use 0, identical to OSAP's missing case; differs only for convertible issuers |
| `che` (cash and short-term investments) | `compustat.che` | `cashneq + investmentsc.fillna(0)` | approx | ZERO-FILLED by OSAP (`che` in `zero_fill_vars`) |
| `oibdp` (operating income before depreciation) | `compustat.oibdp` | `opinc + depamor` (TTM, ART) | approx (remapped; NOT SF1 `ebitda`) | not filled: NaN -> NaN |
| `ceq` (common equity, for the filter) | `compustat.ceq` | SF1 `equity` (includes preferred) | approx | not filled; `NaN < 0` is False so a missing ceq does NOT exclude (despite the SignalDoc text) |

- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt. The only missing item, `dc`, is in OSAP's zero-fill list (upstream_CompustatAnnual.py), hence approx, not infeasible.
- RULINGS applied: (i) SF1.debt users gate on `debtc.notna()`. (ii) "unclassified balance sheets never zero-filled": `investmentsc` is null on the same ~20% unclassified block as `debtc`, so `investmentsc.fillna(0)` would zero-fill an unclassified item there; the `debtc.notna()` gate removes exactly those rows, so the gate serves both rulings. SF1.debt itself is populated on those rows (null 0.03%), which is why the gate is needed, not optional.
- No field outside the map: `debt, debtc, cashneq, investmentsc, opinc, depamor, equity, fxusd` all have keys; `ctx.universe["mkt_cap_usd"]` per `crsp.mve_permco`.

## 2. Variables (exact source names)
`dltt, dlc, dc, che, oibdp, ceq, gvkey, permno, time_avail_m` (m_aCompustat, annual, zero-filled for dc and che), `mve_permco` (SignalMasterTable, month t, $ millions).

## 3. Formula in words and key lines
Enterprise value (market value of equity plus debt plus convertible debt minus cash and short-term investments) over operating income before depreciation; missing when equity is negative or operating income is negative. Low multiple = cheap.
```
df["EntMult"] = (df["mve_permco"] + df["dltt"] + df["dlc"] + df["dc"] - df["che"]) / df["oibdp"]
df.loc[(df["ceq"] < 0) | (df["oibdp"] < 0), "EntMult"] = np.nan ; dropna(subset=["EntMult"])
```
Quirk: `oibdp == 0` is NOT excluded (only `< 0`), so EV/0 = +/-inf survives `dropna` in OSAP's output. Here set NaN (0-1 names per probe month measured).

## 4. Timing / lag convention
OSAP: annual Compustat at `datadate + 6 months`, held 12 months (6-17 months stale), with month-t market value. Here: ART TTM flow (`opinc + depamor`) and latest-filing balance sheet (0-3 months old) with the month-end market cap: a level ratio on a TTM flow, no year-over-year difference, no smear, no `dimension` override. The market value is contemporaneous with the signal month in both (OSAP takes `mve_permco` at t, not t-6).
ART vs ARY: ARY is the faithful annual alternative (stale 0-12 months); ART is the project default, log the choice.

## 5. Filters and measured coverage
Reproduce: `ceq < 0 -> NaN` (here `equity < 0`), `oibdp < 0 -> NaN`. Add: `M > 0`, `EV = M + debt - che` must be > 0 (measured 0-3 negative-EV names per probe month), `fxusd == 1` (numerator in USD cap; non-USD filers 1-64 names, 1 by 2015), non-finite -> NaN. SignalDoc has no Filter.
Measured (harness universe at month-end signal dates; EntMult non-null / universe names), WITH the `debtc.notna()` gate vs WITHOUT (ruling would not allow it; shown for cost only):

| signal | univ | with gate | without | opinc+depamor non-null | oibdp<0 (of non-null) | debtc null |
|---|---|---|---|---|---|---|
| 1999-01 | 2386 | 36.8% | 47.0% | 52.6% | 9.3% | 20.2% |
| 1999-06 | 2417 | 61.0% | 78.2% | 89.9% | 11.6% | 19.7% |
| 1999-12 | 2674 | 57.0% | 70.5% | 85.0% | 15.8% | 17.4% |
| 2001-01 | 2419 | 59.3% | 74.1% | 90.0% | 16.6% | 16.4% |
| 2003-01 | 1941 | 65.4% | 82.9% | 95.7% | 12.1% | 19.7% |
| 2010-06 | 1789 | 73.2% | 87.5% | 97.5% | 8.3% | 17.8% |
| 2015-06 | 1928 | 66.0% | 85.0% | 96.2% | 8.9% | 20.4% |
| 2021-11 | 2312 | 54.7% | 72.2% | 92.3% | 17.8% | 18.7% |

The 1999-01 shortfall is ART warm-up (TTM needs four quarters; opinc+depamor non-null only 52.6% that month, 89.9% by 1999-06), not the gate. The gate costs about 13-18 pp of coverage in every later probe month (financials/REITs/unclassified names); preflight will WARN on the first probe month (< 40%), not hard-fail. The Stage 1 bar is 40% on the window mean, expected ~55-70% in the scored months.

## 6. Predicted sign
SignalDoc `Sign = -1.0` (low enterprise multiple -> high returns); Return 0.95, T-Stat 6.54; Stock Weight EW; LS Quantile 0.1; Portfolio Period 12; Start Month 6; Cat.Form continuous; Cat.Economic valuation. `FactorDef(ascending=False)`.

## 7. The mass-point question
- Do-nothing firm: no new filing leaves debt, cash and EBITDA fixed but M moves with the price every month, so EntMult changes continuously: no stale-value default.
- Exact 0 needs EV = 0; measured none. Among scored names the modal value is 0.07-0.11% of the cross-section with 880-1,530 distinct values (1999-01 has the fewest on a thin sample). No mass point; ties: `rank(method="average")`.
- Distribution: heavy right tail (p1 / median / p99 measured 3.2 / 15.0 / 531 at 2021-11; 2.5 / 11.3 / 635 at 1999-12; 3.7 / 12.3 / 150 at 2015-06); rank-based harness, no winsorising in the factor.
- The scored cross-section excludes loss-makers and equity-negative names (oibdp<0 8-18% of non-null, equity<0 a few %): a coverage reduction, not a mass.

## 8. History needed (snapshot starts 1998-01)
One ART filing with four quarters (first full 1998Q4 filed early 1999), the filing-date debt/cash/equity, and the month-end cap. No return window, no `history_months` (no SEP input), `lookback_months` 0. Earliest decision 1999-01 (36.8% coverage, rising to 61% by 1999-06).

## 9. OSAP metadata (SignalDoc)
Acronym EntMult; Acronym2 EntMult; Loughran and Wellman; 2011; JFQA; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form continuous; Cat.Data Accounting; Cat.Economic valuation;
SampleStart 1963, End 2009; Key Table "3B"; Test "port sort CAPM alpha"; Sign -1.0; Return 0.95; T-Stat 6.54; EW; LS Quantile 0.1; Portfolio Period 12; Start Month 6; Filter blank.
Notes: "Table 3 Panel B. Table 3A shows raw returns but no t-stats." Definition: "Market value of equity + long-term debt (dltt) + debt in current liabilities (dlc) + deferred charges (dc) - cash and short-term investments (che), divided by operating income (oibdp). Exclude if missing book equity or negative operating income."

## 10. Proposed Sharadar mappings and deviations
```
M      = ctx.universe["mkt_cap_usd"]                                   [crsp.mve_permco, approx]
debt   = SF1.debt  where SF1.debtc.notna()  else NaN                   [dltt+dlc; ruling: SF1.debt users gate on debtc.notna()]
dc     = 0                                                             [unavailable; OSAP zero-fills dc]
che    = SF1.cashneq + SF1.investmentsc.fillna(0)                      [approx; inside the debtc gate]
oibdp  = SF1.opinc + SF1.depamor  (ART)                                [approx; NOT SF1.ebitda]
EntMult = (M + debt + dc - che) / oibdp ;  equity<0, oibdp<=0, M<=0, EV<=0, fxusd!=1, non-finite -> NaN ;  ascending=False
```
Deviations: (a) `debt` includes ASC 842 operating-lease liabilities from FY2019 filings (EV is overstated for lessees after adoption) and is reporting-currency (hence the `fxusd == 1` gate); (b) `dc` = 0 understates EV for convertible issuers; (c) `che` includes financing receivables for captive-finance names (CSCO/F/GM-type) and is understated on unclassified names (removed by the gate); (d) `oibdp` uses `depamor` (cash-flow statement D&A, 0-filled when absent; 3.8% of rows) and top-down `opinc`, agreeing with Compustat oibdp approximately; (e) `equity` includes preferred (OSAP ceq excludes it), affects only the sign filter; (f) filing-date TTM (0-3 months) vs annual at datadate+6; (g) `oibdp == 0 -> NaN` (OSAP would carry inf) and the added M > 0 / EV > 0 guards; (h) mve_permco from DAILY.marketcap (primary-class ticker, all-class shares), a few-percent difference on <= 2% of names. `FactorDef`: default dimension ART, inputs `SF1.debt, SF1.debtc, SF1.cashneq, SF1.investmentsc, SF1.opinc, SF1.depamor, SF1.equity, SF1.fxusd`, `family=None` until Phase C.
