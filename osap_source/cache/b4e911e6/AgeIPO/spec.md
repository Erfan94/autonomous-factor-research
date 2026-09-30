# AgeIPO — Firm age at IPO (Ritter 1991, Table 9A)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/AgeIPO.py` (cached
`predictor.py`, `signaldoc_row.csv`, `upstream_IPODates.py`). DATA_SHA 198b281de1a0. field_map
statuses are mappings, not proofs, until the field-checker verifies them on this snapshot.

## 1. Data availability (verdict: INFEASIBLE — founding year has no Sharadar source)

| input (OSAP) | field_map key | Sharadar | field_map status | note |
|---|---|---|---|---|
| `FoundingYear` (Ritter `IPO-age.xlsx`, external) | none (no key exists) | none: TICKERS columns are table, permaticker, ticker, name, exchange, isdelisted, category, cusips, siccode, sicsector, sicindustry, figi, famaindustry, sector, industry, scalemarketcap, scalerevenue, relatedtickers, currency, location, lastupdated, firstadded, firstpricedate, lastpricedate, firstquarter, lastquarter, secfilings, companysite (api_schema/shar_tickers.sql); none carries a founding year | unavailable | THE SIGNAL VALUE. Not a Compustat item, so no OSAP zero-fill applies |
| `IPOdate` (Ritter `offer date`, month-truncated) | `crsp.firstpricedate` | TICKERS.firstpricedate | mapped | only a proxy for the filter term: Sharadar floors at 1997-12-31 (26% of tickers censored), so IPO dates exist only from 1998-01 |
| `permno` linkage of Ritter rows (`CRSP Perm`) | none | none | unavailable | Ritter's file keys on CRSP PERMNO; Sharadar has permaticker only, no PERMNO crosswalk |
| `permno`/`time_avail_m` (SignalMasterTable row presence) | `crsp.smt_row` | SEP price presence | mapped | firm-month gate only |

- No other inputs: the predictor uses no Compustat, IBES, options, 13F, patent or segment item.
  There is no `fillna(0)` and no zero-fill term in `AgeIPO.py` or upstream `IPODates.py`, so the
  rule ("infeasible unless OSAP zero-fills it") makes the missing founding year infeasible.
- **Recommendation: `infeasible`** (class `data_unavailable`). Reason: the signal value (company
  founding year) and the PERMNO-keyed IPO event list are an external hand-collected dataset
  (Jay Ritter, University of Florida) with no Sharadar counterpart.
- The only buildable stand-in is `year(t) - year(firstpricedate)` (0..3 by construction of the
  3-36 month window). That is a different signal (years since listing, i.e. IPO recency), not
  firm age at IPO; do NOT substitute it under the name AgeIPO.

## 2. Variables (exact source names)

`permno`, `time_avail_m` (SignalMasterTable); `IPOdate` (month-start of Ritter offer date),
`FoundingYear` (Ritter; negative values set to missing) from `IPODates.parquet`.

## 3. Formula

```
months_since_ipo = (time_avail_m - IPOdate).days / 30.44
tempipo = 3 <= months_since_ipo <= 36          # NaN if IPOdate missing
AgeIPO  = year(time_avail_m) - FoundingYear    # NaN unless tempipo == 1
tempTotal = sum over the month of tempipo      # count of IPO firms in window that month
AgeIPO  = NaN if tempTotal < 100               # "20*5"
```
Raw integer age in years; larger = older firm at/after IPO. No log, no winsorising, no scaling.
`IPODates.py` keeps the first row per permno, drops permno in {NaN, 999, <= 0}.

## 4. Timing / lag

`IPOdate` is the offer month; the 3-month lower bound is the only lag. The age uses the calendar
year of `time_avail_m`, so AgeIPO steps up by 1 each January for every firm. No Compustat
item, so no ART-as-of-filing or TTM smearing issue. Ritter's file is ex-post (assembled
later; founding years revised), so it is not point-in-time.

## 5. Filters

Only firms 3-36 months post-IPO are scored; `tempTotal >= 100` per month (whole-CRSP count).
The SignalDoc note says to exclude `IndIPO == 0`; `AgeIPO.py` does not implement that line.

## 6. Predicted sign

SignalDoc `Sign = 1.0` (higher AgeIPO, older IPO firm, higher return); LS quantile 0.2, EW,
portfolio period 1, start month 6; sample 1975-1987; evidence "event study, no t-stat";
`Cat.Economic = other`, `Cat.Form = continuous`, `Cat.Data = Event`.

## 7. Mass-point question

- A do-nothing firm (no IPO in the last 3-36 months, or no Ritter row) gets NaN: all of the
  universe outside the IPO window. Estimated from the filter alone, that is roughly 90-95% of
  firm-months (about 33 months of IPO cohorts against a mature universe); this is an estimate, not
  measured, because the Ritter file is not held.
- Scored values are integer years with heavy ties (founding years of young firms cluster at 0-15
  years); ties would need average-rank handling. Even a stand-in would sit far under the 40%
  coverage floor and the 30-names-per-decile floor would bind in thin IPO years (and OSAP's own
  `tempTotal >= 100` gate zeroes out quiet IPO years, e.g. 2001-2003, 2008-2009).

## 8. History needed

OSAP sample 1975-1987; IPO events required from 1972 for a 1975 start. The snapshot starts 1998-01
and TICKERS.firstpricedate is floored at 1997-12-31, so even a stand-in gains IPOs only from 1998-01
and the first scoreable month would be 1998-04. Founding years exist only in the external file.

## 9. OSAP metadata

Acronym AgeIPO; Cat.Signal Predictor; Predictability in OP 2_likely; Signal Rep Quality 2_fair;
Ritter (1991) JF; Table 9A event study, 3 years; SampleStartYear 1975, EndYear 1987; Detailed
definition: "Age is (current year - founding year from Jay Ritter's dataset). Exclude if IndIPO == 0."
Siblings sharing the same upstream IPODates file: IndIPO, RDIPO.

## 10. Proposed Sharadar mappings / deviations

None proposed. No field maps to FoundingYear; `crsp.firstpricedate` gives IPO recency only
(different variable). Not in field_map and needing a new key if anyone ever supplies the file:
`ritter.FoundingYear`, `ritter.IPOdate`, PERMNO-to-permaticker crosswalk. The same blocker
applies to IndIPO and RDIPO (shared `IPODates.parquet` input).
