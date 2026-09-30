# ProbInformedTrading — probability of informed trading, PIN (Easley, Hvidkjaer and O'Hara 2002, JF, Table 6)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Signals/pyCode/Predictors/ProbInformedTrading.py`; cached `predictor.py`, `signaldoc_row.csv`, `upstream_PINData.py`.
Written fresh from source and `field_map_index.yaml`. Schema check against `data/SNAPSHOT_MANIFEST.yaml` (all 13 held tables), DATA_SHA 198b281de1a0. No regression run (nothing to regress on).

## 1. Data availability — VERDICT: DATA_UNAVAILABLE (recommend `infeasible`; no Sharadar field can stand in; OSAP does not zero-fill the missing item)
- The signal is not computed from any price or accounting field. `pin_monthly` comes from `PINData.py`, which downloads a third-party file (`pin_yearly.csv` inside a Dropbox `cpie_data.zip`; SignalDoc: Hvidkjaer's archived PIN 1983-2001 files plus the Duarte-Hu-Young extension) with permno-keyed yearly microstructure parameters `a` (information-event probability), `u` (uninformed arrival rate), `es`, `eb` (sell and buy arrival rates of informed traders). Those parameters are maximum-likelihood estimates from intraday BUY and SELL trade counts per day (TAQ/ISSM trade classification).
- Sharadar inputs that would be needed: daily buy and sell trade counts (or trade-by-trade data with Lee-Ready classification). Searched every column of all 13 held tables in the manifest (ACTIONS, DAILY, DESCRIPTIONS, EVENTS, METRICS, SEP, SF1, SF2, SF3, SF3A, SF3B, SP500, TICKERS): SEP holds only open/high/low/close/volume/closeadj/closeunadj; DAILY is valuation ratios; METRICS holds price/volume averages; SF2 is insider transactions; SF3* is institutional holdings. No trade count, no buy/sell split, no quote data, no PIN parameter. `field_map_index.yaml` has no PIN or trade-count key.
- Missing-item rule: the missing inputs are `a, u, es, eb`; `predictor.py` does no `fillna` on them (rows without a match are dropped by `dropna(subset=["ProbInformedTrading"])`), and `zero_fill_vars` is an annual-Compustat list. So no zero-fill exception: infeasible. No rough proxy (volume, turnover, daily range, Amihud) is an acceptable substitute: PIN is a structural-model output and a proxy is a different hypothesis, not a translation. Not used and also unavailable: IBES, options, 13F pre-2013, patents, segments, ratings, pensions, xad, emp, ob, ppegt.

## 2. Variables (exact source names)
`permno, gvkey, time_avail_m, mve_c` (SignalMasterTable); `permno, time_avail_m, a, u, es, eb` (pin_monthly); derived `pin`, `tempsize`, `year`. Upstream columns of pin_yearly: `permno, year, a, eb, es, u, d`.

## 3. Formula in words and key lines
```
pin = (a * u) / (a * u + es + eb)                      # EHO Eq. 5: expected informed-trade share of volume
tempsize = qcut(mve_c, 2) within time_avail_m (1 = smaller half, 2 = larger half)
pin[tempsize == 2] = NaN                               # large caps dropped each month: the signal exists for the SMALLER HALF only
```
Note the code comment says "top size quintile" while `q=2` is a median split (the code wins).

## 4. Timing / lag convention
Each yearly estimate for calendar year Y is expanded to 12 monthly rows (month m = 1..12) and stamped `time_avail_m = Period(Y, m) + 11` months, so the year-Y estimate is usable from Dec Y through Nov Y+1 (an 11-month availability lag). The value is annual and price-independent, no filing date, no ART/ARQ issue, no flow smearing. SignalDoc sample ends 1998; the code's Duarte et al. extension end date is not readable from the source (external file, not cached), so the scored span is unknown.

## 5. Filters
Drop where mve_c is in the top half of the month's cross-section (`mve_c` median split over the whole SignalMasterTable month, all CRSP names). SignalDoc Filter blank; Quantile Filter blank.

## 6. Predicted sign
SignalDoc `Sign = +1.0` (high PIN -> high returns). Notes: predictability depends on size and is only positive for the bottom 3 size quintiles. Cat.Economic liquidity, Cat.Data Trading, Cat.Form continuous, T-Stat 2.496, Key Table 6 (mv regression), sample 1984-1998, EW, LS Quantile 0.2, Portfolio Period 1, Start Month 6, Predictability 2_likely, Rep quality 1_good, cites 2,835.

## 7. The mass-point question
Not applicable to a constructed series (none exists). For the OSAP series: continuous ratio in (0,1); a firm with no informed trading (a = 0 or u = 0) would sit at exactly 0; unknown share. Moot under the verdict.
Coverage would be capped even with data: only the smaller half of CRSP survives the size split, and the harness universe (NYSE 20th-percentile size entry) is overwhelmingly the LARGER half of CRSP names, so little of the harness universe would be scored; the external file's own end date is unknown (not cached), so the number of scorable 1999-2021 months cannot be stated.

## 8. History needed (snapshot starts 1998-01)
Moot. The external file is not in the snapshot and cannot be added (no `data/` writes except the cache; a new table moves DATA_SHA, stop-and-ask 3).

## 9. OSAP metadata
ProbInformedTrading; Easley, Hvidkjaer and O'Hara; 2002; JF; Predictability 2_likely; Rep quality 1_good; Cat.Economic liquidity; Sign +1.0; T-Stat 2.496; EW; LS Quantile 0.2; Portfolio Period 1; Start Month 6; sample 1984-1998; Key Table 6; Test mv reg. Acronym2 PIN. Notes: "Table 3 has double sorts with size but no t-stats. Sign of predictability depends on size, only increases for bottom 3 size quintiles. Table 6 has mv reg, t=2.5 controlling for size, but size has t-stat of 2.8."

## 10. Proposed Sharadar mappings with deviations
None. Mapping table: `a, u, es, eb` -> no Sharadar field (unavailable); `mve_c` -> `DAILY.marketcap` (available, but only for the size split). Recommendation: no translation; frontier class data_unavailable with reason "PIN parameters come from intraday trade-direction estimates (third-party file); Sharadar has no trade counts or quotes; OSAP drops rows without PIN (no zero-fill)".
