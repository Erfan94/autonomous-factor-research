# iomom_cust — Customers momentum (Menzly and Ozbas 2010, JF, Table 2 (1) r_customer,t-1)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/ZZ1_iomom_cust__iomom_supp.py`
(cached `predictor.py`), which shells out to `ZZ1_iomom_cust__iomom_supp.R` (cached
`upstream_ZZ1_iomom_cust__iomom_supp.R`) on BEA tables downloaded by `BEA_InputOutput.py` (cached
`upstream_BEAInputOutput.py`). One script emits both iomom_cust and iomom_supp (separate specs). DATA_SHA
198b281de1a0.

## 1. Data availability — VERDICT: data_unavailable (infeasible; do not translate)

| input | source in OSAP | Sharadar | status |
|---|---|---|---|
| BEA Make table (customer weights), pre-1997 `IOMake_Before_Redefinitions_1963-1996_Summary.xlsx` and post-1997 `Supply_Tables_1997-20XX_Summary.xlsx` | bea.gov download | none | **external table, not in the snapshot** |
| firm NAICS (`naicsh`, Compustat annual) -> BEA industry | CompustatAnnual.csv | none: `compustat.naicsh` / `compustat.naics` **unavailable** in `field_map_index.yaml` | unavailable |
| CRSP returns and market cap (`ret`, `abs(prc)*shrout`) | monthlyCRSP | SEP-derived (mapped) | available |
| CCM link gvkey<->permno | CCMLinkingTable | not needed under Sharadar ids | n/a |

- Checked on THIS snapshot (parquet schemas, all 13 held tables): TICKERS has `siccode`, `sicsector`,
  `sicindustry`, `famaindustry`, `industry`, `sector` (current classifications only) and no NAICS; no table
  holds customer/supplier links, input-output coefficients or any BEA-style industry-by-industry matrix.
  SF1/SF3/SF2/SEP/DAILY/METRICS/EVENTS/ACTIONS/SP500/DESCRIPTIONS columns were scanned by regex for
  naics/industry/supplier/customer: nothing beyond the TICKERS classification fields above.
- Missing-item rule: the IO weights and the NAICS mapping are NOT zero-filled anywhere in OSAP. The R script
  inner-filters: `filter(!is.na(naics6))`, `filter(!is.na(weight))`, `filter(!is.na(retmatch))`; firms
  without a BEA industry or IO weights drop out. Nothing is filled with 0. OSAP provides no fallback for a
  missing IO matrix. SIC->BEA crosswalk plus a hand-entered IO matrix would be an external dataset and a
  different signal (BEA summary-level codes are NAICS-based; the R code matches naics2/3/4 prefixes).
  Verdict per the rule: **data_unavailable** (infeasible).

## 2. Variables (exact names)
R: `naicsh`->`naics6`, `datadate`, `year_avail = year(datadate + 6 months) + 1`; CRSP `permno, date, ret`
(x100), `mve_c = abs(prc)*shrout`; CCM `gvkey, permno, linkdt, linkenddt`; BEA IO weights `beaind,
beaindmatch, weight`, `year_avail = table_year + 5`. Python: SignalMasterTable `permno, gvkey, time_avail_m`.

## 3. Formula
1. BEA IO tables (Make tables for customers) for each year, `year_avail` = table year + 5 (5-year release
   lag). Industry-by-industry weights, own-industry entries dropped (`beaind != beaindmatch`).
2. Firms matched to BEA industry by Compustat NAICS prefix (4, 3, else 2 digits; `coalesce`).
3. Industry-month return = market-cap-weighted mean of member-firm returns (`weighted.mean(ret, mve_c)`),
   for years >= 1986.
4. For industry i in month t: `retmatch_{i,t}` = IO-weighted average of the returns of the OTHER industries
   linked to i (customer momentum: industry from the rows of the Make table, matched industries from its
   columns).
5. Signal = `retmatch` (continuous, %, month t) merged to each firm via gvkey on `time_avail_m`.
   Decile `portind` is computed in R but the predictor uses `retmatchcustomer` itself.
   iomom_cust = `retmatchcustomer`. Every firm in the same BEA industry-month gets the SAME value.

## 4. Timing / lag
Signal month t uses month-t returns of the linked industries; OSAP then holds it for the following month
(SignalDoc `Portfolio Period` 1). IO tables enter with a 5-year lag.

## 5. Filters
SignalDoc Filter blank; R drops missing NAICS/IO/returns; pre-1986 dropped (NAICS availability).

## 6. Predicted sign
SignalDoc Sign = +1.0: high matched-customer-industry return predicts HIGH returns (`ascending=True`).
Cat.Economic: lead lag. Predictability in OP: 2_likely; Signal Rep Quality 2_fair.

## 7. The mass-point question
Not measured: no construction exists. Structural note for the record: the signal is an industry-level
number, so every firm in a BEA industry shares one value and the number of distinct values per month is
at most the ~70 BEA industries (a tie block is a whole industry; not measured here). This would be a
likely additional preflight risk (10% cliff) even with a substitute matrix.

## 8. History needed
Not reached (OSAP sample 1986-2005; BEA tables 1963+).

## 9. OSAP metadata
Predictor | 2_likely | 2_fair | Menzly and Ozbas 2010 JF | continuous | Other | lead lag | sample 1986-2005 |
Sign +1 | EW | LS quantile blank | Portfolio period 1 | Start month 6 (SignalDoc) | Filter none | t 4.11 (mv reg) | cites 727.
SignalDoc note: "Early in the paper they use a stock level mv reg with many controls; later they sort
industry portfolios instead of stocks ... evidence on standard portfolio sorts is unclear."

## 10. Proposed Sharadar mappings and deviations
None possible. `compustat.naicsh` / `compustat.naics` unavailable (index); BEA Make table external.
Fields not in the map: BEA IO matrix (not a Compustat field; no map key). Recommendation for
`osap_frontier.yaml`: "BEA Make/Use input-output tables (external downloads) and Compustat NAICS are not in
the Sharadar snapshot; OSAP has no fallback and does not zero-fill them". Verdict: **data_unavailable**.
