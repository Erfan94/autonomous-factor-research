# Coskewness — Systematic coskewness from monthly returns (Harvey and Siddique 2000, JF, in text p 1276)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/Coskewness.py` (cached `predictor.py`,
`signaldoc_row.csv`). Upstream `monthlyCRSP` / `monthlyFF` builders not cached; described from `predictor.py`.
DATA_SHA 198b281de1a0. field_map statuses are mappings, not proofs, until the field-checker verifies them.

## 1. Data availability — VERDICT: APPROX (every input constructible; declared substitutions; no zero-fill term)

| input (OSAP) | field_map key | Sharadar source | status | note |
|---|---|---|---|---|
| `ret` (monthlyCRSP) | `crsp.ret` (monthly form) | `ctx.monthly_closeadj(60)` ratio of adjacent business month-ends | mapped | total return (splits + dividends); NO dlret (`crsp.dlret` unavailable) |
| `mktrf` (monthlyFF) -> `mkt` | none; `public_sources` ruling | `ctx.monthly_market(60, col="vw")` (RAW VW, compounded from the guarded daily series) | harness accessor | Sharadar-native reconstruction (common stock on the universe exchanges, no size screen, no dlret, gap returns excluded), not FF Mkt-RF; RAW, not excess |
| `rf` (monthlyFF) | none (not in snapshot) | omitted | unavailable | see deviations: de-meaning removes a constant rf, but rf VARIES over a 60-month window |

- Declare `FactorDef.inputs`: `SEP.closeadj`, `DAILY.marketcap`.
- Not used: SF1, IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob, ppegt.
- Why APPROX: rf omitted (only its within-window variation matters, ~0.1-0.2%/month demeaned, versus ~10% stock and
  ~4.5% market monthly vol), a reconstructed VW market, no dlret, and a ramp of partial windows (section 8).

## 2. Variables (exact source names)
`ret`, `mktrf`, `rf` (monthly), `permno`, `time_avail_m`; derived `mkt = mktrf`, `ret = ret - rf`.

## 3. Formula
Per stock and per window of 60 CALENDAR months ending in month T (months T-59..T; a window exists only if the stock has a
row at T), on months with both returns present:
```
r  = ret - rf ;   m = mktrf                      # excess returns, raw monthly (simple, not log)
r~ = r - mean(r over the window obs);  m~ = m - mean(m over the SAME months)
Coskewness = mean(r~ * m~^2) / ( sqrt(mean(r~^2)) * mean(m~^2) )      # population (1/n) moments
keep only if nobs >= 12
```
This is ACX's formula on monthly data with OSAP's simple de-meaning (the SignalDoc notes OSAP says CAPM residuals but
de-meaning replicates closely). Translator equivalent: r from `monthly_closeadj(60)` adjacent-column ratios (61 columns; a
NaN column makes both adjacent returns NaN, never chain across a gap), m from `monthly_market(60, "vw")` (same month
index, NaN where < 15 market days or the 1998-12 stub); keep months where both are finite; n >= 12; non-finite result
(mean(r~^2) == 0 or mean(m~^2) == 0) -> NaN.

## 4. Timing and lag
Signal at month-end t uses the return through month t; the portfolio earns t+1. No extra lag (OSAP `time_avail_m` = T,
the return in month T is that month's). Price-only: no ART/ARQ issue, `dimension` default, nothing smears. `monthly_*`
accessors are bounded by `signal_asof`; no look-ahead.

## 5. Filters
OSAP file: `nobs >= 12`; inner merge with FF on month (mktrf, rf non-null). SignalDoc Filter `shrcd<=11` (common stock),
Stock Weight VW, LS Quantile 0.3 (tercile LS, value-weighted); the harness universe and decile sort supersede
(deviation). Start Month 12, Portfolio Period 1.

## 6. Predicted sign (SignalDoc)
`Sign = -1.0`: high coskewness predicts LOW subsequent return; `ascending=False`. Cat.Economic `risk`, Cat.Data `Price`,
Cat.Form `continuous`. Sample 1964-1993, T-Stat 1.96, Return 0.30 (% per month), "p-val<0.05 in long-short", Predictability
in OP 2_likely, Signal Rep Quality 1_good. Flipped sign = second hypothesis (|t| >= 2.74).

## 7. The mass-point question
Continuous ratio: no do-nothing value except a stock with zero variance over its window (all months return = rf), which
gives 0/0 -> NaN and is dropped, not a mass point. Exact ties ~0%. The monthly zero-return share of universe stock-months is
0.24-0.68% (field_map `harness-built series` note), so a window of identical months is essentially absent. Ties: rank
average (harness default).

## 8. History needed
- OSAP: window up to 60 months, minimum 12 valid months. Declare `history_months=12` (price within 7 days of t-12 months,
  i.e. 12 monthly returns possible) and `lookback_months=60`. Do NOT declare 60: a 60-month gate would null every name
  until 2003 (SEP starts 1997-12-31), which OSAP's 12-observation rule does not require.
- Measured constraints (from data_layer, not yet run): `monthly_market` is NaN for 1998-12 (stub), first valid market month
  1999-01. So 12 paired observations exist only from the 1999-12-31 signal; signals 1999-01..1999-11 (11 of 276 decision
  months, 4%) are unscorable for every name; the window is FULL (60 pairs) only from 2003-12; 1999-12..2003-11 rest on 12-59
  months (noisier; OSAP's own early-1960s years are the same). Preflight should report the first scorable month and the
  coverage ramp. Gap-month edge case in OSAP's batch labelling (a stock missing a month at T gets a label 60 months later)
  is ignored.

## 9. OSAP metadata
Acronym Coskewness; OSAP alias (Acronym2) Coskew; LongDescription "Coskewness"; Authors Harvey and Siddique; Year 2000;
Journal JF; Sample 1964-1993; Cat.Signal Predictor; Cat.Economic risk; Cat.Data Price; Cat.Form continuous; Sign -1.0;
Return 0.3; T-Stat 1.96; Key Table "in text p 1276"; Test LS port; Stock Weight VW; LS Quantile 0.3; Portfolio Period 1;
Start Month 12; Filter `shrcd<=11`. Notes: text reports 3.60% annual hedge return, p < 0.05, no table; ACX report private
conversations with Harvey about replicating it. Detailed Definition: sample counterpart of E[r~ m~^2]/(SD[r~] SD[m~]^2) with
de-meaned stock excess return and de-meaned market excess return, past 60 months of monthly data, NYSE/AMEX CRSP VW (msic).

## 10. Proposed Sharadar mappings and deviations
- `ret` -> `monthly_closeadj(60)` adjacent-month-end ratios (`crsp.ret` mapped); no dlret.
- `mktrf` -> `ctx.monthly_market(60, col="vw")`. Not in the index: a harness accessor; RAW not excess; reconstructed VW
  (common stock on the universe exchanges, no dlret, >+100% / <-80% daily prints dropped causally).
- `rf` -> omitted. Deviation: slightly larger than in the daily ACX signal because rf varies across 60 months
  (~5%/yr in 1999-2000 to ~0 in 2009-2015); measure in preflight by an in-harness check, do not assume it is nil.
- Calendar 60-month window with n >= 12 valid pairs; population moments as in OSAP; ranking is sector-relative in the harness.
- Fields not in the field map: none besides the harness accessors. Overlaps conceptually with `CoskewACX` (same ratio,
  daily 12m vs monthly 60m); a Phase C / Stage 2 concern, not a construction one.
