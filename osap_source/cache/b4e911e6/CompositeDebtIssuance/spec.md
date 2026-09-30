# CompositeDebtIssuance — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: APPROX (constructible; two declared deviations)
Checked against `osap_source/field_map_index.yaml` (detail: `field_map.yaml`).

| OSAP var | field_map key | Sharadar | status | role |
|---|---|---|---|---|
| dltt + dlc | compustat.dltt_plus_dlc | SF1.debt | mapped (verified-with-deviation 2026-09-30) | level at t and t-5y |
| dltt | compustat.dltt | debtnc | approx (ASC 842), not used | component |
| dlc | compustat.dlc | debtc | mapped, not used | component |

- Use SF1.debt for the sum, NOT `debtc.fillna(0) + debtnc.fillna(0)` (debtc/debtnc
  null ~20% = unclassified balance sheets; debt null only 0.03% ART, populated on
  99.86% of the unclassified block).
- Deviation 1 (why approx): **Sharadar debt INCLUDES operating-lease liabilities
  from ASC 842** (FY2019 calendar filers; FY2018 early adopters), Compustat
  dltt + dlc does not. A 5-year log change whose current end is a FY2019+ filing and
  whose base is earlier carries a one-off lessee-wide positive step (retail,
  restaurants, airlines, REITs). Measured on the universe (ART at Dec): exact-zero
  debt 9.1% (2018) -> 2.9% (2019); median debt/assets 0.291 -> 0.320; YoY change
  p75 0.045 -> 0.115 (2019) -> 0.070 (2020). In-window (to 2021-12) this touches
  the FY2019, FY2020 and FY2021 filing months, and the stale-base effect lasts 5
  years, so for signals from 2019 on the change is confounded. Sector ranking
  removes a sector-wide lease step but not a lessee/non-lessee step inside a sector.
- Deviation 2: bank debt in Sharadar includes repo and short-term borrowings
  (JPM debt 1,064bn on 4,560bn assets); OSAP does not exclude financials and
  Compustat dltt + dlc for banks is a narrower concept.
- OSAP zero-fills neither dltt nor dlc (not in `zero_fill_vars`); a missing
  component makes tempBD NaN. Nothing unavailable; no IBES, options, 13F, patents,
  segments, ratings, pensions, xad, emp, ob or ppegt input.
- Recommend: **approx** (feasible).

## 2. Variables by exact source name (predictor.py)
`m_aCompustat`: gvkey, permno, time_avail_m, dltt, dlc. Upstream
(`upstream_CompustatAnnual.py`, cached): FUNDA consol C, popsrc D, datafmt STD,
curcd USD, INDL; rows with null `at`, `prcc_c` or `ni` DROPPED; dltt/dlc not
zero-filled; `time_avail_m = datadate + 6 months`, each annual row replicated for
12 monthly offsets; dedupe (permno, time_avail_m) keeping the latest datadate.

## 3. Formula
Log growth in total debt over 60 months:

    tempBD = dltt + dlc                    # NaN if either is NaN
    l60    = tempBD at time_avail_m - 60 months (exact calendar match, else shift(60))
    CompositeDebtIssuance = log(tempBD / l60)

Sharadar form: on the ART filing at signal and its same-fiscal-period filing five
years earlier, `log(debt / debt_lag)` with both `debt > 0` (`ctx.fundamentals_yoy(
['debt'], years=5)`; `history_months` not needed, no price window).

## 4. Timing / lag convention; what ART-as-of-filing changes
- OSAP: an annual value is usable from datadate + 6 months and held 12 months, so the
  lag-60 is exactly 5 fiscal years earlier (the shift(60) fallback is a rough
  row-position lag when a month is missing).
- Sharadar: `debt` is a balance-sheet LEVEL, ART == ARQ on 99.5% of same-period
  pairs, so no TTM smear and `dimension=ARQ` adds nothing. ART refreshes each quarter
  at the filing date (datekey), so the signal is more current than OSAP's annual,
  6-month-delayed value (an ARY filing is known a median ~76 days after the
  fiscal year end vs OSAP's 6 months). `years=5` aligns by report period (tol 45 days); do not use
  `lag_months=60` (known_trap yoy_by_report_period). The `fundamentals_yoy` history
  window (4*5+4 = 24 quarters) covers it. For a closer annual replica use
  dimension=ARY (fewer, annual refreshes); the default ART is recommended.

## 5. Filters
predictor.py: none. SignalDoc Filter blank, Quantile Filter blank. OSAP
effectively drops rows with debt = 0 at either end (log of 0 is -inf, 0/0 NaN) and
rows with null at/prcc_c/ni. Translator: require `debt > 0` and `debt_lag > 0`.
No financials exclusion in OSAP (keep them; flag the bank-debt deviation).

## 6. Predicted sign (SignalDoc)
`Sign = -1.0`: heavy debt issuers have low future returns. Score = -CompositeDebtIssuance.
Cat.Form continuous, Cat.Data Accounting, Cat.Economic external financing; EW,
Portfolio Period 12, Start Month 6, LS Quantile 0.333 (top 3 vs bottom 3 deciles,
Table 5B); Acronym2 DebtFinC.

## 7. The mass-point question
- Do-nothing firm (debt unchanged over 5 years) gives log change exactly 0 only if
  the dollar debt is unchanged; unrounded SF1 USD makes that rare (guess under 1%;
  preflight to measure). Not a structural mass point.
- The real mass point is ZERO DEBT: debt exact-zero is 11.1% (1998-12), 12.8% (1999-12),
  11.6% (2008), 4.2% (2020), 4.4% (2021) of the universe ART (SF1 fills 0 where not
  reported: a manufactured 0). Those firms are excluded at either end. Consequence:
  firms going from 0 debt to positive debt (true large issuers) and positive to 0
  (full repayers) are dropped, so the tails are truncated on both sides; coverage is
  below debt's 97-100% level coverage by the zero share at either end (preflight
  measures it). Not a tie problem (ties are tiny); a selection effect.
- Ties: average (percentile) rank.

## 8. History needed
Five years of level history. SF1 ART/ARQ begin with calendardate 1997Q4 (levels
~99.9% populated); the first same-period pair is 1997Q4 vs 2002Q4 (datekey about
2003-01..03), so the first signal month is about 2003-02 and months 1999-01..2002-12
(48 of 276) are empty: coverage is 0 there. The Stage 1 coverage bar (40%) and the
LS-months floor must be read against ~228 signal months.

## 9. OSAP metadata
CompositeDebtIssuance (Acronym2 DebtFinC); Lyandres, Sun and Zhang (2008, RFS),
"Composite debt issuance"; Key Table 5B; port sort CAPM alpha t = 8.59 (return
0.523); sample 1970-2005; Signal Rep Quality 1_good; Predictability 1_clear;
GScholarCites202509 = 663. Detailed Definition: log of long-term debt (dltt) plus
debt in current liabilities (dlc) minus log of the same variable 5 years ago.
Source `Signals/pyCode/Predictors/CompositeDebtIssuance.py` (in tree.txt).

## 10. Proposed Sharadar mappings and deviations
| item | mapping | deviation |
|---|---|---|
| dltt + dlc | SF1.debt (ART), `> 0` at both ends | lease-inclusive from FY2019 (ASC 842 break, 5-year confound through 2023); banks' repo/borrowings included |
| 5-year lag | `fundamentals_yoy(['debt'], years=5)` | aligned by report period, not calendar month 60 |
| timing | ART filing at datekey | more current than OSAP's datadate+6m annual |
| zero debt | excluded (debt = 0 -> NaN) | OSAP: log(0) = -inf/NaN |
| universe / ranks | harness, within sector | OSAP EW decile sort, no size screen |
Fields all in `field_map_index.yaml`; checker needs only `dltt_plus_dlc` (already verified 2026-09-30).
