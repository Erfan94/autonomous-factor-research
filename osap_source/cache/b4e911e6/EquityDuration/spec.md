# EquityDuration — equity duration from a 10-year ROE/growth cash-flow projection (Dechow, Sloan and Soliman 2004, Table 6A HDMLD)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/EquityDuration.py` (cached `predictor.py`).
DATA_SHA 198b281de1a0. Coverage and tail figures below were measured on THIS snapshot (harness `build_universe` +
`MonthContext`, ART, PIT) with the proposed construction re-implemented offline in a scratch script.

## 1. Data availability (verdict: APPROX, feasible; no unavailable input, six stated deviations)

| OSAP input (`a_aCompustat`) | field_map key | Sharadar | map status | OSAP missing rule |
|---|---|---|---|---|
| `ceq` (+ one-year lag) | `compustat.ceq` | SF1 `equity` (ART), lag aligned by reportperiod | approx (incl. preferred) | NaN, row needs a lag |
| `ib` | `compustat.ib` (map says `netinccmn`; ruling: `netinccmn` is ibcom) | SF1 `netinc + netincdis` | approx | NaN; annual row needs non-null `ni` |
| `sale` (+ one-year lag) | `compustat.sale` | SF1 `revenue` (ART) | mapped | NaN growth -> 0 INSIDE OSAP (`fillna(0)`) |
| `prcc_f` x `csho` (fiscal-year-end ME) | `compustat.prcc_f` (approx), `compustat.csho` (mapped) | `SEP.close` at last trading day <= reportperiod (10-day tol) x SF1 `sharesbas` | approx | NaN |

- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt. `sale`, `ceq`, `ib` are not in OSAP's
  `zero_fill_vars`; nothing here is zero-filled except OSAP's own `growth.fillna(0)`, which is reproduced.
- FIELDS NOT IN THE MAP INDEX: `netincdis` (only the known trap `sf1_netincdis_sign_inverted`; ib = netinc +
  netincdis, never minus). Field-checker: re-confirm `netincdis` null share and sign on this snapshot. Also `SEP.close`
  (mapped under `crsp.prc`) and `fxusd` (mapped under `compustat.curcd`).
- `SF1.price` is NOT prcc_f (it is the close on the filing date, 30-100 days after period end; see `compustat.prcc_f`).
  The period-end route in the map is used. `sharesbas` is on today's split basis: pair ONLY with `SEP.close`
  (split-adjusted), never `closeunadj`.
- Measured, universe at probe months (n 1,947-2,674): ART coverage of the signal = 87.2% (1999-03), 89.8% (1999-06),
  84.2% (1999-12), 86.3% (2000-06), 94.4% (2001-12), 96.6% (2005-12), 97.3% (2012-12), 97.2% (2019-12). The shortfall
  in 1999-2000 is the year-ago filing missing (yoy lag present for only 85-92%; SF1 is thin before 1998). All far above
  the 40% bar.

## 2. Variables (exact source names)

`gvkey, permno, time_avail_m, fyear, datadate, ceq, ib, sale, prcc_f, csho` (annual Compustat, $ millions).
Constants: `autocorr_roe=0.57, cost_equity=0.12, autocorr_growth=0.24, longrun_growth=0.06`.

## 3. Formula

```
tempRoE   = ib / ceq_lag1                      # prior annual row (shift(1) by gvkey, NOT checked to be exactly one year)
g         = sale/sale_lag1 - 1                 # inf -> NaN; NaN is FILLED WITH 0 below
RoE_1     = 0.57*tempRoE + 0.12*0.43 ; RoE_t = 0.57*RoE_{t-1} + 0.12*0.43      (t=2..10)
g_1       = 0.24*g.fillna(0) + 0.06*0.76 ; g_t = 0.24*g_{t-1} + 0.06*0.76
BV_1 = ceq*(1+g_1); CD_1 = ceq - BV_1 + ceq*RoE_1 ; BV_t = BV_{t-1}(1+g_t); CD_t = BV_{t-1} - BV_t + BV_{t-1}*RoE_t
MD = sum_{t=1..10} t*CD_t/1.12^t ; PV = sum_{t=1..10} CD_t/1.12^t ; ME = prcc_f*csho
EquityDuration = MD/ME + (10 + 1.12/0.12) * (1 - PV/ME)
```
The signal is a fixed nonlinear function of three ratios only: RoE = ib/ceq_lag, g, and ceq/ME. Nothing else
enters. `g` enters through `g.fillna(0)` for the year-1 and later growth terms; `tempCD` (year 0) is computed but unused.
No guard, no winsorising in OSAP (`inf`/extremes are kept; `ME <= 0` or `ceq_lag = 0` are not guarded).

## 4. Timing / lag convention

- OSAP: annual items available at datadate month + 6, held for 12 months (latest datadate wins). At month t the
  inputs are 6-17 months old and ME is the FISCAL-YEAR-END market cap (stale), so the signal is constant for 12 months.
- Here (proposed): `ctx.fundamentals_yoy([...], years=1)` at ART: latest filed quarter's TTM `netinc`, `netincdis`,
  `revenue` and latest `equity`, `sharesbas`; `equity_lag`/`revenue_lag` = the filing four quarters earlier aligned
  by reportperiod (not by date). ME = `SEP.close` at reportperiod x `sharesbas` (period-end ME of the latest filing).
  ART-as-of-filing makes the inputs 0-3 months old (vs 6-17) and the signal updates quarterly (vs annually).
- Flow smearing: the two flow items (`ib`, `revenue`) enter as TTM level/TTM level-one-year-earlier ratios; the two
  TTM windows do not overlap (4 quarters apart), so no smear and no `dimension=ARQ` override. ROE denominator is
  `ceq_lag` one YEAR earlier, as OSAP. No year-over-year DIFFERENCE of a flow is taken.
- `history_months`: none as a return window; needs one year-ago filing (handled by the yoy alignment).

## 5. Filters

SignalDoc `Filter` is empty. OSAP's annual pipeline drops rows with missing `at`, `prcc_c` or `ni` and requires
`curcd='USD'`; here: NaN when `netinc`, `equity`, `equity_lag`, `sharesbas`, period-end close are missing, and gate
`fxusd == 1` (non-USD reporters 0.05-2.4% of members; 2.4% at 1999-12, 0.05% by 2019). `ME > 0` guard. No positive-book filter:
negative `ceq` (2-5% of members) and negative `ceq_lag` (2.2-4.8%) are kept as in OSAP (RoE flips sign there).

## 6. Predicted sign

SignalDoc `Sign = -1.0` (long duration earns lower returns). Orientation: long LOW EquityDuration (D1), short HIGH.
`Cat.Form` continuous; `Cat.Economic` valuation; `Stock Weight` VW, `LS Quantile` 0.2, `Start Month` 6.

## 7. The mass-point question

- A do-nothing firm (no new filing) keeps the same inputs, and ME here is the PERIOD-END ME (not month-t), so its value
  is unchanged between filings (up to 2 of every 3 months under quarterly filings). That is a cross-month staleness,
  not a cross-sectional mass point: the score is a continuous function of three ratios.
- Measured cross-sectional modal share after rounding to 8 dp: 0.04-0.06% at every probe month; 1,700-2,300 distinct
  values per month. No tie block; exact-zero not special. Ties: rank(method="average") default.
- The real risk is the TAILS, not a mass: measured min/max at probe months run from about -20,649 (1999-12) to
  +1.84M (2005-12); p1 = 2.3-9.7, p50 = 16.7-17.4, p99 = 24-46. Extremes come from `|ceq_lag|` near 0 (RoE blows up)
  and `ceq -> 0`. OSAP does not trim; within-sector percentile rank absorbs the magnitude, but the extreme
  ranks are occupied by near-singular names (both signs of the blow-up). No winsorising in the factor.
- Growth NaN share among scored names: 12.8% (1999-03), 48.8% (1999-06), 41.7% (1999-12), 9.3% (2000-06), 3.4-7.3% after
  2001 (prior-year ART revenue missing early in SF1). Those get `g = 0` as OSAP's own `fillna(0)` does; note this
  is a larger share than a full-history CRSP/Compustat sample and makes the 1999-2000 signal mostly RoE- and
  ceq/ME-driven.

## 8. History needed

One year-ago filing for `equity` and `revenue` plus a current filing: SF1 holds filings from 1993 but is thin before
1998 (yoy lag coverage 85-92% in 1999-2000, 95%+ from 2001). Snapshot starts 1998-01, so the first scored months are
thin, not empty. Period-end close needs SEP (from 1997-12).

## 9. OSAP metadata

`Cat.Signal Predictor`, `Cat.Form continuous`, `Cat.Data Accounting`, `Cat.Economic valuation`, Dechow-Sloan-Soliman 2004
(RAS), sample 1962-1998, `Predictability 1_clear`, `Rep Quality 1_good`, t = 4.37 (Table 6A HDMLD; OSAP uses VW
quintiles), `Sign -1`. `Portfolio Period` 12, `Start Month` 6.

## 10. Proposed Sharadar mappings and deviations

1. `ceq` -> SF1 `equity` (includes preferred; preferred not separable).
2. `ib` -> SF1 `netinc + netincdis` (ART). `netincdis` NOT in the map index (trap entry only). netinc is after NCI and
   before preferred dividends; if `netincdis` is unusable, fallback `netinc` (differs on ~11.7% of rows).
3. `sale` -> SF1 `revenue` (ART), yoy by reportperiod.
4. `prcc_f*csho` -> `SEP.close` at reportperiod x SF1 `sharesbas`; fxusd==1 gate; `ME>0`.
5. Quarterly ART update in place of OSAP's annual June-anchored update; ME is period-end, not contemporaneous.
6. OSAP `ceq_lag`/`sale_lag` = previous annual row (can span a gap year); here strictly 4 quarters earlier.
Field-checker: `netincdis`, `equity`, `revenue`, `sharesbas`, `netinc` on THIS snapshot (map notes quote DATA_SHA
198b281de1a0, same as the pin); `SEP.close` period-end match.
