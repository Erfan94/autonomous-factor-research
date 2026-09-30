# ConvDebt — Convertible debt indicator (Valta 2016, JFQA, Table 4 DCONV)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/ConvDebt.py` (cached `predictor.py`,
`signaldoc_row.csv`, `upstream_CompustatAnnual_dc_derivation.py`). DATA_SHA 198b281de1a0.

## 1. Data availability — VERDICT: INFEASIBLE (both inputs absent; dropping them leaves a constant)

| input (OSAP) | field_map key | Sharadar | status | note |
|---|---|---|---|---|
| `dc` (convertible debt, built upstream) | `compustat.dc` (verified_on 2026-09-30) | none | unavailable | OSAP derives dc from `dcvt` / `dcpstk` / `pstk`; none of dcvt, dcpstk is in SF1 (`compustat.dcvt`, `compustat.dcpstk` unavailable) |
| `cshrc` (common shares reserved for convertible debt) | `compustat.cshrc` | none | unavailable | not zero-filled by OSAP (absent from upstream `zero_fill_vars`) |

- Checked against `data/sharadar_llms.txt` and `osap_source/api_schema/*.sql`: no convertible-debt, reserved-share or
  debt-instrument column in any held table (SF1, DAILY, SEP, TICKERS, ACTIONS, EVENTS, SF2, SF3).
- OSAP zero-fills `dc` (`zero_fill_vars` in upstream `CompustatAnnual.py` line 139, applied AFTER the dcvt/dcpstk
  derivation at lines 106-127). Under the standing rule, the dc term is dropped; `cshrc` is an unavailable
  NON-zero-filled item. With both terms gone the signal is `ConvDebt = 0` for every firm-month: a constant, undefined
  for ranking. Per the rule "dropping leaves the signal constant -> infeasible". Recommend `infeasible`.
- No proxy accepted: SF1 `debt`, `debtc`, `debtnc` are straight debt totals and do not identify a convertible tranche;
  substituting them would be a different signal (leverage), not a near-match. Not used.
- Also not used anywhere: IBES, options, ratings, pensions, segments, patents, ppegt.

## 2. Variables (exact source names)
`dc` (Compustat, derived: `dcpstk - pstk` if dcpstk > pstk, pstk notna, dcvt missing; `dcpstk` if pstk missing and
dcvt missing; else `dcvt`; then NaN -> 0), `cshrc`, `gvkey`, `permno`, `time_avail_m`.

## 3. Formula
```
df["ConvDebt"] = 0
df.loc[(dc.notna() & (dc != 0)) | (cshrc.notna() & (cshrc != 0)), "ConvDebt"] = 1
```
Binary: 1 if the firm has convertible debt (dc != 0) or shares reserved for conversion (cshrc != 0). Because `dc` was
zero-filled upstream the `notna()` test is redundant; in practice the indicator is "any dcvt/dcpstk-derived balance
or any cshrc".

## 4. Timing / lag
`m_aCompustat` = annual Compustat forward-filled to months with OSAP's annual availability lag (the SignalDoc
"Start Month 6" is the portfolio start month; annual data enter about 6 months after fiscal year-end). Annual items, so
no ART/ARQ smear issue would arise here; moot because the inputs do not exist.

## 5. Filters
OSAP predictor file: none. SignalDoc Filter: empty. `drop_duplicates(permno, time_avail_m)` keep first.

## 6. Predicted sign
SignalDoc `Sign = -1.0`: convertible-debt issuers earn LOWER subsequent returns (Valta 2016 Table 4; "t > 2.6 in mv
reg", Stock Weight EW, sample 1985-2012). Cat.Economic `external financing`, Cat.Data Accounting, Cat.Form discrete.
Would be `ascending=False`.

## 7. The mass-point question
A binary indicator is ALL mass points: two values. In Compustat roughly a quarter of firm-years carry convertible
debt / reserved shares (estimate from the published literature, not measured here); ~70-75% of firms "do nothing"
and take 0. Within a sector rank the zero group would tie at the mid-rank; 2 distinct values -> deciles collapse
(D10 and D1 would both be mass points). Would fail the preflight mass-point check even if buildable. Moot: infeasible.

## 8. History needed
Would need annual filings from FY1997 on for the 1999-01 start; SF1 ARY starts 1997Q4. Moot.

## 9. OSAP metadata
Acronym ConvDebt; LongDescription "Convertible debt indicator"; Authors Valta; Year 2016; Journal JFQA; Sample
1985-2012; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form discrete; Cat.Data Accounting;
Cat.Economic external financing; Sign -1.0; T-Stat 4.5; Key Table "4 DCONV" (mv reg); Stock Weight EW;
Portfolio Period 1; Start Month 6. Note (SignalDoc): "We focus on the dummy but it's a judgement call" (the convertible
PROPORTION, Table 5C, has non-monotone sorts). Detailed Definition in the row says "deferred charges (dc)"; the field_map
correction (2026-09-30) and the upstream derivation establish dc is convertible debt, not deferred charges.

## 10. Proposed Sharadar mapping
None. No mapping exists for `dc` or `cshrc`; no factor file should be written. Fields not in the map: none (both are
in the index as unavailable). Frontier row: reason "dc (dcvt/dcpstk) and cshrc absent from SF1; OSAP zero-fill of dc
leaves the indicator constant 0; binary with ~75% mass anyway".
