# GrSaleToGrInv — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: FEASIBLE (coverage-flagged: ~58% of names by construction)
Checked against `osap_source/field_map_index.yaml`.

| OSAP var | Sharadar | status (verified_on) | role |
|---|---|---|---|
| sale | revenue | mapped (2026-09-30) | FLOW (ART TTM), 3 dates |
| invt | inventory | mapped (2026-09-30) | level, 3 dates |

- No unavailable input; no IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob or ppegt.
- **Inventory zero-fill is not a deviation.** OSAP zero-fills invt (`zero_fill_vars`), Sharadar stores 0 for
  non-reporters (exact zero 46.3% of ART rows). OSAP's own rule `avg base == 0 -> NaN` (then `l12 == 0 -> NaN`
  in the fallback) already drops zero-inventory firms, so the exclusion is identical. Sale is NOT zero-filled
  (null stays NaN). This is a coverage ceiling, not an approximation.
- Measured over 275 signal months (1999-01 .. 2021-11, harness universe, ART, fundamentals_yoy years=1 and 2):
  coverage mean 57.8%, median 59.6%, min 25.1%; **12 months below 40%**: 1999-01, 1999-02 and 1999-05 .. 2000-02.
  Cause: a data-start artefact (ART flow revenue for 1998Q1-Q3 is ~50% populated; universe revenue coverage
  57.7% at 1999-01, 92.5% from 1999-03), so those months run largely on the 12-month fallback (fallback-only
  share of scored names 12.1% 1999-01, 23.1% 1999-03, 11.3% 1999-06, 10.1% 2000-03, 22.8% 2000-06, 2.0% 2003-12,
  3.2% 2008-12, 2.1% 2015-06, 1.8% 2021-11) and revenue-at-P-2y is often unavailable; last-240-month mean coverage 59.4%.
  Structural ceiling: inventory exactly 0 at t on 35-45% of the universe and avg(l12, l24) == 0 on 13-37% (rising).
  Probe months first/middle/last: 1999-01 reads 25.1% (coverage warning, not a hard fail), 2003-12 61.2%,
  2021-11 49.5%.

## 2. Variables by exact source name
`m_aCompustat`: gvkey, permno, time_avail_m, sale, invt. Upstream (`CompustatAnnual.py`): rows with null at, prcc_c
or ni dropped; invt zero-filled, sale not. `time_avail_m = datadate + 6 months`; `l12_` / `l24_` are
`groupby(permno).shift(12 / 24)` of the monthly panel = the prior two fiscal-year records.

## 3. Formula
Abarbanell and Bushee (1998) RINV: percentage sales growth minus percentage inventory growth, growth measured
against the average of the two prior years.

    base_s = 0.5*(sale_l12 + sale_l24);   base_i = 0.5*(invt_l12 + invt_l24)
    primary  = (sale - base_s)/base_s - (invt - base_i)/base_i        (each term NaN if its base == 0)
    fallback = (sale - sale_l12)/sale_l12 - (invt - invt_l12)/invt_l12   (each term NaN if l12 == 0)
    GrSaleToGrInv = primary, else fallback where primary is NaN

Pandas arithmetic: primary is NaN if ANY of l12 or l24 is missing (for either variable) or a base is 0, so the
fallback fires when l24 is missing, and ALSO whenever one of the two primary terms is undefined. Growth of -100%
(invt_t = 0 with invt_l12 > 0) is a legitimate value. Translator: report the fallback share per probe month.

## 4. Timing / lag convention
- OSAP: fiscal-year records, available datadate + 6 months, refreshed annually. Sharadar ART at datekey
  refreshes quarterly; use report-period alignment with `ctx.fundamentals_yoy(fields, years=1)` and
  `fundamentals_yoy(fields, years=2)` (latest, P-1y, P-2y; never `lag_months`).
- **Flow item (revenue): no TTM smear.** Sales at P, P-1y and P-2y are ART TTM windows exactly four quarters apart
  and non-overlapping, so each growth term is a clean annual change. Do NOT set `dimension=ARQ` (a single quarter
  against annual-scale bases understates growth ~4x). Inventory is a balance-sheet level.

## 5. Filters
predictor.py applies none; SignalDoc `Filter` is blank. Nothing to add (harness universe: price >= $1).

## 6. Predicted sign (SignalDoc)
`Sign = +1.0`: high (sales growth minus inventory growth) is the long side, score = +GrSaleToGrInv.
Cat.Signal Predictor; Cat.Economic `sales growth`; Cat.Form continuous; Cat.Data Accounting.

## 7. The mass-point question
A do-nothing firm (sales and inventory unchanged at all three dates) gives exactly 0 (both growth terms 0):
essentially no operating firm, and such a firm must also have a nonzero inventory base. The zero-inventory
population is not a mass point at 0: it is NaN through the base-zero guards. Zero sales over a positive base
is -1 growth, a legitimate value varying with the inventory term. Measured modal-value share of the scored
cross-section at 9 probe months: 0.07-0.17% (n scored 598-1,499, distinct values ~= n). The standing tie rule
(level exactly 0 at both ends -> NaN) holds by construction: invt == 0 at both ends makes the base zero (NaN)
in both the primary and the fallback path. Ties: average rank (harness).

## 8. History needed (snapshot starts 1998-01, SF1 from 1997Q4)
- Primary needs P-2y; the earliest held period is 1997Q4 (its ART revenue is only partly populated), so the
  primary formula first exists for P = 1999Q4 (datekey ~2000-03; primary-path share of the universe 13.0% at
  1999-01, 24.8% 1999-03, 42.2% 2000-03, 59.2% 2003-12); earlier the fallback (P-1y, earliest P 1998Q4,
  datekey ~1999-03) carries the score. Signal months 1999-01 and 1999-02 are largely empty (25.1% at 1999-01). `lookback_months`
  ~ 44 (latest filing <= 15 months old + 24 + 45-day tolerance + reporting lag); no `history_months`.

## 9. OSAP metadata
Acronym GrSaleToGrInv; Acronym2 RevG2InvG; Abarbanell and Bushee 1998 (AR), Table 2b RINV; sample 1974-1988;
Predictability in OP 2_likely; Signal Rep Quality 1_good; Sign +1; Return blank; T-Stat 2.372; EW; LS Quantile
blank; Start Month 6; Portfolio Period 12; Filter blank. Source
`Signals/pyCode/Predictors/GrSaleToGrInv.py` at b4e911e69678a7424f318617a61d813f54183123. Output
`GrSaleToGrInv.csv [permno, yyyymm, GrSaleToGrInv]` (via save_predictor). Upstream cached: CompustatAnnual.

## 10. Proposed Sharadar mappings and deviations
1. sale -> revenue (ART TTM, never zero-filled, null = NaN); invt -> inventory (ART level, vendor 0 kept).
2. `fundamentals_yoy(years=1)` and `(years=2)`; compute primary, fall back to the 12-month form where primary is NaN.
3. Growth terms NaN where their base is exactly 0 (not inf); no other guards needed. Score = +value.
4. Deviations: ART quarterly refresh vs annual fiscal year; fallback prevalence in 1999-2000 is a data-start
   effect; no `ppegt`-style unavailable input. Coverage ceiling ~55-62% from 2003 is the OSAP zero-inventory rule.
5. Fields not in field_map: none.
