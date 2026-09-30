# MaxRet — Maximum daily return over the signal month (Bali, Cakici and Whitelaw 2011, JFE, Table 1 VW 10-1)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/MaxRet.py` (cached `predictor.py`; upstream `upstream_CRSPDaily.py`). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`. Measured on the harness universe for all 276 decision months.

## 1. Data availability (verdict: FEASIBLE; every input maps, no zero-fill, no data-start loss)

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `ret` (daily CRSP, dsf; no delisting adjustment) | `crsp.ret` | SEP `closeadj[d] / closeadj[d-1] - 1`, d-1 = previous trading-calendar day | mapped (day-over-day for daily consumers) | rows with NaN ret dropped by `dropna`; a name with no non-NaN day in the month is absent |
| `permno, time_d` | - | harness ID, SEP `date` | - | - |
- No SF1 input, no ART/ARQ question; none of IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt. Declare inputs `SEP.closeadj`.
- Measured coverage: 100.0% of the universe has a value in every one of the 276 decision months (1998-12-31 .. 2021-11-30); share of universe names with >= 15 daily returns in the signal month: mean 99.9%, min 99.3%. Scored names 1,739-2,867.

## 2. Variables (exact source names)
`permno, time_d, ret` from `dailyCRSP`; derived `time_avail_m` (calendar month of `time_d`), `MaxRet`.

## 3. Formula in words and key lines
The largest single-day return of the calendar month t, per stock. No minimum number of days, no winsorising, no skew or volume adjustment.
```
df["time_avail_m"] = month of time_d
MaxRet = df.groupby(["permno","time_avail_m"])["ret"].max()      # pandas max skips NaN
dropna(MaxRet)
```
The first trading day's return of the month uses the previous month's last close (CRSP dsf ret), so a full month has ~21 returns that need ~22 closes.

## 4. Timing / lag convention
Month-t value uses the days of t (known at the t close), held t+1; the SignalDoc description "previous month" is that same month-end signal. No filing date, no flow item, no ART/ARQ smear. Here: signal at business month-end t; window = calendar month of the signal date.
The 1997-12 SEP stub month (`ctx.partial_months("SEP")`, a one-day month) is never a signal month (first signal 1998-12-31); a factor that aggregates calendar months must still drop it: return NaN if the signal month is in `partial_months`.
Daily return needs the previous day's close: use the trading calendar (`harness.data_layer.market_trading_calendar` on the `ctx.daily` dates, as Illiquidity does), so a stray weekend/holiday SEP row is not a trading day and never becomes another name's prior day; nothing chained across a missing row. The measurement used the calendar of ALL SEP dates (market-wide); a factor using only universe dates should reproduce it (calendar = dates with at least half the trailing median name count).

## 5. Filters
OSAP predictor file: none (no SignalMasterTable filter; `dailyCRSP` as built). SignalDoc Filter blank. Harness universe (price >= $1, cap and ADV screens) chooses the scored names.

## 6. Predicted sign
SignalDoc `Sign = -1.0` (a lottery-like high maximum day predicts LOW returns); Stock Weight VW; LS Quantile 0.1; Cat.Economic volatility; Cat.Form continuous; Cat.Data Price. Orientation: long LOW, `FactorDef(ascending=False)`.

## 7. The mass-point question
Do-nothing firm (every day of the month flat): the maximum of zeros is exactly 0.0, a real value, not a default.
Measured, 276 months: share at exactly 0.0 mean 0.0003% (max 0.04%: one or two names); modal share of any value mean 0.12%, max 0.30% (2000-05-31: 0.142857 = 1/7, 9 of 2,670 names; the pre-decimalisation fractional-price grid, e.g. 28 -> 32 = +14.3%, not a data artefact); distinct values 1,732-2,769; monthly cross-sectional median of the signal 2.1%-15.6% (median over months 3.6%); `qcut(10)` yields 10 bins in every month. Tie handling: none needed (harness average rank).

## 8. History needed (snapshot starts 1998-01)
One month of daily closes plus the prior close: `history_months = 1` (a price-window factor needs a gate; the name must have a close one month back, i.e. the first day's return exists) and `lookback_months = 1`; or state `no_history_gate_because` (uses only month-t days). Not binding: 276 of 276 months score. Days of daily history needed: about 35 calendar days back.

## 9. OSAP metadata
MaxRet (Acronym2 MaxRet); Bali, Cakici and Whitelaw 2011 JFE; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form continuous; Cat.Data Price; Cat.Economic volatility;
Sample 1962-2005; Key Table "1 VW 10-1"; Test "port sort"; Evidence "t=2.8 in port sort"; Sign -1.0; Return 1.03; T-Stat 2.83; Stock Weight VW; LS Quantile 0.1; Portfolio Period 1.0; Start Month 6.0; Filter blank; GScholar cites 2069.
Notes: "Doesn't work as well EW. Very nonlinear return vs decile." Definition: "Maximum of daily returns (ret) over the previous month."

## 10. Proposed Sharadar mappings with deviations
```
d = ctx.daily("SEP", ["closeadj"], ~40 days back) ; cal = market_trading_calendar(d["date"]) ; wide close (cal x ID) ; ret = close / close.shift(1) - 1   (close > 0)
MaxRet = ret.loc[signal calendar month].max(skipna) ; NaN if the month has no valid return or the month is in ctx.partial_months("SEP") ; ascending=False
```
Deviations: (a) closeadj ratio (total return incl. dividends, no delisting return) replaces CRSP daily ret; closeadj is on a 3-decimal grid, so a back-adjusted price below $0.50 prints coarse returns (the universe price floor $1 is on the unadjusted price; a heavily back-adjusted low closeadj is possible and would inflate |ret| noise in exactly the high-MaxRet tail; not measured);
(b) no return is formed across a missing row (OSAP's dsf ret is the vendor's own); (c) OSAP scores a name with any single traded day in month t, including a partial-month new listing; here the same (no minimum-days rule), 0.1% of universe names have fewer than 15 returns;
(d) OSAP's test is value-weighted 10-1; the harness ranks, equal-weighted deciles (SignalDoc notes the signal is weaker equal-weighted: a construction fact); (e) harness universe, not all CRSP.
Fields not in the map: none.
