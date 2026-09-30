# CustomerMomentum — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: INFEASIBLE (recommend `infeasible`)
Checked against `osap_source/field_map_index.yaml`: no segment / customer / CCM key exists.

| OSAP input | Sharadar | status |
|---|---|---|
| `CompustatSegmentDataCustomers.csv` (gvkey, datadate, ctype, cnms) | none: SF1 has no segment or customer-name field; no table on the snapshot carries principal-customer names | unavailable |
| `CCMLinkingTable` (gvkey <-> permno) used to match customer NAMES to firms | none (TICKERS has name / permaticker only; fuzzy name matching is not OSAP's construction) | unavailable |
| `monthlyCRSP.ret_b4_dl` | SEP closeadj month ratio | mapped (not the blocker) |

- The signal IS the segment-customer link (which listed firms are a firm's principal
  customers). Without it the customer return cannot be formed at all; there is no OSAP
  zero-fill to drop, and dropping the customer leg leaves nothing. Segments category per
  the standing unavailable list. Do not substitute `iomom_cust` (different acronym,
  input-output customer link, separate spec) or an industry-return proxy.

## 2. Variables (predictor.py)
`cnms` (customer name), `ctype`, `datadate`, `gvkey` from the Compustat segment customers file;
`permno`/`conm` from CCM; `ret_b4_dl` (monthly return before delisting return).

## 3. Formula (for the record)
Customer names are matched to `conm` of CCM-linked firms; CustomerMomentum = average, over a
firm's matched customers, of the customers' monthly returns (Cohen-Frazzini customer momentum). Not reproducible here.

## 4-5. Timing / filters
Not applicable (infeasible). SignalDoc Filter `abs(prc)>5`; `Stock Weight` VW; LS quantile 0.2.

## 6. Predicted sign
SignalDoc `Sign = 1.0` (high customer return predicts high own return; t = 3.79 in OSAP port sort).

## 7. Mass point
n/a. Coverage in OSAP is restricted to firms that disclose named customers (a minority); a
do-nothing firm has no value (missing, not zero).

## 8. History needed
n/a.

## 9. OSAP metadata
Cohen and Frazzini (2008), JF; Cat.Data = Other; Cat.Economic = lead lag; `Predictors/CustomerMomentum.py`;
SignalDoc row cached (`signaldoc_row.csv`), `Predictability in OP` 1_clear, `Signal Rep Quality` 1_good;
sample 1980-2004; Acronym2 MomCust; Portfolio Period 1, Start Month 12.

## 10. Proposed Sharadar mappings
None. Fields not in the map: segment customers (`cnms`), CCM link. `frontier` row:
`infeasible` — "needs Compustat Segment customer names; no Sharadar equivalent".
