# DelFINL — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: APPROX (constructible; preferred-stock term dropped; lease-inclusive debt)
Checked against `field_map_index.yaml` (detail in `field_map.yaml` for dltt, dlc, dltt_plus_dlc, pstk).

| OSAP var | field_map key | Sharadar | status | note |
|---|---|---|---|---|
| `dltt + dlc` | compustat.dltt_plus_dlc | SF1 `debt` | mapped, verified-with-deviation 2026-09-30 | null 0.03%, populated for the unclassified block; includes operating leases from FY2019 (ASC 842) |
| `pstk` | compustat.pstk | none | unavailable | no SF1 field; OSAP itself fills it with 0 (`tempPSTK = pstk.fillna(0)`) |
| `at` | compustat.at | SF1 `assets` | mapped, verified 2026-09-30 | null 0.05% |

- **`pstk` is missing; OSAP's own predictor fills it with 0** when absent, so per the rule the preferred term is DROPPED
  and the row is approx. Dropping does not leave the signal constant (debt change remains). Where Compustat has
  preferred stock (a minority of firms) its y/y change is lost here; preferred sits inside SF1 `equity`, not separable.
- `dltt`, `dlc` are NOT zero-filled by OSAP (not in `zero_fill_vars`): a missing dltt or dlc is NaN. Use `debt`
  (field_map: NOT `debtc.fillna(0) + debtnc.fillna(0)`, which would fabricate artifacts on the ~20% unclassified
  balance sheets; `debt` has 0.03% null there). Deviation: Sharadar `debt` for banks/insurers includes repo and
  short-term borrowings, so financials are in (98-100% universe coverage) where OSAP's dltt/dlc may be sparse.
- **ASC 842 break**: `debt` includes capital AND operating lease obligations; Compustat dltt/dlc excludes operating
  leases. The 12-month change carries a lessee-wide positive step in FY2019-2020 filings (field_map: YoY debt/lagged assets
  p75 0.045 (2018) -> 0.115 (2019) -> 0.070 (2020), p50 0.000 -> 0.031 -> 0.012). A cross-sectional rank in those months is
  dominated by lessee status, an approx deviation, not reproduced away.
- Coverage: universe ART `debt` 98.8% (1998-12), 97.5% (1999-12), 99.8% (2008), 100% (2020/2021); raw-SF1 non-null
  DelFINL 89.7% (1999), 97.4% (2008), 94.8% (2015), 83.1% (2020, year-ago pair).
- No IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob or ppegt input.

## 2. Variables (predictor.py)
`m_aCompustat`: gvkey, permno, time_avail_m, `at`, `pstk`, `dltt`, `dlc`.

## 3. Formula
```
tempPSTK = pstk.fillna(0);   merge 12-month-lag (time_lag12 = time_avail_m - 12 months) of at, dltt, dlc, tempPSTK
tempAvAT = 0.5 * (at + l12_at)
DelFINL  = ((dltt + dlc + tempPSTK) - (l12_dltt + l12_dlc + l12_tempPSTK)) / tempAvAT;   dropna(DelFINL)
```
Change in financial liabilities (long-term debt + current debt + preferred) over two-year average assets. Lag is a
calendar-date merge (a gap gives NaN). No `at > 0` guard; here `avgAT > 0`. Here: `(debt - debt_lag) / avgAT`.

## 4. Timing / lag
- OSAP: annual, `time_avail_m = datadate + 6 months`, held 12 months; signal 6-17 months stale, changes annually.
- Sharadar: `debt` and `assets` are levels (debt ART == ARQ 99.46% same-period); no flow item, no TTM smear, no
  `dimension=ARQ`. Year-ago via `ctx.fundamentals_yoy(years=1)`. ART-as-of-filing: refreshes quarterly, latest
  quarter-end debt vs same quarter a year earlier (0-3 months old vs OSAP 6-17); revolver and commercial paper
  draw-downs at quarter ends are in the signal as they are in the balance sheet.

## 5. Filters
predictor.py: none; SignalDoc Filter and Quantile Filter blank. Harness universe applies (financials stay in).

## 6. Predicted sign
`Sign = -1.0` (Richardson et al. 2005, Table 8C, univariate regression, t = 8.01): orient long low DelFINL, short high.

## 7. Mass-point question
Continuous ratio with a real point mass at 0: a firm with no debt at either date (and, in OSAP, no preferred) gets
exactly 0. Measured exact-zero share of non-null DelFINL on raw SF1 ART (domestic common, Dec-FYE, year-ago
pair): 10.3% (1999), 15.7% (2008), 16.3% (2015), 4.6% (2020; ASC 842 leases push previously debt-free lessees off zero).
Falls from the level-side exact-zero share (`debt` 11-15% in 1998-2008, 4.2-4.4% 2020-21). Ties: harness average; a
~10-16% tie block sits mid-rank, and the first decile will be part zeros. Note that the dropped pstk term would remove some
OSAP zeros (firms with preferred but no debt would be non-zero there).

## 8. History needed
Latest filing plus same-fiscal-period filing one year earlier (`fundamentals_yoy`, `max_fundamental_age_months` 15).
SF1 ART from 1997Q4; year-ago coverage ~38-48% of universe at 1998-12, ~71-89% from 1999-03. No `history_months`.

## 9. OSAP metadata
Richardson, Sloan, Soliman and Tuna (2005), JAE; Cat.Data Accounting; Cat.Economic external financing; continuous;
sample 1962-2001; Acronym2 FinLiabGr; Portfolio Period 12, Start Month 6; EW; Key Table 8C, univariate reg, "FMB
only"; `Predictability in OP` 1_clear, `Signal Rep Quality` 1_good. Source `Predictors/DelFINL.py`.

## 10. Proposed Sharadar mappings
`dltt + dlc` -> `debt` (null stays null, no zero-fill); `pstk` -> dropped (OSAP fillna(0) term); `at` -> `assets`;
all via `ctx.fundamentals_yoy(years=1)`; gate `fxusd == 1`.
`DelFINL = (debt - debt_lag) / (0.5*(assets + assets_lag))`, `avgAT > 0`.
Deviations: pstk dropped, lease-inclusive debt from FY2019 (step in 2019-20), bank debt scope, ART quarterly refresh.
No field not in the map.
