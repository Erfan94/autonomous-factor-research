# NetDebtPrice — Net debt to price (Penman, Richardson and Tuna 2007, Table 4A): (debt + preferred stock + pref. dividends in arrears - treasury preferred - cash) / market equity, non-financials in the upper three book-to-market quintiles

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/NetDebtPrice.py` (cached `predictor.py`; upstream `upstream_CompustatAnnual.py`, `upstream_SignalMasterTable.py` beside it). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`. Measurements: harness universe, 276 decision months (signals 1998-12-31 .. 2021-11-30), recorded snapshot, scratch measurement (no factor file).

## 1. Data availability (verdict: DATA_UNAVAILABLE -> recommend `infeasible`; `pstk` has no SF1 field and OSAP does NOT zero-fill it)

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `dltt` + `dlc` | `compustat.dltt_plus_dlc` | `SF1.debt` (gate `debtc.notna()`) | mapped (ASC 842 leases inside) | not zero-filled; NaN propagates |
| **`pstk`** preferred stock | `compustat.pstk` | none | **unavailable** | **NOT in `zero_fill_vars`: a missing pstk makes the whole numerator NaN** |
| `dvpa` pref. dividends in arrears | `compustat.dvpa` | none | unavailable | zero-filled by OSAP (`zero_fill_vars`) -> can be dropped as 0 |
| `tstkp` treasury preferred | `compustat.tstkp` | none | unavailable | zero-filled by OSAP -> can be dropped as 0 |
| `che` | `compustat.che` | `cashneq + investmentsc.fillna(0)` | approx | zero-filled by OSAP (`che` is in the list) |
| `mve_permco` | `crsp.mve_permco` | `ctx.universe["mkt_cap_usd"]` (DAILY.marketcap, company level) | approx | row absent -> NaN |
| `ceq` | `compustat.ceq` | `SF1.equity` (incl. preferred) | approx | required non-null; also BM filter |
| `at`, `ib`, `csho`, `prcc_f` | `compustat.at/ib/csho/prcc_f` | `assets`, `netinc + netincdis`, `sharesbas`, (price) | mapped / approx | required non-null, else signal NaN |
| `sic` | `compustat.sic` | `TICKERS.siccode` (current) | mapped | SIC 6000-6999 -> NaN |
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt.
- WHY `pstk` DECIDES: preferred stock is one of five summands in the NUMERATOR (a debt-like claim), so it is a signal input, not an adjustment to book equity. The field-map LOOP RULING (2026-09-25, `book_equity_preferred_terms`) covers pstk only where it adjusts book equity (`seq + txditc - pstk` -> approx); it does not extend to a net-debt sum, and a predictor whose signal contains preferred stock stays infeasible. OSAP zero-fills `dvpa` and `tstkp` but not `pstk`, so the missing-item rule gives infeasible. Dropping pstk would also change OSAP's own sample (rows with pstk missing are NaN there; that share is not measurable without Compustat).
- Second, independent concern (measured, information only, pstk omitted): coverage. Scored share of the universe with `debt` (gate `debtc.notna()`: 18.8% median null, the unclassified financial/REIT block), non-financial (SIC not 6xxx; 19.7% median of names are 6xxx), at/ib/csho/ceq present, and BM quintile >= 3: 40.4% median, min 23.8% (first 3 months, SF1 thin), max 43.0%; below 40% in 128 of 276 months (115 of the 263 from 2000-01). Names scored 543-1,234 (median 746). Two deviations from OSAP's filter pull in opposite directions, so read this as "about the 40% bar, direction of correction unknown": (a) OSAP takes BM quintiles over the whole merged cross-section including financials, whose NDP is NaN anyway (more non-financials fall in the excluded bottom two); (b) OSAP keeps names whose `BM_clean` is NaN (negative ceq -> log NaN -> `tempsort` NaN -> not excluded); the measurement here drops them. pstk decides; coverage is not a settled failure.
- Mass point (for completeness): continuous; modal share 0.08-0.38% of scored, distinct values = n scored. Not a concern.

## 2. Variables (exact source names)
`permno, time_avail_m, at, dltt, dlc, pstk, dvpa, tstkp, che, sic, ib, csho, ceq, prcc_f`, `mve_permco` (SignalMasterTable); derived `BM_filter = log(ceq / mve_permco)`, `BM_clean`, `tempsort`.

## 3. Formula in words and key lines
Net debt = long-term debt + debt in current liabilities + preferred stock + preferred dividends in arrears - treasury stock (preferred) - cash and short-term investments, divided by market value of equity; NaN for SIC 6000-6999 and for missing at/ib/csho/ceq/prcc_f; only firms in BM quintiles 3-5 (bottom two BM quintiles set NaN).
```
NetDebtPrice = ((dltt + dlc + pstk + dvpa - tstkp) - che) / mve_permco        # NOTE + dvpa; tstkp subtracted
NaN if 6000 <= sic <= 6999 or any of at, ib, csho, ceq, prcc_f is NaN
BM_clean = log(ceq / mve_permco) (inf -> NaN); tempsort = fastxtile(BM_clean, by time_avail_m, 5); tempsort <= 2 -> NaN
```
SignalDoc-vs-code: the Detailed Definition says "Keep only 3rd B/M Quintile" but the code keeps quintiles 3, 4 and 5; the code is what produced the published series. `mve_permco` is the signal-month market value (not lagged) against accounting data as of datadate + 6 months; the BM quintile uses the same ME. Fastxtile is over the full merged sample (all exchanges, incl. micro-caps), not the project's screened universe: quintile cut-offs are not reproduced identically.

## 4. Timing / lag convention
OSAP: annual data at datadate + 6 months held 12 months; ME at the signal month. Sharadar: ART as of `datekey` (refreshed quarterly) against `mkt_cap_usd` at the signal date. All inputs are balance-sheet LEVELS (no flow, no year-over-year difference, nothing to smear under TTM, no dimension override). ART-as-of-filing makes the level 1-3 months earlier than OSAP's and refreshes it each quarter. `fxusd == 1` gate where a reporting-currency amount meets the USD cap (0.00-0.06% of universe fail it).

## 5. Filters
Predictor: SIC 6000-6999 excluded; at/ib/csho/ceq/prcc_f non-null; BM quintiles 3-5. SignalDoc Filter: empty. Here: harness universe (price >= $1, relative size/dollar-volume screen).

## 6. Predicted sign
SignalDoc `Sign = -1.0` (high net debt to price -> low returns). Orientation `ascending=False`.

## 7. The mass-point question
A do-nothing firm (no debt, no preferred, no cash) gives exactly 0 but is not a default; with unrounded USD levels it is essentially absent: modal share of scored 0.08-0.38%, no zero-fill in the signal. No tie handling needed. Negative values (net cash) are legitimate and form the low tail.

## 8. History needed (snapshot starts 1998-01)
No lookback. SF1 is thin at the first months (scored share 23.8% at 1998-12 / 24.1% at 1999-01 / 24.2% at 1999-02, then 37-43%). Not a data_start issue.

## 9. OSAP metadata
NetDebtPrice; Penman, Richardson and Tuna 2007 (JAR); Cat.Signal Predictor; Cat.Economic leverage; Sample 1963-2001; Sign -1.0; EW; LS Quantile 0.2; Portfolio Period 12.0; Start Month 6.0. LongDescription "Net debt to price". SignalDoc Notes: "ND/P in paper. Table 4a has size adjusted returns for double sorts on NDP and NOA/POA ... Performance here is not great, as noted in the text ... OP drops extreme obs but we don't."

## 10. Proposed Sharadar mappings with deviations (for reference only; recommendation is NOT to translate)
```
debt = f["debt"].where(f["debtc"].notna());  che = cashneq + investmentsc.fillna(0)
nd = (debt - che) / ctx.universe["mkt_cap_usd"].where(> 0), gated fxusd == 1     # pstk omitted: NOT OSAP's numerator
```
Deviations if someone overrides the recommendation: pstk (and the zero-filled dvpa, tstkp) dropped -> preferred-heavy names are mis-stated and OSAP's pstk-missing sample restriction is lost; debt includes ASC 842 operating leases from FY2019; che overstated by financing receivables for captive-finance names; BM quintiles within the project's screened universe; BM-missing names dropped.
Fields not in the map: none.
Recommendation: infeasible (data_unavailable: pstk, not zero-filled by OSAP). Do not translate.
