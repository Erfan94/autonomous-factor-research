# InvestPPEInv — One-year change in gross PP&E plus one-year change in inventory, scaled by lagged assets (Lyandres, Sun and Zhang 2008, RFS, p 2837)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/InvestPPEInv.py` (cached `predictor.py`; upstream `upstream_CompustatAnnual.py` beside it).
DATA_SHA 198b281de1a0. Written fresh from source and `field_map_index.yaml`.

## 1. Data availability (verdict: DATA_UNAVAILABLE -> recommend `infeasible`; the single missing input is `ppegt`)

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `ppegt` (gross PP&E) | `compustat.ppegt` | none (SF1 has `ppnenet`, NET PP&E, only; column scan of SF1: capex, grossmargin, inventory, ppnenet) | unavailable | NOT zero-filled: ppegt is absent from OSAP `zero_fill_vars` (nopi dvt ob dm dc aco ap intan ao lco lo rect invt drc spi gdwl che dp act lct tstkp dvpa scstkc sstk mib ivao prstkc prstkcc txditc ivst); a missing ppegt stays NaN, so the signal is NaN |
| `invt` | `compustat.invt` | SF1 `inventory` (ART level) | mapped | OSAP zero-fills invt; SF1 vendor 0 (46.3% exact zero) IS that zero-fill |
| `at` | `compustat.at` | SF1 `assets` (ART level) | mapped | not zero-filled; `l12.at == 0` -> NaN |
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob. The block is `ppegt` alone (the lead term of the numerator).
- Rule: infeasible unless OSAP itself zero-fills the missing item; OSAP does not. Net-for-gross substitution (`ppnenet`) is NOT adopted: net PP&E moves with depreciation and impairments, so
  the one-year change is not the change in gross investment; the frontier already records the same ruling for another predictor needing ppegt. No coverage/mass-point measurement is owed: the verdict does not turn on one.

## 2. Variables (exact source names)
`gvkey, permno, time_avail_m, ppegt, invt, at` from `m_aCompustat` (annual Compustat, `indfmt=INDL, datafmt=STD, curcd=USD`; rows require at, prcc_c and ni non-null; datadate + 6 months = time_avail_m, each record replicated 12 months).

## 3. Formula in words and key lines
Change in gross PP&E plus change in inventory over one year, divided by total assets one year earlier.
```
df["l12_ppegt"|"l12_invt"|"l12_at"] = df.groupby("permno")[col].shift(12)      # ROW shift of the monthly replicated panel
tempPPE = ppegt - l12_ppegt ; tempInv = invt - l12_invt
InvestPPEInv = (tempPPE + tempInv) / l12_at      where l12_at != 0, else NaN
```
Duplicates on (permno, time_avail_m) dropped keeping first. No winsorising, no size/price filter in the predictor.

## 4. Timing / lag convention
OSAP: annual item available datadate + 6 months, held 12 months; the 12-month row shift lands on the prior fiscal year's record when years are consecutive.
If ever translated: `fundamentals_yoy(..., years=1, dimension="ARY")` (fiscal-year level items, no smear); ppegt, invt, at are all BALANCE-SHEET levels, so ART would also be a level, but the YoY alignment must be by reportperiod.
ARY datekey-reportperiod lag p50 about 76 days, so the new year would enter 2-4 months earlier than OSAP's 6-month lag. No flow item in the predictor, so no TTM smear.

## 5. Filters
OSAP predictor: none (SignalDoc Filter blank). Annual-data gate: at, prcc_c, ni non-null; curcd USD.

## 6. Predicted sign
SignalDoc `Sign = -1.0` (high investment -> low return); Return 0.57; T-Stat 7.13; Stock Weight EW; LS Quantile 0.3; Portfolio Period 1.0; Start Month 6.0. Orientation would be `ascending=False`.

## 7. The mass-point question
Do-nothing firm (ppegt and invt unchanged over the year) produces exactly 0. Share not measurable: ppegt is unavailable. The inventory term alone is a mass point in the INPUT (SF1 inventory exact 0 in 46.3% of ART rows, 42% in 1999-2003 and 53% in 2021-26; 0 -> 0 gives a zero change).
Would need the standing tie rule (level 0 at both ends -> NaN) on the joint term. Not pursued.

## 8. History needed (snapshot starts 1998-01)
Two fiscal-year records per firm (current and one year earlier); SF1 from 1997Q4. Moot.

## 9. OSAP metadata
InvestPPEInv (Acronym2 InvestPPEInv); Lyandres, Sun and Zhang 2008 RFS; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form continuous; Cat.Data Accounting; Cat.Economic investment;
Sample 1970-2005; Key Table "text p 2837"; Test "LS port nonstandard"; Sign -1.0; Return 0.57; T-Stat 7.13; EW; LS Quantile 0.3; Portfolio Period 1.0; Start Month 6.0; Filter blank; GScholar cites 665.
Notes: "Not in a table. Page 2837 has untabulated results. OP does a complicated 3x3 sort with size two stage portfolio construction, but we just equal-weight." Definition: one-year change in ppegt plus one-year change in invt, scaled by one-year lagged at.

## 10. Proposed Sharadar mappings and deviations
None proposed: recommend `infeasible` (data_unavailable: `compustat.ppegt`, not zero-filled by OSAP). Mapped parts if the gross-PP&E gap were ever closed: `invt` -> `inventory` (vendor 0 = OSAP zero-fill), `at` -> `assets`.
Fields not in the map: none.
