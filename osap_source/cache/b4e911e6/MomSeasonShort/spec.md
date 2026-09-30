# MomSeasonShort — Seasonal momentum, year 1: the return in the same calendar month one year ago (Heston and Sadka 2008, JFE, Table 2 "Year 1 Annual")

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/MomSeasonShort.py` (cached `predictor.py`; upstream `upstream_SignalMasterTable.py`, `upstream_CRSPMonthly.py`, `upstream_stata_replication.py` beside it). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`. Measurements: harness universe (build_universe + MonthContext idiom), schedule 1999-01 .. 2021-12 (276 decision months, signals 1998-12-31 .. 2021-11-30), recorded snapshot.

## 1. Data availability (verdict: FEASIBLE; 276 of 276 decision months scorable, floor 120)

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `ret` (monthly total return incl. delisting return) | `crsp.ret` | SEP `closeadj` month-end ratio (`ctx.at_month_ends("SEP", ["closeadj"], [11, 12])`) | mapped | `ret.fillna(0)` on an existing row, then `stata_multi_lag` lag 11: a lag landing in a calendar gap is NaN |
| delisting return (-0.35 / -0.55 rule upstream) | `crsp.dlret` | none | unavailable | not reproduced in a past-return window |
| `permno, time_avail_m`; shrcd 10/11/12, exchcd 1/2/3 | `crsp.shrcd`, `crsp.exchcd` | harness universe | approx | - |
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt; no SF1 input; no filing dates; no ART/ARQ question; closeadj is the total-return price.
- DATA-START ARITHMETIC (exact): the return at lag 11 is close(BME(t-11)) / close(BME(t-12)) - 1, so the deepest close is BME(t-12). The first decision month (signal 1998-12-31) needs 1997-12-31, which is SEP's first date: no leading loss. Measured: >= 10 names scored in all 276 months, 1,692-2,453 scored (median 1,839) of a universe of 1,739-2,867.
- Measured coverage: 85.6%-99.4% of the universe (mean 96.4%, median 97.2%); 94.6% at 1998-12-31, 86.1% at 1999-12-31, 99.2% at 2008-12-31, 92.8% at 2021-11-30. The shortfall is names without a close near BME(t-11) or BME(t-12) (listed under a year, or a gap).

## 2. Variables (exact source names)
`permno, time_avail_m, ret`; derived `ret_lag11`, `MomSeasonShort`.

## 3. Formula in words and key lines
The single monthly return of month t-11 (t = signal month): the same calendar month as the predicted month t+1, one year earlier.
```
df["ret"] = df["ret"].fillna(0)
df = stata_multi_lag(df, "permno", "time_avail_m", "ret", [11])
df["MomSeasonShort"] = df["ret_lag11"]
```
Harness form: `px = closeadj at BME(t-11), BME(t-12)` via `ctx.at_month_ends` (7-day tolerance), each required > 0; `score = px[11] / px[12] - 1`. One return, so one extreme month moves a name a lot; the harness 1/99 winsorisation precedes the rank.

## 4. Timing / lag convention
Signal dated t (business month-end) uses the month t-11 return; it is held in month t+1. No filing dates, no flow items, nothing to smear under TTM, ART-as-of-filing irrelevant. Return-window factor: `history_months = lookback_months = 12`.
OVERLAP WITH THE v0 MOMENTUM LEG (nested, not disjoint): the v0 leg is closeadj[t-1]/closeadj[t-12]-1 (return months t-11 .. t-1); this signal is exactly the OLDEST of those 11 monthly returns. Measured cross-sectional Spearman with the 12-1 value over 276 months: median 0.285, mean 0.276, min -0.080, max 0.641. (MomSeason and MomOffSeason windows, lags 12+, do not overlap the v0 leg; this one does.)

## 5. Filters
SignalDoc Filter `exchcd%in%c(1,2)` (paper portfolio sort); the predictor itself has shrcd 10/11/12, exchcd 1/2/3 and no other screen. Here: harness universe only.

## 6. Predicted sign
SignalDoc `Sign = 1.0` (HIGH same-month return last year is the long leg); Return 1.15; T-Stat 7.6. Orientation: `ascending=True`.

## 7. The mass-point question
A do-nothing firm (close at BME(t-11) equals close at BME(t-12)) produces exactly 0.0; no default, no signal zero-fill (the `ret.fillna(0)` on an existing row is not reproduced: a missing close is NaN here). Measured over 276 months: the only modal value is 0.0 in 226 months (elsewhere a single tied value); modal share of the scored cross-section median 0.22%, mean 0.32%, max 1.63% (1998-12 1.25%, 1999-12 0.91%, 2008-12 0.28%, 2021-11 0.09%); exact zeros at most 37 names in a month; distinct values equal n scored in 11 months, distinct/n >= 0.967 in every month (median 0.998); qcut gives 10 bins in every month; no month reaches 5%. Exact zeros are unchanged month-end closes (no-trade carried prices, the 3-dp closeadj grid below $0.50); cause not decomposed. Tie handling: none designed; guard is a positive close at each end (null otherwise, so blend_ranks renormalises).

## 8. History needed (snapshot starts 1998-01, first close 1997-12-31)
`history_months = lookback_months = 12`: the first probe month (1998-12) is scorable (94.6% coverage); no data-start warning expected beyond the 12-month lookback reaching 1997-12-31.

## 9. OSAP metadata
MomSeasonShort (Acronym2 MomSeasonShort); Heston and Sadka 2008 JFE; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form continuous; Cat.Data Price; Cat.Economic other; Sample 1965-2002; Key Table "2 Year 1 Annual"; Test port sort; Evidence "t=7.6 in port sort"; Sign 1.0; Return 1.15; T-Stat 7.6; EW; LS Quantile 0.1; Portfolio Period 1.0; Start Month 6.0; GScholar cites 442. LongDescription "Return seasonality last year". Definition: "Average return in the same month in the previous year."

## 10. Proposed Sharadar mappings with deviations
```
d = ctx.at_month_ends("SEP", ["closeadj"], [11, 12])
px = d.pivot(index="ID", columns="months_back", values="closeadj").reindex(ctx.ids); px = px.where(px > 0)
score = px[11] / px[12] - 1      # replace inf with NaN
ascending=True ; history_months=12 ; lookback_months=12
```
Deviations: (a) no delisting return; (b) a missing close is NaN, OSAP fills 0 on an existing row; (c) calendar business month-ends, 7-day tolerance, not row-based lags; (d) coverage 85.6%-99.4% of the universe; (e) nested in the v0 Momentum window (Spearman above), a diagnostic not a bar. Fields not in the map: none.
Recommendation: translate (idiom: factors/candidates/MomOffSeason.py, closeadj at month-ends) and preflight; expected to pass.
