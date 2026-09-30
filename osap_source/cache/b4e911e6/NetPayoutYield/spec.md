# NetPayoutYield — Net payout yield: (common dividends + stock repurchases - stock issuance) / market equity lagged 6 months (Boudoukh et al. 2007, Table 6D)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/NetPayoutYield.py` (cached `predictor.py`; upstream `upstream_CompustatAnnual.py`, `upstream_CRSPMonthly.py`, `upstream_SignalMasterTable.py` beside it). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`. Measurements: harness universe, 276 decision months (signals 1998-12-31 .. 2021-11-30), recorded snapshot, scratch measurement (no factor file).

## 1. Data availability (verdict: APPROX; 264 of 276 months scorable, first at signal 1999-12-31, floor 120)

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `dvc` common dividends | `compustat.dvc` | `-ncfdiv` (ncfdiv is outflow-NEGATIVE, predominantly common-only) | approx | NOT zero-filled (only `dvt` is): missing dvc -> NaN |
| `prstkc` purchase of stock | `compustat.prstkc` | `ncfcommon` (NET common flow, inflow-positive) | approx | ZERO-FILLED |
| `sstk` sale of stock | `compustat.sstk` | same column `ncfcommon` | approx | ZERO-FILLED |
| `mve_permco` lagged 6 months | `crsp.mve_permco` | `DAILY.marketcap * 1e6` at BME(t-6) (company level already) | approx | no row 6 months back -> NaN |
| `ceq` | `compustat.ceq` | `SF1.equity` (incl. preferred) | approx | `ceq > 0` or missing kept |
| `sic` | `compustat.sic` | `TICKERS.siccode` (current) | mapped | 6000-6999 dropped |
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt. Gross sstk and prstkc are not separately available but only the NET `prstkc - sstk` enters, and `-ncfcommon` reproduces it (approx: preferred excluded). Missing items: sstk, prstkc zero-filled by OSAP -> null `ncfcommon` = 0 here; dvc not zero-filled -> null `ncfdiv` gives NaN, as in OSAP.
- Measured (harness universe, per month): scored share (after all filters below) 60.6-74.5%, median 70.6%; names scored 1,220-1,804 (median 1,323). Without the SIC 6xxx drop coverage would be 74.7-92.9% (median 88.9%): the financial screen costs about 15 points. Universe share of SIC 6xxx names: median 19.7%.
- Scorable months: the first 12 signals (1998-12 .. 1999-11) are null and 264 of 276 are scorable. The binding constraint is the two-year gate below (`has_price_at(24)`; SEP starts 1997-12 so 24 months of history exists from signal 1999-12-31), NOT DAILY: DAILY.marketcap is null at the 6-month lag for signals up to 1999-05 (100% null 1998-12 .. 1999-05), 5.0% null at 1999-06, 1.4% median over all months. Not data_start (264 >= 120).
- `fxusd != 1` in the universe: 0.00-0.06% of names (gate `fxusd == 1`: a reporting-currency amount meets a USD cap).

## 2. Variables (exact source names)
`permno, time_avail_m, dvc, prstkc, sstk, sic, ceq`, `mve_permco` (SignalMasterTable, 6-month lag via `lag6_date`); derived `NetPayoutYield`, `obs_count`.

## 3. Formula in words and key lines
Dividends plus repurchases minus issuance, over market equity six months earlier; net payout of exactly zero is removed; financials, negative book equity and firms with fewer than 24 observations are dropped.
```
NetPayoutYield = (dvc + prstkc - sstk) / mve_permco_l6          # calendar 6-month lag via merge; dvc NaN -> NaN
exact 0 -> dropped (tiny float residual with nonzero components -> 1e-19 kept)
keep (sic < 6000 or sic >= 7000) and (ceq > 0 or ceq NaN); obs_count = cumcount()+1 per permno on the filtered frame; keep obs_count >= 24; drop NaN/inf
```
Rearrangement: dvc = -ncfdiv (clip ncfdiv to <= 0; positive is wrong sign, 0.19%); prstkc - sstk = -ncfcommon; so numerator = -(ncfdiv + ncfcommon.fillna(0)). SignalDoc-vs-code consistent ("purchase of common AND PREFERRED stock"; Sharadar's net common flow excludes the preferred leg).

## 4. Timing / lag convention
OSAP: annual flows at datadate + 6 months held 12 months, ME at t-6. Sharadar: ART (TTM flows) as of filing, ME at BME(t-6) read as `ctx.at_month_end("DAILY", ["marketcap"], 6)`. Flow LEVEL divided by a price-level: no year-over-year difference, nothing to smear under TTM, no `dimension=ARQ` flag (ART == sum of four ARQ within 1% on 99.6% of rows). ART-as-of-filing: flow known 1-3 months earlier than OSAP's +6-month alignment; the 6-month ME lag is kept from OSAP. `fxusd == 1` gate.

## 5. Filters
Predictor: zero payout dropped; SIC 6000-6999 dropped; `ceq <= 0` dropped; at least 24 observations per firm (counted after the other filters, so a name needs 24 filtered firm-months). SignalDoc Filter empty. Here: harness universe. The 24-observation rule has no direct harness analogue: a factor may not filter the universe, so the translator proposes `history_months = 24` (a trade near the window start, the sanctioned route) as a stated deviation (it counts listing age, not filtered months).

## 6. Predicted sign
SignalDoc `Sign = 1.0` (high net payout yield -> high returns). Orientation `ascending=True`.

## 7. The mass-point question
A do-nothing firm (no dividend, no buyback, no issuance) produces exactly 0, which OSAP REMOVES (set aside, not scored). Measured on the 264 scorable months: exact zeros are 1.0-4.2% of names with data (median 2.0%; 0.98-3.86% of the universe), nulled by the `!= 0` rule, so no mass point is left; modal share of the scored set 0.055-0.082% (2-3 names), distinct values equal n scored (minimum 1,220). Tie handling: null (as OSAP); with `ncfcommon` null -> 0 the null-flow non-payers also fall into this zero removal (consistent with OSAP's zero-fill of sstk/prstkc). Net-issuers are negative, payers positive: a two-sided continuous tail.

## 8. History needed (snapshot starts 1998-01)
`history_months = 24` (the observation gate) plus a lagged market value at t-6. First 12 decision months null by construction; 264 scorable from signal 1999-12-31 (coverage 62.5% there); DAILY's start is not binding.

## 9. OSAP metadata
NetPayoutYield; Boudoukh, Michaely, Richardson, Roberts 2007 (JF); Cat.Signal Predictor; Cat.Economic valuation; Sample 1984-2003; Sign 1.0; EW; LS Quantile 0.1; Portfolio Period 12.0; Start Month 6.0. LongDescription "Net Payout Yield". SignalDoc Notes: "See PayoutYield". Definition: "Dividends (dvc) plus purchase of common and preferred stock (prstkc) minus sale of common and preferred stock (sstk), divided by market value of equity lagged 6 months. Exclude if NetPayoutYield is 0, financial firm based on SIC code, ceq <= 0, or less than 2 years in CRSP".

## 10. Proposed Sharadar mappings with deviations
```
f = ctx.fundamentals(["ncfcommon", "ncfdiv", "fxusd", "equity"])                         # ART
me6 = ctx.at_month_end("DAILY", ["marketcap"], 6)["marketcap"] * 1e6
num = -(f["ncfcommon"].fillna(0) + f["ncfdiv"].clip(upper=0)).where(f["ncfdiv"].notna())
score = (num / me6.where(me6 > 0)).where(f["fxusd"] == 1).where(lambda s: s != 0)
mask: siccode not in 6000..6999 (ctx.ticker_meta), (equity > 0 or NaN) ; ascending=True ; history_months=24 ; inputs SF1.ncfcommon, SF1.ncfdiv, SF1.fxusd, SF1.equity, DAILY.marketcap, TICKERS.siccode
```
Deviations: (a) `ncfcommon` excludes preferred issuance/redemption (Compustat prstkc/sstk include it); the TARP-era error is muted because SIC 6xxx is dropped; (b) `ncfdiv` predominantly common-only (matches `dvc`, but combined-line filers add preferred; cash-paid vs declared timing); (c) TTM flows and as-filed data instead of the annual value at datadate + 6 months; (d) `SF1.equity` includes preferred so the `ceq > 0` screen is nearly immaterial; (e) current SIC, not point-in-time; (f) the 24-observation count is replaced by `history_months = 24` (listing age); (g) the 1e-19 float-residual patch is not reproduced (exact zeros nulled).
Fields not in the map: none (DAILY.marketcap, ticker_meta siccode are mapped).
Recommendation: translate (approx) and preflight.
