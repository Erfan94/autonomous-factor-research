# OPLeverage — Operating leverage (Novy-Marx 2011, ROF, Table III panel b; SignalDoc Acronym2 OperLeverage)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Signals/pyCode/Predictors/OPLeverage.py` (cached `predictor.py`, `upstream_CompustatAnnual.py`).
DATA_SHA 198b281de1a0. Written fresh from the source and `field_map_index.yaml` / `field_map.yaml`. Measured on the harness universe, 276 signal months
1998-12-31 .. 2021-11-30 (decision window 1999-01..2021-12), ART.

## 1. Data availability (verdict: APPROX, feasible; every input exists in Sharadar)
| OSAP input (`m_aCompustat`) | field_map key | Sharadar | status | OSAP missing-item rule |
|---|---|---|---|---|
| `xsga` | `compustat.xsga` | SF1 `sgna` + `rnd` (ART TTM) | approx (D&A embedded for some filers; sgna excludes R&D) | ZERO-FILLED by the predictor itself (`tempxsga`) |
| `cogs` | `compustat.cogs` | SF1 `cor` (ART TTM) | approx (D&A embedded for some filers) | NOT filled; NaN cogs gives NaN signal |
| `at` | `compustat.at` | SF1 `assets` (ART level) | mapped | NaN; at == 0 gives inf, kept by OSAP |
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt. No unavailable input.
- Missing-item rule checked in both places: `CompustatAnnual.zero_fill_vars` does NOT contain xsga, cogs or at (it fills `xsga0`, a separate column the predictor does not read);
  the predictor's own `fillna`-equivalent (`when xsga is null then 0`) zero-fills xsga only. So the xsga term is zero-filled by OSAP (no gate on sgna), cogs is not (gate `cor == 0 -> NaN`,
  ruling `vendor_zero_fills`). The zero-fill of the optional term is OSAP's own, so it does not downgrade the verdict below approx.
- OSAP-side filter not reproduced: upstream `CompustatAnnual` drops annual rows with null `at`, `prcc_c` or `ni` before any predictor reads them.
- MEASURED (harness universe, 276 months; bar 40%): coverage **85.4%** pooled n-weighted with the `cor == 0` gate (mean 85.8%, min 51.4% at 1998-12, 75.9% min from 1999-03, **0 months < 40%**;
  the 1998-12..1999-02 lows are the ART TTM warm-up); **96.1%** without the gate. Universe shares: `cor == 0` mean 10.7% (5.8-15.0%), `cor` null 3.6%;
  `sgna` null 3.6% and `sgna == 0` 4.3% (2.7-6.0%) are both zero-filled here (as OSAP).

## 2. Variables (exact source names)
`xsga, cogs, at` (annual Compustat, $ millions), `gvkey, permno, time_avail_m`.

## 3. Formula
```
tempxsga   = xsga if xsga notnull else 0
OPLeverage = (tempxsga + cogs) / at          # no filter, no winsorising, no lag of the denominator
```
Sum of SG&A (incl. R&D in Compustat) and cost of goods sold, scaled by total assets. `inf` (at == 0) not filtered by OSAP.

## 4. Timing / lag convention
- OSAP: annual values, `time_avail_m = datadate + 6 months`, held until the next annual record (Portfolio Period 12, Start Month 6).
- Here: SF1 ART at the latest filing (0-3 months old, cap `max_fundamental_age_months`). `cor`, `sgna`, `rnd` are TTM flows and `assets` is a same-date level: a within-period ratio,
  no year-over-year difference, no smear, no `dimension=ARQ` override. ART-as-of-filing makes the ratio 6-15 months fresher than OSAP's and moves it up to four times a year.

## 5. Filters
None in `predictor.py` and SignalDoc `Filter` is empty (no SIC, price or share-code screen; financials stay in). LS is EW quintile (LS Quantile 0.2) in OSAP, portfolio-stage, not reproduced.

## 6. Predicted sign
SignalDoc `Sign = +1.0` (high operating leverage -> high future return). `Cat.Form` continuous; `Cat.Economic` other; `Cat.Data` Accounting. Long HIGH: `ascending=True`.

## 7. The mass-point question
- A do-nothing firm (no new filing) holds all three inputs fixed: the ratio is constant between filings and moves only at a filing; it does not depend on price. Ties need identical
  (sgna + rnd + cor)/assets across names.
- MEASURED modal-value share of the scored cross-section (gated): **0.06% mean, 0.13% max** over 276 months; distinct values == n scored (mean 1,678; range 1,172-2,416); 10 bins every month.
- Names with `sgna == 0` and `rnd == 0` score cor/assets (a real, not stale, value). `cor == 0` names are the gated ones: ungated they would score (sgna + rnd)/assets and understate; the gate is part of the construction.
- Tie handling: rank average. Guard `assets > 0` (a zero denominator gives inf; negative is a sign flip).

## 8. History needed (snapshot starts 1998-01)
One latest filing; no `history_months`, no `lookback_months` beyond the filing-age cap. ART revenue/cor coverage is thin at the start (51% of the universe scored at 1998-12..1999-02, 75-80% by 1999-06,
~88% from 2005): a data-start effect, not a gate.

## 9. OSAP metadata (SignalDoc)
Acronym OPLeverage; Acronym2 OperLeverage; Novy-Marx; 2011; ROF; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form continuous; Cat.Data Accounting;
Cat.Economic other; Sample 1963-2008; Key Table 3b; Test port sort; Sign +1.0; Return 0.51; T-Stat 3.38; EW; LS Quantile 0.2; Portfolio Period 12; Start Month 6; no Filter; GScholarCites 534.
Definition: "Sum of administrative expenses (xsga) and cost of goods sold (cogs), scaled by total assets (at). Use xsga = 0 if xsga is missing."

## 10. Proposed Sharadar mappings and deviations
```
f   = ctx.fundamentals(["cor", "sgna", "rnd", "assets"])                  # ART
xs  = f.sgna.fillna(0) + f.rnd.fillna(0)                                   # xsga = sgna + rnd (decision grsaletogroverhead_xsga); missing or zero sgna -> 0, as OSAP
ok  = (f.cor.notna()) & (f.cor != 0) & (f.assets > 0)
OPLeverage = ((xs + f.cor) / f.assets).where(ok)                           # ascending=True
```
Deviations: (a) `cor` is as-reported cost of revenue and INCLUDES D&A for some filers where Compustat `cogs` excludes it; `sgna` likewise. field_map xsga note: OPLeverage is HIGHER by the embedded D&A
(median 0.034 of assets on >=90%-embedded rows vs a 0.673 median level): rank rho 0.999 / 0.999 / 0.995 (1999/2008/2020), ~10% of names move a decile, judged immaterial; (b) `cor == 0 -> NaN` (vendor
zero-fill; OSAP does not fill cogs); (c) `sgna` null or 0 zero-filled, as OSAP's `tempxsga`; `rnd` (vendor zero-filled) added inside xsga because Compustat xsga includes xrd; (d) ART at filing vs annual at
datadate + 6 months; (e) OSAP's null at / prcc_c / ni row drop is not reproduced; (f) SignalDoc EW quintiles not reproduced. Fields not in the map: none. `FactorDef`: ART default, no `history_months`, `family=None` until Phase C.
