# Herf — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: APPROX (constructible; current-only SIC, early-1998 revenue coverage)
Checked against `osap_source/field_map_index.yaml`.

| OSAP var | Sharadar | status (verified_on) | role |
|---|---|---|---|
| sale | revenue (ART TTM), USD via fxusd | mapped (2026-09-30) | FLOW, cross-firm SUM, 36 month-ends |
| sicCRSP | TICKERS.siccode (CURRENT) | sic mapped (2026-09-30); siccd approx | industry key, static |
| shrcd, exchcd | TICKERS.category / exchange | approx (blank) | market scope |

- No unavailable input; no IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob or ppegt.
- **The pinned code groups on SIC4, not SIC3.** `sic3D = str(sicCRSP)[:4]` is the full four-digit code despite the
  name and the SignalDoc text "three digit industry". Follow the code (SIC4). TICKERS.siccode is float64:
  group on the integer, never a string slice of "2834.0".
- **Current-only classification (look-ahead through reclassified firms):** OSAP's sicCRSP is point-in-time;
  TICKERS.siccode/sector are today's (12.3% of SEP-scope tickers changed SIC since 1998). Industry membership
  is applied to all history.
- **Industry sums need the MARKET scope**, not the harness universe: OSAP sums sale over every CRSP common stock
  on NYSE/AMEX/NASDAQ (SMT filter shrcd 10-12, exchcd 1-3). Use `ctx.market_context().fundamentals_at_month_ends(
  ["revenue","fxusd"], range(36), scope="market")` and `ticker_meta(["siccode"], scope="market")`. The sum ACROSS
  firms must convert to USD (known trap sf1_currency_cross_firm_sums): `revenue / fxusd`. fxusd is not in the
  field_map index (known-trap entry only); field-checker to confirm the column.
- **Early-1998 coverage (measured, market scope, month-end lags of signal 2000-12):** names with ART revenue /
  listed names 28.8% 1998-01, 29.9% 1998-02, 69.4% 1998-03, 73.0% 1998-04, 39-47% 1998-05..1998-11, 50.9% 1998-12,
  52.6% 1999-01, 53.5% 1999-02, **85.3% 1999-03**, then 86.0-92.8% through 2000-12. Industry shares summed over
  half the firms overstate Herf in those months.
- Universe coverage (scored share), 9 probe months, unmasked: 88.4% 1999-01, 87.8% 1999-06, 82.8% 2000-01,
  82.7% 2000-02, 85.1% 2000-06, 94.2% 2003-12, 93.4% 2008-12, 91.3% 2015-06, 89.9% 2021-11 (TICKERS.siccode
  null 0.00% in the universe; the remainder is 49xx exclusion 3.7-6.0% plus names without 12 valid months).

## 2. Variables by exact source name
`m_aCompustat` [permno, time_avail_m, sale] right-merged on `SignalMasterTable` [permno, time_avail_m, sicCRSP,
shrcd]. Upstream SMT keeps shrcd in (10, 11, 12) and exchcd in (1, 2, 3); sicCRSP int16 (no NaN). sale is not
zero-filled. `time_avail_m = datadate + 6 months`, annual record repeated 12 months.

## 3. Formula
Hou and Robinson (2006): three-year average of the industry Herfindahl index of firm sales.

    indsale[i,t]   = sum of sale over all SMT firms with SIC4 == i in month t (NaN sales excluded)
    tempHerf[i,t]  = sum over those firms of (sale / indsale)^2
    Herf[f,t]      = asrol mean of tempHerf[sic(f), s] over the firm's 36 calendar months s in (t-35 .. t), min 12 non-null
    Herf = NaN if shrcd > 11;  NaN if SIC startswith "49" (any year); NaN for year < 1951

tempHerf is assigned to EVERY firm-month row of the industry (right merge), so a firm needs no sale of its own
but does need an SMT row (traded that month) and a known SIC. The dated regulated-industry exclusions
(4011/4210/4213 to 1980; 4512 to 1978; 4812 and " 4813" to 1982) never bind after 1998 (the " 4813" literal also
has a leading-space typo); only the 49xx rule (3.7-6.0% of the universe) matters. Market shares need no own-sale
guard: a firm with missing revenue simply contributes nothing.

## 4. Timing / lag convention
- OSAP: fiscal-year sale at datadate + 6 months, refreshed annually; Herf is a 36-month mean of monthly values.
  Sharadar ART revenue as of each month-end (datekey <= month-end) refreshes quarterly, so industry sums mix
  fiscal windows within a month (a level sum of TTM flows, NOT a year-over-year difference: no smear issue).
  Presence at lag s = the firm traded that month (`fundamentals_at_month_ends(scope="market")` already keeps
  only names listed at each lag), matching OSAP's right-merge on SMT rows.
- ART is fresher than OSAP's 6-month lag; no extra lag applied (standing ruling).

## 5. Filters
Shrcd > 11 (shrcd 12 names enter the sums but are not scored), 49xx, dated pre-1983 exclusions (no-ops), year < 1951
(no-op). SignalDoc `Filter` is blank. Harness universe filters are not added to the SUM (market scope is unscreened).

## 6. Predicted sign (SignalDoc)
`Sign = -1.0`: low industry concentration (competitive industries) is the long side; score = -Herf
(ascending=False). Cat.Signal Predictor; Cat.Economic `other`; Cat.Form continuous; Cat.Data Other.

## 7. The mass-point question (this one is structural)
Herf is an INDUSTRY attribute: every firm in a SIC4 with the same 36-month presence shares one value (distinct
values among scored names 335-521 vs 316-334 SIC4 groups). A do-nothing firm does not exist as a concept; the
mass points are industry blocks.
- Cross-section (9 probe months): modal-value share 4.3-7.4% (4.98, 5.28, 5.24, 5.31, 4.27, 5.08, 5.61, 7.38,
  6.54), largest SIC4 share of scored names 5.1-8.2%; `qcut` still yields 10 bins (checked at 4 months). Under the
  preflight 10% hard cliff but in the 5% warn band at most months. Herf == 1 (sole revenue-reporting firm in its
  SIC4) share 0.19% (1999-01) to 1.44% (2021-11), rising.
- **Within-sector (D3 ranks each signal among sector peers): one SIC4 dominates several sectors, and preflight
  will not catch it.** Largest single-SIC4 share of the scored names in a sector: Real Estate SIC 6798 (REITs)
  **93.3% (1999-06), 92.3% (2003-12), 90.5% (2015-06), 84.1% (2021-11)**; Energy SIC 1311 36.8 / 47.4 / 45.2 /
  44.0%; Healthcare SIC 2834 27.8 / 29.2 / 42.7 / 35.4%. Every REIT gets one within-sector rank, so Herf carries
  almost no ranking information inside Real Estate (104-164 scored names, ~5-7% of the universe) and large tie blocks
  inside Energy and Healthcare. The 6798 value also sits at the low end of the cross-section (modal value 0.0176
  in 2015-06, 0.0177 in 2021-11) when SIC is pooled. No tie handling is proposed (they are real values); the
  caller should expect the sector-rank degeneracy to cap the signal's dispersion.
- The standing tie rule (level 0 at both ends -> NaN) does not apply (a level, never a change). Ties: average rank.

## 8. History needed (snapshot starts 1998-01, SEP panel 1997-12, SF1 1997Q4)
- 36 month-end lags of ART revenue, each up to 15 months stale: `lookback_months` ~ 50; min 12 valid months.
  Panel and ART both start 1998-01 (the month-ends before it do not exist).
- **Unmasked** (recommended, with the caveat): months 1998-01..1999-02 (revenue coverage 29-73%) enter the mean;
  first scorable signal 1998-12, scored share 88.4% at 1999-01, so all 276 decision months exist.
  **Masked alternative:** drop lags before 1999-03 (revenue coverage < 80%): first scorable signal 2000-02
  (12 valid lags 1999-03..2000-02), 13 of 276 months empty (1999-01..2000-01). Measured masked vs unmasked
  Spearman 0.960 (2000-02), 0.965 (2000-06), 1.000 from 2003-12 (window clear of 1998). The 36-month mean
  dilutes the early-1998 inflation; recommend unmasked, say so in the docstring.

## 9. OSAP metadata
Acronym Herf; Hou and Robinson 2006 (JF), Table 2 firm-level raw; sample 1963-2001; Predictability in OP 1_clear;
Signal Rep Quality 1_good; Sign -1; Return 0.26; T-Stat 2.14; EW; LS Quantile 0.2; Start Month 6; Portfolio
Period 1; Filter blank. Source `Signals/pyCode/Predictors/Herf.py` at b4e911e69678a7424f318617a61d813f54183123.
Output `Herf.csv [permno, yyyymm, Herf]`. Uses `utils/asrol` (36 x 1mo, min 12, gap-filled calendar months).

## 10. Proposed Sharadar mappings and deviations
1. sale -> `revenue / fxusd` (ART), summed per (integer SIC4, month-end) over the market scope; tempHerf = sum of
   squared shares over firms with non-null revenue (negative revenue kept as OSAP does).
2. Firm value: mean of tempHerf(SIC4 of the firm) over lags 0..35 where the firm was listed, min 12 non-null;
   NaN if siccode null or siccode // 100 == 49. Universe names only are scored.
3. Deviations: siccode current-only; market scope = Sharadar common stock on NYSE/NASDAQ/NYSEMKT (no separate
   shrcd; shrcd > 11 not reproducible, `category` Domestic Common Stock* used); revenue as reported in ART,
   quarterly mixed fiscal windows; early-1998 sums partial (unmasked recommended); SIC4 groups formed from
   TICKERS SIC only (one row per permaticker).
4. Fields not in field_map index: `fxusd` (trap entry only), `category`/`exchange` used via the market scope.
