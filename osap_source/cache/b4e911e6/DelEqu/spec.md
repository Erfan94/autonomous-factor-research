# DelEqu — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: APPROX (constructible; ~97-99% coverage; preferred stock left inside equity)
Checked against `field_map_index.yaml` (detail in `field_map.yaml` for ceq, at).

| OSAP var | field_map key | Sharadar | status | note |
|---|---|---|---|---|
| `ceq` | compustat.ceq | SF1 `equity` | approx, verified-with-deviation 2026-09-30 | parent equity INCLUDING preferred (Compustat ceq excludes it); null 0.05% |
| `at` | compustat.at | SF1 `assets` | mapped, verified 2026-09-30 | null 0.05%; level |

- Neither input is in `zero_fill_vars` (upstream_CompustatAnnual.py) and predictor.py has no fillna: nothing dropped.
  The ceq -> equity preferred deviation is the book-equity preferred adjustment class (ruling
  `book_equity_preferred_terms`): approx, preferred not removed. Preferred changes (issues/redemptions) enter the
  signal here; in OSAP they do not. Coverage: universe ART `equity` 98.7% (1998-12), 97.6% (1999-12), 99.8% (2008),
  100% (2020/2021); raw-SF1 non-null DelEqu with year-ago 89.7% (1999), 97.4% (2008), 94.8% (2015), 83.1% (2020).
- No IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob or ppegt input.

## 2. Variables (predictor.py)
`m_aCompustat`: gvkey, permno, time_avail_m, `at`, `ceq`.

## 3. Formula
```
time_lag12 = time_avail_m - 12 months;   merge l12_at, l12_ceq on (permno, time_lag12)   # calendar-month merge
tempAvAT   = 0.5 * (at + l12_at)
DelEqu     = (ceq - l12_ceq) / tempAvAT;       dropna(DelEqu)
```
Change in book common equity over two-year average assets. Unlike DelCOA/DelCOL, the lag is a date merge (a missing month
gives NaN), not a row shift. Negative book equity is kept; no `at > 0` guard in OSAP, here guard `avgAT > 0`.

## 4. Timing / lag
- OSAP: annual values, `time_avail_m = datadate + 6 months`, held 12 months; signal 6-17 months stale, changes annually.
- Sharadar: levels only (equity ART == ARQ same-period 98.9%); no flow item, no TTM smear, no `dimension=ARQ`.
  Year-ago via `ctx.fundamentals_yoy([...], years=1)` (report-period aligned, tol 45 days). ART-as-of-filing: refreshes
  quarterly, latest quarter-end equity vs same quarter a year earlier (0-3 months old vs OSAP 6-17). The change contains
  retained earnings (net income less dividends), so it is correlated with ROE/ROA and with buybacks (negative) and
  issuance (positive); a rolling quarter-end version picks up current-year earnings earlier than OSAP's does.

## 5. Filters
predictor.py: none; SignalDoc Filter and Quantile Filter blank. Only `dropna(DelEqu)`. Harness universe applies.

## 6. Predicted sign
`Sign = -1.0` (Richardson et al. 2005, Table 9A, multivariate regression, t = 6.25): orient long low DelEqu, short high.

## 7. Mass-point question
Continuous ratio. A do-nothing firm (equity unchanged to the dollar over 12 months) gets exactly 0; measured exact-zero
share of non-null DelEqu 0.00-0.11% (1999/2008/2015/2020, raw SF1 ART). No mass point. Ties: harness average.

## 8. History needed
Latest filing plus same-fiscal-period filing one year earlier (`fundamentals_yoy`, `max_fundamental_age_months` 15).
SF1 ART from 1997Q4; year-ago coverage ~38-48% of universe at 1998-12, ~71-89% from 1999-03. No `history_months`.

## 9. OSAP metadata
Richardson, Sloan, Soliman and Tuna (2005), JAE; Cat.Data Accounting; Cat.Economic investment; continuous; sample
1963-2001; Acronym2 Eq2AGr; Portfolio Period 12, Start Month 6; EW; Key Table 9A, mv reg; `Predictability in OP`
1_clear, `Signal Rep Quality` 1_good. Source `Predictors/DelEqu.py`.

## 10. Proposed Sharadar mappings
`ceq` -> `equity`; `at` -> `assets`; both via `ctx.fundamentals_yoy(years=1)`; gate `fxusd == 1` (0.00-0.06% of
universe) since the ratio is unit-free but the ranking crosses currencies only through the gate.
`DelEqu = (equity - equity_lag) / (0.5*(assets + assets_lag))`, `avgAT > 0`.
Deviations: preferred inside equity, ART quarterly refresh. No field not in the map.
