# ShortInterest — spec (fetched fresh; pinned OSAP ref b4e911e6; checked on DATA_SHA 198b281de1a0, 2026-09-30)

## 1. Data availability and verdict
VERDICT: **data_unavailable -> infeasible**. The predictor is shortint / shrout; shares short is in no held Sharadar table.
- Checked all 13 held tables in data/SNAPSHOT_MANIFEST.yaml column lists: ACTIONS, DAILY, DESCRIPTIONS, EVENTS, METRICS,
  SEP, SF1 (112 columns), SF2, SF3, SF3A, SF3B, SP500, TICKERS. No column or DESCRIPTIONS entry for short interest, shares
  short, days to cover, borrow or lending (regex short|sho|borrow|lend|si_|interest; the only hits were
  `calendardate` and SF2 `transactioncode`). METRICS carries price, beta, moving averages and volume averages only.
  SF2 is insider Form 4 (2008+), SF3* 13F holdings (2013-06+): neither proxies shares short.
- Not in field_map_index / field_map (no shortint key). Flag: `compustat.shortint` absent from the map.
- OSAP zero-fill / fillna: NONE. Predictor builds df from an inner merge (`how="inner", validate="1:1"`) on
  monthlyShortInterest (gvkey, time_avail_m), so a firm without short interest is dropped, not zero-filled. The upstream
  CompustatShortInterest.py does a first-non-missing collapse only. The missing item is the signal itself, not an optional
  term, so there is no approx route. A volume- or ownership-based stand-in would be a different predictor.
- Data start in OSAP itself: comp.sec_shortint_legacy (1973-2024) and comp.sec_shortint (2006+).

## 2. Variables
SignalMasterTable: permno, gvkey, time_avail_m (gvkey required non-null). monthlyCRSP: shrout.
monthlyShortInterest: gvkey, time_avail_m, shortint (Compustat, /1e6 so millions; shrout in thousands -> ratio scale note).

## 3. Formula
ShortInterest = shortint / shrout. Mid-month observation of the bi-weekly short-interest file (four-day reporting lag),
first non-missing observation of the calendar month (gcollapse firstnm), legacy file preferred on overlap.

## 4. Timing
Mid-month short interest, reported with a 4-day lag, labelled month t and used as month t's signal under OSAP's
standard monthly signal lag. Stock (balance) measure, not a flow; nothing to smear.

## 5. Filters
SignalDoc Filter: blank. LS Quantile 0.2 (quintile sort), Portfolio Period 1.0 (monthly), Start Month 6.0.
Requires a valid gvkey in SignalMasterTable (CCM link) - Sharadar has no gvkey; moot given the data gap.

## 6. Predicted sign
SignalDoc Sign = -1 (high short interest = low return). Dechow et al. 2001, JFE,
Table 1A overall average; 35 bps spread in the port sort (pooled, not calendar time); Predictability 2_likely; Rep Quality
2_fair; Cat.Economic short sale constraints; Cat.Data Trading; Cat.Form continuous; sample 1976-1993.

## 7. Mass-point question
In OSAP a firm with no shares short reports shortint = 0 -> ShortInterest = 0 exactly; a real share of names sits at or
near zero in the Compustat file, but this is NOT measurable on the snapshot (no short-interest data). Not applicable;
no scoring possible. Tie handling: n/a.

## 8. History needed
n/a (no data). For reference OSAP's coverage starts 1973 (legacy) and needs only the current month.

## 9. OSAP metadata
Acronym ShortInterest; Predictor; Cat.Signal Predictor; Authors Dechow et al.; Year 2001; Journal JFE; Sample 1976-1993;
Return 0.35; T-Stat blank; Stock Weight EW; LS Quantile 0.2; Portfolio Period 1.0; Start Month 6.0; GScholar cites 1117.
Upstream cached: upstream_CompustatShortInterest.py (WRDS comp.sec_shortint_legacy / comp.sec_shortint).

## 10. Proposed Sharadar mappings
None. shortint has no Sharadar counterpart; shrout would map to SF1.sharesbas (approx) but there is no numerator. Recommend
a frontier row with reason "short interest is in no held Sharadar table (13 checked); OSAP does not zero-fill it".
