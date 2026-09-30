# BetaFP — Frazzini-Pedersen beta (Frazzini and Pedersen 2014, JFE, Table 3 BAB)

OSAP ref b4e911e69678a7424f318617a61d813f54183123. Source: `Signals/pyCode/Predictors/ZZ2_BetaFP.py`
(SignalDoc Acronym `BetaFP`, Cat.Signal Predictor; the file is `ZZ2_*`, the row is the authority).
Cached: `predictor.py`, `signaldoc_row.csv`, `upstream_CRSPDaily.py`, `upstream_FamaFrenchDaily.py`.
DATA_SHA 198b281de1a0. field_map statuses are mappings, not proofs, until verified.

## 1. Data availability — verdict FEASIBLE (declared deviations; no zero-filled optional term)

| OSAP input | field_map key | Sharadar | status (reset) |
|---|---|---|---|
| CRSP daily `ret` (dailyCRSP) | `crsp.ret` | SEP.closeadj, day-over-day ratio (total return) | mapped |
| `mktrf`, `rf` (dailyFF, Ken French) | NO field key (only `public_sources: Ken French factors` prose) | `MonthContext.market_daily(days_back, min_days)` = harness raw prior-day-cap-weighted all-stock return | harness-built, not a field_map field |

- No Compustat, IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob, ppegt input. No fundamentals
  at all: the ART-vs-filing-date question does not arise. No OSAP zero-fill.
- `rf` is genuinely absent from the snapshot (field_map `public_sources`). Declared deviation, see section 3.
- Market series exists ONLY from 1998-12-02 (DAILY.marketcap starts 1998-12-01). SEP alone starts 1997-12-31 but
  there is no market index before 1998-12-02, so SEP history earlier than that is unusable for this signal.
  Consequence (section 8): the first scorable month-end is about 2000-11-30, not 1998-12-31.
- Harness-side only: `crsp.me`/DAILY.marketcap (also the market weights), `crsp.shrcd`, `crsp.exchcd`. Field-checker
  to verify on THIS snapshot: `crsp.ret` (closeadj null rate, continuity across splits); `market_daily` >= 500 days
  by 2000-11 (starts 1998-12-02, `MARKET_MIN_NAMES` 30).

## 2. Variables (exact source names)

`dailyCRSP`: `permno`, `time_d`, `ret`. `dailyFF`: `time_d`, `rf`, `mktrf`. Inner join on `time_d`. Derived:
`LogRet`, `LogMkt`, `sd252_LogRet`, `sd252_LogMkt`, `tempRi`, `tempRm` (3-day log-return sums), `_R2`, `BetaFP`.

## 3. Formula and key lines

BetaFP = sqrt(R2) * sd252(LogRet) / sd252(LogMkt), per stock, evaluated every trading day, month value = the
LAST finite BetaFP of the calendar month. Equivalently |corr| * (sigma_i / sigma_m): the correlation from 3-day
overlapping returns over a long window, the vol ratio from 1-year daily returns (Frazzini-Pedersen's own design).
```
LogRet = log1p(ret); LogMkt = log1p(mktrf)              # one with_columns: LogRet uses RAW ret (ret - rf is unused)
sd252_*  = rolling_std(252, min_samples=120).over(permno)        # on the stock's own rows
tempRi   = LogRet + shift1 + shift2 ; tempRm likewise           # row shifts within permno, not calendar days
cov = rolling_mean(tempRi*tempRm) - rolling_mean(tempRi)*rolling_mean(tempRm)   # window 1260, min_samples 500
_R2  = (cov / (rolling_std(tempRi) * rolling_std(tempRm)))**2
BetaFP = sqrt(abs(_R2)) * sd252_LogRet / sd252_LogMkt
monthly: filter finite, group (permno, month of time_d), last
```
Keep: (a) windows count the stock's OWN rows (a gap stretches the calendar span); (b) BetaFP >= 0 always (sqrt of
R2): a negatively correlated stock gets a POSITIVE value, not a signed beta; (c) `min_samples` 120 rows (vols), 500
rows of 3-day returns (502 trading days incl. shifts); SignalDoc prose says "minimum 3 years", the CODE governs;
(d) covariance from population moments, std ddof=1: corr scaled by (n-1)/n, negligible.
OSAP stock side is total return, market side excess; a raw market shifts sigma_m/corr by rf (~0-2bp/day): declare.
Sharadar-side: stock daily r = SEP.closeadj_t / closeadj_{t-1} - 1 on the stock's previous ROW (no dlret, as OSAP
uses ret only); keep only days that are market trading days (OSAP inner-join with FF); market = `market_daily`.
Bad-print guards cover the MARKET series only; stock returns are untrimmed as in OSAP (an extreme SEP print
inflates sd252 for up to 252 rows). Harness ranks are monotone: no transform of the output.

## 4. Timing / lag

- OSAP: value through the last trading day of month t, `time_avail_m` = that month, portfolio formed from it for
  month t+1 (OSAP Portfolio Period 1, Start Month 6 is the sample-start field, not a lag). No extra lag.
- Here: value through the last SEP/market trading day <= signal_asof. No lag. Nothing in this signal is a filing,
  so ART-as-of-filing changes nothing and there is no flow item to smear (`dimension` not needed, no
  `fundamentals*` call). Factor pulls `ctx.daily("SEP", ["closeadj"], days_back~1900)` (1260 rows ~ 1830 calendar
  days) and `ctx.market_daily(1900, min_days=...)`; declare `SEP.closeadj` and `DAILY.marketcap` in FactorDef.inputs.
  Performance: `ctx.daily` masks the full SEP table each month (~45M rows); compute per month, no cross-month state.

## 5. Filters

OSAP: none beyond the inner merge with FF dates and `is_finite(BetaFP)` (SignalDoc Filter blank). Harness universe
and sector ranking sit outside the factor. < 120 vol rows or < 500 3-day rows -> NaN; IPOs score ~2 years late.

## 6. Predicted sign (SignalDoc)

`Sign = 1.0` (Return 0.7, T-Stat 7.12, Test in OP `port sort nonstandard`, Stock Weight EW, LS Quantile 0.1,
Portfolio Period 1, Start Month 6, Sample 1929-2012, Cat.Economic `other`, Cat.Data `Price`, Cat.Form continuous,
Predictability in OP `2_likely`, Signal Rep Quality `3_distant`). Orientation = SignalDoc Sign as written: high
BetaFP is the long side in the harness. SignalDoc Notes: the paper's factor is a rank-weighted, beta-standardised
median split (BAB), not a D10-D1 sort, so portfolios here are not the paper's. FLAG FOR THE ORCHESTRATOR: this is
a Sign of +1 on a beta-type signal; the translator orients `ascending` by the SignalDoc field only, and a flipped
sign is a second hypothesis (|t| >= 2.74) under the project rules.

## 7. The mass-point question

- Raw values are continuous (ratio of a correlation and a vol ratio). A "do-nothing" firm (constant price, zero
  vol) gives sd = 0 -> corr = 0/0 = NaN -> BetaFP NaN (not 0). OSAP's `is_finite` filter drops it; no value at 0.
- Stale pricing lowers sigma but makes no mass point; share at any single value ~0% in this universe. NaN share
  from history < 500 rows: the recent-IPO tail, largest early (market start). Preflight measures mode%/distinct.
- Ties: none. Guard `sd_m.where(sd_m > 0)` and sd_i likewise -> NaN; never floor. An empty `market_daily`
  (under min_days) makes the month unscorable.

## 8. History needed

- Return window: 1260 rows (5 years) maximum, 500 valid overlapping 3-day rows minimum (~24 months), 120 rows
  for the vol. Declare `history_months=24`, `lookback_months=60` (the 5-year window; preflight will warn the panel
  starts 1998 and early months read low for a data reason, which is true here).
- First signal 1998-12-31 is NOT scorable. SEP starts 1997-12-31 but market_daily starts 1998-12-02. Counting
  market rows from 1998-12-02 (21 in 1998-12, 252 in 1999, 2000 cumulative 212 by end-October, 233 by
  end-November) the 502nd row falls in late 2000-11. First scorable month-end ~2000-11-30, only for names that
  printed on every market day since 1998-12-02. About 22-23 of 276 decision months (~8%) are data-null, and
  2000-11..2001 coverage is below steady state. Docstring states this; preflight reports coverage by year. The
  `history_months=24` gate does not bind before 2000-11 (SEP reaches back 24 months only from 1999-12).

## 9. OSAP metadata

Acronym BetaFP; Frazzini and Pedersen 2014 JFE; LongDescription "Frazzini-Pedersen Beta"; Cat.Signal Predictor;
Cat.Economic `other`; Cat.Data Price; Cat.Form continuous; Key Table `3 BAB`; Sample 1929-2012; Sign 1.0;
GScholarCites202509 323. Detailed Definition: 3-day overlapping returns regressed on the market over 5 years
(min 3), BetaFP = sqrt(R2) * stock vol / market vol.

## 10. Proposed Sharadar mappings and deviations

| OSAP | Sharadar | deviation |
|---|---|---|
| `ret` (crsp.ret) | SEP.closeadj_t/closeadj_{t-1}-1, stock's own previous row | no delisting return (OSAP does not use dlret here either); split/dividend-adjusted on TODAY's basis, ratios unaffected; a name's last move off-exchange absent |
| `mktrf` | `MonthContext.market_daily(days_back, min_days)` col "vw" | raw (no rf); all-stock cap-weighted reconstruction from DAILY.marketcap, prior-day weights, causal spike/reversal/cap-to-ADV guards; no dlret; returns across a trading gap excluded; from 1998-12-02 only |
| `rf` | none | not in snapshot; stock side in OSAP is total return (rf not subtracted from LogRet), market side in OSAP is excess: negligible shift in sigma_m and corr |
| inner merge with FF on `time_d` | keep stock rows on `market_daily` dates | same |
| 252/1260-row rolling windows, `min_samples` 120/500 | numpy/pandas rolling over the stock's own rows | same counts; vol ddof=1, covariance via means (as OSAP) |
| monthly: last finite value of the month | compute at signal_asof (last trading day of the month) | same; last value is the month-end value by construction |
| universe / sector / ranking | harness | none |

Flags: `mktrf`/`rf` have no field_map key (prose only); the translator declares `inputs=("SEP.closeadj",
"DAILY.marketcap")` and quotes the market deviations in the docstring.
