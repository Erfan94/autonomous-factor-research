# grcapx — Two-year growth in capital expenditures (Anderson and Garcia-Feijoo 2006, JF, Table 3B cegth2)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/ZZ1_grcapx_grcapx1y_grcapx3y.py`
(cached as `predictor.py`, plus `upstream_CompustatAnnual.py`, `upstream_SignalMasterTable.py`,
`signaldoc_row.csv`). The script also emits grcapx3y (predictor) and grcapx1y (placebo); only `grcapx`
is this spec. DATA_SHA 198b281de1a0. Field statuses are mappings; `compustat.capx` is verified_on
2026-09-30 in the index, `compustat.ppent` likewise.

## 1. Data availability — VERDICT: approx (constructible; declared deviations, no unavailable input)

| input | field_map key | Sharadar | status | note |
|---|---|---|---|---|
| `capx` (m_aCompustat, annual) | `compustat.capx` | SF1 `capex`, use `-capex` | mapped, verified 2026-09-30 | cash OUTFLOW; ARY = fiscal-year flow, ART = TTM sum |
| `ppent` (capx fallback only) | `compustat.ppent` | SF1 `ppnenet` | mapped, verified | Sharadar zero-fills missing; fallback dropped |
| `at` | loaded, UNUSED | - | - | never enters grcapx |
| `exchcd` (SignalMasterTable) | loaded, UNUSED in value | - | - | sample filter only (INNER merge to SMT rows); not in the value |
| FirmAge (from permno row count) | `FirmAge` | `TICKERS.firstpricedate` | approx | only gates the ppent fallback; moot if dropped |

- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt. The zero_fill_vars list in
  `upstream_CompustatAnnual.py` (nopi dvt ob dm dc aco ap intan ao lco lo rect invt drc spi gdwl che dp act
  lct tstkp dvpa scstkc sstk mib ivao prstkc prstkcc txditc ivst) does NOT contain capx or ppent, and the
  predictor has no `fillna(0)`. OSAP never zero-fills a missing term here, so nothing is silently
  approximated; the only substitution is OSAP's own capx := ppent - l12.ppent fallback.
- Why approx, not feasible: (a) the ppent fallback is not reproduced (Sharadar `ppnenet` zeros are vendor
  zero-fill, indistinguishable from missing; eligible on ~1.5% of the universe, see below);
  (b) denominator guard added (OSAP divides by l24.capx unguarded); (c) OSAP's datadate+6-month annual
  lag replaced by filing-date ARY alignment; (d) Sharadar positive "capex" (sign-inverted outflow,
  1.8% of universe bases) handled by base > 0.

## 2. Variables (exact source names)
`capx`, `ppent`, `at` (Compustat annual, USD millions, replicated 12 months from datadate+6m), `exchcd`,
`permno`, `time_avail_m`; derived `FirmAge`, `tempcrsptime`, `l12_ppent`, `l12/l24/l36_capx`.

## 3. Formula
Per firm-month; `lN` = the same row N calendar months earlier in the replicated monthly series:
```
FirmAge   = cumcount(permno)+1 ; set NaN if == months since 1926-07 (CRSP-start-censored)
capx      = capx.fillna(ppent - l12.ppent)   where capx is NaN and FirmAge >= 24   # BEFORE the lags
grcapx    = (capx - l24.capx) / l24.capx     # no guard: l24.capx == 0 -> +/-inf (or NaN if capx==0 too)
```
Growth of this year's capex over capex two fiscal years earlier (in words). Not winsorised; unbounded
above (tiny base), bounded below at -1 when both are non-negative outflows.
OSAP's save_predictor drops NULL values only; polars `from_pandas` maps NaN to null but leaves +/-inf, so
the published file plausibly carries inf for l24.capx == 0 with capx > 0 (not verified against the CSV).
The harness must null these: base <= 0 -> null, never floored.

## 4. Timing / lag; ART versus ARY
- OSAP: annual values known at datadate+6 months, replicated 12 months; l24 is a calendar-month lag of
  that replicated series, i.e. the fiscal year two years before. Signal 6-17 months stale, changes once a year.
- Sharadar: `ctx.fundamentals_yoy(["capex"], years=2, dimension="ARY")` gives capex at the latest
  fiscal year and at the year two earlier by REPORT PERIOD (tol 45 days); `years=1` only for the
  fallback. New fiscal year enters at the 10-K filing (about 3 months after year-end), 2-4 months
  fresher than OSAP. Updates once per firm-year.
- Flow item: ART capex is a TTM sum of four ARQ (99.5% within 1% of rolling sums); a year-over-year
  difference of TTM flows two years apart uses non-overlapping windows, so it does not smear (ART and ARY
  agree at fiscal year-end on 99.94% of pairs) but ART refreshes each quarter and is null 46% in 1998
  (ARY 0.5%). `dimension="ARY"` recommended (as ChInvIA). Never ARQ (quarterly capex is noisy and seasonal).

## 5. Filters
None in OSAP (SignalDoc Filter blank); harness universe applies. Financials not excluded.

## 6. Predicted sign
SignalDoc Sign = -1.0: high 2-year capex growth predicts LOW returns -> `ascending=False` (low = long side).
Cat.Economic: investment growth. Predictability in OP: 1_clear.

## 7. The mass-point question (MEASURED)
Measured on the snapshot with the harness `build_universe` / `MonthContext`: 46 signal months (every 6th
of the 276, 1998-12-31 .. 2021-06-30), universe ~1,740-2,670 names per month; capx = -ARY capex, l24 = -ARY
capex two fiscal years earlier, guarded form (capx - l24)/l24 for l24 > 0.
- Do-nothing firm (capex unchanged over two years): grcapx = 0 exactly. Share of universe: mean 0.04%,
  max 0.16% (2000-12 onward). Not a mass point.
- Real cluster: capex falls to exactly 0 from a positive base: grcapx = -1 exactly. Share: mean 0.16% of the
  universe (0.00-0.31%, 2000-12 onward). It is the LOWEST value (long side under Sign -1) but tiny.
- Modal share of the guarded cross-section (all 46 probe months): mean 0.20%, max 0.41% (1999-12) (mode usually -1.00; other months 0.0 or
  an isolated value). qcut yields 10 bins in all 46 probe months. No mass-point failure expected.
- Bases OSAP would keep or produce inf/NaN for, share of universe (window 2000-12 .. 2021-06 only: mean, min-max):
  base == 0 (l24 capex exactly 0): 2.72% (1.91-3.79) -> OSAP inf/NaN, here null;
  base < 0 (Sharadar positive capex): 1.82% (1.29-2.85) -> OSAP keeps, here null;
  base > 0: 86.5% (74.1-90.9).
- Value range of the guarded signal: p1 about -1.4 (values below -1 come from sign-inverted current
  capex), p99 about 14.8 (5.0-23.9). Heavy right tail; rank-based harness is robust.
- Tie handling: none in the factor; harness average-rank. Base <= 0 -> null (never floored).

## 8. History needed
Two fiscal years of annual capex before the latest: SF1 ARY starts 1997Q4/FY1997, so the two-year form exists
from ~2000. Measured coverage (computable guarded signal, % of universe): 24.1 at the 1999-01 rebalance
(signal 1998-12-31), 38.4 at 1999-06, 36.8 at 1999-12, 68.3 at 2000-06, 74.1 at 2000-12, then 79-91%
through 2021-06 (mean 2000-12 onward 86.5%, min 74.1, max 90.9). Latest-capex non-null 98.5% mean (94-100%);
the thin part is the l24 lag in 1999-2000. Expect the preflight first-month coverage warning (< 40%) for
1999; the first-year months carry few ranked names. `lookback_months` about 43 (24 + 15 max filing age + 4
filing lag), as ChInvIA. No SEP price window: no `history_months`.
ppent fallback eligibility: capx null = 1.5% of universe (mean, 2000-12 onward), and an eligible firm would
also need FirmAge >= 24 and a non-zero-filled `ppnenet`; dropped, noted.

## 9. OSAP metadata
Predictor | 1_clear | 1_good | Anderson and Garcia-Feijoo 2006 JF | continuous | Accounting | investment growth |
sample 1976-1999 | Acronym2 CAPXgr | Sign -1 | EW | LS quantile 0.2 | Portfolio period 12 | Start month 6 |
Filter none | Return 0.57, t 5.05 (port sort, Table 3B cegth2) | cites 587. Note: "called cegth2".

## 10. Proposed Sharadar mappings and deviations
| OSAP | Sharadar | deviation |
|---|---|---|
| capx | `-capex`, dimension ARY | sign flip; filing-date not datadate+6m; ART alt. noisier/46% null 1998 |
| l24.capx | `fundamentals_yoy(["capex"], years=2, dimension="ARY")` `capex_lag` | report-period alignment (tol 45d) not calendar-month lag |
| ppent fill | dropped | `ppnenet` zero-filled; ~1.5% eligible; capx stays null |
| division | `(capx - l24) / l24.where(l24 > 0)` | OSAP unguarded (inf/NaN); here base <= 0 null (4.5% of universe) |
Fields not in the map: none. `FactorDef`: inputs `SF1.capex`; `dimension="ARY"`; `ascending=False`;
`history_months` none; `family=None`. Predicted availability verdict: **approx**.
