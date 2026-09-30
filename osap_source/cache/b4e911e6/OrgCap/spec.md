# OrgCap — Organizational capital, industry-standardised (Eisfeldt and Papanikolaou 2013 JF, Table 4A.1)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/ZZ1_OrgCap_OrgCapNoAdj.py` (cached
`predictor.py`, `upstream_GNPDeflator.py`, `upstream_CompustatAnnual.py`, `upstream_SignalMasterTable.py`,
`upstream_sicff.py`). The SignalDoc row (Predictor) is OrgCap (industry-adjusted); the script also emits the
placebo OrgCapNoAdj. DATA_SHA 198b281de1a0.

## 1. Data availability — VERDICT: approx (constructible; six declared deviations, no unavailable input)

| input (OSAP) | field_map key | Sharadar | status |
|---|---|---|---|
| `xsga` (annual SG&A, Compustat INCLUDES R&D, excludes D&A) | `compustat.xsga` (+`compustat.xrd`) | SF1 `sgna` + `rnd`, ARY | sgna approx, rnd mapped (verified 2026-09-30) |
| `at` | `compustat.at` | SF1 `assets` | mapped, verified 2026-09-30 |
| `datadate` (keep month 12 only) | `compustat.datadate` | SF1 `reportperiod` month == 12 | mapped |
| `sic` / `sicCRSP` (FF17, financials screen) | `crsp.siccd`, `compustat.sic` | TICKERS.siccode (CURRENT) | approx |
| `gnpdefl` (FRED GNPCTPI, quarterly, +3-month availability) | none | none in any held table | unavailable, see below |

- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt. OSAP's own `xsga.fillna(0)` is the only fill;
  Sharadar `sgna`/`rnd` are nearly always present (null 0.06%/0.07% ARY; rnd == 0 on 63% = "no R&D line", fine in sgna + rnd).
- Deflator: the GNP deflator is external macro data, not in the snapshot. Construction check: it is applied to the
  monthly row BEFORE the recursion (`xsga / gnpdefl`, per time_avail_m), so every vintage carries its own month's
  deflator. All firms kept are December-FYE, so at a given signal month EVERY firm shares the same deflator path
  (d_t, d_t-12, ...): a common weighting of vintages, not firm-specific. It is not a pure month-constant scalar on the
  final value (vintages weighted ~inflation^k), so not strictly rank-invariant; nearly so. Measured: within-universe Spearman of the final industry-z between the
  nominal recursion (no deflator) and the recursion deflated with FRED GNPCTPI (signal-month-indexed proxy, OSAP's 3-month availability
  convention) = 0.9988..1.0000 (mean 0.999) over 23 December probe months 1998-12..2020-12 (universe 1,740..2,674
  names). Verdict: omit the deflator, declared approx (the rank effect is not material).
- Additional approx drivers: (a) xsga = sgna + rnd leaves D&A embedded where the filer reports it in SG&A (Compustat
  excludes D&A; ~36% of non-financial universe-proxy rows embed >=90% of D&A per field_map); (b) current SIC feeds
  the signal VALUE (known_trap `current_sic_signal_values`, RULING 2026-09-30: use harness.industry, declared
  deviation, D3); (c) history truncated (below).

## 2. Variables (exact source names)

`xsga`, `at`, `datadate`, `sic` (m_aCompustat); `gnpdefl` (GNPdefl); `sicCRSP`, `shrcd`, `exchcd` (SignalMasterTable);
`time_avail_m`, `permno`.

## 3. Formula

Per firm, on rows whose current annual `datadate` is in December (annual value replicated monthly, datadate + 6 months):
```
xsga      = xsga.fillna(0) / gnpdefl                   # deflator by time_avail_m
y[t]      = 4*xsga[t]                   for the firm's first 12 monthly rows
y[t]      = 0.85*y[t-12] + xsga[t]      thereafter     # = sum_k 0.85^k xsga_{t-12k} + init remainder; NaN forever after a missing-month gap
OrgCapNoAdj = y / at   (at == 0 -> NaN);   OrgCapNoAdj == 0 -> NaN
temp      = winsorize(OrgCapNoAdj, 1%/99%) by time_avail_m
FF17 = sicff(sicCRSP, 17); drop missing FF17 and sicCRSP == 9999
OrgCap    = (temp - mean_FF17,t) / std_FF17,t   # stats computed over ALL firms incl. financials, THEN financials (6000-6999) dropped
```
Words: a depreciating (15%/yr) stock of 4x initial SG&A then accumulated deflated SG&A, scaled by assets, z-scored within
FF17 industry each month. Key lines: `y[i] = a * y[i-period] + xsga[i]` (period 12, a = 0.85), `init = 4*xsga`.
Harness form: annual series via `ctx.fundamentals_history(["sgna","rnd","assets"], n, dimension="ARY")` on
`ctx.market_context()`; per firm take consecutive December fiscal years ending at the latest one; fold
`y = 4*x0; y = 0.85*y + x_k` (nominal); `/ assets`; 0 -> NaN; industry stats on the market cross-section via
`harness.industry.ff17` (+ a group std; `group_demean` only demeans, so a /std step is new: group mean AND std over
the same FF17 groups, needs >= 2 members); reindex to `ctx.ids`. Winsorise 1/99 per month on the market cross-section
INSIDE the construction, BEFORE the industry mean/std (as OSAP and my probe do); the harness's later universe clip does not replace it.

## 4. Timing / lag
- OSAP: new fiscal year enters at datadate + 6 months, held 12 months (latest datadate wins); non-December firms drop
  out every month (datadate month != 12).
- ARY-as-of-filing: the December 10-K is known ~2-3 months after year-end, so the signal is 3-4 months fresher and
  updates once a year per firm; between year-end and the filing the previous fiscal year is used. Flow item (SG&A is a
  flow) but the recursion sums annual flows, so use ARY (annual), not ART/ARQ: a TTM series would double count the
  overlap and ARQ smears. `dimension="ARY"` required (sanctioned per-factor deviation).
- Recursion order: monthly rows lag 12 = previous fiscal year, so consecutive December fiscal years are needed. A
  missing year in Sharadar ARY (not a data gap in Compustat) breaks OSAP's chain (NaN thereafter).

## 5. Filters
OSAP code: December FYE only; `sicCRSP` non-missing and != 9999; non-financials (`sicCRSP < 6000 or >= 7000`);
`gnpdefl` inner-merged; SignalDoc Filter blank. Non-December firms, financials and missing-SIC firms are NaN here.

## 6. Predicted sign

SignalDoc `Sign = +1.0` (-> `ascending=True`: high organizational capital long). `Cat.Economic` = R&D; `Cat.Data` =
Accounting; port sort, LS quantile 0.2, VW, sample 1970-2008; OSAP t = 2.85; Predictability in OP `1_clear`.

## 7. The mass-point question

A do-nothing firm (constant xsga) yields a stock y -> x/0.15; a firm with zero sgna + rnd in all years has OrgCapNoAdj == 0
-> NaN (dropped). Measured on the harness universe at the 23 December probes: modal share of the final z-score
0.19%..0.65% (mean 0.36%): no mass point. Tie handling: none needed; harness average-ranks.

## 8. History needed, and what was measured

- Coverage (non-null final OrgCap / harness universe, 23 December probe months 1998-12..2020-12): mean 49.8%
  (min 42.4% 1999-12, max 54.9% 2020-12) under "restart the chain at a year gap". Excluded: non-December FYE mean
  25.6% of universe (20.5%..30.2%), no ARY row 0.8%..10.8% (10.8% at 1999-12, ~1-3% after 2001), financials/missing
  SIC/zero for the rest. Under OSAP's "NaN after a gap" rule coverage is 43.7% mean (min 41.5% at 1999-12): ARY
  year gaps bind on 0.9%..10.7% of the universe (mean 7.5%). Stage 1 coverage bar is 40%: thin margin at 1999 only.
- Chain length (consecutive December fiscal years, median over names scored): 1 at 1998-12, 2 at 1999-12, 3 at 2000-12,
  6 at 2003-12, 11 at 2008-12, 13 at 2012-12 and 2019-12. Names with <= 3 years: 88% (1998-12), 82% (1999-12), 64%
  (2000-12), 18% (2003-12), ~13-23% thereafter (new listings).
- The snapshot starts 1997Q4 (first usable fiscal year FY1997), so the OSAP initialisation (4x the firm's first
  Compustat year, often 1950s-1980s) is replaced by 4x the first year seen: the truncated chain carries 0.85^n of a
  mis-scaled initial term. Sensitivity measured by recomputing with the chain restarted 7 years before the end vs the
  full available chain: Spearman of the final industry-z 0.994..1.000 (mean 0.997) across the 23 probes; identical
  (chains <= 7 years) through 2002. So the init matters little for rank, but early months (1999-2002) are essentially
  `SG&A+R&D / assets` of 1-4 years: a different signal in character from the published 40-year stock. Report this.
- Window: scoreable from 1998-12; rebalance.min_months 120 (LS months of 276) is met. The filing-date floor binds at 1997-12.

## 9. OSAP metadata

Acronym OrgCap; Eisfeldt and Papanikolaou, JF 2013; Key Table 4A.1; Portfolio Period 12, Start Month 6; LS Quantile
0.2, VW; GScholar cites 1,211; LongDescription: recursive, xsga 0 if missing, init 4*xsga, .85*prior + xsga/gnpdeflator,
scale by at, Dec year ends, non-financials, non-missing sic, winsorise 1%, FF17 within-month z. Placebo twin: OrgCapNoAdj.

## 10. Proposed Sharadar mappings and deviations

- `xsga` -> SF1 `sgna` + `rnd` (ARY), missing -> 0 (OSAP `fillna(0)`). Deviation: D&A embedded where filers put it in SG&A.
- `at` -> SF1 `assets` (ARY, same fiscal year); 0 -> NaN.
- `datadate` month 12 -> `reportperiod` month == 12 (deliberate deviation from the index's `datadate -> calendardate` mapping: calendardate is quarter-end-normalised and would pass January-FYE firms); non-December FYE -> NaN.
- `gnpdefl` -> OMITTED (no macro table; measured rank effect rho 0.999). No external constant in the factor file.
- `sicCRSP` -> TICKERS.siccode CURRENT via `ctx.market_context().ticker_meta(["siccode"], scope="market")`; FF17 via
  `harness.industry.ff17`; industry mean/std over the market cross-section (OSAP: all CRSP x Compustat), stats before
  dropping financials. Not in field_map: a within-group std helper (new harness piece, or compute groupby in the factor).
- Initialisation: 4x first ARY fiscal year seen (FY1997+); gap rule: restart recommended (coverage 49.8%); OSAP-strict NaN
  gives 43.7%. Translator to state the choice.
- Declared inputs: `SF1.sgna`, `SF1.rnd`, `SF1.assets`, `TICKERS.siccode`. Not in the map: `gnpdefl` (omitted).
