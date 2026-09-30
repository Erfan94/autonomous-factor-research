# VarCF — Cash-flow to price variance (Haugen and Baker 1996, JFE, Table 1 "variability in cf to price")

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Signals/pyCode/Predictors/VarCF.py` (cached `predictor.py`, `signaldoc_row.csv`).
Upstream helper `utils/asrol.py` read at the pinned ref (polars `rolling_std`, sample std, ddof = 1). Written fresh; DATA_SHA 198b281de1a0.
Measured on the harness universe (`build_universe`, recorded snapshot), all 276 decision months (signals 1998-12-31 .. 2021-11-30), scratch script only, no factor file.

## 1. Data availability — VERDICT: APPROX (all inputs present; ib remapped with a declared zero-fill; 60-month rolling history needed)
| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `ib` | `compustat.ib` | `netinc + netincdis` (ART; PLUS, the sign trap) | approx | NOT zero-filled: missing `ib` -> NaN month |
| `dp` | `compustat.dp` | `depamor` (ART) | mapped | ZERO-FILLED (`zero_fill_vars`) |
| `mve_permco` | `crsp.mve_permco` | `DAILY.marketcap` x 1e6 (MILLIONS of USD; company-level already) | approx | none: missing -> NaN month |
- Not used: IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob, ppegt. Nothing unavailable; VarCF.py has no `fillna` of its own (only `dropna` on the result).
- SF1 `netincdis` carries the OPPOSITE sign to the discontinued-operations income it describes (known_trap `sf1_netincdis_sign_inverted`): income before extraordinary items = `netinc + netincdis`, never minus. `ib` is used here, so the trap applies. A null `netincdis` is read as 0 ONLY where `netinc` is present (measured: `netincdis` null share equals the `netinc` null share, 4.8% of ART rows 2001-2021, i.e. it is null only where the whole TTM income block is missing; it is exactly 0 on 82% of all ART rows 2001-2021; row-wise check on 464,813 ART rows 2001-2021: `netinc` present with `netincdis` null on 0.0% of rows, so the fill never fires). This is a declared choice, not an OSAP fill: OSAP's `ib` is not filled. Zero-fill of `dp` (`depamor` null -> 0) mirrors OSAP (6.2% null ART 2001-21) and is applied only where `netinc` is present.
- Verdict APPROX, not feasible: `ib` is an approximation (netinc after NCI, extraordinary items not separable), and the flow is ART (quarterly refresh) not the annual stepwise series.

## 2. Variables (exact source names)
`SignalMasterTable`: permno, time_avail_m, mve_permco. `m_aCompustat`: permno, time_avail_m, ib, dp (annual values copied onto months). Derived `tempCF`, `sigma`, `VarCF`.

## 3. Formula in words and key lines
Every month compute cash flow (income before extraordinary items plus depreciation) divided by the month's company market equity; take the sample standard deviation of that monthly series over a trailing 60-month calendar window (current month included), require at least 24 non-missing months, and square it.
```
df["tempCF"] = (df["ib"] + df["dp"]) / df["mve_permco"]
df = asrol(df, "permno", "time_avail_m", "1mo", 60, "tempCF", "std", "sigma", min_samples=24)
df["VarCF"] = df["sigma"] ** 2
df_final = df.dropna(subset=["VarCF"])
```
`asrol` fills calendar gaps first (`fill_date_gaps_pl`), so a missing month is a null inside the 60-row window, and the window is calendar-, not row-based. The numerator is constant within a fiscal year in OSAP (annual copy); the variance therefore comes mostly from year-to-year steps in (ib + dp) and from monthly movement in `mve_permco`. SignalDoc Detailed Definition agrees ("rolling variance of (ib+dp)/mve_c over the past 60 months, min 24").

## 4. Timing / lag convention
OSAP: annual Compustat stamped datadate + 6 months, copied to months; `mve_permco` monthly. Signal at month t, held 12 months in the paper portfolio (Portfolio Period 12, Start Month 6).
Sharadar: at each of the 60 month-ends back from the signal (`ctx.fundamentals_at_month_ends([netinc, netincdis, depamor], range(60))`, ART, latest filing known at that month-end) and `ctx.at_month_ends("DAILY", ["marketcap"], range(60))` (tolerance 7 days; marketcap x 1e6 to USD, both on the same units as ART). So the numerator refreshes QUARTERLY (TTM, 4 quarters) where OSAP steps annually, and each lag sees only what was public then (no restated look-ahead). Flow items: ib and dp are TTM flows used as levels, never year-over-year differenced, so nothing smears under ART; `dimension=ARQ` would be wrong (4x too small). The 60-row window has overlapping TTMs (adjacent months share 3 quarters), as OSAP's does (adjacent months share the same year).

## 5. Filters
None in the predictor (`dropna` only); SignalDoc Filter blank. Here: harness universe only (price >= $1, relative size/dollar-volume screen). Negative `tempCF` (loss-making) is kept: variance is sign-free.

## 6. Predicted sign
SignalDoc `Sign = -1.0` (Haugen and Baker: high cash-flow variance -> low returns), so `ascending=False` (preflight reads the Sign column). Note the row's Notes state that OSAP finds "monotonic returns with a plus sign" on its own portfolios and that the plus sign is consistent with traditional theory, while the Sign column carries the paper's minus. The Sign column is the published orientation; a reversal would be a flipped-sign second hypothesis (|t| >= 2.74, name ending `Flip`). Cat.Economic "cash flow risk"; Cat.Data Accounting; Cat.Form continuous; T-Stat 2.5 (mv reg, nonstandard; mean coefficient over 90 regressions).

## 7. The mass-point question
A do-nothing firm (constant cash-flow-to-price for 24+ months) would give variance 0; that needs a flat (ib + dp)/mve series, which a varying market cap prevents, so no value is a mode. Continuous, right-skewed. Measured on all scored months (253): modal value 0.052-0.084% of scored names (median 0.058%); distinct values equal the scored count (1,194-1,940); ten `qcut` bins in every scored month. Tie handling: none needed beyond the harness average rank; heavy right tail (ratio of squares), so rank not z-score.

## 8. History needed (snapshot starts 1998-01)
A 60-month window, at least 24 months of (ib + dp)/cap. `lookback_months = 60` (window reach). `history_months` should be 24, NOT 60: OSAP needs only 24 non-missing months (min_samples), and a 60-month price-history gate would drop every name with 24-59 months of history that OSAP scores (the count >= 24 test in the factor already enforces the rule). Binding data starts: `DAILY.marketcap` begins 1998-12-01 (manifest min_date), so 24 month-end caps first exist at the 2000-11-30 signal; ART rows before 1999 are thin (netinc null 43.7% of ART rows dated 1998 vs 7.9% in 1999).
Measured (harness universe, 276 schedule months, signals 1998-12-31 .. 2021-11-30): months with ANY score **253** (first 2000-11-30, 1,194 names = 47.7% of the 2,504-name universe); first month with >= 50% coverage 2000-12-29 (252 months), >= 80% 2001-07-31 (245 months), >= 90% 2002-12-31 (185 months at or above 90%). Across scored months coverage min 47.7 / median 91.5 / max 95.2%; 2021-11 is 82.9% (young names lack 24 months). 23 months (1998-12 .. 2000-10) are unscorable (0 names). 253 >= rebalance.min_months 120, and all scored months lie in 2000-11 .. 2021-11, so the Stage 1 half split falls inside that range. The scored months are 253, NOT 276: Stage 1 coverage over the 276-month window should be read against that, and the 23 empty months cost the first two years of the sample.

## 9. OSAP metadata
VarCF (Acronym2 CF2Pvar); Haugen and Baker; 1996; Journal of Financial Economics; Predictability in OP `2_likely`; Signal Rep Quality `2_fair`; Cat.Economic cash flow risk; Cat.Data Accounting; Cat.Form continuous; Key Table "1 variability in cf to price"; Test "mv reg nonstandard"; Sign -1.0; T-Stat 2.5; EW; LS Quantile 0.2; Portfolio Period 12; Start Month 6; sample 1979-1993; Filter blank; cites 1647.

## 10. Proposed Sharadar mappings with deviations
```
L = range(60)
f = ctx.fundamentals_at_month_ends(["netinc","netincdis","depamor"], L)            # ART, as known at each month-end
f = f.dropna(subset=["netinc"]); cf = f.netinc + f.netincdis.fillna(0) + f.depamor.fillna(0)
m = ctx.at_month_ends("DAILY", ["marketcap"], L)   # mc = marketcap * 1e6 (USD)
t = cf / mc   (mc > 0);  per ID: n = count(t), var = t.var(ddof=1);  score = var where n >= 24
```
inputs `SF1.netinc`, `SF1.netincdis`, `SF1.depamor`, `DAILY.marketcap`; `lookback_months=60`, `history_months=24` (or none); `ascending=False`.
Deviations: (a) ART quarterly TTM as filed, not OSAP's annual copy stamped +6 months (the sample variance of a quarterly-stepping series differs from an annual-stepping one); (b) `ib` = netinc + netincdis with netincdis null -> 0 where netinc is present (netinc is after NCI; extraordinary items not separable); (c) `dp` null -> 0 where netinc is present (OSAP zero-fills dp); (d) `mve_permco` -> DAILY.marketcap (primary-class company-level, in millions; other classes priced at the primary's price); (e) the month-end marketcap (<= 7 days stale) stands in for CRSP month-end `mve_permco`; (f) first scored month 2000-11 (DAILY start), 253 of 276 months; (g) variance via pandas `var(ddof=1)` = polars rolling_std squared; (h) a month missing from the 60 is a missing obs, as OSAP's gap fill. Fields not in the map: none (`DAILY.marketcap` is the mapped `crsp.mve_permco`; `SF1.netincdis` appears in the `ib` entry). Recommendation: translate (approx), run preflight at the first, middle and last probe months; the first probe month (1998-12-31) is unscorable by construction and preflight should be read with that in mind.
