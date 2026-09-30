# IntMom — Intermediate momentum: stock return over months t-12..t-7 (Novy-Marx 2012, JFE, Table 2, column 1; SignalDoc Acronym2 Mom12to7)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/IntMom.py` (cached `predictor.py`; no upstream beyond SignalMasterTable `ret`). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`.

## 1. Data availability (verdict: FEASIBLE, all inputs mapped; one decision month, 1998-12, is unscorable by the snapshot start)

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `ret` (monthly, total return incl. delisting) | `crsp.ret` | SEP `closeadj` month-end ratios (`ctx.monthly_closeadj(13)`) | mapped (no delisting return) | NaN -> 0 inside an existing row; a missing row -> NaN -> IntMom NaN |
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt; no SF1; no zero-fill term; no filing dates. `closeadj` is the total-return price (splits and dividends).

## 2. Variables (exact source names)
`permno, time_avail_m, ret` from SignalMasterTable (common stock 10/11/12, exchcd 1/2/3). Derived: `l7_ret..l12_ret`, `IntMom`.

## 3. Formula in words and key lines
Compound the six monthly returns of months t-12..t-7 (calendar lags 7..12 of the signal month; the five most recent months t-6..t are excluded). The SignalDoc wording "between months t-12 and t-6" is the code's lags 7..12:
```
ret.isna() -> 0 ; for months_back in 7..12: l{m}_ret = ret at time_avail_m - m months (calendar merge; missing row -> NaN)
IntMom = (1+l7)*(1+l8)*(1+l9)*(1+l10)*(1+l11)*(1+l12) - 1
```
Harness equivalent: `ctx.monthly_closeadj(13)`, `close[t-7]/close[t-13] - 1` (six returns). Measured on every decision month: max |ratio - product of the six monthly returns| = 1e-15, and 0 names where the endpoint ratio exists but a
monthly return in between is missing. A year-over-year or ART issue does not arise (price only).

## 4. Timing / lag convention
OSAP `time_avail_m` t signal uses returns of months t-7..t-12; here the signal is at business month-end t (same convention as DolVol/Beta specs), earned month t+1. Skips the most recent six month-ends, so the
month-t return is not used: no look-ahead. No lag beyond the return window; no filing dates; no flow smear; `dimension` default (no SF1).

## 5. Filters
OSAP predictor file: none; SignalMasterTable shrcd 10/11/12, exchcd 1/2/3. SignalDoc Filter blank. Harness universe applies (price >= $1, cap/ADV band).

## 6. Predicted sign
SignalDoc `Sign = +1.0` (high intermediate past return -> high future return); Return 1.2; T-Stat 5.79; Stock Weight VW ("Text says they use VW, but EW performs similarly"); LS Quantile 0.1; Portfolio Period 1; Start Month 6;
Cat.Economic momentum; Cat.Data Price; Cat.Form continuous. Orientation: long HIGH, `ascending=True`.

## 7. The mass-point question
Do-nothing firm: a stale (never trading) price over 13 months gives exactly 0.0. Measured on the harness universe at all 276 decision months (signals 1998-12-31 .. 2021-11-30):
- 1998-12-31 is empty (needs the 1997-11 month-end, before the SEP start 1997-12-31): 0% coverage, one month; 1999-01-29 (t-13 = 1997-12-31, the first SEP row, a valid price) is the first scorable signal. 275 of 276 months score.
- Coverage of the universe in the 275 scorable months: min 85.0%, mean 96.1%, max 99.3% (equals the `has_price_at(13)` history gate: a name needs a close at t-13).
- Exact 0.0 share of scored names: mean 0.07%, max 0.70%. Modal share of the cross-section: mean 0.11%, max 0.70%; 0 months at or above 5% (or the 10% cliff); `qcut(10)` yields 10 bins in all 275 months; 1,684-2,407 distinct values.
- Tie handling: none needed; the harness average rank covers the few exact ties. Nothing removed or floored. The only guard is a positive `closeadj` at both ends.

## 8. History needed (snapshot starts 1998-01)
13 months of price history: `history_months=13` (required: return-window factor), `lookback_months=13`. SEP starts 1997-12 (single stub trading day 1997-12-31 used only as a prior close; no calendar-month aggregation here, so the stub-month
rule does not apply). First scorable signal 1999-01-29, so decision month 1999-01 is empty and 1999-02 onward scores.

## 9. OSAP metadata
IntMom (Acronym2 Mom12to7); Novy-Marx 2012 JFE; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form continuous; Cat.Data Price; Cat.Economic momentum; Sample 1927-2010;
Key Table "2 column 1"; Test "port sort"; Evidence Summary "Tab2 t-stat 5.79"; Sign +1.0; Return 1.2; T-Stat 5.79; Stock Weight VW; LS Quantile 0.1; Portfolio Period 1; Start Month 6; Filter blank; GScholar cites 696.
Definition: "Stock return between months t-12 and t-6".

## 10. Proposed Sharadar mappings and deviations
```
ret -> SEP closeadj at business month-ends: ctx.monthly_closeadj(13); IntMom = close[t-7]/close[t-13] - 1   [crsp.ret, mapped]
```
Deviations: (a) no delisting return (SEP drops at the last trade; CRSP adds dlret, or -35%/-55% defaults); (b) missing monthly return inside the window -> NaN (as OSAP for a missing row), not 0; OSAP 0-fills only a
NaN return inside an existing row; (c) calendar month-ends by `to_bme`, business-day snap with the harness tolerance; (d) OSAP's sort is VW per the paper, SignalDoc Stock Weight VW; the harness ranks, equal-weighted deciles.
Fields not in the map: none. Recommendation: feasible (translate; `FactorDef.history_months=13`, `lookback_months=13`, `ascending=True`, no `dimension`).
