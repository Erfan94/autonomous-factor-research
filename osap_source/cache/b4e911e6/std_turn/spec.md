# std_turn — Share turnover volatility (Chordia, Subrahmanyam and Anshuman 2001, Table 5B; Acronym2 TurnovVol)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/std_turn.py` (cached `predictor.py`; upstream `CRSPMonthly.py` beside it). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`. Measurements: harness universe, 13 probe decision months 1998-12 .. 2021-11 (of 276), recorded snapshot, scratch script (no factor file).

## 1. Data availability verdict: constructible with approximations (APPROX), but the FAITHFUL signal is PREFLIGHT_FAILED (coverage, names per decile) because of OSAP's own size null
| OSAP input | Sharadar | status |
|---|---|---|
| `vol` (CRSP monthly volume) | `SEP.volume` summed over the calendar month | `crsp.vol` verified-with-deviation: split-RESTATED to today's basis; consolidated volume vs CRSP exchange volume (CRSP NASDAQ volume before 2004 double counts dealer trades, so levels differ by exchange mix) |
| `shrout` (per-PERMNO shares, month end) | route A: `SF1.sharesbas` (ARQ, PIT as of each month end); route B: `DAILY.marketcap*1e6 / SEP.close` on the month's last trading day | `crsp.shrout` approx: company-level (all classes) count vs CRSP per-class; BOTH routes restated to today's basis (known_trap `sf1_share_counts_split_restated`) |
| `prc`, `shrout` -> `mve_c` (size quintile) | `DAILY.marketcap` (market scope) | `crsp.me` mapped |
No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt. OSAP zero-fills nothing here.
Turnover pairing: `SEP.volume` is split-restated, so it must be divided by shares on the SAME restated basis. Both routes are (decision `volume_windows`, known_trap `sep_volume_split_restated`), so turnover is split-invariant. This differs from VolSD (raw share volume, rebuilt as-traded via close/closeunadj) because turnover is a ratio: restated volume / restated shares needs no undoing. Do NOT pair volume with closeunadj-based shares.

## 2. Variables
`monthlyCRSP`: permno, time_avail_m, `vol`, `shrout`, `prc` (for `mve_c = shrout*|prc|`).

## 3. Formula
```
tempturn = vol / shrout                                   # monthly turnover
std_turn = tempturn.rolling_std(window_size=36, min_samples=24).over(permno)   # sample std (ddof=1), ROW window
tempqsize = qcut(mve_c, 5) within time_avail_m (whole CRSP cross-section)
std_turn = NULL where tempqsize >= 4                      # "tiny spread per OP Tab3B": ONLY size quintiles 1-3 keep a value
```
## 4. Timing
Month-end CRSP row; monthly panel, no lag beyond the month. No fundamentals if route B; route A reads the latest ARQ filing as of each month end (filing-date cadence, quarterly). No flow items.

## 5. Filters
OSAP predictor.py: the size-quintile null above (this is IN the code, not only the SignalDoc). SignalDoc `Filter` = `exchcd==1` (NYSE only) is NOT in predictor.py; not applied, as for VolSD; the harness universe decides.

## 6. Predicted sign
SignalDoc Sign = -1 (high turnover volatility predicts low returns); T-Stat 3.74; Test "mv reg", Key Table 5B TURN; EW; Portfolio Period 1; Start Month 6. Would be `ascending=False`.

## 7. Mass-point question
A do-nothing firm (constant monthly turnover) produces std exactly 0. Measured at 13 probes, zero-std names 0 on both routes; distinct values equal the scored names (54-262 after the size null; modal share 0.4-1.9% of scored names). No mass point. Tie handling: if built, null an exact-0 std as VolSD does. Turnover is a level-free ratio, so the signal is not a pure size proxy, unlike VolSD.

## 8. History needed (full 36-month window required; OSAP's min_samples=24 not reproduced, decision `volume_windows`)
Snapshot SEP starts 1997-12-31 (1997-12 one-day stub, dropped) and DAILY starts 1998-12-01. Scored share of the universe, FULL window, size null NOT applied:
| signal month | route A (sharesbas) | route B (DAILY) |
|---|---|---|
| 1998-12 / 1999-12 | 0.0% / 0.0% (stub in window) | 0.0% / 0.0% |
| 2000-11 | 41.5% | 0.0% |
| 2000-12 (first clean window 1998-01..2000-12) | 45.1% | 0.0% |
| 2001-06 | 80.4% | 0.0% |
| 2001-11 (first route-B window 1998-12..2001-11) | 82.3% | 83.2% |
| 2003-12 .. 2021-11 (8 probes) | 82.2-91.3% | 82.3-92.3% |
Route A vs B agree: Spearman 0.9992 (2001-11, n=1,760), 0.9995 (2009-12, n=1,640), 0.9997 (2021-11, n=1,901); the level ratio A/B runs 0.08-20 in tails (share-count timing, filing cadence). Route A reaches 2000-12 but with thin early coverage (45%, 80% by 2001-06); B is cleaner from 2001-11. Both clear `rebalance.min_months` only if the size null is dropped.

### The decisive measurement: the size null (faithful construction)
The harness universe ENTERS at the NYSE 20th cap percentile; OSAP keeps only quintiles 1-3 of ALL CRSP-like stocks. Market cross-section = NYSE/NASDAQ/NYSEMKT common stocks from `DAILY.marketcap` at the signal date (6,115 names 2001-11 .. 4,311 in 2018-12; real CRSP-all includes more micro caps and non-common codes, which lowers its 60th percentile and keeps FEWER universe names):
| signal | 60th pct mkt cap ($M) | universe in quintiles 1-3 | scored after null (n / %) |
|---|---|---|---|
| 2001-11 | 261 | 3.3% | 54 / 2.5% |
| 2003-12 | 407 | 5.1% | 97 / 4.8% |
| 2009-12 | 490 | 5.2% | 78 / 4.3% |
| 2012-12 | 786 | 7.6% | 112 / 6.4% |
| 2018-12 | 1,201 | 13.1% | 208 / 11.1% |
| 2021-11 | 1,467 | 15.1% | 262 / 11.3% |
Over all probed months scored coverage is 0.0% (pre-2001-11) then 2.5-11.3%, versus the 40% coverage bar; names per decile (max 262/10 = 26, typically 5-20) versus the bar of 30. The 2000-11..2001-06 probes on route A show 1.6-3.5% (39-80 names). Fails both Stage 1 floors structurally in every probed month, before any sector-rank thinning (min 10 names per sector-month).

## 9. OSAP metadata
Chordia, Subrahmanyam and Anshuman (2001), JFE; Cat.Data Trading; Cat.Economic liquidity; continuous; sample 1966-1995; Acronym2 TurnovVol; Key Table 5B; Test "mv reg"; Predictability 1_clear / Rep Quality 1_good; 1,349 cites. Notes: "CVTURN and TURN in OP. Tab 3B has port sort but no LS or t-stats. Tab 5B has FM reg."

## 10. Proposed Sharadar mappings and the coordinator's ruling
Faithful build: daily `SEP` (`close`, `volume`), restrict to the market trading calendar, monthly V_m = sum of `SEP.volume`; shares_m = `DAILY.marketcap*1e6/SEP.close` on the month's last trading day (route B) or ART/ARQ `sharesbas` (route A); turnover = V_m / shares_m; std(ddof=1) over calendar months t-35..t, all 36 required, exact 0 -> NaN; then null where the month's market-cap quintile (market-scope `DAILY.marketcap`) is 4 or 5. Declare `SEP.close`, `SEP.volume`, `DAILY.marketcap`; `ascending=False`; `history_months=35`, `lookback_months=36`; first scorable signal 2001-11 (route B) or 2000-12 (route A).
Verdict: APPROX availability, FAITHFUL construction preflight_failed (coverage 2.5-11.3%, <=26 names/decile). Dropping the size null would give 82-92% full-window coverage (86-97% with the min-24 floor), but that is a construction deviation OSAP itself calls out (spread tiny in large caps), not a neutral change, and not adopted here: the coordinator rules. Flags: `SEP.volume` consolidated (CRSP NASDAQ volume before 2004 differs); sharesbas is company-level, SEP volume is primary-class (multi-class turnover understated); calendar window vs 36 panel rows; `exchcd==1` not applied.
