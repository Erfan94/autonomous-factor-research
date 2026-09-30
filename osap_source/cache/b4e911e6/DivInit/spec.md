# DivInit — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: APPROX (constructible from ACTIONS; `distcd` filter not reproducible); NOT SCOREABLE as configured (binary, 1.3% ones)
| OSAP input | Sharadar | status |
|---|---|---|
| CRSP `divamt` (`CRSPdistributions`, `exdt`) | `ACTIONS.value` where `action == 'dividend'` (per-share cash, split-adjusted basis) | field_map `crsp.divamt` approx; date = ex-date (checked: KO 2019-03-14 ACTIONS row = the day SEP closeadj/closeunadj steps) |
| `cd2` in (2, 3) (CRSP distribution code, cash dividends) | none: `distcd` unavailable | NOT reproducible. ACTIONS carries cash dividends only (incl. special cash); stock dividends / other distributions never appear. Dividend-type mix differs at the margin. Not zero-filled by OSAP, so a strict reading of the rule says infeasible; judged approx because ACTIONS `dividend` IS the cash-dividend population and a filter replacement exists. Owner may rule otherwise. |
| `permno, time_avail_m, exchcd, shrcd` (SignalMasterTable) | SEP presence x universe, TICKERS.category | mapped / harness-side |
- **ID-mapping check (done)**: 54% of dividend rows have no ID under `ticker_map("ACTIONS")` (OTC/delisted-before-scope names), but for universe
  members the ACTIONS panel reconciles with SF1 `dps`: "paid in 12m via ACTIONS" vs `dps > 0` latest agree on 98.1-99.9% of dps-known names at
  2003-12, 2008-12, 2012-12, 2015-12, 2019-12; among DivInit=1 names 0 of 9-52 (dps-lag known) had `dps > 0` a year earlier; 0 of 1,740-2,005 names
  show `dps > 0` at both year-ago and now with no ACTIONS dividend in 24m. So no false initiations from ticker changes.
- **Panel rule**: the signal is presence-of-ACTIONS-row = "paid", absence = "did not pay" for a universe member (SEP present). Build it as universe x
  ACTIONS, never ACTIONS alone. `ctx.actions("dividend", months_back, fields=("value",))` exists (harness/data_layer.py ~3054, universe IDs, date in (signal-months_back, signal]).
  It windows by exact DateOffset on the month-end; aggregate to calendar months on `date` to match OSAP's `exdt` month. Drop `value <= 0` (0.002%) and vendor outliers (TOPS 2e14; cap `value > 10*SEP.close`).
- No IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob or ppegt input.

## 2. Variables (predictor.py)
`CRSPdistributions`: permno, exdt, cd2, divamt; `SignalMasterTable`: permno, time_avail_m, exchcd, shrcd. `asrol` helper (calendar-month rolling).

## 3. Formula
```
dist      = dist[cd2 in (2,3)]; time_avail_m = month(exdt); divamt_m = sum of divamt per (permno, month); NaN -> 0 for months on SignalMasterTable
divamt_sum = rolling 24-month sum of divamt (min_samples=1); divsum_lag1 = shift(1)
divinit_firstmonth = (divamt > 0) & (divsum_lag1 < 1e-10)
DivInit   = rolling 6-month MAX of divinit_firstmonth (min_samples=1)           # 1 if an initiation occurred in months t-5..t
```
A firm paying in month t after no dividend in the previous 24 months; the flag is held for 6 months. Binary 0/1.

## 4. Timing / lag
- OSAP: event month = month of ex-date (known 2-4 weeks earlier at declaration); OSAP uses the signal dated t to form the portfolio held in t+1. Signal held 6 months.
- Harness: ACTIONS `date <= signal_asof` (month-end), no further lag; an ex-date on the last business day is usable, as in OSAP. SF1 not used; no ART/ARQ issue.
- Convention to choose: OSAP's `min_samples=1` counts a firm whose history is shorter than 24 months (a newly listed payer, or a 1998-99 month with < 24 months of ACTIONS) as an initiation.
  Recommend the STRICT window (all 24 prior months inside ACTIONS coverage) and null (not 0) before 2000-01; the loosened version mislabels ordinary 1999 payers.

## 5. Filters
SignalDoc Filter `shrcd <= 11` (common stock): absorbed by the harness universe (TICKERS.category Domestic Common Stock*, NYSE/NASDAQ/NYSEMKT). OSAP deviation "no NYSE/AMEX requirement" also holds here.

## 6. Predicted sign
`Sign = +1.0` (Michaely, Thaler, Womack 1995, Table 3 init, t = 3.37 event study 12 months; 0.625% monthly). Initiations earn higher returns.

## 7. Mass-point question
A do-nothing firm (no initiation) = 0. **98.7% of the universe is 0** (ones: mean 1.30% of members, range 0.04-3.03%; mean 24.7 names/month, min 1, max 58,
19 of 263 months < 10 ones, 181 of 263 < 30, never zero). Initiation count by year (mean/month): 2000-02 11-13, 2003-05 34-45, 2009 8.7, 2011-15 28-41, 2020 12.3.
- Preflight hard fails (mode 98.7% >= 10% cliff; `qcut` returns 2 bins, not 10). The harness decile statistics (D10-D1, >= 30 names per decile) cannot
  express a binary event with ~25 positive names: the "1" bucket sits under the 30-name floor in 69% of months.
- Tie handling: binary; average rank puts 98.7% at one rank; IC is computable (point-biserial) but the LS bars are not. The caller decides whether this
  is a frontier row (`preflight_failed` with these numbers) or a harness question. Not reproduced: OSAP's own portfolio uses EW long-only event months.

## 8. History needed (snapshot starts 1998-01; ACTIONS dividends 1997-12-31 are a 19-row stub, real coverage starts 1998-01)
- Dividend panel: ACTIONS months 1998-01 .. 2021-12 (monthly counts stable 311-1,390 from 1998-01, quarter-end peaks; 1997-12 has 19 rows only).
- Strict 24-month no-dividend lookback needs 1998-01..1999-12 complete, so the FIRST valid initiation month is **2000-01**; decision months with a defined
  signal: **2000-01 .. 2021-12 = 263** of the 276 (1999-01..1999-12 = 12 months undefined/null, not zero). No `history_months` (no return window), `lookback_months` = 24 for the data-start check.
- Delisted-in-window firms vanish with the universe (survivorship handled by the harness), ACTIONS persists past delisting.

## 9. OSAP metadata
Michaely, Thaler and Womack (1995), JF; Cat.Data Event; Cat.Economic payout indicator; discrete; sample 1964-1988; Acronym2 DivInit; Portfolio Period 1, Start Month 12;
EW; Test event study 12 months; Key Table "3 init, to Day 254"; 1_clear / 2_fair. Source `Signals/pyCode/Predictors/DivInit.py`. Notes: hold 6 months (OSAP paper 12) since most
returns come in the first 6 months; no NYSE/AMEX requirement.

## 10. Proposed Sharadar mappings
`divamt_m` = sum of `ACTIONS.value` (action == 'dividend', `0 < value <= 10*close`) by (ID, calendar month of `date`), via `ctx.actions`; `paid_m` = `divamt_m > 0`. `first = paid_t & no paid in t-24..t-1`
(strict, all 24 months in coverage else NaN); `DivInit = max(first over t-5..t)`, NaN before 2000-01. Declare `ACTIONS.value` (and `ACTIONS.action`) in `FactorDef.inputs`, `lookback_months=24`.
Universe rows with no ACTIONS dividend in the window score 0, not NaN (ACTIONS covers every ticker in scope; see ID check).
Deviations: `distcd` filter unavailable; ACTIONS value is split-adjusted (irrelevant for the indicator); strict vs OSAP min_samples=1 window; `value` outliers capped.
Fields in map: `crsp.divamt`; ACTIONS `value`/`date`/`action` present (verified); `dps` only as cross-check.
