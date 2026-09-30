# IndIPO — IPO indicator, 3 to 36 months after the IPO (Ritter 1991, Table 2, month 12)

OSAP ref b4e911e69678a7424f318617a61d813f54183123. Source `Signals/pyCode/Predictors/IndIPO.py` (cached `predictor.py`,
`signaldoc_row.csv`, `upstream_IPODates.py`). DATA_SHA 198b281de1a0. field_map statuses are mappings, not proofs.

## 1. Data availability and verdict: PREFLIGHT_FAILED (structural mass point). Data: APPROX stand-in only.

| input (OSAP) | field_map key | Sharadar source | status | note |
|---|---|---|---|---|
| `IPOdate` (Ritter `offer date`, month-truncated, file `IPO-age.xlsx`) | none for Ritter; stand-in `crsp.firstpricedate` | `TICKERS.firstpricedate` (permaticker level, `ticker_meta()`) | mapped (as a proxy) | first SEP price date, NOT an IPO offer date |
| `permno` keying of Ritter rows (`CRSP Perm`) | none | none (Sharadar has permaticker only) | unavailable | no PERMNO crosswalk |
| `permno`/`time_avail_m` rows (SignalMasterTable) | `crsp.smt_row` | SEP presence | mapped | firm-month gate only |

- Missing-item rule: OSAP itself sets IndIPO = 0 when IPOdate is missing (`df.loc[IPOdate.isna(), "IndIPO"] = 0`), a zero-fill, so the
  rule does not make this infeasible; but without the Ritter file every name is 0 (a constant), so the only buildable construct is the
  firstpricedate stand-in, a different (broader, left-censored) event list. No IBES/options/13F/patent/segment/rating/pension/xad/emp/ob/ppegt input.
- Sharadar IPO-date source and point-in-time status: `TICKERS.firstpricedate`, which equals SEP's own per-ticker first date and
  the ACTIONS `action == "listed"` date on 13,125 of 13,125 matched IDs (difference 0 days); ACTIONS adds no independent information
  (it carries `listed` rows only for tickers first priced after 1997-12-31: 13,119 of 13,120 post-floor IDs). Point-in-time: a
  historical first-trade date, fully knowable at the time and only used >= 3 months later, so no look-ahead; but TICKERS has no
  per-row vintage (table `lastupdated` only), so a later vendor revision cannot be detected from one frozen snapshot.
- LEFT CENSORING: Sharadar floors `firstpricedate` at 1997-12-31 (the SEP start): 7,873 of 20,993 SEP-scope IDs (37.5%; 13,120 are
  first priced after the floor); a floor-censored name may be a true 1995-97 IPO still inside its 36-month window (signals through ~2000-12). Treating
  censored names as 0 misclassifies them; dropping them leaves ~16% of the universe scored in the first 24 months. Both fail.
- `firstpricedate` is not an IPO date: it also marks spin-offs (12.6% of flagged name-months carry a `spunofffrom` ACTION), SPAC shells
  (2.6% of flagged pooled, 97 of 373 at 2021-11), probable uplistings / Sharadar coverage additions (first-price-date counts of 848 in 2014 and
  1,845 in 2021 against 126-450 in ordinary years), and ticker-level additions; Ritter's published list conventions (from his data page, not
  from the OSAP files) exclude ADRs, units, closed-end funds, REITs, banks/S&Ls, offers under $5 and non-CRSP-listed issues.
- Consistency with AgeIPO (same `IPODates.parquet`): Ritter's file is unavailable there too; this stand-in fails structurally.
- Recommendation: `preflight_failed` (mass point), reason below; do not translate as IndIPO without the tie design the harness cannot give a binary.

## 2. Variables (exact source names)

`permno`, `time_avail_m` (SignalMasterTable); `IPOdate` (month start of the offer date) from `IPODates.parquet`.

## 3. Formula

```
months_since_ipo = (year(t) - year(IPOdate)) * 12 + (month(t) - month(IPOdate))
IndIPO = 1 if 3 <= months_since_ipo <= 36 else 0 ;  IndIPO = 0 where IPOdate is missing
```
Binary 0/1 integer, every SignalMasterTable row scored (never NaN). SignalDoc's Detailed Definition says "past 6-36 months" and Start
Month 12 / Notes say the 3-month minimum helps; the code uses 3. `IPODates.py` keeps the first row per permno, drops permno in {NaN, 999, <= 0}.

## 4. Timing / lag

The IPO month plus a 3-month minimum is the only lag; the signal uses only the IPO date (known at the time). No SF1 item, so no
`dimension`/ART/ARQ issue and nothing smears. Ritter's file is ex post (assembled later), the Sharadar stand-in is a first-trade date.

## 5. Filters

None in the predictor. SignalDoc Filter empty. Notes: "Tab II event study t-stat 5 at 1 year ... sample should end in 1987 ... using minimum
of 3 months since IPO helps".

## 6. Predicted sign (SignalDoc)

`Sign = -1.0`: stocks 3-36 months past their IPO earn LOW subsequent returns. `ascending=False`. Cat.Economic `external financing`, Cat.Data
`Event`, Cat.Form `discrete`; Stock Weight EW; LS Quantile blank; Portfolio Period 1, Start Month 12; Sample 1975-1987; T-Stat 3.97
(event study, 12-month firm match, Table 2 month 12); Predictability in OP 1_clear; Signal Rep Quality 2_fair.

## 7. The mass-point question (THE decisive item)

A do-nothing firm (no IPO in the past 3-36 months, or no date) produces exactly 0 and is the modal value. Measured on THIS snapshot,
all 276 decision months, harness universe, stand-in = `firstpricedate` in (t-36, t-3] months and > 1997-12-31:
- Zero share: mean 89.9% of the universe (min 78.8%, max 95.4%); ones share mean 10.1% (min 4.6%, max 21.2%); 2 distinct values.
- Probe months (first / middle / last of the schedule): 1998-12-31 modal 0 share 95.35% (106 ones of 2,281); 2010-06-30 93.40% (118 of
  1,789); 2021-11-30 83.87% (373 of 2,312). `masspoint_stats`: qcut yields 1 bin in all three. Every month's modal share exceeds the 10%
  cliff; 168 of 276 months exceed 90%. Ones per month: min 90, mean 204.7, max 548 (so the positive class is large enough; the failure is
  structural, not thinness).
- A binary indicator cannot fill ten deciles: no tie design (remove / null / floor) creates 10 bins; ranking collapses to D1 = D10 tie
  blocks. Tie handling is moot. Verdict `preflight_failed`, not `data_unavailable`.

## 8. History needed, measured coverage

- Needs IPO events from (first signal - 36 months). The stand-in holds IPOs only from 1998-01. Positive class under-observed for signals
  1998-12-31..2000-12 (the 3-36 month window reaches back before 1998-01; measured floor-censored share of the universe: mean 84.0% over
  the first 24 months, 38.4% at the last signal 2021-11-30). Complete only from the 2001-01 signal.
- Coverage: 100% if zero-filled (OSAP's rule), about 16% of the universe if censored names are NaN'd in the first 24 months.
- Spikes: SPAC listings lift the ones share to 16.1% at 2021-11-30 (97 SPAC-linked names of 373).
- Measured on THIS snapshot, DATA_SHA 198b281de1a0, 276 decision months (signals 1998-12-31..2021-11-30).

## 9. OSAP metadata

Acronym `IndIPO`; LongDescription "Initial Public Offerings"; Authors Ritter; Year 1991; Journal JF; Sample 1975-1987; Cat.Signal Predictor;
Sign -1.0; Return 0.8525; T-Stat 3.97; Key Table "2 month 12"; Test "event study 12 month firm match"; Stock Weight EW; Portfolio Period 1;
Start Month 12; GScholarCites 936. Detailed Definition: "1 if IPO in the past 6-36 months. 0 otherwise. IPO dates are taken from Jay
Ritter's IPO data ... Missing IPO dates imply IndIPO = 0". Siblings on the same file: AgeIPO, RDIPO.

## 10. Proposed Sharadar mappings and deviations

None to translate. If anyone insists on the stand-in: `IPOdate` -> `TICKERS.firstpricedate` (month start), valid only after 1997-12-31,
no Ritter filters, floor-censored names unknowable; it yields a binary signal that fails the harness mass-point preflight in every month.
Not in field_map and needed if a file is ever supplied: `ritter.IPOdate`, a PERMNO-to-permaticker crosswalk.
