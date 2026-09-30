# High52 — 52-week high ratio (George and Hwang 2004, Table 1)

OSAP ref b4e911e69678a7424f318617a61d813f54183123 (cache b4e911e6); source `Predictors/High52.py` (cached
`predictor.py`, `signaldoc_row.csv`, `upstream_CRSPDaily.py`, `upstream_CRSPMonthly.py`). DATA_SHA 198b281de1a0.
SignalDoc row (Cat.Signal == Predictor): Cat.Data = Price, Cat.Economic = momentum, Predictability 2_likely,
Signal Rep Quality 1_good.

## 1. Data availability (verdict: FEASIBLE — SEP daily close; one price-basis fork, stated below)

| input (OSAP) | field_map key | Sharadar | status | note |
|---|---|---|---|---|
| `prc` daily, `abs()` (dailyCRSP: raw CRSP `prc`, NOT divided by `cfacpr`) | `crsp.prc` | SEP.closeunadj (raw) — or SEP.close (split-restated) | mapped | see fork; SEP has no negative-price convention, close > 0 on every row |
| `time_d` -> `time_avail_m` (calendar month) | none | SEP.date | mapped | |

- No unavailable input, no zero-fill, no other table. Sharadar METRICS has `high52w` but only 30,936 rows (current
  snapshots, not history): unusable, and it is not OSAP's construction (monthly maxima of daily closes, current
  month excluded). Recommendation: `feasible` (a one-line deviation list in section 10).
- **The price-basis fork.** The pinned code states "Use absolute price without split adjustment (following original
  methodology)": it reads dailyCRSP `prc` (raw; `cfacpr` is loaded but never applied). SignalDoc's Detailed
  Definition says "prc/cfacshr", i.e. split-adjusted. The code is the construction: `closeunadj` reproduces it (a
  split in the 13-month window drops the ratio by the split factor for ~12 months, an OSAP artefact).
  `close` (split-restated) reproduces the SignalDoc text and is invariant to splits inside the window. Measured on the
  harness universe at all 276 signal months 1998-12-31..2021-11-30, ratio built both ways: rows where the two differ
  by more than 1% = 4.9% on average (0.5%-16.3%; 15.8% at 1998-12..1999-02, 11.5% at 1999-12, 5.4% at 2003-12,
  2.5% at 2008-12, 1.0% at 2021-11); per-month Spearman rank correlation of the two versions mean 0.94 (0.83-0.99).
  Recommendation: build the pinned `closeunadj` version as the pre-registered translation; `close` is a declared
  alternative (a second construction, not to be tried after a result). The 1998-99 divergence (~16%) sits where the
  sample is thinnest.
- Note for the record: the `field_map.yaml` note on `crsp.prc` says close is the split-adjusted series "per High52's
  construction"; the pinned code reads raw `prc`. The mapping index entry stands; this line is the correction.

## 2. Variables (exact source names)

`permno`, `time_d`, `prc` (dailyCRSP). Derived: `prcadj = prc.abs()`, `maxpr`, `temp`.

## 3. Formula

```
df["prcadj"]  = df["prc"].abs()                      # raw price, not split-adjusted
monthly       = groupby(permno, calendar month).agg(maxpr=max(prcadj), prcadj=last(prcadj))
for i in 1..12: l{i}_maxpr = groupby(permno)["maxpr"].shift(i)          # shift by ROW, not calendar
temp   = max over l1_maxpr..l12_maxpr (axis=1, skipna)                  # current month EXCLUDED
High52 = prcadj / temp                                                  # month-end price / prior-12-month max
```
- The denominator is the maximum of the 12 previous monthly maxima of the daily close; the current month's maximum
  is excluded and the numerator is the last price of month m, so the ratio can exceed 1 (new 52-week high): measured
  15.1% of the universe on average (0.6%-40.5% by month; bull-market months high). No cap.
- `max(axis=1)` skips NaN: there is NO minimum-history rule; a firm with one prior month gets a value. Measured
  (universe): at least one prior month present 99.8% of rows (min 98.4%); 1-11 prior months present for 3.4% of rows
  on average (up to 13.7%).
- Uses daily CLOSE maxima, not intraday highs: do not use SEP.high.

## 4. Timing / lag

No lag: month-m value uses month m's last close; stamped month-end m, portfolio earns m+1 (SignalDoc Portfolio
Period 6, Start Month 6 is the published holding design; the harness holds one month). Harness read:
`ctx.daily("SEP", ["closeunadj"], days_back ~ 400)` grouped to calendar months, or `at_month_ends` for the last price.
The month of the signal is the harness's last business month-end. SEP has a row on no-trade days (volume == 0;
price carried): OSAP's dsf likewise carries no-trade days, so do not filter them. No SF1 item: ART/TTM not in play.
The 1997-12 month holds one trading day (snapshot start): ruling `sep_snapshot_start_stub_month`, drop it via
`ctx.partial_months("SEP")`, which means the 1998-12 signal has 11 full prior months, not 12.

## 5. Filters

None in `High52.py` (no price, exchange or share-code filter; universe filters are the harness's). SignalDoc Filter
blank; Quantile Filter blank; LS Quantile 0.3.

## 6. Predicted sign

SignalDoc `Sign = +1.0` (near the 52-week high, higher return): George-Hwang Table 1, port sort, EW, return 0.45,
t = 2.0 in long-short; Key Table "1 High 52". Notes: sign depends on January vs non-January. `ascending=True`.

## 7. The mass-point question

A do-nothing firm (price flat for 13 months, e.g. a pending-deal stock) gives exactly 1.0. Measured on the harness
universe at all 276 signal months 1998-12-31..2021-11-30, closeunadj version:
- Share exactly at 1.0: mean 0.10%, max 0.53% (1998-12). It is the modal value in several of the months inspected (1998-12, 1999-12, 2003-12).
- Cross-section mode share (exact equality): mean 0.14%, max 0.53%; 0 of 276 months at or above the 10% cliff
  and none at or above 5%; 10 `qcut` bins every month; distinct values mean 1,955 (1,733-2,794).
- Coverage of the universe: any prior month 99.8% mean (98.4% min); a full 12 non-partial prior months 95.9% mean,
  0% at 1998-12 (stub), 94.4% at 1999-01, >= 40% from 1999-01. This is the `history_months=12` gate's effect
  (the harness gate is a price at lag 12); it is the recommended gate for young listings (3.4% of rows have 1-11
  prior months; OSAP keeps them). Median ratio 0.84 (0.46-0.98 across months).
- Tie handling: average rank; nothing to remove or floor.

## 8. History needed

OSAP sample 1963-2001; the ratio needs 13 months of daily closes. Snapshot SEP starts 1997-12 (stub): the first
signal month with a full 12-month window is 1999-01 (1998-12 has 11 full months); `history_months=12`,
`lookback_months=13`. Return-window factor: `history_months` is required.

## 9. OSAP metadata

Acronym High52, George and Hwang 2004, Journal of Finance, "52 week high". Cat.Form continuous, Cat.Data Price,
Cat.Economic momentum, Portfolio Period 6, Start Month 6, GScholar cites 1177. Output column `High52`.

## 10. Proposed Sharadar mappings

| OSAP | Sharadar | deviation |
|---|---|---|
| `prc.abs()` daily (raw) | SEP.closeunadj | faithful to the pinned code; alt. SEP.close (SignalDoc `prc/cfacshr` intent), rho 0.94 mean |
| monthly max and last of daily prc | max and last of SEP closeunadj per calendar month | SEP carries a row on no-trade days, as dsf does |
| shift 1..12 by row | 12 preceding calendar months | OSAP rows skip months with no CRSP row; calendar is cleaner, rare difference |
| no minimum history | `history_months=12` recommended (drops 3.4% of rows) | declared stricter; OSAP keeps >= 1 prior month |
| 1997-12 stub | dropped via `ctx.partial_months("SEP")` | per ruling |

Fields not in the field map index: none. Orientation `ascending=True`.
