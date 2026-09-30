# ChInv — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: FEASIBLE (both inputs mapped, verified 2026-09-30)
Checked against `osap_source/field_map_index.yaml` (detail for invt in `field_map.yaml` l.764-781).

| OSAP var | field_map key | Sharadar | status | role |
|---|---|---|---|---|
| invt | compustat.invt | SF1.inventory | mapped, verified 2026-09-30 | level at t and t-12m (numerator) |
| at | compustat.at | SF1.assets | mapped, verified 2026-09-30 | level at t and t-12m (denominator) |

- Both are balance-sheet LEVELS; ART == ARQ within $1 on 99.69% of pairs. No flow item,
  so no TTM smear and no `dimension=ARQ`. Keep ART default. The ~50% populated
  1998Q1-Q3 ART TTM flows do not matter (no flow input); levels are ~99.9% populated.
- invt is in OSAP `zero_fill_vars` (upstream_CompustatAnnual.py l.139-144). Sharadar
  reports 0 for non-inventory firms (exact-zero 45.6% ART of non-null), the same value
  OSAP's fill produces, and null is 0.04%. No unavailable term, no zero-fill deviation:
  not `approx`. The mass point is real and is the main risk (section 7).
- at is NOT zero-filled by OSAP; rows with null at (or prcc_c, ni) are dropped
  upstream. Sharadar assets null 0.05%; exact-zero 0.01% (data errors).
- No unavailable data (no IBES, segments, ppegt, pensions, xad, emp, ob).

## 2. Variables by exact source name (predictor.py)
`m_aCompustat` columns gvkey, permno, time_avail_m, `at`, `invt`. Upstream
(FUNDA; consol C, INDL, STD, USD): rows with null at, prcc_c or ni dropped; invt
null -> 0; `time_avail_m = datadate + 6 months`, each annual row repeated over 12
months (offsets 0-11), de-duplicated on (permno, time_avail_m), keep last datadate.

## 3. Formula
12-month change in inventory over average total assets (Thomas-Zhang 2002, Delta Invent):

    invt_l12 = groupby(permno).shift(12);  at_l12 = groupby(permno).shift(12)
    ChInv = (invt - invt_l12) / ((at + at_l12) / 2)

`shift(12)` is 12 monthly ROWS; with annual data forward-filled, that is the prior
fiscal year's row (a panel gap misaligns it; ChInv is constant within a fiscal year
and refreshes once a year). Stata legacy: `(invt-l12.invt)/((at+l12.at)/2)`, same.
Sharadar form:
`y = ctx.fundamentals_yoy(["inventory","assets"])`;
`ChInv = (inventory - inventory_lag) / ((assets + assets_lag)/2)`; score = -ChInv.

## 4. Timing and lag convention
- OSAP: datadate + 6m availability, ChInv changes once a year. Sharadar ART as-of
  datekey: latest filed level (refreshes quarterly, up to ~9 months fresher than
  OSAP); the change spans the latest 4 quarters, not the fiscal year. ART-as-of-filing
  therefore gives a rolling, more current signal with no 6-month wait; it does not
  leak (datekey <= signal date).
- Year-ago level: use `ctx.fundamentals_yoy` (aligned by reportperiod within 45 days,
  NaN when no year-ago period or the latest filing is stale). Do NOT use
  `fundamentals(lag_months=12)` (wrong quarter ~15% of the time; a stale filing at
  both dates yields a false exact-zero change, which would inflate the mass point).
- invt null handling: fill null inventory with 0 ONLY where the filing exists (row
  has reportperiod / reportperiod_lag); never fill the NaN that `fundamentals_yoy`
  returns for a missing year-ago period, or unscored names become 0-change names.
- Flow items: none. ASC 842 and fxusd: irrelevant (ratio of two reporting-currency levels).

## 5. Filters
predictor.py has no sample filter beyond the upstream at/prcc_c/ni non-null. SignalDoc
`Filter` is empty; `Quantile Filter` empty. No factor-level filter; the harness
universe applies. Guard: average assets > 0, else NaN.

## 6. Predicted sign (SignalDoc)
`Sign = -1.0`: high inventory growth predicts low returns. Score = -ChInv (long low/
negative change). Cat.Signal Predictor; Cat.Economic `investment alt`; Cat.Form
continuous; Cat.Data Accounting; Thomas and Zhang 2002 (RAS); sample 1970-1997;
Predictability in OP 1_clear; Signal Rep Quality 1_good; Key Table "1 Delta Invent",
"port sort size adjusted no LS", "t>2.6 in port sort" (T-stats missing in the paper).

## 7. The mass-point question
A do-nothing firm (inventory unchanged year on year) gets exactly 0. Overwhelmingly
these are firms with invt = 0 in both years (vendor/OSAP zero-fill, services,
software, banks, REITs): the 12-month change is exactly 0 for 34.7% / 34.1% / 42.5%
of universe names in 1999 / 2008 / 2020 (measured, field_map invt note). Genuine
inventory holders with an exactly unchanged balance are a negligible subset. Hence
~35-43% of the universe ties at one value, and within service-heavy sectors (Financial
Services, Real Estate, Technology software) the tied share is far higher, so the
sector-relative rank is a near-constant for most names there.
- Ties: average rank at the mass point (a flat 0.5-ish block in the middle of the
  cross-section); the tails are the non-zero changers, so deciles 1 and 10 stay
  populated but D4-D7 collapse to the tied block. Preflight must report the modal-value
  share (expect ~0.35-0.43, above any typical mass-point limit) and the sector-by-sector
  share; a sector-month with <10 scored names falls back to the cross-section rank.
- Do not break ties with noise or a secondary key. A preflight mass-point failure is
  a measured, logged outcome (`preflight_failed` / frontier row), not a reason to alter
  the construction. Do not drop the zero-inventory names to "fix" it: that changes the
  population relative to OSAP (OSAP keeps them).
- at is continuous, so no mass point in the denominator.

## 8. History needed
`history_months = 12` plus filing lag (year-ago report period). Snapshot ART begins
1997Q4 in breadth: first signal months (1999-01..) rest on year-ago filings from 1998
as-of dates; first 1-3 months may be thin. preflight reports first-month coverage.
Inventory levels are ~99.9% populated from 1998Q1 (unlike TTM flows).

## 9. OSAP metadata
Acronym ChInv; Thomas and Zhang 2002; Cat.Economic investment alt; Sign -1; LS
quantile 0.1; EW; start month 6; portfolio period 12; Filter none. Source
`Signals/pyCode/Predictors/ChInv.py` (legacy `ChInv.do`) at
b4e911e69678a7424f318617a61d813f54183123. Output `ChInv.csv [permno, yyyymm, ChInv]`.
Cached here: predictor.py, legacy.do, signaldoc_row.csv, upstream_CompustatAnnual.py,
upstream_SignalMasterTable.py. SignalDoc Detailed Definition: "12 month change in
inventory (invt) divided by average total assets". Sibling ChInvIA (industry-adjusted)
is a separate predictor.

## 10. Proposed Sharadar mappings and deviations
1. invt -> SF1.inventory (ART); null -> 0 only where the filing exists (matches OSAP fill).
2. at -> SF1.assets (ART); average of t and year-ago, guard > 0; null -> NaN (OSAP drops).
3. Year-ago via `fundamentals_yoy` (report-period aligned), not shift(12) rows.
4. Score = -ChInv; `history_months = 12`; `family = None` until Phase C.
Deviations: rolling quarterly refresh vs OSAP annual; 4-quarter span vs fiscal year;
no portfolio filter. Fields not in field_map: none.
