# NetEquityFinance — Net equity financing: (sale of stock - purchase of stock - cash dividends) / average total assets (Bradshaw, Richardson, Sloan 2006, Table 3)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/NetEquityFinance.py` (cached `predictor.py`; upstream `upstream_CompustatAnnual.py` beside it). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`. Measurements: harness universe, 276 decision months (signals 1998-12-31 .. 2021-11-30), recorded snapshot, scratch measurement (no factor file).

## 1. Data availability (verdict: APPROX; 276 of 276 months scorable, coverage 82-98.6% from 1999-03)

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `sstk` sale of stock | `compustat.sstk` | `ncfcommon` (NET common-equity flow, inflow-positive) | approx | ZERO-FILLED (`zero_fill_vars`) |
| `prstkc` purchase of stock | `compustat.prstkc` | same column `ncfcommon` (net; sstk - prstkc == ncfcommon) | approx | ZERO-FILLED (`zero_fill_vars`) |
| `dv` cash dividends (common + pref.) | `compustat.dv` | `ncfdiv` (outflow-NEGATIVE, predominantly common-only) | approx | NOT zero-filled (only `dvt` is): missing dv -> NaN |
| `at`, lag-12 `at` | `compustat.at` | `assets` (ART, current and the filing one year earlier) | mapped | lag via `shift(12)` on the monthly panel: missing -> NaN |
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt. Gross sstk and prstkc are not separately available, but the signal only uses their NET (sstk - prstkc), which `ncfcommon` reproduces (the field map calls this exact for the net pair). Missing items: sstk, prstkc zero-filled by OSAP -> a null `ncfcommon` is set to 0 here, consistent with OSAP; dv is not zero-filled -> a null `ncfdiv` leaves the signal NaN, as in OSAP. `ncfcommon` null is 98.9% on ncfo-null rows (no cash-flow statement).
- Measured (harness universe, per month): `ncfdiv` null median 3.0% (0.4-48.1%; the high end is the first months, SF1 thin), `ncfcommon` null median 3.0%, lag-12 assets null median 3.1% (1.1-51.6%). Scored share of the universe: median 96.0%; 47.1% / 48.3% / 55.4% in the first three months (1998-12, 1999-01, 1999-02: lagged assets thin, SF1 has few filings; not a data-start failure), 82.0-98.6% from 1999-03 (87.7% at 1999-03). Names scored: 1,074-2,379 (median 1,818).
- Sample restriction `abs(ratio) > 1 -> NaN` removes 0.46% of the universe median (max 3.7%).

## 2. Variables (exact source names)
`gvkey, permno, time_avail_m, sstk, prstkc, at, dv`; derived `l12_at` (12-month lag of `at`), `NetEquityFinance`.

## 3. Formula in words and key lines
Net equity issuance minus cash dividends, scaled by the average of total assets now and twelve months earlier; ratios beyond +/-1 are set missing.
```
l12_at = groupby(permno)["at"].shift(12)
NetEquityFinance = (sstk - prstkc - dv) / (0.5 * (at + l12_at));  |NetEquityFinance| > 1 -> NaN
```
SignalDoc-vs-code: the Detailed Definition reads "sale of common stock (sstk) minus purchase of common stock (prstkc), scaled by average total assets"; it OMITS `- dv`. The code subtracts `dv` (total cash dividends), so the published series is net equity financing AFTER dividends (negative for payers). The code is documented here. No SIC/financial screen, no ceq screen, no price screen.

## 4. Timing / lag convention
OSAP: annual flows and assets at datadate + 6 months, held 12 months; `shift(12)` on the monthly-expanded panel gives the prior fiscal year's `at` at the same month. Sharadar: ART (TTM flows) and assets as of filing, with the lagged assets from the filing for the same fiscal period one year earlier (`ctx.fundamentals_yoy(["assets","ncfcommon","ncfdiv"], years=1)`, aligned by reportperiod). The numerator is a TTM LEVEL of flows and the average spans the same window: no year-over-year difference of a flow, so nothing smears under TTM and no `dimension=ARQ` flag is needed (ART default; ART == sum of four ARQ within 1% on 99.6% of rows). ART-as-of-filing changes: signal 1-3 months earlier than OSAP's +6-month alignment and refreshed every quarter rather than yearly; fiscal-year vs trailing-four-quarter window. Both flows and assets are in reporting currency: same-currency ratio, no `fxusd` gate needed.

## 5. Filters
Predictor: only `abs(ratio) <= 1`. SignalDoc Filter empty. Here: harness universe (price >= $1, relative size/dollar-volume screen); financials are NOT dropped.

## 6. Predicted sign
SignalDoc `Sign = -1.0` (high net equity financing -> low returns). Orientation `ascending=False`.

## 7. The mass-point question
A do-nothing firm (no issuance, no buyback, no dividend) gives exactly 0.0. Measured on all 276 months: exact zero is the modal value, share of scored 0.96-4.13% (median 1.96%), distinct values 1,060-2,313 (scored n 1,074-2,379): below the 5% warn and the 10% cliff at every month, so qcut keeps ten bins. The zero is a real value, arising from ncfcommon null -> 0 together with ncfdiv == 0 (non-payers without issuance). No tie handling designed; average-rank ties. Dividend non-payers (60% of non-null `ncfdiv` is exact 0) are not a mass point because ncfcommon is non-zero for most of them (14.5% of ncfcommon non-null are exact zero).

## 8. History needed (snapshot starts 1998-01)
Two filings one year apart (current ART + the same period a year earlier). No price window, no `history_months`. First three months thin (scored 47.1% / 48.3% / 55.4%), 82% or more from 1999-03.

## 9. OSAP metadata
NetEquityFinance; Bradshaw, Richardson, Sloan 2006 (JAE); Cat.Signal Predictor; Cat.Economic external financing; Sample 1971-2000; Sign -1.0; EW; LS Quantile 0.1; Portfolio Period 12.0; Start Month 6.0. LongDescription "Net equity financing". Definition as in section 3 (dv omitted there).

## 10. Proposed Sharadar mappings with deviations
```
y = ctx.fundamentals_yoy(["assets", "ncfcommon", "ncfdiv"], years=1)                 # ART
num = y["ncfcommon"].fillna(0) + y["ncfdiv"].clip(upper=0)    # = sstk - prstkc - dv ; ncfdiv NaN -> NaN (dv not zero-filled)
avg = 0.5 * (y["assets"] + y["assets_lag"]);  score = (num / avg.where(avg > 0)).where(abs(.) <= 1)
ascending=False ; no history_months ; inputs SF1.ncfcommon, SF1.ncfdiv, SF1.assets
```
Sign rearrangement: Compustat dv is positive, SF1 `ncfdiv` is outflow-negative, so `- dv == + ncfdiv`; `sstk - prstkc == ncfcommon`. Positive `ncfdiv` (0.19% of rows, wrong sign) is clipped to 0.
Deviations: (a) `ncfcommon` EXCLUDES preferred issuance/redemption (Compustat sstk/prstkc include it); matters for financials, which this predictor does NOT drop: TARP-era ARY ($M) C 2008 +6,857 (common only; ~$45B TARP + ~$20B private preferred absent), JPM 2009 +5,756 ($25B repayment absent), BAC 2009, WFC 2009 etc., numerators off by tens of $B for 2008-2011 financials; (b) `ncfdiv` is predominantly common-only while `dv` is common + preferred (inconsistent: included for combined-line filers, excluded where preferred is a separate line; FNMA/FMCC = 0 against $6-17B/yr preferred dividends); NCI distributions excluded; (c) taxes paid on net share settlement and option-exercise flows sit inside `ncfcommon`; (d) TTM flows and as-filed assets rather than fiscal-year values at datadate + 6 months; (e) lagged assets by reportperiod, not `shift(12)` rows.
Fields not in the map: none (all four mapped/approx).
Recommendation: translate (approx) and preflight.
