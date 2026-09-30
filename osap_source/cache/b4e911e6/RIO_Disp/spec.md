# RIO_Disp — Residual institutional ownership among high forecast-dispersion stocks (Nagel 2005, JFE, Table 2)

OSAP ref b4e911e69678a7424f318617a61d813f54183123 (cache b4e911e6). Emitted by
`Signals/pyCode/Predictors/ZZ1_RIO_MB_RIO_Disp_RIO_Turnover_RIO_Volatility.py` (cached as `predictor.py`; no `RIO_Disp.py`).
Upstream read: `upstream_IBESEPSUnadjusted.py`, `upstream_InstitutionalHoldings13F.py`. SignalDoc row (Cat.Signal ==
Predictor): Cat.Data = 13F, Cat.Economic = short sale constraints, Predictability 1_clear, Quality 1_good.
DATA_SHA 198b281de1a0. Siblings from the same script: RIO_MB, RIO_Turnover, RIO_Volatility.

## 1. Data availability (verdict: DATA_UNAVAILABLE, and also `data_start` -> recommend `infeasible`)

| input (OSAP) | Sharadar | status |
|---|---|---|
| IBES `stdev` (cross-analyst std of EPS forecasts, `fpi == "1"`, summary file) | none | unavailable |
| `tickerIBES` link | none | unavailable |
| `instown_perc` (TR_13F, Thomson s34) | SF3A `shrunits` x1000 / shares outstanding (derived) | no field_map key; 2013-06-30+ only |
| `at` (m_aCompustat) | SF1.assets (`compustat.at`) | mapped |
| `mve_c`, `exchcd` (SignalMasterTable) | DAILY.marketcap (x1000: OSAP is $ thousands), TICKERS.exchange | approx |

- **IBES dispersion does not exist on Sharadar** (no estimate, forecast or dispersion item; see the REV6 spec for the
  DESCRIPTIONS search). Nothing stands in for forecast dispersion.
- **No zero-fill rescue for the conditioning variable.** `Disp = stdev/at if stdev > 0 else NaN`: missing or zero dispersion
  is excluded, never filled. `RIO_Disp = cat_RIO if cat_Disp >= 4 and cat_Disp not null`; with no Disp the signal is empty for
  every stock. (The script's zero-fill of `instown_perc` is a separate matter; see RIO_MB spec section 1.)
- 13F from 2013-06-30 only: same count as RIO_MB, **94 scorable decision months < rebalance.min_months 120**.
- Recommendation: **infeasible** (data_unavailable: IBES stdev; data_start: 13F 94 months).

## 2. Variables (exact source names)

IBES_EPS_Unadj: `tickerIBES`, `time_avail_m`, `stdev` (`fpi == "1"`). TR_13F: `permno`, `time_avail_m`, `instown_perc`.
SignalMasterTable: `permno`, `tickerIBES`, `time_avail_m`, `exchcd`, `mve_permco`, `mve_c`. m_aCompustat: `at`, `ceq`, `txditc`.
monthlyCRSP: `vol`, `shrout`, `ret`. Intermediates `sizecat`, `temp`, `RIO`, `RIOlag`, `cat_RIO`, `Disp`, `cat_Disp`.

## 3. Formula (same RIO as RIO_MB; see its spec for the full key lines)

```
RIO      = ln(t/(1-t)) + 23.66 - 2.89*ln(mve_c) + 0.08*ln(mve_c)^2 ,  t = instown_perc/100, NaN->0, clipped to [.0001, .9999]
RIOlag   = RIO six calendar months earlier ; cat_RIO = quintile of RIOlag by month (fastxtile n=5), after dropping NYSE/AMEX-20th-pct-size
Disp     = stdev / at  if stdev > 0 ;  cat_Disp = quintile of Disp by month
RIO_Disp = cat_RIO  where cat_Disp >= 4 (the script first sets it for cat_Disp == 5, then the "patch" widens to 4 and 5)
```
The signal is the lagged residual-ownership QUINTILE (1..5), defined only for names in the top two dispersion quintiles.
SignalDoc: "We deviate a bit to avoid IBES detail file ... screen stdev > 0 and also keep both 4th and 5th quintiles of dispersion."

## 4. Timing / lag

RIO lagged six months (calendar). No 45-day 13F filing lag in OSAP (quarter-end `rdate` month, forward-filled by `tsfill`
between a permno's first and last report). Point-in-time on Sharadar: quarter Q usable for signals as-of >= Q + 45 days (SF3A
carries only the period-end `date`). No ART/ARQ issue for `at` beyond the mapped SF1 convention.

## 5. Filters

Drop stocks below the NYSE/AMEX (exchcd 1 or 2) 20th size percentile of `mve_c` before any sort; `stdev > 0`. The harness
universe already enters at the NYSE 20th percentile (leaves below the 15th): the size filter is nearly absorbed.

## 6. Predicted sign

`Sign = +1.0` (Return 0.54, T-Stat 2.47, conditional sort, Table 2): within high-dispersion stocks, higher residual
institutional ownership (less short-sale constraint) -> higher return.

## 7. The mass-point question

Output takes five values (1..5). Measured on the harness universe for the sibling RIO_MB and RIO_Turnover (same cat_RIO; see
RIO_MB section 7): 5 distinct values, modal share ~28% mean (22-36% over 94 months), so a 10-decile sort collapses to 5 bins
(`pd.qcut(q=10, duplicates="drop")` cannot produce 10 bins from 5 values; the harness decile cliff is 10% modal share). Coverage
would be two of five Disp quintiles: at most 40% of names with IBES `stdev > 0` (RIO_MB's single-quintile analogue measured 18.4%, so
roughly 37% before IBES coverage gaps), at or below the 40% Stage 1 coverage bar. Not measured for Disp itself: no IBES input.

## 8. History needed

OSAP sample 1980-2003 (SignalDoc). Snapshot: SEP/SF1 from 1998, SF3A 2013-06-30..2026-06-30, so no decision month before 2014-03
has a real RIOlag; 94 by 2021-12. IBES absent throughout.

## 9. OSAP metadata

Acronym RIO_Disp, Nagel 2005, Journal of Financial Economics, "Inst Own and Forecast Dispersion"; Cat.Form discrete,
Cat.Data 13F, Cat.Economic short sale constraints, Key Table 2, Test port sort, EW, Portfolio Period 1, Start Month 12,
GScholarCites 1500. Output column `RIO_Disp`.

## 10. Proposed Sharadar mappings

None proposed. IBES `stdev`/`tickerIBES`: no Sharadar field (data_unavailable). `instown_perc`: SF3A.shrunits x1000 / (DAILY.marketcap
x 1e6 / SEP.closeunadj) - a derived approx, NOT in field_map_index.yaml (no 13F key; needs sharadar-field-checker only if a
sibling is ever pursued). Frontier row suggestion: `infeasible` - "IBES forecast dispersion absent; 13F 2013-06+ only (94
scorable months < 120); output is a 5-value quintile".
