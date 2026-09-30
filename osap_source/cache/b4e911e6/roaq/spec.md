# roaq — Return on assets, quarterly (Balakrishnan, Bartov and Faurel 2010, JAE)

## 1. Data availability — VERDICT: approx (feasible with declared deviations); no zero-fill involved
| OSAP input | field_map_index | Sharadar | note |
|---|---|---|---|
| ibq (income before extraordinary items, quarterly) | mapped -> netinccmn (index entry stale, see 10) | netinc + netincdis at dimension=ARQ | approx: netinc is after NCI; extraordinary items not separable |
| atq (total assets, quarterly) | mapped | assets (ARQ) | level, ART==ARQ |
| gvkey link | - | ticker -> harness ID | none needed |
OSAP zero-fill: upstream_CompustatQuarterly.py zero_fill_vars = acoq actq apq cheq dpq drcq invtq intanq ivaoq gdwlq lcoq lctq loq mibq prstkcy rectq sstky txditcq. Neither ibq nor atq is zero-filled, and the predictor has no fillna. A missing ibq or atq drops the row (`dropna(subset=['roaq'])`). Nothing is missing here in a way OSAP fills; verdict is approx only because of the ibq proxy.

## 2. Variables (exact source names)
m_QCompustat: atq, ibq (gvkey, time_avail_m). SignalMasterTable: permno, gvkey, time_avail_m. No price, no industry.

## 3. Formula in words and key lines
Latest quarter's income before extraordinary items divided by the PREVIOUS quarter's total assets (assets three months earlier in the monthly panel).
```
df = SMT(permno, gvkey, time_avail_m) inner-merge m_QCompustat(gvkey, time_avail_m, atq, ibq)
df["time_lag3"] = time_avail_m - 3 months
atq_lag3 = atq of the same permno at time_lag3          # self-merge, left
roaq = ibq / atq_lag3 ; dropna
```
Because m_QCompustat holds each quarter for 3 monthly rows (offsets 0,1,2), atq at t-3 is the prior quarter's assets. No winsorising, no sign flip, no industry adjustment.

## 4. Timing / lag convention; ART-as-of-filing; flow smear
- OSAP availability: time_avail_m = datadate month + 3, or the rdq month if later; quarters with rdq > 6 months after datadate are dropped; each quarter is held 3 months then replaced (max staleness ~5 months after quarter end).
- Sharadar: SF1 `datekey` (the named `date` in the direct API) is the filing date: use ctx.fundamentals_history(["netinc","netincdis","assets"], 2, dimension="ARQ"), latest = q_back 0 (ibq), previous = q_back 1 (assets). Stock at the signal date, no ad hoc lag. This is a real filing-date version of OSAP's datadate+3/rdq rule.
- FLOW SMEAR: ibq is a single-quarter flow. It MUST be read at dimension="ARQ" (and FactorDef.dimension="ARQ"). The harness default ART is a trailing four-quarter sum and would make this a TTM ROA, a different signal (field_map_index ibq note: ART == rolling-4 sum of ARQ). assets is a level (ART==ARQ).
- Align previous assets by REPORT PERIOD: require reportperiod(q_back 1) to be about 3 months before reportperiod(q_back 0) (measured gap window 2..4 months below); a missing intermediate quarter -> NaN, as in OSAP (panel row at t-3 absent). See the reviewed factors/candidates/EarningsSurprise.py for the same ARQ history/k-index handling.
- Staleness: OSAP drops a quarter after ~3 monthly rows; the harness tolerance is 15 months. Recommend a latest-filing age gate (EarningsSurprise uses 110 days). Measured: 1.33% of universe-month names (2,404 of 180,240 over a 92-month subsample, every third month of 1999-01..2021-12) have a latest ARQ datekey older than 110 days, so the gate is cheap.
- SIGN TRAP (known_trap sf1_netincdis_sign_inverted): ib = netinc + netincdis, PLUS, not minus. Measured: netincdis != 0 on 11.5% of latest-quarter rows in the decision window (pooled over 276 months), so the sign matters for ~1 in 9 names.

## 5. Filters
OSAP predictor: none (valid gvkey link; both terms non-missing). SignalDoc Filter abs(prc)>1 is the portfolio stage, not in predictor.py (universe: price >= $1). Denominator guard recommended: assets_lag > 0 (assets exact-zero 0.01% of non-null, data-error rows).

## 6. Predicted sign
SignalDoc Sign = +1 (high quarterly ROA earns higher returns; LS 0.1, EW, monthly; sample 1976-2005, t=6.45; Cat.Economic = profitability, Cat.Data = Accounting, quality 1_good; SignalDoc note: "like a more timely version of the other profitability measures").

## 7. Mass-point question
A do-nothing (zero-income) firm gives ibq = 0 -> roaq = 0; MEASURED on the harness universe, all 276 decision months (signals 1998-12-31..2021-11-30), ibq = netinc + netincdis over previous-quarter assets with gap 2..4 months: the modal exact value holds at most 0.17% of scored names (mean 0.06%); exact zeros at most 3 names per month (mean 0.6); at least 1,722 distinct values (mean 1,936) per month. No mass point. Names that do nothing in the sense of not filing are NaN (stale), not a value. Ties: none to handle; NaN -> blend renormalises.

## 8. History needed
Two quarterly filings (the latest and the one before). Snapshot starts 1998-01, SF1 ARQ history before that is thin; measured coverage at the first month (signal 1998-12-31) is 97.2% of the universe, at 1999-12-31 95.2%, so no data-start problem. No return window, no `history_months` needed.

## 9. OSAP metadata
Acronym roaq; Acronym2 RoAq; Cat.Economic = profitability; Cat.Data = Accounting; Cat.Form continuous; Sample 1976-2005; Sign +1; portfolio monthly; pinned ref b4e911e6; upstream: osap_source/cache/b4e911e6/roaq/upstream_CompustatQuarterly.py and upstream_SignalMasterTable.py.

## 10. Proposed Sharadar mappings and deviations
- ibq -> SF1.netinc + SF1.netincdis at ARQ (approx; matches the 2026-09-30 remap of compustat.ib, PLUS sign). FLAG: field_map_index still lists compustat.ibq as mapped -> netinccmn (after preferred dividends; its note says ARQ is a genuine quarterly flow). The index entry is out of step with the ib remap; this spec follows the ib remap because ibq is the same quantity at a quarterly dimension. netinccmn would differ on ~12% of rows (prefdivis), ib-remap vs netinc on 11.5%.
- atq -> SF1.assets at ARQ, previous reportperiod (mapped).
- Deviations: (1) OSAP first-available = datadate+3/rdq month held 3 months; here the SF1 filing date (datekey) and an age gate. (2) netinc is after minority interest (ib is before NCI split); extraordinary items are not separable. (3) OSAP Compustat quarter is overwritten on restatement; SF1 ARQ keeps the as-reported (PIT) row known at the signal. (4) Previous assets by report period, not by the panel's month-3 row.
- Fields not in the map: none.
- Measured coverage (same measurement, 276 months): mean 98.64% of the universe scored (min 94.59%) with the 2..4-month gap rule; 98.86% (min 95.05%) without it; universe mean 1,965 names per month (min 1,739, max 2,867).
Recommendation: feasible with approx deviations; ready to translate; no `history_months`; FactorDef.dimension="ARQ", ascending=True.
