# ChTax — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: FEASIBLE (two inputs, both mapped) with deviations to log
| OSAP var | field_map key | Sharadar | status | role |
|---|---|---|---|---|
| txtq | compustat.txtq | SF1.taxexp, dimension=ARQ | mapped (same column as txt; single-quarter flow confirmed) | numerator flow, current and year-ago |
| at | compustat.at | SF1.assets | mapped, verified 2026-09-30 (null 0.05%) | denominator, lagged |

- No unavailable data (no IBES, segments, ppegt, pensions, xad, emp, ob). Neither term is a
  zero-fill deviation: txtq is not in OSAP `zero_fill_vars` (upstream_CompustatAnnual.py l.139-142);
  `at` is not filled either.
- ONE data property that is not an OSAP deviation but drives the verdict's risk: Sharadar itself
  zero-fills `taxexp` when not on the statements (DESCRIPTIONS), ARQ exact-zero 20.64% of all rows.
  This is a real mass point (section 7). Recommend `feasible`; `approx` only if the reviewer counts
  the lagged-assets substitution (section 4) as material, which it should not.
- FLOW ITEM: txtq is a single-quarter flow. A year-over-year difference must be taken on ARQ
  (`FactorDef.dimension = "ARQ"`), NOT ART, where the 12-month difference of a TTM sum smears four
  quarters (and is ~50% populated 1998Q1-Q3). The assets legs are levels (ART == ARQ).

## 2. Variables by exact source name (predictor.py)
Annual m_aCompustat: gvkey, permno, time_avail_m, `at` (FUNDA, +6 months, repeated 12 months).
Quarterly m_QCompustat: gvkey, time_avail_m, `txtq` (FUNDQ; time_avail_m = datadate + 3 months, or
the rdq month if later; dropped if rdq > 6 months after datadate; repeated over 3 months 0-2).
Inner merge on (gvkey, time_avail_m).

## 3. Formula
Thomas and Zhang 2011, Table 2 col (1): 4-quarter change in quarterly total taxes scaled by lagged
total assets.
    l12_txtq, l12_at = same gvkey, time_avail_m - 12 months (calendar-matched, NOT shift)
    ChTax = (txtq - l12_txtq) / l12_at
Sharadar form (ARQ): `y = ctx.fundamentals_yoy(["taxexp","assets"])`;
`ChTax = (taxexp - taxexp_lag) / assets_lag`; guard `assets_lag > 0`, else NaN; score = +ChTax
(Sign +1). taxexp null -> NaN (0.28% in a 1999-2021 US-common pair sample); no fill.

## 4. Timing and lag convention
- OSAP: a quarterly signal available at datadate+3 months (or rdq month), held up to 3 months; the
  pairing with t-12 is the same quarter a year earlier (calendar match; absent if a quarter is
  missing). DENOMINATOR quirk: `at` is the ANNUAL item forward-filled, so l12_at is the total assets
  of the latest fiscal year-end known 12 months earlier, i.e. 18-30 months before signal date
  (stale by design). Sharadar ARQ `assets_lag` = total assets at the quarter a year before the
  latest reported quarter: fresher (12 months), a deviation in level of a few to ~10%, inside a
  ratio that ranks; log it.
- ARQ as-of-filing: the latest filed quarter's taxexp vs the same fiscal quarter a year earlier via
  `fundamentals_yoy` (reportperiod aligned, NaN when absent/stale). Do not use
  `fundamentals(lag_months=12)`. Refresh: once per quarterly filing, as OSAP.
- Stale filings: when the latest filing is stale at both dates, yoy is NaN rather than a false 0.
- fxusd cancels (both terms reporting currency). No leak (datekey <= signal date).
- SF1 ARQ flows start in broad form 1997Q4: year-ago needs a filing >= 1998Q4 as of the signal
  date, so 1999-01..02 signal months are thin (only a few early Q4 filers); coverage normal from
  ~1999-03/04. preflight reports first-month coverage.

## 5. Filters
predictor.py: none. SignalDoc `Filter` empty, `Quantile Filter` empty. No factor-level filter;
harness universe applies. Guard assets_lag > 0 only.

## 6. Predicted sign (SignalDoc)
`Sign = +1.0`: a rise in taxes predicts higher returns (long high ChTax; OSAP LS 0.1 quantile,
EW). Cat.Signal Predictor; Cat.Economic `other`; Cat.Form continuous; Cat.Data Accounting;
Thomas and Zhang 2011 (JAR); sample 1977-2006; Predictability in OP 1_clear; Rep Quality 1_good;
Key Table "Table 2, column (1)", "port sort", T-stat 11.26 in decile sort; OSAP Return 1.3;
Portfolio Period 3; Start Month 6. Acronym2 `TaxGr`.

## 7. The mass-point question
SF1 zero-fills taxexp; a firm with taxexp == 0 in both quarters (loss-makers, NOL, tax-free
structures, plus vendor-imputed zeros) produces ChTax EXACTLY 0. Measured here on SF1 ARQ, US
Domestic Common on NYSE/NASDAQ/NYSEMKT, calendardate-paired year-ago quarters 1999-2021 (438,474
pairs, NOT universe-filtered, so a proxy): both-zero 16.7% of non-null pairs; 18.3% (1999),
14.0% (2008), 18.5% (2020); unchanged nonzero 0.45%; diff == 0 in total 17.2%; lagged assets null
or <= 0 0.05%. Expect roughly 10-18% of universe names at exactly 0 (universe membership should
lower it: larger firms pay tax); preflight must report the modal share, by sector and by year.
- Ties: average rank at 0; it sits between negative and positive changes, so it is an interior
  block (deciles ~4-6 collapse if ~15% tie), tails remain populated (Sign +1: long D10 = large
  tax increase, short D1 = large decrease/benefit). Sector-relative rank: tied share is higher in
  Health Care/Technology (loss-makers); a sector-month with <10 scored names falls back.
- Do not break ties with noise or a secondary key; a preflight mass-point failure is a measured
  outcome, not a reason to alter the construction. Do not drop zero-tax firms (OSAP keeps them).
- Real benefit values (negative taxexp, ARQ 14.98% negative) are legitimate; do not clip.

## 8. History needed
`history_months = 12` plus one quarterly filing lag (year-ago quarter). SF1 from 1997Q4; first
signal months 1999-01..03 thin as above. Snapshot starts 1998-01 for the price side.

## 9. OSAP metadata
Acronym ChTax; Thomas and Zhang 2011; Cat.Economic other; Sign +1; EW; LS quantile 0.1; portfolio
period 3; start month 6; Filter none. Source `Signals/pyCode/Predictors/ChTax.py` at
b4e911e69678a7424f318617a61d813f54183123; output `ChTax.csv [permno, yyyymm, ChTax]` (via
save_predictor). Cached: predictor.py, signaldoc_row.csv, upstream_CompustatAnnual.py,
upstream_CompustatQuarterly.py. Definition: "4-quarter change in quarterly total taxes (txtq),
scaled by lagged total assets (at)."

## 10. Proposed Sharadar mappings and deviations
1. txtq -> SF1.taxexp with `FactorDef.dimension = "ARQ"`; year-ago via `fundamentals_yoy`.
2. lagged at -> `assets_lag` from the same ARQ yoy frame (level; ART == ARQ), guard > 0.
3. score = +ChTax; `history_months = 12`; `family = None` until Phase C.
4. No zero-fill, no clipping, no winsorising in the factor.
Deviations: denominator is the year-ago QUARTER assets, not the stale annual assets; Sharadar
imputed zeros (DESCRIPTIONS) may inflate the tie at 0 relative to Compustat txtq, where an
unreported quarter is NaN (share not separable here); OSAP's 3-month hold (Portfolio Period 3)
is harness-side. Fields not in field_map: none (taxexp/txtq verified; assets mapped).
