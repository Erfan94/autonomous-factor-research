# OrderBacklog — Order backlog scaled by average assets (Rajgopal, Shevlin, Venkatachalam 2003, RAS)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/OrderBacklog.py` (cached `predictor.py`,
`upstream_CompustatAnnual.py`). DATA_SHA 198b281de1a0.

## 1. Data availability — VERDICT: data_unavailable (recommend `infeasible`)

| input (OSAP) | field_map key | Sharadar | status |
|---|---|---|---|
| `ob` (Compustat annual order backlog) | `compustat.ob` | none | unavailable ("no SF1 field; infeasible unless OSAP zero-fills it") |
| `at` | `compustat.at` | SF1 `assets` (ART/ARY) | mapped, verified 2026-09-30 |

- SF1 has 112 columns; none is `ob`, backlog, or any near-equivalent (I searched all 13 held tables by name). The
  nearest-sounding item, `deferredrev`, is unearned revenue (a liability), a different concept: NOT substituted.
- OSAP DOES zero-fill `ob` (`CompustatAnnual.py`, `zero_fill_vars` contains `'ob'`, applied by
  `compustat_data['ob'].fillna(0)`). Under the project rule ("infeasible unless OSAP itself zero-fills the missing
  item") this looks like a rescue, but it is not: the predictor then sets `OrderBacklog = NaN` wherever
  `ob == 0` and drops NaN rows. So OSAP's zero-fill means "missing backlog == no signal". With `ob` wholly absent
  from Sharadar, every firm takes the zero-filled value, every firm is NaN, and the signal is undefined for 100% of
  the universe. The zero-fill of a signal-DEFINING item that the predictor then nulls is undefined, not a constant
  approx. Nothing to rank.
- Measured: 0% coverage by construction (ob absent from all 13 tables); no probe months run. A real signal exists in
  OSAP only for firms that report a non-zero Compustat `ob`, information Sharadar does not carry and cannot be
  inferred from any held field.

## 2. Variables (exact source names)

`gvkey`, `permno`, `time_avail_m`, `ob`, `at` (m_aCompustat, annual values replicated monthly from datadate + 6 months).

## 3. Formula

```
at_lag12      = at shifted 12 monthly rows within permno
OrderBacklog  = ob / (0.5 * (at + at_lag12))        # backlog over average of this and last year's assets
OrderBacklog  = NaN where ob == 0                   # so the zero-filled missing case is excluded
dropna
```

## 4. Timing / lag

Annual item, 6-month lag from fiscal year-end (datadate + 6 months), carried 12 months; `at_lag12` is the same row a
year earlier in the monthly replicated series. Under ARY/ART-as-of-filing the signal would arrive ~3 months after year-end
instead of 6; moot here. Stock/flow: `ob` is a balance (stock), no TTM smear issue.

## 5. Filters

None in the code (SignalDoc Filter blank); "Exclude if order backlog is 0" is the `ob == 0 -> NaN` line.

## 6. Predicted sign

SignalDoc `Sign = -1.0` (-> `ascending=False`). `Cat.Economic` = sales growth; `Cat.Data` = Accounting; LS Quantile blank
(OP is a regression: FMB size-adjusted t=2.38, Table 3A gamma1, univariate), EW, sample 1981-1999. Predictability in OP
`1_clear`, quality `1_good`.

## 7. The mass-point question

In OSAP itself the non-reporting majority is NaN (not a cluster). Here, with `ob` unavailable, 100% are NaN. No value
ever exists, so no mass point and no tie handling is meaningful.

## 8. History needed

Two fiscal years of `at` (t and t-12 months); no `ob` history exists to count.

## 9. OSAP metadata

Acronym OrderBacklog; Acronym2 OrderBacklog; Key Table 3A gamma1; Portfolio Period 12, Start Month 6; GScholar cites 295;
"Table 3, but FMB size adjusted only. Other tables use nonlinear regressions."

## 10. Proposed Sharadar mappings

- `at` -> SF1 `assets` (mapped; would be used as ART average of this and 4 quarters earlier, or ARY).
- `ob` -> NONE. Recommend `infeasible`; frontier reason: "order backlog (Compustat ob) not in SF1; OSAP zero-fills ob
  then nulls ob == 0, so the signal is undefined for every firm".
