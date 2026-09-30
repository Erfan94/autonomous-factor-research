# ChNNCOA — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: APPROX (every input exists; 3 deviations, none unavailable)
Checked against `osap_source/field_map_index.yaml` (detail: field_map.yaml act, lt, debt, ivao).

| OSAP var | field_map key | Sharadar | status | role |
|---|---|---|---|---|
| at | compustat.at | SF1.assets | mapped, verified 2026-09-30 | level, scale, guard |
| act | compustat.act | SF1.assetsc | mapped, verified 2026-09-30; null 20.06% ART (unclassified BS) | level |
| ivao | compustat.ivao | SF1.investmentsnc | APPROX: includes equity-method investments (ivao + ivaeq) | level |
| lt | compustat.lt | SF1.liabilities | mapped, verified 2026-09-30 (null 0.05%) | level |
| dlc + dltt | compustat.dltt_plus_dlc | SF1.debt | mapped as a pair; carries ASC 842 lease break | level |

- Recommend `approx`, not `infeasible`: no IBES / segments / ppegt / pensions / xad / emp / ob input.
- Why approx: (1) ivao scope broader than Compustat; (2) `debt` (dlc+dltt, lease-inclusive from
  FY2019) produces a one-off lessee spike in the 12-month change in 2019-2021 filings;
  (3) act is null on the ~20% unclassified balance sheets, handled by OSAP's own zero-fill (below).
- OSAP `zero_fill_vars` (upstream_CompustatAnnual.py l.139-142) contains `act` and `ivao`; NOT
  `at`, `lt`, `dlc`, `dltt`. Rows with null at / prcc_c / ni are dropped upstream (l.86).
- Flow items: none (all balance-sheet levels, ART == ARQ). No `dimension=ARQ`, no TTM smear; the
  ~50% populated 1998Q1-Q3 ART TTM flows are irrelevant; levels are ~99.9% populated.

## 2. Variables by exact source name (predictor.py)
m_aCompustat columns gvkey, permno, time_avail_m, `at`, `act`, `ivao`, `lt`, `dlc`, `dltt`.
Annual FUNDA, `time_avail_m = datadate + 6 months`, each annual row repeated 12 months,
de-duplicated on (permno, time_avail_m) keeping first.

## 3. Formula
Net noncurrent operating assets scaled by total assets, then a 12-month difference (Soliman 2008,
Table 7 DeltaNCO):
    temp = ((at - act - ivao) - (lt - dlc - dltt)) / at
    ChNNCOA = temp - temp.groupby(permno).shift(12)      # 12 monthly ROWS = prior fiscal year
Algebra: (at - act - ivao) - (lt - dlc - dltt) = at - act - ivao - lt + (dlc + dltt), so dlc and
dltt enter only as their sum: Sharadar `debt`. Sharadar form:
`y = ctx.fundamentals_yoy(["assets","assetsc","investmentsnc","liabilities","debt"])`;
`r = (assets - assetsc0 - investmentsnc0 - liabilities + debt) / assets` evaluated on the current
and the `_lag` column sets; `ChNNCOA = r - r_lag`; score = -ChNNCOA (Sign -1).
Null handling (OSAP's own fill): `assetsc0 = assetsc.fillna(0)`, `investmentsnc0 =
investmentsnc.fillna(0)` ONLY where the filing exists (reportperiod / reportperiod_lag present);
never fill the NaN that `fundamentals_yoy` returns for a missing year-ago period. No fill on
assets, liabilities or debt (OSAP does not fill at, lt, dlc, dltt). Guard `assets > 0`, else NaN
(OSAP has no guard; a non-positive at yields inf/garbage). Consequence of the act fill: the
unclassified block (71% Financial Services, 20% Real Estate) stays IN and gets r = (at - ivao -
lt + debt)/at, exactly OSAP's value for a Compustat-null act. The field_map "never zero-fill act"
advice is for predictors where OSAP does not fill; here OSAP does, so the term is dropped (= 0)
and the row is approx. Translator must log this choice; preflight should report the
unclassified-block share of scored names.

## 4. Timing and lag convention
- OSAP: value changes once a year (annual data, +6 months). Sharadar ART-as-of-filing: the latest
  filed levels refresh quarterly, up to ~9 months fresher; the difference spans the latest 4
  quarters, not the fiscal year. No leak (datekey <= signal date).
- Year-ago via `ctx.fundamentals_yoy` (reportperiod aligned within 45 days; NaN if absent/stale).
  Do NOT use `fundamentals(lag_months=12)` (wrong quarter ~15% of the time; a stale repeated filing
  yields a false exact-zero change).
- Fill the zero-fill terms on BOTH sides consistently (current and lag).
- ASC 842: from FY2019 filings `debt` includes operating-lease liabilities while `liabilities`
  also includes them and `assets` includes right-of-use assets, so r jumps for lessees by about
  ROU/at (Compustat nets this: its dltt excludes leases, lt includes them). The change signal in
  2019-2021 signal months carries a cross-sectional lessee spike (retailers, airlines, restaurants).
  The window ends 2021-12, so ~3 years of the 23 are affected; a known, logged deviation.
- fxusd cancels (ratio of reporting-currency levels).

## 5. Filters
predictor.py has no filter beyond upstream at/prcc_c/ni non-null. SignalDoc `Filter` and
`Quantile Filter` empty. No factor-level filter; the harness universe applies.

## 6. Predicted sign (SignalDoc)
`Sign = -1.0`: higher growth in net noncurrent operating assets predicts lower returns. Score =
-ChNNCOA. Cat.Signal Predictor; Cat.Economic `investment alt`; Cat.Form continuous; Cat.Data
Accounting; Soliman 2008 (AR); sample 1984-2002; Predictability in OP 1_clear; Rep Quality 1_good;
Key Table "7 DeltaNCO", "mv reg", T-stat 5.26 (multivariate regression, no port sort).

## 7. The mass-point question
Continuous ratio difference. A do-nothing firm (balance sheet unchanged) produces exactly 0, which
is essentially only a stale-filing artefact (handled by `fundamentals_yoy`). Sharadar's own
zero-fills (ivao 51.5% exact zero, act ~0% zero) do not tie the DIFFERENCE, because at, lt and
debt move every quarter. Expected modal-value share ~0% (not measured here; preflight reports
it). Ties: average rank; no noise breaking. Firms with act null (unclassified) are NOT tied, they
get a normal value.

## 8. History needed
`history_months = 12` plus filing lag. SF1 broad from 1997Q4; first 1999 signal months rest on
year-ago 1998-dated filings: act-level year-ago coverage is ~38% at 1998-12 and ~71% from
1999-03 (field_map act). With act filled, coverage is governed by assets/liabilities/debt (>97%
universe levels). First 1-3 months may be thin; preflight reports first-month coverage.

## 9. OSAP metadata
Acronym ChNNCOA; Soliman 2008; Cat.Economic investment alt; Sign -1; EW; LS quantile blank;
portfolio period 12; start month 6; Filter none. Source `Signals/pyCode/Predictors/ChNNCOA.py`
at b4e911e69678a7424f318617a61d813f54183123; output `ChNNCOA.csv [permno, yyyymm, ChNNCOA]`. Cached:
predictor.py, signaldoc_row.csv, upstream_CompustatAnnual.py. SignalDoc definition: "Twelve-month
change in noncurrent operating assets. NCOA is ((at - act - ivao) - (lt - dlc - dltt))/at."

## 10. Proposed Sharadar mappings and deviations
1. at -> assets; act -> assetsc.fillna(0) where filing exists (OSAP fill); ivao ->
   investmentsnc.fillna(0) (broader, approx); lt -> liabilities; dlc+dltt -> debt (lease break).
2. Ratio on both sides of `fundamentals_yoy`; ChNNCOA = r - r_lag; score = -ChNNCOA; guard assets>0.
3. `history_months = 12`; `family = None` until Phase C; default dimension ART.
Deviations: rolling quarterly refresh vs annual; 4-quarter span vs fiscal year; ivao scope;
ASC 842 lessee spike 2019-21; at>0 guard. Fields not in field_map: none.
