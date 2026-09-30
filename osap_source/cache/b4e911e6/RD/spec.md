# RD — R&D expense over market value of equity (Chan, Lakonishok and Sougiannis 2001, JF, Table 4 "first year")

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Signals/pyCode/Predictors/RD.py`; cached `predictor.py`, `signaldoc_row.csv`, `upstream_CompustatAnnual.py`, `upstream_CRSPMonthly.py`, `upstream_SignalMasterTable.py`.
Written fresh from source and `field_map_index.yaml` (`compustat.xrd` detail read in `field_map.yaml`). DATA_SHA 198b281de1a0.
Measured on the harness universe (`build_universe`) + `MonthContext.fundamentals` (PIT, ART), all 276 decision months (signals 1998-12-31 .. 2021-11-30), recorded snapshot, scratch code only.

## 1. Data availability — VERDICT: PREFLIGHT_FAILED, coverage (constructible in principle; every reading fails a bar measured here ahead of the screen; recommend not translating). Mechanism: `harness/preflight.py` only WARNS below 40% coverage, so Reading B would pass preflight with a warning and then fail the Stage 1 `coverage_pct >= 40` bar; `preflight_failed` is the frontier class used for this case (Frontier). Reading A hard-fails preflight on the mass point
| input (OSAP) | field_map key | Sharadar | status |
|---|---|---|---|
| `xrd` (m_aCompustat, annual) | `compustat.xrd` | `SF1.rnd` (ART, dollars) | mapped, but the vendor zero-fills non-reporters |
| `mve_permco` (SignalMasterTable, month t) | `crsp.mve_permco` | `DAILY.marketcap` at the signal month-end (`ctx.universe["mkt_cap_usd"]`), already company-level | approx |
- Declare `FactorDef.inputs` would be `SF1.rnd`, `DAILY.marketcap`. Not used: IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob, ppegt.
- Missing-item rule: OSAP does NOT zero-fill `xrd`. `zero_fill_vars` in `upstream_CompustatAnnual.py` (nopi, dvt, ob, dm, dc, aco, ap, intan, ao, lco, lo, rect, invt, drc, spi, gdwl, che, dp, act, lct, tstkp, dvpa, scstkc, sstk, mib, ivao, prstkc, prstkcc, txditc, ivst) has no xrd; `xad0` and `xsga0` are separate zero-filled copies, not xrd; `RD.py` itself only does `dropna(subset=["RD"])`. So a firm without Compustat `xrd` gets NO RD value in OSAP, and the OSAP sample is the set of R&D reporters. SF1.rnd is 0 for non-reporters AND for reported zeros (inseparable; field_map: exact-zero 63.25% of non-null ART = vendor zero-fill). Faithful reading: `rnd == 0 -> missing` (drops genuine reported zeros as well, a small set declared as a deviation, bound unmeasurable).
- Because the faithful reading is not a zero-fill it is not automatically infeasible; it fails on coverage instead (section 7).

## 2. Variables (exact source names)
`xrd` (annual Compustat via `m_aCompustat`, columns `gvkey, time_avail_m, xrd`); `mve_permco` (SignalMasterTable `permno, gvkey, time_avail_m, mve_permco`; = sum over a permco's classes of `abs(prc) * shrout` at month t); derived `RD`.

## 3. Formula in words and key lines
R&D expense of the latest fiscal year divided by the company's market value of equity at the signal month.
```
df = signal_master.dropna(subset=["gvkey"]);  df = df.merge(m_aCompustat[gvkey, time_avail_m, xrd], how="inner")
RD = xrd / mve_permco ;   df = df.dropna(subset=["RD"])          # no fillna, no winsorise, no sign filter
```
Negative xrd (0.16% of non-null ART rows on the snapshot, restated/adjustment rows) gives negative RD and is kept; `mve_permco` is not guarded for zero (an `inf` would be kept; none expected).

## 4. Timing / lag convention
OSAP: annual `xrd` for fiscal year ending datadate is stamped `time_avail_m = datadate + 6 months` and carried 12 months (CompustatAnnual lines 215-246), so a month-t value uses xrd 6-17 months after fiscal year-end. `mve_permco` is CONTEMPORANEOUS (month t CRSP cap, not lagged). Harness: `ctx.fundamentals(["rnd"])` ART as of the filing date is 0-4 months old and updates quarterly (TTM of four quarters; a level, so no year-over-year smear and no `dimension` override). Coverage measured on both `lag_months=0` and `lag_months=6` (the latter closer to OSAP's staleness): pooled 31.9% / 30.6% (section 7). ART-as-of-filing makes the numerator fresher than OSAP's by roughly 6-13 months for the same fiscal year; R&D is slow-moving, the effect is a few percent of rank, not a look-ahead. SignalDoc Start Month 6, Portfolio Period 12.

## 5. Filters
None in the predictor and SignalDoc Filter blank (LS Quantile 0.2, EW). Harness universe replaces the all-CRSP + gvkey-linked sample. `fxusd != 1` gate is an option (numerator in reporting currency over a USD cap; non-USD reporters are <= 0.06% of members).

## 6. Predicted sign
SignalDoc `Sign = +1.0` (high R&D/market value -> high returns); `ascending=True`. Cat.Economic R&D, Cat.Data Accounting, Cat.Form continuous, Return 0.8875, T-Stat blank (Table 6 high-RD t = 4.44), Key Table "4, first year", Test port sort no LS, sample 1975-1995, Predictability 1_clear, Rep quality 1_good, cites 2,982.

## 7. The mass-point question (and the measurement that decides the verdict)
A do-nothing firm (no R&D) produces `rnd = 0` -> RD = 0 in Sharadar. Universe share at rnd == 0, 276 months (lag 0): min 40.1%, median 65.9%, max 70.0%; rnd null 0.3-42.8% (median 2.6%, high in early 1999 thin ART); rnd < 0: 0.0-0.3%; rnd > 0: 17.1-41.3% (median 31.1%).
Reading A (keep the zeros, i.e. treat the vendor zero as a value): coverage 57-99.7% but the mode is 0 for 56.6-70.7% of scored names (median 68.0%, well past the 10% decile cliff) and `qcut` yields only 3-6 of 10 bins in all 276 months. Preflight hard-fails (mass point). It is also not OSAP's construction (OSAP drops non-reporters, does not score them at 0).
Reading B (faithful: `rnd == 0 -> NaN`, score only rnd != 0, which is effectively rnd > 0 plus 0.1% negatives): scored n per month 391-1,187 (>= 300 every month, so >= 39 names per decile), modal value share 0.08-0.26%, ten qcut bins every month, BUT coverage (scored / universe, the `coverage_pct` bar of 40%): pooled 31.9% over 276 months (lag 0; 30.6% at lag_months=6); per month 17.1-41.4% at lag 0 (median 31.2%), only 4 of 276 months at or above 40% (2000-03, 2000-04, 2021-03, 2021-04), 0 of 276 at lag_months=6 (12.9-37.0%). By year (lag 0, median monthly coverage): 1998 17.1, 1999 27.9, 2000 35.4, 2001-2019 28.5-34.8, 2020 36.8, 2021 37.0. Excluding the thin 1998-12 .. 1999-11 ART months it is still 32.3% pooled, minimum 28.5%.
Conclusion: Reading B is OSAP's construct and fails the pre-registered coverage >= 40% bar (`stage1_standalone.min_coverage_pct: 40.0` in config/test_config.yaml) by ~8 points, structurally (about 65% of the harness universe is non-R&D firms, which OSAP scores as missing). Reading A is an unfaithful construction that hard-fails the mass-point preflight. No tie handling can fix either without changing the hypothesis (e.g. scoring non-reporters at 0 in a separate bucket, sector-restricted R&D scoring). Precedent: `Frontier` is classed preflight_failed on the same SF1.rnd zero-fill/coverage ground in `osap_source/osap_frontier.yaml`.
Tie handling if ever translated (Reading B): average rank on the rnd > 0 names, nulls renormalised; within-sector ranks with < 10 scored names fall back to the cross-section rank (R&D concentrates in a few sectors, so many sector-months would fall back).

## 8. History needed (snapshot starts 1998-01)
ART TTM is thin early: coverage 17.1% at 1998-12 and 27.9% median in 1999; no `history_months` price gate. All 276 months have a cross-section (n scored 391 at minimum), so `min_months` 120 is met; the failure is coverage, not history.

## 9. OSAP metadata
RD; Chan, Lakonishok and Sougiannis; 2001; JF; Predictability 1_clear; Rep quality 1_good; Cat.Economic R&D; Sign +1.0; Return 0.8875; T-Stat blank; EW; LS Quantile 0.2; Portfolio Period 12; Start Month 6; sample 1975-1995; Key Table "4, first year"; Test port sort no LS. Notes: "Table 4 has portfolio returns, but no-tstats. Table 6 does not show LS, but it has t-stat for high = 4.44." Acronym2 RD. Detailed: "R&D expense (xrd) over market value of equity."

## 10. Proposed Sharadar mappings with deviations (if the owner overrides the verdict)
```
rnd = ctx.fundamentals(["rnd", "fxusd"])["rnd"]          # ART, dollars; lag_months 0 (or 6 to mimic OSAP staleness)
me  = ctx.universe["mkt_cap_usd"].where(> 0)               # DAILY.marketcap at the signal month-end, contemporaneous as OSAP
RD  = (rnd.where(rnd != 0)) / me ;  non-finite -> NaN ;  ascending=True
```
Deviations: (a) `rnd == 0` treated as missing (vendor zero-fill; drops genuine reported zeros); (b) ART TTM at filing date replaces annual xrd aged 6-17 months; (c) `DAILY.marketcap` replaces CRSP `mve_permco` (primary close x 10-K total shares, company-level); (d) harness universe replaces gvkey-linked CRSP. Field mappings: `compustat.xrd` -> `SF1.rnd` (mapped, zero-fill caveat above), `crsp.mve_permco` -> `DAILY.marketcap` (approx). Fields not in the map: none.
Recommendation: frontier class `preflight_failed`; reason as in section 7; do not translate.
