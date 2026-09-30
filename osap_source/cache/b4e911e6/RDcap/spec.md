# RDcap — R&D capital to assets, small firms only (Li 2011 RFS, Table 7)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Signals/pyCode/Predictors/RDcap.py` (cached `predictor.py`, `upstream_CompustatAnnual.py`,
`upstream_SignalMasterTable.py`, `upstream_stata_replication.py`). DATA_SHA 198b281de1a0. Reviewed fiscal-year handling for a similar recursion: `factors/candidates/OrgCap.py` (`reportperiod - 7 days`).

## 1. Data availability — VERDICT: preflight_failed (coverage 0 by construction, plus a structural mass point). Data itself is mapped/approx.

| input (OSAP) | field_map key | Sharadar | status |
|---|---|---|---|
| `xrd` | `compustat.xrd` | SF1 `rnd`, ARY | mapped (verified 2026-09-30); vendor zero-filled, `rnd == 0` 63.5% of non-null ARY rows |
| `at` | `compustat.at` | SF1 `assets`, ARY | mapped (verified 2026-09-30) |
| `mve_c` (size tercile; `prc * shrout` from SignalMasterTable) | `crsp.mve_permco` family | panel `mkt_cap_usd` (DAILY.marketcap, company-level) | approx |
| `shrcd`/`exchcd` restriction (SMT: 10,11,12; NYSE/AMEX/NASDAQ) | universe/market scope | `market_constituent_ids` | approx |

- Missing-item rule: OSAP zero-fills the missing item itself (`tempXRD = xrd.fillna(0)`), so a missing `xrd` is 0 in both worlds: no infeasibility from `rnd` and no extra approx beyond
  vendor-zero-vs-null, which is moot here. No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt input.
- Decisive: the size cut is to the bottom tercile of the WHOLE market, which contains no harness-universe name in any month (section 8).

## 2. Variables (exact source names)
`permno, time_avail_m, at, xrd` (`m_aCompustat`); `mve_c` (`SignalMasterTable`); temp `tempXRD`, `tempXRD_lag12/24/36/48`, `tempsizeq`.

## 3. Formula (words + key lines)
R&D capital = 0.8^k weighted sum of the last five annual R&D values, over total assets; set missing before 1980 and unless the firm is in the smallest market-cap tercile that month.
```
tempXRD = xrd.fillna(0)            # AFTER fill_date_gaps (calendar gaps filled with NaN rows, then 0)
RDcap   = (tempXRD + .8*lag12 + .6*lag24 + .4*lag36 + .2*lag48) / at
tempsizeq = qcut(mve_c, 3) by time_avail_m ; RDcap = NaN if tempsizeq >= 2 or tempsizeq is NaN
```
Lags are calendar lags (12/24/36/48 months) on the monthly-expanded annual series = the previous four fiscal years. A missing fiscal year inside the firm's span contributes 0 (fill then fillna);
a row needs panel history 48 months back, i.e. the firm's first annual record must be >= 4 fiscal years before the current one, else the sum is NaN. `at` is NaN on filled gap rows; `at == 0` gives inf/NaN.
Zeros are NOT nulled (unlike OrgCap's `raw != 0`): a firm with no R&D in five years has RDcap exactly 0 and stays in the sample.

## 4. Timing / lag
OSAP: annual record at `datadate + 6 months` held 12 months. SF1: `dimension="ARY"` (annual flow summed over five years; ART double-counts, ARQ smears). Fiscal-year key: `reportperiod - 7 days`
(52/53-week filers, as reviewed for OrgCap). ARY filing date is ~3 months earlier than OSAP's +6. Size tercile is formed at the signal month on market cap.

## 5. Filters
Code: year >= 1980; bottom market-cap tercile (across Compustat x SMT common stocks on NYSE/AMEX/NASDAQ, per month); `at` non-missing. SignalDoc Filter blank; Quantile Filter blank.

## 6. Predicted sign (SignalDoc)
`Sign = +1.0` (`ascending=True`). Cat.Economic `asset composition`, Cat.Form continuous, Cat.Data Accounting; Sample 1980-2007; T-stat 2.64 (long-short, "Table 7 RDCAP small size"); Return 0.69; VW; LS quantile 0.5; Portfolio Period 12; Start Month 6; `1_clear`.

## 7. The mass-point question
A do-nothing firm (no R&D in five years, or no R&D line) has `tempXRD = 0` in every term, so RDcap = 0 exactly and OSAP keeps it. Measured on the harness universe, all 276 months (1998-12-31..2021-11-30),
WITHOUT the size cut (the size cut leaves 0 names, so this is the only scorable form; it is a different, broader signal than OSAP's):
- Non-null coverage of the universe (history rule above, `at > 0`): mean 77.0% (min 9.5% at 1998-12, 44.3% at 2001-12, 80.0% at 2002-12; >= 40% in 248 of 276 months).
- Modal value is exactly 0 every month: share of non-null 63.2%-74.0% (mean 68.9%); >= 10% cliff in 276 of 276 months; distinct values 62-671 (mean 463); `qcut` yields 3-5 bins of 10 (< 10 in 276 of 276).
  Probes: 1998-12-31 72.65% zeros (3 bins); 2010-06-30 69.49% (4 bins); 2021-11-30 65.47% (4 bins). No tie design (null / floor / remove) can yield ten deciles unless the zeros are NULLED (a different signal:
  zero-R&D firms dropped, leaving the ~31% with R&D capital).
- The signal is therefore a mass point even before the size cut; the size cut is a second, independent failure.

## 8. History needed and MEASURED coverage with OSAP's size cut
- Size tercile formed on the market scope (every listed common stock that traded in the signal month and has an ARY row known, 4,148-6,869 names; `mkt_cap_usd`, tercile 1 = bottom third).
  Universe names in the bottom tercile: 0 of ~1,965, in all 276 months (e.g. 2010-06-30: of 1,789 universe names, 1,456 in the top tercile, 328 in the middle, 0 in the bottom; 5 without market cap).
  The harness universe screens at the NYSE 20th market-cap percentile, which lies above the bottom third of the full market. Scored names under OSAP's definition: 0 in 276 of 276 months; coverage 0%.
- History: SF1 ARY starts FY1992-FY1997 (few before FY1996); first non-null RDcap (without size cut) at the 1998-12 signal (9.5% of the universe), >= 40% from 2001-12; scorable months are not the blocker
  (rebalance.min_months 120), FY1997-only start would put the first full five-year sum at FY2001 for names first seen at FY1997.
- Forming the tercile inside the universe instead is a different signal (and would still carry the 63-74% zero mass point).

## 9. OSAP metadata
Acronym `RDcap`; Li, RFS 2011 ("R&D and Stock Returns"); Key Table "7 RDCAP small size"; LS port; VW; LS quantile 0.5; Portfolio Period 12; Start Month 6; Sample 1980-2007; GScholar cites 709.
Detailed Definition: weighted sum of lagged xrd (1, .8, .6, .4, .2) scaled by `at`, xrd missing -> 0, missing before 1980 or if the firm is in the upper two thirds of market cap (shrout*abs(prc)) in a month.

## 10. Proposed Sharadar mappings and deviations (only if the preflight failures were ever waived)
- `xrd -> SF1.rnd` (ARY, missing -> 0); `at -> SF1.assets` (ARY, same fiscal year, > 0 guarded); fiscal year by `reportperiod - 7 days`; five consecutive fiscal years with gap years = 0; NaN unless the firm's first ARY row is >= 4 fiscal years old.
- `mve_c -> mkt_cap_usd` (panel; DAILY.marketcap) on `ctx.market_context()`; tercile 1 only. Not in field_map: a per-month market-scope size tercile helper.
- Recommend `preflight_failed`: zero scored names in 276 of 276 months under OSAP's size cut, and an exact-zero mass point of 63-74% (3-5 qcut bins) even without it. No file to translate.
