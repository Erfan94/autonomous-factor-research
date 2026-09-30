# IntanEP — Intangible return using earnings-to-price: residual of the 5-year return on lagged EP and EP-change-plus-return (Daniel and Titman 2006, JF, Table 4)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/IntanEP.py` (the script `ZZ1_IntanBM_IntanSP_IntanCFP_IntanEP`, cached `predictor.py`, byte-identical across the four Intan* acronyms; SignalDoc row Acronym = IntanEP). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml` (+ field_map.yaml detail for ib, dp, csho); `IntanBM/spec.md` conventions reused. Only the IntanEP branch is documented.

## 1. Data availability (verdict: APPROX; constructible, first scorable signal 2002-12-31, 228 of 276 decision months score)

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `ni` (net income, m_aCompustat) | `compustat.ni` | SF1 `netinc` (ART TTM) | mapped (to parent, after NCI, before preferred dividends) | not zero-filled by OSAP: NaN -> NaN |
| `mve_permco` (company cap, months t and t-60) | `crsp.mve_permco` | SEP `close` x SF1 `sharesbas` at each month-end (both on today's split basis) | approx | NaN propagates |
| `ret` (monthly) | `crsp.ret` | SEP `closeadj` month-end ratio over 60 months | mapped (no delisting return) | NaN -> 0 inside an existing row |
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt; no book equity, so the book_equity_preferred_terms ruling does not arise (no preferred term).
- Reasons for APPROX: ME approx; per-month trim; regression sample; no other approximation (ni is mapped). Not infeasible, not data_start: SEP/SF1 history gives the first signal 2002-12-31 (t-60 = 1997-12-31), 228 scorable months.
- ME convention: SEP.close x SF1.sharesbas at t and t-60 (EP/EBM precedent; fxusd == 1 gate), as the IntanBM spec's 2026-10-01 addendum (coordinator decision intanbm_me_source) now also states; the body of `IntanBM/spec.md` still describes the superseded DAILY route.

## 2. Variables (exact source names)
`ni`, `mve_permco`, `ret`, `permno`, `gvkey`, `time_avail_m` (the sibling predictors' inputs are not used here). Derived: `tempAccEP`, `tempCumRet`, `tempRet60`, `tempAccEP_lag60`, `tempAccEPRet`, `tempU_tempAccEP` = IntanEP.

## 3. Formula in words and key lines
Each month, over all firms with data: regress the five-year stock return `tempRet60` on `X_lag60` (the ratio five years ago) and `XRet` = (X_t - X_lag60 + tempRet60), with an intercept. IntanEP is the firm's residual, the part of the five-year return unexplained by the change in the fundamental-to-price ratio (the "intangible return").
```
tempAccEP   = ni / mve_permco     # X = ni / mve_permco; ratio is a level, may be negative; no log, no positivity requirement
tempCumRet  = exp(cumsum(log(1+ret))) by permno ; ret NaN -> 0 ; over the rows of the m_aCompustat x SMT inner merge
tempRet60   = (CumRet_t - CumRet_{t-60})/CumRet_{t-60}       # calendar lag 60 via merge on time_avail_m - 60 months
winsor2(tempRet60, trim=True, cuts=[1,99])                   # NO by(): percentiles over the WHOLE pooled panel, all months
tempAccEPRet = tempAccEP - tempAccEP_lag60 + tempRet60
each month: OLS tempRet60 ~ const + tempAccEP_lag60 + tempAccEPRet on rows with all three present (>= 2 rows) -> residual
```
Only tempRet60 is trimmed; the regressors are not (OSAP), so a few extreme ratios can dominate the fit.

## 4. Timing / lag convention
OSAP: annual Compustat, available 6 months after the fiscal year-end and carried 12 months (m_aCompustat); X_t uses a stale flow over the month-t cap; X_lag60 is the same construction five years earlier.
Here: `ctx.fundamentals_at_month_ends([...], [0, 60], scope="market")` (as known by `datekey` at each month-end) and `ctx.at_month_ends("SEP", ["close"], [0, 60], scope="market")`; signal at the month-end, earned month t+1.
The flow is an ART TTM sum, a LEVEL at each date (equal to the annual figure at fiscal year-ends): X_t - X_lag60 is a five-year difference of two TTM levels, so there is NO four-quarter smear and no `dimension=ARQ` (ARQ would be a single quarter, a quarter-sized numerator). Default ART (IntanBM convention, quarterly refresh); `dimension="ARY"` mimics OSAP's annual cadence and raises early coverage (see section 7). 60 ROWS of returns in OSAP vs 60 calendar months here.

## 5. Filters
OSAP code: none; SMT shrcd 10/11/12, exchcd 1/2/3; gvkey present; one row per permno-month. SignalDoc Filter `abs(prc)>5` (portfolio-level; not in predictor.py): NOT applicable inside a factor (no universe filters in factors); the harness $1 floor and cap/ADV band are the partial substitute (a deviation). No EP > 0 requirement: loss makers are scored (the ratio is a level, no log).
Extra guards proposed: ME > 0 (close > 0 and sharesbas > 0), fxusd == 1 at t and t-60 (non-USD reporters <= 0.06% of members), non-finite -> NaN.

## 6. Predicted sign
SignalDoc `Sign = -1.0`: a high residual (high intangible return) predicts a LOW future return (long-term-reversal type); Cat.Economic long term reversal. Orientation: long LOW, `FactorDef(ascending=False)`.

## 7. The mass-point question
Do-nothing firm: there is no constant value. A firm with unchanged fundamentals and price still gets `-(a + b1*X_lag60 + b2*XRet)` plus its return term: a continuous residual; no zero-fill or floor makes a mass.
Measured on the harness universe (market-scope regression, per-month 1/99 trim of tempRet60 via `cs_trim`, OLS via `ols_residual`, ART; all 228 scorable months for coverage, 39 sampled months for the ib/dp diagnostics):
- Universe coverage of the scored residual (ART; every decision month from signal 2002-12-31, 228 months): 38.0% (2002-12-31), 39.2% (2003-01-31), 40.4% (2003-02-28), 66.5% (2003-03-31), 67.2% (2003-04-30), 48.6% (2003-05-30), 47.6-54.7% through 2004-02-27, then 71.4-85.4% (mean 79.3%, 213 months 2004-03-31..2021-11-30).
  226 of 228 scorable months are >= 40% (the misses are the first two signal months). The dips are the ART flow at t-60 (`ni` at t-60 exists for 24.5-27.0% of the market in signals 2002-12..2003-02, 53.6-56.1% in 2003-03/04, 36.7-46.8% in 2003-05..2004-02 and 67.7-73% afterwards; see IntanSP). `dimension="ARY"` gives 46.4%, 47.1%, 48.5%, 68.7%, 69.9%, 70.3% ... and >= 72.2% from 2004-03 in every sampled month (37 sampled months; >= 46.4% throughout). Both proposed: ARY is OSAP-faithful, ART fresher.
- Regression sample (listed names with all three regressors, 213 months from 2004-03): 2,888-4,053 (mean ~3,350). R2 of the monthly regression 0.001-0.951 (median 0.177, 90th pct 0.707; share of months with R2 > 0.8 = 6.1%; 213 months from 2004-03); b(EP_lag60) -0.65..0.90 (sign flips: 0.41 at 2003-12, -0.11 at 2004-06, -0.41 at 2004-12), b(EPRet) 0.00..0.92. A few untrimmed high-|EP| microcaps dominate some months' fit (OSAP trims only the return): unstable, reproduced as stated.
- Shape: distinct residuals 1,420-1,673 per month on 1,739-2,312 universe names (mean 1,878); modal share 0.06-0.07% (one name); `qcut(10)` yields 10 bins in every scorable month. No tie handling needed.

## 8. History needed (snapshot starts 1998-01)
SEP closeadj from t-60 (first month-end 1997-12-31, so returns alone allow 2002-12-31; signal months 1998-12..2002-11 have < 61 price columns and are empty: 48 of the 276 decision months), SF1 (1997Q4) flow at t-60 (binding for coverage, above), sharesbas at t-60. `history_months=60` (return-window factor, required), `lookback_months=60`. Above the 120-month rebalance floor (228 scorable months; 226 with coverage >= 40%).

## 9. OSAP metadata
IntanEP (Acronym2 IntanEP); Daniel and Titman 2006 JF; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form continuous; Cat.Data Accounting; Cat.Economic long term reversal; Sample 1968-2003;
Key Table "4 r^I(E)"; Test "mv reg"; Evidence "t=4.6 in mv reg"; Sign -1.0; T-Stat 4.64; Stock Weight EW; Portfolio Period 12; Start Month 6; Filter `abs(prc)>5`; GScholar cites 1640.
Definition: "In each month, run a cross-sectional regression of a firm's five-year stock return on the 5 year lagged EP = net income (ni)/market value of equity and a constructed regressor that is the change in EP from 5 years ago to today plus the five-year stock return. The residual from that regression is IntanEP." 

## 10. Proposed Sharadar mappings and deviations
```
ni         -> SF1 netinc (ART or ARY), ctx.fundamentals_at_month_ends(["netinc","sharesbas","fxusd"], [0, 60], scope="market")   [compustat.ni, mapped]
mve_permco -> SEP close x SF1 sharesbas at t and t-60, both months via ctx; ME = close*sharesbas where close>0, sharesbas>0, fxusd==1   [crsp.mve_permco, approx]
ret        -> ctx.market_context().monthly_closeadj(60): close[t]/close[t-60]-1                                                     [crsp.ret, mapped]
ep = netinc / ME at t and t-60 ; Ret60 trimmed per month at 1/99 (cs_trim) ; OLS Ret60 ~ 1 + X60 + (X - X60 + Ret60) on the market cross-section (ols_residual) ; residual -> universe IDs ; ascending=False
```
The regression is the signal's definition (precedent: IntanBM, Frontier). Deviations: (a) cap is SEP close x sharesbas (company-level, share count steps at filings; DAILY.marketcap not used); (b) OSAP's trim of tempRet60 uses the WHOLE pooled sample (future months included, a look-ahead): a per-month trim is used; (c) `abs(prc)>5`/the published filter is not applied inside the factor; (d) fundamentals as known by `datekey` (quarterly ART refresh) rather than annual + 6 months; (e) cumulative return is the calendar closeadj ratio (OSAP's runs over merged rows only and uses 0 for NaN returns); (f) no delisting return; (g) regression sample is market scope (as OSAP's all CRSP-Compustat firms), not the screened universe; (h) 60 calendar months, OSAP needs a row exactly 60 months back; `ols_residual` requires >= 30 fitting rows (OSAP >= 2; never binding, samples >= 1,400); (i) the first 48 decision months are empty and two more are below the 40% coverage bar;
Fields not in the map: none. Recommendation: approx (translate with the stated deviations; consider dimension="ARY" for the early-coverage dips).
