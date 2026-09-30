# ChNWC — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: APPROX (all inputs exist; che is approx; ~19-20% coverage loss)
Checked against `osap_source/field_map_index.yaml` (detail: field_map.yaml che, dlc, act, lct).

| OSAP var | field_map key | Sharadar | status | role |
|---|---|---|---|---|
| act | compustat.act | SF1.assetsc | mapped, verified 2026-09-30; null 20.06% ART | level |
| che | compustat.che | SF1.cashneq + investmentsc.fillna(0) | APPROX (scope overshoot on financing receivables; understates for financials) | level |
| lct | compustat.lct | SF1.liabilitiesc | mapped, verified 2026-09-30; null 20.16% ART | level |
| dlc | compustat.dlc | SF1.debtc | mapped, verified 2026-09-30; null 20.10% ART; exact-zero 26.95% of non-null | level |
| at | compustat.at | SF1.assets | mapped, verified 2026-09-30 | scale |

- Recommend `approx`: che deviates (cash-and-STI scope), and the unclassified balance sheets
  (financials 71%, REITs 20%; same rows null in assetsc, liabilitiesc, debtc) cannot be scored
  from Sharadar. No IBES / segments / ppegt / pensions / xad / emp / ob input; not infeasible.
- OSAP `zero_fill_vars` (upstream_CompustatAnnual.py l.139-142) contains `act`, `che`, `lct`; NOT
  `dlc` and NOT `at`. In OSAP a bank with null act/lct gets 0/0 but still needs dlc non-null; in
  Sharadar dlc (debtc) is null on exactly that block, and `debt - debtnc` is null there too, so
  those names are NaN. Apply OSAP's fills only where the filing exists: assetsc.fillna(0),
  liabilitiesc.fillna(0); they are then moot because debtc is null on the same rows. Do NOT
  zero-fill debtc (OSAP does not fill dlc). Expected scored share of the universe ~80% vs OSAP's
  higher share; preflight reports coverage (universe ART coverage of debtc 79.7% / 82.6% / 81.5% /
  81.2% at 1998-12 / 1999-12 / 2008 / 2020).
- Flow items: none (levels; ART == ARQ). No `dimension=ARQ`, no TTM smear.

## 2. Variables by exact source name (predictor.py)
m_aCompustat columns gvkey, permno, time_avail_m, `act`, `che`, `lct`, `dlc`, `at`. Annual FUNDA
(consol C, INDL, STD, USD; rows with null at / prcc_c / ni dropped, l.86), time_avail_m =
datadate + 6 months, repeated over 12 months.

## 3. Formula
    nwc_numerator = (act - che) - (lct - dlc)
    at <= 0 -> NaN;   NWC = nwc_numerator / at
    ChNWC = NWC - NWC_lag12          # stata_multi_lag, [12]: 12-month CALENDAR lag on time_avail_m
Sharadar form: `y = ctx.fundamentals_yoy(["assetsc","cashneq","investmentsc","liabilitiesc","debtc","assets"])`;
`che = cashneq + investmentsc.fillna(0)` (fill only where filing exists); on both sides
`NWC = ((assetsc - che) - (liabilitiesc - debtc)) / assets` with assets <= 0 -> NaN;
`ChNWC = NWC - NWC_lag`; score = -ChNWC (Sign -1). Note "NWC" excludes cash and current debt:
it is non-cash working capital net of non-debt current liabilities (operating working capital).

## 4. Timing and lag convention
- OSAP: changes once a year (annual, +6 months; 12-month calendar lag = prior fiscal year).
  Sharadar ART-as-of-filing: latest filed levels, refreshing quarterly, up to ~9 months fresher;
  the difference spans the latest 4 quarters. No leak (datekey <= signal date).
- Year-ago via `ctx.fundamentals_yoy` (report-period aligned, NaN when absent/stale). Not
  `fundamentals(lag_months=12)` (wrong quarter ~15%; stale filing gives false zero change).
- Balance-sheet levels only: ART-as-of-filing changes the vintage, not a flow smear.
- ASC 842: debtc/debtnc lease inclusion was measured for debtnc (from FY2019) and debt; whether
  debtc carries current operating-lease liabilities is NOT measured in field_map (field-checker
  item). lct includes current lease liabilities in both Compustat and Sharadar; if debtc does not,
  (lct - dlc) rises by the current lease liability for lessees from FY2019 (small; ~1-2% of
  assets), a one-off in 2019-2021 signal months.
- fxusd cancels (ratio of reporting-currency levels).

## 5. Filters
predictor.py: none besides `at <= 0 -> NaN` and the upstream non-null at/prcc_c/ni. SignalDoc
`Filter = abs(prc)>5` (an OSAP portfolio-stage price filter, not in the script): not applied in the
factor; the harness universe (price >= $1, size/dollar-volume bands) applies. Quantile Filter empty.

## 6. Predicted sign (SignalDoc)
`Sign = -1.0`: higher growth in net working capital predicts lower returns. Score = -ChNWC.
Cat.Signal Predictor; Cat.Economic `investment alt`; Cat.Form continuous; Cat.Data Accounting;
Soliman 2008 (AR); sample 1984-2002; Predictability in OP 1_clear; Rep Quality 1_good; Key Table
"7 Model 2 DeltaWC", "mv reg", T-stat 4.61 (annual Fama-MacBeth, no sorts).

## 7. The mass-point question
Continuous ratio difference. A do-nothing firm (all four levels unchanged) gives exactly 0, only
arising from stale filings (excluded by `fundamentals_yoy`). Components with mass points: debtc
exact-zero 26.95% of non-null (17-27% of the universe by year), che ~0.2-1% zero; these do not tie
the difference because act, lct and cash move every quarter. Expected modal-value share ~0% (not
measured; preflight reports it). Ties: average rank, no noise. The ~20% unclassified names are
NaN, not tied (coverage, not a mass point).

## 8. History needed
`history_months = 12` plus filing lag. SF1 broad from 1997Q4. Year-ago coverage of the act-type
classified names is ~38% at 1998-12 and ~71% from 1999-03 (field_map act: lag_months=12 form);
`fundamentals_yoy` should do no worse. First 1-3 signal months may be thin; preflight reports it.

## 9. OSAP metadata
Acronym ChNWC (Acronym2 NWCgr); Soliman 2008; Cat.Economic investment alt; Sign -1; EW; LS
quantile blank; portfolio period 12; start month 6; Filter abs(prc)>5 (portfolio stage). Source
`Signals/pyCode/Predictors/ChNWC.py` at b4e911e69678a7424f318617a61d813f54183123; output
`ChNWC.csv [permno, yyyymm, ChNWC]`. Cached: predictor.py, signaldoc_row.csv,
upstream_CompustatAnnual.py. Definition: "NWC is ((act - che) - (lct - dlc))/at".

## 10. Proposed Sharadar mappings and deviations
1. act -> assetsc, lct -> liabilitiesc (fillna(0) only where filing exists; moot), dlc -> debtc
   (no fill), at -> assets (<= 0 -> NaN), che -> cashneq + investmentsc.fillna(0) (approx).
2. NWC on both sides of `fundamentals_yoy`; ChNWC = NWC - NWC_lag; score = -ChNWC.
3. `history_months = 12`; `family = None` until Phase C; default dimension ART.
Deviations: che scope; ~20% unclassified names unscoreable; rolling quarterly refresh vs annual;
4-quarter span; possible debtc lease inclusion from FY2019 (unmeasured); no price>5 filter.
Fields not in field_map: none.
