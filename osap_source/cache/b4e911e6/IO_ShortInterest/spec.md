# IO_ShortInterest — Institutional ownership among high short interest stocks (Asquith, Pathak and Ritter 2005, Table 5)

OSAP ref b4e911e69678a7424f318617a61d813f54183123 (cache b4e911e6); source `Predictors/IO_ShortInterest.py` (cached
`predictor.py`, `signaldoc_row.csv`, `upstream_CompustatShortInterest.py`, `upstream_InstitutionalHoldings13F.py`,
the last two copied from the ShortInterest/ and RIO_Turnover/ caches). DATA_SHA 198b281de1a0. SignalDoc row
(Cat.Signal == Predictor): Cat.Data = 13F, Cat.Economic = ownership, Predictability 2_likely, Quality 1_good.

## 1. Data availability (verdict: DATA_UNAVAILABLE -> recommend `infeasible`)

| input (OSAP) | field_map key | Sharadar | status | note |
|---|---|---|---|---|
| `shortint` (monthlyShortInterest; Compustat `sec_shortint_legacy` 1973-2024 + `sec_shortint` 2006+) | none | NONE | unavailable | no short-interest column in any of the 13 held tables |
| `instown_perc` (TR_13F; Thomson Reuters s34 via `tr_13f.csv`, % of shares held by 13F institutions) | none | SF3A `shrunits` / shares outstanding (derived) | approx, 2013-06 start | no percent-of-float column; 13F only from 2013-06 |
| `shrout` (monthlyCRSP) | `crsp.shrout` | SF1.sharesbas / DAILY.marketcap/close | approx | split-restated |
| `gvkey` link (SignalMasterTable) | none | none | n/a | |
| `exchcd` (SignalDoc "Keep NYSE Only", NOT in the code) | `crsp.exchcd` | TICKERS.exchange (CURRENT) | approx | |

- **Short interest does not exist on the snapshot.** Checked: column names of SF1, SEP, DAILY, ACTIONS, METRICS,
  SP500, SF2, SF3, SF3A, SF3B, TICKERS, EVENTS and the DESCRIPTIONS indicator rows contain no short-interest,
  short-volume or days-to-cover item (EVENTS `eventcodes` are corporate events). Nothing can stand in for it.
- **Institutional ownership data.** Sharadar holds 13F data as SF3 (81,210,476 detail rows: ticker, investorid,
  securitytype, date, value, units), SF3A (670,115 security summaries: `shrunits`, `shrvalue`, `shrholders`,
  `totalvalue`, `percentoftotal`; 31,201 tickers) and SF3B (306,512 investor summaries). Measured on this
  snapshot: SF3A dates run 2013-06-30..2026-06-30, 53 quarter-ends. So `instown_perc` exists (as `shrunits` over
  shares outstanding) only from 2013-06: at most 102 of the 276 signal months (2013-06..2021-11), i.e.
  ~37% of the window (fewer after the 13F 45-day filing lag), and OSAP's own sample is 1980-2002 (SignalDoc).
- **The zero-fill rule does not rescue it.** OSAP does `fillna(0)` on `tempshortratio` and on `instown_perc`, but
  `shortint` is the SAMPLE FILTER, not an additive term: a row is kept only if `shortint/shrout >= the month's 99th
  percentile` of the raw ratio. With no short-interest field the 99th percentile is NaN and the code sets
  `temp = NaN` for every row (`temps99.isna()`). A missing filter is not a zero-fillable optional term: the signal
  would be empty, not neutral. The OSAP zero-fill serves only to exclude firms without short data.
- Recommendation: **infeasible** (data_unavailable; short interest absent; institutional ownership from 2013-06 only).

## 2. Variables (exact source names)

`permno`, `gvkey`, `time_avail_m` (SignalMasterTable); `instown_perc` (TR_13F); `shrout` (monthlyCRSP); `shortint`
(monthlyShortInterest). Intermediates `tempshortratio`, `temps99`, `temp`.

## 3. Formula

```
tempshortratio = shortint / shrout ; .fillna(0)
temps99  = groupby(time_avail_m).apply((shortint/shrout).quantile(0.99))     # on the raw ratio, NaN excluded
temp     = instown_perc.fillna(0)
temp     = NaN where tempshortratio < temps99 or temps99 is NaN
IO_ShortInterest = temp
```
Institutional ownership of the firms in the top 1% of short interest each month; everything else NaN. Rows with
a missing `gvkey` keep no `shortint` (ratio 0, below temps99, NaN).

## 4. Timing / lag

No lag in the code: `time_avail_m` of the short-interest month and of the 13F report quarter (`rdate`, forward-filled
to months by `tsfill`) are merged in place. A faithful build would need filing-date availability for 13F (due 45 days
after quarter end), which SF3A does not stamp as a filing date. No SF1 item: ART/TTM not in play.

## 5. Filters

Code: none beyond the 99th-percentile short-interest screen. SignalDoc Filter `exchcd==1` ("Keep NYSE Only") is
documented but not implemented; Quantile Filter `5 EW 99th`.

## 6. Predicted sign

SignalDoc `Sign = +1.0`: Asquith-Pathak-Ritter Table 5, "strong port sort but no long-short" (no published LS
return), portfolio-period 4-factor alpha difference, return 0.98, EW, LS Quantile 0.33.

## 7. The mass-point question

Not measurable: the signal cannot be built. Structural facts from the harness universe and the code:
- A firm not in the top 1% is NaN; the scored set is about 1% of names. The harness universe averages 1,965 names
  per month (1,739-2,867 over 276 months); 1% is about 20 names, ~2 per decile against the `>= 30 names per
  decile` bar and far under the 40% coverage bar, even if short interest existed. OSAP's percentile runs over all
  SignalMasterTable rows with short data (~4,000-5,000 names), so its scored set is ~40-50 names before intersecting
  with the universe.
- Within the scored set `instown_perc` is continuous with a mass at 0 (`fillna(0)` for firms without a 13F record,
  plausibly common among the small, heavily shorted names); not measurable here.

## 8. History needed

OSAP sample 1980-2002. Snapshot: SEP 1997-12, SF1 1997Q4, SF3A 2013-06-30 (53 quarter-ends to 2026-06-30). Even with
short interest, 1998-12..2013-05 (174 of 276 signal months) has no institutional ownership.

## 9. OSAP metadata

Acronym IO_ShortInterest (Acronym2 InstOwnSI), Asquith, Pathak and Ritter 2005, Journal of Financial Economics,
"Inst own among high short interest". Cat.Form continuous, Cat.Data 13F, Cat.Economic ownership, SampleStartYear
1980-2002, Portfolio Period 1, Start Month 12, Evidence "strong port sort but no long-short", Test "port sort 4-factor
alpha difference", GScholar cites 1302. Predictor output column `IO_ShortInterest`.

## 10. Proposed Sharadar mappings

None. `shortint`: no Sharadar field (data_unavailable). `instown_perc`: SF3A.shrunits / shares outstanding from
2013-06 only (approx, not needed). No field beyond the field map's existing entries is proposed; Sharadar SF3/SF3A/SF3B
are not keyed in `field_map_index.yaml` (no 13F field has been verified for this snapshot).
