# MomRev — Momentum and long-term reversal: binary flag, 1 = top Mom6m quintile AND bottom Mom36m quintile, 0 = bottom Mom6m AND top Mom36m (Chan and Ko 2006, JOIM, Table 5)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/MomRev.py` (cached `predictor.py`; upstream `upstream_SignalMasterTable.py`, `upstream_CRSPMonthly.py`, `upstream_stata_replication.py` beside it). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`.

## 1. Data availability (verdict: preflight_failed, MEASURED IN THIS SPEC against the preflight rule (mode_pct >= 10 or qcut bins < 10), not a `preflight.py` run — a discrete two-valued signal; inputs are available and 251 of 276 decision months can score, but the signal is a mass point by design and covers a mean 9.0% of the universe)

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `ret` (monthly total return incl. delisting return) | `crsp.ret` | SEP `closeadj` month-end ratios (`ctx.at_month_ends("SEP", ["closeadj"], range(1, 38))`) | mapped | `ret.isna() -> 0` on existing rows only (NO `fill_date_gaps`); `stata_multi_lag` is calendar-based, so a lag with no row is NaN and the compounded product is NaN |
| delisting return (dlret) | `crsp.dlret` | none | unavailable | not reproduced |
| `permno, time_avail_m` | `crsp.smt_row`; shrcd/exchcd | harness universe | approx | - |
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt; no SF1 input; no filing dates; no ART/ARQ question.
- Data start: lag 36 needs the close at BME(t-37); SEP's first close is 1997-12-31, so the first full-window signal is 2001-01-31 = decision month 2001-02. Of the 276 decision months (signals 1998-12-31 .. 2021-11-30), 25 are null by construction and **251 can score** (>= `rebalance.min_months` 120), so not data_start.
- Measured on the harness universe (quintiles formed among the universe's own scored names each month, Mom6m and Mom36m separately as in OSAP): in the 251 scorable months n flagged 73-371 (median 165), of which MomRev=1 28-211 (median 85) and MomRev=0 31-187 (median 77); coverage 4.2%-16.7% of the universe (mean 9.0%; 11.1% at 2001-01-31, 8.5% at 2011-06-30, 5.8% at 2021-11-30). Pooled over all 276 months (the harness `coverage_pct` rule) it is 8.0%. Coverage is 0 in the 25 leading months. The other ~91% of names (every cell except the two corners) are NaN by construction.

## 2. Variables (exact source names)
`permno, time_avail_m, ret`; derived `ret_lag1..5`, `ret_lag13..36`, `Mom6m`, `Mom36m`, `Mom6m_clean`, `Mom36m_clean`, `tempMom6`, `tempMom36`, `MomRev`.

## 3. Formula in words and key lines
Mom6m = compounded returns of lags 1..5 (months t-5..t-1, five months despite the name) - 1; Mom36m = compounded returns of lags 13..36 (months t-36..t-13, 24 months; the most recent 12 are skipped) - 1. Each is cut into monthly quintiles (`pd.qcut(q=5, duplicates="drop")`, per month, over every stock with a value). Flag 1 = Mom6m quintile 5 and Mom36m quintile 1; flag 0 = Mom6m quintile 1 and Mom36m quintile 5; all other stocks NaN.
```
df["tempMom6"]  = groupby(time_avail_m)["Mom6m"].transform(qcut 5) + 1
df["tempMom36"] = groupby(time_avail_m)["Mom36m"].transform(qcut 5) + 1
df.loc[(tempMom6 == 5) & (tempMom36 == 1), "MomRev"] = 1
df.loc[(tempMom6 == 1) & (tempMom36 == 5), "MomRev"] = 0
```
Note: `Mom6m_clean`/`Mom36m_clean` (inf removed) are computed but the qcut reads the un-cleaned `Mom6m`/`Mom36m`. SignalDoc Definition says "Exclude if price less than 5"; the code has no price filter (SignalDoc Filter is empty). The harness universe has price >= $1 only; a $5 cut is not proposed.
Harness form: px = closes BME(t-1)..BME(t-37); ret_k = px[k]/px[k+1]-1; Mom6m = prod(1+ret_k, k=1..5)-1 (= px[1]/px[6]-1); Mom36m = prod(1+ret_k, k=13..36)-1 (= px[13]/px[37]-1); a NaN interior close makes the product NaN.

## 4. Timing / lag convention
Signal dated t uses returns of months t-5..t-1 and t-36..t-13, holding t+1; month t itself is skipped in both (lags start at 1). No filing dates, no flow items, no ART/ARQ.
Overlap with the v0 Momentum leg (closeadj[t-1]/closeadj[t-12]-1, return months t-11..t-1): the Mom6m component (months t-5..t-1) lies ENTIRELY inside the v0 window (five of its eleven months). The Mom36m component (months t-36..t-13) is disjoint from it (v0 covers t-11..t-1; month t-12 is used by neither). No correlation measured for the binary flag itself.

## 5. Filters
SignalDoc Filter blank; Definition "Exclude if price less than 5" (not in code). Here: harness universe only.

## 6. Predicted sign
SignalDoc `Sign = +1.0` (flag 1 = momentum winner and long-term loser is the long leg); Return 0.48; T-Stat 4.29; LS port FF3 alpha, 3-month portfolio period, Cat.Form `discrete`. Orientation: `ascending=True`.

## 7. The mass-point question
Discrete: distinct values = 2 ({0, 1}) plus NaN. A do-nothing firm produces NaN (no corner cell) — about 91% of the universe. Among scored names the modal share is 50.0%-73.4% (median 55.9%) over the 251 scorable months; the two-value signal can only fill 2 of 10 deciles (`pd.qcut(rank, 10, duplicates="drop")` yields at most 2 bins, well under the preflight cliff of 10% mass point and 10 bins), and the Stage 1 bars (>= 30 names per decile, coverage >= 40%) cannot be met: coverage mean 9.0% (max 16.7%). This is the same class as the discrete signals excluded as mass points (EarnSupBig, IndMom, MS). Tie handling: there is nothing to design that preserves the signal; a continuous substitute (e.g. a Mom6m rank minus a Mom36m rank) would be a different predictor, not this one.

## 8. History needed (snapshot starts 1998-01; first SEP close 1997-12-31)
`history_months = 37`, `lookback_months = 37`. First scorable decision month 2001-02 (25 leading months null, data-start warning at the first probe month 1998-12 expected). Not a data_start failure (251 >= 120).

## 9. OSAP metadata
MomRev (Acronym2 MomRev); Chan and Ko 2006 JOIM; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form discrete; Cat.Data Price; Cat.Economic momentum; Sample 1965-2001; Key Table "5"; Test LS port FF3 alpha; Sign +1.0; Return 0.48; T-Stat 4.29; Stock Weight EW; Portfolio Period 3.0; Start Month 6.0; GScholar cites 17. LongDescription "Momentum and LT Reversal". Evidence "t=4.3 in long-short".

## 10. Proposed Sharadar mappings with deviations
Not proposed for translation (preflight_failed). If ever built: px via `ctx.at_month_ends("SEP", ["closeadj"], range(1, 38))`, `px.where(px > 0)`, quintiles over `ctx.ids` scored names, `ascending=True`, `history_months=37`. Deviations it would carry: no delisting return; NaN interior close -> NaN (OSAP zero-fills an existing row's NaN ret); quintile cuts over the harness universe rather than all CRSP; month-end-calendar lags with 7-day tolerance; no $5 price filter; 3-month OSAP holding vs the harness one-month hold.
Fields not in the map: none.
