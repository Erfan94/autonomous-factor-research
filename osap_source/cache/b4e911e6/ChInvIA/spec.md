# ChInvIA — Change in capital investment, industry adjusted (Abarbanell and Bushee 1998, Table 2b RCAPX)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/ChInvIA.py` (cached
`predictor.py`, `legacy.do`, `signaldoc_row.csv`). DATA_SHA 198b281de1a0. field_map statuses are
mappings, not proofs, until the field-checker verifies them on this snapshot.

## 1. Data availability (verdict: APPROX — constructible; three declared deviations, no missing input)

| input (OSAP) | field_map key | Sharadar | field_map status | note |
|---|---|---|---|---|
| `capx` (m_aCompustat, annual) | `compustat.capx` | SF1 `capex`, use `-capex` | mapped, verified_on "" | cash OUTFLOW sign; ART is a TTM sum, ARY = fiscal year |
| `ppent` (only for the capx fallback) | `compustat.ppent` | SF1 `ppnenet` | mapped, verified_on "" | Sharadar ZERO-FILLS missing (5.9% exact zero); OSAP never zero-fills |
| `sicCRSP` -> `sic2D` (SignalMasterTable) | `crsp.siccd` | TICKERS.siccode (CURRENT) | approx | point-in-time CRSP siccd vs current Sharadar code; `compustat.sic` itself verified 2026-09-30 |

- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt. No OSAP zero-fill term:
  OSAP's only fallback is capx := ppent - ppent_l12 when capx is missing (not a zero-fill).
- Why approx: (a) siccode is the CURRENT classification, used inside the signal VALUE (industry
  mean), not just a filter; (b) the ppent fallback is unreliable (zero-filled ppnenet), dropped or
  gated; (c) OSAP's 6-month annual lag is not reproduced. `at` is loaded upstream but unused.
- Field-checker: verify `capex`, `ppnenet` in SF1 **ARY** (ART too if chosen), `TICKERS.siccode` in
  market scope. Fields not in the map: none.
- Measured (raw SF1, unfiltered, not a verification): ARY `capex` null by datekey year 1998/2000/2010/
  2020 = 0.5%/0.1%/0.7%/1.7%, exact zero 2.5%/2.2%/3.8%/7.9%, positive 2.9%/3.4%/3.7%/3.5%.
## 2. Variables (exact source names)

`capx`, `ppent` (Compustat annual, $ millions, replicated 12 months from datadate+6m), `sicCRSP` ->
`sic2D` = first two characters of str(sicCRSP), `time_avail_m`, `permno`.
## 3. Formula

Per firm-month; `l12`/`l24` = the same row 12/24 calendar months earlier:
```
capx    = capx.fillna(ppent - l12.ppent)            # fill is applied BEFORE the lags, so l12/l24 capx are filled values
avg     = 0.5*(l12.capx + l24.capx)
pchcapx = (capx - avg)/avg            if avg != 0 else NaN
pchcapx = (capx - l12.capx)/l12.capx  where pchcapx is NaN (l12.capx != 0 else NaN)
temp    = mean(pchcapx) by (sic2D, time_avail_m)   # all stocks with a Compustat annual row and an SMT row
ChInvIA = pchcapx - temp
```
Growth of capex over the mean of the prior two years (prior year only when t-2 is missing), minus the
same-SIC2 average that month.
Proposed Sharadar construction (dimension is the sanctioned per-factor deviation):
- `dimension="ARY"` (recommended): OSAP's capx is annual and l12/l24 are the two prior fiscal years.
  `ctx.fundamentals_yoy(["capex"], years=1, dimension="ARY")` and `years=2` give capx_l12, capx_l24 by
  REPORT PERIOD (`yoy_by_report_period`); gate each on `reportperiod_lag.notna()`. ARY nulls 0.1-1.7%
  (ART 4-9%, 46% in 1998). ART alternative: TTM windows t, t-4q, t-8q, updates quarterly, noisier.
- capx = -capex. Denominators: require `avg > 0` (resp. `l12 > 0` in the fallback), per field_map
  ("require base > 0"); this nulls the `avg == 0` case OSAP nulls AND negative bases (Sharadar
  positive capex, 2.7% of computable rows), which OSAP would keep. Declared deviation, small.
- ppent fallback: binds on <~1% of rows under ARY. Recommended: DROP it (null capx -> NaN), since
  ppnenet == 0 is indistinguishable from missing and would make spurious "capx". Alternative: fill
  only where ppnenet > 0 at both ends, for each of t, t-12, t-24 (needs `yoy(years=1,2,3)`).
- Industry mean: OSAP averages over the whole CRSP x Compustat cross-section, not the screened
  universe. Compute pchcapx on `ctx.market_context()`, then `harness.industry.group_demean(pchcapx,
  sic_group(mctx.ticker_meta(["siccode"])["siccode"], 2))`, reindex to `ctx.ids`. The helper exists
  (harness/industry.py, floor `MIN_GROUP_FOR_DEMEAN = 5`); no new one needed. Deviations: OSAP has no
  floor (a one-firm SIC2 gets 0; here NaN) and groups missing-SIC names as "na" (here NaN).
- No winsorising upstream; keep raw. pchcapx is unbounded (tiny `avg` gives huge ratios), so the SIC2
  mean is outlier-driven: ranks within one SIC2 are unaffected (constant shift), comparison ACROSS
  SIC2 groups inside a sector is. OSAP's behaviour; reproduce, do not clip.
- 3-digit SIC (68 of 20,829 codes): OSAP str(700)[:2] = "70"; `sic_group` gives 7. Immaterial.

## 4. Timing / lag

- OSAP: annual capx known at datadate + 6 months, replicated 12 months, latest datadate wins; l12/l24
  are calendar-month lags of that replicated series. The signal is 6-17 months stale, year-end only.
- Here (ARY): latest 10-K with `datekey <= signal_asof` (max age 15 months); the new year enters ~3
  months after fiscal year-end, not 6, so 2-4 months fresher; updates once a year per firm (ART: each
  filing, TTM). Rank correlation with OSAP expected high, not exact; say so in the docstring.
- Industry mean at t uses the market cross-section at t only. Flow item: under ART the lags are 4
  and 8 quarters (non-overlapping TTM windows), nothing smears; ARQ is not wanted.

## 5. Filters

None in OSAP (SignalDoc Filter blank); harness universe applies. Financials not excluded upstream
(capex often 0/NaN, so they mostly drop via `avg == 0`). Missing SIC -> NaN here (0.65% of tickers).

## 6. Predicted sign

SignalDoc `Sign = -1.0`: high industry-adjusted capex growth predicts LOW returns -> `ascending=False`
(low value = long side). Cat.Economic: investment growth.

## 7. The mass-point question

- Do-nothing firm (capex identical in t, t-12, t-24): pchcapx = 0, ChInvIA = -(SIC2 mean); literally
  identical capex is 0.03% of computable ARY firm-years. Not a mass point.
- Real mass point: capex falling to exactly 0 from a positive base gives pchcapx = -1 exactly, then
  `-1 - SIC2 mean` (identical within a SIC2-month): about 1.0% of computable observations (2000-2021
  report years, unfiltered). Zero capex in t is 4.9% of rows; with a zero base it is dropped (NaN).
- Null/inadmissible (ARY, unfiltered): `avg == 0` 2.6%, `avg < 0` 2.7% (nulled here); computable ~82%.
- Tie handling: the harness averages ranks over ties; none needed in the factor. The -1 cluster is
  the LOWEST raw value, i.e. the long extreme under Sign -1; preflight should report the modal share.

## 8. History needed

Annual capx at t, t-12m, t-24m (t-36m only with the ppent fill). SF1 starts 1997Q4: the two-lag form
exists from ~2000 (FY1999 10-K has FY1997, FY1998); 1999 comes from the l12-only fallback (as OSAP
when t-2 is missing); Jan-Feb 1999 is thin (Dec-FY filers have FY1997 only). ART is thinner through
1999-2000 (1998 TTM flows ~50% populated). `history_months` = 24 (36 with the fill).

## 9. OSAP metadata

Predictor | 1_clear | 1_good | Abarbanell and Bushee 1998, AR | continuous | Accounting | investment growth |
sample 1974-1988 | Acronym2 InvestGr | Sign -1 | EW | Portfolio period 12 | Start month 6 | Filter none |
Table 2b RCAPX, reg | cites 1123. Inputs: m_aCompustat (capx, ppent, at), SignalMasterTable (sicCRSP).

## 10. Proposed Sharadar mappings and deviations

| OSAP | Sharadar | deviation |
|---|---|---|
| capx | `-capex`, dimension ARY (ART alt.) | sign flip; bases <= 0 nulled; filing-date lag not datadate+6m |
| ppent fill | `ppnenet` (drop, or gate on > 0) | zero-filled vendor field; fallback mostly dormant |
| l12, l24 | `ctx.fundamentals_yoy(years=1)`, `(years=2)` | report-period alignment, not calendar-month lag |
| sicCRSP[:2] | `TICKERS.siccode` via `ctx.market_context().ticker_meta`, `sic_group(.., 2)` | CURRENT, not point-in-time, SIC; 2-digit |
| industry mean | `harness.industry.group_demean` over `market_context()` | floor of 5 per SIC2-month (OSAP none); missing-SIC group NaN |

`FactorDef`: `inputs` declare `SF1.capex`, (`SF1.ppnenet`), `TICKERS.siccode`; `dimension="ARY"`;
`history_months=24`; `family=None`; `ascending=False`. Predicted availability verdict: **approx**.
