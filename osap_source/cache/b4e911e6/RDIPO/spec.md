# RDIPO — IPO and no R&D spending (Gou, Lev and Shi 2006 JBFA, Table 8 row 2)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Signals/pyCode/Predictors/RDIPO.py` (cached `predictor.py`,
`upstream_CompustatAnnual.py`, `upstream_IPODates.py`). DATA_SHA 198b281de1a0.

## 1. Data availability — VERDICT: preflight_failed (binary flag, structural mass point); data is approx stand-in only

| input (OSAP) | field_map key | Sharadar | status |
|---|---|---|---|
| `xrd` (annual R&D, raw) | `compustat.xrd` | SF1 `rnd`, ARY | mapped (verified 2026-09-30); vendor zero-filled: null 0.06%, `rnd == 0` 63.5% of non-null ARY rows |
| `IPOdate` (Ritter `IPO-age.xlsx` offer date, month-truncated, keyed by CRSP permno) | none for Ritter | stand-in `TICKERS.firstpricedate` (`crsp.firstpricedate`, mapped) | approx: first SEP price date, floored at 1997-12-31; NOT an IPO offer date |
| `permno`/`time_avail_m` rows (`m_aCompustat`) | `compustat.datadate` | SF1 row present | mapped |

- Missing-item rule: OSAP sets `tempipo = 0` where `IPOdate` is missing and tests `xrd == 0` on RAW `xrd` (not zero-filled; `xrd` is not in `zero_fill_vars`), so a missing `xrd`
  gives RDIPO = 0. The Ritter file is unavailable, so every name would be 0 without a stand-in; `firstpricedate` is a different, broader, left-censored event list (caveats
  identical to `IndIPO/spec.md` section 1 and the IndIPO frontier row: 1997-12-31 floor, spin-offs, SPAC shells, uplistings; inherited by reference, not re-measured).
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt input.

## 2. Variables (exact source names)
`permno, time_avail_m, xrd` (`m_aCompustat`), `IPOdate` (`IPODates.parquet`).

## 3. Formula
```
months_since_ipo = (year(t)-year(IPOdate))*12 + (month(t)-month(IPOdate))
tempipo = 1 if 6 < months_since_ipo <= 36 else 0 ; tempipo = 0 if IPOdate missing
RDIPO   = 1 if tempipo == 1 and xrd == 0 else 0
```
Binary 0/1 integer on every `m_aCompustat` row (never NaN where the row exists). Window is 7..36 months after the IPO month (the IndIPO window is 3..36).

## 4. Timing / lag
IPO date is known when it happens; `xrd` is the annual record at `datadate + 6 months` held 12 months. SF1 ARY is as-of-filing (2-3 months fresher). `xrd` is a fiscal-year flow:
`dimension="ARY"` (an ART/TTM value moves the zero test only marginally; measured ART variant ones: mean 86.7 vs 94.6 for ARY). No smear issue for the flag itself.

## 5. Filters
None in the code. SignalDoc Filter blank. Only `xrd == 0` and the IPO window qualify a name.

## 6. Predicted sign (SignalDoc)
`Sign = -1.0` (`ascending=False`: IPO-with-no-R&D firms earn LOW returns). Cat.Economic `R&D`, Cat.Form `discrete`, Cat.Data `Event`; Sample 1980-1995; T-stat 2.68 (port sort FF3+Mom alpha); Return 0.76; EW; Portfolio Period 1; Start Month 6.

## 7. The mass-point question (THE decisive item)
A do-nothing firm (no IPO in the window, or no date, or `xrd != 0`) produces exactly 0 and is the modal value. Measured on THIS snapshot, all 276 decision months (1998-12-31..2021-11-30),
harness universe (mean 1,965 names, 1,739-2,867), stand-in = `firstpricedate` month in (t-36, t-6] and `firstpricedate > 1997-12-31`, AND latest ARY `rnd == 0`:
- Distinct values: 2 (0 and 1) every month. Ones per month: min 37, mean 94.6, max 176 (1.6%-7.5% of the universe, mean 4.8%). Modal 0 share: min 92.5%, max 98.4% (mean 95.2%); >= 90% in 276 of 276 months; >= 10% cliff in 276 of 276.
- Probe months: 1998-12-31 modal 98.38% (37 ones of 2,281); 2010-06-30 96.25% (67 of 1,789); 2021-11-30 95.54% (103 of 2,312). `masspoint_stats`: qcut yields 1 bin (a 0/1 flag) at every month.
- IPO window names (stand-in, post-floor) are 8.9% of the universe on average (61-447 per month); 52.9% of them have `rnd == 0` (pooled); `rnd` null 6.45 per month. SF1 coverage of the universe 98.4% mean.
- Left censoring: floor-dated names (`firstpricedate <= 1997-12-31`) in the 7-36 month window exist only for signals 1998-12..2000-12 (25 months; mean 84% of the universe over the first 24 months,
  2,157 of 2,281 at 1998-12) and are EXCLUDED above, so those 25 months under-count ones; from 2001-01 the window is fully observed (ones: min 42, mean 92.9, max 172, all 251 months).
- A binary flag cannot fill ten deciles: no tie design (remove / null / floor) gives 10 bins. Verdict preflight_failed, same as IndIPO.
- Differences to OSAP's own flag: OSAP's ones need an explicit Compustat `xrd == 0`; SF1 zero-fills every non-reporter to 0, so the ones share here is larger than OSAP's (approx).

## 8. History needed
IPO events from 1995-12 onward for the 1998-12 signal; the stand-in holds IPOs only from 1998-01, so the first 25 months are censored (above). `m_aCompustat` rows: SF1 ARY from FY1992+.
Measured on DATA_SHA 198b281de1a0, 276 months, harness universe via `build_universe`; SF1 `rnd` as-of-filing ARY. All 276 months are scorable in count but every month collapses to one bin.

## 9. OSAP metadata
Acronym `RDIPO`; Gou, Lev and Shi, JBFA 2006; Key Table "8 row 2"; Test "port sort FF3+Mom alpha" (LS 4-factor alpha); Sign -1.0; Return 0.76; T 2.68; EW; Start Month 6; Portfolio Period 1;
GScholar cites 277. LongDescription "IPO and no R&D spending". Detailed Definition: binary, 1 if `xrd == 0` and IndIPO == 1, else 0 (code uses the 6 < m <= 36 window). Shares `IPODates.parquet` with IndIPO and AgeIPO.

## 10. Proposed Sharadar mappings and deviations
None to translate. If a file were ever supplied: `IPOdate -> TICKERS.firstpricedate` (month start, valid only after 1997-12-31, no Ritter filters), `xrd -> SF1.rnd` (ARY, `== 0` incl. vendor zeros), 7..36-month window,
binary 0/1; it fails the harness mass-point preflight in every month. Not in field_map and needed: `ritter.IPOdate`, a PERMNO-to-permaticker crosswalk. Recommend `preflight_failed`.
