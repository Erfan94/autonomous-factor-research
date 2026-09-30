# GrLTNOA — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: APPROX (constructible; aco, lco not in SF1; ao, lo, che approximate)
Checked against `osap_source/field_map_index.yaml` (detail in `field_map.yaml` for aco/lco/ao/lo).

| OSAP var | Sharadar | status (verified_on) | role |
|---|---|---|---|
| rect, invt, ap, intan, ppent | receivables, inventory, payables, intangibles, ppnenet | mapped (2026-09-30) | levels, 2 dates |
| at | assets | mapped (2026-09-30) | level, 2 dates |
| dp | depamor | mapped (2026-09-30) | FLOW (ART TTM), 1 date |
| aco, lco | none | UNAVAILABLE | levels, 2 dates |
| ao | assetsnc - ppnenet - intangibles - investmentsnc | approx (blank; investmentsnc verified) | levels |
| lo | liabilitiesnc - debtnc | approx (2026-09-30) | levels |

- **aco and lco have no SF1 field; OSAP ZERO-FILLS both** (upstream `zero_fill_vars` holds aco, lco, ao, lo, ap,
  intan, rect, invt, dp, che, act, lct). Rule: zero-filled by OSAP -> **approx, not infeasible**. No IBES,
  options, patents, segments, ratings, pensions, xad, emp, ob or ppegt needed.
- OSAP's zero is only the missing case; real aco/lco are ~3% / ~9% of assets (medians, below), so zero-filling
  them for every Sharadar firm is a systematic deviation. **Here it matters more than in a denominator:
  the accrual term differences aco and lco directly (d aco - d lco), so dropping them changes the accrual.**
- Two routes (the choice is the caller's; ChAssetTurnover was translated on Route A):
  - **Route A (OSAP-literal):** aco = lco = 0. LTNOA = rect + invt + ppent + intan + ao - ap - lo;
    accrual numerator = d rect + d invt - d ap - dp.
  - **Route B (recommended; rebuilds real aco/lco from the identities):** aco = act - che - rect - invt,
    lco = lct - dlc - ap - txp. With ao = assetsnc - ppnenet - intangibles - investmentsnc the PPE, intangible and
    ao terms collapse, and LTNOA becomes
    `(assetsc - che) + (assetsnc - investmentsnc) - (liabilitiesc - debtc) - (liabilitiesnc - debtnc)`,
    che = cashneq + investmentsc.fillna(0). Accrual numerator =
    `d(assetsc - che) - d(liabilitiesc - debtc) - dp`. Residual deviations: che (investmentsc carries financing
    receivables for vendor-finance filers), txp (unavailable) stays inside lco, non-current deferred taxes inside lo.
- Measured, harness universe (build_universe + MonthContext, ART, fundamentals_yoy years=1), 7 probe months
  1999-01, 1999-06, 2000-03, 2003-12, 2008-12, 2015-06, 2021-11: Spearman(A, B) of the final signal 0.92-0.96
  (0.946, 0.937, 0.919, 0.932, 0.957, 0.952, 0.920); of the level change alone 0.83-0.87. Medians: aco proxy
  0.022-0.031 of assets, lco proxy 0.076-0.094, LTNOA/at 0.50-0.58, accrual term -0.033 to -0.043.
- **Coverage (both routes identical; both need the classified balance sheet).** assetsc / assetsnc / liabilitiesc /
  liabilitiesnc / debtc / debtnc are null on ~20% of rows (91% financials and REITs); never zero-filled (ruling),
  so those names are NaN whereas OSAP keeps them with zero-filled ao/lo/aco/lco. Measured over 275 signal
  months (1999-01 .. 2021-11): mean 77.1%, median 77.6%, min 38.2%; **only 1999-01 is below 40%**
  (39.1%; 1999-02 45.5%; 1999-03 70.2%; 71-80% thereafter, 79.0% 2003-12, 74.4% 2021-11).

## 2. Variables by exact source name
`m_aCompustat`: gvkey, permno, time_avail_m, rect, invt, ppent, aco, intan, ao, ap, lco, lo, at, dp.
Upstream (`CompustatAnnual.py`: FUNDA, rows with null at, prcc_c or ni dropped): rect, invt, aco, intan, ao, ap,
lco, lo, dp zero-filled; ppent and at not. `time_avail_m = datadate + 6 months`, annual record repeated 12 months.
Lags are `shift(12)` of the monthly panel = the prior fiscal year's record.

## 3. Formula
Fairfield, Whisenant and Yohn (2003) growth in long-term net operating assets: change in NOA/at minus accruals.

    ltnoa_t   = (rect + invt + ppent + aco + intan + ao - ap - lco - lo) / at      (and ltnoa_{t-12})
    accrual   = ( d rect + d invt + d aco - (d ap + d lco) - dp ) / ((at + at_{t-12}) / 2)
    GrLTNOA   = ltnoa_t - ltnoa_{t-12} - accrual

Only d of the working-capital items (rect, invt, aco, ap, lco) enters the accrual; ppent, intan, ao, lo enter only
through the level change. No guard on at (at <= 0 gives inf or a sign flip): translator requires at > 0 at both
dates and the average. Null dp is zero-filled by OSAP; here zero-fill dp ONLY on a filing whose revenue (TTM
window) is populated (measured: dp null on 0.1-2.5% of scorable rows, of which 0.1-1.2% have revenue present);
a null dp on an unpopulated early ART row stays NaN (1999-01: 47% of ART dp null, a data-start artefact).

## 4. Timing / lag convention
- OSAP: fiscal-year data available datadate + 6 months, refreshed once a year; change = fiscal year on fiscal year.
  Sharadar ART as of filing date (datekey) refreshes quarterly (balance items latest-filed levels, ART == ARQ):
  up to ~9 months fresher; the change spans the latest four quarters.
- **Use report-period alignment: `ctx.fundamentals_yoy(fields, years=1)`**, not `fundamentals(lag_months=12)`.
- **Flow item dp: no smear.** It is one TTM value at the current date, added once (not differenced); do NOT set
  `dimension=ARQ` (a single quarter over an annual-scale base would understate the accrual ~4x).
- ASC 842 (FY2019+): right-of-use assets enter ppnenet / other assets while lease liabilities sit inside
  debtc / debtnc and cancel against liabilitiesc / liabilitiesnc (both routes), leaving a one-off positive jump in
  NOA for lessees across the adoption year (2019-2020 signals). Caveat only; ranks largely absorb it.

## 5. Filters
predictor.py applies none. SignalDoc `Filter = abs(prc)>5` is OSAP's portfolio-stage filter; do NOT add it in the
factor (harness universe: price >= $1). Recorded deviation.

## 6. Predicted sign (SignalDoc)
`Sign = +1.0` (SignalDoc authority): high GrLTNOA is the long side, score = +GrLTNOA. The prior on growth in
operating assets is usually negative, so this orientation is worth stating; a flipped sign would be a second
hypothesis (|t| >= 2.74). Cat.Signal Predictor; Cat.Economic `investment`; Cat.Form continuous; Cat.Data Accounting.

## 7. The mass-point question
A do-nothing firm (every balance item unchanged) has zero level change and zero working-capital change, so
GrLTNOA = dp / avg(at) > 0: a mass point only if dp is also exactly 0 (Sharadar dp exact zero on 1.3-2.3% of
filings, and those firms also need unchanged balance sheets), i.e. effectively nobody. Measured modal-value
share of the scored cross-section: 0.05-0.11% at all 7 probe months (n scored 934-2,086; every value distinct
to the last observation). No tie rule is needed; the standing level-0-at-both-ends rule does not bite
(a ratio over at > 0; NOA exactly 0 at both dates has no population). Ties: average rank (harness).

## 8. History needed (snapshot starts 1998-01, SF1 from 1997Q4)
- One year back: the earliest usable P is 1998Q4 (datekey ~1999-03); signal months 1999-01 and 1999-02 are
  partial by construction (scorable share 39.1% / 45.5%). First full month 1999-03. `lookback_months` ~ 32
  (latest filing <= 15 months old + 12 + 45-day tolerance + reporting lag); no `history_months` (no price window).

## 9. OSAP metadata
Acronym GrLTNOA; Acronym2 LTNOAgr; Fairfield, Whisenant and Yohn 2003 (AR), Table 5A and B; sample 1964-1993;
Predictability in OP 2_likely; Signal Rep Quality 1_good; Sign +1; Return 0.61 (61 bps LS); T-Stat blank; EW;
LS Quantile 0.1; Start Month 6; Portfolio Period 12; Filter abs(prc)>5. SignalDoc Notes: "Long port has t=3.2 by
itself, so it's a judgment call." Source `Signals/pyCode/Predictors/GrLTNOA.py` at
b4e911e69678a7424f318617a61d813f54183123. Output `GrLTNOA.csv [permno, yyyymm, GrLTNOA]`.

## 10. Proposed Sharadar mappings and deviations
1. One-to-one: receivables, inventory, payables, intangibles, ppnenet (vendor 0 when not reported; OSAP
   forward-fills and never zero-fills it), assets, depamor (ART TTM).
2. aco, lco -> Route B (recommended) or 0 (Route A); ao, lo, che approx as in section 1.
3. ART, report-period aligned, quarterly refresh; `fundamentals_yoy(years=1)`. Score = +GrLTNOA.
4. Guards: at > 0 at both dates; unclassified block NaN (never zero-filled); dp zero-fill only with revenue present.
5. Fields to verify on this snapshot (verified_on blank): assetsnc, investmentsnc, investmentsc, liabilitiesnc,
   debtnc, debtc, assetsc, liabilitiesc in their use here. No key missing from the field map.
