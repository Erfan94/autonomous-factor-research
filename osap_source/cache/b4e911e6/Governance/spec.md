# Governance — Governance index (Gompers, Ishii and Metrick 2003, QJE, Table 7 (1); SignalDoc "Governance Index")

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Signals/pyCode/Predictors/Governance.py` (cached `predictor.py`, `upstream_GovernanceIndex.py`).
DATA_SHA 198b281de1a0. Written fresh from the source and `field_map_index.yaml`.

## 1. Data availability (verdict: DATA_UNAVAILABLE; recommend infeasible)
- The only input is the G-index `G` (count of 24 anti-takeover provisions, 1-24; OSAP clips to 5-14) from the authors' spreadsheet
  (`upstream_GovernanceIndex.py` downloads `Governance.xlsx`, sheet `governance index`, from the Yale/Metrick faculty site), merged onto SignalMasterTable by `ticker`.
  It is an external academic data set, not a CRSP/Compustat item. Sharadar publishes no governance index, provision count, or takeover-defence field.
- Checked on THIS snapshot (13 tables held): no column whose name or DESCRIPTIONS text contains governance / G-index / anti-takeover in SF1 (112 columns), TICKERS (28), SF2, SF3, SF3A, SF3B,
  METRICS, EVENTS (`ticker, date, eventcodes` only), ACTIONS, SP500, SEP, DAILY. No proxy in `field_map_index.yaml` (no governance key).
- OSAP does not zero-fill or default it: a name with no G matches nothing (`dropna(subset=["Governance"])`), so the missing-item rule gives no escape. Filling the signal
  with a constant would leave no cross-section.
- Independent of availability, the OSAP series cannot cover the decision window: surveys exist for 1990, 1993, 1995, 1998, 1999 (2000 recoded to 1999), 2002+ (assumed January), each
  name's last observation is forward-filled only to 2007-01 (`last_row["time_avail_m"] = 2007-01-01`), and there are no rows after that. Sample 1990-1999 in the SignalDoc, index "available
  every 2-3 years", so an implementation would at most score 1999-01..2007-01 of the 276 decision months, and only for the covered tickers (ticker merge; names without a ticker get no value).
- Not measured: no data exists to measure (nothing built, nothing to probe).

## 2. Variables (exact source names)
`G` (GovIndex.parquet: `ticker, time_avail_m, G`), `ticker`, `permno`, `exchcd`, `time_avail_m` (SignalMasterTable).

## 3. Formula
```
Governance = G;  Governance = 5 if G <= 5;  Governance = 14 if G >= 14   # clip to [5, 14]
drop if Governance missing
```
Levels 5..14 only (10 distinct integers, a discrete index, `Cat.Form` discrete).

## 4. Timing / lag convention
Publication month assigned by survey year: 1990 -> Sep, 1993 -> Jul, 1995 -> Jul, 1998 -> Feb, 1999 -> Nov, 2002+ -> Jan (of that year); held (forward-filled) to the next survey and to 2007-01.
No SF1 dimension is involved (no flow item).

## 5. Filters
None in the predictor (`exchcd` is selected but unused). SignalDoc `Filter` empty; Stock Weight VW; Portfolio Period 1; Start Month 12 in the SignalDoc row.

## 6. Predicted sign
SignalDoc `Sign = -1.0` (higher G = weaker shareholder rights = lower returns); `Cat.Form` discrete; `Cat.Data` Other; `Cat.Economic` other. Long LOW G; `ascending=False`.
SignalDoc Notes: the VW FF alpha t is 2.73 at Table 7 and the raw LS may not be significant; port sort "not very monotonic".

## 7. The mass-point question
Would be severe if it existed: a 10-level integer index clipped at both ends, where covered firms cluster in the middle of the range and the clipped ends (5 and 14) pool every tail firm; each level is a
tie block, plausibly near or above the 10% decile cliff (not measured), and a forward-filled firm does nothing for 2-3 years. Moot: no data.

## 8. History needed (snapshot starts 1998-01)
Not applicable (no data). Even with data the series ends 2007-01, leaving 1999-01..2007-01 (97 of 276 months) and none of 2007-02..2021-12.

## 9. OSAP metadata (SignalDoc)
Acronym Governance; Gompers, Ishii and Metrick; 2003; QJE; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form discrete; Cat.Data Other; Cat.Economic other;
Sample 1990-1999; Key Table 7 (1); Test in OP blank; Sign -1.0; Return 0.72; T-Stat 2.77; VW; Portfolio Period 1; Start Month 12. Definition: index from the Yale (Metrick) site, only available every 2-3 years
per firm, intermediate missing values replaced with the latest available, value-weighted.

## 10. Proposed Sharadar mappings
None. All inputs unmappable. Recommended `osap_frontier.yaml` reason: data_unavailable (external governance index, not in Sharadar; OSAP series ends 2007-01). Fields not in the map: `G` (no key, no Sharadar source).
