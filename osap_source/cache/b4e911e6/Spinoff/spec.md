# Spinoff — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: APPROX (constructible from ACTIONS); PREFLIGHT_FAILED on the mass point (binary, ~99% zeros)
| OSAP input | Sharadar | status |
|---|---|---|
| CRSP `msedist` `acperm` > 999 (distribution's acquiring/receiving permno; upstream `CRSPAcquisitions.py` -> `SpinoffCo = 1`) | `ACTIONS` rows `action == 'spunofffrom'` (child side: `ticker` = spun-off company, `contraticker` = parent, `date` = distribution date, `value` = ratio) | approx: ACTIONS carries spin-offs only; OSAP's acperm set also includes other distributions that deliver a second company's shares |
| `FirmAgeNoScreen <= 24` (months since first CRSP monthly row of the permno) | months since the spin date (ACTIONS `date`), window (t-24m, t] via `ctx.actions("spunofffrom", 24)` | approx: OSAP age runs from first CRSP row, here from the ACTIONS spin date; equal for a clean spin-off |
| `permno, time_avail_m` (SignalMasterTable) | SEP presence x harness universe | mapped / harness-side |
- No IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob or ppegt input; no SF1 input.
- `TICKERS.relatedtickers` (28,209 non-null) links share classes, ADRs and prior tickers: NOT a spin-off indicator, not used.
- Parent side (`spinoff`, `spinoffdividend` rows, 572 and 525) is the wrong side: OSAP's `acperm` is the CHILD, so only `spunofffrom` is used.
- Missing-item rule: the flag is 0 (not NaN) for every permno outside the set (`np.where(..., 1, 0)`), so the absence is OSAP's own zero: coverage 100% by construction.
- MEASURED (harness universe, 276 signal months 1998-12-31 .. 2021-11-30, `build_universe` + `MonthContext.actions`, n = 1,739-2,867 names, mean 1,965):
  | quantity | value |
  |---|---|
  | distinct universe IDs with a `spunofffrom` row in the prior 24 months | mean 20.5 (min 6, max 43) names/month |
  | same, share of the universe | mean 1.06% (0.26-2.22%), so the zero block is 98.9% (97.8-99.7%) |
  | same, prior 12 months only | mean 10.6 (min 3, max 24) |
  | months with < 30 ones / < 10 ones | 237 of 276 / 13 of 276 |
  | distinct values; `qcut(q=10)` bins | 2 by construction (0/1); qcut on the rank collapses to 1-2 bins (98.9% tie block; not run, follows from the mode share) |
- **Recommendation: `preflight_failed` (mass point)**: the modal share (98.9% at 0) breaches the 10% cliff in every month and the "1" bucket sits under the
  30-name floor in 86% of months. Same shape as DivInit / IndIPO. A binary event indicator needs an event-study harness the design does not have.

## 2. Variables (exact source names)
`SignalMasterTable`: `permno, time_avail_m`; `m_CRSPAcquisitions`: `permno` (= distribution `acperm`), `SpinoffCo`. Upstream `CRSPAcquisitions.py`:
`crsp.msedist` -> keep `acperm > 999` and non-null `exdt`, rename `acperm` -> `permno`, `SpinoffCo = 1`, `drop_duplicates()` on (permno, SpinoffCo) -- the ex-date is DROPPED.

## 3. Formula
```
df = SignalMasterTable[permno, time_avail_m].merge(m_CRSPAcquisitions, on="permno", how="left")     # time-invariant flag by permno
df["FirmAgeNoScreen"] = groupby(permno).cumcount() + 1          # count of the permno's master-table months
Spinoff = where((SpinoffCo == 1) & (FirmAgeNoScreen <= 24), 1, 0)
```
A firm that was ever a distribution recipient scores 1 in its first 24 master-table months, 0 afterwards and 0 for all others. Output every (permno, month).

## 4. Timing / lag
Event-time flag (no ART/ARQ): known when the spin-off trades. OSAP holds it for the first 24 master-table rows of the permno. Harness: ACTIONS `date <= signal_asof`; `value` irrelevant. The spin date is the ex/distribution date (a few days before when-issued trading
may begin), so the flag can lead the first full trading month by days. Flow items / TTM smearing: none.

## 5. Filters
SignalDoc `Filter` empty. The 2-year age cap is the only screen. OSAP includes impure spin-offs (SignalDoc Notes: the paper drops ~75%).

## 6. Predicted sign
`Sign = +1.0` (Cusatis, Miles and Woolridge 1993: spun-off companies earn higher post-spin returns; Table 3B I-24, event study t = 2.43 as recorded in SignalDoc).

## 7. The mass-point question
A do-nothing firm = 0 and that is **98.9% of the universe** (ones mean 1.06%, 20.5 names/month). Binary: ties collapse to two average ranks, the standalone IC
is point-biserial and computable, but the decile LS (D10-D1) and the >= 30 names per decile floor cannot be met (only ~20 positives). No tie rule (remove / null
/ floor) creates ten deciles from two values. A variant that scored only the ~20 spin-offs against a matched non-event sample would be a different construction.

## 8. History needed (snapshot starts 1998-01)
- ACTIONS spin rows: 8-41 per year 1998-2021 (none in 1997 for `spunofffrom`; 1 stub row in `spinoffdividend`). Window 24 months is fully
  covered only from **2000-01**; 1999-01..1999-12 undercount (window reaches before ACTIONS begins): mean 15.5 flagged in 1999 vs 20.8 in 2000+. `lookback_months = 24`.
- Delisted-in-window firms vanish with the universe; ACTIONS rows persist past delisting.

## 9. OSAP metadata
Cusatis, Miles and Woolridge (1993), JFE; Cat.Data Event; Cat.Economic other; discrete; sample 1965-1988; Acronym2 Spinoff; Key Table "3B I-24"; test "event study
nonstandard data"; VW; Portfolio Period 1, Start Month 12; Predictability 2_likely, Signal Rep Quality 4_lack_data. SignalDoc Notes: OP uses CCH Capital Changes Reporter,
OSAP uses the CRSP acquisition file, includes impure spin-offs, 140 spin-offs in the paper. Source `Signals/pyCode/Predictors/Spinoff.py`.

## 10. Proposed Sharadar mappings
`Spinoff_t = 1` if `ACTIONS.action == 'spunofffrom'` for the ID with `signal_asof - 24m < date <= signal_asof`, else 0 (NaN for 1999 if a strict complete window is wanted).
Inputs to declare: `ACTIONS.action`, `ACTIONS.date`, `ACTIONS.ticker` (ID via `ticker_map("ACTIONS")`). Deviations: child-side ACTIONS spin-offs vs CRSP `acperm` set;
age from spin date not first CRSP row. Fields in map: none of these (`crsp.acperm`, `crsp.distcd` not in `field_map_index.yaml`); ACTIONS `spunofffrom` verified by the counts above.
