# EarningsConsistency — average earnings growth over the previous 48 months with sign-consistency filters (Alwathainani 2009, BAR, Table 11A CLG-CHG)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/EarningsConsistency.py` (cached `predictor.py`). DATA_SHA 198b281de1a0.
Written fresh from the source and `field_map_index.yaml`. Only `m_aCompustat.epspx` is read; no price, no SignalMasterTable.

## 1. Data availability (verdict: APPROX, feasible; one input, `eps`)

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `epspx` (annual EPS excl. extraordinary items) | `compustat.epspx` | SF1 `eps`, annual dimension `ARY` (proposed) | mapped | NaN (not in zero_fill_vars) |

- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt; nothing zero-filled or dropped.
- `eps` = netinccmn/shareswa: includes discontinued operations, after preferred dividends (Compustat epspx excludes extraordinary items; basic). `eps` is restated to TODAY's split basis on every historical row
  (known trap `sf1_share_counts_split_restated`), i.e. all years of one firm sit on one basis, so the growth ratios below are scale-invariant and unaffected by splits. No price enters.
- Field-checker (THIS snapshot), the open question: ARY `eps` coverage by reportperiod year 1993-1999 for universe names (map: null 1.9% ARY overall; universe ARY coverage of netinccmn 94.7% at 1999-01, but the history BACK from FY1997 is what matters;
  snapshot broad from calendardate 1997Q4, ARY reaches ~1993 for some names). Also `eps` exact-zero share and the 2-decimal rounding of `eps` (lattice), and null share of `eps` in ARY universe rows 1999-2021.

## 2. Variables (exact source names)
`epspx` (annual, dollars per share, available at datadate + 6 months, repeated 12 months), `permno, time_avail_m`. Derived: `egrowth`, `l12_*`..`l48_*` (12-month row lags), `exception`.

## 3. Formula in words and key lines
Annual EPS growth is the change in EPS divided by the average absolute EPS of the two prior years; the signal is the average of the five most recent annual growth rates (current and 12/24/36/48 months back), blanked when
EPS is missing, when EPS more than sextupled in ratio, or when the growth sign is inconsistent with the previous year's.
```
egrowth  = (epspx - l12_epspx) / (0.5 * (abs(l12_epspx) + abs(l24_epspx)))      # inf -> NaN
EarningsConsistency = mean(egrowth, l12_egrowth, l24_egrowth, l36_egrowth, l48_egrowth)   # skipna: one valid term is enough
exception = epspx.isna() | l12_epspx.isna()
          | abs(epspx / l12_epspx) > 6                                              # also true when l12_epspx == 0 (inf)
          | (egrowth > 0) & (l12_egrowth < 0) & egrowth.notna()
          | (egrowth < 0) & ((l12_egrowth > 0) | l12_egrowth.isna()) & egrowth.notna()
-> NaN where exception
```
ASYMMETRY (do not symmetrise): negative growth is excluded when the prior growth is positive OR MISSING; positive growth is excluded only when the prior growth is NEGATIVE (missing prior growth is kept). `egrowth == 0` triggers neither sign test.
`egrowth` needs `epspx`, `l12_epspx`, `l24_epspx` all non-NaN and a non-zero denominator; `0/0` is NaN (not > 6), so `l12 == 0` with `epspx != 0` is excluded; `l12 == epspx == 0` passes the ratio test, and its growth is NaN only if `l24 == 0` too, otherwise exact `egrowth = 0` (kept, feeds the exact-0 mass in 7: preflight should count exact-0 terms as well as exact-0 scores).

## 4. Timing / lag convention
- OSAP: annual EPS at datadate + 6 months for 12 months; `egrowth` is an annual step function of the panel (all lags step together), so the signal changes once a year (June for December filers) plus nothing monthly. `shift(12)` counts panel ROWS, equal to a fiscal year only when contiguous.
- Here: `FactorDef(dimension="ARY")` and `ctx.fundamentals_history(["eps"], n_periods=7, dimension="ARY")` (or `fundamentals_yoy(years=1..6)`), aligned by reportperiod (known trap `yoy_by_report_period`; `lag_months=12` lands on the wrong period ~15% of the time). The annual value appears at the 10-K `datekey`
  (about 2-3 months after FYE) vs OSAP's FYE + 6 months, so the score is 3-4 months earlier than OSAP. `max_fundamental_age_months` = 15 gates the latest 10-K; a filer more than 15 months stale scores NaN.
- Why not ART: ART eps is a trailing-four-quarter SUM that moves every quarter; a 12-month ART difference is a TTM-to-TTM change on a different cadence from OSAP's fiscal-year step, and the full window (eps 72 months back) would not exist until ~2004 on ART (first full TTM 1998Q4).
  The quarterly dimension is NOT appropriate either (annual-on-annual growth). State `dimension="ARY"`: it is the one sanctioned per-factor deviation.
- Minimum history: one `egrowth` term needs EPS at 0, -12, -24 months (3 annual values); the exception sign test needs `l12_egrowth`, i.e. EPS at -36 (4 values) for a negative-growth name to survive; the full five-term mean needs 7 annual values (EPS at 0..-72 months). Partial windows score
  (skipna mean), with a mean of 1-4 terms early; with ARY history starting ~1993-1997 (checker) the five-term mean is not available before ~FY2002 filings.

## 5. Filters
- In the code: the `exception` block (missing EPS, |ratio| > 6, sign inconsistency). SignalDoc `Filter` `abs(prc)>1` (and the Definition's "Exclude if price less than 5") are portfolio-stage, NOT in `predictor.py`: not reproduced; universe price >= $1.
- SignalDoc Definition: "Average earnings growth over previous 48 months. ... Exclude if price less than 5, absolute value of 12 month earnings growth greater 600%, or earnings growth and earnings growth 12 months ago have different signs." The code (ratio test, asymmetric sign test) is the authority.
- Coverage RISK: requires three years of EPS and passes only sign-consistent firm-years. Rough prior (not measured): growth positive ~55% of the time, prior growth positive given that ~55%; negative growth needs negative prior growth (~50%); about 40-55% of firm-years with 3+ years of EPS survive, and firms with < 3 years of ARY history or a zero EPS drop first. The 40% Stage-1 coverage bar is AT RISK,
  especially in 1999-2002 (thin ARY history). Preflight measures it.

## 6. Predicted sign
SignalDoc `Sign = +1.0` (high consistency -> high return); Stock Weight EW; `Cat.Form` continuous; `Cat.Economic` earnings growth; Signal Rep Quality 2_fair. Orientation: long HIGH. `FactorDef(ascending=True)`.

## 7. The mass-point question
- A do-nothing firm (no new 10-K) holds the same score for 12 months under OSAP's step, and under ARY here between 10-K filings: it equals last period's value, continuous across firms, so no single common value. Cross-sectional mass points come from `eps`'s 2-decimal rounding: EPS of 0.01-0.30 gives coarse growth lattices; the 5-term average thins it but with
  a single valid term (1999-2002) the lattice is visible. Exact `egrowth == 0` (EPS unchanged) needs the same rounded EPS in two consecutive years, plausible for a few tenths of a percent of names.
- Expected modal share < 1% of scored names (2.0% of ARQ eps exact zero in the map; ARY not measured). Preflight to report the exact-0 share and modal share, and the decile collapse in 1999-2002. Ties: rank(method="average"); no floor, no winsorisation (growth is unbounded when the two denominators are small, e.g. eps 0.5 vs lags 0.1 gives +4; the harness ranks).
- The scored cross-section is selected on sign consistency: expect a structural lean toward non-loss, steadily growing or steadily shrinking firms; that is the construction, not a bug.

## 8. History needed (snapshot starts 1998-01)
ARY annual EPS for up to seven fiscal years. Snapshot SF1 broad from 1997Q4 (ARY to ~1993 for some names). At 1999-01 the latest known 10-K is FY1997/98 (filed 1998 / early 1999); three annual values need FY1995-FY1997 rows, so early coverage is thin and is the field-checker's measurement;
the five-term window is first complete around FY2002 (filed 2003). `lookback_months` ~ 84; no return window, no `history_months`.

## 9. OSAP metadata (SignalDoc)
Acronym EarningsConsistency; Acronym2 EarnCons; Alwathainani; 2009; BAR; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 2_fair; Cat.Form continuous; Cat.Data Accounting; Cat.Economic earnings growth; SampleStart 1971, End 2002;
Key Table "11A CLG-CHG"; Test "LS port"; Sign +1.0; Return 0.3608; T-Stat 2.67; Stock Weight EW; LS Quantile blank; Portfolio Period 12; Start Month 6; Filter `abs(prc)>1`. Notes: "Could not access OP, so we used the Alwathainani's dissertation from VCU. We follow MP, which is simpler than OP."

## 10. Proposed Sharadar mappings and deviations
```
epspx -> SF1 eps, dimension="ARY", ctx.fundamentals_history(["eps"], n_periods=7, dimension="ARY")      [compustat.epspx, mapped]
e0, e1, ..., e6 = eps at reportperiod, -1y, ..., -6y (aligned by reportperiod, tol ~45 days)
g_k = (e_k - e_{k+1}) / (0.5 * (|e_{k+1}| + |e_{k+2}|)),  k = 0..4 ; inf -> NaN
score = mean(g_0..g_4, skipna);  NaN where: e0/e1 missing, |e0/e1| > 6 (incl. e1 == 0),
        (g_0 > 0 & g_1 < 0), (g_0 < 0 & (g_1 > 0 or g_1 missing))      # asymmetric, as OSAP
ascending=True
```
Deviations: (a) `eps` includes discontinued operations and preferred dividends (epspx excludes extraordinary items; optional continuing-EPS rebuild `(netinc + netincdis - prefdivis)/shareswa` ARY uses the INVERTED `netincdis` sign and is not in the map; not proposed);
(b) annual dimension ARY at the 10-K `datekey` (3-4 months earlier than OSAP's FYE + 6, between 10-Ks the value is a step, as OSAP's); (c) periods aligned by reportperiod, not by panel row; (d) 12-month panel shift replaced by fiscal-year alignment, changing behaviour for fiscal-year changes and gaps;
(e) `abs(prc)>1` and the price filter not reproduced; (f) `FactorDef.dimension="ARY"` override is recorded in the result block (`dimension_overrides`). Fields not in the map: none for the proposal (`netincdis`, `prefdivis` only in the unproposed alternative; `prefdivis` is mapped via `compustat.dvp`).
`family=None` until Phase C.
