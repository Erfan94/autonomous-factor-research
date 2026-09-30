# EarningsSurprise — standardized unexpected quarterly EPS (Foster, Olsen and Shevlin 1984, AR, Table 4 days +1 to +60)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/EarningsSurprise.py` (cached `predictor.py`, `upstream_CompustatQuarterly.py`, `upstream_SignalMasterTable.py`).
Written fresh from the source and `field_map_index.yaml`. Map statuses are mappings, not proofs; the numbers in 7/8 were measured on THIS snapshot (DATA_SHA 198b281de1a0) with a scratch replica, not the harness preflight.

## 1. Data availability — VERDICT: APPROX, feasible (no unavailable input)

| OSAP input | field_map key | Sharadar | map status | OSAP missing-item rule |
|---|---|---|---|---|
| `epspxq` (quarterly EPS excl. extraordinary items) | `compustat.epspxq` | SF1 `eps`, `dimension="ARQ"` | mapped (with deviation, see 10) | not zero-filled (NaN -> lag NaN -> signal NaN) |
| `gvkey/permno/time_avail_m` | SMT | harness universe | n/a | `dropna(gvkey)`, inner merge on m_QCompustat |

- No IBES / options / 13F / patents / segments / ratings / pensions / xad / emp / ob / ppegt. Nothing is zero-filled. (Only `epspxq` is read; OSAP's zero-fill list for quarterly data does not include it.)
- `eps` is in the map and verified: ARQ is a per-quarter LEVEL (AAPL rolling-4-quarter sum of ARQ eps == ART), null 4.5% ARQ, exact-zero 2.0% of non-null.
- TRAP: use `dimension="ARQ"` (FactorDef.dimension). Under the project default ART, `eps` is the trailing-4Q SUM and the year-over-year difference `eps - eps_{t-12m}` would smear (three quarters overlap) into a growth-of-TTM figure.
- Measured here: SF1 ARQ eps is on TODAY's split basis in every vintage row (AAPL 2019-03 ARQ eps 0.62 = the 2019 value after the 2020 4:1 split; NVDA 2020-01 0.039 after the 2021 4:1 and 2024 10:1 splits). All quarters of a name share one scale, and the signal is a ratio to its own SD, so the scale cancels exactly.

## 2. Variables (exact source names)
`epspxq` (m_QCompustat, quarterly, expanded to 3 monthly rows per quarter), `gvkey, permno, time_avail_m` (SignalMasterTable).

## 3. Formula in words and key lines
Year-over-year change in quarterly EPS, minus its own two-year average change (drift), divided by the standard deviation of the eight previous such unexpected changes.
```
GrTemp_t = epspxq_t - epspxq_{t-12m}
Drift_t  = mean(GrTemp_{t-3m}, GrTemp_{t-6m}, ..., GrTemp_{t-24m})           # 8 lags, mean skips NaN
ES_t     = GrTemp_t - Drift_t                                                  # = epspxq - epspxq_l12 - Drift
SD_t     = std(ES_{t-3m}, ..., ES_{t-24m}, ddof=1)                             # needs >= 2 non-NaN
EarningsSurprise = ES_t / SD_t ; inf -> NaN ; drop SD NaN or SD <= 1e-10
```
In report-period terms (quarter q, q_back index): GrTemp_q = eps_q - eps_{q+4 back}; Drift_q = mean(GrTemp of the 8 quarters before q); ES_q = GrTemp_q - Drift_q; SD = std(ES over the 8 quarters before q); signal = ES_0/SD.
Incomplete windows are scored: pandas `.mean()` / `.std()` skip NaN by default, so Drift and SD are taken over whatever lags exist (SD needs two). That is the source's own behaviour, not a deviation. A full window needs 21 quarters of eps (eps_q back to eps_{q-20}); the minimum is 8.

## 4. Timing / lag convention
- OSAP: m_QCompustat has one quarter available at `datadate + 3 months` (or the `rdq` month if later; dropped when rdq is > 6 months after datadate), expanded to exactly 3 monthly rows (offsets 0,1,2); the panel is then inner-merged, so a row exists at t only for a firm whose latest quarter became available within the last 3 months. Lags of 3,6,... months are calendar month shifts on that panel.
- Here: the signal changes at each new 10-Q/10-K filing (datekey, median ~44 days after quarter end) and is constant until the next; between filings it repeats (a step function, like OSAP's 3-month plateaus).
- Alignment: measured with as-of month-end lags (`ctx.fundamentals_at_month_ends(["eps"], range(0,61,3), dimension="ARQ")`). `MonthContext.fundamentals_yoy` documents that an as-of lag lands on the wrong quarter about 15% of the time under variable filing dates. RECOMMENDED: `ctx.fundamentals_history(["eps"], n_periods=21, dimension="ARQ")` pivoted on `q_back`, aligning the same-quarter-last-year by report period. This is a deviation from OSAP's calendar lag, logged; OSAP's 3-month expansion makes its lag approximately report-period aligned for regular filers.
- Staleness: OSAP keeps a quarter for only 3 months; the harness tolerance is `max_fundamental_age_months = 15`. Gate on the latest filing being at most ~4 months old (measured: requiring age <= 110 days removes 0.1-0.7 pp of coverage: 34.3 -> 34.2% in 1999-01, 91.7 -> 91.0% in 2003-01). Flow item under ART would smear: `dimension="ARQ"` is mandatory.

## 5. Filters
In code: `gvkey` non-null; SD non-null and SD > 1e-10; inf -> NaN. Reproduce all. SignalDoc `Filter = abs(prc)>5` is portfolio-stage, NOT in `predictor.py`: not reproduced (project universe: price >= $1). Exchange/share-code filters belong to the harness universe.

## 6. Predicted sign
SignalDoc `Sign = +1.0` (high surprise -> high returns); Stock Weight EW; LS Quantile 0.1; Portfolio Period 1; Start Month 12; Cat.Economic earnings growth. `FactorDef(ascending=True)`.

## 7. The mass-point question
- Do-nothing firm: identical eps in all quarters gives GrTemp = 0, ES = 0, SD = 0 -> signal NaN (dropped by SD > 1e-10), not a mass at 0. A firm that just files no new quarter repeats its prior signal (time plateau), not a cross-sectional tie.
- Measured on the scratch replica (month-end-lag proxy, universe ~1,900-2,700 names): SD <= 1e-10 on 0-4 names per month; ES exactly 0 among non-null ES: 0.48% (1999-01), 1.33% (1999-06, thin), 0.46%, 0.49%, 0.20%, 0.00% (2003-01), 0.00% (2010-06), 0.06% (2015-06), 0.05% (2021-11); modal value of the scored signal 0.05-0.16% of names; thousands of distinct values. No mass point. Ties: `rank(method="average")`, none expected.

## 8. History needed (snapshot starts 1998-01; SF1 ARQ eps rows start ~1993)
- Full window 21 quarters (about 60 months). Measured coverage of the universe (non-null signal / universe names): 34.3% (1999-01), 42.2% (1999-06), 47.6% (1999-12), 49.0% (2000-01), 80.0% (2001-01), 91.7% (2003-01), 96.5% (2010-06), 90.7% (2015-06), 86.4% (2021-11). Median count of usable ES lags among scored names: 0 (1999-01), 1 (1999-12), 5 (2001-01), 8 from 2003. Current-quarter eps is non-null on 95.6-99.4% of the universe every probe month, so the early shortfall is warm-up (too few prior quarters for SD), not data gaps.
- Preflight will WARN on the first probe month (coverage < 40%, a warning not a hard fail); the Stage 1 bar is on the mean over the window. Set `lookback_months` ~ 60 (preflight then warns the window reaches before the panel start). No `history_months` (no SEP input). Final coverage numbers come from preflight (these are from the month-end-lag proxy; report-period alignment not separately measured).

## 9. OSAP metadata (SignalDoc)
Acronym EarningsSurprise; Acronym2 EarnSurp; Foster, Olsen and Shevlin; 1984; AR; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 2_fair; Cat.Form continuous; Cat.Data Accounting;
Cat.Economic earnings growth; SampleStart 1974, End 1981; Key Table "4 Days +1 to +60"; Test "event study 2 months"; Sign +1.0; Return 2.975; T-Stat blank; EW; LS Quantile 0.1; Filter `abs(prc)>5`.
Notes: "No LS but very strong return pattern". Definition: "EPS (epspxq) minus EPS twelve months ago - Drift, scaled by standard deviation of that expression. Drift is the average earnings growth (EPS - EPS twelve months ago) over the past two years. Exclude if price less than 5".

## 10. Proposed Sharadar mappings and deviations
```
epspxq -> SF1.eps, dimension="ARQ" (per-quarter level; NOT the TTM sum)
eps_q, eps_{q-4}..  by report period via ctx.fundamentals_history(["eps"], 21, dimension="ARQ") (q_back pivot)
GrTemp/Drift/ES/SD as in 3 (skipna mean/std, ddof=1); signal = ES_0 / SD ; SD <= 1e-10 or non-finite -> NaN ; ascending=True
gate: latest filing age <= ~4 months (mirrors OSAP's 3-month plateau)
```
Deviations: (a) Sharadar `eps` = netinccmn / shareswa (net income to common incl. discontinued operations; basic, after sharefactor) vs Compustat `epspxq` (basic EPS EXCLUDING extraordinary items, as first reported). Not in the map as an extraordinary-item split; the surprise is on net rather than continuing EPS.
(b) `eps` on the current split basis throughout (scale cancels in ES/SD; OSAP's raw epspxq carries spurious split "surprises" that are absent here). (c) report-period alignment instead of calendar month lags (see 4). (d) 15-month harness staleness tolerance replaced by a ~4-month gate. (e) `abs(prc)>5` not reproduced. (f) restated quarters: dedup on reportperiod keeps the latest datekey at or before t, which can differ from first-print eps used by OSAP's Compustat snapshot.
`FactorDef`: `dimension="ARQ"`, inputs `SF1.eps`, `lookback_months=60`, `family=None` until Phase C. No fields outside the map (`eps`, `datekey`, `reportperiod` all present).
