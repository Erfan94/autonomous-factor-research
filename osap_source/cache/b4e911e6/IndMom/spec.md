# IndMom — Industry momentum: market-cap-weighted 5-month past return of the 2-digit SIC industry, assigned to every member (Grinblatt and Moskowitz 1999, JF, Table 2A)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/IndMom.py` (cached `predictor.py`; upstream `upstream_CRSPMonthly.py`, `upstream_SignalMasterTable.py` cached beside it).
DATA_SHA 198b281de1a0. Written fresh from source and `field_map_index.yaml`.

## 1. Data availability (verdict: PREFLIGHT_FAILED, mass point; inputs are available, so this is a construction-level failure, not a data one)

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `ret` (monthly, total return) | `crsp.ret` | SEP `closeadj` month-end ratios (`monthly_closeadj`) | mapped (no delisting return) | NaN ret -> 0 inside an existing row; a missing row -> NaN |
| `mve_c` (per-PERMNO cap, month t) | `crsp.mve_permco` (no `mve_c` key in the map) | DAILY.marketcap at the signal date (company-level) | approx | weight needs mve_c > 0 |
| `sicCRSP` -> first 2 chars | `crsp.siccd` | `TICKERS.siccode` (CURRENT, not point-in-time) via `harness.industry.sic_group(.., 2)` | approx | - |
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt. No SF1 input, no zero-fill, no ART/ARQ question.
- Industry aggregates over all listed common stock use `ctx.market_context()` / `scope="market"` accessors (the aggregate is over ALL CRSP-like names, not the screened universe).

## 2. Variables (exact source names)
`permno, time_avail_m, ret, sicCRSP, mve_c` from SignalMasterTable (common stock 10/11/12, exchcd 1/2/3). Derived: `sic2D`, `l1_ret..l5_ret`, `Mom6m`, `IndMom`.

## 3. Formula in words and key lines
Per firm: compound the last FIVE monthly returns, months t-5..t-1 (the signal month t itself is skipped). Per (2-digit SIC, month): mve_c-weighted mean of that firm Mom6m over firms with valid Mom6m and mve_c > 0.
Every firm in the industry-month is assigned that mean, including firms with no Mom6m of their own.
```
df["sic2D"] = df["sicCRSP"].astype(str).str[:2]
df.loc[ret.isna(), "ret"] = 0 ; for lag in range(1, 6): l{lag}_ret = ret of month t-lag (calendar merge)
Mom6m   = (1+l1)*(1+l2)*(1+l3)*(1+l4)*(1+l5) - 1            # FIVE returns although the name and the SignalDoc say "6 month"
IndMom  = sum(Mom6m*mve_c)/sum(mve_c)  by (sic2D, time_avail_m)   # no minimum group size; singleton industries score
```
The code is five returns (l1..l5), NOT six: a translator must not "fix" it to six. Harness equivalent: `monthly_closeadj(6)` -> `close[t-1]/close[t-6] - 1` (the ratio of two month-end closeadj equals the compounded monthly returns to 1e-15,
measured on the six-return IntMom window over 275 months; a name with a missing intermediate close is the only place they could differ, 0 cases). The SignalDoc "OP's long port equally weights three industry portfolios" is not reproduced by OSAP itself (it equal-weights stocks; Notes column).

## 4. Timing / lag convention
OSAP signal at `time_avail_m` t uses returns of t-1..t-5 and mve_c of month t; no publication lag. Here: signal at business month-end t, `closeadj` t-6..t-1, cap at the signal date, earned month t+1.
No filing dates, no flow items, no ART/ARQ smear. Weights use the month-t cap, known at the signal date (no look-ahead).

## 5. Filters
OSAP: SignalMasterTable filter only (shrcd 10/11/12, exchcd 1/2/3); SignalDoc Filter blank. Here: aggregate over `market_constituent_ids` listed that month (no price/size/ADV screen), the harness
universe only chooses which names are SCORED. Non-financial or price screens: none in OSAP.

## 6. Predicted sign
SignalDoc `Sign = +1.0` (high industry momentum -> high return); T-Stat 4.65; Return 0.43; Stock Weight EW; LS Quantile 0.3; Portfolio Period 6; Start Month 6; Cat.Economic momentum, Cat.Data Price, Cat.Form continuous.
Orientation: long HIGH, `ascending=True`.

## 7. The mass-point question (verdict turns on it)
The signal is one constant per (2-digit SIC, month) shared by every member. Do-nothing firm: irrelevant, every member of an industry ties exactly with every other member.
Measured on the harness universe at the 276 decision months (1998-12-31 .. 2021-11-30 signals; market-scope aggregate over ~4,150-6,900 listed names with Mom6m, cap, SIC; 69-72 two-digit industries, 63-68 with a universe member):
- Coverage 99.95-100% (every member with a SIC inherits a value); distinct values 63-68 on ~1,960 scored names (1,739-2,867).
- Modal share of the pooled cross-section: min 8.4%, mean 10.7%, max 20.3%; >= 5% in 276/276 months; >= 10% in 144/276; `qcut(10)` yields < 10 bins in 33/276 months.
- Preflight probe months: 1998-12-31 12.3% (67 distinct, 10 bins), 2010-06-30 8.6% (warning), 2021-11-30 14.5% (hard fail). Two of three probes breach the 10% cliff.
- The harness ranks WITHIN sector. Measured on 46 sampled months (every 6th): names sharing their exact value with >= 10% of their sector peers 62-71% (mean 65.2%), with >= 25% of peers 41-56% (mean 48.8%).
  Mean distinct values per sector: Utilities 1.7 (modal share 98.4%), Real Estate 4.0 (90.5%), Communication Services 7.8 (58.7%), Financial Services 8.4 (40.4%), Healthcare 11.2, Energy 11.4, Technology 14.0,
  Basic Materials 18.3, Consumer Defensive 13.7, Industrials 32.2 (15.6%), Consumer Cyclical 32.3 (11.8%). No sector-month under 10 scored names, so no cross-section fallback.
- Tie handling: the ties ARE the construction; removing them needs noise or a firm-level term, which is a different factor. Not proposed. Same class as EarnSupBig (industry-level value assigned to members).
Verdict basis: preflight would hard-fail the mass point (first and last probe months) and the within-sector rank carries ~65% of names in large tie blocks; the fault is structural, not a data gap.

## 8. History needed (snapshot starts 1998-01)
6 month-ends of `closeadj` (t-6); SEP from 1997-12, so 1998-12-31 (first signal, t-6 = 1998-06-30) is fully scorable: 276/276 months have a value. Own-firm Mom6m coverage of the universe 91.3-99.9% (mean 98.3%), but own momentum is not needed
to receive the industry value. `history_months` (if a translator declares one) should NOT gate on the firm's own price history, or it shrinks coverage beyond OSAP's rule.

## 9. OSAP metadata
IndMom (Acronym2 IndMom); Grinblatt and Moskowitz 1999 JF; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form continuous; Cat.Data Price; Cat.Economic momentum;
Sample 1963-1995; Key Table "2A Raw"; Test "LS port nonstandard (industry)"; Sign +1.0; Return 0.43; T-Stat 4.65; Stock Weight EW; LS Quantile 0.3; Portfolio Period 6; Start Month 6; Filter blank;
GScholar cites 2565. Definition: "Weighted average of firm-level 6 month buy-and-hold return. Average is taken over two digit industries each month and weights are based on market value of equity."

## 10. Proposed Sharadar mappings and deviations (if ever translated; current verdict is not to)
```
ret     -> SEP closeadj, ctx.market_context().monthly_closeadj(6):  close[t-1]/close[t-6]-1
mve_c   -> ctx.at_month_end("DAILY", ["marketcap"], 0, scope="market") * 1e6       [crsp.mve_permco, approx: company-level]
sic2D   -> harness.industry.sic_group(ctx.ticker_meta(["siccode"], scope="market")["siccode"], 2)   [crsp.siccd, approx: CURRENT]
score   = cap-weighted mean by sic2D, reindexed to universe IDs; ascending=True
```
Deviations: (a) current, not point-in-time, SIC (12.3% of names changed SIC, map); (b) OSAP groups on `str[:2]` of the SIC string, `sic_group` divides by 100: differs only for the ~68 three-digit codes;
(c) company-level cap, not per-PERMNO; (d) no delisting return and no NaN->0 for a missing return; (e) equal-weighted stock portfolios as in OSAP, the paper's three-industry portfolios not reproduced.
Fields not in the map: `mve_c` (use `crsp.mve_permco`). Recommendation: `preflight_failed` (mass point, measured above).
