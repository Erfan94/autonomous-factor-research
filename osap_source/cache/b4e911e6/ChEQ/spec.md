# ChEQ — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: APPROX (constructible; one deviation)
Checked against `osap_source/field_map_index.yaml` (detail: `field_map.yaml` ceq).

| OSAP var | field_map key | Sharadar | status | role |
|---|---|---|---|---|
| ceq | compustat.ceq | SF1.equity | approx, verified_on 2026-09-30 (verified-with-deviation) | level at t and t-12m |

- **The one deviation**: SF1.equity is parent equity INCLUDING preferred;
  Compustat `ceq` EXCLUDES preferred (pstk/pstkl/pstkrv/pstkq are unavailable in
  SF1). Preferred here only adjusts the book-equity level, so per ruling
  `book_equity_preferred_terms` (events.jsonl 2026-09-30) the verdict is
  **approx, not infeasible**. Effect: growth of common equity is proxied by
  growth of total parent equity; differs only for the few preferred issuers.
- No other input: predictor.py reads only `ceq`; no flows, no zero-filled term.
- Measured (field_map): equity null 0.05% ART / 0.04% ARQ /
  0.04% ARY; exact-zero 0.01% of non-null (data errors; excluded by `> 0`);
  universe ART coverage 98.7% (1998-12-31), 97.6% (1999-12-31), 99.8% (2008),
  100% (2020-21). Negative equity is real (all-ART p10 = -$4.4M): those names
  are excluded by the positivity filter, so ChEQ coverage is below the equity
  coverage by the negative-equity share (preflight measures it).

## 2. Variables by exact source name
`m_aCompustat` columns `gvkey, permno, time_avail_m, ceq` (predictor.py).
Upstream (`upstream_CompustatAnnual.py`, cached here): FUNDA, annual rows with
null `at`, `prcc_c` or `ni` DROPPED; ceq is NOT zero-filled (it is not in
`zero_fill_vars`); `time_avail_m = datadate + 6 months`; each annual record is
replicated 12 times with offsets 0-11; de-duplicated on (permno, time_avail_m),
keep last datadate. `predictor.py` also de-duplicates (permno, time_avail_m)
keep first. Sharadar: `SF1.equity` (raw USD).

## 3. Formula
Ratio (not a percent change) of this year's book equity to last year's:

    df["l12_ceq"] = df.groupby("permno")["ceq"].shift(12)
    df["ChEQ"] = np.where((df.ceq > 0) & (df.l12_ceq > 0), df.ceq / df.l12_ceq, np.nan)

`shift(12)` is 12 monthly ROWS; with the annual expansion this is the prior
fiscal year's value, but a skipped fiscal-year record misaligns it (the row 12
back is then two years back or absent). ChEQ = 1 means no change. The code docstring says "sustainable growth"; the SignalDoc definition
(book equity growth, Lockwood-Prombutr SUSG) and code agree on the ratio.
Sharadar form: `eq = ctx.fundamentals_yoy(["equity"])` -> `equity` and
`equity_lag`; `ChEQ = equity / equity_lag` where both > 0, else NaN; the score
is `-ChEQ` (sign -1; section 6).

## 4. Timing and lag convention
- OSAP: fiscal-year ceq available datadate + 6 months, held constant for 12
  months, so the signal steps once a year (6-17 months old). Sharadar ART/ARQ
  as-of datekey: the latest filing known at the signal, refreshed every
  quarter, usually 0-3 months old. The 6-month lag is not reproduced; the
  Sharadar signal is fresher and is a rolling 4-quarter growth, not a
  fiscal-year one. More changes of value month to month than OSAP.
- Year-ago level: use `ctx.fundamentals_yoy(["equity"])` (aligns by REPORT
  PERIOD within 45 days), NOT `fundamentals(lag_months=12)` (wrong quarter about
  15% of the time). Stale filings yield NaN rather than a zero change.
- ART-as-of-filing changes: equity is a LEVEL (ART == ARQ equity on the same
  reportperiod, 98.9% of 740,031 pairs within $1; ARY identical for AAPL). So
  there is NO flow and NO TTM smear; `dimension=ARQ` is NOT needed. Keep the ART
  default. The alternative `dimension="ARY"` mirrors OSAP's annual cadence
  (yearly refresh, prior fiscal year) but is staler and, at the snapshot start,
  thinner; a translator choice to state in the docstring, ART recommended.
- **Early-window thinness**: SF1 holds calendardate from 1997Q4 only, so the
  year-ago period for a latest period 1998Q1-Q3 (1997Q1-Q3) is NOT in the
  snapshot. Signal months in 1999 whose latest filing is 1998Q1-Q3 (Jan-Feb
  1999 for December FYE; later for other fiscal year-ends) yield NaN. Coverage
  becomes broad once filings for 1998Q4 (year-ago 1997Q4) or 1999Q1 (year-ago
  1998Q1) are known, about March-May 1999. Preflight must report the first 3-5
  months' coverage; do not back-fill. (Level coverage itself is ~99.9% and
  unaffected; the ~50% population of ART TTM flows in 1998Q1-Q3 is irrelevant
  here because ChEQ uses no flow.)
- fxusd: a same-filer ratio cancels the reporting currency (fxusd != 1 on
  0.00-0.06% of universe members); no gate needed.

## 5. Filters
predictor.py: positive equity this year AND a year ago (the only filter). SignalDoc
`Filter` is empty. Add none in the factor (the harness universe applies price
>= $1 and the cap/dollar-volume band). Upstream Compustat row filter (non-null
at, prcc_c, ni) is not reproduced: a deviation in sample, not in value.

## 6. Predicted sign (SignalDoc)
`Sign = -1.0`: high book-equity growth predicts low returns (score = -ChEQ;
long low growth). Lockwood and Prombutr 2010 (SignalDoc Journal `JFR`), Table 4A SUSG, port sort; EW; LS quantile 0.2; t = 5.38 in the
paper's EW sort (SignalDoc "Evidence Summary"); Predictability in OP 1_clear;
Signal Rep Quality 1_good; Cat.Form continuous; Cat.Data Accounting;
Cat.Economic `investment`; Acronym2 BEgrowth.

## 7. The mass-point question
- A do-nothing firm (equity unchanged year on year) produces exactly
  `ChEQ = 1.0`. True inactivity is nearly nonexistent: equity moves with every
  quarter of earnings, dividends, buybacks and option issuance. Expect exact
  ratio 1.0 on a tiny fraction (well under 1%; dormant shells, rounding of
  reported equity); measured modal-value share is reported by preflight.
  Filing-staleness ties are removed by `fundamentals_yoy` (NaN, not 1.0).
- No zero-fill: OSAP does not zero-fill ceq; missing or non-positive equity ->
  NaN. Do NOT fill negative-equity names with 0 or 1 (would create a large
  mass). The non-positive exclusion removes the negative-equity share of names
  (larger among small caps and post-buyback large caps).
- Right-skewed ratio (prior equity near zero gives huge values); ranks are
  unaffected, no winsorising, raw ratio not log (monotone).
- Ties: average rank in the harness.

## 8. History needed
Not a return window (no history_months); one year-ago period via
fundamentals_yoy. SF1 starts 1997Q4: first broad coverage ~March-May 1999.

## 9. OSAP metadata
Acronym ChEQ; Lockwood and Prombutr 2010, JFR; sample 1964-2007; Start Month 6;
Portfolio Period 12; EW; LS Quantile 0.2; Sign -1; T-Stat 5.38; Return 0.8;
GScholarCites 111. Source `Signals/pyCode/Predictors/ChEQ.py` at
b4e911e69678a7424f318617a61d813f54183123 (in tree.txt line 535). Cached here:
predictor.py, signaldoc_row.csv, upstream_CompustatAnnual.py,
upstream_save_standardized.py. Output `ChEQ.csv [permno, yyyymm, ChEQ]`.
## 10. Proposed Sharadar mappings and deviations
1. ceq -> SF1.equity (approx: includes preferred; ruling book_equity_preferred_terms).
2. Year-ago via `ctx.fundamentals_yoy(["equity"])`, ART default; no dimension=ARQ.
3. ChEQ = equity / equity_lag if both > 0 else NaN; score = -ChEQ (ascending False).
4. Not reproduced: datadate+6m lag and annual step; upstream at/prcc_c/ni row filter.
5. Early-1999 NaNs where year-ago period predates SF1 1997Q4.
Fields not in field_map: none.
