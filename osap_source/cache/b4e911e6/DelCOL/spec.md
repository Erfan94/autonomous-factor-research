# DelCOL — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: APPROX (constructible; ~65-76% coverage; OSAP lct zero-fill not reproduced)
Checked against `field_map_index.yaml` (detail in `field_map.yaml` for lct, dlc).

| OSAP var | field_map key | Sharadar | status | note |
|---|---|---|---|---|
| `at` | compustat.at | SF1 `assets` | mapped, verified 2026-09-30 | null 0.05%; level |
| `lct` | compustat.lct | SF1 `liabilitiesc` | mapped, verified-with-deviation 2026-09-30 | null 20.2% ART = unclassified balance sheets (71% Financial Services, 20% Real Estate) |
| `dlc` | compustat.dlc | SF1 `debtc` | mapped, verified-with-deviation 2026-09-30 | null ~20% (same rows); exact-zero 27% of non-null (real mass point, but only inside a difference here) |

- **OSAP zero-fills `lct`** (`zero_fill_vars`, upstream_CompustatAnnual.py) but NOT `dlc`, `at`. So in OSAP an
  unclassified filer has lct = 0 and dlc = NaN, making the row NaN anyway unless Compustat reports dlc; a filer with
  dlc present but lct missing gets -dlc artifacts. Not reproduced: lct stays null where Sharadar has no classified
  current liabilities (per the unclassified-balance-sheet rule); those names are MISSING. Verdict approx, not feasible,
  because of this, the ~20% structural coverage loss and the ASC 842 point below.
- ASC 842 (unverified for this pair): Sharadar `debt` (= debtc + debtnc) includes operating-lease obligations from
  FY2019; Compustat dlc excludes them while Compustat lct includes the current operating-lease line. If `debtc` carries the
  current lease portion, `liabilitiesc - debtc` drops it, which differs from Compustat lct - dlc in FY2019-20 filings.
  Not measured on this field pair (field_map only measures debtnc and debt); the change term carries a one-off
  lessee step in 2019-2020 filings. Flag for the field-checker.
- Measured coverage (raw SF1 ART, domestic common, Dec-FYE rows with prior-year Dec row; not the harness universe):
  non-null DelCOL 69.7% (1999), 76.1% (2008), 72.9% (2015), 65.0% (2020). Harness-universe coverage is ~80% of
  ART level (field_map lct: 79.5% 1998-12, 82.3% 1999-12, 81.4% 2008, 81.2% 2020), lower for the year-ago pair.
- No IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob or ppegt input.

## 2. Variables (predictor.py)
`m_aCompustat`: gvkey, permno, time_avail_m, `at`, `lct`, `dlc` (annual FUNDA; `lct` zero-filled upstream).

## 3. Formula
```
tempAvAT = 0.5 * (at + lag_at)                      # groupby(permno).shift(12), row-based
DelCOL   = ((lct - dlc) - (lag_lct - lag_dlc)) / tempAvAT
```
Change in current operating liabilities (current liabilities net of short-term debt) over two-year average assets.
No `at > 0` guard in OSAP; here guard `avgAT > 0`. Dedup on (permno, time_avail_m) keep first (irrelevant here).

## 4. Timing / lag
- OSAP: annual values, `time_avail_m = datadate + 6 months`, held 12 months; `shift(12)` is row-based (a gap in the
  monthly panel misaligns the lag). Signal is 6-17 months stale, changes once a year.
- Sharadar: all three inputs are levels (ART == ARQ on the same reportperiod: liabilitiesc 99.93%, at ~99%), no TTM smear,
  default ART fine, no `dimension=ARQ`. Year-ago via `ctx.fundamentals_yoy([...], years=1)` (report-period aligned),
  not `fundamentals(lag_months=12)`. ART-as-of-filing: the signal refreshes every quarter and compares the latest
  quarter-end balance sheet with the same quarter a year earlier (0-3 months old, vs OSAP 6-17). A rolling y/y change,
  not an FYE change; quarter-end seasonality of current liabilities cancels in the same-quarter comparison.

## 5. Filters
predictor.py: none; SignalDoc Filter and Quantile Filter blank. No financials exclusion (they drop out via null
`liabilitiesc`). Harness universe applies.

## 6. Predicted sign
`Sign = -1.0` (Richardson et al. 2005, Table 8C, univariate regression, t = 4.49): orient long low DelCOL, short high.

## 7. Mass-point question
Continuous ratio of a difference of two USD level differences. Do-nothing firm (no change in lct or dlc) = exactly 0;
measured exact-zero share of non-null DelCOL 0.02-0.06% (1999/2008/2015/2020). No mass point. The dlc
27% exact-zero is a level-side point mass and cancels into a difference. Ties: harness average.

## 8. History needed
Latest filing plus the same-fiscal-period filing one year earlier (`fundamentals_yoy`, 4 quarters back;
`max_fundamental_age_months` 15). SF1 ART from 1997Q4, so the year-ago pair for decisions in early 1999 is thin
(~38-48% of universe year-ago level per field_map at/act); full by ~1999-03. No `history_months`.

## 9. OSAP metadata
Richardson, Sloan, Soliman and Tuna (2005), JAE; Cat.Data Accounting; Cat.Economic external financing;
continuous; sample 1962-2001; Acronym2 LiabCGr; Portfolio Period 12, Start Month 6; EW; Key Table 8C, univariate reg,
"FMB only"; `Predictability in OP` 1_clear, `Signal Rep Quality` 1_good. Source `Predictors/DelCOL.py`.

## 10. Proposed Sharadar mappings
`lct` -> `liabilitiesc` (null stays null, do NOT zero-fill); `dlc` -> `debtc` (null stays null); `at` -> `assets`
(gate `fxusd == 1`, ~0% of universe); all via `ctx.fundamentals_yoy(years=1)`;
`DelCOL = ((liabilitiesc - debtc) - (liabilitiesc_lag - debtc_lag)) / (0.5*(assets + assets_lag))`, `avgAT > 0`.
Deviations: lct zero-fill not reproduced (~20% NaN), ASC 842 treatment of debtc unverified, ART quarterly refresh.
No field not in the map.
