# Illiquidity — Amihud's illiquidity (Amihud 2002, Table 2)

OSAP ref b4e911e69678a7424f318617a61d813f54183123. Source `Signals/pyCode/Predictors/Illiquidity.py` (cached `predictor.py`,
`signaldoc_row.csv`; Cat.Signal == Predictor). Reads `dailyCRSP.parquet` (permno, time_d, ret, prc, vol). No upstream file cached
for this acronym (the CRSPDaily builder is described in IdioVol3F/upstream_CRSPDaily.py: ret, vol, prc from crsp.dsf). DATA_SHA 198b281de1a0.
field_map statuses are mappings, not proofs.

## 1. Data availability (verdict: FEASIBLE; every input maps, no zero-fill; deviations declared)

| input (OSAP) | field_map key | Sharadar source | status | note |
|---|---|---|---|---|
| `ret` (daily) | `crsp.ret` | `SEP.closeadj[d]/closeadj[d-1] - 1` | mapped | total return, no dlret; closeadj 3-dp grid quantises back-adjusted prices < $0.50 |
| `prc` (daily, abs) | `crsp.prc` | `SEP.close` | mapped | split-restated, SAME basis as `SEP.volume`; NEVER `closeunadj` (not split-restated; pairing it with split-restated volume breaks the dollar-volume product) |
| `vol` (daily, shares) | `crsp.vol` | `SEP.volume` | mapped | shares, split-restated; explicit 0 on a no-trade day (not null) |

- Declare inputs: `SEP.closeadj`, `SEP.close`, `SEP.volume`. (`DAILY.marketcap` only if the translator uses the `market_daily` calendar.)
- Not used: any SF1/Compustat item, IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob, ppegt.
- Deviations that keep this a feasible mapping (level differences, same formula): CRSP NASDAQ volume before 2004 double-counts
  dealer-to-dealer trades while SEP volume is consolidated (the exchange mix of the LEVEL differs; same note as DolVol); return from
  closeadj includes dividends and uses no delisting return; quantisation of closeadj on sub-$0.50 back-adjusted prices adds noise to |ret|.
- Recommendation: `feasible`.

## 2. Variables (exact source names)

`permno`, `time_d`, `ret`, `prc`, `vol`; derived `ill`, `time_avail_m` (yyyymm), `ill_lag1..ill_lag11`, `non_missing_count`.

## 3. Formula

```
ill_d      = |ret_d| / (|prc_d| * vol_d);   +-inf -> NaN            # vol_d = 0 gives inf (ret != 0) or NaN (ret = 0) -> NaN
ill_m      = mean over the month's days of ill_d, skipping NaN      # groupby(permno, month).mean
Illiquidity = mean(ill_m, ill_m_lag1, ..., ill_m_lag11)  only if ALL 12 are non-missing (count == 12), else NaN
```
Amihud's x10^6 scaling is absent (rank-invariant). Raw value, no log. The 12 months include the signal month t.
NOTE: the lags are `groupby(permno).shift(k)` over the permno's OWN monthly rows, i.e. panel ROWS, not calendar months: a name with a
missing month silently borrows an older month. Translator: use calendar months t-11..t and require all 12 (declared deviation; differs
only for names with a gap in their monthly history).

## 4. Timing / lag

The month-t value uses days of t (known at the t close), held t+1; no extra lag. No SF1 item, so no `dimension`/ART/ARQ issue and
nothing smears. The 1997-12 SEP stub month (`ctx.partial_months("SEP")`) never enters any window: the first signal 1998-12-31 reads
1998-01..1998-12 (measured stub_in_window = 0 for that month; later windows start later still).
Daily return for day d needs the previous trading day's closeadj: use the `market_daily` trading calendar (as CoskewACX does) so a
stray weekend/holiday SEP row does not create a return; nothing chained across a missing row. (A probe used a name-count calendar,
dates with >= 50% of the median active-name count; it is a shortcut, not the recommendation.)

## 5. Filters

The predictor file applies none. SignalDoc Filter = "abs(prc)>5, exchcd==1" (Open Source AP's TEST filter for the portfolio, NOT in
`Illiquidity.py`): price above $5 and NYSE only. The harness universe (price >= $1, NYSE/NASDAQ/NYSEMKT, relative cap and dollar-volume
screens) applies instead; the $5 and NYSE-only restriction is not reproduced (deviation; it makes the harness sample more micro-cap than OP's).

## 6. Predicted sign (SignalDoc)

`Sign = +1.0`: high illiquidity earns a HIGH subsequent return (liquidity premium). `ascending=True`. Cat.Economic `liquidity`, Cat.Data
`Trading`, Cat.Form `continuous`; Stock Weight EW; Portfolio Period 12, Start Month 6; Sample 1964-1997; T-Stat 6.6 (univariate reg,
Table 2); Predictability in OP 1_clear; Signal Rep Quality 1_good.

## 7. The mass-point question

A do-nothing (no-trade) name: days with vol = 0 become NaN and drop out of the monthly mean; a name with ret = 0 on trading days has
ill = 0 for those days. Measured on THIS snapshot, all 276 decision months, harness universe: zero-volume name-days are 0.001% - 0.18% of
the universe's window days (inside the universe; the field_map all-rows figure of ~5% is the full SEP incl. micro caps). Prototype of the
formula, `masspoint_stats`: max modal value share 0.059% of scored names (mean 0.053%), distinct values 100% of scored names, `qcut`
yields 10 bins in every month. No mass point; ties by average rank, no design needed. Scale is extremely right-skewed; ranks absorb it.

## 8. History needed, measured coverage

- OSAP: 12 consecutive monthly values (rows). Declare `history_months=11` (price within 7 days of the t-11 month-end; with the harness
  gate counted at the window start) and `lookback_months=12`. A name listed inside the window is unscorable by the all-12 rule.
- SEP starts 1997-12-31, so the first signal 1998-12-31 has exactly 12 full months (1998-01..12). Measured: 0 of 276 decision months
  unscorable. The snapshot start binds nothing here.
- Coverage of universe names scored: 96.7% mean over all 276 months (identical over scorable months, none excluded); min 86.2% at
  1999-12-31; by year 1998 94.7%, 1999 92.0%, 2000 88.4% (dot-com IPOs fail the all-12 rule), 2001 95.9%, 2002-2020 96.2-99.2%, 2021 93.3%.
  Scored names per month: min 1,693, median 1,842.
- Measured on THIS snapshot, DATA_SHA 198b281de1a0, 276 decision months (signals 1998-12-31..2021-11-30).

## 9. OSAP metadata

Acronym `Illiquidity`; Acronym2 `Illiquid`; LongDescription "Amihud's illiquidity"; Authors Amihud; Year 2002; Journal JFM; Sample
1964-1997; Cat.Signal Predictor; Sign +1.0; T-Stat 6.6; Key Table 2; Test reg; Stock Weight EW; Portfolio Period 12; Start Month 6;
GScholarCites 14,669. Detailed Definition: "Past twelve month average of: daily return (abs(ret)) divided by turnover
((abs(prc)*vol)". (The stated "turnover" is dollar volume, as the code shows.)

## 10. Proposed Sharadar mappings and deviations

- `ret` -> `SEP.closeadj` day-over-day (`crsp.ret` mapped, daily form).
- `prc`, `vol` -> `SEP.close` x `SEP.volume`, both split-restated (dollar volume split-invariant); never `closeunadj` x `volume`.
- Zero-volume days -> NaN (as OSAP's inf -> NaN), before the monthly mean; a month with no valid day is NaN and sinks the 12-month rule.
- Calendar months t-11..t (not panel rows). OP's price > $5 / NYSE-only filter not applied. CRSP NASDAQ volume double counting (pre-2004) vs SEP.
- Fields the field-checker must confirm on THIS snapshot: `crsp.vol` split basis against `crsp.prc` (close) on a split name, and the
  `crsp.ret` daily form. No new field_map key required.
