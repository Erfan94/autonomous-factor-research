# IndRetBig — Return of the 30% largest firms in the same FF48 industry, assigned to the smaller firms (Hou 2007, RFS, Table 6, R_i,3(-1))

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/IndRetBig.py` (cached `predictor.py`; upstream `upstream_CRSPMonthly.py`, `upstream_SignalMasterTable.py`, `upstream_sicff.py` cached beside it).
DATA_SHA 198b281de1a0. Written fresh from source and `field_map_index.yaml`.

## 1. Data availability (verdict: PREFLIGHT_FAILED; inputs available, the mass point and the coverage bar fail on construction)

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `ret` (month t, total return) | `crsp.ret` | SEP `closeadj` month-end ratio | mapped (no delisting return) | NaN skipped by the groupby mean |
| `mve_c` (per-PERMNO cap, month t) | `crsp.mve_permco` (no `mve_c` key) | DAILY.marketcap at the signal date, company-level | approx | NaN rank -> not big, but still scored |
| `sicCRSP` -> FF48 | `crsp.siccd` | `TICKERS.siccode` (CURRENT) via `harness.industry.ff48` (verbatim `sicff.py`, byte-identical to the cached upstream) | approx | FF48 NaN -> dropped |
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt; no SF1 input; no zero-fill.
- The big-firm rank and mean are over ALL listed common stock: `ctx.market_context()` / `scope="market"`.

## 2. Variables (exact source names)
`permno, time_avail_m, ret, mve_c, sicCRSP`. Derived: `tempFF48, tempRK, IndRetBig`.

## 3. Formula in words and key lines
Per (FF48 industry, month): rank firms by `mve_c` (percentile rank, average ties, in (0,1]); "big" = rank > 0.7. IndRetBig = equal-weighted mean month-t `ret` of the big firms. Assign it to every firm of the industry,
then set it to NaN for firms with rank >= 0.7 (the big firms are never scored on their own cell); "Exclude the largest 30% for IndRetBig (not to compute the anomaly!)" is part of the construction.
```
tempFF48 = sicff(sicCRSP, 48) ; dropna(tempFF48)
tempRK   = relrank(mve_c by [tempFF48, yyyymm])       # == groupby.rank(method="average", pct=True); NaN mve -> NaN rank
IndRetBig = mean(ret | tempRK > 0.7) by (tempFF48, time_avail_m)  ; merged back to ALL firms ; NaN where tempRK >= 0.7
```
No minimum number of big firms or of non-null returns (an industry with 2 big firms still scores; measured minimum 2 big firms per FF48-month). Firms with NaN `mve_c` keep a value (NaN rank is neither big nor excluded).

## 4. Timing / lag convention
The signal uses the month-t return of the big firms, known at the month-end signal date; earned month t+1 (lead-lag: big-firm news diffuses to small firms). No filing dates, no flow items, no ART/ARQ smear, no lag.
Harness: `ctx.market_context().monthly_closeadj(1)` -> `close[t]/close[t-1]-1`; cap at the signal date. FF48 from current SIC (deviation).

## 5. Filters
OSAP: SignalMasterTable (shrcd 10/11/12, exchcd 1/2/3), FF48 non-missing; SignalDoc Filter blank. Here the big/small split is over ALL listed names (faithful to OSAP), so it is NOT the harness universe: the universe is the cap-screened top tail
of those names, and most universe members are "big" (see 7).

## 6. Predicted sign
SignalDoc `Sign = +1.0` (high big-firm industry return -> high small-firm return); T-Stat 11.0 ("mv reg weekly"); Stock Weight EW; Portfolio Period 1; Start Month 12; Cat.Economic lead lag; Cat.Data Price; Cat.Form continuous.
Orientation: long HIGH, `ascending=True`.

## 7. The mass-point question (verdict turns on it), measured on the harness universe, all 276 decision months (signals 1998-12-31 .. 2021-11-30)
- Do-nothing firm: irrelevant; every non-big member of an FF48 industry ties exactly. At most 48 distinct values exist; all 48 industries had big-firm returns every month.
- Coverage of the universe (scored names): min 20.4%, mean 28.9%, max 36.9%; below the 40% Stage 1 bar in 276/276 months. Cause: 63.0-79.3% (mean 70.7%) of universe members rank >= 0.7 among all listed names in their FF48 industry and are
  set NaN; FF48 missing on 0.1-0.5%.
- Modal share of the pooled cross-section: min 10.2%, mean 13.9%, max 26.1%; >= 10% in 276/276 months; `qcut(10)` yields < 10 bins in 126/276 months; distinct values 32-46 (mean 39.2).
  Preflight probe months: 1998-12-31 12.6% (35 distinct, 10 bins, coverage 20.9%), 2010-06-30 12.9% (37 distinct, coverage 28.6%), 2021-11-30 19.3% (45 distinct, 9 bins, coverage 35.9%): hard fail at all three probes.
- Within sector (11 sectors, all months): share of scored names in a (sector, value) cell >= 10% of the sector: 71.7-87.0% (mean 80.1%); mean distinct values per sector Real Estate 2.1 (modal 96.3%), Utilities 1.7 (98.2%),
  Financial Services 3.6 (65.3%), Communication Services 5.0 (66.1%), Energy 6.0 (61.7%), Healthcare 7.4, Consumer Defensive 8.3, Basic Materials 9.2, Technology 10.6, Consumer Cyclical 12.6, Industrials 16.7. Sector-months under 10 scored names (cross-section fallback): 7 of 3036.
- Universe-scope alternative (big = top 30% of the screened universe instead of all listed names), run on the three probe months: coverage 68.6/68.3/68.8%, modal share 12.8/9.1/15.1%, 47-48 distinct, 10 bins. Coverage is fixed
  but the mass point is not (two of three probes still exceed 10%): the constants cannot be removed because a value per industry-month IS the predictor. It would also be a different construction (scored firms would be the universe's
  small 70%, not the market's).
- Tie handling: none available without changing the construction (average ranks on exact ties are what the harness does). Do not add noise.
Verdict basis: preflight hard-fails the mass point at every probe month; coverage is under the 40% bar in every month. Same class as EarnSupBig.

## 8. History needed (snapshot starts 1998-01)
Two month-end closes (t-1, t) and the signal-date cap: 1998-12-31 is scorable; 276/276 months have values.

## 9. OSAP metadata
IndRetBig (Acronym2 IndRetBig); Hou 2007 RFS; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form continuous; Cat.Data Price; Cat.Economic lead lag; Sample 1972-2001;
Key Table "6 R_i,3(-1)"; Test "mv reg weekly"; Sign +1.0; T-Stat 11.0; Stock Weight EW; Portfolio Period 1; Start Month 12; Filter blank; GScholar cites 814.
Definition: "Average monthly return (ret) of the 30% largest companies by market value of equity in the same Fama-French 48 industry. Exclude the largest 30% of companies for IndRetBig (not to compute the anomaly!)".
Notes: "Table 2 presents a VAR with two states: return of big firms and return of small firms. Table 6 is easier to compare to others."

## 10. Proposed Sharadar mappings and deviations (if ever translated; current verdict is not to)
```
ret   -> SEP closeadj, ctx.market_context().monthly_closeadj(1): close[t]/close[t-1]-1         [crsp.ret, mapped, no dlret]
mve_c -> ctx.at_month_end("DAILY", ["marketcap"], 0, scope="market")                          [crsp.mve_permco, approx]
FF48  -> harness.industry.ff48(ctx.ticker_meta(["siccode"], scope="market")["siccode"])       [crsp.siccd, approx: CURRENT SIC]
score = mean ret of rank>0.7 firms per FF48, assigned to rank<0.7 firms; NaN for rank>=0.7; ascending=True
```
Deviations: (a) current SIC, FF48 from SIC4 only; (b) company-level cap, not per-PERMNO `mve_c`; (c) no delisting return; (d) rank over listed names that traded in the month (market scope) as OSAP does.
Fields not in the map: `mve_c` (use `crsp.mve_permco`). Recommendation: `preflight_failed` (mass point 10.2-26.1% in all months; coverage 20-37%).
