# Cash — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: APPROX (fully constructible; one term is an approximation)
Checked against `osap_source/field_map_index.yaml` (no field outside the map).

| OSAP var | field_map key | Sharadar | index status | role |
|---|---|---|---|---|
| cheq | compustat.cheq | SF1.cashneq + investmentsc.fillna(0) | approx (verified 2026-09-30 via `che`) | numerator, level |
| atq | compustat.atq | SF1.assets | mapped (`at` verified 2026-09-30) | denominator, level |
| rdq | compustat.rdq | SF1.datekey (filing date) | approx (verified 2026-09-30) | availability clock |

- Nothing is unavailable and OSAP zero-fills nothing that Sharadar lacks. The only
  OSAP zero-fill is `cheq` (upstream `zero_fill_vars`, see section 2), and that is
  a fill of a field Sharadar does have, so it is not a missing-item case.
- Why approx: `che` = cash AND short-term investments. `cashneq` alone is cash
  only (never use it alone; rank rho vs the sum 0.91-0.96, 37-51% of non-financials
  change decile). The sum overshoots for vendor-financing/captive-finance names
  (CSCO, F, GM, IBM, HPE, HOG: `investmentsc` holds current financing receivables)
  and understates for the unclassified block (investmentsc null ~20% of ART rows,
  86-92% financials/REITs; there che = cashneq, short-term securities sit in
  `investments` with loans and cannot be recovered). Both are declared deviations.
- Measured coverage of che on the universe (field_map verified_note): 98.8%
  (1998-12-31), 97.5% (1999), 99.8% (2008), 100.0% (2020, 2021); null only where
  cashneq is null (0.04% ART). assets null 0.05%, exact-zero 0.01% of non-null.
- Recommend: **approx** (feasible). No IBES, options, 13F, patents, segments,
  ratings, pensions, xad, emp, ob or ppegt input.

## 2. Variables by exact source name (predictor.py)
`m_QCompustat` columns `gvkey, rdq, cheq, atq`; `SignalMasterTable` columns
`permno, gvkey, time_avail_m`. Upstream (upstream_CompustatQuarterly.py, FUNDQ:
consol C, popsrc D, datafmt STD, curcdq USD, INDL):
- `cheq` is in `zero_fill_vars`: a missing Compustat cheq becomes 0, so OSAP
  Cash = 0 for a firm with atq present and cheq missing. `atq` is not filled.
- Dedupe to one row per (gvkey, fyearq, fqtr) keeping the latest datadate.
- `time_avail_m = datadate + 3 months`, moved LATER to the `rdq` month when that
  is later; rows with rdq more than 6 months after datadate are dropped.
- SignalMasterTable keeps only shrcd in {10,11,12} and exchcd in {1,2,3} with a
  gvkey link (harness universe replaces this).

## 3. Formula
Cash = cheq / atq (quarterly cash and short-term investments over total assets).

    qcompustat = qcompustat[gvkey.notna() & dup==1 & atq.notna()]   # one row per (gvkey, rdq)
    time_avail_m = month(rdq)                                      # rdq NaT -> row unusable
    expand to months rdq_m, rdq_m+1, rdq_m+2; keep the newest rdq per (gvkey, month)
    df = df.query("atq > 0"); df["Cash"] = df["cheq"] / df["atq"]

Sharadar form: `Cash = (cashneq + investmentsc.fillna(0)) / assets`, on rows
with `assets > 0`.

## 4. Timing / lag convention; what ART-as-of-filing changes
- OSAP: a quarter's value is usable from the month of its `rdq` (earnings
  announcement) and held for exactly 3 monthly rows, then disappears (NaN) until
  the next rdq. A firm whose next quarter is late, or has null rdq, has gaps.
- Sharadar: latest row with `datekey <= signal date`; `datekey` is the SEC
  filing date, usually later than rdq by days to weeks (median datekey minus
  reportperiod 44d), so the signal arrives slightly later than OSAP's. It does
  NOT expire after 3 months: a stale filer keeps its last ratio (translator: check
  whether MonthContext imposes a staleness limit; if not, state the deviation).
- Both inputs are balance-sheet LEVELS. ART == ARQ on the same reportperiod
  (cashneq 99.96%, investmentsc 99.98% within $1); keep the ART default. There is
  no flow item, so no TTM smear, and `dimension=ARQ` is not needed (harmless but
  unnecessary). fxusd cancels (ratio in reporting currency).
- No year-ago term: no lag_months, no history_months beyond the filing itself.

## 5. Filters
- predictor.py: `atq.notna()` and `atq > 0`; nothing else. SignalDoc `Filter` and
  `Quantile Filter` are blank (no price screen). Harness universe applies price
  >= $1, NYSE/NASDAQ/NYSEMKT common stock, cap/volume bands.
- Translator: gate `assets > 0`; leave the signal NaN when cashneq is null (do not
  zero-fill it to 0: OSAP's zero-fill of missing cheq applies to a Compustat
  gap, here only 0.04% of rows, and a fabricated 0 would be a bottom-decile
  outlier). Log as a deviation. No financials exclusion in OSAP.

## 6. Predicted sign (SignalDoc)
`Sign = +1.0`: high cash/assets predicts high returns. Score = +Cash (long high).
Published: Palazzo (2012, JFE), "Cash to assets", Cat.Economic = asset
composition, Cat.Form continuous, sample 1972-2009, EW, LS quantile 0.1,
portfolio period 1, Start Month 6.

## 7. The mass-point question
- Do-nothing firm: a firm that stays unchanged re-reports a near-identical ratio
  each quarter; there is no cross-sectional constant. Cash is continuous in (0, 1].
- Exact zeros: che exact-zero 1.06% / 0.88% / 0.34% / 0.24% / 0.17% of non-null
  at 1998-12 / 1999 / 2008 / 2020 / 2021 universe probes (zero-fill manufactures
  no mass point). Share at exactly 0 is about 0.2-1%, far below a decile (10%),
  so a decile is not collapsed; the zeros tie at the bottom rank. Ties: average
  (percentile) rank; no tie-break noise needed.
- Level of cash/assets is sector-dependent (high in technology/biotech, low in
  banks, utilities, real estate), so within-sector ranking changes the
  composition of the extremes versus OSAP's cross-sectional sort.

## 8. History needed
Level only. Snapshot starts 1998-01 (SF1 ART/ARQ/ARY broad from calendardate
1997Q4; levels ~99.9% populated, so the ART TTM-flow thinness of 1998Q1-Q3 does
not touch this predictor). Decisions from 1999-01 have a prior filing in hand;
che coverage 97.5-98.8% at the first months. `history_months` = 0 (no return
window).

## 9. OSAP metadata
- Acronym Cash; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep
  Quality 1_good; Authors Palazzo; Year 2012; Journal JFE; Cat.Data Accounting;
  Cat.Economic asset composition; SampleStartYear 1972, SampleEndYear 2009.
- Evidence: Table 4 long-short t = 2.14 raw EW (0.69 return), stronger after factor
  adjustments; Key Table 4, port sort. GScholarCites202509 = 500.
- Detailed Definition: ratio of quarterly cash and short-term investments (cheq)
  to total assets (atq). Source: `Signals/pyCode/Predictors/Cash.py`
  (confirmed in tree.txt line 532; not a Placebo).

## 10. Proposed Sharadar mappings and deviations
| item | mapping | deviation |
|---|---|---|
| cheq | `cashneq + investmentsc.fillna(0)` (SF1 ART) | approx: overshoot on financing-receivable filers; understates for the ~20% unclassified block (mostly financials/REITs); restricted cash inside cashneq for some filers |
| atq | `assets` (ART), require `> 0` | none material |
| rdq clock | latest `datekey <= signal date` | datekey later than rdq; no 3-month expiry |
| cheq zero-fill | NOT reproduced: null cashneq -> NaN | OSAP 0 for missing cheq; 0.04% of rows |
| universe | harness | OSAP keeps shrcd 10/11/12 and exchcd 1/2/3 all sizes; EW decile sort on raw cross-section; here within-sector ranks |
All fields are in `field_map_index.yaml`; the checker needs only the already-verified `che`, `at`, `datekey` entries.
