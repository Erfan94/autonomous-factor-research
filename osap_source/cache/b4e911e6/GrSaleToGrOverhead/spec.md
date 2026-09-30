# GrSaleToGrOverhead — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: APPROX (xsga is approximate: R&D and D&A classification)
Checked against `osap_source/field_map_index.yaml`.

| OSAP var | Sharadar | status (verified_on) | role |
|---|---|---|---|
| sale | revenue | mapped (2026-09-30) | FLOW (ART TTM), 3 dates |
| xsga | sgna (+ rnd, see below) | approx (2026-09-30) | FLOW (ART TTM), 3 dates |

- No unavailable input; no IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob or ppegt.
- **xsga:** SF1.sgna is the AS-REPORTED SG&A line: it EXCLUDES R&D (sgna == rnd on 0.003% of rnd > 0 rows; MSFT,
  AAPL opex = sgna + rnd exactly) and INCLUDES D&A where the filer reports D&A inside SG&A. Compustat xsga
  INCLUDES xrd and excludes D&A (moved to dp); CBOperProf in this repo already uses xsga - xrd == sgna. Faithful
  proxy: **`sgna + rnd.fillna(0)`**, gated on sgna != 0. Alternative: bare `sgna`. Measured Spearman between the two
  final signals 0.943-0.963 at 9 probe months (0.943, 0.947, 0.954, 0.943, 0.944, 0.949, 0.946, 0.959, 0.963);
  coverage identical (rnd is never a gate). Embedded D&A is a level issue that largely cancels in a same-line
  growth rate (SG&A growth against its own past); the cross-filer presentation switch is the residual risk.
- **OSAP does NOT zero-fill xsga** (not in `zero_fill_vars`): sgna == 0 -> NaN (ruling vendor_zero_fills; exact
  zero 2.5% of non-null ART, 2.7-5.9% of the universe). rnd zero (63% of ART rows) is a true "no R&D".
- Measured over 275 signal months (1999-01 .. 2021-11, harness universe, ART, fundamentals_yoy years=1 and 2):
  coverage mean 86.3%, median 89.1%, min 32.6%; **2 months below 40%** (1999-01 32.6%, 1999-02); 1999-03 70.5%,
  2003-12 88.4%, 2008-12 89.7%, 2021-11 82.7%. Fallback-only share of scored names 17.6% 1999-01, 37.5% 1999-03,
  16.1% 2000-03, 3.5% 2003-12, 5.1% 2008-12, 4.2% 2021-11 (data start: 1998Q1-Q3 ART revenue ~50% populated and
  P-2y reaches 1997Q4). Nulls: revenue ART 7.8% pooled, sgna ART 7.8% pooled.

## 2. Variables by exact source name
`m_aCompustat`: gvkey, permno, time_avail_m, sale, xsga. Upstream (`CompustatAnnual.py`): rows with null at,
prcc_c or ni dropped; sale and xsga NOT zero-filled. `time_avail_m = datadate + 6 months`; `l12_` / `l24_` are
`groupby(permno).shift(12 / 24)` of the monthly panel = the prior two fiscal-year records.

## 3. Formula
Abarbanell and Bushee (1998) RS&A: sales growth minus overhead (SG&A) growth against the two-year average base.

    primary  = (sale - 0.5*(sale_l12 + sale_l24)) / (0.5*(sale_l12 + sale_l24))
             - (xsga - 0.5*(xsga_l12 + xsga_l24)) / (0.5*(xsga_l12 + xsga_l24))      (each term NaN if base == 0)
    fallback = (sale - sale_l12)/sale_l12 - (xsga - xsga_l12)/xsga_l12                (each NaN if l12 == 0)
    GrSaleToGrOverhead = primary, else fallback where primary is NaN

Primary is NaN if any of l12 or l24 is missing for either variable, or a base is 0 (then the fallback fires).
SignalDoc Detailed Definition says "GrSaleToGrOverHead", matching the file. Translator reports the fallback share.

## 4. Timing / lag convention
- OSAP: fiscal-year records available datadate + 6 months, refreshed annually; Sharadar ART at datekey
  refreshes quarterly. Use `ctx.fundamentals_yoy(fields, years=1)` and `(years=2)` (latest, P-1y, P-2y by report
  period; never `lag_months`).
- **Flow items (revenue, sgna, rnd): no TTM smear.** The three values are ART TTM windows exactly four quarters
  apart and non-overlapping, so every growth term is a clean annual change. Do NOT set `dimension=ARQ`.

## 5. Filters
predictor.py applies none; SignalDoc `Filter` is blank. Nothing to add.

## 6. Predicted sign (SignalDoc)
`Sign = +1.0`: high (sales growth minus overhead growth) is the long side, score = +value.
Cat.Signal Predictor; Cat.Economic `sales growth`; Cat.Form continuous; Cat.Data Accounting.

## 7. The mass-point question
A do-nothing firm (sales and SG&A unchanged at all three dates) gives exactly 0: essentially none. Zero SG&A is
NaN (sgna == 0 nulled before the ratio), so it forms no tie at 0. Measured modal-value share of the scored
cross-section at 9 probe months: 0.05-0.13% (n scored 777-2,165, distinct values ~= n). The standing tie rule
(level exactly 0 at both ends -> NaN) holds by construction (zero base -> NaN in both paths). Ties: average rank.

## 8. History needed (snapshot starts 1998-01, SF1 from 1997Q4)
- Primary needs P-2y; earliest held period 1997Q4 (partly populated ART flows), so primary exists from P =
  1999Q4; before that the fallback (needs P-1y >= 1997Q4, earliest P 1998Q4) carries the score. Signal months
  1999-01 and 1999-02 are below the 40% bar; 70.5% at 1999-03. `lookback_months` ~ 44 (latest filing <= 15 months
  + 24 + 45-day tolerance + reporting lag); no `history_months`.

## 9. OSAP metadata
Acronym GrSaleToGrOverhead; Acronym2 RevG2OHG; Abarbanell and Bushee 1998 (AR), Table 2b RS&A; sample 1974-1988;
Predictability in OP 2_likely; Signal Rep Quality 1_good; Sign +1; Return blank; T-Stat 2.069; EW; LS Quantile
blank; Start Month 6; Portfolio Period 12; Filter blank. SignalDoc Notes (OSAP's own, construction-relevant):
the 5th quintile was once removed and is now kept. Source `Signals/pyCode/Predictors/GrSaleToGrOverhead.py` at
b4e911e69678a7424f318617a61d813f54183123. Output `GrSaleToGrOverhead.csv [permno, yyyymm, GrSaleToGrOverhead]`.

## 10. Proposed Sharadar mappings and deviations
1. sale -> revenue (ART TTM, null = NaN); xsga -> `sgna + rnd.fillna(0)` where sgna != 0 (else NaN); alternative
   bare sgna (rho 0.94-0.96).
2. `fundamentals_yoy(years=1)` and `(years=2)`; primary, then fallback where primary is NaN; zero base -> NaN.
3. Deviations: sgna is as-reported (D&A inside for some filers); xsga includes R&D (rnd added back); ART quarterly
   refresh vs annual fiscal year; 1999-2000 months lean on the fallback (data start).
4. Fields not in field_map: none. Verify rnd (verified 2026-09-30) and sgna on the snapshot as used.
