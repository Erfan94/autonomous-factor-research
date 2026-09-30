# DolVol — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: FEASIBLE (mapped inputs; deviation notes only)
| OSAP input | Sharadar | status |
|---|---|---|
| CRSP monthly `vol` (`monthlyCRSP`, `crsp.msf`) | sum of `SEP.volume` over the calendar month (shares; restated to today's split basis) | field_map `crsp.vol` mapped, verified 2026-09-30 (0.00% null) |
| CRSP monthly `prc` (signed price, bid/ask mean if no trade) | `SEP.close` on the month's last trading day (split-adjusted; consistent with the split-restated volume) | field_map `crsp.prc` mapped, verified 2026-09-30 |
- Measured on this snapshot (5 probe months, 1998-12 .. 2021-11): coverage of the universe 99.0-99.9%; zero-volume names in month t-2: 0; distinct values >= 99.5% of names; mode 0.04-0.06%.
- No IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob or ppegt input; no SF1.

## 2. Variables (predictor.py)
`monthlyCRSP`: permno, time_avail_m, `vol`, `prc`. (CRSPMonthly.py is the WRDS download: `msf.vol`, `msf.prc`.)

## 3. Formula
```
vol_lag2 = vol.shift(2);  prc_lag2 = prc.shift(2)                      # row-based shift in OSAP
DolVol   = log(vol_lag2 * |prc_lag2|);  dropna
```
Log dollar volume of the calendar month two months before the signal month: monthly share volume times the month-end price. (OSAP does not drop -inf from zero-volume months; the harness version guards `> 0`.)

## 4. Timing / lag
Signal dated t uses month t-2 data: an intentional 2-month skip, fully observed (no publication lag). Harness: signal_asof = month-end; target calendar month = signal month minus 2. `ctx.daily("SEP", ["close","volume"], days_back)` with `days_back` ~ 100 covers t-2 (window is (signal - d, signal]). No SF1, so no ART/ARQ issue and no flow smear.

## 5. Filters
SignalDoc Filter blank. Harness universe (price >= $1, cap and dollar-volume percentile band) applies.

## 6. Predicted sign
`Sign = -1.0` (Brennan-Chordia-Subrahmanyam 1998 Table 6A, t = 2.86 NYSE; 2.6 NASDAQ): high dollar volume, lower return. `ascending=False` (high value to the short side of the ranking).

## 7. Mass-point question
Do-nothing firm: a name with no trading in t-2 has no row, NaN (not 0). Continuous signal; no mass point (mode 0.04-0.06% in the probes; `qcut` gives 10 bins). Tie handling: drop non-positive `volume x close` (NaN), no floor. Names listed after the month t-2 (no t-2 row) are NaN; ~1% of the universe.
Structural note (diagnostic, not a bar): the harness universe entry/exit rule already uses trailing dollar volume and cap, so the signal is truncated from below; Spearman with log market cap 0.74-0.84 in the probes, i.e. strongly size-related, relevant to the Stage 2 residual projection.

## 8. History needed (snapshot starts 1998-01; SEP from 1997-12-31, 1997-12 a one-day stub)
Needs one full calendar month t-2: decision month 1999-01 uses signal 1998-12-31, i.e. t-2 = 1998-10, within SEP. Usable decision months: **276** of 276 (1999-01 .. 2021-12). `lookback_months` = 3; no `history_months` (no return window). Avoid 1997-12 (`ctx.partial_months("SEP")`), irrelevant here.

## 9. OSAP metadata
Brennan, Chordia and Subrahmanyam (1998), JFE; Cat.Data Trading; Cat.Economic volume; continuous; sample 1966-1995; Acronym2 VolumeDol; Test "mv reg", Key Table 6A; EW; Portfolio Period 1, Start Month 12; 1_clear / 1_good; T-stat 2.86. Source `Signals/pyCode/Predictors/DolVol.py`.

## 10. Proposed Sharadar mappings
```
w = ctx.daily("SEP", ["close","volume"], 100); keep rows in calendar month (signal month - 2)
g = w.groupby("ID"); dv = g.volume.sum() * g.close.last()   # date-sorted; last = month-end close
DolVol = log(dv.where(dv > 0))
```
Declare `SEP.close`, `SEP.volume`; `ascending=False`; `lookback_months=3`.
Deviations: (a) CRSP monthly volume is the exchange's monthly total (NASDAQ counts dealer-to-dealer trades, inflating pre-2004 NASDAQ volume); SEP volume is the vendor's consolidated daily volume, so the exchange mix differs, not the formula. (b) Month-end close x monthly volume (matches OSAP); the sum of daily close x volume is an alternative with correlation 0.997-0.9995 to it in the probes (same ranks, different level). (c) OSAP `prc` for a no-trade month is the bid/ask average; here no row = NaN. (d) Calendar-month lag, not row-based shift. Fields in map: `crsp.vol`, `crsp.prc` (both mapped).
