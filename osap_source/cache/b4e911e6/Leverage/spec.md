# Leverage — Market leverage: total liabilities divided by market value of equity (Bhandari 1988, JF, Table 1 DER)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/Leverage.py` (cached `predictor.py`; upstream `upstream_CRSPMonthly.py`, `upstream_CompustatAnnual.py`, `upstream_SignalMasterTable.py` beside it).
DATA_SHA 198b281de1a0. Written fresh from source and `field_map_index.yaml`.

## 1. Data availability (verdict: APPROX, translatable; no unavailable input)

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `lt` (total liabilities) | `compustat.lt` | SF1 `liabilities`, ART (a level) | mapped (verified) | not zero-filled: missing lt -> NaN (row dropped) |
| `mve_permco` (company market equity, month t) | `crsp.mve_permco` | `ctx.universe["mkt_cap_usd"]` = DAILY.marketcap x 1e6 (already company-level) | approx | NaN -> NaN |
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt. No zero-fill of an optional term (lt is not in OSAP `zero_fill_vars`). SF1 debt fields not used (the debtc gate does not apply; `liabilities` is not null-inflated by unclassified balance sheets: null 0.05% ART).
- Status `approx` because `mve_permco` is approx (other listed classes priced at the primary's price, unlisted classes included; <= 2% of names) and for the currency mix below; not for any missing item.

## 2. Variables (exact source names)
`gvkey, permno, time_avail_m, lt` from `m_aCompustat` (annual Compustat, 6-month lag, replicated 12 months; first row per permno-month kept); `permno, time_avail_m, mve_permco` from SignalMasterTable; inner merge.

## 3. Formula in words and key lines
```
Leverage = lt / mve_permco ;  df.dropna(subset=["Leverage"])        # no guards: lt = 0 gives 0, lt < 0 gives a negative value
```
Total liabilities over the company's market capitalisation at the signal month; no winsorising, no filter, no log. Contrast with book leverage (BookLeverage, assets / book equity): the denominator here is MARKET equity.

## 4. Timing / lag convention
OSAP: lt is an annual balance-sheet item available datadate + 6 months and held 12 months (6-17 months old); mve_permco is the month-t market cap (current). Here: ART `liabilities` of the latest filing with datekey <= signal date
(filing age, monthly median over the universe: mean 50 days across 276 months, range 3 .. 111 days), quarterly refresh, and market cap at the signal date. The 6-month annual lag is not reproduced: the balance sheet is fresher than OSAP's. lt is a LEVEL, so ART equals ARQ at the same reportperiod (99.0% within $1); no flow item, no TTM smear, no `dimension` override needed.

## 5. Filters
OSAP: SignalMasterTable filter only (shrcd 10/11/12, exchcd 1/2/3); SignalDoc Filter blank. Here: harness universe only.

## 6. Predicted sign
SignalDoc `Sign = +1.0` (high market leverage -> high return); T-Stat 3.93 (regression, Key Table "1 DER", Test "mv reg"); Return blank; Stock Weight EW; LS Quantile blank; Portfolio Period 12.0; Start Month 6.0; Cat.Economic leverage. Orientation: `ascending=True` (long HIGH).

## 7. The mass-point question
Do-nothing firm: a continuous ratio; the only default value is lt = 0 (no liabilities) giving exactly 0. Measured on the harness universe at all 276 signal months (1998-12-31 .. 2021-11-30):
- Modal share of the scored cross-section max 0.10%, mean 0.05%; distinct values = n scored (min 1,736, max 2,829); no `qcut(10)` collapse. Exact-zero or negative `liabilities` among non-null: mean 0.03%, max 0.29%.
- Coverage of the universe (share with a value): mean 99.6%, min 97.0% (null `liabilities` up to 2.8% in the earliest months, 0.0% by 2021), max 100.0%. Median leverage by month 0.23 .. 1.06 (mean of monthly medians 0.51).
Tie handling: none needed; harness average rank.

## 8. History needed (snapshot starts 1998-01)
One filing (ART) and a market cap; no price window, no `history_months`. `lookback_months` = the 15-month maximum filing age. Coverage is full from the first decision month (98.5% at 1998-12, 98.4% at 1999-01).

## 9. OSAP metadata
Leverage (Acronym2 Leverage); Bhandari 1988 JF; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form continuous; Cat.Data Accounting; Cat.Economic leverage;
Sample 1952-1981; Key Table "1 DER"; Test "mv reg"; Sign +1.0; T-Stat 3.93; EW; Portfolio Period 12.0; Start Month 6.0; Filter blank; GScholar cites 2597. Definition: total liabilities (lt) divided by market value of equity.

## 10. Proposed Sharadar mappings with deviations
```
f  = ctx.fundamentals(["liabilities", "fxusd"])            # ART, latest datekey <= signal
Leverage = f["liabilities"] / ctx.universe["mkt_cap_usd"].where(mkt_cap_usd > 0)   ; .where(f["fxusd"] == 1) ; ascending=True
```
Deviations: (a) CURRENCY: `liabilities` is reporting currency, `mkt_cap_usd` is USD (DAILY); gate `fxusd == 1` (drops 0.00-0.06% of names, measured coverage gap 0.03 points on average) or divide by fxusd (USD = field / fxusd); OSAP keeps curcd = USD rows only, which the gate matches.
(b) TIMING: latest quarterly ART filing instead of OSAP's 6-month-lagged annual item. (c) `mve_permco` -> `mkt_cap_usd` (approx, see field map: secondary-class pricing, unlisted classes). (d) OSAP keeps lt = 0 and lt < 0 (0.03% mean); measured here with `liabilities > 0` only, keeping lt >= 0 changes at most 0.29% of names (max month). Either is acceptable; the translator states which.
Factual overlap, measured as Spearman per month averaged over 276 months on the harness universe: rho(Leverage, assets / mkt_cap_usd) mean 0.947 (range 0.92 .. 0.97), the AM candidate's ratio; rho(Leverage, SF1 equity / mkt_cap_usd) mean 0.563 (range 0.44 .. 0.76), the book-to-market ratio family behind the v0 Value leg (raw equity / cap, not the leg's exact book equity).
Fields not in the map: none.
