# DivOmit — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: APPROX on data (constructible from ACTIONS; `distcd` filter not reproducible); INFEASIBLE FOR SCREENING (recommend `infeasible`): ~5 positive names per month
| OSAP input | Sharadar | status |
|---|---|---|
| CRSP `divamt` (`CRSPdistributions`, `exdt`) | `ACTIONS.value`, `action == 'dividend'` | field_map `crsp.divamt` approx; date = ex-date (KO 2019-03-14 ACTIONS row coincides with the SEP closeadj/closeunadj step) |
| `cd2` in (2, 3) | none: `distcd` unavailable | not reproducible; ACTIONS is cash dividends only. Not OSAP-zero-filled; approx by the same judgement as DivInit (owner may rule infeasible) |
| `permno, time_avail_m, exchcd, shrcd` | SEP presence x universe, TICKERS.category | harness-side |
- ID mapping validated against SF1 `dps` on the universe (see DivInit spec section 1): "paid in 12m" agrees with `dps > 0` on 98.1-99.9% of names; panel = universe x ACTIONS (absence = non-payer), never ACTIONS alone.
  `ctx.actions("dividend", months_back)` exists; aggregate to calendar months on `date`.
- The infeasibility is the measured event count, not a missing field (section 7). No IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob or ppegt input.

## 2. Variables (predictor.py)
`CRSPdistributions` (permno, exdt, cd2, divamt); `SignalMasterTable` (permno, time_avail_m, exchcd, shrcd); `asrol` calendar-month rolling.

## 3. Formula
Per-month `divind = (divamt_m > 0)`. Three payer definitions (quarterly, semi-annual, annual), each:
```
sumW      = rolling W-month sum of divind              (W = 3, 6, 12; min_samples=1)
temppaid  = (sumW == 1)                                # exactly one payment month in the window
temppayer = (rolling L-month mean of temppaid == 1)    # L = 18 (W=3, 6), 24 (W=12), min_samples=1
omit_W    = (sumW == 0) & (sumW.shift(1) > 0) & (temppayer.shift(W) == 1)
omitnow   = omit_3 | omit_6 | omit_12
DivOmit   = (rolling 2-month sum of omitnow == 1)      # an omission in t-1..t (an omission in both months sums to 2 and is dropped)
```
A regular payer (quarterly or semi-annual for 18 months, annual for 24) that fails to pay over the past quarter / half-year / year. Binary 0/1. The `sum == 1` definition breaks if two ex-dates fall in one window (date drift).

## 4. Timing / lag
OSAP: event month = month of ex-date; signal at t used for return t+1; held 2 months. Harness: ACTIONS `date <= signal_asof`; omission is defined by ABSENCE of a dividend, so the flag is known only after the full window closes without one (an ex-date that never comes is revealed at the end of the month) - no lookahead, but the OSAP signal is month-end-of-absence, same here. No SF1; no ART/ARQ issue.
Strict windows (all required months inside ACTIONS coverage from 1998-01; OSAP `min_samples=1` lets short history through).

## 5. Filters
SignalDoc Filter `shrcd <= 11`: absorbed by the harness universe (Domestic Common Stock*, NYSE/NASDAQ/NYSEMKT). No NYSE/AMEX requirement (OSAP deviation). Not filtered to "existed > 1 year" (predictor.py comment).

## 6. Predicted sign
`Sign = -1.0` (Michaely, Thaler, Womack 1995, Table 3 omit, t = 6.33; 0.917% monthly): omissions earn lower returns; short the omitters (OSAP's own portfolio is short omitters, long EW CRSP).

## 7. Mass-point question
Do-nothing firm = 0. Measured on the universe, strict windows, decision months 1999-11 .. 2021-12 (265): ones mean **0.37%** of members (7.2 names/month; median 5; max 73 in 2020), 206 of 265 months < 10 ones, 112 < 5, 3 months with zero.
Names by leg per month: quarterly `omit_3` 3.7, semi-annual `omit_6` 0.05, annual `omit_12` 0.05 (the `o3` leg dominates). Year means: 1999-2001 10-14, 2002-2015 3-10, 2020 19.9.
- 99.6% at 0 -> preflight hard fail (>= 10% cliff, `qcut` 2 bins); the short bucket is far under the >= 30 names per decile floor in every month; SignalDoc itself notes "very few stocks in the omission portfolio".
- Tie handling: binary, average rank; IC computable but dominated by the zeros; LS bars undefined. Recommend `infeasible` for screening.

## 8. History needed (snapshot starts 1998-01; ACTIONS 1997-12 is a 19-row stub)
First month each leg is computable with a strict window: `omit_3` **1999-11**, `omit_6` **2000-05**, `omit_12` **2001-11**; the two-month OR `DivOmit` is defined (with the legs available so far) from 1999-11, i.e. **265 decision months 1999-11 .. 2021-12**; with all three legs from 2001-11: **241 months** (mean 6.7 ones, median 5, 197 < 10, 3 zero).
`history_months` not needed (no return window); `lookback_months` = 36 (annual leg: 24-month payer window ending t-12).

## 9. OSAP metadata
Michaely, Thaler and Womack (1995), JF; Cat.Data Event; Cat.Economic payout indicator; discrete; sample 1964-1988; Acronym2 DivOmit; Portfolio Period 1, Start Month 12; EW;
Key Table "3 omit, to Day 254"; 1_clear / 2_fair. Hold 2 months (performance concentrated early). Source `Signals/pyCode/Predictors/DivOmit.py`.

## 10. Proposed Sharadar mappings (if the owner overrides the recommendation)
Same panel as DivInit: `divind_m` = any ACTIONS dividend row (`0 < value <= 10*close`) in the calendar month (ID, month), universe x ACTIONS; NaN until the strict window is full;
legs as in section 3 via calendar-month rolling sums; `DivOmit` null before 1999-11 (or 2001-11 for the full three-leg form). Declare `ACTIONS.value`, `ACTIONS.action` in inputs.
Deviations: `distcd` filter unavailable; strict windows vs `min_samples=1`; ex-date jitter across a month boundary (Dec 31 / Jan 2) creates spurious `sum == 2`/`0` windows in both OSAP and here. Fields in map: `crsp.divamt`.
