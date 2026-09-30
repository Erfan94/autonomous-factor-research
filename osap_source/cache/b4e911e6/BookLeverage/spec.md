# BookLeverage -- Book leverage (Fama and French 1992, Table 3 Ln(A/BE))

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/BookLeverage.py` (cached
`predictor.py`, `signaldoc_row.csv`, `legacy.do`, `upstream_CompustatAnnual.py`). DATA_SHA 198b281de1a0.
Construction only.

## 1. Data availability (verdict: APPROX; no unavailable input beyond the preferred-stock adjustment)

| input (OSAP) | field_map key | Sharadar | status (verified_on 2026-09-30) | note |
|---|---|---|---|---|
| `at` | `compustat.at` | SF1 `assets` (ART) | mapped, verified | level; null 0.05%; universe coverage 97.5-100% |
| `seq` | `compustat.seq` | SF1 `equity` (ART) | mapped, verified | parent equity incl. preferred = the seq concept; null 0.05% |
| `ceq` | `compustat.ceq` | SF1 `equity` | approx, verified-with-deviation | same column as seq; only reached if seq null, so the branch is dead |
| `lt` | `compustat.lt` | SF1 `liabilities` (ART) | mapped, verified | only reached if equity null (0.05%) |
| `txditc` | `compustat.txditc` | SF1 `taxliabilities` | approx, verified-with-deviation | generic tax-liability line, not deferred tax + ITC; Sharadar zero-fills it (51.4% exact zero); OSAP also zero-fills it (`zero_fill_vars` and the predictor's `fillna(0)`) |
| `pstk`,`pstkrv`,`pstkl` | `compustat.pstk*` | none | unavailable | LOOP RULING `book_equity_preferred_terms` (events.jsonl): preferred only adjusts book equity -> approx |

- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt. Nothing is infeasible.
- Approx source: preferred stock is not separable in SF1. OSAP's denominator is
  `tempSE + txditc - tempPS`; Sharadar gives `equity + taxliabilities`, preferred not removed.
- Field-checker: all mapped keys already verified on THIS snapshot (2026-09-30); nothing further needed.
  All four SF1 inputs share the reporting currency, so the ratio is unit-free: no `fxusd == 1` gate (unlike AM).

## 2. Variables (exact source names)

`at`, `lt`, `txditc`, `pstk`, `pstkrv`, `pstkl`, `seq`, `ceq` from `m_aCompustat` (Compustat annual,
`datadate + 6 months`, replicated 12 months); keys `permno`, `time_avail_m`.

## 3. Formula

BookLeverage = at / book_equity, where
```
txditc = txditc.fillna(0)
tempPS = pstk; fill pstkrv; fill pstkl                    # NaN if all three missing
tempSE = seq; fill (ceq + tempPS); fill (at - lt)
book_equity = tempSE + txditc - tempPS
BookLeverage = at / book_equity   (NaN where book_equity == 0)
```
Behaviours that matter and that the Sharadar build cannot all reproduce:
1. **Negative book equity is kept**: no `book_equity > 0` filter, so negative-equity firms get NEGATIVE
   BookLeverage (the lowest values). Sign is -1 (see 6), so they land on the long side. Sharadar:
   liabilities > assets on ~6.3% of ART rows. Reproduce as is (do not mask); the per-sector rank puts them
   at the bottom. The translator must not add a positivity guard; only `== 0` -> NaN (and inf -> NaN).
2. **`tempPS` NaN gate**: if pstk, pstkrv and pstkl are ALL missing, `tempSE + txditc - NaN` is NaN, so OSAP
   drops the observation, even though `seq` exists. Compustat `pstk` is frequently blank for firms with no
   preferred (NOT in `zero_fill_vars`), so OSAP's sample is firms with a reported preferred item; the
   share is not measurable here (no pstk field). Sharadar computes for all firms with equity.
3. **Preferred removal**: when `seq` is used (the normal branch), OSAP subtracts preferred from seq (seq
   includes it), so its book equity is common equity + txditc; Sharadar `equity` keeps preferred.
   When the `ceq + tempPS` branch is used, preferred cancels exactly (ceq + PS - PS) -- dead here.
   Material only for firms with sizeable preferred.
4. `seq` and `ceq` null (Sharadar: same column, 0.05%) -> `at - lt`; here `assets - liabilities + taxliabilities`.

## 4. Timing and lag

- OSAP: annual balance sheet at `datadate`, available `datadate + 6 months`, held 12 months (latest datadate
  wins): the value is 6-17 months stale, changes once a year, NOT updated with price.
- Here: `ctx.fundamentals(["assets","equity","liabilities","taxliabilities"])` ART at the signal as-of,
  latest filing with `datekey <= signal_asof`, within `max_fundamental_age_months` = 15 (config). The value
  updates quarterly and is 0-3 months old; `yoy_by_report_period` ruling: OSAP's 6-month lag is not
  reproduced. ART-as-of-filing changes the signal by between-filing growth in assets and equity only.
- All four inputs are balance-sheet LEVELS (ART == ARQ ~99%): no TTM smear, no `dimension=ARQ`, nothing
  differenced year over year. Price-independent.

## 5. Filters

SignalDoc `Filter`, `Quantile Filter`, `LS Quantile`: blank; EW. No price/size/exchange/SIC filter in the
script (financials kept). Harness universe applies; sector ranks absorb the cross-sector leverage level.

## 6. Predicted sign

`Sign = -1.0` (SignalDoc): higher book leverage predicts LOWER returns (t = 5.34 in mv reg, 1963-1990).
Orient: long LOW BookLeverage (D10 after negation), short high.
The negative-equity firms (negative values) therefore sit on the LONG side (see 3.1). This is a quirk of
OSAP's unfiltered ratio; a flipped-sign screen would be a second hypothesis (|t| >= 2.74).

## 7. The mass-point question

A do-nothing firm (no new filing) carries the same value (annual in OSAP; quarterly-updated here), so the
signal is piecewise-constant in time but continuous across firms. No zero-fill default in the ratio: a firm
has `at` and an equity figure or is dropped. `txditc` is a mass point in the INPUT (51% exact-zero in SF1)
but only a small additive term, so the ratio is still continuous: ties negligible. Only exact ties:
`equity + taxliabilities == 0` (~0.01%, set NaN). Expected share at any single value ~0%. Ties: harness
default (average). Preflight should confirm coverage near the
universe (~97-100%, higher than OSAP's pstk-gated sample).

## 8. History needed

No return window: one latest filing; no `history_months`. ART levels ~99.9% from 1997Q4; universe ART
coverage 98.8% (1998-12), 97.5% (1999-12). The 15-month age cap drops stale filers (minor).

## 9. OSAP metadata (SignalDoc)

Cat.Signal Predictor; Cat.Form continuous; Cat.Data Accounting; Cat.Economic **leverage**; Fama and French
1992, JF; sample 1963-1990; Acronym2 BookLev; Key Table "3 Ln(A/BE)"; Test mv reg; T-Stat 5.34;
Predictability 1_clear; Rep Quality 1_good; Sign -1.0; EW; Portfolio Period 12; Start Month 6. Placebo BookLeverageQuarterly is a separate acronym.

## 10. Proposed Sharadar mappings and deviations
```
at   -> assets         (ART)   [compustat.at, mapped, verified]
seq  -> equity         (ART)   [compustat.seq, mapped, verified]   ceq -> same column, dead branch
lt   -> liabilities    (ART)   [compustat.lt, mapped, verified]   fallback only (equity null)
txditc -> taxliabilities.fillna(0)  [compustat.txditc, approx]
pstk/pstkrv/pstkl -> none; preferred not removed (ruling book_equity_preferred_terms)
BE = equity.fillna(assets - liabilities) + taxliabilities.fillna(0)
BookLeverage = assets / BE  (BE == 0 or non-finite -> NaN; negative BE kept)
orientation: sign -1 (long low)
```
Deviations (all stated, none blocks):
1. Preferred stock not removed from book equity: denominator slightly larger for preferred-issuers.
2. OSAP's hidden pstk-missing gate (sample = firms with a reported preferred item) not reproduced; Sharadar
   covers all firms with equity.
3. `taxliabilities` is a generic tax-liability line, not deferred taxes and ITC; 51% exact-zero mixes true
   zeros with Sharadar imputation.
4. Freshness: latest ART filing (0-3 months old) vs OSAP's annual + 6 months (6-17).
5. Negative-book-equity firms retained with negative values (faithful to OSAP), landing on the long leg.
6. Sector-relative ranks remove the across-sector level.

Fields NOT in the map: none. FactorDef: dimension default ART, no `history_months`, `family=None` until
Phase C (SignalDoc Cat.Economic = leverage).
