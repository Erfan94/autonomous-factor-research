# DelDRC — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: APPROX (constructible; coverage after OSAP's own filters is thin, ~20-27%)
Checked against `field_map_index.yaml` (detail in `field_map.yaml` for drc, sic, sale).

| OSAP var | field_map key | Sharadar | status | note |
|---|---|---|---|---|
| `drc` | compustat.drc | SF1 `deferredrev` | approx, verified-with-deviation 2026-09-30 | TOTAL deferred revenue (drc + drlt), not the current line |
| `at` | compustat.at | SF1 `assets` | mapped, verified 2026-09-30 | null 0.05% |
| `ceq` | compustat.ceq | SF1 `equity` | approx, verified 2026-09-30 | parent equity incl. preferred; filter only tests sign, immaterial |
| `sale` | compustat.sale | SF1 `revenue` | mapped, verified 2026-09-30 | raw USD (Compustat sale is $ millions): threshold `< 5` becomes `< 5e6` |
| `sic` | compustat.sic | TICKERS.siccode | mapped, verified-with-deviation | CURRENT classification, not point-in-time; universe null 0.00% |

- **OSAP zero-fills `drc`** (`zero_fill_vars`), and Sharadar itself zero-fills deferredrev (67% exact-zero of non-null,
  "value of 0 is used"), so null -> 0 (0.03%) matches OSAP. Deviation: deferredrev = drc + drlt; OSAP `drc` is the
  current portion only. Firms with only long-term deferred revenue enter here but are zero in OSAP (approx).
- **Coverage warning.** The filter `(drc == 0) & (DelDRC == 0) -> NaN` removes every name with zero deferred revenue at
  both ends (63-72% of names, field_map: 62-68% exact-zero 12-month change), then ceq <= 0, revenue < $5m and SIC
  6000-6999 (15-20% of universe). Measured on raw SF1 ART, domestic common, Dec-FYE rows with prior-year Dec row (not the
  harness universe): surviving non-null share 19.5% (1999), 26.5% (2008), 24.8% (2015), 20.9% (2020). The Stage 1
  coverage floor is 40%; expect preflight to report a coverage shortfall and the verdict is then inconclusive/preflight
  failure, not a spec problem. Do not weaken the filters to raise coverage.
- No IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob or ppegt input.

## 2. Variables (predictor.py)
`m_aCompustat`: gvkey, permno, time_avail_m, `drc`, `at`, `ceq`, `sale`, `sic`.

## 3. Formula
```
DelDRC = (drc - drc.shift(12)) / (0.5 * (at + at.shift(12)))        # groupby(permno), row-based
DelDRC = NaN where  ceq <= 0  |  (drc == 0 & DelDRC == 0)  |  sale < 5  |  (6000 <= sic < 7000)
```
Annual change in deferred revenue over two-year average assets. Filter conditions use NaN-false semantics: a missing
`ceq` or `sale` does NOT trigger the exclusion (pandas comparison with NaN is False). No `at > 0` guard; here `avgAT > 0`.
Note `(drc == 0) & (DelDRC == 0)` tests the CURRENT drc and a zero change, i.e. zero at both ends.

## 4. Timing / lag
- OSAP: annual, `time_avail_m = datadate + 6 months`, held 12 months; `shift(12)` row-based. Portfolio Period 1 in
  SignalDoc, but the signal only changes annually.
- Sharadar: drc, at, ceq levels (ART == ARQ: deferredrev 99.71%); no TTM smear. `revenue` is a FLOW: ART = TTM, used
  only as a level threshold (`< 5e6`), so the TTM smear matters only where ART revenue is ~50% populated in 1998Q1-Q3;
  a null revenue is not excluded (NaN-false), matching OSAP. Year-ago via `ctx.fundamentals_yoy(years=1)`. ART-as-of-filing:
  rolling y/y (latest quarter vs same quarter a year earlier), 0-3 months old vs OSAP 6-17. Deferred revenue is seasonal
  (Q4-heavy for subscription/education filers) but the same-quarter comparison cancels it.

## 5. Filters
Inside predictor.py (quoted above): negative/zero book equity, zero deferred revenue at both ends, revenue < $5m (here
5e6 USD), SIC 6000-6999 (here current TICKERS.siccode; ~15-20% of the universe, 14.9-20.5%). Harness universe also applies.

## 6. Predicted sign
`Sign = +1.0` (Prakash and Sinha 2013, CAR, Table 7, t = 3.59, sample 2002-2007, 5 years): long HIGH DelDRC, short low.
Different orientation from the other Del* predictors in this batch.

## 7. Mass-point question
After the filter the exact-0 mass point is removed by design: before it, 63-72% of names have a zero 12-month change
(zero at both ends); after it, exact-zero DelDRC among survivors is 0.2-0.7% (1999 0.72%, 2008 0.38%, 2015 0.18%,
2020 0.28%; drc > 0 with unchanged value). A do-nothing firm with drc == 0 is NaN, not 0. Ties: harness average.

## 8. History needed
Latest filing plus the same-period filing one year earlier (`fundamentals_yoy`, `max_fundamental_age_months` 15).
SF1 ART from 1997Q4; year-ago coverage ~38-48% at 1998-12, ~71-89% from 1999-03. No `history_months`.

## 9. OSAP metadata
Prakash and Sinha (2013), CAR; Cat.Data Accounting; Cat.Economic investment alt; continuous; sample 2002-2007;
Acronym2 DeferRev; Portfolio Period 1, Start Month 6; EW; Key Table "7 Delta DRC", univariate reg;
`Predictability in OP` 2_likely, `Signal Rep Quality` 1_good. SignalDoc Filter blank; filter is in the detailed
definition and code. Source `Predictors/DelDRC.py`.

## 10. Proposed Sharadar mappings
`drc` -> `deferredrev` (null -> 0, keep zeros, use once); `at` -> `assets`; `ceq` -> `equity`; `sale` -> `revenue`
(USD; threshold 5e6); `sic` -> TICKERS.siccode (integer compare); `assets`/`equity`/`revenue` gate `fxusd == 1`.
`DelDRC = (deferredrev - deferredrev_lag) / (0.5*(assets + assets_lag))`, masked by the four exclusions.
Deviations: total vs current deferred revenue, current (not PIT) SIC, ART quarterly refresh, preferred inside equity
(immaterial). Field not in the map: none (check the harness exposes siccode to MonthContext).
