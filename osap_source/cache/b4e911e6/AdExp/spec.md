# AdExp — spec (Phase A, fetch batch 01)

Ref b4e911e69678a7424f318617a61d813f54183123. Source: Signals/pyCode/Predictors/AdExp.py (cached predictor.py,
signaldoc_row.csv). Upstream data prep (m_aCompustat.parquet, SignalMasterTable) is not cached for this acronym;
traced via the sibling cache `Accruals/upstream_CompustatAnnual.py` and `upstream_SignalMasterTable.py`.

## 1. Data availability verdict: INFEASIBLE

- The numerator `xad` (Compustat annual advertising expense) has NO Sharadar field. `field_map_index.yaml`
  line 175: `compustat.xad` -> sharadar "" status `unavailable` ("no SF1 field; infeasible unless OSAP zero-fills it").
  `field_map.yaml` (xad entry): `sf1: null`, `status: unavailable`.
- The zero-fill escape does not apply. AdExp.py uses raw `xad` (NOT the `xad0 = xad.fillna(0)` variant that
  CompustatAnnual builds for other predictors); a missing `xad` gives a missing AdExp, and `xad <= 0` is set to
  missing. The signal is defined only on the few firms that report advertising, so there is no `approx`
  route: dropping xad leaves nothing, and no Sharadar item (e.g. sgna, opex) isolates advertising.
- Recommend `infeasible` (frontier reason: "xad advertising expense not published by Sharadar SF1").
- Denominator side is available (see 10), so the failure is solely xad. Not measured on the snapshot because
  the field_map records no SF1 column for xad; the field-checker may confirm by scanning SF1 column names
  for any advertising item (none expected), but no further work is needed for the verdict.

## 2. Variables (exact source names)

| source name | origin | field_map key |
|---|---|---|
| xad | Compustat annual (`funda.xad`) via m_aCompustat | `compustat.xad` (unavailable) |
| mve_permco | SignalMasterTable (CRSP me summed to permco) | `crsp.mve_permco` (approx -> DAILY.marketcap) |

(Conceptually the SignalDoc definition is `xad / (shrout*abs(prc))`; the code uses `mve_permco`, company level.)

## 3. Formula

AdExp = xad / mve_permco, set to NaN where xad <= 0 (`df.loc[df["xad"] <= 0, "AdExp"] = np.nan`).
Key lines: `df["AdExp"] = df["xad"] / df["mve_permco"]`. Right-join onto SignalMasterTable, so the panel is the CRSP
firm-month presence; firms without xad are NaN, not zero.

## 4. Timing / lag

- m_aCompustat (CompustatAnnual upstream): `time_avail_m = datadate month + 6`, each annual record replicated
  12 months (offsets 0..11), latest datadate kept per permno-month. So xad is held 6 to 17 months after fiscal year
  end. Stale by construction.
- mve_permco is the contemporaneous month-t market equity (SignalMasterTable), not lagged to the fiscal year end.
- ART-as-of-filing would shorten the lag to the actual filing date (typically 2-3 months after FYE) and the
  fixed 6-month lag would be replaced by the filing-based value; moot since xad is unavailable.
- Flow item: xad is an annual flow; TTM would be the natural ART analogue with no smearing issue (level, not a
  year-over-year difference). Moot.

## 5. Filters

None in the script beyond `xad > 0`. Portfolio design from SignalDoc: EW, LS quantile 0.2, portfolio period 12,
start month 6, no quantile filter.

## 6. Predicted sign

SignalDoc `Sign` = 1.0 (higher AdExp -> higher returns). Return 0.529 (bps-per-month style spread, t-stat blank),
Predictability in OP `2_likely`, quality `1_good`, Cat.Economic `R&D`, Cat.Form continuous, Cat.Data Accounting.
Paper: Chan, Lakonishok, Sougiannis (2001, JF), Table 7 first year, sample 1975-1996.

## 7. Mass-point question

A do-nothing firm (no advertising reported, or xad = 0) is NaN, not a value, so there is no mass point in the
scored set; ties are continuous. The large share of firms with no xad (majority of the universe, since only a
minority of Compustat industrials report advertising, and reporting is voluntary/biased to consumer firms)
means coverage would be low and sector-skewed (concentrated in consumer and retail sectors). That would raise
the coverage floor (>= 40%) and sector-rank min-names (10) issues, but this is academic given infeasibility.

## 8. History needed

None beyond the current fiscal year's annual record (value, no return window). Snapshot starts 1998-01 and
the predictor could be scored from there if it had data.

## 9. OSAP metadata

Acronym AdExp; Cat.Signal Predictor; Cat.Economic R&D; Authors Chan, Lakonishok and Sougiannis; Year 2001;
Journal JF; SampleStartYear 1975, SampleEndYear 1996; Sign 1.0; Stock Weight EW; LS Quantile 0.2;
Portfolio Period 12; Start Month 6; Key Table "7, first year"; Test "port sort no LS"; GScholarCites202509 2972.
Notes: "Most of the paper is about R&D, AdExp is kinda an afterthought." Detailed definition: advertising
expense (xad) over market value of equity (shrout*abs(prc)).

## 10. Proposed Sharadar mappings (for completeness; not to be translated)

| OSAP | Sharadar | field_map key | deviation |
|---|---|---|---|
| xad | none | `compustat.xad` | UNAVAILABLE; blocks the predictor |
| mve_permco | DAILY.marketcap (primary-class ticker, millions USD, company-level) | `crsp.mve_permco` (approx) | units: millions vs xad in millions in Compustat, consistent only if xad existed; marketcap at month end vs CRSP month-end me |
| me (alt. reading) | DAILY.marketcap | `crsp.me` (mapped) | |
| shrout*abs(prc) (SignalDoc wording) | DAILY.marketcap*1e6/SEP.close; SEP.closeunadj | `crsp.shrout`, `crsp.prc` | not used by code |

Fields not in the map: none. Only `compustat.xad` needs field-checker attention, and it is already recorded
as unavailable.
