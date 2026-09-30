# HerfAsset — Industry concentration (assets) (Hou and Robinson 2006, Table 2 H(Assets))

OSAP ref b4e911e69678a7424f318617a61d813f54183123 (cache b4e911e6); source `Predictors/HerfAsset.py` (cached
`predictor.py`, `signaldoc_row.csv`). DATA_SHA 198b281de1a0. SignalDoc row (Cat.Signal == Predictor):
Cat.Data = Other, Cat.Economic = other, Predictability 2_likely, Signal Rep Quality 1_good.

## 1. Data availability (verdict: APPROX — buildable; preflight expected to pass on the cross-section)

| input (OSAP) | field_map key | Sharadar | status | note |
|---|---|---|---|---|
| `at` (m_aCompustat: annual `at`, lagged 6m from datadate, forward-filled) | `compustat.at` | SF1.assets (ART level) | mapped | null 0.05%, exact-zero 0.01%; level, so no TTM smear |
| `sicCRSP` (SignalMasterTable, point-in-time CRSP siccd) | `crsp.siccd` | TICKERS.siccode (CURRENT only) | approx | 12.3% of SEP-scope tickers changed SIC since 1998 |
| `shrcd` (drop if > 11) | `crsp.shrcd` | TICKERS.category Domestic Common Stock* | approx | the harness universe and market scope already apply it |
| SignalMasterTable row (firm in CRSP that month, exchcd 1-3, shrcd 10-12) | `crsp.smt_row` | SEP presence that month, market scope | mapped | industry sums run over ALL listed common stock, not the screened universe |

- Nothing is unavailable and nothing is zero-filled. Deviation that makes it `approx`: SIC is today's
  classification, and it enters the signal VALUE (through the industry grouping and the 49xx exclusion), the
  same look-ahead class as any industry-mean factor (ChInvIA). Recommendation: `approx`, proceed.

## 2. Variables (exact source names)

`permno`, `time_avail_m`, `at` (m_aCompustat); `sicCRSP`, `shrcd` (SignalMasterTable). Helper: `utils.asrol`.

## 3. Formula

```
df = m_aCompustat[permno,time_avail_m,at].merge(SMT[permno,time_avail_m,sicCRSP,shrcd], how="inner")
df["sic3D"]    = str(sicCRSP)[:4]                               # NAME SAYS 3D, CODE KEEPS 4 DIGITS
df["indasset"] = df.groupby([sic3D,time_avail_m])["at"].transform("sum")
df["tempHerf"] = (at/indasset)**2 summed within [sic3D,time_avail_m]      # Herfindahl, NaN at skipped
HerfAsset      = asrol(permno, 1mo window of 36, mean of tempHerf, min_samples=12)
HerfAsset = NaN if shrcd > 11; NaN if sic in {4011,4210,4213} & year<=1980; 4512 & <=1978;
            {4812,4813} & <=1982; any 49xx (all years)
```
- The pinned code groups on the FOUR-digit SIC string (`str[:4]`). SignalDoc's "three digit" wording differs;
  the code is the construction. Translator: `harness.industry.sic_group(sic, 4)`, not string slicing (3-digit
  codes 100/700/800/900 are hundreds-multiples; 68 of 20,829 values).
- A firm's value is its industry's Herfindahl averaged over the firm's own listed months in the last 36. Every
  firm in one SIC4 with the same listing history gets the same number. No winsorising. The rows are
  `how="inner"` with m_aCompustat (unlike Herf's `right`), so a row needs a Compustat record, not a non-null `at`.
- Only the 49xx rule is live in 1999-2021 (the others end <= 1982). 49xx is 5.0% of the universe (3.6-6.2%).

## 4. Timing / lag

OSAP: annual data available from datadate + 6 months, forward-filled; month-m value uses industry months m-35..m.
Harness: `ctx.market_context()` / `fundamentals_at_month_ends(["assets"], range(36), scope="market")` reads the
latest filing by `datekey` (ART default, max age 15 months), at each of 36 lagged business month-ends, keeping a
firm at a lag only if it traded that month. ART/ARY change nothing structurally (level); measured both: ART
coverage 91.0% mean, ARY 89.7%. Recommend ART. Filings appear at the 10-K/10-Q date (2-4 months earlier than OSAP's
6-month rule): a fresher, small deviation. Signal stamped at month-end m, earns m+1. No flow item, no TTM smear.
Rolling mean needs >= 12 observed months: first scorable signal month is 1998-12 (filings start 1997Q4).

## 5. Filters

Common stock only (universe). Exclude 49xx (utilities); null SIC -> NaN (never null in the universe, 0.0%).
The harness universe filters are the harness's; the factor applies only the 49xx exclusion.

## 6. Predicted sign

SignalDoc `Sign = -1.0` (higher concentration, lower return): Hou-Robinson Table 2 H(Assets), characteristics-adjusted
portfolio sort, EW, t = 2.12, return 0.2, Portfolio Period 1, Start Month 6; sample 1963-2001. Notes: "OP uses
characteristics adjustments ... Not sure if raw return would exceed 1.96". `ascending=False`.

## 7. The mass-point question

Do-nothing firm: none in the usual sense; the value is an industry attribute, so firms of one SIC4 with the same
36-month listing history tie EXACTLY. Measured on the harness universe (`build_universe`, all 276 signal months
1998-12-31..2021-11-30; ARY and ART variants, identical mass statistics):
- Scored share (siccode present, not 49xx, >= 12 observed months): ART mean 91.0%, ARY 89.7%; first two months
  thin (1998-12 48.1% ART / 44.0% ARY, 1999-01 55.7% / 44.8%, data start), from 1999-02 >= 80.6% ART / 75.4% ARY;
  0 months under 40%. Scored n median 1,745 (ART), min 1,097.
- Cross-section mode share (exact equality): median 5.9%, mean 5.9%, max 7.7% (ART); 0 of 276 months at or above
  the 10% cliff; 228-233 months at or above the 5% warning; `qcut` gives 10 bins in every month; 430 distinct
  values (median, ART), 337-858. The modal block is SIC 6798 (REITs), 88 names (2008-12), 107 (2013-12), 133 (2021-11).
- **Within-sector (the D3 ranking) the ties concentrate** (ARY run; the ART book-equity run agrees within 3 pts): Real Estate 82-86% at one value, Energy 37-43%,
  Healthcare 24-31%, Financial Services 18-21%, Technology 16-22%, Communication Services 14-21%, others under
  10% (2008-12, 2013-12, 2021-11). Utilities has 1-2 names (the < 10-name fallback applies). Preflight will
  pass (it reads the cross-section), but within-sector ranking removes most of the signal's variation in
  Real Estate and Energy. Flag for the reviewer; not a verdict.
- Tie handling: average rank; no value is a legitimate zero; single-firm SIC4 = exactly 1.0 (0.87% of scored).
- H never exceeds 1 (assets are non-negative), so no sign-flip pathology here (HerfBE differs).

## 8. History needed

OSAP sample 1963-2001. Snapshot SEP starts 1997-12 (one-day stub month), SF1 1997Q4: a 36-month window is full
only from about 2001-01; the 12-observation minimum makes 1998-12 the first scorable month. Declare
`lookback_months` ~ 51 (36 + 15 filing age). No `history_months` (no price window); do not count the 1997-12
stub (irrelevant here: SF1-based, not SEP-month aggregated).

## 9. OSAP metadata

Acronym HerfAsset, Hou and Robinson 2006, Journal of Finance, "Industry concentration (assets)". Cat.Form
continuous, Cat.Data Other, Cat.Economic other, Quantile 0.2 EW, Key Table in OP `2 H(Assets)`, test "port sort
char adjusted", GScholar cites 1316. Predictor output column `HerfAsset`.

## 10. Proposed Sharadar mappings

| OSAP | Sharadar | deviation |
|---|---|---|
| `at` | SF1.assets, ART (ARY alt.) | filing-date availability, not datadate + 6m; level |
| `sicCRSP` -> `sic3D` (4-digit) | TICKERS.siccode via `harness.industry.sic_group(.,4)`, market scope | CURRENT SIC, look-ahead in the value (D3 kind) |
| SMT row / m_aCompustat row | listed at lag (`_listed_at`) AND a filing <= 15 months old | OSAP needs a Compustat row; same |
| industry sum over all CRSP-Compustat | `ctx.market_context()` market scope (all listed common stock) | same set, vendor coverage |
| `asrol` 36m, min 12 | mean of per-month H over lags 0..35, n >= 12 | months without a qualifying filing are skipped, as OSAP's forward-fill expires at 12m |
| regulated-industry NaN | 49xx only (others outside window) | current SIC |

Fields not in the field map index: none (all keys present). Orientation `ascending=False`.
