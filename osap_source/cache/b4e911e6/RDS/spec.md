# RDS — Real dirty surplus (Landsman et al. 2011 Accounting Review, Table 4)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Signals/pyCode/Predictors/RDS.py` (cached `predictor.py`, `upstream_CompustatAnnual.py`,
`upstream_CompustatPensions.py`). DATA_SHA 198b281de1a0. No measurement was needed: the verdict follows from OSAP's own code plus field availability.

## 1. Data availability — VERDICT: data_unavailable (infeasible). The zero-fill does NOT rescue it.

| input (OSAP) | field_map key | Sharadar | status |
|---|---|---|---|
| `recta` (retained earnings unappropriated adjustments) | `compustat.recta` | none | unavailable |
| `msa` (marketable securities adjustment) | `compustat.msa` | none | unavailable |
| `pcupsu`, `paddml` (pension unrecognised prior service cost, additional minimum liability) | none (not in `field_map_index.yaml`) | none (pensions) | unavailable |
| `ceq` | `compustat.ceq` | SF1 `equity` | approx (no preferred split) |
| `ni` | `compustat.ni` | SF1 `netinc` | mapped |
| `dvp` | `compustat.dvp` | SF1 `prefdivis` | mapped |
| `dvc` | `compustat.dvc` | SF1 `ncfdiv` | approx (predominantly common-only) |
| `prcc_f` (fiscal-year-end price) | `compustat.prcc_f` | SF1 `price` | approx |
| `csho` | `compustat.csho` | SF1 `sharesbas` | mapped |

- The missing-item rule: OSAP DOES fill `recta`, `msa` with 0 and treats missing pension data as 0 inside `min_pension`. But it then nulls the signal where the
  items were ORIGINALLY missing (key lines below). With `recta` and `msa` both unavailable in SF1, that mask is True on every row, so OSAP's own code would set
  RDS = NaN for the whole cross-section: the zero-fill is an input convention for partial reporters, not a rescue of an absent field. (Same logic as the
  IO_ShortInterest frontier row: a fill does not rescue a filter that depends on the missing field.) Pensions are zero-filled by OSAP and are not the obstacle.
- Dropping the mask and running with DS = 0 would yield `d(ceq) - (ni - dvp) + dvc - prcc_f * d(csho)`, a different signal (a clean-surplus violation proxy that
  leaves out the dirty-surplus components the paper is about); not adopted (near-match rule). Not proposing `accoci` either; it is not in the field map.
- No IBES/options/13F/patents/segments/ratings/xad/emp/ob/ppegt input, but pensions (`pcupsu`, `paddml`) are unavailable.

## 2. Variables (exact source names)
`recta, ceq, ni, dvp, dvc, prcc_f, csho, msa` (`m_aCompustat`), `pcupsu, paddml` (`CompustatPensions`, year+1 availability lag), `permno, gvkey, time_avail_m`.

## 3. Formula
```
DS  = (msa - l12.msa) + (recta - l12.recta) + 0.65*(min(pcupsu - paddml,0) - min(l12.pcupsu - l12.paddml,0))
RDS = (ceq - l12.ceq) - DS - (ni - dvp) + dvc - prcc_f*(csho - l12.csho)
```
`msa`, `recta` current values `fillna(0)` (lags NOT filled); missing pension terms count as 0 in the `min()`. Lags are the row 12 months earlier (calendar merge on `time_avail_m - 12 months`).
Key lines: `both_missing_mask = (recta_orig_missing & l12_recta_orig_missing) & (msa_orig_missing & l12_msa_orig_missing)`; `df.loc[both_missing_mask, "RDS"] = np.nan`; `df.dropna(subset=["RDS"])`.

## 4. Timing / lag
OSAP annual records at `datadate + 6 months` held 12 months; pensions carry an extra 1-year lag (`year = datadate.year + 1`). SF1 would be ARY at filing date. `ceq`, `csho`, `prcc_f` are levels at fiscal year end, `ni`, `dvp`, `dvc` are
flows (year-over-year level differences of balance items, annual flows): ARY needed (ART would mis-window the 12-month lag, ARQ smears); `dimension="ARY"` would be required.

## 5. Filters
None in the code besides the dropna on RDS. SignalDoc Filter blank. Sample in the paper: 1976-2003.

## 6. Predicted sign (SignalDoc)
`Sign = +1.0` (`ascending=True`). Cat.Economic `composite accounting`, Cat.Form continuous, Cat.Data Accounting; Test "port sort FF3 alpha"; T-stat 5.84; Return 0.333 (tercile sorts); LS quantile 0.333; EW; Portfolio Period 12; Start Month 6; Predictability `1_clear`.

## 7. The mass-point question
Moot (no value is computable). Were DS forced to 0 the output would be continuous (a difference of level changes), with no mass point; a firm with no change in any term produces exactly 0 but that is a measure-zero case. Not measured.

## 8. History needed
Moot. The 12-month lag would need FY1997+ pairs (SF1 ARY from ~FY1996/97), which would leave >= 120 months; the data, not the history, is the obstacle. Not measured on the snapshot (no SF1 field to read for `msa`, `recta`, `pcupsu`, `paddml`).

## 9. OSAP metadata
Acronym `RDS` (Acronym2 `RDirtSurp`); Landsman, Miller, Peasnell, Yeh, The Accounting Review 2011 ("Do investors understand really dirty surplus?"); Key Table 4; Sample 1976-2003; Sign +1; T 5.84; GScholar cites 75.
Detailed Definition: dirty surplus = annual change in `msa` + change in `recta` + .65 * change in `min(pcupsu - paddml, 0)`; real dirty surplus = change in `ceq` - DS - (`ni` - `dvp`) + dividends - `prcc_f` * change in `csho`.

## 10. Proposed Sharadar mappings and deviations
None to translate. Needed and not in field_map: `msa`, `recta`, `pcupsu`, `paddml` (none carried by any of the 13 held tables). `ceq -> SF1.equity` (approx), `ni -> netinc`, `dvp -> prefdivis`, `dvc -> ncfdiv` (approx), `prcc_f -> price` (approx), `csho -> sharesbas`.
Recommend `data_unavailable`: OSAP's own `both_missing_mask` nulls every row when `msa` and `recta` are absent.
