# DelLTI — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: INFEASIBLE (recommend `infeasible`; measured, two independent reasons)
Every input exists, but the signal cannot clear the harness gates on this snapshot:
- **Mass point.** OSAP zero-fills `ivao` (`zero_fill_vars`, upstream_CompustatAnnual.py), and Sharadar
  zero-fills `investmentsnc` the same way (DESCRIPTIONS: "value of 0 is used"; 51.5% exact-zero ART). So DelLTI
  = 0 for every firm whose `ivao` is 0 in both years. Measured on the universe (`fundamentals_yoy`, avg assets > 0):
  exact-zero share of SCORED names 58.2% (1999-06), 54.4% (2003-12), 50.7% (2008-12), 57.1% (2015-12),
  59.9% (2019-12); both-years-zero names = 40.4-45.6% of the whole universe. Preflight cliff is 10%
  (`qcut` yields < 10 bins): hard fail on every probe month.
- **The only tie treatment that removes it fails coverage.** Nulling exact zeros leaves scored coverage of
  30.9% (1999-06), 36.2% (2003-12), 39.5% (2008-12), 32.9% (2015-12), 30.7% (2019-12) of the universe,
  below the 40% Stage 1 bar (distinct non-zero values ~570-750 per month).
Not a zero-fill-dropped term (nothing is dropped); this is a mass-point/coverage infeasibility.

| OSAP var | field_map key | Sharadar | status |
|---|---|---|---|
| `ivao` | compustat.ivao | SF1 `investmentsnc` | approx (see section 10); OSAP zero-fills it |
| `at` | compustat.at | SF1 `assets` | mapped, verified 2026-09-30 (null 0.05%) |

## 2. Variables (predictor.py)
`m_aCompustat`: gvkey, permno, time_avail_m, `at`, `ivao` (annual FUNDA; `ivao` zero-filled upstream).

## 3. Formula
```
tempAvAT = 0.5 * (at + l12_at)            # l12 = same permno, time_avail_m - 12 months (month-merge)
DelLTI   = (ivao - l12_ivao) / tempAvAT   # dropna
```
Change in long-term investments and advances, scaled by average total assets (year t and t-1).
Duplicates on (permno, time_avail_m) keep first. No `at > 0` guard in OSAP (guard `avgAT > 0` here).

## 4. Timing / lag
- OSAP: `time_avail_m = datadate + 6 months`, replicated over 12 months; the 12-month lag merge hits the prior
  fiscal year's row exactly when it exists (merge on date, not row shift). Signal is 6-17 months stale.
- Sharadar: both terms are LEVELS (stocks; ART == ARQ same-period 100% on 544k `investmentsnc` rows): no TTM
  flow smear, `dimension` stays ART. Year-ago via `ctx.fundamentals_yoy([...], years=1)` (report-period aligned,
  tol 45 days), never `lag_months=12`. ART-as-of-filing turns OSAP's annual-FYE change into a rolling 4-quarter
  change refreshed every quarter and 0-3 months old.

## 5. Filters
SignalDoc Filter and Quantile Filter blank; predictor.py has none. Harness universe applies.

## 6. Predicted sign
`Sign = -1.0` (Richardson, Sloan, Soliman, Tuna 2005, Table 8C, t = 3.38 mv reg; "FMB only"): higher change in long-term
investment predicts lower returns; long low, short high.

## 7. Mass-point question
Do-nothing firm (ivao 0 in both years, or unchanged) = exactly 0. Share: 50.7-59.9% of scored names, 40-46% of the
universe (section 1). Ties: average rank would put more than half the cross-section at one rank; deciles collapse
(D1..D5+ identical). OSAP has the same point mass (its zero-fill), which is why its quantile sort is unstable on
this signal. No legitimate tie handling clears coverage >= 40%.

## 8. History needed (snapshot starts 1998-01)
Latest filing + same period a year earlier (`fundamentals_yoy`). Universe coverage: `assets_lag` 49.8% at
1999-01, 89.1% 1999-03, ~92-98% thereafter; DelLTI scored 39.7% (1999-01), 71.0% (1999-03), 74-80% later (before
zero-nulling; `investmentsnc` null 20.0% = unclassified balance sheets). No `history_months`.

## 9. OSAP metadata
Richardson et al. (2005), JAE; Cat.Data Accounting; Cat.Economic investment; continuous; sample 1962-2001;
Acronym2 ChLTI; Portfolio Period 12, Start Month 6; EW; Key Table 8C univariate reg; 1_clear / 1_good.
Source `Signals/pyCode/Predictors/DelLTI.py`. SignalDoc definition: "Difference in investment and advances (ivao)
between years t-1 and t, scaled by average total assets (at) in years t-1 and t."

## 10. Proposed Sharadar mappings (if the owner overrides the recommendation)
`ivao` -> `investmentsnc` (null stays null; never zero-fill), `at` -> `assets` (gate `fxusd == 1`, <= 0.06% of
universe), via `fundamentals_yoy(years=1)`; `avgAT > 0`.
Deviations: `investmentsnc` is BROADER than ivao (includes equity-method investments: KO FY2023 $19.8B ~ its
$19.4B equity-method line, so ivao + ivaeq); ART quarterly refresh vs annual; ~20% structural null block
(financials/REITs; OSAP's zero-fill would give them 0). All fields in the map; none unavailable.
