# CompEquIss — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: APPROX (constructible; declared deviations)
Checked against `osap_source/field_map_index.yaml`. No Compustat item enters.

| OSAP var | field_map key | Sharadar | status | role |
|---|---|---|---|---|
| ret | crsp.ret | SEP.closeadj month-end ratio (`ctx.monthly_closeadj(60)`) | mapped, verified 2026-09-30 | 60-month buy-and-hold return |
| mve_c | crsp.me / crsp.shrout | DAILY.marketcap (USD m), or SEP.close x SF1.sharesbas | me mapped (verified 2026-09-30); shrout approx | ME at t and t-60 |
| dlret | crsp.dlret | none (config delisting proxy) | unavailable | only inside OSAP `ret` |

- Why approx: (a) OSAP `ret` folds the delisting return into the index; Sharadar has
  none. A name alive at t has no delisting in its window, so this only touches the
  survivor composition. (b) `mve_c` = |prc| x shrout per PERMNO (security level,
  upstream_CRSPMonthly.py line 105); Sharadar marketcap is company-level on the
  primary ticker. The 60-month ratio of a company-level measure is what a
  multi-class firm's issuance means; differs for dual-class names only.
  (c) SF1 share counts are split-restated to today's basis (known_trap
  sf1_share_counts_split_restated): safe here only because BOTH ends use one route
  and the price is SEP.close (split-adjusted) or DAILY.marketcap (the same product).
  Never pair sharesbas with closeunadj. (d) Filing-date cadence of share counts vs
  CRSP's monthly shrout: the issuance piece updates stepwise, quarterly.
- No IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob or
  ppegt. OSAP zero-fills nothing here. Recommend: **approx** (feasible).

## 2. Variables by exact source name (predictor.py)
`SignalMasterTable`: permno, time_avail_m, ret, mve_c. Upstream
(`upstream_CRSPMonthly.py`, cached): `ret = (1+ret)(1+dlret)-1` with dlret defaulting
to -0.35 (NYSE/AMEX) / -0.55 (NASDAQ) for performance delistings and ret = dlret when
ret is missing; `mve_c = (shrout/1000) * abs(prc)` (USD millions). SignalMasterTable
keeps shrcd in {10,11,12}, exchcd in {1,2,3}.

## 3. Formula
Five-year log growth in market value of equity minus the five-year buy-and-hold
return (note: log minus SIMPLE):

    tempIdx = cumprod(1 + ret) per permno              # starts at 1 on the first row
    tempIdx_lag60, mve_c_lag60 = calendar-exact 60-month lags
    tempBH  = (tempIdx - tempIdx_lag60) / tempIdx_lag60
    CompEquIss = log(mve_c / mve_c_lag60) - tempBH

Sharadar form (both routes are valid; pick one and log it):
- Route A (preferred start date): `ME_t = SEP.close_t * SF1.sharesbas(ARQ, as of t)`,
  `ME_{t-60}` likewise via `ctx.at_month_end('SEP', ['close'], 60)` and
  `fundamentals_at_month_ends(['sharesbas'], [60], dimension='ARQ')`. Reaches back
  to SEP 1997-12-31, but `sharesbas` at the t-60 end needs an SF1 filing known
  by then: the earliest SF1 datekey is the 1997Q4 filing (early 1998), so the lag
  end is usable only from ~1998-02/03 (checker to confirm the earliest datekey).
- Route B: `DAILY.marketcap` at the signal month-end and `at_month_end('DAILY',
  ['marketcap'], 60)`. DAILY starts 1998-12-01, so the first 60-month lag is 1998-12.
- BH: `closeadj_t / closeadj_{t-60} - 1` from `ctx.monthly_closeadj(60)` (total return).
- Score = `-(log(ME_t/ME_{t-60}) - BH)`; require ME > 0 at both ends and closeadj
  non-null at both. The harness declares `history_months=60` and gates
  `has_price_at(60)`.

## 4. Timing / lag convention
Signal dated month t uses the month-t close; the portfolio code applies the usual
one-month forward hold. The 60-month lags are calendar-exact; a firm must have a
CRSP row exactly 60 months earlier, so every name needs 5 years of listing
(Sharadar has_price_at(60) replicates). OSAP cumprod treats a missing month's ret
as no change for later months; Sharadar month-end closeadj has no such hole. No
flow input: no TTM smear, no `dimension=ARQ` flow issue (ARQ only for sharesbas
alignment). ART-as-of-filing affects only the share-count step dates (filing date vs
CRSP's continuous shrout).

## 5. Filters
predictor.py none. SignalDoc Filter `abs(prc)>5` (applied in OSAP's portfolio
stage): the harness universe is price >= $1, so the $5 cut is NOT reproduced
(declared deviation); Quantile Filter blank. EW, Portfolio Period 1, Start Month 6.

## 6. Predicted sign (SignalDoc)
`Sign = -1.0`: heavy equity issuers underperform (Daniel and Titman Table 3,
regression t = 4.39). Score = -CompEquIss. Cat.Form continuous, Cat.Data Accounting,
Cat.Economic external financing; sample 1968-2003.

## 7. The mass-point question
- Continuous; do-nothing firm (no issuance or buyback, no dividends) gets
  `log(1+R) - R`, a smooth negative function of its five-year return R, not a
  constant. No structural mass point; ties negligible (average rank).
- Mechanical content to read at preflight: because the formula subtracts a SIMPLE
  return from a LOG growth, the signal = log(share ratio) - [R - log(1+R)], and
  R - log(1+R) ~ R^2/2 >= 0. Five-year winners (big R) score very negative (long
  leg after the sign), losers with R near -1 score enormously positive (short leg).
  Correlation with the 5-year return level/convexity is built in, not only with
  issuance. This is OSAP's formula; replicate, do not fix.
- Coverage limited to names with a 60-month history: no signal for the first five
  years after an IPO.

## 8. History needed
60 months of price and market cap. Route A: first usable t-60 is the first month with an SF1 filing
in hand (~1998-02/03; SEP alone starts 1997-12-31), so the first signal month is
~2003-02/03 (decision months 1999-01..~2003-01, ~49-50 of 276, empty; ~226 signal months). Route B: first month 2003-12 (59 empty, ~217 months). Stage 1
coverage bar (40%) and the LS-months floor must be read against that.

## 9. OSAP metadata
CompEquIss; Daniel and Titman (2006, JF), "Composite equity issuance"; Key Table 3
(`iota(t-5,t)`), univariate reg, t = 4.39; sample 1968-2003; Signal Rep Quality
1_good; Predictability 1_clear; GScholarCites202509 = 1640. Detailed Definition:
5 year growth rate of market value of equity minus 5 year stock return. Source
`Signals/pyCode/Predictors/CompEquIss.py` (in tree.txt, not a Placebo).

## 10. Proposed Sharadar mappings and deviations
| item | mapping | deviation |
|---|---|---|
| ret / BH | `monthly_closeadj(60)` ratio - 1 | no dlret; month-end ratio |
| mve_c | DAILY.marketcap or SEP.close x sharesbas (one route at both ends) | company-level, not per security; split-restated shares; quarterly share steps |
| Filter abs(prc)>5 | not reproduced (universe price >= $1) | looser |
| universe/ranks | harness; ranked within sector | OSAP EW cross-section |
Fields all in `field_map_index.yaml` (crsp.ret, crsp.me verified 2026-09-30;
crsp.shrout approx, not verified: the field-checker should verify sharesbas ARQ on
this snapshot if Route A is chosen).
