# AnnouncementReturn: earnings announcement return (Chan, Jegadeesh, Lakonishok 1996)

OSAP ref b4e911e69678a7424f318617a61d813f54183123. Source: `Predictors/ZZ2_AnnouncementReturn.py` (cached
`predictor.py`; the acronym's emitter is the `ZZ2_` script, `signaldoc_row.csv` row Predictor). Upstream cached:
`upstream_CompustatQuarterly.py` (rdq), `upstream_CRSPDaily.py`, `upstream_FamaFrenchDaily.py`.
DATA_SHA 198b281de1a0. field_map statuses are mappings, not proofs, until the field-checker verifies them here.

## 1. Data availability (verdict: APPROX, weak announcement-date proxy; preflight rules on data start)

The one input Sharadar lacks is the Compustat `rdq` (actual earnings-announcement date; OSAP zero-fills nothing,
the rows with missing rdq are simply dropped). Proxy exists, so not infeasible, but it is a partial one:

| input (OSAP) | field_map key | Sharadar | status |
|---|---|---|---|
| `rdq` (m_QCompustat) | `compustat.rdq_alt` | EVENTS.eventcodes contains '22' (8-K Item 2.02), earliest in [reportperiod, SF1 `date`] per ARQ quarter | approx |
| `rdq` fallback | `compustat.rdq` | SF1 ARQ `date` (filing date, frame name `datekey`) | approx (10-Q/10-K date, not the release) |
| `ret` (dailyCRSP) | `crsp.ret` | SEP.closeadj day-over-day, consecutive rows | mapped |
| `mktrf + rf` (dailyFF) | NO key; `public_sources` ruling | `ctx.market_daily(...)` raw VW market (SEP.closeadj + DAILY.marketcap) | approx |
| `permno/gvkey` link (CCM) | `crsp.smt_row` (SEP presence) | ticker identity in EVENTS/SF1/SEP | approx |

- MEASURED on THIS snapshot (new; the `rdq_alt` note only measured 2005 and 2015 and misses the cliff): first EVENTS
  row with code 22 is **2004-08-23** (Item 2.02 effective date). Match rate of ARQ (ticker, reportperiod) to a code-22
  8-K in [reportperiod, first datekey], all ARQ rows, by reportperiod year: 1998-2002 0.0%; 2003 0.0%; 2004 35.8%;
  2005 72.8%; 2006 72.4%; 2007 72.2%; 2008 72.3%; 2009 72.4%; 2010 73.3%; 2012 73.4%; 2014 74.4%; 2016 74.1%;
  2018 72.8%; 2020 67.9%; 2021 64.5%. Median lead of the 8-K over the SF1 date: 13 days (2005), 6 (2010), 3 (2015),
  1 (2017+). Pre-2004 the legacy 8-K items map to codes 71/81/91 (Reg FD/Other/Exhibits), not code 22; using them
  would flag every non-earnings 8-K, so they are NOT proposed.
- Consequence: announcement-date coverage is exactly zero for 1999-01..2004-07 = 67 of 276 decision months (24%,
  all in the first half); thin to ~2004-11; ~72% of reportperiods thereafter (all-ARQ rate; preflight sees the
  universe-restricted rate).
- No IBES (SignalDoc text says IBES fpi=6; the pinned code uses Compustat rdq), no options/13F/patents/segments/
  ratings/pensions/xad/emp/ob/ppegt. No fundamental VALUE is used, only dates: no zero-fill term.
- market_daily starts 1998-12-02 (DAILY.marketcap 1998-12-01): no market-adjusted window exists before that.

## 2. Variables
`rdq`, `ret` (daily CRSP total return), `mktrf`, `rf`, CCM link (gvkey, permno, link dates). Output per permno-yyyymm.
## 3. Formula (from the code, not from SignalDoc)

Per announcement date (distinct non-null rdq per gvkey): sum over a FOUR-trading-day window of the daily excess
return `ret - (mktrf + rf)`. rf cancels: `mktrf + rf` is the total VW market return, so the harness raw VW market
from `market_daily` is exactly the needed object (the `public_sources` "no rf" caveat does NOT bite). Key lines:
```
df["AnnouncementReturn"] = df["ret"] - (df["mktrf"] + df["rf"])
# time_temp = per-permno trading-day counter; anndat = 1 if time_d == rdq (exact-date merge)
time_ann_d = time_temp where anndat==1; +1 where anndat_f1 (next day is ann); +2 where anndat_f2; -1 where anndat_l1
groupby(permno, time_ann_d).agg(AnnouncementReturn=sum, time_d=max)
```
- Window = ann-2, ann-1, ann, ann+1: FOUR trading days, ARITHMETIC sum (not compounded). SignalDoc says "one day
  before to 2 days after"; the pinned code (comment: two before, one after) is authoritative. Flag in docstring.
- An rdq on a non-trading day never matches a CRSP row (exact-date merge): that quarter is dropped; do the same
  for an 8-K date not on SEP (drop, do not shift). Overlapping windows: later assignment wins (rare; ignore).

## 4. Timing and lag

- The window's value is stamped to the month of its LAST trading day (`time_d` max -> `time_avail_m`). Last window
  per permno-month kept. A missing month is filled with the most recent window value up to 6 months back
  (sequential fill of `shift(1..6)`: a stale value survives at most 6 months after its stamp month, then NaN).
- Harness reading: at signal_asof t use the latest window with ann+1 <= signal_asof and stamp month in (t-6m, t].
  An announcement on the last trading day of a month closes next month: the translator must NOT use windows whose
  last day is after signal_asof (look-ahead guard; no calendar dates in the factor).
- Upstream hygiene (`upstream_CompustatQuarterly.py`): quarters with rdq more than 6 months after quarter end are
  dropped (replicate as ann - reportperiod <= ~183 days); dedupe (gvkey, fyearq, fqtr) keeps the latest datadate.
- ART-as-of-filing vs ARQ: no value is read, only SF1 `reportperiod` and `date`; read them from `dimension=ARQ`
  (one row per quarterly filing; ART/ARY would add fiscal-year duplicates). `ctx.fundamentals_history` dedups to
  the LATEST datekey (an amendment), widening the EVENTS span; the earliest code-22 event in it is still right.
  No flow-difference smear applies.
- EVENTS `date` is the 8-K filing date, up to ~4 business days after the release; ann-2 usually still covers it.

## 5. Filters
SignalDoc `Filter`, `Quantile Filter`, `LS Quantile` blank; EW; the code has no price or exchange filter;
the harness universe applies.

## 6. Predicted sign
`Sign = 1.0`: higher announcement return predicts higher future return (SignalDoc t = 9.25, 'mv reg', Table 7 ABR,
sample 1977-1992). Orientation: long high, short low. No flip.

## 7. Mass-point question
A do-nothing firm (no announcement window closed in the last 6 months) gets NaN and is dropped; no zero default.
Expected share small for regular quarterly filers (a window lands every ~3 months and carries up to 6), but the
match rate caps it: ~27% of quarters unmatched under option B (preflight measures the universe share). The value
is a continuous sum of four returns less four market returns: exact ties ~0%. SEP no-trade rows carry the price
(return 0) while the market moves, so illiquid names get minus the market sum, not a zero (`crsp.ret` caveat 3).
Ties: harness default. A stale (carried) value ranks like a fresh one; staleness is 0..5 months.

## 8. History needed (snapshot starts 1998-01)
Return-window factor: declare `history_months=7` (anchor lookback <= 6 months + a few days of window + the day
before the first return). SEP from 1997-12-31, DAILY/market_daily from 1998-12-02, EVENTS from 1993-11 but code 22
only from 2004-08-23. With option B the first scorable month is about 2004-09 (thin) and full by ~2005-01.

## 9. OSAP metadata (SignalDoc)
AnnouncementReturn (Acronym2 AnnounRet); Predictor; continuous; Cat.Data Price; Cat.Economic earnings event;
Chan, Jegadeesh and Lakonishok 1996 JF; sample 1977-1992; Key Table 7 ABR; mv reg; 1_clear; 1_good; Sign 1.0; EW;
Portfolio Period 1; Start Month 12. Definition text: one day before to 2 days after (code: t-2..t+1).

## 10. Proposed Sharadar mappings and deviations

```
ann_date  = earliest EVENTS date with '22' in eventcodes.split('|') within [ARQ reportperiod, ARQ datekey]  # rdq_alt
ret_d     = SEP.closeadj[d] / SEP.closeadj[d-1] - 1  (consecutive rows, ctx.daily("SEP", ["closeadj"], days_back))
mkt_d     = ctx.market_daily(days_back)  (raw VW, stands in for mktrf + rf)
window    = the 4 SEP trading days ann-2..ann+1 (ann must be a SEP date; else drop the quarter)
AR        = sum(ret_d - mkt_d over window); keep the latest window per ID with ann+1 <= signal_asof, age <= 6 months
```
Two anchor options, measured above; RECOMMEND B, preflight decides:
- **A**: code-22 anchor with SF1 ARQ `date` as fallback everywhere. Coverage reaches 1999 and the ~27% unmatched, but
  before 2004-08 the signal is a filing-date CAR (a different event: the release precedes the 10-Q by weeks) inside
  the first-half IC bar, and it coincides with the release only after ~2017. A calendar-date switch between the two
  is forbidden (no dates in a factor).
- **B**: code-22 only, no fallback. NaN for 1999-01..2004-07 and for unmatched quarters; truer to OSAP's rdq. The
  first-half IC bar then tests ~2004-09..2010 only: state this in the verdict. Coverage bar 40%: matched ~72% of
  reportperiods plus 6-month carry should clear it from ~2005 on; preflight measures the pooled figure.

Deviations: (1) announcement-date proxy (8-K 2.02 vs Compustat rdq; 25-35% unmatched); (2) market = Sharadar VW
(prior-day cap weights, bad-print guards) vs CRSP VW + rf, rf cancelling exactly; (3) no delisting return; (4)
`closeadj` 3-decimal grid quantises returns below $0.50; (5) SEP carried-price no-trade days; (6) ticker identity
instead of the CCM link; (7) window per the code, not the SignalDoc text; (8) harness universe filter.

Fields NOT in the map: `mktrf`, `rf`, `ccm link` (covered by the `public_sources` ruling and harness identity).
Declare in `FactorDef.inputs`: `SEP.closeadj`, `DAILY.marketcap`, `EVENTS.eventcodes`, SF1 ARQ `reportperiod`/`date`
(only for option A). `dimension=ARQ` only if fundamentals_history is used for the span bounds. `family=None`.
