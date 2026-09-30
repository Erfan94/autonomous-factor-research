# FirmAgeMom — Momentum among the youngest firms (Zhang 2006, Table 4; Acronym2 MomYoung)

OSAP ref b4e911e69678a7424f318617a61d813f54183123 (cache b4e911e6); source `Predictors/FirmAgeMom.py` (cached
`predictor.py`, `signaldoc_row.csv`). DATA_SHA 198b281de1a0. SignalDoc row (Cat.Signal == Predictor):
Cat.Data = Price, Cat.Economic = momentum.

## 1. Data availability (verdict: PREFLIGHT_FAILED — coverage by construction; construction is approx)

| input (OSAP) | field_map key | Sharadar | status | note |
|---|---|---|---|---|
| `ret` (monthly return, `fillna(0)` on existing rows) | `crsp.ret` | closeadj ratio month-end to month-end (`ctx.monthly_closeadj`) | mapped | OSAP zero-fills a missing `ret`: approx for that term only |
| `prc` (abs >= 5, missing kept) | `crsp.prc` | SEP.closeunadj at the signal | mapped | |
| firm age (`cumcount()+1` of a permno's rows) | `crsp.smt_row`, `crsp.firstpricedate` | SEP panel presence / TICKERS.firstpricedate | mapped | left-censored at 1997-12 |
| cross-sectional age quintile (whole CRSP: shrcd 10-12, exchcd 1-3) | none | universe-relative here | approx | quintile is universe-relative, not CRSP-wide |

- Buildable in principle, but two structural limits: (a) the signal is defined only for the youngest age
  quintile, so coverage can never exceed about 20% and the 40% Stage 1 floor is unreachable whatever the
  translation; (b) the age clock is censored at 1997-12, so the youngest quintile cannot be identified for
  the first 71 of 276 signal months (measured).
- **Recommendation: `preflight_failed`** (class coverage). Reason: scored share pooled 13.7%, at most 20.0% in
  any month, zero in 71 signal months (1998-12-31..2004-10-29); a Stage 1 coverage bar of 40% is structurally unmeetable.

## 2. Variables (exact source names)

`permno`, `time_avail_m`, `ret`, `prc` (SignalMasterTable). Derived: `age`, `l1_ret..l5_ret`, `age_quintile`.

## 3. Formula

```
ret = ret.fillna(0);  age = groupby(permno).cumcount() + 1          # age in rows (months), incl. month t
keep if (abs(prc) >= 5 or prc is NaN) and age >= 12                 # rows failing are DROPPED before lags/quintile
l1..l5 = calendar-based lags (stata_multi_lag) of ret, 1..5 months back
FirmAgeMom = (1+l1)(1+l2)(1+l3)(1+l4)(1+l5) - 1                     # five returns, months t-5..t-1; month t excluded
age_quintile = pd.qcut(age, 5, duplicates="drop") within time_avail_m, over the KEPT rows
FirmAgeMom = NaN unless age_quintile == 1                           # youngest 20% only
```
The docstring, SignalDoc Detailed Definition ("6 month return") and Acronym2 say six months but the code
multiplies FIVE lagged returns (l1..l5), skipping the current stamp month. Document the five-month, 1-month-
skip construction from the code. `stata_multi_lag` is calendar-based: a listing gap gives NaN for that lag
(so a NaN product), and `fillna(0)` only fills missing `ret` on rows that exist. Raw compound return, no
winsorising.

## 4. Timing / lag

Stamp month t: signal uses returns of months t-5..t-1 (the stamp month's own return is NOT used); stamped t,
portfolio earns t+1, so in harness terms the signal at month-end `sig` (= end of t) needs closeadj(end t-1) /
closeadj(end t-6) - 1, flagged for the translator to confirm against the repo's other stamp-t return-window
legs (Mom6m not yet translated). Age includes month t, matching age-through-signal-month in the harness. No SF1
item: no ART/TTM question. Needs `history_months` (>= 6 plus the 12-month age floor).

## 5. Filters

`abs(prc) >= 5` (missing prc kept), `age >= 12` months, youngest age quintile. SignalDoc: Zhang excludes
price < 5 and firms younger than 12 months. The harness price floor is $1 (universe), so the $5 screen is a
within-signal null; flag for the translator.

## 6. Predicted sign

SignalDoc `Sign = 1.0` (higher past return among young firms, higher return). Port sort, EW, LS quantile 0.2,
Portfolio Period 1, Start Month 6; sample 1983-2001; t = 7.21 in long portfolio ("4 middle U5"); Returns
"monotonic in momentum, so this variable can be continuous". Predictability in OP 1_clear, Quality 1_good.

## 7. Mass-point question

Same harness universe and 276 signal months (1998-12-31..2021-11-30) as FirmAge. Eligible = price >= 5 (harness
price, 97-99% of universe) and age >= 12; censored names (firstpricedate <= 1997-12-31) are ranked OLDER than
every known age, which gives the correct quintile only once known-age names exceed 20% of the eligible set.
- Quintile identifiable (20th age percentile falls on a known-age name) only from 2004-11: 205 of 276 months;
  zero scored in 71 signal months (1998-12-31..2004-10-29).
- Where defined: 325..434 scored names per month (median 363), 18.3-20.0% of universe (mean 19.3%); 20th age
  percentile 61..98 months. Pooled over all 276 months 13.7%. Probe months: 1998-12-31 scored 0; 2010-06-30
  344 (19.2%, q20 = 93 months); 2021-11-30 434 (18.8%, q20 = 62 months).
- A do-nothing firm (old, or censored) is NaN; the signal itself is a continuous 5-month return with no
  expected mode. A firm with no movement gives 0.0 only if its five closeadj ratios are exactly 1 (rare at
  the $5 floor), expected share ~0%; not measured on the return itself. Ties at the quintile edge (integer
  ages) fall into the youngest bin (`age <= q20`).
- Decile floor: Stage 1 needs >= 30 names per decile, so >= 300 scored; met in all 205 defined months, but only
  just (min 325).

## 8. History needed

OSAP sample 1983-2001. Snapshot starts 1998-01: return window from 1998-06 at the earliest, age floor of 12
months from 1998-12, and youngest-quintile identification from 2004-11 (above).

## 9. OSAP metadata

Acronym FirmAgeMom (Acronym2 MomYoung); Cat.Signal Predictor; Zhang, JF 2006; Cat.Form continuous;
Cat.Data Price; Cat.Economic momentum; sample 1983-2001; Stock Weight EW; GScholar cites (2025-09) 2599.

## 10. Proposed Sharadar mappings / deviations

- Return leg: SEP closeadj month-end ratios (`crsp.ret`); age: `crsp.firstpricedate` / `crsp.smt_row` (censored
  names NaN for age-rank purposes, treated as older for quintile membership); price: `crsp.prc` (closeunadj).
- Deviations: (1) quintile is universe-relative (harness universe), not CRSP-wide; (2) age censored at 1997-12;
  (3) `ret.fillna(0)` for a missing month is not reproduced (NaN instead; universe staleness <= 7 days);
  (4) $5 screen applied as a null inside the signal, not as a universe rule.
- Not in field_map: nothing new.
