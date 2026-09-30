# EBM — Enterprise book-to-market (Penman, Richardson and Tuna 2007, Table 4A; SignalDoc "Enterprise component of BM")

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/ZZ1_EBM_BPEBM.py` (cached `ZZ1_EBM_BPEBM.py` and
`predictor.py`, byte-identical to the copy cached under BPEBM; one script emits EBM and BPEBM). DATA_SHA 198b281de1a0.
Written fresh from the source and `field_map_index.yaml`. Sibling spec and translation: `BPEBM/spec.md`, `factors/candidates/BPEBM.py`.

## 1. Data availability (verdict: APPROX, feasible; identical input set to BPEBM, no unavailable core input)

| OSAP input (`m_aCompustat`) | field_map key | Sharadar | map status | OSAP missing-item rule |
|---|---|---|---|---|
| `ceq` | `compustat.ceq` | SF1 `equity` (ART) | approx | not zero-filled (NaN) |
| `che` | `compustat.che` | SF1 `cashneq + investmentsc.fillna(0)` | approx | zero-filled |
| `dltt + dlc` (only as a sum) | `compustat.dltt_plus_dlc` | SF1 `debt` (ART) | mapped | not zero-filled (NaN) |
| `dc` (CONVERTIBLE debt, not deferred charges) | `compustat.dc` | none -> 0 | unavailable | zero-filled |
| `dvpa` | `compustat.dvpa` | none -> 0 | unavailable | zero-filled |
| `tstkp` | `compustat.tstkp` | none -> 0 | unavailable | zero-filled |
| `mve_permco` (SignalMasterTable) | `crsp.mve_permco` | DAILY.marketcap x1e6 = `ctx.universe["mkt_cap_usd"]` | approx | SMT row required |

- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt. `dc`, `dvpa`, `tstkp` are in OSAP's
  `zero_fill_vars` (`upstream_CompustatAnnual.py` of BPEBM cache), so dropping them is allowed: APPROX, not infeasible.
- The code is the authority: it divides by `mve_permco` (company-level cap); the SignalDoc text says `mve_c`. Use the map's `mve_permco` mapping.
- Field-checker (THIS snapshot): `compustat.ceq`, `compustat.che`, `compustat.dltt_plus_dlc`, `compustat.curcd`, `crsp.mve_permco`;
  BPEBM's checks cover the same fields (map entries verified_on 2026-09-30 for ceq/che/dltt_plus_dlc/mve_permco). Nothing new to verify beyond the EV guard counts.

## 2. Variables (exact source names)
`ceq, che, dltt, dlc, dc, dvpa, tstkp` (Compustat annual, $ millions), `mve_permco` ($ millions, month t), `permno, time_avail_m`.

## 3. Formula
```
temp = che - dltt - dlc - dc - dvpa + tstkp          # net financial assets T
EBM  = (ceq + temp) / (mve_permco + temp)            # enterprise book / enterprise value
```
With dc = dvpa = tstkp = 0: `T = che - debt`, `EBM = (ceq + T) / (M + T)`. The denominator IS enterprise value `M + T`.
No guard in OSAP (`inf`/negative kept, no non-finite filter in `upstream_save_standardized.py`). Algebraically `EBM = BP - BPEBM`
for the same inputs, so EBM is book-to-price with the leverage effect of T removed, and is strongly tied to plain book-to-price.

## 4. Timing / lag convention
- OSAP: annual items available at datadate + 6 months, held 12 months (latest datadate wins); `mve_permco` is month t, so the
  two legs are misaligned by 6-17 months. The signal moves monthly with price.
- Here: `ctx.fundamentals(["equity","debt","cashneq","investmentsc","fxusd"])` at the as-of (ART; all are balance-sheet LEVELS, ART==ARQ
  for the same period). Book side is the latest filed quarter (0-3 months old, cap `max_fundamental_age_months` = 15) vs 6-17 months; `M` is
  `mkt_cap_usd` at the same month-end. No flow item, no year-over-year difference: no smear, no `dimension=ARQ` override.

## 5. Filters
- SignalDoc `Filter` `abs(prc)>5` is portfolio-stage, not in `predictor.py`; not reproduced (universe is price >= $1; factors may not filter).
- NaN rules in OSAP: any of `ceq, che(after zero-fill), dltt, dlc` NaN -> EBM NaN (dltt/dlc are not zero-filled). Implicit: annual row needs
  non-null `at, prcc_c, ni`, `curcd='USD'`, CCM link, SMT row (shrcd 10/11/12, exchcd 1/2/3). No financials exclusion (within-sector ranking absorbs level).

## 6. Predicted sign
SignalDoc `Sign = +1.0` (high EBM -> high future return), `Stock Weight` EW, `LS Quantile` 0.1, `Cat.Form` continuous, `Cat.Economic` valuation.
Orientation: long HIGH EBM (D10), short LOW. `FactorDef(ascending=True)`.

## 7. The mass-point question
- A do-nothing firm (no new filing) holds `ceq, che, debt` fixed but `M` changes every month, so EBM changes continuously: no stale-value mass point.
- Exact 0 needs `ceq + T = 0` to the dollar: effectively never. Expected modal share of any single value ~0% (< 0.1%); ties: none, rank(method="average").
- The real risk is the TAIL. `M + T -> 0+` makes |EBM| huge and positive (top of the rank); `M + T <= 0` (cash exceeds market cap plus debt, i.e. `T >= M`)
  FLIPS the sign of the denominator, so a deeply overcapitalised firm would rank as if it were cheap. For BPEBM the EV > 0 guard was an addition;
  for EBM the denominator IS EV, so the guard is the sign-flip fix itself: names with `M + T <= 0` (or `M <= 0`) -> NaN. Preflight to report the
  share removed (not measured here; expected small, concentrated in cash-rich small-cap tech/biotech, 1999-2001 especially) and the p1/p99 of EBM.
  Numerator `ceq + T` may be negative (negative book or net debt above equity): keep it, as OSAP does. Do not winsorise or log.
- Coverage bounded by the filing-age cap and `equity`/`debt`/`cashneq` populated (~99.9% of ART rows); `che` zero-fill keeps financials/REITs (understated `che`).

## 8. History needed (snapshot starts 1998-01)
One latest filing plus current market cap; no return window, no `history_months`, no `lookback_months` beyond the filing-age cap. SF1 ART levels from
1997Q4 (level items populated; the ~50% ART-flow gap for 1998Q1-Q3 concerns flows only), DAILY from 1998-12-01: 1999-01 is covered.

## 9. OSAP metadata (SignalDoc)
Acronym EBM; Acronym2 BMent; Penman, Richardson and Tuna; 2007; JAR; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good;
Cat.Form continuous; Cat.Data Accounting; Cat.Economic valuation; SampleStart 1963, End 2001; Key Table 4A NOA/P^NOA; Test double sort size adj;
Sign +1.0; Return 0.12; T-Stat 3.0; Stock Weight EW; LS Quantile 0.1; Portfolio Period 12; Start Month 6; Filter `abs(prc)>5`.
Definition: "(ceq + che - dltt - dlc - dc - dvpa + tstkp) / (mve_c + che - dltt - dlc - dc - dvpa + tstkp). Exclude if price less than 5."
SignalDoc Notes: enterprise = operating = NOA in OP, "this should be NOA/P^NOA"; the code (balance-sheet net financial assets) is the authority.

## 10. Proposed Sharadar mappings and deviations (reuse BPEBM's conventions verbatim)
```
ceq  -> SF1 equity (ART)                               [compustat.ceq, approx]
che  -> SF1 cashneq + investmentsc.fillna(0)           [compustat.che, approx; NaN only if cashneq NaN]
debt -> SF1 debt (ART) replaces dltt + dlc             [compustat.dltt_plus_dlc, mapped sum]
dc = dvpa = tstkp = 0                                  [zero-filled in OSAP; no Sharadar source]
M    -> ctx.universe["mkt_cap_usd"]                    [crsp.mve_permco, approx]
T = che - debt;  EV = M + T;  score = (equity + T) / EV,  ascending=True
guards: M > 0; EV > 0 (else NaN); fxusd == 1 (else NaN); non-finite -> NaN; negative equity kept
```
Deviations: (a) `dc` (convertible debt), `dvpa`, `tstkp` always 0; (b) `debt` INCLUDES operating-lease liabilities (ASC 842 break, FY2019 filings) and
bank repo, and is populated for financials where `debtc`/`debtnc` are ~20% null; the known-trap ruling "gate SF1.debt on debtc.notna()" would
drop that ~20% (mostly financials/REITs) to mimic OSAP's un-zero-filled dltt/dlc; BPEBM did NOT gate, so follow BPEBM for consistency and log it;
(c) `equity` includes preferred (OSAP `ceq` excludes it; a preferred-only book adjustment is approx per ruling `book_equity_preferred_terms`);
(d) `che` includes financing receivables for captive-finance names, understates for banks/insurers; (e) book side is the latest quarter, not the
6-17-month-old fiscal year; (f) `mve_permco` -> company-level DAILY.marketcap (other classes priced at the primary's price), few-% error on <=2% of names;
(g) EV > 0 guard and fxusd == 1 gate are additions (OSAP keeps only curcd USD reporters, no EV guard); (h) price >= 5 filter and the June annual
rebalance not reproduced. Fields not in the map: none. `FactorDef`: dimension ART (default), no `history_months`, `family=None` until Phase C.
Redundancy note (construction, not outcome): EBM = BP - BPEBM, so its ranks share most variance with plain book-to-price.
