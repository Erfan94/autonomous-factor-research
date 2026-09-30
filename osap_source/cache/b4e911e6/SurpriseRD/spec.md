# SurpriseRD — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: APPROX inputs (xrd vendor-zero-filled); PREFLIGHT_FAILED, on two independent grounds (binary mass point; coverage under the xrd ruling)
| OSAP input (`m_aCompustat`) | field_map key | Sharadar | status | OSAP missing-item rule |
|---|---|---|---|---|
| `xrd` | `compustat.xrd` | SF1 `rnd` (ART, yoy by reportperiod) | mapped, VENDOR ZERO-FILL (63% of non-null ART is exact 0) | NOT zero-filled (not in `zero_fill_vars`; no `fillna` in the predictor): NaN rows get no signal |
| `revt` | `compustat.revt` | SF1 `revenue` (ART, TTM) | mapped | NaN; `xrd/revt` NaN if missing |
| `at` | `compustat.at` | SF1 `assets` | mapped | NaN |
- No IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob or ppegt input.
- The binding item is `xrd`. Ruling in force (`compustat.xrd` map entry; `vendor_zero_fills` trap): a bare xrd without an OSAP fill treats `rnd == 0` as MISSING
  (genuine reported zeros are dropped too; the two cannot be separated). SurpriseRD is such a case, so **variant A (faithful to OSAP's NaN handling) = rnd == 0 -> missing.**
- MEASURED on the harness universe, 276 signal months 1998-12-31 .. 2021-11-30 (`build_universe` + `MonthContext.fundamentals_yoy`, ART, year-ago period aligned by reportperiod), n mean 1,965:
  | quantity | A: `rnd == 0` -> missing (ruling) | B: `rnd == 0` kept as 0 (deviation) |
  |---|---|---|
  | scored names / month (mean) | 570 (min 226, max 908) | 1,766 (min 801, max 2,310) |
  | coverage, pooled n-weighted (per-month mean; min / max) | **29.0%** (29.2%; 9.9 / 37.2) | 89.9% (90.8%; 35.1 / 98.2) |
  | months with coverage >= 40% | **0 of 276** | 273 of 276 |
  | ones (mean names / share of scored; share min-max) | 181 / 32.0% (15.4-48.1%) | 186 / 10.5% (4.9-16.6%) |
  | zeros = modal value (share of scored, mean; min-max) | 68.0% (51.9-84.6%) | 89.5% (83.4-95.1%) |
  | distinct values; `qcut(q=10)` bins | 2; 1 bin in 272 months, 2 in 4 | 2; 1 bin in 274 months, 2 in 2 |
  Underlying (universe means): `rnd` non-null 96.1% of names; exact 0 on 66.8% of those; `rnd` non-null in BOTH years 89.9%.
- **Recommendation: `preflight_failed`.** (i) Two distinct values under EITHER variant: the modal share exceeds the 10% cliff in all 276 months (68.0% / 89.5% mean), and
  qcut yields 1-2 bins, so ten deciles cannot be formed and no tie handling changes that. (ii) Under the ruling (A) coverage is 29.0% with 0 of 276 months at the 40% bar.
  Variant B clears coverage but is not OSAP's signal (R&D-less firms enter as 0 instead of NaN, and initiators with a lagged zero score 1, see section 3) and is still binary.
  The verdict therefore does not hinge on the xrd ruling.

## 2. Variables (exact source names)
`m_aCompustat`: `gvkey, permno, time_avail_m, xrd, revt, at`. `xrd_lag12 = xrd.shift(12)`, `at_lag12 = at.shift(12)` within permno (monthly rows; annual values replicated 12 months).

## 3. Formula
```
c1 = xrd/revt > 0;  c2 = xrd/at > 0;  c3 = xrd/xrd_lag12 > 1.05;  c4 = (xrd/at)/(xrd_lag12/at_lag12) > 1.05
c5 = xrd.notna();   c6 = xrd_lag12.notna()
SurpriseRD = 1 if c1&c2&c3&c4&c5&c6;   0 if not(all of those) and c5&c6;   NaN if xrd or xrd_lag12 is NaN
```
Binary: R&D positive relative to sales and assets, R&D up > 5% year over year, and R&D/assets up > 5%. Pandas detail: xrd_lag12 = 0 with xrd > 0 gives a ratio of +inf,
which passes c3 and c4, so a genuine zero-to-positive R&D initiation scores 1 (only reachable where OSAP has a reported 0, i.e. rarely; under variant B every vendor-zero initiator does).
0/0 and negative-ratio cases are False -> 0. No winsorising, no standardising.

## 4. Timing / lag convention
- OSAP: annual fundamentals, available at datadate + 6 months, replicated each month for 12 months; the signal changes once a year and compares consecutive fiscal years.
- Harness: SF1 ART is a TTM rolling sum refreshed every quarter at the filing `datekey`, so "year-ago" = the ART value four quarters earlier (aligned by reportperiod, `fundamentals_yoy`). The
  growth test is on TTM R&D, updated 4x a year: a different cadence and a smoothed growth rate versus OSAP's fiscal-year comparison. `dimension="ARY"` reproduces the fiscal-year cut
  (annual, one update a year) and is the closer match; ART was used for the measurement above (the project default), ARY not measured. Coverage differs little because both drop the same vendor-zero names.
- ART-as-of-filing: the filing lag (median ~44 days) is shorter than OSAP's 6-month rule, so the signal is available earlier. Flow item `rnd`: the year-over-year comparison is between two non-overlapping TTM windows (reportperiod matched, tol 45 days), so no smear; ARQ (single-quarter flow) would be a different signal.

## 5. Filters
SignalDoc `Filter` empty. (Universe: harness US-common NYSE/NASDAQ/NYSEMKT, price >= $1, relative size/ADV screens.)

## 6. Predicted sign
`Sign = +1.0` (Eberhart, Maxwell and Siddique 2004: an unexpected R&D increase is followed by higher returns; Table 5 LS t = 3.54 as recorded in SignalDoc).

## 7. The mass-point question
A do-nothing firm (no R&D, or R&D growth <= 5%) scores 0. Under A: 68.0% of scored names are 0 (range 51.9-84.6%), i.e. 19.8% of the universe is a 0 and 9.2% a 1 (29.0% scored); under B:
89.5% of scored names are 0 (and ~10% of the universe has no R&D history at all). Ones run 79-310 names/month (A), so a "1" bucket clears 30 names every month, but the
D10 bucket is the whole tied block of ones, and the deciles below it are one tied block: D1..D9 are not distinct. Tie handling: average rank gives two values (IC is point-biserial,
computable); the LS bars need either ten deciles (impossible) or a two-bucket rule the pre-registered design does not define. Not reproduced: OSAP's EW long-only event-style portfolio on the ones.

## 8. History needed (snapshot starts 1998-01)
One year of `rnd`/`assets` lag: first scorable universe month 1998-12 (A coverage 9.9% in the first two months, 801 of 2,281 names have both years at 1998-12), rising to 16.7% (447 of 2,674) at 1999-12.
Coverage is rising through 1999 for a data reason (SF1 history starts 1998-01); under A it never reaches 40%. `history_months` not needed (no return window); lookback 12-15 months.

## 9. OSAP metadata
Eberhart, Maxwell and Siddique (2004), JF; Cat.Data Accounting; Cat.Economic R&D; discrete; sample 1974-2001; Acronym2 SurpriseRD; Key Table "5A EW"; test "long port FF3 alpha";
EW; Portfolio Period 1, Start Month 6; 1_clear / 1_good; SignalDoc Notes: Table 3 event study, Table 5 LS ports, p-value 0.000 so t set by norm dist at p = 0.0004; FF3 loadings should roughly cancel.
Source `Signals/pyCode/Predictors/SurpriseRD.py`.

## 10. Proposed Sharadar mappings
`xrd = SF1.rnd` (ART or ARY; `rnd == 0 -> NaN`), `revt = SF1.revenue`, `at = SF1.assets`; lags via `ctx.fundamentals_yoy(["rnd","revenue","assets"], years=1)` (dimension per note above).
Deviations: `rnd` vendor zero (genuine zero vs non-reporter indistinguishable; both dropped under A); ART TTM cadence vs fiscal-year; filing lag vs 6-month rule. All three fields are in `field_map_index.yaml`
(`compustat.xrd`, `.revt`, `.at`). Declare inputs `SF1.rnd, SF1.revenue, SF1.assets`. Not a preflight-clean candidate: see section 1.
