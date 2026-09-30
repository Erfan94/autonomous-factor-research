# VolSD — Volume variance: 36-month rolling standard deviation of monthly trading volume (Chordia, Subrahmanyam, Anshuman 2001, Table 5B DVOL)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/VolSD.py` (cached `predictor.py`; upstream `CRSPMonthly.py` beside it). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`. Measurements: harness universe, 11 probe decision months spread over 1998-12-31 .. 2021-11-30 (of 276), recorded snapshot, scratch measurement (no factor file).

## 1. Data availability verdict: APPROX (constructible; one trap that must be handled in the translation)
| OSAP input | Sharadar | status |
|---|---|---|
| `vol` (CRSP monthly share volume, as traded, /10000) | sum over the month of `SEP.volume x SEP.close / SEP.closeunadj` = AS-TRADED shares | `crsp.vol` mapped-with-deviation; SEP.volume is split-RESTATED to today's basis (field_map `sep_volume_split_restated`) |
No IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob, ppegt; no SF1; OSAP zero-fills nothing.
TRAP (look-ahead): VolSD is the std of RAW SHARES, unscaled. On the restated basis a cross-firm rank at a past date favours later splitters (future information). Fix: rebuild as-traded shares per daily row as `volume * close / closeunadj` (the field-map-endorsed route), then sum by month. Measured: restated-vs-as-traded Spearman of the signal 0.80-0.93 across probes (0.80 at 1999-12, 0.93 at 2020-12), so the difference is material. Verdict stays approx: CRSP NASDAQ volume before 2004 double counts dealer trades (exchange-mix level difference, inherent).

## 2. Variables
`monthlyCRSP`: permno, time_avail_m, `vol`. Only `vol`.

## 3. Formula
```
VolSD = vol.rolling_std(window_size=36, min_samples=24).over(permno)    # sample std (ddof=1) of the monthly vol, ROW window t-35..t
```
Plainly: the standard deviation of monthly share volume over the last 36 months (at least 24 observed). A raw-level measure: it scales with how many shares the firm trades, so it is a turnover/size proxy unless deflated (OSAP does not deflate).

## 4. Timing / lag
Month-t value, signal dated t, return t+1; no 6-month lag in predictor.py. Harness: the 36 calendar months ending at the signal month-end (incl. month t). `ctx.daily("SEP", ["close","closeunadj","volume"], ~1150)`. No SF1. Drop the 1997-12 stub with `ctx.partial_months("SEP")`. A split INSIDE the window creates a step in as-traded volume exactly as in OSAP (CRSP vol is unadjusted); not corrected (faithful). Stray weekend/holiday SEP rows: 0 found in the universe scope at all 11 probes (stray volume share 0.0).

## 5. Filters
SignalDoc Filter `exchcd==1` (NYSE only) is a portfolio/sample filter of the paper; it is NOT in predictor.py, which scores every stock. Not applied; the harness universe decides (also TICKERS.exchange is the current exchange only, `crsp.exchcd` approx).

## 6. Predicted sign
SignalDoc `Sign = -1.0` (t = 3.56, FM regression): high volume variability predicts low returns. `ascending=False`.

## 7. Mass-point question
Do-nothing firm: no trading for 24+ months gives std 0 (all months 0); a constant-volume series is also 0. Measured at the 10 probes with scorable months: modal share of scored names 0.046-0.061%, distinct values = scored names (1,641-2,170), measured exact-zero std: 0 names at all 11 probes (also 0 on the restated basis), `qcut` 10 bins. Continuous, no mass point; guard `std > 0`. Tie handling: none needed. Structural: rank correlation with market cap 0.27-0.56 (Spearman of the signal with cap, measured at the probes), i.e. a size-flavoured level signal; the harness ranks within sector, not within size (diagnostic for Stage 2 residualisation).

## 8. History needed (snapshot starts 1998-01; SEP from 1997-12-31)
Months usable = calendar months 1998-01 onward (1997-12 stub dropped). Decision month d uses signal d-1 (decision 1999-01 = signal 1998-12-31, index 0).
| rule | first scorable signal | unscorable decision months | scorable of 276 |
|---|---|---|---|
| OSAP min 24 of 36 (proposed exception, faithful) | 1999-12 | 12 (1999-01..1999-12) | **264** |
| full 36-month window (DEFAULT, `momentum_partial_windows`: history_months = full window) | 2000-12 | 24 | **252** |
Universe coverage measured: min-24 rule 0.0% at 1998-12, 81.2% at 1999-12, 82.9% at 2000-12, 86.5-96.5% thereafter; full-36: 0.0% (1999-12), 78.7% (2000-12), 82.3-93.1% thereafter. Both clear `rebalance.min_months` 120. DEFAULT under the recorded decision `momentum_partial_windows`: full window, `history_months=35`, `lookback_months=37`, 252 of 276 months, names with 24-35 months NaN (declared deviation from OSAP's min-24 rule). PROPOSED EXCEPTION for the coordinator to rule on: OSAP states the min-24 floor explicitly (a statistical floor, not a skipna accident), so the faithful version is `history_months=23`, 264 months. Both are given; the coordinator decides. State the choice in the factor docstring.

## 9. OSAP metadata
Chordia, Subrahmanyam and Anshuman (2001), JFE; Cat.Data Trading; Cat.Economic liquidity; continuous; sample 1966-1995; Acronym2 VolumeSD; Key Table 5B DVOL; Test "mv reg"; EW; Portfolio Period 1; Start Month 6; Predictability 1_clear / Signal Rep Quality 1_good; T-stat 3.56; 1,349 cites. Source `Signals/pyCode/Predictors/VolSD.py`. (LongDescription "Volume Variance"; notes "CVVOL and VOL in OP".)

Reconstruction tail (measured at 5 probes, 2000-12 .. 2021-11): rows with close/closeunadj > 1000 (massive reverse splits) exist for 0-10 universe names per probe (2-3 names in 2008/2021, 0 in 2016) and have volume < 1 on 9-50% of rows and volume == 0 on 0-26%, against 0.03-0.2% zero-volume rows overall; the restatement divides volume by the factor, so the as-traded reconstruction loses those shares. Names with any row > 100: 30 / 17 / 7 / 4 / 12 (2000-12 / 2003-12 / 2008-12 / 2016-12 / 2021-11), i.e. <= 1.5% of the ~2,000 universe; they can show spurious low-volume months. Not material to the verdict; closeunadj > 0 and close > 0 held on every row (0 bad-price rows). No guard beyond `closeunadj > 0` is proposed.

## 10. Proposed Sharadar mappings
```
d = ctx.daily("SEP", ["close","closeunadj","volume"], ~1150); drop the 1997-12 stub month
d = d[d.closeunadj > 0]                                           # guard: bad row -> dropped
d["sh"] = d.volume * d.close / d.closeunadj                       # as-traded shares (undo the split restatement)
m = d.groupby(["ID", month]).sh.sum()                             # monthly as-traded share volume (0 is an observation)
VolSD = m.groupby("ID") over months t-35..t: std(ddof=1), NaN if count < 36 (default full window; < 24 under the min-24 exception); where(> 0)
```
Declare `SEP.close`, `SEP.closeunadj`, `SEP.volume`; `ascending=False`; `history_months=35` (default; 23 under the min-24 exception); `lookback_months=37`.
Deviations: (a) restated volume rebuilt to as-traded via close/closeunadj (closeunadj is used only as the ratio that undoes the restatement, never paired raw with volume). (b) consolidated SEP volume vs CRSP exchange volume (NASDAQ dealer double count pre-2004). (c) calendar window (36 months) rather than 36 panel rows. (d) `exchcd==1` not applied. Fields: `crsp.vol` (map note + known_trap `sep_volume_split_restated`), `crsp.prc` (closeunadj ratio); both in the map.
