# RIO_Turnover — Residual institutional ownership among high-turnover stocks (Nagel 2005, JFE, Table 2)

OSAP ref b4e911e69678a7424f318617a61d813f54183123 (cache b4e911e6). Emitted by
`Signals/pyCode/Predictors/ZZ1_RIO_MB_RIO_Disp_RIO_Turnover_RIO_Volatility.py` (cached as `predictor.py`; no `RIO_Turnover.py`),
upstream `InstitutionalHoldings13F.py`. SignalDoc row (Cat.Signal == Predictor): Cat.Data = 13F, Cat.Economic = short sale
constraints, Predictability 1_clear, Quality 1_good. DATA_SHA 198b281de1a0. Shares the RIO build with RIO_MB (full key lines there).

## 1. Data availability (verdict: DATA_START -> recommend `infeasible`; also fails the coverage and decile bars)

| input (OSAP) | Sharadar | status |
|---|---|---|
| `instown_perc` (TR_13F) | SF3A `shrunits` x1000 / shares outstanding (derived) | NOT in field_map (no 13F key); 2013-06-30+ only |
| `vol` (monthlyCRSP, monthly share volume) | SEP.volume summed over the month's trading days (`crsp.vol`: mapped daily volume) | mapped (monthly sum is harness-side) |
| `shrout` (monthlyCRSP) | DAILY.marketcap x1e6 / SEP.closeunadj, or SF1.sharesbas | `crsp.shrout` approx (today's split basis for sharesbas) |
| `mve_c`, `exchcd` | DAILY.marketcap x1000; TICKERS.exchange (current) | `crsp.me` mapped; `crsp.exchcd` approx |

- Same 13F start as RIO_MB: **94 scorable decision months** (as-of 2014-02-28..2021-11-30, return months 2014-03..2021-12, 45-day
  filing lag and six-month RIO lag; 95 without the filing lag) < rebalance.min_months 120 -> `data_start`.
- The script's zero-fill of missing `instown_perc` to 0 (then floor .0001) would let 270 of 276 months "score", but in the 176
  months without real 13F data RIOlag is a function of market cap alone (Spearman with log cap -0.96 mean), so the result is a
  size sort, not residual institutional ownership. Not accepted as `approx`; see RIO_MB spec section 1 for the measurement.
- Turnover itself is constructible (volume and shares are in Sharadar): only the ownership leg blocks it.
- SignalDoc detailed text says "Volatility quintile == 5" for RIO_Turnover; the CODE conditions on `cat_Turnover == 5` (text slip;
  the code is the authority).

## 2. Variables (exact source names)

TR_13F `instown_perc`; SignalMasterTable `permno`, `time_avail_m`, `exchcd`, `mve_c`; monthlyCRSP `vol`, `shrout`. Intermediates
`sizecat`, `temp`, `RIO`, `RIOlag`, `cat_RIO`, `Turnover`, `cat_Turnover`.

## 3. Formula

RIO and RIOlag/cat_RIO exactly as RIO_MB (logit of clipped ownership plus the size adjustment 23.66 - 2.89 ln mve + 0.08 ln(mve)^2,
lagged six calendar months, quintiled by month after dropping stocks under the NYSE/AMEX 20th size percentile).
```
Turnover = vol / shrout ;  cat_Turnover = fastxtile(Turnover, n=5, by=time_avail_m)
RIO_Turnover = cat_RIO if cat_Turnover == 5 else NaN
```
Residual institutional ownership quintile among the highest-turnover (most heavily traded) quintile; values 1..5.

## 4. Timing / lag

RIO lagged six months; Turnover is the same month's volume over shares (no lag). OSAP uses quarter-end 13F with no filing lag;
Sharadar PIT needs quarter end + 45 days (SF3A has only the period-end date). No ART/ARQ/TTM items (price and 13F data).
Sharadar volume is consolidated share volume (shares, not hundreds); the ratio is unit-consistent if `vol` and `shrout` are on the
same split basis (SEP.volume and unadjusted shares are; the field map warns `shrout` is on today's split basis for sharesbas).

## 5. Filters

NYSE/AMEX 20th-percentile size cut (absorbed by the harness universe). SignalDoc Filter blank.

## 6. Predicted sign

`Sign = +1.0` (Return 0.92, T-Stat 2.71, conditional sort, Table 2, EW, Portfolio Period 1, Start Month 12): within high-turnover
stocks, higher residual institutional ownership -> higher return; oriented ascending.

## 7. The mass-point question

Measured on the harness universe (94 real-13F months; universe ~1,890 names with RIOlag; cohort quintiles taken within the
universe; Turnover = SEP month volume / (DAILY.marketcap/SEP.closeunadj)):
- Output is one of five integers for scored names; NaN elsewhere. Distinct values **5** every month; modal share **28.9% mean**
  (22.4%-34.3%) vs the 10% decile cliff: a 10-decile sort collapses to 5 bins, ~76 names per value.
- **Coverage**: scored names 379 mean (359-449) => **19.6% of the universe** (18.7%-20.0%) < the 40% Stage 1 bar, by construction.
- Clipping in RIO as for RIO_MB: 13.7% of names >100% computed ownership (clipped to .9999), 0.7% below .0001.
- Zero-fill-era figures (record only): 270 scorable months, coverage 19.3%, modal share 26.6% mean.

## 8. History needed

OSAP sample 1980-2003. Snapshot SEP/DAILY from 1998-01; 13F from 2013-06-30 (SF3A): 94 scorable decision months < 120.

## 9. OSAP metadata

Acronym RIO_Turnover, Nagel 2005, Journal of Financial Economics, "Inst Own and Turnover"; Cat.Form discrete, Cat.Data 13F,
Cat.Economic short sale constraints, SampleStartYear 1980, SampleEndYear 2003, Key Table 2, Test port sort, EW, Portfolio Period 1,
Start Month 12, Evidence "t = 2.71 in conditional sort", GScholarCites 1500. Output column `RIO_Turnover`.

## 10. Proposed Sharadar mappings

- `instown_perc` -> SF3A.shrunits x 1000 / shares outstanding, PIT at quarter end + 45 days (NOT in field_map_index.yaml; 13F
  pre-2013 unavailable). `vol` -> `crsp.vol` (SEP.volume, month sum); `shrout` -> `crsp.shrout` (approx); `mve_c` -> `crsp.me`
  (x1000); `exchcd` -> `crsp.exchcd` (approx, current exchange only).
- Frontier row suggestion: `infeasible` (data_start) - "13F from 2013-06-30 only: 94 scorable months < min_months 120; also
  coverage 19.6% < 40% and a 5-value output (modal share 28.9%)".
