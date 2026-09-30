# RoE — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: APPROX (constructible; declared deviations)
Checked against `osap_source/field_map_index.yaml`. No IBES, options, 13F, patents, segments,
ratings, pensions, xad, emp, ob or ppegt. OSAP zero-fills neither input.

| OSAP var | field_map key | Sharadar | status | note |
|---|---|---|---|---|
| ni | compustat.ni | SF1.netinc (ART) | mapped, verified 2026-09-30 | parent NI after NCI, before preferred dividends, includes discontinued ops; this is Compustat `ni`, NOT `ib` (the `ib = netinc + netincdis` trap does not apply: RoE reads `ni`) |
| ceq | compustat.ceq | SF1.equity (ART) | approx, verified-with-deviation | parent equity INCLUDING preferred (ceq excludes it; no pstk in SF1; ruling book_equity_preferred_terms: approx, not infeasible) |

Why approx: (a) equity includes preferred, so RoE is slightly understated for preferred issuers;
(b) OSAP uses fiscal-year annual ni / year-end ceq with a 6-month availability lag; here TTM ni
over the latest-filing equity, as known at the signal date. Recommend: **approx** (feasible).

## 2. Variables by exact source name (predictor.py)
`m_aCompustat.parquet`: gvkey, permno, time_avail_m, ni, ceq. Upstream
(`upstream_CompustatAnnual.py`, cached): annual Compustat rows are kept only if `at`, `prcc_c`
and `ni` are all non-missing (line 86); `time_avail_m = datadate month + 6`, each annual row then
replicated for 12 months (offset 0..11), duplicates resolved to the latest datadate.

## 3. Formula
    df = groupby(permno, time_avail_m).first()      # duplicate rows: keep first
    RoE = ni / ceq ;  dropna(RoE)

Key line: `df["RoE"] = df["ni"] / df["ceq"]`. No positivity guard: ceq < 0 gives a sign-flipped
ratio (a loss-maker scores positive), ceq == 0 gives +/-inf which `dropna` does NOT drop.
Sharadar form (translator): `netinc / equity.where(equity > 0)`, both from `ctx.fundamentals`
(ART, same filing). Both fields are in reporting currency, so the ratio is currency-free
(no fxusd gate needed, no market term).

## 4. Timing / lag convention
OSAP: fiscal-year ni and ceq, available 6 months after datadate, held 12 months (data up to
18 months stale at the end of the hold). Signal dated month t, portfolio held t+1.
Sharadar: latest ART filing with datekey <= signal date (median lag 44 days, p95 101 days),
max age 15 months (config). ART-as-of-filing is fresher than OSAP, so the horizon of the
information differs, not the concept. FLOW numerator: `netinc` ART is a TTM sum (equals the
rolling-4 ARQ sum), a level at each filing, not a single quarter. Do NOT use
`dimension=ARQ` (a quarter of income over equity would be quarter-sized); ART default is
right. No year-over-year difference enters, so no TTM smear.

## 5. Filters
predictor.py: none. SignalDoc `Filter`: `abs(prc)>5` (not reproduced; harness universe is
price >= $1, US common, relative cap/dollar-volume screens). Quantile Filter blank. The
OSAP annual-row requirement (at, prcc_c, ni non-missing) is not reproduced beyond ni/equity
non-null.

## 6. Predicted sign (SignalDoc)
`Sign = +1.0`: high return on equity -> high returns (Haugen and Baker 1996, Table 1;
Evidence "t=4.5 in mv reg nonstandard"; OP reports mean regression coefficient across 90
regressions). `ascending=True`. Cat.Economic profitability; Cat.Form continuous; Cat.Data
Accounting; sample 1979-1993; EW, LS Quantile 0.2, Portfolio Period 12, Start Month 6.

## 7. The mass-point question
Do-nothing firm: continuous ratio, no constant. Measured on the harness universe at 92 of the
276 decision months (every third month, 1998-12-31 .. 2021-09-30; universe 1,739-2,867 names):
- modal share of scored names 0.06% mean (max 0.12%); distinct values == n; 10 qcut bins.
- exact ni == 0: 0.01% of non-null names (max 0.09%).
- equity <= 0: 3.2% of equity-non-null names (range 1.7%-6.9%); those are nulled by the
  positivity guard (OSAP would keep them sign-flipped; zero-equity rows 0.01% of non-null).
- |RoE| > 5 (tiny positive equity): 0.5% of scored names (max 1.2%); OSAP does not trim.
Tie handling: none needed; average rank. Not a mass-point candidate.
Coverage (ni and equity > 0, of universe): 93.6% mean (min 55.9% at 1998-12-31 when ART
ni is 57% populated, 89.6% at 1999-03-31, 83-95% through 1999, 94.7% median overall).

## 8. History needed
One filing. Snapshot starts 1998-01; ni null 40.7% ART for reportperiod 1998, so the first
decision month (1998-12-31 signal) is thin (56% coverage) and the rest are >= 83%.
No `history_months` (no price window).

## 9. OSAP metadata
Acronym RoE (Acronym2 RoE); Haugen and Baker 1996, JFE ("Commonality in the determinants of
expected stock returns"); Key Table "1 return on equity"; Test "mv reg nonstandard"; Signal
Rep Quality 2_fair; Predictability 2_likely; GScholarCites202509 1647. Detailed Definition:
net income (ni) over book value of equity (ceq); exclude if price less than 5. Source
`Signals/pyCode/Predictors/RoE.py` (in tree.txt, not a Placebo).

## 10. Overlap with the v0 composite (factual, from factors/composite.py)
- Profitability leg = (revenue - cor - (sgna + rnd + intexp)) / equity, ART, equity > 0.
  RoE = netinc / equity, ART. Same denominator (SF1.equity, same filing); numerators differ
  (operating profit before tax vs after-tax net income to parent). Measured cross-sectional
  Spearman of raw RoE with the raw Profitability leg: mean 0.71 (range 0.62-0.81, 92 months).
- Value leg (equity / mkt cap): mean -0.34. Size leg (log mkt cap): mean 0.28. Momentum: 0.09.
Cat.Economic (profitability) matches the Profitability seed family's label.

## 11. Proposed Sharadar mappings and deviations
| item | mapping | deviation |
|---|---|---|
| ni | SF1.netinc, ART | TTM as of filing vs fiscal-year; parent NI (after NCI) |
| ceq | SF1.equity, ART | includes preferred; negative/zero equity nulled (OSAP keeps, sign-flipped / inf) |
| Filter abs(prc)>5 | not reproduced | looser; universe price >= $1 |
| duplicates keep-first | n/a | one SF1 row per ID as-of |
Fields all in `field_map_index.yaml`; nothing new to check (netinc, equity verified 2026-09-30).
