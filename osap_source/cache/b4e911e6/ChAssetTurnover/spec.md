# ChAssetTurnover — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: APPROX (constructible; aco and lco are not in SF1)
Checked against `osap_source/field_map_index.yaml` (detail in `field_map.yaml` for aco/lco/lo).

| OSAP var | Sharadar | status (verified_on) | role |
|---|---|---|---|
| rect, invt, ap | receivables, inventory, payables | mapped (2026-09-30) | levels, 3 dates |
| ppent, intan | ppnenet, intangibles | mapped (blank) | levels, 3 dates |
| aco, lco | none | UNAVAILABLE | levels, 3 dates |
| lo | liabilitiesnc - debtnc | approx (blank) | level, 3 dates |
| sale | revenue | mapped (2026-09-30) | FLOW (ART TTM), 2 dates |

- **aco and lco have no SF1 field, and OSAP zero-fills both** (upstream `zero_fill_vars` holds
  aco, lco, lo, ap, intan, rect, invt). Rule: zero-filled by OSAP -> **approx, not infeasible**.
- OSAP's zero is only the MISSING case; real Compustat aco/lco are non-zero (several % of assets
  each) for most industrials, so zero-filling them for EVERY Sharadar firm is a systematic
  deviation. Two routes (translator picks, states it in the docstring):
  - **Route B (recommended; reproduces the real values).** Compustat identities
    `act = che + rect + invt + aco`, `lct = dlc + ap + txp + lco` give
    `aco = act - che - rect - invt`, `lco = lct - dlc - ap - txp`, hence
    `temp = (act - che) + ppent + intan - (lct - dlc) - lo`
    = `assetsc - (cashneq + investmentsc.fillna(0)) + ppnenet + intangibles
    - (liabilitiesc - debtc) - (liabilitiesnc.fillna(0) - debtnc.fillna(0))`. All inputs mapped.
    Deviations: txp (unavailable) stays inside lco so `-lco` is overstated by taxes payable
    (small); che is approx (financing-receivable overshoot); names with null
    assetsc/liabilitiesc/debtc (~20%: financials, REITs) are NaN.
  - **Route A (OSAP-literal):** `receivables + inventory + 0 + ppnenet + intangibles - payables
    - 0 - lo`. Faithful to OSAP's missing-case but omits aco and lco for all firms (base biased,
    more small or negative denominators); keeps financials as OSAP does, with noise.
- lo: liabilitiesnc CONTAINS long-term debt (>= debtnc on 99.8%), hence the difference; residual
  deviation is non-current deferred taxes. In Route B the FY2019+ lease inclusion in debtc/debtnc
  cancels against liabilitiesc/liabilitiesnc, so the debtnc lease trap is neutral.
- ppent: OSAP forward-fills null ppent (never zero-fills); Sharadar fills 0 for not-reported
  (exact-zero 5.9%; 2.6% in 1999-2003, 11.8% in 2021-26). A never-reported name is dropped by OSAP
  and kept here; accepted.
- Nulls (index): assetsc/liabilitiesc/debtc ~20%; other levels ~0.04%; revenue ART 7.8%
  (1998 reportperiods 40.6%). No IBES, options, patents, segments, ratings, pensions, xad, emp, ob,
  ppegt needed.

## 2. Variables by exact source name
`m_aCompustat`: gvkey, permno, time_avail_m, rect, invt, aco, ppent, intan, ap, lco, lo, sale.
Upstream (`upstream_CompustatAnnual.py`: FUNDA, consol C, INDL, STD, USD): rows with null at,
prcc_c or ni dropped; rect, invt, aco, intan, ap, lco, lo zero-filled; ppent, sale not.
`time_avail_m = datadate + 6 months`, annual record repeated over 12 monthly offsets, de-duplicated
on (permno, time_avail_m).

## 3. Formula
Soliman (2008) DeltaATO. The code comment "total assets" misleads: `temp` is an OPERATING net
asset base (operating assets less operating liabilities).

    temp = rect + invt + aco + ppent + intan - ap - lco - lo      (ppent ffilled by permno)
    AT   = sale / ((temp + temp[-12]) / 2)        ; AT < 0 -> NaN
    ChAT = AT - AT[-12]                            ; dropna

`[-12]` is a calendar-exact 12-month merge on (permno, time_avail_m), not a positional shift.
The signal therefore needs temp at t, t-12, t-24 (three fiscal years) and sale at t and t-12.
No zero guard in OSAP (sale/0 -> inf survives dropna). Translator: require avg base > 0 (a
negative base with positive sale gives AT < 0 -> NaN as in OSAP; zero sale over a negative base
gives -0.0, which is NOT < 0 and stays 0).

## 4. Timing / lag convention
- OSAP: fiscal-year data, available datadate + 6m, refreshed once a year. Sharadar ART as of
  datekey refreshes quarterly (balance items latest-filed levels, ART == ARQ; sale a TTM sum):
  up to ~9 months fresher, and the change spans the latest four quarters, not the fiscal year.
- **Use report-period alignment, not `fundamentals(lag_months=12)`.** `fundamentals_yoy` returns
  latest and year-ago only, the signal needs t, t-1y, t-2y: call `fundamentals_yoy(fields,
  years=1)` and `fundamentals_yoy(fields, years=2)`, or `fundamentals_history(n_periods=12)`
  selected by reportperiod within 45 days of t-1y and t-2y.
- **Flow item (sale): no TTM smear.** AT_t uses TTM sale at t, AT_{t-1} the TTM sale exactly four
  quarters earlier; the windows do not overlap, so the difference is a clean annual change under
  ART. Do NOT set `dimension=ARQ` (single-quarter sale over an annual base understates AT ~4x).
- ASC 842 (FY2019+): ppnenet may absorb right-of-use assets (level jump in 2019-2021). Caveat only.

## 5. Filters
predictor.py applies none. SignalDoc `Filter = abs(prc)>5` is OSAP's portfolio-stage filter; do
NOT add it in the factor (harness universe: price >= $1). Recorded deviation.

## 6. Predicted sign (SignalDoc)
`Sign = +1.0`: a rise in asset turnover predicts higher returns. Score = +ChAT (long high).
Cat.Signal Predictor; Cat.Economic `sales growth`; Cat.Form continuous; Cat.Data Accounting;
Soliman 2008 (Accounting Review), sample 1984-2002; Predictability in OP 1_clear; Signal Rep
Quality 1_good; Key Table 7 Model 1 DeltaATO. SignalDoc row 306 `pchgm_pchsale` is a Placebo
whose Acronym2 also reads ChAssetTurnover; not this predictor.

## 7. The mass-point question
A do-nothing firm (unchanged sale and balance sheet) has AT_t = AT_{t-1}, ChAT = 0, but only if
sale and all three temp levels repeat EXACTLY (the average-base denominator shifts with any
balance change): essentially no operating firm. The real mass point is the **zero-revenue firm**:
sale = 0 in both years gives AT = 0 twice and ChAT = 0. Universe exact-zero revenue (level) is
0.48% (1999), 0.28% (2008), 2.04% (2020), 1.82% (2021); both years zero is a subset, roughly
0.2-1.5% of scored names, rising over time. Zero revenue over a positive base gives AT = 0; over a
negative base -0.0 (kept); over a zero base NaN. Ties: average rank (harness). Hazards:
- Do NOT zero-fill sale, assetsc, liabilitiesc or debtc: null sale is NaN in OSAP.
- Route A's aco/lco zero is structural (moves the base, not the output ties).
- Near-zero base makes AT explosive (heavy tails; ranks absorb it).

## 8. History needed (snapshot starts 1998-01, ART breadth from 1997Q4)
- Latest period P, P-1y, P-2y: the earliest held period is 1997Q4, so the earliest P is 1999Q4
  (datekey ~2000-03). Signal months 1999-01 .. ~2000-02 (~14 of 276, ~5%) are empty by
  construction even though levels are ~99.9% populated. First full month ~2000-03; preflight
  must report first-month coverage.
- Sale at P-1y: ART flows ~50% populated for 1998Q1-Q3 (universe revenue coverage 57-59% in
  1998-12..1999-02, 92.5% from 1999-03); 1998Q4 on is fine. Early nulls are NaN, never zeros.
- `history_months` >= 24 plus filing lag and `max_fundamental_age_months` (recommend 27+; check
  it does not shrink the scored set). Route B coverage ceiling ~80% of names.

## 9. OSAP metadata
Acronym ChAssetTurnover; Soliman 2008; Cat.Economic sales growth; Sign +1; Start Month 6;
Portfolio Period 12; EW; LS Quantile blank; Filter abs(prc)>5; T-Stat 5.12; Acronym2 ATurnGr.
Source `Signals/pyCode/Predictors/ChAssetTurnover.py` at b4e911e69678a7424f318617a61d813f54183123.
Cached: predictor.py, signaldoc_row.csv, upstream_* (shared with Accruals). Output
`ChAssetTurnover.csv [permno, yyyymm, ChAssetTurnover]`.

## 10. Proposed Sharadar mappings and deviations
1. One-to-one: receivables, inventory, payables, intangibles, ppnenet (0 when not reported), revenue (ART TTM).
2. aco, lco -> Route B (recommended) or 0 (Route A); che approx; lo approx (section 1).
3. ART, report-period aligned, quarterly refresh; no ARQ. Score = +ChAT; reads via MonthContext.
4. Guards: avg base > 0; AT < 0 -> NaN; null sale -> NaN; ChAT needs AT_t and AT_{t-1}.
5. Not in field_map: none. field-checker to verify (blank): ppnenet, intangibles, liabilitiesnc, debtnc.
