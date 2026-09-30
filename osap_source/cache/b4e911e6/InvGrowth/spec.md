# InvGrowth — deflated year-over-year inventory growth (Belo and Lin 2012, RFS, Table 2A EW)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/InvGrowth.py` (cached `predictor.py`, `upstream_CompustatAnnual.py`, `upstream_GNPDeflator.py`; SignalDoc row Acronym = InvGrowth, Cat.Signal Predictor). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`. Measurements: harness universe, ALL 276 decision months (signal dates 1998-12-31 .. 2021-11-30), dimension ART.

## 1. Data availability (verdict: APPROX; constructible, every month scores, coverage 44-57% from 1999-03)

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `invt` (annual inventories) | `compustat.invt` | SF1 `inventory` (ART) | mapped | ZERO-FILLED by OSAP (`zero_fill_vars`); Sharadar 0 = vendor zero-fill: same rule, no deviation |
| `gnpdefl` (FRED GNPCTPI / 100, 3-month lag) | not in map (`public_sources`: FRED/BEA not in the snapshot) | none | see below: DROPS OUT of any rank | inner merge (drops months with no deflator) |
| `sic` | `compustat.sic` / `crsp.siccd` | TICKERS.siccode (CURRENT) | approx (look-ahead ruling `current_sic_signal_values`) | NaN kept (`"nan"` does not start with 4/6) |
| `at` | `compustat.at` | SF1 `assets` | mapped | `at > 0` required |
| `ppent` | `compustat.ppent` | SF1 `ppnenet` | mapped, 0-vs-missing ambiguity | NaN kept, `ppent <= 0` dropped (NOT zero-filled by OSAP) |
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt.
- **GNP deflator is rank-invariant.** invt/defl_t / (invt_{t-12}/defl_{t-12}) - 1 = (invt_t/invt_{t-12}) * (defl_{t-12}/defl_t) - 1: both deflator values are month-t constants shared by every firm, so the signal is a positive affine map of the nominal growth ratio within a month. Sector-relative percentile ranks, IC and deciles are identical, so omitting the deflator is exact for the harness. (OSAP's inner merge would also drop months with no deflator; placeholder data if no FRED key: irrelevant.) Not a missing-input case: no zero-fill needed, no infeasibility.
- Verdict APPROX: current-SIC filter look-ahead, ppnenet 0/missing ambiguity, per-quarter rather than annual refresh.

## 2. Variables (exact source names)
`invt, sic, ppent, at, gnpdefl, permno, gvkey, time_avail_m`. Derived `invt_lag12`, `InvGrowth`.

## 3. Formula in words and key lines
Growth of deflated inventory from the previous fiscal year to the latest one; firms in utilities/transport (SIC 4xxx) and financials (SIC 6xxx) and firms with non-positive assets or PP&E excluded.
```
df["invt"] = df["invt"] / df["gnpdefl"]                      # inner merge on time_avail_m
drop sic_str.startswith("4") or startswith("6")
keep (at > 0) & ((ppent > 0) | ppent.isna())
invt_lag12 = invt at time_avail_m - 12 months (calendar merge on permno)
InvGrowth  = invt / invt_lag12 - 1 ; dropna only (inf is NOT dropped)
```

## 4. Timing / lag convention
OSAP: annual `invt` available datadate + 6 months, held 12 months (m_aCompustat); the 12-month calendar lag therefore compares consecutive fiscal years (changes once a year; no row at t-12 -> NaN, e.g. a fiscal-year change or a gap). Signal is 6-17 months stale.
Here: inventory is a balance-sheet LEVEL (ART == ARQ level on the same reportperiod, field_map), so there is no four-quarter smear and no `dimension=ARQ` override. Proposed `ctx.fundamentals_yoy(["inventory","assets","ppnenet"], years=1)`: latest filing and the filing whose reportperiod is ~1 year earlier, both as known at the signal. ART refreshes quarterly, so the signal updates four times a year and is fresher than OSAP; `dimension="ARY"` would mimic the annual cadence (not adopted; measured on 28 months ART vs ARY coverage mean 49.2% vs 47.6%, scored names 994 vs 959). Default ART.
The deflator's 3-month availability lag is irrelevant (rank-invariant).

## 5. Filters
In predictor.py (construction, not portfolio stage): SIC 4xxx and 6xxx excluded; `at > 0`; `ppent > 0 or NaN`. SignalDoc Filter blank; Notes "Drop if 1 digit sic code is 4 or 6, or if at or ppent <= 0".
Measured share of the universe excluded by SIC 4/6 (current siccode, `str(int(sic)).startswith(("4","6"))`, null kept): 25.1-33.1%, mean 30.5%. TICKERS.siccode is today's classification (12-14% of names reclassified since 1998): a declared look-ahead in the filter, per the `current_sic_signal_values` ruling; point-in-time SIC from ACTIONS not built.
`ppnenet`: Sharadar fills 0 for "not reported", so a value 0 cannot be told from a missing one. OSAP keeps NaN, drops <= 0. Measured: ppnenet == 0 on 0.17-0.57% (mean 0.37%) of names with positive lagged inventory. Lenient (keep 0, OSAP forward-fills and never zero-fills) proposed: coverage 44.4-57.0% vs strict 44.3-56.8%.

## 6. Predicted sign
SignalDoc `Sign = -1.0`: high inventory growth predicts LOW returns. Cat.Economic `profitability`, Cat.Data Accounting, Cat.Form continuous; T-Stat 6.64; Return 0.89; Stock Weight EW; LS Quantile 0.1; Portfolio Period 12; Start Month 6. Orientation: long LOW growth, `FactorDef(ascending=False)`.

## 7. The mass-point question
A do-nothing firm (inventory unchanged) gives InvGrowth = 0 only if two filings tie to the dollar: 0.00-0.39% (mean 0.10%) of scored names. The real mass is ZERO INVENTORY: 46% of ART rows are exactly 0 (vendor/OSAP zero-fill; 42% in 1999-2003, 53% in 2021-26; 34% financial services). 0/0 = NaN in OSAP so these firms are unscored; that is 30-43% of the universe (inv_lag == 0 and invt == 0 or > 0; 36.0% mean; 32.5% 1998-2003, 33.7% 2004-09, 35.6% 2010-15, 40.9% 2016-21).
- Universe firms with lagged inventory > 0 (pass before SIC/at/ppent): 50.2-65.3% (mean 60.1%).
- inv_lag == 0 and invt > 0 (OSAP's pandas output yields `inf`, which `dropna` keeps; the Stata legacy makes it missing): 0.26-2.40% of the universe (mean 0.69%). Proposed `where(lag > 0)` -> NaN; a deviation from the literal Python output.
- invt == 0 with lag > 0 gives exactly -1.0: a second mass point at the bottom, 0.19-2.15% of scored names (mean 0.71%; max in 1999-2000). Kept (OSAP's value); ties averaged by the rank; ascending=False puts them in the long leg.
- Measured scorable universe coverage: min 44.4%, mean 52.2%, max 57.0% for the 273 months from 1999-03; 28.1%, 29.1%, 33.5% at signal dates 1998-12-31, 1999-01-29, 1999-02-26 (thin early ART at the t-12 date). Late drift down: 50.6% (to 2003), 54.9% (2004-09), 53.0% (2010-15), 49.0% (2016-21), 45.0% at 2021-11, as zero-inventory firms rise. The 40% coverage bar is not at risk after 1999-02.
- Scored names 896-1,380 per month (>= 89 per decile); `qcut(10)` gives 10 bins in every month; distinct values 888-1,351; modal share 0.19-2.15%. Tie handling: average ranks.

## 8. History needed (snapshot starts 1998-01)
12-month lookback on a quarterly level: SF1 starts 1997Q4, SEP irrelevant. The t-12 filing exists for 28% of the universe at the first signal date and the yoy match rate is 48-57% until 1999-02 (measured have_yoy 48.4% at 1998-12, 49.9% 1999-01, 57.1% 1999-02, 89.1% 1999-03, 85-98% after). No `history_months` needed (fundamentals-only factor). Not a data_start case.

## 9. OSAP metadata
InvGrowth (Acronym2 InvenGr); Belo and Lin 2012 RFS; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form continuous; Cat.Data Accounting; Cat.Economic profitability; Sample 1965-2009; Key Table "2A EW"; Test "port sort"; Evidence "t=6.6 in port sort"; Sign -1.0; Return 0.89; T-Stat 6.64; Stock Weight EW; LS Quantile 0.1; Portfolio Period 12; Start Month 6; Filter blank; GScholar cites 220.
Definition: "Defate invt growth using gnp deflator. Signal is deflated invt growth rate from fiscal year t to fiscal year t-1. Drop if 1 digit sic code is 4 or 6, or if at or ppent <= 0".

## 10. Proposed Sharadar mappings and deviations
```
invt, invt_lag12 -> SF1 inventory (ART), ctx.fundamentals_yoy(["inventory","assets","ppnenet"], years=1)   [compustat.invt, mapped]
gnpdefl          -> omitted (rank-invariant within a month)
sic              -> TICKERS.siccode via ctx.ticker_meta(["siccode"]) ; exclude str(int(sic)).startswith(("4","6")), null kept  [approx, current SIC]
at > 0           -> SF1 assets > 0 ; ppent -> SF1 ppnenet > 0 or == 0 (treated as missing) or null
InvGrowth = (inventory / inventory_lag).where(inventory_lag > 0) - 1 ; ascending=False
```
Deviations: (a) deflator omitted (exact for ranks); (b) current siccode (look-ahead on 12-14% reclassified names); (c) ppnenet == 0 kept; (d) quarterly ART refresh vs annual + 6 months; (e) `inf` (lag 0, invt > 0) set NaN; (f) calendar-12-month row merge replaced by reportperiod-aligned year-ago filing (tol 45 days). Fields not in the map: GNPCTPI (FRED; moot). Recommendation: approx.
