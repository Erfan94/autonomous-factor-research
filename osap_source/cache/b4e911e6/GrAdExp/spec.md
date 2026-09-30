# GrAdExp — Growth in advertising expenses (Lou 2014, RFS, Table 2A Year 1 Excess; SignalDoc Acronym2 AdExpGr)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Signals/pyCode/Predictors/GrAdExp.py` (cached `predictor.py`). Upstream table construction:
`CompustatAnnual.py` (see `Frontier/upstream_CompustatAnnual_zerofill_excerpt.py`, same pinned ref, for the zero-fill list). DATA_SHA 198b281de1a0.
Written fresh from the source and `field_map_index.yaml`.

## 1. Data availability (verdict: DATA_UNAVAILABLE; recommend infeasible)
| OSAP input | field_map key | Sharadar | status | OSAP missing-item rule |
|---|---|---|---|---|
| `xad` (advertising expense) | `compustat.xad` | none | UNAVAILABLE | NOT zero-filled for this predictor |
| `mve_c` (size decile filter) | `crsp.me` | DAILY.marketcap = `mkt_cap_usd` | mapped | SMT row |
| `at` (loaded, unused) | `compustat.at` | SF1 `assets` | mapped | not used in the formula |
- `xad` IS the signal. SF1 (112 columns) has no advertising, marketing or selling-expense line; `sgna` is total SG&A and does not separate it (`sgna` excludes `rnd`, but carries advertising inside it);
  no other held table has one (checked column names across SF1, TICKERS, SF2, SF3*, METRICS, SEP, DAILY, ACTIONS, EVENTS, SP500: none contains advertising).
- The missing-item rule cannot rescue it, for two reasons: (1) GrAdExp reads the RAW `xad` column from `m_aCompustat` (`columns=["permno","time_avail_m","at","xad"]`), not `xad0`, and
  `zero_fill_vars` in `CompustatAnnual.py` does not include `xad` (the zero-filled copy `xad0` exists separately and Frontier alone applies `xad.fillna(0)` itself); (2) even a zero-fill would be
  removed by OSAP's own filter `xad < 0.1 -> NaN`, and `log(0) = -inf` would be NaN'd by it, so every zero-filled name would be unscored. A do-nothing or no-advertising firm has no value here.
- No measurement is possible (nothing to build). The filter ingredients alone exist: `mkt_cap_usd` for the smallest-decile screen.

## 2. Variables (exact source names)
`xad` (annual Compustat, $ millions, positive when reported; Compustat reports it only for a minority of firms), `mve_c` (CRSP price x shares, $ millions), `permno, time_avail_m`.

## 3. Formula
```
log_xad      = log(xad)                                  # -inf for xad = 0, NaN for xad < 0 or missing
GrAdExp      = log_xad - log_xad.shift(12)              # 12 ROWS back within permno (monthly panel, replicated annual rows)
tempSize     = size decile of mve_c, cross-section of the month (pd.qcut q=10, duplicates dropped, over all rows in the merged panel)
GrAdExp = NaN if xad < 0.1 or tempSize == 1             # small advertisers (< $100k) and the smallest market-value decile removed
```
Log growth of advertising spending over the last year. The lag is taken on the merged panel rows, so it equals 12 calendar months only when the firm's monthly rows are contiguous.

## 4. Timing / lag convention
OSAP: annual `xad` at datadate + 6 months, each annual row replicated across 12 monthly rows, so the signal is constant for a year and the shift(12) compares this year's annual value with last year's.
Here (if data existed): a year-over-year change of an annual flow; by the project ruling it would be `ctx.fundamentals_yoy(years=1)` gated on `reportperiod_lag.notna()`. ART TTM would smear the quarterly change.

## 5. Filters
`xad >= 0.1`; exclude market-value decile 1 (by `mve_c`, all stocks in the merged panel, month by month). SignalDoc Filter `abs(prc) > 5` is portfolio-stage (not in `predictor.py`). Duplicate (permno, time_avail_m) rows dropped keeping the first.

## 6. Predicted sign
SignalDoc `Sign = -1.0` (high advertising growth -> lower future return); `Cat.Form` continuous; `Cat.Economic` investment alt; Stock Weight EW; LS Quantile 0.1; Portfolio Period 1; Start Month 12.
Long LOW GrAdExp; `ascending=False`.

## 7. The mass-point question
A do-nothing firm (no change in advertising) produces GrAdExp = 0 exactly; advertisers holding spending flat report identical annual figures, and all firms share the annual replication (the signal is
constant for 12 months). Advertisers are a minority of firms, so the zero share would be a small fraction of the scored set, but it is unmeasured: no data. Moot.

## 8. History needed (snapshot starts 1998-01)
Not applicable (no `xad`). The construction itself needs two annual values (13+ months of history).

## 9. OSAP metadata (SignalDoc)
Acronym GrAdExp; Acronym2 AdExpGr; Lou; 2014; RFS; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form continuous; Cat.Data Accounting; Cat.Economic investment alt;
Sample 1974-2010; Key Table 2A Year 1 Excess; Test LS port; Sign -1.0; Return 0.58; T-Stat 3.54; EW; LS Quantile 0.1; Portfolio Period 1; Start Month 12; Filter `abs(prc)>5`.
Definition: "Log of advertising expense (xad) minus log of advertising expense last year. Exclude if price less than 5, xad less than .1 or stock in the lowest decile of market value of equity."
The SignalDoc text mentions a price < 5 exclusion; the code applies `xad < 0.1` and the smallest-size-decile exclusion only.

## 10. Proposed Sharadar mappings
None for `xad`. Recommended `osap_frontier.yaml` reason: data_unavailable (advertising expense not in Sharadar; `xad` not zero-filled by this predictor, and OSAP's `xad < 0.1` filter would remove a zero-fill anyway).
Fields not in the map as a live item: `compustat.xad` is mapped as unavailable (present). `mve_c` -> `crsp.me` is present and mapped.
