# zerotrade1M — Liu (2006) turnover-adjusted zero-trading-day measure, 1-month window (zerotradeAlt1)

OSAP ref b4e911e69678a7424f318617a61d813f54183123. Source `Signals/pyCode/Predictors/ZZ1_zerotrade_zerotradeAlt1_zerotradeAlt12.py` (one
script emits zerotrade1M, zerotrade6M, zerotrade12M; cached `predictor.py`, `signaldoc_row.csv`, `upstream_CRSPDaily.py`; Cat.Signal ==
Predictor). Reads `dailyCRSP.parquet` (permno, time_d, vol, shrout; built from crsp.dsf). DATA_SHA 198b281de1a0 (measured 2026-09-30).
field_map statuses are mappings, not proofs.

## 1. Data availability (verdict: APPROX; every input exists, no zero-fill; near-degenerate signal flagged in section 7)

| input (OSAP) | field_map key | Sharadar source | status | note |
|---|---|---|---|---|
| `vol` (daily, shares) | `crsp.vol` | `SEP.volume` | mapped | split-restated shares; explicit 0 on a no-trade day (row kept, price carried forward: trap `sep_no_trade_days_are_rows`) |
| `shrout` (daily) | `crsp.shrout` | `SF1.sharesbas` (ART, latest filing <= the month's last trading day, age <= 15 months) | approx | company-level (all classes), split-restated to today's basis = same basis as `SEP.volume`, so `volume/sharesbas` is split-free |
| `time_d` (calendar) | -- | `SEP.date` on the market trading calendar | -- | stray weekend/holiday rows excluded (`market_trading_calendar`) |

- Declare inputs `SEP.volume`, `SF1.sharesbas`. No `SEP.close` needed. No IBES, options, 13F, patents, segments, ratings, pensions, xad,
  emp, ob, ppegt. No Compustat statement item: the project default ART is used; `sharesbas` is a point-in-time count (not a flow), so there is no
  `dimension` question and nothing to smear (ART vs ARQ equality not separately measured).
- Why `approx` and not `feasible`: `crsp.shrout` is status approx in the map (company-level count at filing cadence, not CRSP's per-PERMNO
  daily-ish series); SEP volume is consolidated (CRSP NASDAQ volume before 2004 double counts dealer trades) and SEP carries no-trade days as
  explicit volume-0 rows, which is the signal's raw material. Nothing is unavailable; mechanical preflight checks pass (section 7).
- Alternative shares route rejected: `DAILY.marketcap*1e6/SEP.close` (month-end). DAILY starts 1998-12-01, so windows opening in 1998 are NaN;
  measured on this snapshot it leaves qcut < 10 bins or an empty cross-section in 1 of the 276 decision months for this window.

## 2. Variables (exact source names)

`permno`, `time_d`, `vol`, `shrout`; derived `time_avail_m` (yyyymm), `countzero` (= 1 if vol == 0), `turn` (= vol/shrout, daily), `days`,
`ndays`, `temp_zerotrade`, `temp_zerotrade`, `zerotrade1M`.

## 3. Formula

```
countzero_d = 1 if vol_d == 0 else 0            turn_d = vol_d / shrout_d
per (permno, month):  countzero = sum, turn = sum over the month's days, ndays = count of rows
temp_zerotrade = (countzero + (1/turn)/480000) * (21/ndays)
zerotrade1M   = temp_zerotrade.shift(1)                 # previous month's value
```
Plain words: over the single calendar month t-1, count the days with zero trading volume, add a tie-breaker that is the reciprocal of total turnover scaled by the
deflator 480,000 (so the added term stays below 1 and only orders names with equal zero-day counts), then scale the window to 21 x 1
days by the number of rows in it. High value = many no-trade days or low turnover = illiquid. The SignalDoc text says "sum of monthly
turnover divided by ..."; the CODE is 1/turnover (Liu's formula), and the code governs. The deflator scale is irrelevant to ranks while the
tie-break term stays below the smallest nonzero zero-day value: measured: max tie-break term among countzero=0 names 0.226 (< 0.913, the min value of any countzero>=1 name).

## 4. Timing / lag

`.shift(1)` over the permno's own monthly rows: the signal dated month t uses the single calendar month t-1 and NOT month t itself (a one-month skip). No publication
lag (price/volume only), no ART/ARQ choice, no smear. Translator: read `ctx.daily("SEP", ["volume"], days_back=70)` (month t-1 is at most ~62 days before the signal date); drop the signal month's rows,
keep calendar months t-1..t-1, all 1 required (deviation: OSAP shifts panel ROWS, so a name with a missing month borrows an older month
there; here a gap is NaN). Declare `history_months=1` (price near the end of month t-1), `lookback_months=2`. A window containing the
partial snapshot-start month (ctx.partial_months("SEP")) is NaN (decisions volume_windows / momentum_partial_windows: full windows only).
Shares: `ctx.fundamentals_at_month_ends(["sharesbas"], [1..N])` (latest ART filing with datekey <= that month-end; every filing is <= signal_asof,
no look-ahead), applied to every day of that month. DEVIATION: OSAP's `turn` sum silently skips days with missing `shrout` (pandas sum) and a
shares-less month gives Turn = 0 -> inf; here a month without shares is NaN and sinks the window (strict; see the coverage rows of section 7). The translator may relax to 'sum over days with shares, >= 1 such month day' (a design choice).

## 5. Filters

The predictor file applies none. SignalDoc Filter `exchcd==1` (NYSE only) is OP's portfolio filter, not in the code: not applied; the harness
universe (NYSE/NASDAQ/NYSEMKT, price >= $1, relative cap and dollar-volume screens) decides.

## 6. Predicted sign (SignalDoc)

`Sign = +1.0`: high value (illiquid) earns a HIGH subsequent return; `ascending=True`. Cat.Economic `liquidity`, Cat.Data `Trading`,
Cat.Form `continuous`. Acronym2 `zerotradeAlt1`; Sample 1960-2003; Return 0.56, T-Stat 3.46; Key Table "2 LM1, Hp12m"; EW, LS quantile 0.1,
Portfolio Period 12, Start Month 12; Predictability 1_clear; Rep Quality 1_good; GScholar 1,521. Notes: 1-month version works for 6 or 12 month holding periods, but not 1 month.
DEVIATION (holding period): OSAP's published LM1 result is for a 12-month holding period (Portfolio Period 12) and SignalDoc says it does not
work at 1 month; the harness holds and scores one month, so this screen is off the paper's own horizon.

## 7. The mass-point question (measured on the harness universe, every scored decision month, signals 1998-12-31..2021-11-30)

What a do-nothing firm produces: a name with no volume at all in the window has `Turn = 0`, so `1/Turn = inf` (OSAP emits +inf; measured: 2 name-months in
276 at 1M, none at 6M/12M); translator sets it NaN. A name WITH volume but no zero-volume day has `countzero = 0` and a value equal
to the tiny tie-breaker, which is a continuous function of turnover: it is NOT an exact tie.

Measured on THIS snapshot (route: `SF1.sharesbas` ART as above), per decision month, scored names:

| measure | zerotrade1M |
|---|---|
| decision months with a full window | 276 of 276 |
| scored names per month | 1,734 min / 1,885 median / 1,953 mean |
| coverage of universe names (strict: rows in every month AND shares on every day) | 99.43 mean, 96.20 min (cov counted on universe names) |
| coverage if the turnover term were dropped (countzero only) | 99.82 mean, 98.36 min |
| modal exact-value share of scored names, range over months (percent) | 0.036 - 0.058 |
| distinct exact values vs scored names | equal in every month (0 tied pairs; modal share = 1/n) |
| `pd.qcut(rank, 10)` bins | 10 in 276 of 276 |
| share of scored names with ZERO zero-volume days (countzero == 0), percent | 99.94 mean, 99.38 min |
| names with countzero >= 1 | 1.2 names/month mean, 14 max; 105 of 276 months have NO name with a zero-volume day |
| zero-volume days as share of window days of scored names (percent) | 0.007 mean, 0.062 max |
| Spearman of the value with 1/Turn, per month | 0.997 mean, 0.986 min |

So there is no exact mass point (modal share <= 0.083% in every window, all deciles populated, preflight's 10% cliff is nowhere near). But the signal is
near-degenerate in substance: on average 99.3-99.9% of scored names have countzero = 0 and are ordered ONLY by the reciprocal-turnover tie-breaker,
so the cross-section is 0.983-0.997 (mean) rank-correlated with 1/turnover (low turnover = high value); the OSAP zero-day count acts only on the
handful of names listed above, which sit above every other name (groups never interleave, measured in all months). The within-universe
zero-day rarity is a property of the price >= $1 and dollar-volume screens, unlike the all-SEP figure of ~4.8% zero-volume rows in the
field_map. Tie handling: average rank on the exact value; `Turn == 0` -> NaN. Stage 1 therefore measures a turnover sort with a zero-day
overlay on 0 to 95 names a month (means 1.2/6.7/13.9 at 1M/6M/12M); expect it to overlap with any other turnover or illiquidity leg (and with the zerotrade siblings).
Early-year coverage: none (first signal 1998-12-31 reads 1998-11 only).

## 8. History needed

OSAP: 1 monthly rows plus one lag. Declare `history_months=1`, `lookback_months=2`. SEP starts 1997-12-31 (stub month); the first signal
1998-12-31 reads month 1998-11. Early coverage gaps are the share series at each month-end (SF1 ART filings start 1993), not price history.

## 9. OSAP metadata

Acronym `zerotrade1M`; Acronym2 `zerotradeAlt1`; LongDescription "Days with zero trades"; Authors Liu; Year 2006; Journal JFE; Sample 1960-2003; Cat.Signal
Predictor; Sign +1.0; Return 0.56; T-Stat 3.46; Key Table "2 LM1, Hp12m"; Test port sort; EW; LS quantile 0.1; Portfolio Period 12; Start Month 12;
Filter exchcd==1 (not in code). Detailed Definition: see signaldoc_row.csv ("sum of monthly turnover" wording; the code uses 1/turnover).

## 10. Proposed Sharadar mappings and deviations

- `vol` -> `SEP.volume` (split-restated; `volume == 0` is the no-trade flag), `shrout` -> `SF1.sharesbas` ART as of the month's last trading
  day; `turn = volume/sharesbas` daily, split-free because both are restated to today's basis (never pair with closeunadj).
- Trading calendar = `market_trading_calendar` over the universe's SEP dates (as factors/candidates/Illiquidity.py); a stray row is not a day.
- Calendar months t-1..t-1, not panel rows; all 1 months required; the 1997-12 stub window is NaN; `Turn == 0` -> NaN.
- Deviations: company-level shares, filing cadence; consolidated volume (CRSP NASDAQ pre-2004 double counting); OP's NYSE-only filter not
  applied; deflator kept at 480,000 (scale-free for ranks, verified above).
- Fields not in the map: none. Field-checker items: `crsp.shrout` via `SF1.sharesbas` ART coverage by year (early windows, table above) and
  `crsp.vol` zero-volume share inside the universe (measured here: 0.007-0.022% of window days).
- Verdict: `approx`. The three zerotrade variants share one code path (one helper is possible).
