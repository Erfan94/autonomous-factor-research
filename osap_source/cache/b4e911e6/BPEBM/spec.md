# BPEBM — BP minus EBM (leverage component of book-to-market; Penman, Richardson and Tuna 2007, Table 1D)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/ZZ1_EBM_BPEBM.py` (cached `predictor.py`;
emits EBM and BPEBM). DATA_SHA 198b281de1a0. field_map statuses are mappings, not proofs (notes quoting other
DATA_SHAs are a predecessor pull).

## 1. Data availability (verdict: APPROX, feasible; five stated deviations, none is an unavailable core input)

| OSAP input (`m_aCompustat`) | field_map key | Sharadar | map status | OSAP missing-item rule |
|---|---|---|---|---|
| `ceq` | `compustat.ceq` | SF1 `equity` (ART) | approx | NOT zero-filled (NaN) |
| `che` | `compustat.che` | SF1 `cashneq + investmentsc.fillna(0)` | approx | zero-filled |
| `dltt + dlc` (used only as a sum) | `compustat.dltt_plus_dlc` (parts: `compustat.dltt`->`debtnc` approx, `compustat.dlc`->`debtc` mapped) | SF1 `debt` (ART) | mapped (sum) | NOT zero-filled (NaN) |
| `dc` | `compustat.dc` (+ `compustat.dcvt`, `compustat.dcpstk`, both unavailable) | none -> 0 | unavailable | zero-filled |
| `dvpa` | `compustat.dvpa` | none -> 0 | unavailable | zero-filled |
| `tstkp` | `compustat.tstkp` | none -> 0 | unavailable | zero-filled |
| `mve_permco` (SignalMasterTable) | `crsp.mve_permco` | DAILY.marketcap x1e6 -> `ctx.universe["mkt_cap_usd"]` | approx | row must exist (inner join) |

- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt. The unavailable `dc`, `dvpa`, `tstkp` are
  all in OSAP's `zero_fill_vars` (`upstream_CompustatAnnual.py`), so the rule allows 0: APPROX, not infeasible.
- FIELD_MAP DISCREPANCY: the map glosses `dc` as "Deferred charges"; in OSAP `dc` is CONVERTIBLE DEBT, derived from
  `dcpstk`/`pstk`/`dcvt` (`upstream_CompustatAnnual.py`, `mask_dc1..3`). Sharadar has no such field, so `dc` = 0 for
  every firm, where OSAP is 0 only when blank; affects convertible issuers only, size not measurable here.
  Field-checker: confirm no SF1 field carries convertibles and log the map correction.
- Field-checker, THIS snapshot: `compustat.ceq`, `compustat.che` (`cashneq`, `investmentsc`),
  `compustat.dltt_plus_dlc` (`debt`; `debtc`/`debtnc` only for the section-10 alternative), `compustat.curcd`
  (`fxusd`), `crsp.mve_permco` (`mkt_cap_usd`). All ART balance-sheet LEVELS (ART==ARQ same period), ~99.9% populated
  from 1997Q4 (the ~50% ART-flow gap for 1998Q1-Q3 concerns flows; none used). Predecessor-pull figures, to re-measure:
  `debt` null ~0.03%; `debtc`/`debtnc` null ~20%; `investmentsc` null 14-19% of the universe (mostly financials).
## 2. Variables (exact source names)

`ceq, che, dltt, dlc, dc, dvpa, tstkp` (Compustat annual, $ millions, available at `datadate + 6 months`),
`mve_permco` ($ millions, month t: `|prc|*shrout/1000` summed over permco), `permno, time_avail_m`.
## 3. Formula

```
temp  = che - dltt - dlc - dc - dvpa + tstkp            # net financial assets (cash+STI minus debt, convertibles, pref. arrears, plus treasury pref.)
EBM   = (ceq + temp) / (mve_permco + temp)              # enterprise book-to-market
BP    = (ceq + tstkp - dvpa) / mve_permco
BPEBM = BP - EBM
```
With the zeroed terms (dvpa = tstkp = dc = 0): `T = che - debt`, `BP = ceq/M`, and algebraically
`BPEBM = T (ceq - M) / (M (M + T))`. So the signal is 0 when T = 0, changes sign with the sign of net financial
assets T and of (book - market), and BLOWS UP as `M + T -> 0`. It is NOT monotone in BP and not a pure leverage
measure; an EV <= 0 firm (cash > market cap, T > M) flips the denominator sign. OSAP applies no guard; it keeps
`inf`/extreme values (`upstream_save_standardized.py` has no non-finite filter). The translator must guard `M > 0`
and `M + T != 0` (NaN) and record how many names that removes. Do not winsorise or log it.
## 4. Timing / lag convention

- OSAP: annual items are available at datadate month + 6, repeated for 12 months (offsets 0..11), latest datadate
  wins. At month t the balance sheet is 6-17 months old; `mve_permco` is month t itself, so the two legs of the ratio
  are misaligned by up to 17 months and the signal moves monthly with price.
- Here: `ctx.fundamentals(["equity","debt","cashneq","investmentsc"])` at the signal as-of (ART, `datekey <=` as-of,
  cap `max_fundamental_age_months`). The balance sheet is the latest filed quarter, 0-3 months old (vs 6-17), and
  updates quarterly. The project's ART-as-of-filing convention changes the book-side staleness only; market cap is
  the same month-t value (`mkt_cap_usd`, DAILY month-end, not SF1.marketcap).
- Flow smearing: none (all levels, no year-over-year difference); no `dimension=ARQ` override.
## 5. Filters

- SignalDoc `Filter` = `abs(prc)>5`. It lives in OSAP's portfolio stage, NOT in `predictor.py`. The project universe
  uses price >= $1 and factors may not filter: no price cut in the factor; recorded as a deviation.
- No SIC/financials exclusion in OSAP; within-sector ranking here absorbs the level difference. Implicit OSAP
  filters: annual row needs non-null `at`, `prcc_c`, `ni`; `curcd='USD'`; CCM link; SMT row (shrcd 10/11/12, exchcd 1/2/3).
## 6. Predicted sign

SignalDoc `Sign = -1.0` (high BPEBM -> low future return); `Stock Weight` EW; `Cat.Form` continuous;
`Cat.Economic` leverage. Orientation: long LOW BPEBM (D1), short HIGH BPEBM. FactorDef carries `sign=-1`
(or scores `-BPEBM`); no flip beyond OSAP's published sign.
## 7. The mass-point question

- A firm that does nothing (no new filing) keeps ceq/che/debt fixed but `M` moves with price monthly, so BPEBM
  changes continuously: no stale-value mass point.
- Exact 0 needs `T = 0`: cash-and-STI equal to debt to the dollar (essentially never) or both 0. Sharadar `debt`
  is exactly 0 on ~15% of ART rows (filled zero, field_map), `cashneq` on ~0.8% of non-null; both at once is a small
  fraction of a percent (estimate; preflight to measure the share at `|BPEBM| < 1e-12`). `ceq == M` ~0.
- The real risk is the TAILS, not a mass: `M + T -> 0` yields huge |BPEBM| of either sign, so the extremes of the
  rank are occupied by the near-singular names. Preflight should report the share with `M + T <= 0` (not measured
  here) and the extreme-percentile magnitudes; those names land in D1 or D10 by the sign of the blow-up.
- Ties: continuous float; harness default rank(method="average"); expect no tie block. Coverage bounded by the
  filing-age cap and `debt`/`equity` (~99.9%); che zero-fill keeps financials/REITs (understated che).
## 8. History needed (snapshot starts 1998-01)

One latest filing plus current market cap; no return window, no `history_months`, no `lookback_months`. SF1 ART
levels from 1997Q4, DAILY from 1998-12-01, SEP from 1997-12-31: the first decision month 1999-01 is covered.
## 9. OSAP metadata (SignalDoc)

Acronym BPEBM; Acronym2 BMlev; Authors Penman, Richardson and Tuna; Year 2007; Journal JAR; Cat.Signal Predictor;
Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form continuous; Cat.Data Accounting;
Cat.Economic leverage; SampleStart 1963, End 2001; Key Table 1D (portfolio sort), Test univariate reg; Sign -1.0;
Stock Weight EW; LS Quantile blank; Portfolio Period 12; Start Month 6; Filter `abs(prc)>5`;
Definition "BP - EBM, BP = (ceq + tstkp - dvpa)/(shrout*abs(prc))"; SignalDoc Notes mention "B/P - NOA/P^NOA in OP"
(the code is the authority). The same script also emits EBM.

## 10. Proposed Sharadar mappings and deviations
```
ceq   -> SF1 equity (ART)                               [compustat.ceq, approx]
che   -> SF1 cashneq + investmentsc.fillna(0)           [compustat.che, approx; NaN only if cashneq NaN]
debt  -> SF1 debt (ART)  replaces dltt + dlc            [compustat.dltt_plus_dlc, mapped sum]
dc = dvpa = tstkp = 0                                   [zero-filled in OSAP; no Sharadar source]
M     -> ctx.universe["mkt_cap_usd"]                    [crsp.mve_permco, approx]
T = che - debt;  BP = ceq/M;  EBM = (ceq+T)/(M+T);  score = BP - EBM, sign -1
guards: M > 0; M + T != 0 (else NaN); no winsorising
```
Convert reporting-currency SF1 items (`equity`, `debt`, `cashneq`, `investmentsc`) by `/fxusd` (units per 1 USD)
so they match `mkt_cap_usd` in USD; OSAP keeps only `curcd='USD'` reporters (faithful alternative: NaN where
`fxusd != 1`, ~3.5% of ART rows overall; the checker measures the universe share).
Deviations: (a) `dc`, `dvpa`, `tstkp` always 0 (`dc` = convertible debt is the only one of size); (b) `debt` replaces
`dltt + dlc`: it INCLUDES operating-lease liabilities (ASC 842 break in FY2019 filings) and bank repo, and is populated
for financials where `debtc`/`debtnc` are ~20% null (OSAP's are NaN when blank; the NaN-propagating `debtc + debtnc`
is stricter-faithful but drops that ~20%); (c) `equity` includes preferred (OSAP `ceq` excludes it); (d) `che` includes
financing receivables for captive-finance names and understates for banks/insurers; (e) book side is the latest
quarter, not the 6-17-month-old fiscal year; (f) `mve_permco` multi-class as in the map (all-class shares at the
primary's price); (g) the price>=5 filter and OSAP's annual-June rebalance (Portfolio Period 12, Start Month 6)
are not reproduced.
Fields not in the map: none. Correction owed to the map: `compustat.dc` description (convertible debt, not deferred
charges). `FactorDef`: dimension ART (default), no `history_months`, `family=None` until Phase C.
