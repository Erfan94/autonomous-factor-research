# FirmAge — Firm age since start of CRSP coverage (Barry and Brown 1984, Table 3)

OSAP ref b4e911e69678a7424f318617a61d813f54183123 (cache b4e911e6); source `Predictors/FirmAge.py` (cached
`predictor.py`, `signaldoc_row.csv`, `upstream_SignalMasterTable.py`, `upstream_CRSPMonthly.py`). DATA_SHA
198b281de1a0. SignalDoc row (Cat.Signal == Predictor): Cat.Data = Other, Cat.Economic = info proxy.

## 1. Data availability (verdict: PREFLIGHT_FAILED — coverage; a construction exists but is approx)

| input (OSAP) | field_map key | Sharadar | status | note |
|---|---|---|---|---|
| SignalMasterTable rows per `permno` (age = `cumcount()+1` of a firm's rows: months since first CRSP row) | `crsp.smt_row` and `crsp.firstpricedate` | SEP presence; TICKERS.firstpricedate (one row per permaticker via `ticker_meta()`) | mapped / mapped | age clock = first trade month; SEP panel starts 1997-12 |
| `tempcrsptime == FirmAge` (firm existed at CRSP start 1926-07, age censored, set NaN) | none | TICKERS.firstpricedate <= 1997-12-31 (floor) | approx | OSAP's own censoring rule, re-applied at Sharadar's 1997-12 start |
| `exchcd` (loaded, NOT used in FirmAge.py) | `crsp.exchcd` | TICKERS.exchange (current only) | approx | SignalDoc filter `exchcd==1` not implemented in code |
| `gvkey` (loaded, unused) | none | none | n/a | |

- No unavailable input: the signal is buildable, but only as an approximation (`approx`), because Sharadar's
  history starts 1997-12 (TICKERS.firstpricedate is floored at 1997-12-31; field_map: 26% of 74,245 tickers
  sit at the floor and must be NaN'd). Censored firms are NaN by OSAP's own rule, so there is no zero-fill.
- Do NOT propose "age since 1998-01" for censored firms as a stand-in: that is a different variable.
- **Recommendation: `preflight_failed`** (coverage, structural from the data start; mass point at the first
  probe month). Measured (below): scored share averages 35%, under the 40% Stage 1 floor.

## 2. Variables (exact source names)

`gvkey`, `permno`, `time_avail_m`, `exchcd` (SignalMasterTable; only `permno`, `time_avail_m` matter). The
SignalMasterTable keeps `shrcd in {10,11,12}` and `exchcd in {1,2,3}` rows, so the age clock counts months on
those rows only.

## 3. Formula

```
df = df.sort_values(["permno","time_avail_m"])
df["FirmAge"] = df.groupby("permno").cumcount() + 1                       # months since first row
df["tempcrsptime"] = round((time_avail_m - 1926-07-01).days / 30.44) + 1  # months since CRSP start
df.loc[tempcrsptime == FirmAge, "FirmAge"] = NaN                          # firm present since 1926-07
```
Integer months, no log, no winsorising. Note it counts ROWS, not calendar months: a month with no row does
not advance the clock.

## 4. Timing / lag

No lag: the month-m row's age includes month m (age 1 in the first row); stamped m, portfolio earns m+1.
No SF1 item, so ART-as-of-filing and TTM smearing are not in play. `firstpricedate` is permaticker-level, equals
SEP's per-ticker min(date) on 100% of the 20,985 SEP-scope tickers (field_map), and is a current TICKERS
field: a future re-pull could revise it (not testable from one snapshot).

## 5. Filters

None in `FirmAge.py` (the loaded `exchcd` is unused). SignalDoc Filter `exchcd==1` (NYSE only) and Notes
"OP uses special NYSE archive data that we lack" document that the published result used older NYSE data.
SignalDoc Signal Rep Quality = 4_lack_data.

## 6. Predicted sign

SignalDoc `Sign = -1.0` (older firm, lower return). Regression (mv reg nonstandard data), EW, Portfolio
Period 1, Start Month 6; sample 1931-1980; t = 2.48; Predictability in OP 2_likely.

## 7. Mass-point question

Measured on the harness universe (`build_universe`, hysteresis chain warmed from the first panel month) at all
276 signal months 1998-12-31..2021-11-30. Age = months from first SEP-panel month through the signal month,
inclusive; scored = firstpricedate after 1997-12-31. Panel-based and firstpricedate-based scoring agree on
100% of universe rows. A do-nothing firm (listed before 1997-12-31, i.e. censored) is NaN, not a value.
- Scored share: 5.4% (1998-12), 34.8% (2010-06), 61.6% (2021-11); yearly mean 11% 1999, 22% 2000, 35% 2010,
  47% 2015, 60% 2021; pooled 34.7%; 170 of 276 months under 40%; first month >= 40% is 2013-02. n scored ranges
  124..1424, >= 100 in every month, < 300 in 8 months.
- Preflight probe months (first/middle/last of the schedule, `masspoint_stats` on the non-null signal):
  1998-12-31 n=124, mode age 6 months = 14.5%, 11 distinct values, qcut yields 9 bins; 2010-06-30 n=622, mode
  2.4%, 141 distinct, 10 bins; 2021-11-30 n=1424, mode 2.2%, 266 distinct, 10 bins. The first probe month
  hits the 10% cliff and `qcut_bins` < 10, so preflight would HARD-fail it (n=124 is above `MIN_OBS_RANK`=10).
- Mode share of the scored set >= 10% in 11 months (1998-12..1999-11), median 2.1% thereafter.
- Tie handling: integer months, so ties are real; average rank. No value is a legitimate zero.

## 8. History needed

OSAP sample 1931-1980; only the age clock matters. The snapshot starts 1998-01: the scored set in early years is
"listed since 1998" only, so the age distribution is top-truncated (at most 12 months in 1998-12, 36 months in
2000, about 280 months by 2021) until the 2010s. That is a different shape from OSAP's (ages of decades).
Coverage, not data start, is the binding failure.

## 9. OSAP metadata

Acronym FirmAge; Cat.Signal Predictor; Barry and Brown, JFE 1984; Cat.Form continuous; Cat.Data Other;
Cat.Economic info proxy; Key Table in OP "3 full samp, period of listing"; Test "mv reg nonstandard data";
sample 1931-1980; Stock Weight EW; GScholar cites (2025-09) 949.

## 10. Proposed Sharadar mappings / deviations

- Age clock: months between TICKERS.firstpricedate and the signal (equivalently the count of monthly-panel
  months with a trade), NaN where firstpricedate <= 1997-12-31. Key: `crsp.firstpricedate` (mapped),
  `crsp.smt_row` (mapped).
- Deviations: (1) censoring at 1997-12 (54%-95% of universe-months) instead of 1926-07; (2) OSAP counts months
  on the shrcd/exchcd-filtered rows (an OTC-to-NASDAQ move restarts the clock); firstpricedate does not;
  (3) NYSE-only SignalDoc filter not applied (current-only exchange); (4) universe-relative, not CRSP-wide.
- Not in field_map: nothing new; needs `history_months` only if translated as panel-count.
