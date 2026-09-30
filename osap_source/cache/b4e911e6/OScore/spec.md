# OScore — Ohlson O-Score, binary top-decile flag (Dichev 1998, JF, Table 5; SignalDoc Acronym2 OScore)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Signals/pyCode/Predictors/OScore.py` (cached `predictor.py`, `upstream_CompustatAnnual.py`, `upstream_GNPDeflator.py`, `upstream_SignalMasterTable.py`).
DATA_SHA 198b281de1a0. Written fresh from the source and `field_map_index.yaml` / `field_map.yaml`. Measured on the harness universe, 276 signal months 1998-12-31 .. 2021-11-30, ART.

## VERDICT: two constructions. (1) OSAP's published BINARY flag: preflight_failed by construction (mass point 87.4%, coverage < 40% in 179 of 276 months).
## (2) The CONTINUOUS O-Score OSAP ranks before binarising: APPROX, feasible, coverage marginal against the 40% bar. Recommend translating (2) as a declared deviation.

## 1. Data availability (every input exists in Sharadar)
| OSAP input | field_map key | Sharadar | status | OSAP missing-item rule |
|---|---|---|---|---|
| `at`, `lt` | `compustat.at`, `compustat.lt` | SF1 `assets`, `liabilities` (ART levels) | mapped | NaN |
| `act`, `lct` | `compustat.act`, `compustat.lct` | SF1 `assetsc`, `liabilitiesc` (ART levels) | mapped | ZERO-FILLED upstream (`zero_fill_vars`), but inert (below) |
| `ib` (and `ib` 12 months earlier) | `compustat.ib` | SF1 `netinc + netincdis` (ART TTM; PLUS, known trap sf1_netincdis_sign_inverted) | approx | NaN |
| `fopt`, then `oancf` | `compustat.fopt`, `compustat.oancf` | SF1 `ncfo` (ART TTM) | approx (real deviation, below) | `fopt.fillna(oancf)` |
| `sic` | `compustat.sic` | TICKERS.siccode (CURRENT) | mapped | NaN sic fails the keep test only if > 5999 / 4000-4999: NaN is dropped here |
| `gnpdefl` | FRED GNPCTPI (public source) | not needed (below) | n/a | inner merge |
| `prc` | SignalMasterTable | universe price >= $1 | n/a | merged only (no screen in code) |
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt. No unavailable input.
- `act`/`lct` zero-fill is INERT: with act = 0 the term `lct/act` is NaN (`safe_divide` returns NaN when the denominator is 0), so OScore is NaN for every name OSAP zero-filled. A Sharadar null act
  (unclassified balance sheet) is NaN too: same outcome, never zero-filled. The null block is mostly financials that the SIC screen already removes: among SIC-eligible names with assets, `assetsc` null is 2.1% (mean; 1.3-2.9%).
- GNP deflator: the term `-0.407*log(at/gnpdefl)` has `gnpdefl` merged on `time_avail_m` only, so it is one additive constant per month, rank-invariant within a month (and within a sector-month).
  No FRED input is needed and its absence is not a deviation for a ranked signal; `log(assets)` alone is used. (The same holds for the `at` currency unit.)
- `ib_lag12` is OSAP's `ib` from the monthly row 12 months earlier, i.e. the prior fiscal year. Missing -> the last term is NaN -> OScore NaN.

## 2. Variables (exact source names)
`fopt, at, lt, act, lct, ib, oancf, sic` (annual Compustat, $ millions), `ib_lag12`; SignalMasterTable `prc`; `gnpdefl`; `gvkey, permno, time_avail_m`.

## 3. Formula
```
fopt   = fopt.fillna(oancf)
OScore = -1.32 - 0.407*log(at/gnpdefl) + 6.03*(lt/at) - 1.43*((act - lct)/at) + 0.076*(lct/act) - 1.72*(lt > at)
         - 2.37*(ib/at) - 1.83*(fopt/lt) + 0.285*((ib + ib_lag12) < 0) - 0.521*((ib - ib_lag12)/(|ib| + |ib_lag12|))
OScore = NaN if 3999 < sic < 5000 or sic > 5999                       # keep SIC <= 3999 and 5000-5999
tempsort = decile of OScore within month (pd.qcut, duplicates="drop")
OScore (output) = 1 if tempsort == 10 ; 0 if tempsort in 1..7 ; NaN for deciles 8-9
```
Division by 0 or NaN -> NaN (`safe_divide`); log of a non-positive -> NaN. SignalDoc's "exclude price < 5" and "exclude the bottom quintile" are NOT in the code (price is merged but unused; the code drops deciles 8-9).

## 4. Timing / lag convention
- OSAP: annual values at `datadate + 6 months`; `ib_lag12` is the prior annual record. Portfolio Period 1 (monthly), Start Month 6.
- Here: SF1 ART at the latest filing; `ib` and `ib` one year earlier through `ctx.fundamentals_yoy(..., years=1)` aligned by REPORT PERIOD: two non-overlapping four-quarter windows, so the level
  (P) and its prior-year value (P-1y) are clean annual flows; no smear, no `dimension=ARQ` override. `ncfo` is a TTM flow over the same four quarters as `ib`; the ratios use same-date levels.
  ART-as-of-filing makes the score 6-15 months fresher than OSAP's and moves it up to four times a year.

## 5. Filters
SIC keep-test above (MEASURED: keeps 53.3% of the universe, 48.2-57.2%; it drops utilities, transport, communications, finance and ALL services incl. software, so ~53% is the coverage ceiling).
SIC is the CURRENT `TICKERS.siccode`. `abs(prc) > 5` is SignalDoc `Filter`, not in `predictor.py`, not reproduced (universe price >= $1). The LS is EW, long deciles 1-7 / short decile 10 in OSAP.
Within-sector ranking of a score whose sample excludes whole SIC ranges is well defined; sectors with fewer than 10 scored names fall back to the cross-section rank (harness).

## 6. Predicted sign
SignalDoc `Sign = -1.0` (high O-Score = high default risk -> low future return). `Cat.Form` discrete; `Cat.Economic` default risk; `Cat.Data` Accounting. Continuous translation: `ascending=False`
(low O-Score is the long side). The paper's pattern is non-monotonic (SignalDoc Notes), so a continuous D10-D1 is not the published test.

## 7. The mass-point question
- Binary flag (construction 1), MEASURED on 276 months: exactly 2 distinct values; 87.3-87.5% of the scored names sit on 0 (7 of the 8 retained deciles) every month; `qcut` gives 2 bins. Fails the 10% cliff on every probe.
  Coverage of the flag is 37.8% pooled n-weighted (mean 38.2%; 179 of 276 months < 40%; 15.1% at 1998-12). Not screenable as published.
- Continuous score (construction 2), MEASURED: distinct values == n scored every month (mean 927, range 430-1,192); modal share 0.11% mean, 0.23% max (1 name of 430 at 1998-12); 10 bins.
  Dummy terms: `I(lt > at)` is 1 for 2.9% of scored names (0.9-6.3%/month) and `I(ib + ib_lag12 < 0)` for 20.6% (11.1-39.7%); all four dummy combinations are present every month. They shift the score by constants of
  1.72 / 0.285 on top of continuous terms, so they create no tie.
- Do-nothing firm (no new filing): all inputs fixed, score constant between filings (price enters only the harness universe). Tie handling: rank average.

## 8. History needed (snapshot starts 1998-01)
Needs the latest filing AND the prior-year filing (`fundamentals_yoy years=1`), so ART must reach back to about 1997-Q4; `ib_lag` is null for 60.6% of SIC-eligible names at 1998-12 and 5.5% median.
Continuous coverage by year: 18.9% (1998-12), 26.0% (1999), 40.3% (2000), 45.9% (2001), 47-52% 2002-2012, 46-49% 2013-2021. **15 months < 40%, all 1998-12 .. 2000-02** (data start plus the SIC screen).
Pooled 47.2% (47.6% from 1999-03); marginal against the Stage 1 40% bar, not a hard failure. The preflight first probe month (1998-12) will read 18.9%.

## 9. OSAP metadata (SignalDoc)
Acronym OScore; Dichev; 1998; JF; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form discrete; Cat.Data Accounting; Cat.Economic default risk; Sample 1981-1995;
Key Table "5 highest 10 percent"; Test LS port; Sign -1.0; Return 1.17; T-Stat 3.36; EW; Quantile Filter none; Portfolio Period 1; Start Month 6; Filter abs(prc)>5; GScholarCites 1615.
SignalDoc Notes: Table 5 gives t = 3.36 if long low 70% and short high 10%; the price screen is not in OP but closer results come with it. OScore_q is a Placebo (quarterly variant), not this predictor.

## 10. Proposed Sharadar mappings and deviations
```
y   = ctx.fundamentals_yoy(["netinc", "netincdis", "assets", "liabilities", "assetsc", "liabilitiesc", "ncfo"], years=1)   # ART, by report period
ib, ib1 = netinc + netincdis, netinc_lag + netincdis_lag                     # PLUS; null netincdis nulls ib (3.6%, same rows as netinc null)
sd  = lambda a, b: a / b.where(b != 0)
keep = siccode.notna() & ~(((siccode > 3999) & (siccode < 5000)) | (siccode > 5999))
score = (-1.32 - 0.407*log(assets.where(assets > 0)) + 6.03*sd(liabilities, assets) - 1.43*sd(assetsc - liabilitiesc, assets) + 0.076*sd(liabilitiesc, assetsc)
         - 1.72*(liabilities > assets) - 2.37*sd(ib, assets) - 1.83*sd(ncfo, liabilities) + 0.285*((ib + ib1) < 0) - 0.521*sd(ib - ib1, |ib| + |ib1|)).where(keep)   # ascending=False
```
Deviations: (a) CONTINUOUS score, not the binary top-decile / bottom-70% flag (mass point 87.4%, coverage 37.8%); the harness D10-D1 replaces OSAP's long-70%/short-10% test, and the published pattern is non-monotonic;
(b) `ncfo` replaces `fopt` (fopt_approx, on OScore's PRIMARY input): Compustat fopt is funds from operations BEFORE working-capital changes, ncfo is after; on a proxy the sign disagrees on 14.4% of rows and the
rank correlation of ncfo/liabilities vs proxy/liabilities is 0.773 (field_map fopt); (c) `ib` = netinc + netincdis, approx (netinc is after non-controlling interest, extraordinary items not separable);
(d) GNP deflator dropped (rank-invariant additive constant, not a deviation for ranking); (e) SIC is current, not point-in-time; (f) ART at filing vs annual at datadate + 6 months, prior year by report period;
(g) `abs(prc) > 5` not reproduced; (h) non-USD reporters (<= 0.06% of members): `log(assets)` is in reporting currency (constant-shift only for USD), could gate `fxusd == 1`, not required.
Fields not in the map: none. `FactorDef`: ART default, `lookback_months` about 36 (latest filing plus prior year by report period), no `history_months`, `family=None` until Phase C.
