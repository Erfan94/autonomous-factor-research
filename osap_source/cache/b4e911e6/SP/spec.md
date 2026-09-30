# SP — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: APPROX (constructible; declared deviations)
Checked against `osap_source/field_map_index.yaml`. No IBES, options, 13F, patents, segments,
ratings, pensions, xad, emp, ob or ppegt. OSAP zero-fills nothing here (`sale` is not in
CompustatAnnual `zero_fill_vars`).

| OSAP var | field_map key | Sharadar | status | note |
|---|---|---|---|---|
| sale | compustat.sale | SF1.revenue (ART) | mapped, verified 2026-09-30 | same column as revt; reporting currency |
| mve_permco | crsp.mve_permco | `ctx.universe["mkt_cap_usd"]` (DAILY.marketcap at the signal date, x1e6) | approx | company-level already; other classes priced at the primary's price |
| curcd | compustat.curcd | SF1.fxusd | approx | gate `fxusd == 1` for the reporting-currency numerator over a USD denominator |

Why approx: mve_permco mapping (company-level cap on the primary ticker), TTM numerator as of
filing vs annual with 6-month lag. Recommend: **approx** (feasible).

## 2. Variables by exact source name (predictor.py)
`m_aCompustat.parquet`: permno, time_avail_m, sale. `SignalMasterTable.parquet`: permno,
time_avail_m, mve_permco. Upstream `SignalMasterTable` = CRSP monthly restricted to shrcd
10/11/12 and exchcd 1/2/3; `mve_permco` = sum over a permco's securities of
(shrout/1000) x |prc| (USD millions), computed at each month-end (CRSPMonthly.py).
`upstream_CompustatAnnual.py` (cached): annual rows require at, prcc_c, ni non-missing;
`time_avail_m = datadate month + 6`, held 12 months.

## 3. Formula
    compustat = groupby(permno, time_avail_m).first()
    df = inner merge with SignalMasterTable on (permno, time_avail_m)
    SP = sale / mve_permco ;  dropna(SP)

Key line: `df["SP"] = df["sale"] / df["mve_permco"]`. The denominator is the CURRENT month's market
equity (price moves change SP monthly), the numerator the stale annual sales.
Sharadar form: `revenue.where(fxusd == 1) / mkt_cap_usd.where(mkt_cap_usd > 0)` with
`f = ctx.fundamentals(["revenue","fxusd"])` (ART) and `mkt_cap_usd` from `ctx.universe`
(USD, raw dollars; the harness applies the 1e6 scale). Revenue <= 0 is NOT guarded (OSAP does
not: sale = 0 gives SP = 0; a negative value would be scored as is).

## 4. Timing / lag convention
Market value at the signal date (price side is contemporaneous, like OSAP's month-t mve_permco);
sales known as of filing (median lag 44 days). OSAP: fiscal-year sales, available datadate +6
months. FLOW: `revenue` ART is a TTM sum (verified equals rolling-4 ARQ for large tickers),
a level at each filing. Do NOT use `dimension=ARQ` (single-quarter revenue over full market
value would be a quarter-sized ratio). No year-over-year difference, so no TTM smear.

## 5. Filters
predictor.py: none. SignalDoc `Filter` blank, `Quantile Filter` blank. Harness universe:
price >= $1, US common, relative cap/dollar-volume screens.

## 6. Predicted sign (SignalDoc)
`Sign = +1.0`: high sales-to-price -> high returns (Barbee, Mukherji and Raines 1996, FAJ,
Table 2 model 1; "t=2.5 in mv reg"; Acronym2 Rev2Price). `ascending=True`. Cat.Economic
valuation; Cat.Form continuous; Cat.Data Accounting; sample 1979-1991; EW; Portfolio Period
12, Start Month 6; Signal Rep Quality 1_good; Predictability 2_likely.

## 7. The mass-point question
Do-nothing firm: no structural constant; SP is a continuous ratio that moves with price.
The only point mass is sale == 0 (pre-revenue names) -> SP = 0. Measured at 92 of 276
decision months (every third, 1998-12-31 .. 2021-09-30; universe 1,739-2,867):
- modal value 0.0 in 89 of 92 months; modal share 0.56% mean, max 3.77% (2021-03-31, 2,176
  scored names; SPAC-era zero-revenue shells); rises 1.8-2.3% in 2020-09..2021-09; all below
  the 10% cliff; qcut yields 10 bins.
- revenue <= 0 among revenue-non-null: 0.7% mean (max 4.2% at 2021-03-31).
- fxusd != 1 (nulled by the gate): 0.03% of names (max 0.06%).
Tie handling: none in OSAP; average rank suffices. Noted for the translator, not a blocker.
Coverage (revenue non-null, fx == 1, cap > 0): 96.5% mean (57% at 1998-12-31, 92.5% at
1999-03-31, 85.7% at 1999-12-31).

## 8. History needed
One filing. No price window. SF1 revenue null 37% in 1994-98 ART warm-up (per field map);
first decision month (1998-12-31 signal) is thin at 57%, >= 85% from 1999-03.

## 9. OSAP metadata
Acronym SP (Acronym2 Rev2Price); Barbee, Mukherji and Raines 1996, FAJ; Key Table "2 model
1"; Test "mv reg"; T-Stat 2.52; GScholarCites202509 420. Detailed Definition: ratio of annual
sales (sale) to market value of equity. Source `Signals/pyCode/Predictors/SP.py`.

## 10. Overlap with the v0 composite (factual, from factors/composite.py)
- Value leg = equity.where(equity > 0) / mkt_cap_usd (ART). SP = revenue / mkt_cap_usd: SAME
  denominator (universe mkt_cap_usd); numerators differ (revenue vs book equity). Measured
  Spearman of raw SP with the raw Value leg: mean 0.40 (range 0.24-0.74, 92 months).
- Profitability leg (contains `revenue` in its numerator, divided by equity): 0.25.
  Size leg (log mkt cap, raw): -0.09. Momentum: -0.19. Cat.Economic (valuation) matches the
  Value seed family's label.

## 11. Proposed Sharadar mappings and deviations
| item | mapping | deviation |
|---|---|---|
| sale | SF1.revenue, ART | TTM as of filing vs annual +6 months |
| mve_permco | universe mkt_cap_usd | company-level on primary ticker; one route, no class sum |
| currency | `fxusd == 1` gate on the numerator | drops ~0.03% of names |
| universe/ranks | harness; within sector | OSAP EW cross-section |
Fields all in `field_map_index.yaml` (revenue, marketcap verified 2026-09-30).
