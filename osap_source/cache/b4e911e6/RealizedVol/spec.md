# RealizedVol — Realized (total) volatility (Ang, Hodrick, Xing, Zhang 2006, Table 6A)

OSAP ref b4e911e69678a7424f318617a61d813f54183123 (config ref b4e911e6). Emitted by
`Signals/pyCode/Predictors/ZZ0_RealizedVol_IdioVol3F_ReturnSkew3F.py` (cached as `predictor.py`; there is no `RealizedVol.py`).
Authority is the SignalDoc row with `Cat.Signal == Predictor` (`signaldoc_row.csv`). The same script emits IdioVol3F and
ReturnSkew3F (sibling acronyms). Upstream read: `upstream_CRSPDaily.py`, `upstream_FamaFrenchDaily.py`. DATA_SHA 198b281de1a0.

## 1. Data availability (verdict: `feasible`; no missing input, no zero-fill; rf omission immaterial)

| input (OSAP) | field_map key | Sharadar source | status |
|---|---|---|---|
| `ret` (dailyCRSP) | `crsp.ret` | `SEP.closeadj[d] / closeadj[d-1] - 1` on the market calendar | mapped (total return, no dlret; closeadj 3-dp grid) |
| `rf` (dailyFF) | none (`public_sources`: rf NOT in snapshot) | omitted | unavailable, immaterial (see below) |
| `mktrf, smb, hml` (dailyFF) | none | NOT NEEDED | RealizedVol uses no factor (see 3) |

- Declare inputs: `SEP.closeadj` only. No `DAILY`, no `SF1`, no `ff3_daily`: unlike the IdioVol3F sibling, the smb/hml 1999-07 data
  start does not bind, so all 276 decision months are scorable.
- rf: the signal is std(ret - rf). rf is near-constant within a calendar month (~0-2bp/day, the harness's own note) and its
  day-to-day variation is orders of magnitude below daily stock volatility, so std(ret) equals it to rounding. Verdict `feasible`
  (`crsp.ret` is mapped; the rf omission is an immaterial, stated deviation, not an `approx` input).
- Not used: IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob, ppegt.

## 2. Variables (exact source names)

`ret`, `rf`, `time_d`, `permno` (dailyCRSP joined inner on `time_d` to dailyFF `[time_d, rf, mktrf, smb, hml]`); derived
`time_avail_m = time_d.dt.truncate("1mo")`, `ret = ret - rf`.

## 3. Formula in words and the key lines

The signal is the sample standard deviation (ddof = 1, polars `.std()`) of the stock's daily excess returns over the signal's
calendar month. NOTE: SignalDoc's Detailed Definition says "residuals from CAPM regressions", but the code's RealizedVol is the
plain std of `ret` (the regression residuals feed IdioVol3F, a different column). The code is the authority: RealizedVol is TOTAL
volatility, not idiosyncratic, and needs no factor regression.
```
df = crsp.join(ff, on="time_d", how="inner");  ret = ret - rf
... .filter(pl.col("ret").count().over(["permno","time_avail_m"]) >= 15)      # Bali-Hovakimian minimum
RealizedVol = pl.col("ret").std()  per (permno, time_avail_m)                   # raw; no log, no annualisation here
```
(The annualisation x sqrt(252) happens only in RIVolSpread.) In OSAP the std sits on rows that survive the FF3 regression's
null-residual drop and the >= 15 count; with the full CRSP/FF daily panel those add nothing beyond the 15-return rule.

## 4. Timing / lag

Signal month t uses the days of month t only (no rolling window), known at the month-end close; portfolio earns t+1; OSAP applies
no extra lag. Price-only: no filing date, no ART/ARQ choice, no flow item, nothing smears under TTM. Translator idiom (reuse the
reviewed IdioVol3F pattern, minus `ff3_daily`): `ctx.market_daily(45, col="vw")` index = market calendar; `ctx.daily("SEP",
["closeadj"], 45)` pivoted by ID, `px > 0`, reindexed onto the calendar, `ret = px/px.shift(1) - 1` (previous MARKET day, nothing
chained across a gap); keep the days of `ctx.signal_asof`'s month; >= 15 valid returns; `std(ddof=1)`. Skip months in
`ctx.partial_months("SEP")` (1997-12 stub, never reached).

## 5. Filters

None in the predictor (SignalDoc Filter empty); the harness universe and within-sector ranking apply on top.

## 6. Predicted sign

SignalDoc `Sign = -1.0`: high total volatility predicts LOW returns. `ascending=False`. Cat.Economic `volatility`, Cat.Data `Price`,
Cat.Form `continuous`. t = 2.86 (port sort, Table 6A), VW, LS quantile 0.2, Portfolio Period 1, Start Month 6.

## 7. The mass-point question

A do-nothing (flat-price) name produces exactly 0.0 (every daily return 0, std 0). Share: ~0. MEASURED on this snapshot, all 276
decision months (signals 1998-12-31 .. 2021-11-30), harness universe, prototype = the translation in 4 (no rf, no factors):
- exact zeros: 0 in every month; distinct values >= 99.9% of scored names; largest modal share 0.115% (2012-03-30), mean 0.065%;
- `qcut` yields 10 bins in all 276 months; no tie design needed (average rank). If a zero ever appears set it NaN (a stale price,
  not a measured risk), as the IdioVol3F translation does; it is a dead branch on this snapshot.

## 8. History needed and measured coverage

- 15 daily returns inside the month; the 15-return floor binds only in 2001-09 (15 trading days; all 2,142 scored names pass).
- `history_months=1` (a price at t-1 month, the return-window gate), `lookback_months=2` (the month plus the prior close).
- Coverage of universe names with >= 15 valid returns: mean 99.90%, min 99.26% (2000-02-29), 4 months below 99.5%; first signal
  1998-12-31 already 99.82% (2,277 scored). Scored names per month: min 1,737 (2012-03-30), median ~1,890; universe 1,739-2,867.
- Measured BEFORE the `history_months=1` gate (the gate can only lower it slightly; the same idiom carried the gate at ~99.9% in IdioVol3F).
- Measured on DATA_SHA 198b281de1a0, 276 of 276 months, harness `build_universe` (band hysteresis chain from the first panel month).
- Not data_start: no factor build, so nothing truncates the first months.

## 9. OSAP metadata

Acronym `RealizedVol`; LongDescription "Realized (Total) Volatility"; Authors Ang et al.; Year 2006; Journal JF; Sample 1963-2000;
Cat.Signal Predictor; Cat.Economic volatility; Cat.Data Price; Cat.Form continuous; Sign -1.0; Return 0.97; T-Stat 2.86; Key Table 6A;
Test "port sort"; Stock Weight VW; LS Quantile 0.2; Portfolio Period 1; Start Month 6; Acronym2 IdioVol; Predictability 1_clear;
Signal Rep Quality 1_good; GScholarCites 6,340. Also consumed as an input by RIVolSpread (annualised there).

## 10. Proposed Sharadar mappings and deviations

- `ret` -> `SEP.closeadj` day-over-day on the market calendar (`crsp.ret` mapped; total return, no delisting return; 3-dp grid
  quantises back-adjusted prices below $0.50).
- `rf` -> omitted (not in snapshot; constant within the month, std unchanged). `mktrf/smb/hml` -> not needed.
- Window: days of the signal's calendar month; >= 15 valid daily returns else NaN; `std(ddof=1)`; no annualisation.
- Overlap, stated for the record: same script and same daily-return panel as IdioVol3F; the two differ by the FF3 projection
  (RealizedVol keeps the market, size and value components). Whether it adds information is a Stage 2 question, not availability.
- No new field_map key. Fields for the field-checker: `crsp.ret` (daily form) only.
