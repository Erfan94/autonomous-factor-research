# CPVolSpread — Call minus put implied volatility (Bali and Hovakimian 2009, Table 3 Panel B)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/CPVolSpread.py` (cached
`predictor.py`, `signaldoc_row.csv`, `upstream_bali_hovak.R` = `PrepScripts/bali_hovak.R`).
DATA_SHA 198b281de1a0.

## 1. Data availability (verdict: INFEASIBLE — the signal IS option-implied volatility)

- Core input: OptionMetrics IvyDB (`optionm.secprd<yr>` x `optionm.opprcd<yr>`): per-contract
  `impl_volatility`, `best_bid`, `best_offer`, `open_interest`, `exdate`, `strike_price`, `cp_flag`.
  Staged as `pyData/Prep/bali_hovak_imp_vol.csv`, joined to the master table on `secid`
  (OptionMetrics security id, via `OptionMetricsCRSPLink`).
- Sharadar publishes no option chains, no implied volatility, no open interest, no bid/ask quotes
  for options. The snapshot holds SEP/DAILY/SF1/SF2/SF3/SF3A/ACTIONS/EVENTS/TICKERS etc.; grep of
  `data/SNAPSHOT_MANIFEST.yaml` for "option" returns nothing, and `field_map_index.yaml` has no
  implied-vol, option-price, or `secid` key (its only "option" hits are `sstk` notes and SIC mappings).
- No zero-fill: OSAP drops rows with missing CPVolSpread (`dropna(subset=["CPVolSpread"])`);
  nothing is imputed. There is no OSAP zero-fill to make this `approx`.
- Not reconstructible: a realised-vol proxy, put/call volume or any SEP-derived stand-in would be a
  different signal (Sharadar has no options at all), not a deviation of this one.
- **Recommendation: `infeasible`.** Measured reason: required input (OptionMetrics implied vol by
  call/put) absent from the snapshot and the field map; OSAP does not zero-fill it.
- The harness-side parts (shrcd 10/11, SIC exclusions) would be available (`crsp.siccd` approx,
  TICKERS.siccode current-only) but are moot.

## 2. Variables (exact source names)

`mean_imp_vol` by `cp_flag` in {C, P, BOTH} -> pivoted to `mean_imp_volC`, `mean_imp_volP`;
`mean_day`, `nobs`, `ticker`, `secid`, `date`; from SignalMasterTable `permno`, `time_avail_m`,
`secid`, `sicCRSP`.

## 3. Formula

Per option (upstream R): keep observations with 30 <= exdate-date <= 90 days, open_interest > 0,
best_bid > 0, non-NaN impl_volatility, (ask-bid) < 0.5 x midpoint, and near-the-money
|ln(close / (strike/1000))| < 0.1. Keep each optionid's last observation in the month; average
`impl_volatility` within (secid, cp_flag, month).
```
CPVolSpread = mean_imp_volC - mean_imp_volP
```
Rows with cp_flag == "BOTH" and `mean_day < 0` are dropped; closed-end funds (sicCRSP 6720-6730)
and REITs (6798) excluded. Level, not a change (the change version is the separate `dCPVolSpread`).

## 4. Timing / lag

Options stamped at the month's last day, joined to `time_avail_m` of the same month (no extra lag;
OSAP then applies its usual month-t availability to the portfolio at t). ART-as-of-filing is
irrelevant: no fundamentals. No flow items, no TTM smear.

## 5. Filters

OSAP SignalDoc Filter `shrcd%in%c(10,11)`; sic exclusions above; drops missing secid (stocks
without listed options). Note in SignalDoc: paper says NYSE only; OSAP finds all stocks closer.

## 6. Predicted sign

SignalDoc Sign = +1 (higher call-minus-put vol -> higher returns); Cat.Economic `optionrisk`,
Cat.Data `Options`, Cat.Form continuous, Journal MS, sample 1996-2004, in-paper t=4.2 port sort,
LS quantile 0.2, VW, start month 6, Portfolio Period 1.

## 7. Mass-point question

Continuous difference of two averages; no do-nothing firm, no mass point. Coverage, not ties, is
the issue: only stocks with liquid listed ATM options, 30-90 day, both call and put present in the
month, roughly a minority of CRSP names in early years. Moot here (no data).

## 8. History needed

OptionMetrics starts 1996-01. The snapshot has no options at any date, so the history question is
unanswerable; nothing can be built from 1998-01 onward.

## 9. OSAP metadata

Acronym CPVolSpread; Cat.Signal Predictor; Bali and Hovakimian 2009 MS; Predictability in OP
1_clear; Signal Rep Quality 1_good; Key Table 3 Panel B; Return 1.045, T-Stat 4.2; GScholar cites
499 (2025-09). Sibling predictor `dCPVolSpread` (same OptionMetrics input) is a separate row.

## 10. Proposed Sharadar mappings

None. Not in the field map: OptionMetrics `impl_volatility`, `cp_flag`, `secid`, `open_interest`,
option `best_bid`/`best_offer`/`strike_price`/`exdate`. No field-checker run is warranted.
Frontier row text: "OptionMetrics implied volatility; Sharadar publishes no options data".
