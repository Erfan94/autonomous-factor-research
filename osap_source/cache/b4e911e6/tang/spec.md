# tang — Asset tangibility (Hahn and Lee 2009, Table 4A constrained; Almeida-Campello formula; Acronym2 Tangibility)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/tang.py` (cached `predictor.py`; upstream `CompustatAnnual.py` beside it). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`. Measurements: harness universe, 6 probe decision months 1998-12 .. 2021-11 (of 276), recorded snapshot, scratch script (no factor file).

## 1. Data availability verdict: PREFLIGHT_FAILED (coverage) as primary; DATA_UNAVAILABLE (`ppegt`) as second independent blocker; recommend infeasible
NOTE: the pinned `predictor.py` reads `ppegt` (GROSS property, plant and equipment), NOT `ppent`; SignalDoc's prose says "ppent". The code is the authority.
| OSAP input | Sharadar | OSAP zero-fill? | status |
|---|---|---|---|
| `che` | `cashneq + investmentsc.fillna(0)` | YES (`zero_fill_vars`) | `compustat.che` APPROX: investmentsc overshoots into current financing/loan receivables for captive-finance names |
| `rect` | `receivables` | YES | mapped; vendor zero 17.8% matches the OSAP fill |
| `invt` | `inventory` | YES | mapped; vendor zero 45.6% matches the OSAP fill |
| `ppegt` | none | NO (not in `zero_fill_vars`) | `compustat.ppegt` UNAVAILABLE. OSAP drops the firm (`dropna(subset=["tang"])`), so no fill; missing-item rule: infeasible |
| `at` | `assets` | no | mapped; null 0.05%, exact-zero 0.01% (guard assets > 0) |
| `sic` (comp.names header, current) | `TICKERS.siccode` | no | mapped, CURRENT code (same as OSAP's header SIC in kind) |
No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob. The only route to a PP&E term is `ppnenet` (= `ppent`, NET PPE), a substitution: gross - accumulated depreciation, on the 0.535 weight, in manufacturers where net/gross is well below 1. Not adopted (no near-match substitution).

## 2. Variables
`m_aCompustat` (annual, carried monthly): che, rect, invt, ppegt, at, sic.

## 3. Formula
```
keep 2000 <= sic <= 3999                                     # manufacturing only
tang = (che + 0.715*rect + 0.547*invt + 0.535*ppegt) / at
tempFC (at size deciles per month) and FC are COMPUTED BUT NEVER USED
drop tang missing
```
Discrepancy to state: SignalDoc says "Exclude the lowest tercile of manufacturing firms by total assets" (Table 4 constrained sample); `tang.py` builds `tempFC`/`FC` from `at` deciles and NEVER applies them, so the emitted predictor is every manufacturing firm with a non-missing tang.

## 4. Timing
Annual Compustat, m_aCompustat availability (OSAP's m_aCompustat availability lag, nominally 6 months after datadate); on Sharadar ART at the filing date (`datekey`), as-of the signal month, so the signal is available ~1-3 months after the year end rather than after a fixed 6-month lag, and it refreshes with every 10-Q (ART), i.e. a quarterly-cadence version of an annual signal. Levels, no flow items; no ARQ smear question, but ART (default) vs ARY is a declared cadence deviation (ART==ARY on 99.9% of rows).

## 5. Filters
SIC 2000-3999 (part of the signal). SignalDoc `Filter` blank; Quantile Filter blank.

## 6. Predicted sign
SignalDoc Sign = +1 (high tangibility earns more); T-Stat 3.37, univariate reg (FMB), Key Table 4A Constrained; EW; Portfolio Period 1; Start Month 6. `ascending=True`.

## 7. Mass-point question (measured with a ppnenet PROXY, illustration only)
A do-nothing firm: a manufacturer with che = rect = invt = ppe = 0 produces tang = 0; essentially none. Proxy (ppnenet for ppegt) modal share of the scored cross-section 0.12-0.16% (6 probes), continuous, no mass point; exact-zero ppnenet among manufacturers 0.0% (1998-2008), 0.16% (2013), 0.44% (2018), 0.46% (2021-11) (Sharadar zero-fills ppnenet; OSAP would drop those names, a minor deviation). Tie handling: none needed.

## 8. History needed
Annual data from 1998; first scorable month 1998-12 (proxy scored 822 of 2,281). No return window, no SEP stub issue.

## 9. The decisive coverage measurement (proxy ppnenet build, SIC screen)
Manufacturers (SIC 2000-3999, `TICKERS.siccode`, current) as a share of the harness universe, 6 probes:
| signal | universe | manufacturers | share | scored (proxy) |
|---|---|---|---|---|
| 1998-12 | 2,281 | 831 | 36.4% | 822 |
| 2003-12 | 2,005 | 772 | 38.5% | 769 |
| 2008-12 | 1,794 | 657 | 36.6% | 655 |
| 2013-12 | 1,813 | 637 | 35.1% | 637 |
| 2018-12 | 1,877 | 686 | 36.5% | 686 |
| 2021-11 | 2,312 | 868 | 37.5% | 868 |
Coverage as preflight counts it (scored / universe) is 35.1-38.5% in every probe, below the 40% Stage 1 floor before the `ppegt` gap is even considered. Names per decile 64-87, above the 30 bar. The faithful signal (ppegt) is additionally unbuildable.

## 10. OSAP metadata
Hahn and Lee (2009), JF; Cat.Data Accounting; Cat.Economic asset composition; continuous; sample 1973-2001; Acronym2 Tangibility; Key Table 4A Constrained; Test univariate reg; Predictability 1_clear / Rep Quality 1_good; 243 cites. Notes: paper "painful to read"; tangibility formula of Almeida and Campello; Table 4 finds predictive power only in constrained firms (FM reg); OSAP follows Table 4.

## 11. Proposed Sharadar mappings
None recommended (`ppegt` has no SF1 field; `ppnenet` is a net-vs-gross substitution). If the coordinator ruled the substitution admissible: `che = cashneq + investmentsc.fillna(0)`, `rect = receivables`, `invt = inventory`, `ppe = ppnenet`, `at = assets` (ART, assets > 0), SIC via `TICKERS.siccode` (current), tang = (che + 0.715 rect + 0.547 invt + 0.535 ppe)/at, `ascending=True`; it would still fail the 40% coverage floor (35.1-38.5%). Verdict: infeasible (preflight_failed coverage; data_unavailable ppegt).
