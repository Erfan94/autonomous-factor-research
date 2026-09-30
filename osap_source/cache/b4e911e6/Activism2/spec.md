# Activism2 — spec (Phase A, fetch batch 01)

Pinned ref b4e911e69678a7424f318617a61d813f54183123. Snapshot DATA_SHA 198b281de1a0.

## 1. Data availability — VERDICT: INFEASIBLE

Two of the three required inputs do not exist on this snapshot, and they never overlap in time.

| input | source in OSAP | Sharadar | verdict |
|---|---|---|---|
| `G` (Gompers-Ishii-Metrick governance index) | `upstream_GovernanceIndex.py`: external Governance.xlsx (Gompers site), survey years 1990/93/95/98/99/2002/04/06, forward-filled monthly, **ends 2007-01** | none. No Sharadar table carries takeover-defence / charter-provision counts | UNAVAILABLE |
| `maxinstown_perc` (TR_13F; largest single 13F holder's % of shares) | `upstream_InstitutionalHoldings13F.py`: Thomson Reuters 13F (WRDS) `tr_13f.csv`, forward-filled | SF3 (holder-level 13F) starts **2013-06-30** (manifest min_date); SF3A starts 2013-06. Pre-2013 13F is out of scope per project rules. Also no field_map key exists for 13F holdings | UNAVAILABLE pre-2013 |
| `shrcls` (CRSP share class) | `monthlyCRSP.shrcls` | no key in field_map_index; TICKERS carries one primary-class row per company, no point-in-time share-class letter | approx at best |
| `ticker` (join key to GovIndex) | SignalMasterTable (Compustat tic) | `compustat.tic` -> `ticker` (mapped) | fine, but moot |

Decisive: G exists only through 2007-01 and 13F only from 2013-06. The two supports are disjoint,
so **no month on this snapshot has both inputs**; even with an external GIM file, the decision window
(1999-01 .. 2021-12) would be populated only 1999-2006 (about 96 months) and only from a
13F source this snapshot cannot supply for those years. SF3-era months (2013+) have no G, so the
signal is missing for every firm there. Recommendation: **infeasible**. Not approximable: the
"high external governance" filter is the signal, not an optional term; zero-filling G would
produce an unrelated 13F blockholding variable (a different hypothesis).

Field-checker list (field_map key -> Sharadar): only `compustat.tic` -> `ticker`; `crsp.shrcd` ->
`TICKERS.category` and `crsp.exchcd` -> `TICKERS.exchange` (universe only). No key exists for
G, maxinstown_perc, instown_perc, numinstown, shrcls. Nothing needs verifying for a factor file
because none should be written.

## 2. Variables (exact source names, from ZZ1_Activism1_Activism2.py)
- `maxinstown_perc` (TR_13F, permno x time_avail_m): % of shares held by the largest 13F institution; monthly via ffill of quarterly 13F between first and last observation of each permno.
- `G` (GovIndex, ticker x time_avail_m): GIM index 1-24 (higher = more takeover defences = weaker external governance). `int8`.
- `shrcls` (monthlyCRSP): share-class letter; "" for single class.
- `ticker`, `exchcd`, `permno`, `time_avail_m` (SignalMasterTable).

## 3. Formula
Words: the largest institutional blockholder's ownership percent (set to 0 if at most 5 percent), kept only for
firms with strong external governance (24 - G >= 19, i.e. G <= 5) and a single share class; missing otherwise.
```
tempBLOCK = maxinstown_perc if maxinstown_perc > 5 else 0      # null maxinstown_perc -> 0 (polars when/otherwise)
tempBLOCK = None if G is null
          = None if shrcls != "" and shrcls not null            # dual class
tempBLOCK = None if (24 - G) < 19
Activism2 = tempBLOCK
```
The script also emits Activism1 (quartile of tempBLOCK by month, then 24 - G); Activism2 uses no quartile step and no fastxtile.
Quirk: rows with null `ticker` skip the GovIndex join (G null) so are always missing.
Note the dual-class test in Activism2 treats null shrcls as single class; Activism1's test (`shrcls != ""`) differs on nulls.

## 4. Timing / lag
time_avail_m is the merge key for both 13F and G. 13F `rdate` month is used as availability month (the quarter-end
month, NOT the ~45-day later filing date) — a look-ahead of up to 2 months in OSAP. Source lag is not added by the
script; the signal at month t is the value in t's row. GIM G availability months are hard-coded
(1990-09, 93-07, 95-07, 98-02, 99-11, >=2002-01). Flow items: none (levels only), so no ARQ/TTM smear and
ART-as-of-filing is irrelevant. Not applicable to Sharadar since nothing maps.

## 5. Filters
Stock must have non-null G (hence in the GIM universe, ~1,500 large firms of the IRRC set), single share class,
G <= 5. No price/size/exchange filter inside the script (SignalMasterTable supplies permno-months).

## 6. Predicted sign
SignalDoc `Sign` = 1.0 (higher blockholder percent -> higher return). Long-short quantile 0.25, VW, LS quantile per
SignalDoc; Cat.Economic = ownership; Cat.Data = 13F; Return 0.66 %/mo, T-Stat 2.0 (published, in-sample 1990-2001).

## 7. Mass-point question
High. Among firms passing the G <= 5 filter, everyone with maxinstown_perc <= 5 or no 13F record gets exactly 0.
Largest single 13F holder is above 5 percent for a minority of large caps (in the 1990s especially), so the do-nothing
mass at 0 is expected to be a majority of the populated cross-section (order of 60-80 percent; an estimate, not
measured, because the data do not exist here). Ties: all zeros tie; the nonzero part is continuous (range 5 to
about 30). A decile sort would collapse D1-D5+ onto the same value; ranks would need average-rank ties. This
alone would be a preflight concern even if the data existed.

## 8. History needed
No return-window history. Data supports: G from 1990-09 to 2007-01 only; 13F (TR) from 1980 in OSAP; Sharadar SF3
2013-06 on. Snapshot starts 1998-01, so even the G-covered window is 1999-01 .. 2006-12 at most.

## 9. OSAP metadata
Acronym Activism2; Cat.Signal Predictor; Predictability in OP 2_likely; Rep Quality 1_good; Cremers and Nair 2005 JF
("Governance mechanisms and equity prices"); long description "Active shareholders"; Cat.Form continuous; Cat.Data 13F;
Cat.Economic ownership; sample 1990-2001; Key table "4A VW EXT=4"; Test "port sort CAPM alpha"; Stock Weight VW;
Start Month 6; Portfolio Period 1. Script: Signals/pyCode/Predictors/ZZ1_Activism1_Activism2.py (emits both).
Upstream: DataDownloads/GovernanceIndex.py, InstitutionalHoldings13F.py (cached as upstream_* under Activism1/).
There is no file named Activism2.py; the SignalDoc row is authoritative (Cat.Signal == Predictor).

## 10. Proposed Sharadar mappings
None viable. Candidate partial proxies and why they are rejected:
- SF3 `maxinstown_perc` from holder-level `value`/`units` per `ticker` per quarter: possible only 2013-06 on, and needs
  shares outstanding (SF1 `sharesbas`) as denominator; yields ownership but no G, and so would be a different signal.
- G: no proxy. Not in the field map (flag for index: "external governance index (GIM)" -> unavailable).
- shrcls: none; dual-class could be approximated from multiple TICKERS rows per permaticker/company with
  category "... Primary/Secondary Class" — not needed.
Recommendation to the loop: log as `infeasible` in `osap_source/osap_frontier.yaml`, reason "G index (GIM) external,
ends 2007-01; 13F (SF3) starts 2013-06; supports disjoint; no month has both". Sibling Activism1 shares the same
inputs and the same verdict (note only; construction identical in inputs).
