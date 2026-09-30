# DebtIssuance — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: INFEASIBLE (recommend `infeasible`; not a zero-fill case)
Checked against `field_map_index.yaml` / `field_map.yaml` (`compustat.dltis`, `net_not_gross_financing_flows`).

| OSAP var | field_map key | Sharadar | status | note |
|---|---|---|---|---|
| `dltis` (Compustat annual gross long-term debt issuance) | compustat.dltis | SF1 `ncfdebt` | approx | `ncfdebt` = NET debt flow (issuance - repayment) INCLUDING the short-term / CP net change; map note: "not usable for one gross side" |
| `ceq` | compustat.ceq | SF1 `equity` | approx (verified-with-deviation 2026-09-30) | parent equity incl. preferred |
| `mve_permco` | crsp.mve_permco | `ctx.universe["mkt_cap_usd"]` (DAILY.marketcap) | approx (verified 2026-09-30) | company level |
| `shrcd` | crsp.shrcd | universe (TICKERS.category) | approx | harness-side |

- The signal is a one-sided test on the GROSS item: `dltis > 0`. `ncfdebt > 0` is a different
  event (net borrower over the year): a firm that issues 100 and repays 120 is 1 in OSAP and
  0 here; a firm whose only activity is a net commercial-paper increase is 0 in OSAP and 1
  here. SF1 has no gross issuance line. OSAP does NOT zero-fill `dltis` (absent from
  `zero_fill_vars` in `upstream_CompustatAnnual.py`), so the zero-fill escape does not apply.
  `ncfdebt` measured pooled ART 1999-2025: null 6.96%, exact-zero 15.38% of non-null, >0
  39.6%, <0 45.0% (field_map). The OSAP-side share of `dltis > 0` cannot be measured here.
- Net debt flow is the concept of NetDebtFinance (cached as its own predictor); a
  thresholded copy under the DebtIssuance name would be a near-match substitution. Not done.
- Independently, the signal is DISCRETE (two values); see section 7.
- No IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob or ppegt input.

## 2. Variables (predictor.py)
`m_aCompustat`: permno, time_avail_m, `ceq`, `dltis`. `SignalMasterTable`: `mve_permco`, `shrcd`.
Upstream: FUNDA annual (INDL, STD, USD, consol C), rows with null at/prcc_c/ni dropped;
`time_avail_m = datadate + 6 months`, replicated for 12 monthly offsets.

## 3. Formula
```
BM = log(ceq / mve_permco)
DebtIssuance = ((dltis > 0) & dltis.notna()).astype(int)     # NaN dltis -> 0, NOT missing
DebtIssuance = NaN if (shrcd > 11) or BM is NaN
```
Consequences: a missing `dltis` becomes 0 (OSAP's zeros include non-reporters). `ceq < 0` ->
log NaN -> excluded; `ceq == 0` -> BM = -inf (not NaN) -> kept. Only observations with `ceq > 0`
(and a market cap) carry a value.

## 4. Timing / lag
OSAP: annual flow at fiscal year end, usable datadate + 6 months, held 12 months (6-17 months
stale). Sharadar ART `ncfdebt` is a TTM (rolling 4-quarter) flow refreshed quarterly at the
filing date; ART == sum of 4 ARQ within 1% on 99.63% of pairs, ARY == ART at FYE on 99.97%
(field_map). No year-over-year difference is taken, so there is no smear; the TTM window just
shifts quarterly (the indicator can flip at each 10-Q, OSAP flips once a year). ART coverage of
TTM flows is ~50% in 1998Q1-Q3 (snapshot start), so Jan-Mar 1999 signals are thin.

## 5. Filters
SignalDoc Filter blank; exclusion rule above is the predictor's own (share code > 11, missing BM).
Harness universe replaces the share-code test.

## 6. Predicted sign
`Sign = -1.0`: debt issuers earn lower returns (long non-issuers; OSAP evidence t = 2.19 FF3 alpha
on the long portfolio, EW, Table 4A).

## 7. Mass-point question
Two values only (0/1). Every firm is at one of two points: a do-nothing firm (no issuance)
produces 0; the zero share is large (majority or near-majority of firm-years; cannot be
measured without gross `dltis`; with `ncfdebt > 0` the zero class is ~60% of non-null ties). Deciles collapse by
construction (at most two distinct rank values, within-sector ranks likewise): this would fail
the preflight mass-point check irrespective of the mapping. Ties: average rank; D10 - D1 is the
1-group minus 0-group spread.

## 8. History needed
None beyond one TTM filing; SF1 ART from 1997Q4 covers the first decision month (1999-01) only
partially (see section 4). No `history_months`.

## 9. OSAP metadata
Spiess and Affleck-Graves (1999), JFE; Cat.Data Accounting; Cat.Economic external financing;
`Cat.Form` discrete; sample 1975-1989; Acronym2 DebtIssuance; Portfolio Period 1, Start Month 6;
EW; Test "long less risk-free ff3 alpha"; `Predictability in OP` 2_likely, `Signal Rep Quality` 2_fair.
SignalDoc note: OP uses Investment Dealers' Digest, OSAP uses Compustat.

## 10. Proposed Sharadar mappings
None recommended. If the owner overrides: `ncfdebt` (ART) > 0 gated by `equity > 0` and
`mkt_cap_usd > 0`, NaN `ncfdebt` -> 0 as OSAP does; label it "net-debt-flow indicator, not
OSAP DebtIssuance". Fields not in the map: a gross `dltis` (none exists in SF1).
Frontier row: `infeasible` — "gross dltis not published; ncfdebt is net incl. short-term".
