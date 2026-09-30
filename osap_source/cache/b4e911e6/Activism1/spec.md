# Activism1 — spec (pinned ref b4e911e69678a7424f318617a61d813f54183123)

Source: `Signals/pyCode/Predictors/ZZ1_Activism1_Activism2.py` (the filename is the
`ZZ1_` joint script; the SignalDoc row with Acronym=Activism1, Cat.Signal=Predictor
is the authority). Cached: `predictor.py`, `signaldoc_row.csv`,
`upstream_GovernanceIndex.py`, `upstream_InstitutionalHoldings13F.py`.
Paper: Cremers and Nair (2005, JF), "Takeover vulnerability", Table 3A.

## 1. Data availability — VERDICT: INFEASIBLE

Two of the three substantive inputs do not exist on this snapshot, and their
date ranges do not overlap even if they did.

| input | OSAP source | field_map key | status | Sharadar on THIS snapshot |
|---|---|---|---|---|
| G (Gompers-Ishii-Metrick governance index) | external GIM Excel download (`GovernanceIndex.py`), NOT CRSP/Compustat | none | NOT IN MAP, unavailable | no governance/anti-takeover-provision table in the 13 held tables |
| maxinstown_perc (largest 13F holder's ownership %) | Thomson Reuters 13F prep file `tr_13f.csv` (`InstitutionalHoldings13F.py`) | none | NOT IN MAP | SF3 / SF3A (institutional holdings) start 2013-06; 13F pre-2013 is unavailable |
| shrcls (dual share class flag) | CRSP monthly `shrcls` | none (closest: `crsp.shrcd` = TICKERS.category) | NOT IN MAP | TICKERS.category Primary vs Secondary Class is a company-level proxy only (approx) |
| ticker (join key to G) | SignalMasterTable `ticker` | `compustat.tic` -> SEP/TICKERS.ticker | mapped | fine, but the join target (G) is absent |
| exchcd | SignalMasterTable (selected, never used in the construction) | `crsp.exchcd` | approx | not needed |

Measured reason the signal cannot exist in the decision window (1999-01..2021-12):
- G is forward-filled only to 2007-01 by `GovernanceIndex.py` (each ticker's last
  observation is extended to 2007-01-01 and no further; survey dates 1990, 1993,
  1995, 1998-02, 1999-11, then 2002+ as January). Hence Activism1 is non-missing
  only for months <= 2007-01 even in OSAP itself.
- Sharadar holdings tables begin 2013-06 (SF3 / SF3A). The earliest month with a
  13F block-ownership value is therefore ~2013-06-2013-09, 6+ years AFTER G ends.
- Intersection of G availability and 13F availability = empty. Zero non-missing
  Activism1 firm-months on the snapshot regardless of how the missing data were
  synthesised. No proxy for G exists (no GIM/ISS/RiskMetrics table, no charter/bylaw
  provisions, no state-law indicators).
- Recommendation: `infeasible` (data Sharadar does not publish: governance index;
  13F pre-2013). Not `approx`: there is no zero-fill of a minor optional term; the
  two defining terms are both absent. No candidate file should be written.
  Frontier reason string: "GIM governance index (external, ends 2007-01) and 13F
  maxinstown_perc (Sharadar SF3 from 2013-06): no overlapping month; not in any
  Sharadar table."

The remaining sections document construction for the record.

## 2. Variables (exact source names)

- `G` (GovIndex.parquet, int8, ticker x month, 1..24 provisions; ffilled between
  survey dates, dup ticker-year rows dropped keeping first; survey year 2000 re-labelled 1999)
- `maxinstown_perc` (TR_13F.parquet: `MAX` over institutions of the percent of
  shares outstanding held by a single 13F filer; permno x month, ffilled between report dates within a firm's observed range)
- `shrcls` (monthlyCRSP), `ticker`, `permno`, `time_avail_m`, `exchcd` (SignalMasterTable)

## 3. Formula

```
tempBLOCK     = maxinstown_perc if maxinstown_perc > 5 else 0      # missing 13F -> 0, never NaN
tempBLOCKQuant= fastxtile(tempBLOCK, by=time_avail_m, n=4)         # cross-sectional quartile, Stata-style, over ALL SignalMasterTable firms that month
tempEXT       = NaN if G is NaN else 24 - G                        # 24-G : higher = fewer takeover defences
Activism1     = NaN if tempBLOCKQuant <= 3                         # keep top blockholder quartile only
              = NaN if shrcls != ""                                # dual-class excluded (NULL shrcls is kept)
              = tempEXT otherwise
```
In words: external-governance strength (absence of anti-takeover provisions) among
firms in the top quartile of largest-blockholder ownership, excluding dual-class
firms. Firms with no G (non-GIM firms, everything after 2007-01) are missing.
Quartile is formed before the G and shrcls restrictions, on all master-table firms
(not only G firms); tempBLOCK=0 for the large mass of firms with no >5% holder, so
"top quartile" is determined within a distribution with a big tie mass at 0.

## 4. Timing / lag

- `time_avail_m` is the month the value is assumed known. G availability months are
  hand-coded publication months (1990-09, 1993-07, 1995-07, 1998-02, 1999-11, 2002+ -> 01),
  i.e. lag is built into the survey calendar, not a generic 6-month rule.
- 13F `rdate` month is used directly as `time_avail_m` (no filing-delay lag, no
  45-day 13F deadline). Lookahead of up to ~1.5 months vs true filing date.
- SignalDoc `Start Month = 6`, Portfolio Period 1.
- No SF1 flow items, so the ART/ARQ smear and ART-as-of-filing do not apply.

## 5. Filters

Top quartile of tempBLOCK each month; shrcls blank (single class); G non-missing.
SignalDoc Filter column empty; Quantile Filter empty; LS Quantile 0.25; Stock Weight VW.

## 6. Predicted sign

SignalDoc `Sign = 1.0` (high 24-G = weaker anti-takeover provisions among blockheld
firms -> higher returns; published long-short return 0.9025 %/mo, t=3.13 in the
1990-2001 paper sample, Table 3A BLOCK=4). Cat.Economic = other, Cat.Data = 13F.

## 7. Mass-point question

- Signal is a small integer: 24-G with G in 1..24 -> about 20 distinct values in
  practice (G between ~5 and ~19 for most firms), so heavy ties even among scored
  names. A do-nothing firm keeps its G for years (ffilled between 3-7 year survey gaps)
  so the signal is almost constant over time within a firm.
- Non-missing share (OSAP): G covers ~1,500 firms; intersect with top blocks quartile
  and no dual class -> roughly 3-8 % of master-table firm-months in 1990-2006 and
  0 % afterwards. Decile formation would collapse (only ~20 values, few names per
  value); ties would need average-rank handling. On THIS snapshot the share is 0 %.

## 8. History needed

1990 onwards for G; 13F from 1980. Snapshot begins 1998-01 (SEP 1997-12-31; SF3 from
2013-06), so even the G-side history would be only ~9 years and the 13F side would
not overlap.

## 9. OSAP metadata

Cat.Signal Predictor; Predictability in OP 1_clear; Rep Quality 1_good; Cremers and
Nair 2005 JF; sample 1990-2001; Cat.Form continuous; Cat.Data 13F; Cat.Economic other;
Evidence: t=3.1 in port sort, Table 3A BLOCK=4; Start Month 6; GScholar cites 2036.
Sibling output Activism2 comes from the same script (blockholdings among high
external governance firms; also infeasible for the same reasons).

## 10. Proposed Sharadar mappings / deviations

None proposed. Fields NOT in `field_map_index.yaml`: G (governance index),
maxinstown_perc, shrcls. A holdings-based maxinstown_perc could in principle be built
from SF3 (per-investor shares / `sharesbas`) from 2013-06, and dual class approximated
from TICKERS.category, but G has no Sharadar source, so the conjunction cannot be
formed. Status: infeasible; no field-checker or translator work is required.
