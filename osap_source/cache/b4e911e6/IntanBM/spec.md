# IntanBM — Intangible return using book-to-market: residual of the 5-year return on lagged BM and BM-change-plus-return (Daniel and Titman 2006, JF, Table 4)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/IntanBM.py` (the script `ZZ1_IntanBM_IntanSP_IntanCFP_IntanEP`, cached `predictor.py`; SignalDoc row Acronym = IntanBM). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`; `utils/winsor2.py` read at the pinned ref. Only the IntanBM branch is documented (the script also emits IntanSP/CFP/EP).

## 1. Data availability (verdict: APPROX; constructible, 216 of 276 decision months score, first scorable signal 2003-12-31)

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `ceq` (annual common equity, m_aCompustat) | `compustat.ceq` | SF1 `equity` (ART; preferred NOT removed) | approx (book_equity_preferred_terms ruling: OSAP's ceq has no preferred term to zero-fill; `equity` includes it) | `ceq/mve <= 0` -> log NaN -> dropped |
| `mve_permco` (company cap, months t and t-60) | `crsp.mve_permco` | DAILY.marketcap (company-level, primary ticker) x 1e6 | approx | NaN propagates |
| `ret` (monthly, total return) | `crsp.ret` | SEP `closeadj` month-end ratio over 60 months | mapped (no delisting return) | NaN -> 0 inside an existing row |
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt; no zero-fill term; preferred stock appears only as the deviation above (it does not enter the signal itself).
- The DAILY cap is needed at t-60: DAILY starts 1998-12-01 (map), so signals up to 2003-11 have no t-60 cap (measured 0% coverage at 2002-12-31 and 2003-02-28; by construction every signal before 2003-12-31).
  The SF1 route (sharesbas x price) would start 2002-12 (map) and is not adopted (a second route for one lag is not OSAP's).

## 2. Variables (exact source names)
`ceq, mve_permco, ret, permno, gvkey, time_avail_m` (sale/ib/dp/ni belong to the sibling predictors). Derived: `tempAccBM = log(ceq/mve_permco)` (NaN if ratio <= 0), `tempCumRet`, `tempRet60`, `tempAccBM_lag60`, `tempAccBMRet`, `tempU_tempAccBM` = IntanBM.

## 3. Formula in words and key lines
Each month, over all firms with data: regress the five-year stock return `tempRet60` on `BM_lag60` (log BM five years ago) and `BMRet` = (BM_t - BM_lag60 + tempRet60), with an intercept. IntanBM is the firm's residual (the part of the
five-year return not explained by the change in BM; the "intangible return").
```
tempAccBM   = log(ceq/mve_permco)  if ceq/mve_permco > 0 else NaN
tempCumRet  = exp(cumsum(log(1+ret))) by permno ; ret NaN -> 0 ; over the rows of the m_aCompustat x SMT inner merge
tempRet60   = (CumRet_t - CumRet_{t-60})/CumRet_{t-60}         # calendar lag 60 via merge on time_avail_m - 60 months
winsor2(tempRet60, trim=True, cuts=[1,99])                     # NO by(): percentiles over the WHOLE pooled panel, all months
tempAccBMRet = tempAccBM - tempAccBM_lag60 + tempRet60
each month: OLS tempRet60 ~ const + tempAccBM_lag60 + tempAccBMRet on rows with all three present (>= 2 rows)  ->  residual
```
Regression inputs are therefore: five-year return t-60..t (60 returns, includes month t), log BM at t-60 and at t.

## 4. Timing / lag convention
OSAP: ceq from the ANNUAL Compustat file, made available 6 months after the fiscal year end and carried forward up to 12 months (m_aCompustat), so BM_t uses a stale ceq and the month-t cap; BM_lag60 is the same construction five years earlier.
Here: `ctx.fundamentals_at_month_ends(["equity"], [0, 60], scope="market")` (as-known at each month-end by `datekey`) and `ctx.at_month_ends("DAILY", ["marketcap"], [0, 60], scope="market")`; signal at the month-end, earned month t+1.
ART `equity` is a LEVEL (ART equity equals ARQ equity on the same reportperiod, map): no four-quarter smear, no `dimension=ARQ` needed. ART refreshes quarterly (earlier than the OSAP annual + 6-month lag); `dimension="ARY"`
would mimic the annual cadence: measured on 42 sampled months, ART vs ARY universe coverage means 77.4% vs 75.7%, regressions near-identical (R2 mean 0.60 vs 0.56). Default ART proposed. A window needs 60 ROWS of returns in OSAP but
60 calendar months here.

## 5. Filters
OSAP code: none; SMT shrcd 10/11/12, exchcd 1/2/3; gvkey present (Compustat-linked only); one row per permno-month. SignalDoc Filter `abs(prc)>5` (a portfolio-level price filter, not in the predictor file): NOT applicable inside a factor
(no universe filters in factors); the harness $1 price floor and cap/ADV band are the partial substitute (a deviation). No financial-firm or ceq>0 exclusion except the log rule.

## 6. Predicted sign
SignalDoc `Sign = -1.0`: a high residual (high intangible return) predicts a LOW future return (long-term-reversal type); Cat.Economic long term reversal; Cat.Data Accounting; Cat.Form continuous; T-Stat 3.99; Stock Weight EW;
Portfolio Period 1; Start Month 6. Orientation: long LOW, `FactorDef(ascending=False)`.

## 7. The mass-point question
Do-nothing firm: there is no constant value: a firm with an unchanged book equity and price still gets `-(a + b1*BM_lag60 + b2*BMRet)` plus its return term, a continuous residual. Measured on the harness universe (market-scope regression,
per-month 1/99 trim of tempRet60), all 276 decision months checked for availability, 42 sampled months (every 6th plus extras, 2003-12 .. 2021-11) for shape:
- Scorable months: signals 1998-12-31 .. 2003-11-28 (60 months) empty (no t-60 cap); 2003-12-31 .. 2021-11-30 (216 months) score. Above the 120-month rebalance floor, so not a data_start case.
- Coverage of the universe (ART, 42 sampled scorable months): min 67.7%, mean 77.4%, max 82.5% (67.7% at 2021-11, 71.9% at 2020-12, 82.5% at 2012-12); 40% bar not at risk; the loss is names without a t-60 record or ceq <= 0 at t
  (equity non-positive on 4.8-15.6% of listed names with equity at t; 15.6% at 2021-11).
- Cross-sectional regression sample (all listed names with the three regressors): 2,773-3,908 names (mean 3,315); R2 0.11-0.93 (mean 0.60), b(BM_lag60) 0.08-0.71, b(BMRet) 0.31-1.07; the fit is unstable month to month.
- Modal share of the universe cross-section 0.064-0.072% (one name, every scored name distinct: about 1,400-1,570 distinct values per month on the 1,740-2,312-name universes of the coarser 24-month-step run); `qcut(10)` yields 10 bins in every sampled month. No tie handling needed.

## 8. History needed (snapshot starts 1998-01)
SEP closeadj from t-60 (first month-end 1997-12-31, so returns alone could start 2002-12), SF1 equity at t-60 (SF1 from 1997Q4 ok), DAILY.marketcap at t-60 (first 1998-12-01): binding, so the first scorable signal is 2003-12-31.
`history_months=60` (return-window factor, required), `lookback_months=60`. `fundamentals_at_month_ends` also carries the 15-month staleness tolerance at both ends.

## 9. OSAP metadata
IntanBM (Acronym2 IntanBM); Daniel and Titman 2006 JF; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form continuous; Cat.Data Accounting; Cat.Economic long term reversal; Sample 1968-2003;
Key Table "4 reg 3 r^I(B)"; Test "mv reg"; Evidence "t=4.0 in mv reg"; Sign -1.0; T-Stat 3.99; Stock Weight EW; Portfolio Period 1; Start Month 6; Filter `abs(prc)>5`; GScholar cites 1640.
Definition: "In each month, run a cross-sectional regression of a firm's five-year stock return on 5 year lagged BM (defined above) and a constructed regressor that is the change in BM from 5 years ago to today plus the five-year stock return. The residual from that regression is IntanBM."

## 10. Proposed Sharadar mappings and deviations
```
ceq        -> SF1 equity (ART), ctx.fundamentals_at_month_ends(["equity"], [0, 60], scope="market")   [compustat.ceq, approx]
mve_permco -> DAILY marketcap*1e6 at the signal date and at t-60 (ctx.at_month_ends(..., scope="market")) [crsp.mve_permco, approx; scale cancels in the intercept]
ret        -> SEP closeadj: ctx.market_context().monthly_closeadj(60): close[t]/close[t-60]-1         [crsp.ret, mapped]
BM = log(equity/cap) if > 0 ; Ret60 trimmed per month at 1/99 ; OLS Ret60 ~ 1 + BM60 + (BM - BM60 + Ret60) on the market cross-section ; residual -> universe IDs ; ascending=False
```
The regression is the signal's definition (precedent: Frontier's pooled regression); `harness.crosssection.ols_residual` exists. Deviations:
(a) book equity includes preferred stock (approx per ruling; also not Compustat ceq exactly); (b) company-level cap on the primary ticker; (c) OSAP's trim of tempRet60 uses percentiles of the WHOLE pooled sample (future
months included, a look-ahead): it cannot be reproduced point-in-time, so a per-month trim (or `harness.crosssection.cs_trim`) is used; (d) `abs(prc)>5` not applied (harness $1 floor instead); (e) fundamentals as known by `datekey`
(quarterly refresh) rather than annual + 6 months; (f) cumulative return is the calendar closeadj ratio, OSAP's runs over merged rows only (breaks at months without a Compustat link) and uses 0 for a NaN return;
(g) no delisting return; (h) regression sample is market-scope (as OSAP's all CRSP-Compustat firms), not the screened universe; (i) 60 calendar months, OSAP needs a row exactly 60 months back.
Fields not in the map: none. Recommendation: approx (translate with the stated deviations; first scorable decision month 2004-01).

## Addendum 2026-10-01 — route superseded (coordinator decision intanbm_me_source; alpha_review batch12 major)
Sections 1, 4, 7, 8 and 10 above describe the DAILY.marketcap route (first signal 2003-12-31, 216 scoring months). The translation uses ME = SEP.close x SF1.sharesbas at t and t-60 (as CompEquIss/EP; sharefactor not applied, declared), per-month cs_trim of Ret60, market-scope ols_residual, fxusd == 1 at both ends. Re-measured on this snapshot with the translated file (scratch preflight, harness universe): first scorable signal 2002-12-31 (47.4%; 2002-10/11 0%); 2003-03 onward 73-76%; June probes 2004-2021 69.1-82.1%. Scoring months 2002-12..2021-11 = 228 of 276 (above min_months 120).
