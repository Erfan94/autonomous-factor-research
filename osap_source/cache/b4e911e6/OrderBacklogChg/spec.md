# OrderBacklogChg — Change in normalized order backlog (Baik and Ahn 2007)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/OrderBacklogChg.py` (cached `predictor.py`,
`upstream_CompustatAnnual.py`). DATA_SHA 198b281de1a0.

## 1. Data availability — VERDICT: data_unavailable (recommend `infeasible`)

| input (OSAP) | field_map key | Sharadar | status |
|---|---|---|---|
| `ob` | `compustat.ob` | none | unavailable |
| `at` | `compustat.at` | SF1 `assets` | mapped, verified 2026-09-30 |

- Same gap as OrderBacklog: no `ob`/backlog column in any of the 13 held tables (SF1 112 columns checked by name;
  `deferredrev` is unearned revenue, a different item, not substituted).
- OSAP zero-fills `ob` (`CompustatAnnual.py` `zero_fill_vars` includes `'ob'`; `fillna(0)`), and the predictor then
  does `OrderBacklog = NaN where ob == 0`. Both the level and its 12-month lag are NaN for every non-reporter, so
  `OrderBacklogChg = OrderBacklog - OrderBacklog_lag12` needs a non-zero reported backlog at BOTH t and t-12. With
  `ob` absent, every firm is NaN at both ends: the signal is undefined for 100% of the universe. The zero-fill
  nulls the signal-defining item rather than supplying a neutral value; the missing-item rule gives `infeasible`.
- Measured: 0% coverage by construction; no probe months run.

## 2. Variables (exact source names)

`gvkey`, `permno`, `time_avail_m`, `ob`, `at` (m_aCompustat).

## 3. Formula

```
at_lag12            = at shifted 12 rows within permno
OrderBacklog        = ob / (0.5 * (at + at_lag12));  NaN where ob == 0
OrderBacklog_lag12  = OrderBacklog shifted 12 rows
OrderBacklogChg     = OrderBacklog - OrderBacklog_lag12
dropna
```
Needs `at` at t, t-12, t-24 (the lagged OrderBacklog uses `at` at t-12 and t-24) and `ob` at t and t-12.

## 4. Timing / lag

Annual, datadate + 6 months, replicated 12 months; lags are monthly rows. OP assumes a 4-month lag; OSAP uses the
standard 6 (SignalDoc note). `ob` is a stock, no TTM smearing; the year-over-year difference is a plain annual change.

## 5. Filters

None in code; "Exclude if order backlog is 0" is the `ob == 0` null.

## 6. Predicted sign

SignalDoc `Sign = +1.0` (-> `ascending=True`: high change in backlog long). `Cat.Economic` = accruals; `Cat.Data`
= Accounting; port sort, LS quantile 0.1, EW, sample 1971-1999; quality `2_fair`, OSAP return 1.17%.

## 7. The mass-point question

Moot. In OSAP the non-reporters are NaN, not a cluster; firms with unchanged normalized backlog give exactly 0 only when
backlog and average assets are both unchanged (negligible). Here 100% NaN.

## 8. History needed

Three fiscal years of `at`, two of `ob` (none available).

## 9. OSAP metadata

Acronym OrderBacklogChg; Key Table 2 High-Low; Portfolio Period 12, Start Month 6; GScholar cites 23;
"Define normalized order backlog as order backlog (ob) divided by average total assets (at) in years t-1 and t.
Exclude if order backlog is 0. Signal is normalized order backlog minus normalized order backlog one year ago."

## 10. Proposed Sharadar mappings

- `at` -> SF1 `assets`. `ob` -> NONE. Recommend `infeasible`; frontier reason as OrderBacklog.
