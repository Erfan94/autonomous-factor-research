# BidAskSpread — Corwin-Schultz high-low spread (Amihud and Mendelson 1986, Table 2 "Spread Mean")

OSAP ref b4e911e69678a7424f318617a61d813f54183123; DATA_SHA 198b281de1a0. Source: `Predictors/BidAskSpread.py`
(cached `predictor.py`) only READS `../pyData/Prep/corwin_schultz_spread.csv`, built by the SAS program
`Corwin_Schultz_Edit.sas` (cached here as `corwin_schultz_edit.sas`; it is the real construction). The tree also
holds `DataDownloads/BidAskSpreads.py` (TAQ `hf_spread`) and `Placebos/BidAskTAQ.py`: neither feeds it.

## 1. Data availability (verdict: FEASIBLE with small deviations -> `approx`)

| input (OSAP) | field_map key | Sharadar | status | note |
|---|---|---|---|---|
| `hiprc` = CRSP `askhi` (daily) | `crsp_to_sharadar.askhi` | SEP.high | mapped | split-adj same basis as close; 0.00% null; high==low on ~9% of rows |
| `loprc` = CRSP `bidlo` | `crsp_to_sharadar.bidlo` | SEP.low | mapped | same |
| `prc` (daily close, sign = quote flag) | `crsp_to_sharadar.prc` | SEP.close (NOT closeunadj / closeadj) | mapped | no negative-price convention; close>0 always |
| `vol` (daily) | `crsp_to_sharadar.vol` | SEP.volume | mapped | volume==0 is the only no-trade flag; 4.8% of rows overall (7.5% 1999) |
| permno, month | SEP ticker -> ID, calendar month | harness ID | n/a | |

- No Compustat, IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob, ppegt, TAQ or rf term; no
  OSAP zero-fill. Inputs are daily from 1997-12-31.
- Deviation inventory (why `approx`, not `mapped`): (a) OSAP's quote-based flags (negative `prc` = bid/ask average,
  negative `loprc`/`hiprc` = closing bid/ask on no-trade days) do not exist in SEP; `volume==0` replaces them and
  the SAS screen already nulls those days the same way (see 3). (b) CRSP `dsf` prices are NOT split-adjusted; SEP
  `close/high/low` are. OSAP's raw series shows a split-day discontinuity that its overnight adjustment turns
  into a spurious range; SEP has none, so split-day estimates differ (small, rare). (c) CRSP `dsf` covers
  NYSE/AMEX/NASDAQ common; the harness universe restricts the same way. No daily-data access is blocked: verified
  `MonthContext.daily("SEP", [...], days_back)` exists and returns ticker/date rows for universe IDs.
- Field-checker on THIS snapshot: askhi, bidlo, prc, vol carry only `probed_on_prior_snapshot` (2026-09-25); re-probe.
- Scratch check of the algorithm on SEP (close>=$1, 2001-03/2008-03/2015-03): 6896/5717/5609 names, 0.8/0.6/0.6% fail
  N>=12, median spread 0.0155/0.0138/0.0071, exact-zero 0.0%.
## 2. Variables (exact source names)

SAS input: `permno, date, prc, bidlo (->loprc), askhi (->hiprc), vol (->volume), month=yyyymm`. Output column `hlspread`
= `mspread_0`, renamed `BidAskSpread` in `BidAskSpread.py`; `time_avail_m` = the calendar month of the daily rows.

## 3. Formula (Corwin and Schultz 2011, closed form eqs 14 and 18), in words and key lines

Per stock, daily, in date order (the SAS lags run over the whole permno history, across month boundaries):
1. Screen: if `loprc==hiprc or loprc<=0 or hiprc<=0 or prc<=0 or volume==0` then `loprc,hiprc = missing`.
2. Retained range (`loprcr,hiprcr`): if `0<loprc<hiprc` the day's range becomes the retained one. Otherwise fill from
   the retained range of the last good day: within `[loprcr,hiprcr]` -> copy it; `prc<loprcr` -> `loprc=prc`,
   `hiprc=hiprcr-(loprcr-prc)`; `prc>hiprcr` -> `hiprc=prc`, `loprc=loprcr+(prc-hiprcr)`. No retained range yet
   (series start) -> stays missing. Retention has no time limit.
3. Drop if `loprc!=0 and hiprc/loprc>8`.
4. Overnight adjustment vs prior day's close `lprc` and prior-day (post-reset) range `llo, lhi`:
   `lprc<loprc` -> `thiprc=hiprc-(loprc-lprc), tloprc=lprc`; `lprc>hiprc` -> `thiprc=lprc, tloprc=loprc+(lprc-hiprc)`;
   else `thiprc=hiprc, tloprc=loprc`. Lags reset at a new permno.
5. `beta=ln(thiprc/tloprc)^2 + ln(lhiprc/lloprc)^2`; `hiprc2=max(thiprc,lhiprc)`, `loprc2=min(tloprc,lloprc)`,
   `gamma=ln(hiprc2/loprc2)^2`; `c=3-2*sqrt(2)`.
```
alpha  = (sqrt(2*beta)-sqrt(beta))/c - sqrt(gamma/c)
spread = 2*(exp(alpha)-1)/(1+exp(alpha))
spread_0 = max(spread, 0)          # missing stays missing
```
6. Monthly: per `permno, month`, `N = count(non-missing spread)`; keep only `N>=12`;
   `hlspread = mean(spread_0)` (mean of the daily values, negatives set to zero BEFORE averaging). The value is a
   fraction of price (round-trip), already scale-free; no further division by price despite the SignalDoc wording.

## 4. Timing and lag

- OSAP: the estimate for calendar month m is stamped `time_avail_m = m` (no lag); the portfolio formed on it earns
  month m+1. Here: at signal date `signal_asof` (month-end business day), use daily rows of the calendar month that
  ends at `signal_asof`. Same information set as OSAP. No filing data, so no ART/ARQ/as-of-filing question; there
  is no fundamental input and `dimension` stays default (not applicable, not set).
- Day 1 of the month needs the prior month's last trading row (lag) and the retained range: `ctx.daily` must pull
  ~100 calendar days back (warm-up) and the estimate must be scored only from rows in the target calendar month.
  Warm-up differs from OSAP's infinite retention only for names with >~80 calendar days of no good range (rare).
- No flow item, no year-over-year difference: nothing smears under TTM.

## 5. Filters

SignalDoc `Filter` and `Quantile Filter`: blank; Stock Weight EW. The only OSAP screens are in the SAS (steps 1-3, N>=12). The harness
universe (US common, NYSE/NASDAQ/NYSEMKT, price >= $1, relative cap/dollar-volume membership band) applies on top;
it removes the widest-spread sub-$1 stocks. OSAP does NOT exclude low-price names in this signal.

## 6. Predicted sign

`Sign = 1.0`: higher spread predicts higher return (liquidity premium). Long D10 (widest spread), short D1.
Evidence: "strong port sorts but no LS special data" (no t-stat in SignalDoc).
No flip. A flipped sign would be a second hypothesis (|t| >= 2.74).

## 7. The mass-point question

- A do-nothing (no-trade) day is NOT zero-filled: `volume==0` days are screened, then replaced from the retained
  range, which yields a positive spread about equal to the old range. A firm that trades every day has a
  continuous average. Monthly `mean(spread_0)` is exactly 0 only if every one of >=12 daily estimates is <= 0
  (daily negative share is ~30-32% in the three sample months), so the exact-zero mass is ~0 (0.0% measured).
- Missing-by-rule: firms with N<12 valid days (0.6-0.8% of price>=$1 names) are DROPPED, not zero-filled: these
  are dead-traded stocks; the harness liquidity band nearly removes them already.
- Ties: float means, no material mass point (largest value-tie 0.06-0.11% of names in a month). Harness default
  tie handling (average) suffices. Preflight must still confirm the measured mass and coverage on the universe.

## 8. History needed

Two calendar months of SEP (target month + warm-up for the lag and the retained range); snapshot SEP starts
1997-12-31, first decision 1999-01 needs Dec 1998 plus warm-up from Oct-Nov 1998: available. Declare
`history_months` = 3 (return-window rule; this factor reads SEP prices). DAILY is not used directly.

## 9. OSAP metadata (SignalDoc)

Acronym BidAskSpread; Cat.Signal Predictor; Cat.Form continuous; Cat.Data Trading; Cat.Economic liquidity;
Authors Amihud and Mendelson; Year 1986; Journal JFE; SampleStartYear 1961, End 1980; Key Table "2 Spread Mean";
Test "double sort no LS"; Predictability 2_likely; Rep Quality 2_fair; Sign 1.0; Stock Weight EW; LS Quantile 0.142857;
Start Month 1; Portfolio Period 1. Definition: effective bid-ask spread based on Corwin-Schultz, scaled by price.
Notes: OSAP follows McLean-Pontiff, CS instead of the paper's Fitch quotes.

## 10. Proposed Sharadar mappings and deviations
```
hiprc  -> SEP.high     loprc -> SEP.low     prc -> SEP.close     volume -> SEP.volume
frame  = ctx.daily("SEP", ["high","low","close","volume"], days_back=~100)   # sorted by ID, date
```
The translator vectorises the SAS recursion per ID: step 1 mask; retained range = ffill of good (0<lo<hi) ranges
shifted one row; steps 2-4 by boolean masks; `lag` = previous row of the same ID; spread_0; keep the target
calendar month; `N>=12` else NaN; mean by ID. No harness universe filters, dates or ranking in the factor.

Deviations:
1. SEP `close` split-adjusted vs CRSP raw `prc`/`bidlo`/`askhi` (split-day artefact in OSAP absent here).
2. `volume==0` replaces CRSP negative `prc` and the bid/ask-on-no-trade values; `prc<=0` never fires.
3. Retained range seeded from a ~100-day warm-up, not full history.
4. Different price vendor than CRSP (high/low extrema may differ slightly); not measurable without CRSP.
Fields not in the map: none. `FactorDef`: no `dimension`; `history_months=3`; `family=None` until Phase C.
