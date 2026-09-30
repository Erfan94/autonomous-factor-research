# DelCOA — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: APPROX (constructible; ~80% coverage; one OSAP artifact not reproduced)
Checked against `field_map_index.yaml` (detail in `field_map.yaml` for act, che, at).

| OSAP var | field_map key | Sharadar | status | note |
|---|---|---|---|---|
| `at` | compustat.at | SF1 `assets` | mapped, verified 2026-09-30 | null 0.05%; level |
| `act` | compustat.act | SF1 `assetsc` | mapped, verified-with-deviation 2026-09-30 | null 20.06% ART = unclassified balance sheets (71.5% Financial Services, 19.8% Real Estate) |
| `che` | compustat.che | SF1 `cashneq + investmentsc.fillna(0)` | approx, verified-with-deviation 2026-09-30 | investmentsc also holds financing/loan receivables for captive-finance filers (overstates che for CSCO/F/GM/IBM/HPE/HOG); financials/REITs understated |

- **OSAP zero-fills BOTH `act` and `che`** (`zero_fill_vars`, upstream_CompustatAnnual.py).
  So in OSAP a firm with no classified current assets (banks, insurers, REITs) gets
  act = 0 and DelCOA = -(che - che_lag)/avgAT: an artifact of the fill, not the signal.
  Not reproduced: `act` is available for ~80% of the universe; the ~20% null block is a structural gap
  (field_map: never zero-fill) that OSAP papers over with its zero-fill, so those names are MISSING here.
  No term is dropped; the verdict is approx because of the `che` scope deviation, the ART quarterly
  refresh and the ~19-20% coverage loss. Coverage: universe ART `assetsc` 80.1% (1998-12), 83.0%
  (1999-12), 81.5% (2008), 81.1% (2020), 80.9% (2021); year-ago level ~71% from 1999-03 (38%
  at 1998-12; SF1 starts 1998). Sector-months < 10 scored names fall back to the cross-section rank.
- Deviation: `che` mapping (above); ART uses the latest quarter's balance, not fiscal year-end.
- No IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob or ppegt input.

## 2. Variables (predictor.py)
`m_aCompustat`: gvkey, permno, time_avail_m, `at`, `act`, `che` (annual FUNDA; act/che zero-filled).

## 3. Formula
```
tempAvAT = 0.5 * (at + at.shift(12))                       # row-shift 12 on monthly panel
DelCOA   = ((act - che) - (act.shift(12) - che.shift(12))) / tempAvAT
```
Change in non-cash current assets, scaled by average total assets of the two years. OSAP drops duplicates
on (permno, time_avail_m) keeping `first`; no `at > 0` guard (negative/zero avg assets give odd signs:
guard `avgAT > 0` here).

## 4. Timing / lag
- OSAP: annual values, `time_avail_m = datadate + 6 months`, held 12 months; `shift(12)` on the monthly
  panel = previous fiscal year's annual row only when months are contiguous (row-based, a gap
  misaligns). Signal is 6-17 months stale, updates once a year.
- Sharadar: levels only (assetsc, cashneq, investmentsc, assets: ART == ARQ same-period, no TTM smear;
  `dimension` default ART, no ARQ needed). Year-ago via `ctx.fundamentals_yoy([...], years=1)` (report-period
  aligned, tol 45 days), NOT `lag_months=12` (known_trap yoy_by_report_period). ART-as-of-filing changes the signal:
  it refreshes every quarter and compares the latest quarter-end balance with the same quarter a year
  earlier (0-3 months old vs OSAP 6-17), so it is a rolling year-over-year change, not an annual-FYE change.
  No flow item in the formula.

## 5. Filters
predictor.py: none; SignalDoc Filter blank, Quantile Filter blank. No financials exclusion in OSAP (here
they are dropped by the null `assetsc`). Harness universe applies.

## 6. Predicted sign
`Sign = -1.0` (Richardson et al. 2005, Table 8C, univariate regression t = 8.71): high increase in non-cash
current operating assets predicts low returns; orient long low DelCOA, short high.

## 7. Mass-point question
Continuous ratio. A do-nothing firm (no change in act or che between years) gets exactly 0; such exact
zeros are rare for a ratio of differences of two USD levels (expected share well below 1%; not measured, preflight
confirms). Under OSAP's zero-fill, unclassified filers sit at -Delta-che/avgAT (continuous, no point mass). Null
(not zero) here for unclassified. Ties: harness average.

## 8. History needed
Latest filing plus the same-fiscal-period filing one year earlier: `fundamentals_yoy` covers it (4 quarters
back; `max_fundamental_age_months` 15). SF1 ART from 1997Q4; first decision month 1999-01 is ~38-48% covered
for the year-ago level (1998-12), ~71-89% from 1999-03 (field_map at/act). No `history_months`.

## 9. OSAP metadata
Richardson, Sloan, Soliman and Tuna (2005), JAE; Cat.Data Accounting; Cat.Economic investment alt;
continuous; sample 1962-2001; Acronym2 AssetCGr; Portfolio Period 12, Start Month 6; EW; Key Table 8C, univariate reg,
"FMB only"; `Predictability in OP` 1_clear, `Signal Rep Quality` 1_good. Source `Predictors/DelCOA.py`.

## 10. Proposed Sharadar mappings
`act` -> `assetsc` (null stays null; do NOT zero-fill); `che` -> `cashneq + investmentsc.fillna(0)`;
`at` -> `assets` (gate `fxusd == 1`, ~0% of universe); all three via `ctx.fundamentals_yoy(years=1)`;
`DelCOA = ((assetsc - che) - (assetsc_lag - che_lag)) / (0.5*(assets + assets_lag))`, `avgAT > 0`.
Deviations: che scope, ART quarterly refresh, ~19-20% structural NaN where OSAP zero-fills. No field not in the map.
