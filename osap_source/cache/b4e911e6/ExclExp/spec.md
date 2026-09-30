# ExclExp — excluded expenses (Doyle, Lundholm and Soliman 2003, Table 5 total exclusions)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/ExclExp.py` (cached `predictor.py`).
DATA_SHA 198b281de1a0.

## 1. Data availability (verdict: DATA_UNAVAILABLE -> infeasible)

| OSAP input | source | Sharadar | status / OSAP missing rule |
|---|---|---|---|
| `int0a` (IBES unadjusted actual EPS, the "street" number) | `IBES_UnadjustedActuals.parquet` via `tickerIBES` (IBES-CRSP link in SignalMasterTable) | NONE: IBES / analyst data is not in Sharadar (ruling) | unavailable; left merge gives NaN and `dropna` removes the row, NOT zero-filled |
| `tickerIBES` link | `SignalMasterTable` (IBESCRSPLinkingTable) | none | unavailable |
| `epspiq` (quarterly EPS excl. extraordinary items) | `m_QCompustat` | SF1 `eps` at `dimension=ARQ` (`compustat.epspiq`, mapped) | mapped, available |

- The signal is `int0a - epspiq`: the excluded items are exactly the gap between the analyst-defined actual and the
  GAAP number. Without `int0a` there is nothing to difference; `epspiq` alone is a GAAP EPS level, a different factor.
  OSAP does not zero-fill `int0a` (missing -> dropped), so the missing-item rule gives `infeasible`.
- No substitute is proposed: no SF1 field carries a non-GAAP/street EPS (SF1 `eps`, `epsdil` are GAAP, `netinc` is
  GAAP), `EVENTS` holds 8-K item codes only, SF3* are institutional holdings. Nothing to measure: the input does
  not exist on the snapshot, so there is no coverage or mass-point number.

## 2. Variables (exact source names)

`int0a` (IBES unadjusted actual, latest, per tickerIBES-month), `epspiq` (Compustat quarterly EPS, basic, excluding
extraordinary items), `permno, gvkey, tickerIBES, time_avail_m`.

## 3. Formula

```
ExclExp = int0a - epspiq                                   (merge inner on gvkey,time_avail_m with m_QCompustat; left on IBES)
ExclExp = clip(ExclExp, quantile 1%, quantile 99%)         (whole-panel quantiles, pooled across all months)
```
Rows with NaN ExclExp dropped. Note the winsorisation is over the pooled panel (not month by month), a forward
look that the harness would replace with cross-sectional ranks.

## 4. Timing / lag convention

The quarterly Compustat EPS and the IBES actual are aligned on `time_avail_m` in OSAP (upstream `m_QCompustat` lag not
traced here; moot for an infeasible input). Not buildable here; flow item `eps` would be read at `dimension=ARQ`
(per-quarter level, as a single quarter's EPS, not a TTM sum) so no smear.

## 5. Filters

SignalDoc `Filter` is empty; inner merge with quarterly Compustat (gvkey non-null) and IBES availability: the
effective sample is IBES-covered firms only (1988+ at best).

## 6. Predicted sign

SignalDoc `Sign = -1.0` (higher excluded expenses, lower future returns). `Stock Weight EW`, `Cat.Form continuous`,
`Cat.Data Analyst`, `Cat.Economic composite accounting`.

## 7. The mass-point question

Not measurable (no input). For reference only, in OSAP `int0a - epspiq` is exactly 0 for firms whose street and GAAP
EPS agree (common); that zero block would itself be a material mass point, but the question is moot here.

## 8. History needed

Not applicable. IBES actuals would be needed from 1988 (sample 1988-1999).

## 9. OSAP metadata

`Cat.Signal Predictor`, `Cat.Form continuous`, `Cat.Data Analyst`, `Cat.Economic composite accounting`, Doyle,
Lundholm and Soliman 2003 (RAS), sample 1988-1999, `Predictability 1_clear`, `Rep Quality 1_good`, t = 6.78 (hand
collected Table 5 regression, "mv reg"), `Sign -1`, `Portfolio Period 12`, `Start Month 6`.

## 10. Proposed Sharadar mappings and deviations

None: `int0a` has no Sharadar counterpart. `epspiq` -> SF1 `eps` ARQ (mapped) would be the only available term.
Field not in the map index: `int0a` / IBES actuals (unavailable by ruling, no `field_map` key).
Recommendation: frontier as `data_unavailable` (IBES analyst actuals not in Sharadar; not zero-filled by OSAP).
