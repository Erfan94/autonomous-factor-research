# BMdec — Book to market using December ME (Fama and French 1992, Table 3 Ln(BE/ME))

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Signals/pyCode/Predictors/BMdec.py` (cached
`predictor.py`, `legacy.do`, `signaldoc_row.csv`). DATA_SHA 198b281de1a0. No upstream_* cached for BMdec;
intermediates `m_aCompustat` (zero_fill_vars read in `BPEBM/upstream_CompustatAnnual.py`) and `monthlyCRSP`.

## 1. Data availability — VERDICT: APPROX (constructible; preferred stock cannot be removed)

| OSAP input | field_map key | Sharadar | index status | note |
|---|---|---|---|---|
| `seq` | `compustat.seq` | SF1 `equity` (ART) | mapped | parent equity INCLUDING preferred; null 0.05% |
| `ceq` (fallback 1) | `compustat.ceq` | SF1 `equity` | approx | same column as seq: the `ceq + pstk` branch is dead code |
| `at`, `lt` (fallback 2) | `compustat.at`, `compustat.lt` | SF1 `assets`, `liabilities` | mapped | used only if `equity` null (0.05%) |
| `txditc` | `compustat.txditc` | SF1 `taxliabilities` | approx | generic tax-liability line, deferred-tax-like; 51.4% exact zero, Sharadar zero-filled |
| `pstk`, `pstkrv`, `pstkl` | same keys | NONE | unavailable | no SF1 field |
| `prc`, `shrout` -> Dec ME | `crsp.prc`, `crsp.shrout`, `crsp.me` | DAILY `marketcap` (millions USD) | mapped (me) / approx (shrout) | use DAILY.marketcap directly, one route |
| `permno`, `time_avail_m` | `crsp.smt_row` | SEP/DAILY presence | mapped | inner-merge gate only |

Why APPROX, not INFEASIBLE (conflict flagged for the caller):
- OSAP does NOT zero-fill `pstk`/`pstkrv`/`pstkl` (`zero_fill_vars` has txditc, not pstk; BMdec.py has no
  fillna(0) on them). Read literally, the stated rule "infeasible unless OSAP zero-fills" gives INFEASIBLE.
- field_map.yaml holds a standing ruling on `compustat.pstk`/`pstkrv`/`pstkl` (LOOP RULING 2026-09-25,
  process_finding `book_equity_preferred_terms`): when pstk only adjusts book equity (`seq + txditc - pstk`)
  the predictor is APPROX, preferred not removed; only a predictor whose SIGNAL is preferred stock stays
  infeasible. BMdec fits; batch 01's AccrualsBM dropped its unavailable adjuster the same way. Recommend
  APPROX. NOTE: `research/events.jsonl` has no `book_equity_preferred_terms` row (grep 0 hits); the ruling
  lives only in field_map.yaml, so the caller should confirm it binds.
- Deviation: Sharadar BE is too high by the preferred carrying value for preferred issuers (most firms: none).
- OSAP quirk: `tempBE = tempSE + txditc - tempPS` with `tempPS` NOT zero-filled, so if all three preferred
  items are missing, OSAP BE (hence BMdec) is MISSING. OSAP's sample is conditioned on a non-missing
  preferred item; Sharadar cannot reproduce that, so coverage is broader. Not measurable on this snapshot.
- `txditc` IS zero-filled by OSAP (CompustatAnnual zero_fill_vars AND BMdec.py `fillna(0)`): `taxliabilities`
  (itself zero-filled) is the same choice; its zeros mix genuine and imputed.
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt. Harness-only: shrcd, exchcd.

## 2. Variables (exact source names)

`txditc, seq, ceq, at, lt, pstk, pstkrv, pstkl` (m_aCompustat, $M); `prc, shrout` (monthlyCRSP, thousands); `time_avail_m`, `permno`.

## 3. Formula

BMdec = BE / ME_Dec. BE = SE + txditc - PS; SE = seq, else `ceq + PS`, else `at - lt`; PS = pstk, else
pstkrv, else pstkl. ME_Dec = `abs(prc)*shrout` in DECEMBER only (per permno), carried to every month of that
calendar year (`groupby(permno, year).transform("min")`). Key lines:
```
tempDecME = groupby(permno,year).min( where(month==12, abs(prc)*shrout) )
tempBE = tempSE + txditc - tempPS
BMdec = tempBE / l12.tempDecME if month >= 6 else tempBE / l17.tempDecME   (l12/l17 = row at t-12/t-17 months)
```
Raw ratio, not log (monotone: ranks, deciles, rank-IC identical). `DecME == 0` -> NaN. Negative BE is KEPT
(no positivity filter), so BMdec can be negative. Sharadar form:
`(equity.fillna(assets - liabilities) + taxliabilities.fillna(0)) / ME_Dec`, preferred not removed.

## 4. Timing and lag

- DENOMINATOR = a June-to-May rule. At month t in year Y, `l12.tempDecME` (Jun-Dec) is the December ME of
  Y-1 (row at t-12 is in Y-1, its year-min is Dec Y-1). For Jan-May, `l17` lands in Y-2, so Dec Y-2. Net:
  June Y through May Y+1 uses Dec Y-1 ME (FF 1992 convention). In `ctx.at_month_end` terms:
  months_back = m for m in Jun..Dec and m+12 for m in Jan..May (Jan 13, May 17, Jun 6, Dec 12), m = month of
  `signal_asof` (translator to confirm this matches OSAP `time_avail_m`).
- OSAP needs merged rows at t-12/t-17 and a December row that year; Sharadar needs a DAILY row near December month-end.
- Numerator in OSAP: annual BE available `datadate + 6m`, held 12 months (6-17 months stale). Here:
  `ctx.fundamentals(...)` ART at signal as-of (0-3 months stale, age cap `max_fundamental_age_months`=15);
  `ARY` is the closer-to-OSAP alternative. Recommend ART as in the Value leg, so Stage 2 isolates ME timing.
- Flow smearing: none. All SF1 inputs are balance-sheet LEVELS (ART==ARQ ~99%); no `dimension=ARQ`.
- Units: OSAP $M / $K (constant x1000, rank-neutral). Here BE raw USD; DAILY.marketcap is MILLIONS
  (harness scales only `mkt_cap_usd`; a lagged `at_month_end("DAILY", ["marketcap"], k)` read is raw
  millions: multiply by 1e6).
- ME scope: OSAP's ME is per PERMNO (one share class) against firm-level BE; DAILY.marketcap is
  company-level on the primary ticker (`crsp.mve_permco` note). For multi-class firms Sharadar is the
  consistent ratio; approx deviation, small share of names.

## 5. Filters
SignalDoc `Filter`, `Quantile Filter`, `LS Quantile`: blank. No price/exchange filter in BMdec.py. Harness
universe applies. Translator decision, state both readings: OSAP keeps negative BE (BMdec < 0 lands in D1
under ascending=True; ~6% of rows have liabilities > assets); the composite's Value leg drops `equity <= 0`.
Faithful = keep. Any BE > 0 filter must be logged as a deviation, not assumed.

## 6. Predicted sign
`Sign = 1.0`: higher BMdec predicts higher returns (1963-1990). Long D10, short D1. `ascending=True`. No flip.

## 7. Mass-point question
No single-value pile-up: continuous ratio; `equity == 0` 0.01% of non-null, `DecME == 0` 0.06% (NaN). A
do-nothing firm has BOTH numerator (between filings) and denominator (fixed June-May) frozen, so BMdec is
piecewise-constant within a year and ranks barely move month to month: very low turnover and near-identical
adjacent-month ICs by construction (fewer effective independent observations than 276; watch the NW t).
Changes occur at filings and June rollovers. Ties: harness default (average).

## 8. History needed
The denominator reaches Dec Y-2 for Jan-May: declare `lookback_months=17` (not a return window, so no
`history_months`); preflight checks it. `MonthContext.at_month_end(table="DAILY", ...)` exists in
`harness/data_layer.py`; no harness change needed. DATA-START GAP: DAILY.marketcap starts 1998-12-01, so
Dec 1998 ME is the first available and BMdec is fully formed from June 1999. Jan-May 1999 (5 of 276 decision
months) need Dec 1997 ME. Options: leave NaN (RECOMMENDED; preflight will warn) or fall back to SEP.close x
SF1.sharesbas at Dec 1997 (both on today's split basis per the `crsp.shrout` note; not closeunadj). ART levels
are ~99.9% populated from 1997Q4, so the numerator exists from 1999-01.

## 9. OSAP metadata

Cat.Signal Predictor; Cat.Economic valuation; Cat.Data Accounting; Cat.Form continuous; Fama and French 1992
(JF); sample 1963-1990; Evidence "t=5.71 in univariate reg"; Key Table "3 Ln(BE/ME)"; Sign 1.0; Return 0.5;
T-Stat 5.71; Stock Weight EW; Portfolio Period 12; Start Month 6; Predictability 1_clear; Rep Quality 1_good.

## 10. Proposed Sharadar mappings; difference from the composite's Value leg

Mappings: `seq/ceq -> SF1.equity` (fallback `assets - liabilities`); `txditc -> SF1.taxliabilities.fillna(0)`
(approx); `pstk/pstkrv/pstkl -> omitted` (preferred not removed); `December ME -> DAILY.marketcap at the
December business month-end via ctx.at_month_end`, x1e6. Fields not in the map: none.

Versus Value (`factors/composite.py` `_value`, osap_acronym BM):
1. Denominator: Value = signal-date `mkt_cap_usd` (moves monthly); BMdec = prior-December market cap, fixed
   June-May. The main difference.
2. Book equity: Value = `equity` alone; BMdec adds back `taxliabilities` (OSAP also subtracts preferred,
   not reproducible).
3. Non-positive BE: Value drops `equity <= 0`; BMdec as written keeps negative BE.
4. Numerator cadence is the same under the ART route, so ME timing separates the two; their rank correlation
   is a Stage 2 measurement, not asserted here.
