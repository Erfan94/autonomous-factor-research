# RIO_MB — Residual institutional ownership among high market-to-book stocks (Nagel 2005, JFE, Table 2B)

OSAP ref b4e911e69678a7424f318617a61d813f54183123 (cache b4e911e6). Emitted by
`Signals/pyCode/Predictors/ZZ1_RIO_MB_RIO_Disp_RIO_Turnover_RIO_Volatility.py` (cached as `predictor.py`; no `RIO_MB.py`),
upstream `InstitutionalHoldings13F.py`. SignalDoc row (Cat.Signal == Predictor): Cat.Data = 13F, Cat.Economic = short sale
constraints, Predictability 1_clear, Quality 1_good. DATA_SHA 198b281de1a0. Siblings: RIO_Disp, RIO_Turnover, RIO_Volatility.

## 1. Data availability (verdict: DATA_START -> recommend `infeasible`; also fails the coverage and decile bars)

| input (OSAP) | Sharadar | status |
|---|---|---|
| `instown_perc` (TR_13F, Thomson s34; % of shares held by 13F filers) | SF3A `shrunits` (thousands of shares) x1000 / shares outstanding; SF3 for detail | NOT in field_map (no 13F key); 2013-06-30+ only |
| `mve_c` (SignalMasterTable, $ thousands) | DAILY.marketcap (millions) x1000 | `crsp.me` mapped |
| `mve_permco` (company-level cap for MB) | DAILY.marketcap (already company level) | `crsp.mve_permco` approx |
| `exchcd` (NYSE/AMEX size breakpoint) | TICKERS.exchange (CURRENT exchange only) | `crsp.exchcd` approx |
| `ceq` | SF1.equity (ART) | `compustat.ceq` approx (no preferred split) |
| `txditc` | SF1.taxliabilities (ART) | `compustat.txditc` approx; OSAP zero-fills txditc |

- Sharadar holds 13F from 2013-06-30 (SF3A 2013-06-30..2026-06-30, 53 quarter-ends; 670,115 rows). Pre-2013 13F is on the
  standing-unavailable list. Measured here: 49% of SF3A rows have a ticker that maps to no SEP security (non-US, funds, etc).
- **Scorable months, counted on the snapshot against the harness universe (decision window 276 months, signal as-of 1998-12-31..
  2021-11-30):** with the 45-day 13F filing lag, the first usable quarter (2013-06-30) is available at as-of 2013-08-30; RIO is lagged
  six months, so the first real RIOlag is at as-of **2014-02-28 (return month 2014-03)** and the last is as-of 2021-11-30
  (return month 2021-12): **94 months** (no-lag OSAP-faithful reading: quarter at as-of 2013-07-31, RIOlag from 2014-01-31, 95
  months). Either way **< rebalance.min_months 120 -> `data_start`**: Stage 1 would be inconclusive by construction.
- **OSAP zero-fill (read the rule literally):** the script does `temp = instown_perc/100; temp = 0 if missing; temp = .9999 if > .9999;
  temp = .0001 if < .0001`. A name with no 13F record becomes `.0001`. Applied to a snapshot with NO 13F before 2013-06, every
  name in 1998-2013 gets `.0001`, so `RIO = logit(.0001) + 23.66 - 2.89 ln(mve) + 0.08 ln(mve)^2` is a pure monotone function of
  market cap. Measured: 270 of 276 months would be "scorable" under that fill (first as-of 1999-06-30; the 6 lost months are the
  six-month lag), but in the 176 months before RIOlag has any real 13F content its Spearman correlation with log market cap is
  -0.96 (range -0.98..-0.85), against -0.38 in the 94 real-13F months. So the fill would produce a size-reversal sort
  (small names in the high-MB quintile) under the signal's name, not residual institutional ownership. This is `approx` only in
  a formal sense; **not recommended as an approx**. Primary verdict: `data_start` (real-13F months 94 < 120).
- Independent of data start, two preflight-type failures would follow (section 7): coverage 18.4% of the universe < the 40% bar,
  and a 5-valued output (no 10 deciles).

## 2. Variables (exact source names)

TR_13F: `permno`, `time_avail_m`, `instown_perc` (left merge; missing -> 0). SignalMasterTable: `permno`, `time_avail_m`, `exchcd`,
`mve_permco`, `mve_c`. m_aCompustat: `ceq`, `txditc` (and `at`). Intermediates `sizecat`, `temp`, `RIO`, `RIOlag`, `cat_RIO`, `MB`, `cat_MB`.
(The script also loads IBES `stdev`, `at`, `vol`, `shrout`, `ret` for its siblings; not used by RIO_MB.)

## 3. Formula in words and key lines

Residual institutional ownership (Nagel): log-odds of institutional ownership, minus its fitted dependence on size. Lag it
six months, cut it into quintiles within month, keep only the stocks in the top market-to-book quintile, and report the RIO quintile.
```
drop if mve_c <= NYSE/AMEX (exchcd 1 or 2) 20th percentile of mve_c that month                 # sizecat == 1
temp = instown_perc/100 ; temp = 0 if missing ; temp = min(temp,.9999) ; temp = max(temp,.0001)
RIO  = ln(temp/(1-temp)) + 23.66 - 2.89*ln(mve_c) + 0.08*ln(mve_c)^2
RIOlag = RIO at the same permno six CALENDAR months earlier (dict lookup on the pre-filter month row; missing if no row)
cat_RIO = fastxtile(RIOlag, n=5, by=time_avail_m)
MB  = mve_permco / (ceq + txditc)  with txditc = 0 if missing ; NaN if (ceq + txditc) < 0
cat_MB = fastxtile(MB, n=5, by=time_avail_m)
RIO_MB = cat_RIO if cat_MB == 5 else NaN
```
(SignalDoc text says ".9999 above, .0001 below" and "23.6"; the code uses 23.66.) Output takes values 1..5 and is NaN for ~80% of rows.

## 4. Timing / lag convention

RIO is lagged six months by construction. OSAP puts 13F at the quarter-end month (`rdate`), forward-filled between a
permno's first and last report, with NO 45-day filing lag (look-ahead of up to 45 days). Sharadar SF3A carries only the period-end
`date`; point-in-time use needs as-of >= quarter end + 45 days (used in the counts above). MB uses the merged m_aCompustat
row of the same month (OSAP's monthly Compustat build; its publication-lag convention was not traced here): on Sharadar the equivalent is SF1 ART
as of filing (`datekey`), which makes book equity timelier than OSAP's annual-lag convention. No flow item, so no ARQ/TTM smearing.
The harness signal as-of is the business month-end before the rebalance date, returns earned the following month.

## 5. Filters

SignalDoc Filter blank; in code: the NYSE/AMEX 20th-percentile size cut above, and `MB` missing when book (ceq + txditc) < 0. The
harness universe enters at the NYSE 20th percentile of cap and leaves below the 15th, so the size filter is nearly absorbed.

## 6. Predicted sign

`Sign = +1.0` (Return 1.07, T-Stat 4.91, conditional sort Table 2B, EW, Portfolio Period 1, Start Month 12): among high-MB
(glamour, high-short-cost-expectation) stocks, higher residual institutional ownership -> higher return; oriented ascending.

## 7. The mass-point question

Measured on the snapshot with the harness universe (94 real-13F months, as-of 2014-02..2021-11; RIOlag from SF3A, MB from SF1 ART
equity + taxliabilities (OSAP zero-fill of txditc), universe avg 1,965 names/month over 276 months; cohort quintiles taken within
the universe, an approximation of OSAP's broader CRSP cohort):
- **Do-nothing output**: a name outside the top MB quintile is NaN (no score). Among scored names the value is one of five integers.
- Distinct values: **5** in every month. Modal share **27.5% mean** (22.9%-35.6%), i.e. far over the 10% decile cliff:
  10 equal-count deciles cannot be formed from 5 values (`qcut(q=10, duplicates="drop")` returns <= 5 bins; within-sector average ranks
  break ties arbitrarily between sector peers). Ties: average rank; Stage 1 deciles collapse. Names per value ~71.
- **Coverage**: scored names 355 mean (338-414) of ~1,890 => **18.4% of the universe** (16.6%-19.0%), below the 40% Stage 1 bar,
  by construction (top MB quintile of universe names).
- Clipping mass inside RIO: 13.7% of universe names have `instown_perc` computed above .9999 (clipped; Sharadar shrunits / shares
  from DAILY.marketcap/SEP.closeunadj overstates ownership for some names), 0.7% below .0001, 0.5% without an SF3A row. Median
  computed instown about 0.86 in the 13F era.
- Zero-fill-era figures (for the record, not a verdict): 270 scorable months, modal share 27.1% mean (21.8%-42.8%), coverage 18.4%.

## 8. History needed

OSAP sample 1980-2003. RIOlag needs a mve_c row six months back and a 13F quarter. Snapshot: SEP/SF1/DAILY from 1998-01, SF3A from
2013-06-30: **94 scorable decision months** (as-of 2014-02..2021-11) vs min_months 120, even though the 13F era runs to 2026-06
(2022+ is the out-of-sample block and is not used for decisions).

## 9. OSAP metadata

Acronym RIO_MB, Nagel 2005, Journal of Financial Economics, "Inst Own and Market to Book"; Cat.Form discrete, Cat.Data 13F,
Cat.Economic short sale constraints, SampleStartYear 1980, SampleEndYear 2003, Key Table 2B, Test port sort, EW, Portfolio
Period 1, Start Month 12, Evidence "t = 4.91 in conditional sort", GScholarCites 1500. Output column `RIO_MB`.

## 10. Proposed Sharadar mappings

- `instown_perc` -> SF3A.shrunits x 1000 / (DAILY.marketcap x 1e6 / SEP.closeunadj), PIT at quarter end + 45 days, keyed by ticker
  -> ID. **Not in field_map_index.yaml** (no 13F key; would need sharadar-field-checker). Deviation: no percent-of-float column,
  shares basis differs from Thomson's, >100% values clipped to .9999 by OSAP's own rule.
- `mve_c` -> `crsp.me` (DAILY.marketcap x 1e6 / 1000 for $ thousands); `mve_permco` -> `crsp.mve_permco` (approx).
- `ceq` -> `compustat.ceq` (SF1.equity ART, approx); `txditc` -> `compustat.txditc` (SF1.taxliabilities, approx; zero-fill kept).
- `exchcd` -> `crsp.exchcd` (TICKERS.exchange, current only, approx).
- Frontier row suggestion: `infeasible` (data_start) - "13F from 2013-06-30 only: 94 scorable months (45-day lag, 6-month RIO lag)
  < rebalance.min_months 120; also coverage 18.4% < 40% and a 5-value output (modal share 27.5%)".
