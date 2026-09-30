# grcapx3y — Capex relative to the prior three-year average (Anderson and Garcia-Feijoo 2006, JF, Table 3D cegth3)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/ZZ1_grcapx_grcapx1y_grcapx3y.py`
(cached `predictor.py`, `upstream_CompustatAnnual.py`, `upstream_SignalMasterTable.py`, `signaldoc_row.csv`).
Same script as grcapx (spec `grcapx/spec.md`); this spec mirrors it. Coordinator decision
`grcapx_fallback_and_base` applies: capx = -SF1.capex at ARY, ppent fallback NOT reproduced, base <= 0 -> NaN.
DATA_SHA 198b281de1a0. Field statuses are mappings; `compustat.capx` and `compustat.ppent` verified_on 2026-09-30.

## 1. Data availability — VERDICT: approx (constructible; declared deviations, no unavailable input)

| input | field_map key | Sharadar | status | note |
|---|---|---|---|---|
| `capx` (m_aCompustat, annual) | `compustat.capx` | SF1 `capex`, use `-capex` | mapped, verified 2026-09-30 | cash OUTFLOW (negative on 90.6% of non-null); ARY = fiscal-year flow |
| `ppent` (capx fallback only) | `compustat.ppent` | SF1 `ppnenet` | mapped, verified | vendor zero-fill; fallback dropped (as grcapx) |
| `at`, `exchcd`, FirmAge | - | - | - | `at` loaded, unused; `exchcd` sample filter only; FirmAge gates the ppent fallback only (moot) |

- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt. `zero_fill_vars` in
  `upstream_CompustatAnnual.py` does not contain capx or ppent, and the predictor has no `fillna(0)`: OSAP
  never zero-fills a missing term, so nothing is silently approximated. The only OSAP substitution is its
  own capx := ppent - l12.ppent fallback (applied BEFORE the lags, so it would also fill lagged capx).
- Why approx, not feasible: (a) ppent fallback not reproduced (capx null on ~1.5% of the universe in
  grcapx's probe; here `cur` null 1.4% mean 2001-06 onward); (b) denominator guard added (OSAP divides by the
  lag sum unguarded); (c) OSAP's datadate+6m replicated-annual timing replaced by filing-date ARY alignment;
  (d) three year-lags required instead of one, so history starts later (section 8).

## 2. Variables (exact source names)
`capx`, `ppent`, `at`, `exchcd`, `permno`, `time_avail_m`; derived `FirmAge`, `tempcrsptime`, `l12_ppent`,
`l12_capx`, `l24_capx`, `l36_capx`.

## 3. Formula
Per firm-month; `lN` = the same row N calendar months earlier in the replicated (annual-held-12-months) series:
```
capx      = capx.fillna(ppent - l12.ppent)  where capx is NaN and FirmAge >= 24      # BEFORE the lags
grcapx3y  = capx / (l12.capx + l24.capx + l36.capx) * 3
```
In words: current-year capex divided by the AVERAGE of the three previous fiscal years' capex. It is a
level ratio, not a growth rate: 1.0 means "unchanged from the trailing three-year mean" (no "-1"). The
SignalDoc Detailed Definition says "sum" and omits the x3; the code multiplies by 3 (code is authority).
Any NaN lag makes the sum NaN, so all three lags are required. Not winsorised; `base == 0` -> +/-inf or NaN
in OSAP (polars maps NaN to null but leaves inf; the published CSV plausibly carries inf, not verified).
Harness form: `capx / base.where(base > 0) * 3` with `base = l12+l24+l36`; base <= 0 -> null, never floored.

## 4. Timing / lag; ART versus ARY
- OSAP: annual values known at datadate+6 months, replicated 12 months; signal changes once a year and is
  6-17 months stale; lags are calendar-month shifts of that series.
- Sharadar: `fundamentals_yoy` supports ONE lag only, so use
  `ctx.fundamentals_history(["capex"], n_periods>=8, dimension="ARY")` and align the latest filing and the
  periods 1, 2 and 3 fiscal years earlier by REPORT PERIOD (|gap| <= 45 days, closest wins, same rule as
  `fundamentals_yoy`). New fiscal year enters at the 10-K filing (about 3 months after year-end), 2-4 months
  earlier than OSAP. The measurement below used exactly this alignment.
- Flow item: ART capex is a TTM sum; year-over-year windows one, two, three years apart do not overlap, so
  there is no smear, but ART refreshes each quarter and is null 46% in 1998 (ARY 0.5%; see grcapx).
  `dimension="ARY"` recommended; never ARQ (quarterly capex noisy, seasonal).

## 5. Filters
None in OSAP (SignalDoc Filter blank); harness universe applies. Financials not excluded.

## 6. Predicted sign
SignalDoc Sign = -1.0: high current capex relative to its own 3-year average predicts LOW returns ->
`ascending=False`. Cat.Economic: investment growth. Predictability in OP: 1_clear.

## 7. The mass-point question (MEASURED)
Measured on the snapshot with the harness `build_universe` / `MonthContext`: 46 signal months (every 6th of
the 276, 1998-12-31 .. 2021-06-30), universe 1,740-2,674 names per month (all 276 months: 1,739-2,867, mean
1,965). Signal = guarded form, capx = -ARY capex, three lags by report period.
- Do-nothing firm (capex constant across four years): grcapx3y = 1.0 exactly. Share of the ranked
  cross-section: 0.00% in most months, max 0.11% (2021-06); mean 0.03% from 2001-06 on. Not a mass point.
- Real cluster: capex exactly 0 this year from a positive base -> signal exactly 0. Share 0.27% mean over all
  46 months, 0.25% mean (max 0.49%) from 2001-06 on. It is the LOWEST cluster and sits at the long end under
  Sign -1 but is tiny.
- Modal share of the ranked cross-section: mean 0.28%, max 0.76% (2000-06). qcut yields 10 bins in all 46
  months. No mass-point failure expected.
- Base handling, share of the universe (2001-06 .. 2021-06, 41 probe months, mean): base > 0 83.0%;
  base == 0 (all three lags present, sum exactly 0) 2.32%; base < 0 (sign-inverted Sharadar capex in the
  lags) 1.35% -> the last two are null here (OSAP inf/NaN or negative kept).
- Value range (ranked, 2001-06 on): p1 about -0.42 (range -1.52 .. 0), p99 about 7.7 (4.0-12.2). Negative
  values come from sign-inverted current capex (positive Sharadar `capex`). Heavy right tail; ranks robust.
- Tie handling: none in the factor; harness average-rank. No floor.

## 8. History needed
Three fiscal years of annual capex before the latest: SF1 ARY starts FY1997, so the four-year form exists
from the filings of FY2000 (early 2001). `lookback_months` about 55-58 (36 + 15 max filing age + 4 lag).
No SEP price window: no `history_months`. Measured coverage (computable guarded signal, % of universe):
12.7 at 1998-12, 19.4 at 1999-06, 20.1 at 1999-12, 34.8 at 2000-06, 39.3 at 2000-12, then 69.0 at 2001-06
and 79-88 thereafter (mean 83.0, min 69.0, max 87.9 over 2001-06 .. 2021-06; mean 76.7 over all 46 probe
months; 5 of 46 probe months under 40%). Expect the preflight first-month coverage warning (< 40%) for
1999-2000. `cur` (latest capex non-null) is 89-99.6% throughout; the thin part is the 3rd lag in 1999-2000.
The 1999-2000 months carry few ranked names (still >= 30 per decile above ~300 names).

## 9. OSAP metadata
Predictor | 1_clear | 1_good | Anderson and Garcia-Feijoo 2006 JF | continuous | Accounting | investment growth |
sample 1976-1999 | Acronym2 CAPXgr3y | Sign -1 | EW | LS quantile 0.2 | Portfolio period 12 | Start month 6 |
Filter none | Return 0.6, t 4.71 (port sort, Table 3D cegth3) | cites 587.
Note: "We follow OP, not HXZ. OP notation is odd, uses cegth2 and cegth3 but no cegth."

## 10. Proposed Sharadar mappings and deviations
| OSAP | Sharadar | deviation |
|---|---|---|
| capx | `-capex`, ARY latest filing | sign flip; filing-date not datadate+6m |
| l12/l24/l36 capx | `fundamentals_history(["capex"], n_periods=8, dimension="ARY")`, periods 1/2/3 fiscal years back, |gap|<=45d | report-period alignment, not calendar-month lags; three lags all required |
| ppent fallback | dropped | `ppnenet` zero-filled; capx stays null (coordinator decision) |
| division | `capx / (l12+l24+l36).where(> 0) * 3` | OSAP unguarded; base <= 0 -> null (3.7% of universe) |
Fields not in the map: none. `FactorDef`: inputs `SF1.capex`; `dimension="ARY"`; `ascending=False`;
`osap_acronym="grcapx3y"`; `history_months` none; `family=None`. Predicted availability verdict: **approx**.
