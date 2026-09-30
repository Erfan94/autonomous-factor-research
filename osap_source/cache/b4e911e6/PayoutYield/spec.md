# PayoutYield — Payout yield (Boudoukh, Michaely, Richardson, Roberts 2007, JF, Table 6B)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/PayoutYield.py` (cached `predictor.py`; `legacy.do` beside it). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`. Measurements: scratch, harness universe, 264 of 276 months (context only; the verdict turns on field availability, not on a measurement).

**VERDICT: data_unavailable (infeasible)**, two independent grounds:
1. `pstkrv` (preferred redemption value) is a numerator term of the signal and Sharadar has no SF1 field for it. It is NOT zero-filled: absent from `zero_fill_vars` in `CompustatAnnual.py` (list: nopi, dvt, ob, dm, dc, aco, ap, intan, ao, lco, lo, rect, invt, drc, spi, gdwl, che, dp, act, lct, tstkp, dvpa, scstkc, sstk, mib, ivao, prstkc, prstkcc, txditc, ivst) and no `fillna` in `predictor.py` or `legacy.do`. `(dvc + prstkc + pstkrv)` therefore propagates a missing pstkrv to NaN: OSAP's sample is, by construction, firms with a reported pstkrv (and dvc, also not zero-filled), a membership Sharadar cannot reproduce. The standing ruling (`book_equity_preferred_terms`: approx when preferred only adjusts book equity) does not apply: here preferred is part of the SIGNAL, and the ruling's last sentence keeps such predictors infeasible.
2. `prstkc` enters GROSS (purchase of common and preferred stock; the `- sstk` leg is absent). Sharadar has only the NET common flow `ncfcommon` (`field_map`: "Exact for net sstk - prstkc only"; preferred excluded; "a predictor needing gross repurchases alone remains infeasible", prstkcc note). `ncfcommon` cannot be split: 45.8% of universe names (median, 264 months; range 32.6-66.0%) have a net issue (ncfcommon > 0), 46.5% net buy back, 5.3% exactly zero, so gross buybacks of net issuers are not observable. Not substituted: `-ncfcommon` or its clip at zero is a different signal (NetPayoutYield already carries the net form).

## 1. Data availability
| OSAP input | key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `dvc` | compustat.dvc | `-ncfdiv` (outflow-negative, predominantly common; cash paid vs declared) | approx | NOT zero-filled: NaN (`dvt` only is) |
| `prstkc` | compustat.prstkc | `ncfcommon` (NET; gross unavailable) | approx, gross infeasible | ZERO-FILLED |
| `pstkrv` | compustat.pstkrv | none | unavailable | NOT zero-filled: NaN |
| `mve_permco` (t-6) | crsp.mve_permco | `SEP.close x SF1.sharesbas` at BME(t-6) (as EP, NetPayoutYield) | approx | no row 6 months back -> NaN |
| `ceq`, `sic` | compustat.* | `equity`; `TICKERS.siccode` (current; known trap `current_sic_signal_values`) | approx / mapped | `ceq > 0` or missing kept; sic 6000-6999 dropped |
IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob, ppegt: none. `sstk` appears in the load but not in the formula. Context: ncfdiv non-null 85.5-99.6% (median 97.0%), ncfcommon non-null 85.5-99.6% of the universe; fin (SIC 6xxx) 13.2-22.3% (median 19.8%).

## 2. Variables
`permno, time_avail_m, dvc, prstkc, pstkrv, sstk (loaded, unused), sic, ceq, datadate`; `mve_permco` from SignalMasterTable.

## 3. Formula in words and key lines
Total payouts (common dividends + purchase of common and preferred stock + preferred redemption value) over market equity six months earlier; non-positive yields dropped; financials, non-positive book equity and firms under 24 observations dropped.
```
PayoutYield = (dvc + prstkc + pstkrv) / mve_permco_l6      # calendar 6-month lag via merge; any NaN term -> NaN
PayoutYield <= 0 -> NaN ; keep (sic < 6000 or sic >= 7000) and (ceq > 0 or ceq NaN) ; obs_count >= 24
```
SignalDoc says `max(pstkrv, 0)`; the code (and legacy.do) adds pstkrv raw. The Stata original keeps only `ceq > 0` (drops missing ceq), the python port keeps missing ceq.

## 4. Timing / lag convention
Annual flows at datadate + 6 months held 12; ME at t-6. Flow over price LEVELS: no year-over-year difference, nothing to smear under TTM (no `dimension=ARQ`). ART-as-of-filing would be as in NetPayoutYield (flows read at BME(t-6)). Moot given the verdict.

## 5. Filters
As above (non-positive yield, SIC 6xxx, ceq, 24 observations). SignalDoc Quantile Filter empty.

## 6. Predicted sign
SignalDoc `Sign = 1.0` (high payout yield -> high returns). Cat.Economic valuation; Cat.Data Accounting; sample 1984-2003; EW; LS Quantile 0.1; Portfolio Period 12; Start Month 6; T-Stat 3.92 (Table 3 port sort implemented, not Table 6).

## 7. The mass-point question
Not reached (infeasible). For the record: a do-nothing firm (no dividend, no buyback, no preferred redemption) gives exactly 0, which OSAP sets to NaN (`<= 0`); net-issuing firms with small dividends are also excluded only where the sum is <= 0, so the sample is the positive side of the payout distribution.

## 8. History needed (snapshot starts 1998-01)
Not reached; would match NetPayoutYield (first scorable signal 1999-12-31 with `history_months = 24`).

## 9. OSAP metadata
PayoutYield; Boudoukh et al. 2007 (JF); Cat.Signal Predictor; 1_clear / 2_fair; Cat.Form continuous; Acronym2 PayYield; Key Table 6B; Test "port sort FF3 alpha"; Sign 1.0. NetPayoutYield's SignalDoc Notes: "See PayoutYield".

## 10. Proposed Sharadar mappings with deviations
None proposed. The two missing pieces are (a) `pstkrv` (no field; membership-defining because it is not zero-filled) and (b) gross `prstkc` (only net `ncfcommon`). Fields not in the map as a usable source: `pstkrv` (unavailable, LOOP RULING does not cover a signal term).
Recommendation: `infeasible` (data_unavailable). Do not substitute NetPayoutYield's formula or a clipped net flow.
