# Mom12mOffSeason — Momentum without the seasonal part: average return over months t-10..t-1 (Heston and Sadka 2008, JFE, Table 2 Year 1 Nonannual)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/Mom12mOffSeason.py` (cached `predictor.py`; upstream `upstream_SignalMasterTable.py`, `upstream_CRSPMonthly.py`, `upstream_stata_replication.py` beside it). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`.

## 1. Data availability (verdict: FEASIBLE, all inputs mapped; no data-start loss)

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `ret` (monthly total return incl. delisting return) | `crsp.ret` | SEP `closeadj` month-end ratios (`ctx.monthly_closeadj(11)`) | mapped | `fill_date_gaps` then `fillna(0)`: a missing month INSIDE a firm's life is 0; a lag BEFORE the first row is NaN and is skipped by the mean |
| delisting return (dlret, -0.35 / -0.55 rule in upstream) | `crsp.dlret` | none | unavailable | no delisting return in the past window here |
| `permno, time_avail_m`; shrcd 10/11/12, exchcd 1/2/3 | `crsp.shrcd`, `crsp.exchcd` | harness universe | approx | - |
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt; no SF1 input; no filing dates; no ART/ARQ question. closeadj is the total-return price.
- Data start: 11 closes (s-11..s-1). Measured on the harness universe, all 276 decision months (1999-01 .. 2021-12; universe 1,739-2,867): full-window scored names 1,693-2,480, coverage 86.4%-99.6% (mean 96.7%). Floor 120 met with 276.

## 2. Variables (exact source names)
`permno, time_avail_m, ret`; derived `ret_lag1 .. ret_lag10` (the `off_season_lags` list), `Mom12mOffSeason`.

## 3. Formula in words and key lines
Arithmetic mean (not compounded) of the ten monthly returns of months t-10..t-1.
```
off_season_lags = [lag for lag in range(1, 11) if (lag + 1) % 12 != 0]
df["Mom12mOffSeason"] = df[[f"ret_lag{n}" for n in off_season_lags]].mean(axis=1)     # pandas skipna
```
The "exclude the same calendar month" clause is vacuous here: `range(1, 11)` is lags 1..10, and lag 11 (the same calendar month as the predicted month t+1) is already outside it, so every lag 1..10 is kept. Month t (lag 0) is skipped as in the other OSAP momentum signals.
Harness form: `px = ctx.monthly_closeadj(11)`; ret_k = px[BME(t-k)] / px[BME(t-k-1)] - 1 for k = 1..10 (11 closes); mean of the ten.
PARTIAL WINDOWS (OSAP-literal): `mean(axis=1)` skips NaN, so a firm with only 3 prior rows is scored from 3 returns. Measured on the harness universe: names with some but not all ten returns are on average 59 per month, 2.8% of scored names. The harness gate `history_months = 11` nulls them. This is a deviation, stated; the translator should choose it knowingly. A missing interior close makes that return NaN here, whereas OSAP would have zero-filled it.

## 4. Timing / lag convention
Signal dated t uses returns of t-10..t-1, holding t+1. No filing dates, no flow items. `partial_months` irrelevant (point reads of month-end closes).
Overlap with the v0 Momentum leg (composite.py `_momentum`: closeadj[t-1]/closeadj[t-12]-1, return months t-11..t-1): this window (t-10..t-1) is the same window minus month t-11, arithmetic mean instead of compound. Measured cross-sectional Spearman with that 12-1 value, 276 months: median 0.92, mean 0.91, p10/p90 0.84/0.95, min 0.55 (2009-09).

## 5. Filters
SignalDoc Filter `exchcd%in%c(1,2)` (NYSE/AMEX in the paper's portfolio sort); OSAP predictor itself: shrcd 10/11/12, exchcd 1/2/3. Here: harness universe only.

## 6. Predicted sign
SignalDoc `Sign = +1.0`; Return 1.17; T-Stat 4.2. Orientation: `ascending=True`.

## 7. The mass-point question
Do-nothing firm (ten zero returns) produces exactly 0.0; a continuous mean of returns with no default and no signal zero-fill.
Measured, 276 months: modal share of the scored cross-section max 0.12% (median 0.05%); distinct values = n scored (min 1,692); no `qcut(10)` collapse. Tie handling: none designed.

## 8. History needed (snapshot starts 1998-01)
`history_months = 11`, `lookback_months = 11`. First signal 1998-12-31 reaches 1998-01-30; inside the panel.

## 9. OSAP metadata
Mom12mOffSeason (Acronym2 Mom12mOffSeason); Heston and Sadka 2008 JFE; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form continuous; Cat.Data Price; Cat.Economic other; Sample 1965-2002; Key Table "2 Year 1 Nonannual"; Test port sort; Sign +1.0; Return 1.17; T-Stat 4.2; EW; LS Quantile 0.1; Portfolio Period 1.0; Start Month 6.0; GScholar cites 442.
Notes: "different form than the other off season Heston and Sadka ones because its behavior is distinct; the other off season signals behave like long-term reversal." Definition: "Average return in other months over the previous year."

## 10. Proposed Sharadar mappings with deviations
```
px = ctx.monthly_closeadj(11); cols = BME(t-11) .. BME(t-1)
r = px[cols[1:]].values / px[cols[:-1]].values - 1 ; Mom12mOffSeason = mean of the 10 returns, NaN unless all 10 present
ascending=True ; history_months=11 ; lookback_months=11
```
Deviations: (a) no partial windows (harness history gate; 2.8% of scored names in OSAP-literal); (b) no delisting return; (c) NaN interior close -> NaN, not 0; (d) calendar business month-ends with 7-day tolerance, not row-based lags; (e) total-return price; (f) mean of ten returns, NOT the endpoint ratio.
Fields not in the map: none.
