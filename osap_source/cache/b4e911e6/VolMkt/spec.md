# VolMkt — Volume to market equity: 12-month average dollar volume / market value of equity (Haugen and Baker 1996, Table 1)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/VolMkt.py` (cached `predictor.py`; upstream `CRSPMonthly.py` beside it). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`. Measurements: harness universe, 11 probe decision months spread over 1998-12-31 .. 2021-11-30 (of 276), recorded snapshot, scratch measurement (no factor file).

## 1. Data availability verdict: APPROX (all inputs available; the market-cap denominator is company-level, OSAP's is share-class-level). No zero-fill, no unavailable input.
| OSAP input | Sharadar | status |
|---|---|---|
| `vol` (CRSP monthly, /10000 in CRSPMonthly.py) | sum of `SEP.volume` over the calendar month | `crsp.vol` mapped (verified 2026-09-30); split-RESTATED |
| `prc` (month-end, abs) | `SEP.close` on the month's last row (same restated basis as `volume`) | `crsp.prc` mapped |
| `shrout` (for mve_c = shrout x abs(prc), CLASS level, not mve_permco) | `ctx.universe["mkt_cap_usd"]` (DAILY.marketcap, raw USD, company level, at the signal month-end) | `crsp.shrout` approx / `crsp.me` mapped |
No IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob or ppegt; no SF1. OSAP zero-fills nothing here.
Split basis: `close x volume` is split-invariant (dollar volume); `closeunadj` is NOT used with volume. The market cap is DAILY.marketcap, itself on the same-day price, so the ratio is dimensionless and basis-free.

## 2. Variables (exact source names)
`monthlyCRSP`: permno, time_avail_m, `vol`, `prc`, `shrout`. Derived: `mve_c = shrout * abs(prc)`, `temp = vol * abs(prc)`, `tempMean`.

## 3. Formula
```
mve_c   = shrout * |prc|                              # shrout in millions after /1000, vol /10000: both in $ millions
temp    = vol * |prc|                                 # monthly share volume x month-end price
tempMean= temp.rolling_mean(window_size=12, min_samples=10).over(permno)   # ROW window: months t-11..t incl. the current month
VolMkt  = tempMean / mve_c                            # mve_c at month t
```
Plainly: the average over the last 12 months (at least 10 observed) of monthly dollar volume (shares traded x the month-end price), divided by the current market cap. A turnover-like measure in dollar terms.

## 4. Timing / lag
OSAP: month-t values, signal dated t, return earned in t+1 (SignalDoc Start Month 6 / Portfolio Period 12 are the paper's portfolio convention; predictor.py applies no 6-month lag). Harness: signal_asof = month-end; the window is the 12 calendar months ending in the signal month (month t included in full). No SF1, so no ART/ARQ issue and no flow smear; `ctx.daily("SEP", ["close","volume"], ~400)` covers 12 calendar months (<= ~366 days + margin).
Partial-month guard: drop the 1997-12 one-day stub with `ctx.partial_months("SEP")` (never reached: the first window is 1998-01..1998-12). Stray weekend/holiday SEP rows: 0 rows found in the universe scope at all 11 probes (stray volume share 0.0), so no calendar filter is needed; `market_trading_calendar` (Illiquidity idiom) may still be applied harmlessly.

## 5. Filters
SignalDoc Filter `abs(prc)>5` is a portfolio-formation filter; it is NOT in predictor.py and is not applied (DolVol/Illiquidity convention). The harness universe (price >= $1, cap/dollar-volume band) decides.

## 6. Predicted sign
SignalDoc `Sign = -1.0` (t = 4.0, mv reg, nonstandard): HIGH volume/market cap predicts LOW returns. `ascending=False` (high value to the short side).

## 7. Mass-point question
Do-nothing firm: zero trading in all 12 months gives 0 (monthly volume sums to 0); a name with no SEP rows in a month is a missing month (NaN), not 0. Measured at 11 probe months: no exact-zero or negative value (0 of the scored names), modal share 0.043-0.058% of scored names (single tie), distinct values = scored names (1,710-2,346), `qcut` 10 bins everywhere. Continuous; no mass point, no tie design needed. A positive-volume requirement is unnecessary; guard `tempMean > 0` anyway to keep 0 out of the ranks.
Structural: the universe band already selects on trailing dollar volume and cap, so the ratio is truncated from below and is strongly related to size through the denominator (diagnostic, not a bar).

## 8. History needed (snapshot starts 1998-01; SEP from 1997-12-31, 1997-12 a one-day stub)
Both the min-10 rule and the full 12-month window (`momentum_partial_windows` default) give the same 276 months, so no ruling is needed. OSAP rule: at least 10 of the 12 window rows. Earliest signal 1998-10 has 10 months (1998-01..1998-10); the first decision month (1999-01, signal 1998-12-31) has 12. Scorable decision months: **276 of 276** under the min-10 rule (and under the full-12 rule: signal 1998-12 has exactly 12). Measured coverage of universe members: 87.7-99.5% across probes (96.1% at 1998-12, 87.7% at 1999-12, 94.4% at 2021-11; 12-of-12 share 86.4-99.3%); the gap is names listed fewer than 10 months. `lookback_months` ~13, `history_months` 9 (a price at t-9 gives 10 monthly observations; the compute enforces the count itself; 11 under the full-window convention, which would drop the 10-11 month names, cov 86.4-99.3% 12-of-12 vs 87.7-99.5%). Well above `rebalance.min_months` 120.

## 9. OSAP metadata
Haugen and Baker (1996), JFE; Cat.Data Trading; Cat.Economic volume; continuous; sample 1979-1993; Acronym2 Volume2Mkt; Test "mv reg nonstandard" (OP reports the mean coefficient across 90 multiple regressions); EW; LS Quantile 0.2; Portfolio Period 12; Start Month 6; Predictability 2_likely / Signal Rep Quality 2_fair; T-stat 4.0; 1,647 cites (2025-09). Source `Signals/pyCode/Predictors/VolMkt.py`.

## 10. Proposed Sharadar mappings
```
d = ctx.daily("SEP", ["close","volume"], 400); keep calendar months t-11..t (drop partial_months); sort ID,date
d = d[d.close > 0]
m = d.groupby(["ID","month"]).agg(vol=volume.sum, px=close.last); dv = m.vol * m.px     # dv > 0 or the month counts as 0
mean12 = dv.groupby("ID").mean() if count >= 10 else NaN
VolMkt = mean12 / ctx.universe["mkt_cap_usd"]; where(VolMkt > 0)
```
Declare `SEP.close`, `SEP.volume`; `ascending=False`; `history_months=9`; `lookback_months` ~13.
Deviations: (a) `volume` is the consolidated daily volume summed to a month; CRSP NASDAQ volume before 2004 double counts dealer trades, so the level differs by exchange mix (ranked within sector). (b) OSAP mve_c is share-CLASS level; DAILY.marketcap is company level (all classes) while the volume is one ticker's, so multi-class issuers read low (not measured). (c) Month-end `close` carries the last price on no-trade days, no bid/ask mean. (d) Calendar-month window, not panel-row window (a gap month is missing, not skipped). (e) mkt cap at the signal month-end day, matching OSAP's month-t mve_c. (f) `abs(prc)>5` not applied. Fields: `crsp.vol`, `crsp.prc`, `crsp.shrout`/`crsp.me` (all in the map).
