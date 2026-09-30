# EarnSupBig — Industry earnings surprise of the 30% largest firms, assigned to the smaller firms (Hou 2007, RFS, Key Table AR_i,3)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/EarnSupBig.py` (cached `predictor.py`; upstream `upstream_CompustatQuarterly.py`,
`upstream_SignalMasterTable.py`, `upstream_sicff.py` cached beside it). DATA_SHA 198b281de1a0. Written fresh from source and `field_map_index.yaml`.

## 1. Data availability (verdict: APPROX, feasible on inputs; PREFLIGHT MASS-POINT RISK HIGH, see 7)

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `epspxq` (quarterly EPS excl. extraordinary items) | `compustat.epspxq` | SF1 `eps`, `dimension="ARQ"` | mapped | NaN propagates |
| `mve_c` (SMT, per-PERMNO cap) | `crsp.mve_permco` (company-level cap; `mve_c` key not in map) | `ctx.universe["mkt_cap_usd"]` | approx | rank needs non-NaN |
| `sicCRSP` (-> FF48) | `crsp.siccd` / `compustat.sic` | `TICKERS.siccode` via `ctx.ticker_meta(["siccode"])` + `harness.industry.ff48` | approx (CURRENT SIC) | FF48 NaN -> dropped |
| `gvkey` link, `time_avail_m` | - | harness ID; SF1 `datekey` | - | - |

- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt; no analyst forecasts (the "surprise" is a time-series drift surprise in EPS, not analyst-based). No zero-fills.
- `eps` (= netinccmn/shareswa) INCLUDES discontinued operations and is after preferred dividends; `epspxq` excludes extraordinary items. Basic EPS on both.
- `eps` is restated to TODAY's split basis on every row (known trap `sf1_share_counts_split_restated`): the final score is a ratio (surprise / SD) so a common rescale cancels; no price is involved.
- `harness/industry.py` already holds `ff48` copied verbatim from `upstream_sicff.py` (byte-identical to the cached copy). SICs not in the FF48 table (9100-9999, 6780-6789, 6797) -> NaN -> dropped, as upstream.
- Field-checker (THIS snapshot): ARQ `eps` null share and coverage 1998-2021 (map: null 4.5% ARQ; per-quarter LEVEL, ART returns a trailing sum); first ARQ period on the snapshot (1997Q4); `siccode` null share in universe; FF48 NaN share.

## 2. Variables (exact source names)
`epspxq` (monthly-expanded quarterly Compustat, `m_QCompustat`), `mve_c`, `sicCRSP`, `permno, gvkey, time_avail_m`. Derived: `GrTemp, Drift, EarningsSurprise (raw), SD, EarningsSurprise (standardised), tempFF48, tempRK`.

## 3. Formula in words and key lines
Per firm: (i) YoY change in quarterly EPS; (ii) surprise = YoY change minus the mean of the eight previous quarters' YoY changes; (iii) divide by the std of the eight previous quarters' surprises.
Per (FF48 industry, month): take the top 30% of names by market cap (relative rank >= 0.7 among ALL names in that industry-month, whether or not they have a surprise); the average standardised
surprise of those big names is assigned to every name in the industry that is NOT big; big names themselves are NaN.
```
GrTemp   = epspxq - epspxq.shift(12)                    # 12 MONTHS ROWS of the monthly panel = same quarter a year ago
Drift    = mean(GrTemp.shift(n) for n in 3,6,...,24)     # 8 terms = 1..8 quarters back; mean skips NaN
ES_raw   = GrTemp - Drift
SD       = std(ES_raw.shift(n) for n in 3,6,...,24)      # 8 terms, ddof=1, skips NaN
ES       = ES_raw / SD   (NaN if SD is NaN, 0 or < 1e-8)
tempRK   = relrank(mve_c by FF48, month)                 # pandas rank(pct=True, method="average"), output in (0,1]
EarnSupBig = mean(ES over names with tempRK >= 0.7)  by (FF48, month) ; NaN where tempRK >= 0.7
```
Minimum history (skipna): ES needs GrTemp(q0) (eps at q0 and q-4) and >= 1 lagged GrTemp; SD needs >= 2 valid ES among q-1..q-8, each with its own Drift. Smallest case: GrTemp at q0, q-1, q-2, q-3, i.e. EPS for 8
consecutive quarters (q0..q-7). Full window: EPS at q0..q-20 (21 quarters). Partial windows score in OSAP (an SD from 2 values, a Drift from 1): replicate, it is not a min-count rule.

## 4. Timing / lag convention
- OSAP: quarterly record available at datadate + 3 months (or the `rdq` month if later; records with `rdq` > 6 months after datadate dropped), repeated 3 months; `shift(n)` counts ROWS of the
  inner-merged (SMT x quarterly) permno panel, which equals n months only when the panel is contiguous.
- Here: `ctx.fundamentals_history(["eps"], n_periods=21, dimension="ARQ")` (known filings only, deduplicated on reportperiod, `q_back` 0..20), quarters aligned by reportperiod - 3k months, not by row.
  GrTemp(q-k) = eps(q-k) - eps(q-k-4). Filing date = SF1 `datekey` (10-Q/10-K date), typically ~1.5 months after quarter end vs OSAP's +3: earlier than OSAP, and restatements are not in the as-first-filed numbers beyond what `datekey` dedup keeps.
- `FactorDef.dimension = "ARQ"` is REQUIRED: ART is a trailing-four-quarter SUM, so a 12-month difference of ART smears four quarters into one number (known trap `art_is_a_sum_for_flows_and_a_level_for_stocks`; here eps is the flow). ARQ eps is a true single-quarter value.
  `max_fundamental_age_months` = 15 gates the latest filing; `fundamentals_history` returns nothing for a stale name.
- Industry mean and big/small split are computed from the month-t cross-section (`ctx.universe` market caps and `ticker_meta` SIC); no cross-month state.

## 5. Filters
- OSAP: SMT filter shrcd 10/11/12 and exchcd 1/2/3; `dropna(gvkey)`; FF48 must be non-missing; nothing on price. SignalDoc Filter blank. The "exclude the largest 30%" is part of the construction (big firms NaN), not a portfolio filter.
- Here: big/small cut is over the project UNIVERSE (cap >= NYSE 20th percentile entry band, dollar-volume screen), not all CRSP: the "30% largest" of an industry means the top 30% of universe members in that FF48 industry, and the small firms scored are mid-caps. Stated deviation.

## 6. Predicted sign
SignalDoc `Sign = +1.0` (high EarnSupBig -> high return); Stock Weight EW; `Cat.Form` continuous; `Cat.Economic` lead lag (industry information diffusion from big to small firms). Orientation: long HIGH. `FactorDef(ascending=True)`.

## 7. The mass-point question (preflight-fail risk: HIGH)
- The signal is an (FF48 industry, month) CONSTANT shared by every non-big firm of the industry. A cross-section holds at most ~44 distinct values (FF48 industries with a big firm that has a surprise); the project ranks WITHIN `TICKERS.sector`,
  and FF48 is not nested in Sharadar sectors, so a sector sees only the handful of FF48 blocks that overlap it (more for Industrials/Technology, fewer for Real Estate/Utilities); a sector-month with < 10 scored names falls back to the cross-section rank.
- A do-nothing firm (no new filing) still inherits the industry value; all non-big firms in an industry tie exactly. Expected modal share = largest industry's non-big scored names / all scored names: banks (FF48 44), business services (34) and
  pharma/biotech (13) are each about 5-11% of a cap-screened universe and the 70% non-big cut keeps roughly the same share of scored names, so the modal share is ESTIMATED at 6-11%, borderline against the 10% hard-fail, worst in bank-heavy months (not measured here; preflight measures it).
  The "< 10 qcut bins" check is likely to bind within sectors (blocks > 10% of a sector) and possibly in the pooled cross-section when one block exceeds 10%.
- Tie handling: rank(method="average") on exact ties; the ties are the construction and cannot be removed without changing it (adding idiosyncratic terms would be a different factor). Do not add noise. If preflight rejects on the mass point, record the measured modal share and sector-level bin counts.
- Coverage <= 70% by construction (big firms are NaN); further cut by industries with no big firm having a valid ES, by ES needing 8+ quarters of eps, and by names with missing SIC. The 40% Stage-1 bar may bind in 1999-2001.
- Exact-zero of the value: a mean of standardised surprises is 0 only by coincidence; negligible.

## 8. History needed (snapshot starts 1998-01)
ARQ filings from 1997Q4 (first reportperiod on snapshot; `ARQ` coverage broad from calendardate 1997Q4). The minimum of 8 consecutive quarters of EPS is first met at 1999Q3 (filed ~Nov 1999), so decision months 1999-01..~1999-10 are EMPTY; scores exist thereafter with
thin windows (SD from 2-3 surprises, Drift from 1-2 terms) until ~2002-2003 when the full 21-quarter window exists. The big-firm mean is then built from noisy standardised values in 1999-2002. No `history_months` (no price window); `lookback_months` ~ 63 (21 quarters).

## 9. OSAP metadata (SignalDoc)
Acronym EarnSupBig; Acronym2 EarnSupBig; Hou; 2007; RFS; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form continuous; Cat.Data Accounting; Cat.Economic lead lag; SampleStart 1972, End 2001; Key Table "AR_i,3";
Test "mv reg weekly"; Sign +1.0; T-Stat 8.91; Stock Weight EW; LS Quantile blank; Portfolio Period 1; Start Month 12; Filter blank. Definition: "Average monthly value of EarningsSurprise of the 30% largest companies by market value of equity in the same Fama-French 48
industry. Exclude the largest 30% of companies for EarnSupBig (not to compute the anomaly)". Notes: "Only shows up in Table 6. t-stat is from firm-week regressions."

## 10. Proposed Sharadar mappings and deviations
```
epspxq -> SF1 eps, dimension="ARQ", ctx.fundamentals_history(["eps"], 21)      [compustat.epspxq, mapped]
mve_c  -> ctx.universe["mkt_cap_usd"]                                          [crsp.mve_permco, approx; universe-only ranks]
FF48   -> harness.industry.ff48(ctx.ticker_meta(["siccode"])["siccode"])       [crsp.siccd/compustat.sic, approx: CURRENT SIC]
score  = mean ES of tempRK >= 0.7 names per FF48, assigned to names with tempRK < 0.7 ; ascending=True
```
Deviations: (a) `eps` includes discontinued operations (and, pre-2015, extraordinary items are inside net income) whereas `epspxq` excludes extraordinary items; (b) current (not point-in-time) `siccode`, 12-14% of names changed SIC since 1998, and FF48 from SIC4 only
(`sicCRSP` is the CRSP SIC, not Compustat); (c) "30% largest" is within the cap-screened universe, not all CRSP; `mkt_cap_usd` is company-level (all classes) vs per-PERMNO `mve_c`; relrank reproduced as rank(pct=True, average), threshold >= 0.7;
(d) quarter alignment by reportperiod, not by panel row; (e) quarter known at `datekey` (earlier than datadate + 3 months); (f) skipna partial windows retained (noisy early scores); (g) the harness ranks within sector, so the signal is further blockwise in `ctx.universe["sector"]`.
Hard-rule note: the industry aggregation is the signal's definition, not a harness task (precedent: OrgCap/IndRetBig use `harness/industry.py`); no sector ranking, universe filter or hedging in the factor. `FactorDef(dimension="ARQ")`, `family=None` until Phase C. Fields not in the map: `mve_c` (use `crsp.mve_permco`).
