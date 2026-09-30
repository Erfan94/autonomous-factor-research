# IntanSP — Intangible return using sales-to-price: residual of the 5-year return on lagged SP and SP-change-plus-return (Daniel and Titman 2006, JF, Table 4)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/IntanSP.py` (the script `ZZ1_IntanBM_IntanSP_IntanCFP_IntanEP`, cached `predictor.py`, byte-identical across the four Intan* acronyms; SignalDoc row Acronym = IntanSP). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml` (+ field_map.yaml detail for ib, dp, csho); `IntanBM/spec.md` conventions reused. Only the IntanSP branch is documented.

## 1. Data availability (verdict: APPROX; constructible, first scorable signal 2002-12-31, 228 of 276 decision months score)

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `sale` (annual sales, m_aCompustat) | `compustat.sale` | SF1 `revenue` (ART TTM) | mapped | not zero-filled by OSAP: NaN -> NaN |
| `mve_permco` (company cap, months t and t-60) | `crsp.mve_permco` | SEP `close` x SF1 `sharesbas` at each month-end (both on today's split basis) | approx | NaN propagates |
| `ret` (monthly) | `crsp.ret` | SEP `closeadj` month-end ratio over 60 months | mapped (no delisting return) | NaN -> 0 inside an existing row |
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt; no book equity, so the book_equity_preferred_terms ruling does not arise (no preferred term).
- Reasons for APPROX: ME approx; per-month trim; regression sample; no other approximation (sale is mapped). Not infeasible, not data_start: SEP/SF1 history gives the first signal 2002-12-31 (t-60 = 1997-12-31), 228 scorable months.
- ME convention: SEP.close x SF1.sharesbas at t and t-60 (EP/EBM precedent; fxusd == 1 gate), as the IntanBM spec's 2026-10-01 addendum (coordinator decision intanbm_me_source) now also states; the body of `IntanBM/spec.md` still describes the superseded DAILY route.

## 2. Variables (exact source names)
`sale`, `mve_permco`, `ret`, `permno`, `gvkey`, `time_avail_m` (the sibling predictors' inputs are not used here). Derived: `tempAccSP`, `tempCumRet`, `tempRet60`, `tempAccSP_lag60`, `tempAccSPRet`, `tempU_tempAccSP` = IntanSP.

## 3. Formula in words and key lines
Each month, over all firms with data: regress the five-year stock return `tempRet60` on `X_lag60` (the ratio five years ago) and `XRet` = (X_t - X_lag60 + tempRet60), with an intercept. IntanSP is the firm's residual, the part of the five-year return unexplained by the change in the fundamental-to-price ratio (the "intangible return").
```
tempAccSP   = sale / mve_permco     # X = sale / mve_permco; ratio is a level, may be negative; no log, no positivity requirement
tempCumRet  = exp(cumsum(log(1+ret))) by permno ; ret NaN -> 0 ; over the rows of the m_aCompustat x SMT inner merge
tempRet60   = (CumRet_t - CumRet_{t-60})/CumRet_{t-60}       # calendar lag 60 via merge on time_avail_m - 60 months
winsor2(tempRet60, trim=True, cuts=[1,99])                   # NO by(): percentiles over the WHOLE pooled panel, all months
tempAccSPRet = tempAccSP - tempAccSP_lag60 + tempRet60
each month: OLS tempRet60 ~ const + tempAccSP_lag60 + tempAccSPRet on rows with all three present (>= 2 rows) -> residual
```
Only tempRet60 is trimmed; the regressors are not (OSAP), so a few extreme ratios can dominate the fit.

## 4. Timing / lag convention
OSAP: annual Compustat, available 6 months after the fiscal year-end and carried 12 months (m_aCompustat); X_t uses a stale flow over the month-t cap; X_lag60 is the same construction five years earlier.
Here: `ctx.fundamentals_at_month_ends([...], [0, 60], scope="market")` (as known by `datekey` at each month-end) and `ctx.at_month_ends("SEP", ["close"], [0, 60], scope="market")`; signal at the month-end, earned month t+1.
The flow is an ART TTM sum, a LEVEL at each date (equal to the annual figure at fiscal year-ends): X_t - X_lag60 is a five-year difference of two TTM levels, so there is NO four-quarter smear and no `dimension=ARQ` (ARQ would be a single quarter, a quarter-sized numerator). Default ART (IntanBM convention, quarterly refresh); `dimension="ARY"` mimics OSAP's annual cadence and raises early coverage (see section 7). 60 ROWS of returns in OSAP vs 60 calendar months here.

## 5. Filters
OSAP code: none; SMT shrcd 10/11/12, exchcd 1/2/3; gvkey present; one row per permno-month. SignalDoc Filter is BLANK for IntanSP (the published note removes the price filter): nothing to drop or to approximate; the harness $1 floor and cap/ADV band apply to the universe as for every factor.
Extra guards proposed: ME > 0 (close > 0 and sharesbas > 0), fxusd == 1 at t and t-60 (non-USD reporters <= 0.06% of members), non-finite -> NaN.

## 6. Predicted sign
SignalDoc `Sign = -1.0`: a high residual (high intangible return) predicts a LOW future return (long-term-reversal type); Cat.Economic long term reversal. Orientation: long LOW, `FactorDef(ascending=False)`.

## 7. The mass-point question
Do-nothing firm: there is no constant value. A firm with unchanged fundamentals and price still gets `-(a + b1*X_lag60 + b2*XRet)` plus its return term: a continuous residual; no zero-fill or floor makes a mass.
Measured on the harness universe (market-scope regression, per-month 1/99 trim of tempRet60 via `cs_trim`, OLS via `ols_residual`, ART; all 228 scorable months for coverage, 39 sampled months for the ib/dp diagnostics):
- Universe coverage of the scored residual (every decision month from signal 2002-12-31, 228 months): 38.1% (2002-12-31), 39.3% (2003-01-31), 40.5% (2003-02-28), 66.5% (2003-03-31), 67.2% (2003-04-30), 48.7% (2003-05-30), 47.7-54.8% through 2004-02-27, then 71.4-85.4% (mean 79.3%, 213 months 2004-03-31..2021-11-30).
  226 of 228 scorable months are >= 40%; both misses are the first two signal months. The dips are the t-60 flow: ART sale at t-60 exists for 24.5-27.0% of the market in signals 2002-12..2003-02, 53.6-56.1% in 2003-03/04, 36.7-46.8% in 2003-05..2004-02 and 67.7-73% afterwards (ART needs four quarters; SF1 starts 1997Q4); `ME` at t-60 is 35.6% (2002-12), 66-73% (2003-03..2003-12), 61-82% later, so the binding gate is the ART flow, not the price or share count.
  `dimension="ARY"` (annual filings, OSAP's own cadence) removes the early dips: 46.5%, 47.2%, 48.6%, 68.7%, 69.9%, 70.4%, then >= 71.4% in every sampled month through 2021-11 (37 sampled months; >= 46.5% throughout). Both dimensions proposed to the translator; ARY is OSAP-faithful, ART fresher. ME (close x sharesbas) is read from the same dimension in these runs.
- Regression sample (listed names with all three regressors, 213 months from 2004-03): 2,888-4,053 (mean ~3,350). R2 of the monthly regression 0.000-0.511 (median 0.009, 90th pct 0.058; 213 months from 2004-03); b(SP_lag60) -0.01..0.33, b(SPRet) -0.01..0.62: SP explains almost none of the five-year return here, so the residual is ~ the demeaned five-year return (the SignalDoc note: "the other coefficients in the regression are significant"). Extreme untrimmed SP values of microcaps are leverage points.
- Shape: distinct residuals 1,420-1,673 per month on 1,739-2,312 universe names (mean 1,878); modal share 0.06-0.07% (one name); `qcut(10)` yields 10 bins in every scorable month. No tie handling needed.

## 8. History needed (snapshot starts 1998-01)
SEP closeadj from t-60 (first month-end 1997-12-31, so returns alone allow 2002-12-31; signal months 1998-12..2002-11 have < 61 price columns and are empty: 48 of the 276 decision months), SF1 (1997Q4) flow at t-60 (binding for coverage, above), sharesbas at t-60. `history_months=60` (return-window factor, required), `lookback_months=60`. Above the 120-month rebalance floor (228 scorable months; 226 with coverage >= 40%).

## 9. OSAP metadata
IntanSP (Acronym2 IntanSP); Daniel and Titman 2006 JF; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 2_fair; Cat.Form continuous; Cat.Data Accounting; Cat.Economic long term reversal; Sample 1968-2003;
Key Table "4 r^I(S)"; Test "mv reg"; Evidence "t=4.3 in mv reg"; Sign -1.0; T-Stat 4.24; Stock Weight EW; Portfolio Period 12; Start Month 6; Filter blank; GScholar cites 1642.
Notes: "Not as clear as the other Intan* variables because the other coefficients in the regression are significant. We took the liberty to remove the price filter and categorize this as clear".
Definition: "In each month, run a cross-sectional regression of a firm's five-year stock return on 5 year lagged SP (defined above) and a constructed regressor that is the change in SP from 5 years ago to today plus the five-year stock return. The residual from that regression is IntanSP." 

## 10. Proposed Sharadar mappings and deviations
```
sale       -> SF1 revenue (ART or ARY), ctx.fundamentals_at_month_ends(["revenue","sharesbas","fxusd"], [0, 60], scope="market")   [compustat.sale, mapped]
mve_permco -> SEP close x SF1 sharesbas at t and t-60, both months via ctx; ME = close*sharesbas where close>0, sharesbas>0, fxusd==1   [crsp.mve_permco, approx]
ret        -> ctx.market_context().monthly_closeadj(60): close[t]/close[t-60]-1                                                     [crsp.ret, mapped]
sp = revenue / ME at t and t-60 ; Ret60 trimmed per month at 1/99 (cs_trim) ; OLS Ret60 ~ 1 + X60 + (X - X60 + Ret60) on the market cross-section (ols_residual) ; residual -> universe IDs ; ascending=False
```
The regression is the signal's definition (precedent: IntanBM, Frontier). Deviations: (a) cap is SEP close x sharesbas (company-level, share count steps at filings; DAILY.marketcap not used); (b) OSAP's trim of tempRet60 uses the WHOLE pooled sample (future months included, a look-ahead): a per-month trim is used; (c) `abs(prc)>5`/the published filter is not applied inside the factor; (d) fundamentals as known by `datekey` (quarterly ART refresh) rather than annual + 6 months; (e) cumulative return is the calendar closeadj ratio (OSAP's runs over merged rows only and uses 0 for NaN returns); (f) no delisting return; (g) regression sample is market scope (as OSAP's all CRSP-Compustat firms), not the screened universe; (h) 60 calendar months, OSAP needs a row exactly 60 months back; `ols_residual` requires >= 30 fitting rows (OSAP >= 2; never binding, samples >= 1,400); (i) the first 48 decision months are empty and two more are below the 40% coverage bar;
Fields not in the map: none. Recommendation: approx (translate with the stated deviations; consider dimension="ARY" for the early-coverage dips).
