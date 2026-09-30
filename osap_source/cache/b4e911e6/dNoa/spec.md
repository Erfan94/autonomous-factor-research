# dNoa — Change in net operating assets (Hirshleifer, Hou, Teoh, Zhang 2004, JAE, Table 7B DeltaNOA)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/dNoa.py` (cached `predictor.py`; upstream
`upstream_CompustatAnnual.py`). DATA_SHA 198b281de1a0. Construction only. Compared with the reviewed
`factors/candidates/NOA.py` (same paper, same NOA level; dNoa is the 12-month change in the level over lagged `at`).
Measured on the harness universe, ALL 276 decision months (signal 1998-12-31 .. 2021-11-30), SF1 ART via
`fundamentals_yoy`.

## 1. Data availability (verdict: APPROX — no input missing; every non-exact term is OSAP's own zero-fill or a declared scope deviation)
| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `at` | `compustat.at` | `assets` | mapped | not filled; NaN -> NaN; `at_lag12` NaN or 0 -> NaN |
| `che` | `compustat.che` | `cashneq + investmentsc.fillna(0)` | approx | ZERO-FILLED upstream |
| `dltt` | `compustat.dltt` | `debtnc` | approx (ASC 842) | zero-filled BY THE PREDICTOR |
| `dlc` | `compustat.dlc` | `debtc` | mapped | zero-filled BY THE PREDICTOR |
| `mib` | `compustat.mib` | `assets - liabilities - equity` (residual) | approx | ZERO-FILLED upstream |
| `pstk` | `compustat.pstk` | absorbed in `equity` (SF1 equity includes preferred); not separately needed | unavailable, eliminated algebraically | zero-filled BY THE PREDICTOR (moot) |
| `ceq` | `compustat.ceq` | `equity` | approx | not filled; NaN -> NaN |
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt. The only unavailable input (`pstk`) needs no value here (it is eliminated by the algebra below and OSAP zero-fills it anyway), so the verdict is `approx`, not `infeasible`.
- TRAP vs the brief: `dNoa` does NOT use `dc` (convertible debt); that is NOA. Its `dlc` is debt in current liabilities (the SignalDoc text "deferred charges (dlc)" is a mislabel; code: `for var in [dltt, dlc, mib, pstk]: fillna(0)`). `dlc` maps cleanly to `debtc`, and there is no convertible-debt term to set to zero.
- ALGEBRA. OA = at - che; OL = at - dltt - mib - dlc - pstk - ceq; NOA = OA - OL = dltt + dlc + mib + pstk + ceq - che. Compustat mib + pstk + ceq ~ at - lt, so with mib := assets - liabilities - equity and ceq := equity (pstk inside `equity`: OSAP's OL subtracts pstk, so preferred is on the financing side in OSAP too) the equity terms cancel: `NOA_level = debtnc + debtc + (assets - liabilities) - che`. SF1.equity is not an input. dc, txp, ppegt etc. are not needed.
- Unclassified balance sheets (financials/REITs: `debtc`/`debtnc`/`investmentsc` null, ~19% of the filed universe) are a different statement format. OSAP's own `fillna(0)` of dltt/dlc would keep those filers in; the project ruling (field_map, translator rule: zero-fill only a real zero, never a different-format block) is to gate them NaN, as NOA.py does (`debtc.notna() & debtnc.notna()`). This is a stated deviation and the main coverage loss. Measured: share of the universe with a filing but null debtc/debtnc: median 18.7%, min 13.0%, max 21.7%. `cashneq` null -> NaN (OSAP zero-fills che).

## 2. Variables (exact source names)
`at, che, dltt, dlc, mib, pstk, ceq` (`m_aCompustat`, annual, $ millions); derived `tempOA, tempOL, tempNOA, at_lag12, dNoa`.

## 3. Formula in words and key lines
Net operating assets at the current fiscal year-end minus the same a year earlier, divided by total assets a year earlier.
```
tempOA = at - che ;  tempOL = at - dltt - mib - dlc - pstk - ceq   (dltt, dlc, mib, pstk filled 0)
tempNOA = tempOA - tempOL
dNoa = (tempNOA - tempNOA_lag12) / at_lag12        # NaN if either lag is NaN or at_lag12 == 0
```
Harness: `y = ctx.fundamentals_yoy(["assets","liabilities","debtnc","debtc","cashneq","investmentsc"])` (ART);
`noa = debtnc + debtc + (assets - liabilities) - (cashneq + investmentsc.fillna(0))` evaluated on the current and `_lag` sets; `dNoa = (noa - noa_lag) / assets_lag.where(assets_lag > 0)`; NaN where debtc or debtnc is null on EITHER side; inf -> NaN. Score `ascending=False`. Same-currency ratio (all reporting currency): no fxusd gate.

## 4. Timing / lag convention
OSAP: annual balance sheet at `datadate + 6 months`, held 12 months; the lag is the prior annual row (exactly one fiscal year). Here: latest ART filing known at the signal (datekey <= signal, <= 15 months old) against the same fiscal period one year earlier, aligned by reportperiod (45-day tolerance). The span is four quarters refreshed quarterly, not the fiscal year; 0-3 months fresher than OSAP's 6-17. Levels only (ART == ARQ on the same reportperiod): no flow, no TTM smear, no `dimension=ARQ`. Stale or missing year-ago period -> NaN (never 0), via `fundamentals_yoy`; never `fundamentals(lag_months=12)`.
ASC 842: `debtnc` and `debtc` absorb operating-lease liabilities from the adoption filing (FY2019 calendar filers); `assets` (right-of-use) and `liabilities` rise by the same amount, so `assets - liabilities` is unchanged but `debt` rises: NOA_level steps UP by ~lease/assets for lessees, and the year-over-year change carries a one-off lessee spike in 2019-2021 signal months. Compustat's dltt/dlc exclude operating leases, so OSAP's dNoa has no such step. Declared, not adjusted (3 of 23 window years).

## 5. Filters
None in the predictor; SignalDoc `Filter` blank. Harness universe only.

## 6. Predicted sign
SignalDoc `Sign = -1.0` (T-Stat 8.85, mv reg, EW; Return blank): growth in net operating assets predicts LOWER returns; long LOW dNoa, `ascending=False`. SignalDoc Notes: "Seems to be monthly ... minimum 4 month lag."

## 7. The mass-point question
Continuous difference-of-levels ratio. A do-nothing firm (balance sheet unchanged over 12 months) gives exactly 0, essentially a stale-filing artefact, which `fundamentals_yoy` converts to NaN. The fills (che partly filled; no dc term) are components, not the signal, and do not tie a difference. Standing tie rule for change-in-level signals: no noise-breaking, harness average rank, no mass point expected. Measured over 276 months on the scored cross-section: exact-zero share median 0.000%, mean 0.016%, max 0.136% (<= 2 names); modal share median 0.068%, max 0.144%; distinct values equal n scored (nearly); qcut 10 bins in 276 of 276 months. Tie handling: none needed.

## 8. History needed (snapshot starts 1998-01)
Needs a year-ago filing: SF1 starts 1997Q4, so the first months are thin (same pattern as NOA). Year-ago period present for universe names: 48.6% (1998-12), 50.0% (1999-01), 57.3% (1999-02), 89.1% (1999-03), median 96.9%. dNoa scored share of the universe: min 37.7% (1998-12-31), 39.3% (1999-01), 45.7% (1999-02); 2 of 276 months < 40% (first two signals); from 1999-03 min 70.4%, median 77.9%, mean 77.8%, max 82.0%. Scored n min 861, median 1,472, max 2,090. `lookback_months` 31 as NOA.

## 9. OSAP metadata
dNoa; Hirshleifer, Hou, Teoh, Zhang 2004 JAE; Cat.Signal Predictor; Cat.Form continuous; Cat.Data Accounting; Cat.Economic investment; Sample 1964-2002; Key Table "7B DeltaNOA"; Test mv reg; Evidence "t=8.9 in mv reg"; Predictability 1_clear; Rep Quality 1_good; Sign -1.0; T-Stat 8.85; EW; Portfolio Period 1; Start Month 6; GScholar cites 1,136. Definition: 12-month growth in Net Operating Assets scaled by lagged total assets (at); operating assets = at - che; operating liabilities = at - dltt - mib - dlc - ceq - pstk; all items except at and ceq replaced with 0 if missing.

## 10. Proposed Sharadar mappings with deviations
```
y = ctx.fundamentals_yoy(["assets","liabilities","debtnc","debtc","cashneq","investmentsc"])   # ART, lookback 31
noa(s) = debtnc_s + debtc_s + (assets_s - liabilities_s) - (cashneq_s + investmentsc_s.fillna(0))   # s in {now, _lag}
dNoa = (noa - noa_lag) / assets_lag.where(assets_lag > 0) ; NaN where debtc/debtnc null either side ; ascending=False
```
Deviations vs OSAP: (a) dltt/dlc zero-fill NOT applied: the unclassified block (~19% of the filed universe: financials/REITs) is NaN (coverage ~78%); (b) `pstk` is not a deviation (preferred is financing-side in OSAP and in SF1 `equity`); `mib` -> `assets - liabilities - equity` leaves only redeemable NCI and temporary/SPAC equity on the financing side here where OSAP (non-redeemable mib only) leaves them in OL, so NOA_level is higher by those amounts; they largely cancel in the 12-month change except across SPAC issuance/redemption 2019-23; (c) `che` = cashneq + investmentsc.fillna(0): overstates for captive-finance/vendor-financing names (investmentsc holds current financing receivables); cashneq null -> NaN; (d) ASC 842 lessee step 2019-2021 (section 4); (e) four-quarter rolling change refreshed quarterly vs fiscal-year change held 12 months; no 6-month lag; (f) `at_lag12 > 0` guard (OSAP only excludes 0); (g) upstream row filter (at, prcc_c, ni non-null) not reproduced. Versus NOA.py: adds `debtc` (dlc) to the financing side, has no dc term, and differences the level before scaling. Fields not in the map: none (pstk and dc unavailable, handled above).
Recommendation: **approx** — translate and preflight (expect coverage < 40% at the first two probes only, a warn, not a hard fail).

## Addendum 2026-09-30 — no debtc gate
Coordinator decision dnoa_debt_no_gate: the predictor zero-fills dltt/dlc (predictor.py:64-65), so the translation reads SF1.debt with a zero-fill and no debtc/debtnc gate; unclassified balance sheets are scored. The coverage and mass-point figures above were measured on the gated variant; preflight re-measures.
