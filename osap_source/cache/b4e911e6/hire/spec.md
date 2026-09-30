# hire — Employment growth (Bazdresch, Belo and Lin 2014, JPE, Table 1A, "LaborGr")

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/hire.py` (cached `predictor.py`,
`upstream_CompustatAnnual.py`, `signaldoc_row.csv`). DATA_SHA 198b281de1a0.

## 1. Data availability — VERDICT: data_unavailable (recommend infeasible; do not translate)

| input | field_map key | Sharadar | status |
|---|---|---|---|
| `emp` (Compustat annual, employees, thousands) | `compustat.emp` | none | **unavailable** |

- `emp` has no SF1 field. Checked on THIS snapshot (parquet schemas): SF1 (112 cols), TICKERS (28), SF2
  (insiders, 23), SF3/SF3A/SF3B (13F), SEP, DAILY, METRICS, EVENTS, ACTIONS, SP500, DESCRIPTIONS carry no
  employee / headcount / staff column (regex over column names; DESCRIPTIONS text hits only `sbcomp`, share
  based compensation, which is not a headcount). `field_map_index.yaml`: `compustat.emp` status unavailable.
- Missing-item rule: OSAP DOES zero-fill the OUTPUT when emp is missing:
  `hire.loc[emp.isna() | l12_emp.isna()] = 0`, and `emp` is NOT in upstream `zero_fill_vars` (the list is
  nopi dvt ob dm dc aco ap intan ao lco lo rect invt drc spi gdwl che dp act lct tstkp dvpa scstkc sstk mib
  ivao prstkc prstkcc txditc ivst). Read literally that makes the nominal verdict approx. But here `emp` is
  missing for 100% of firms, not for the thin subset OSAP zero-fills, so every firm-month gets hire = 0.
  The result is a constant, not an approximation of the predictor (see 7). Recommended verdict:
  **data_unavailable**; if the coordinator applies the rule mechanically (approx) it must fail preflight
  (mass point 100% > 10% cliff, qcut bins 0-1, coverage 100% of no information) and land as
  preflight_failed. Either way it is not screened. No proxy (SIC-industry employment, revenue per share,
  asset growth) may stand in: a near-match is a different hypothesis.

## 2. Variables (exact source names)
`emp`, `permno`, `time_avail_m` (from m_aCompustat, annual, replicated 12 months from datadate+6m).

## 3. Formula
```
l12_emp = emp at time_avail_m - 12 months  (calendar merge on permno)
hire    = (emp - l12_emp) / (0.5 * (emp + l12_emp))
hire    = 0 where emp or l12_emp is NaN ; NaN where year < 1965
```
In words: employee growth over the last year, scaled by the two-year average headcount (a symmetric,
bounded [-2, 2] growth rate).

## 4. Timing / lag
OSAP: annual emp known at datadate+6 months, replicated 12 months; the lag is 12 calendar months, so within
the replicated series hire is 0 for the first months after each new year only when consecutive years
are equal, and the series changes once a year. Not applicable here: no source field.
Flow vs stock: emp is a year-end stock, not a flow; no ART/ARQ smear issue would arise.

## 5. Filters
None in OSAP (SignalDoc Filter blank). Harness universe would apply.

## 6. Predicted sign
SignalDoc Sign = -1.0: high employment growth predicts LOW returns -> `ascending=False`.
Cat.Economic: investment alt. Predictability in OP: 1_clear.

## 7. The mass-point question
A firm with no employee data, or with unchanged headcount, gets hire = 0. With no `emp` source every firm
gets 0: the do-nothing share is 100% of the universe by construction (universe 1,739-2,867 names over all
276 months of the schedule, mean 1,965; measured size, not the signal). qcut would yield 1 bin. Even with
a real emp column, OSAP's zero-fill of missing emp is a known mass point (emp is missing on a large share of
Compustat firm-years); here it is total. No tie-handling rule repairs a constant.

## 8. History needed
Not reached. (emp would need one prior year; SF1 ARY starts FY1997.)

## 9. OSAP metadata
Predictor | 1_clear | 1_good | Bazdresch, Belo and Lin 2014 JPE | continuous | Other | investment alt |
sample 1965-2010 | Acronym2 LaborGr | Sign -1 | EW | LS quantile 0.2 | Portfolio period 12 | Start month 6 |
Filter none | Return 0.87, t 5.78 (port sort, Table 1A) | cites 489.

## 10. Proposed Sharadar mappings and deviations
None possible. `compustat.emp` -> no Sharadar field (mapping table says so). No field is missing from
the map (emp is listed, unavailable). Recommendation for `osap_frontier.yaml`: reason
"emp (employees) not published by Sharadar SF1 or any held table; OSAP zero-fills hire to 0 when emp is
missing, so a no-emp build is the constant 0 (100% mass point)". Verdict: **data_unavailable**.
