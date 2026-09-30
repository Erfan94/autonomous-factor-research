# DelNetFin — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: APPROX (constructible; 70-80% coverage; `pstk` term dropped; lease and ivst deviations)
| OSAP var | field_map key | Sharadar | status |
|---|---|---|---|
| `ivst` | compustat.ivst | SF1 `investmentsc` | approx (captive-finance receivables overstate ivst for CSCO/F/GM/IBM/HPE/HOG) |
| `ivao` | compustat.ivao | SF1 `investmentsnc` | approx (includes equity-method investments) |
| `dltt` | compustat.dltt | SF1 `debtnc` | approx, verified-with-deviation 2026-09-30: includes operating leases from ASC 842 (FY2019 calendar filers) |
| `dlc` | compustat.dlc | SF1 `debtc` | mapped, verified-with-deviation 2026-09-30 (null ~20%, same unclassified block) |
| `pstk` | compustat.pstk | none (unavailable) | DROPPED: OSAP itself does `tempPSTK = pstk.fillna(0)` |
| `at` | compustat.at | SF1 `assets` | mapped, verified 2026-09-30 |
- Rule: a missing item that OSAP zero-fills is dropped and the row is approx. Dropping `pstk` leaves the signal defined
  (and firms without preferred stock, the majority, are unaffected); firms with preferred outstanding get net financial
  assets overstated by pstk and a change that omits preferred issuance/retirement.
- OSAP zero-fills `ivst` and `ivao`; it does NOT zero-fill `dltt`/`dlc`. Here the `investmentsc`/`investmentsnc`/`debtc`/`debtnc`
  null blocks are 100%-coincident with `assetsc` null (unclassified balance sheets: 71% Financial Services, 20% Real Estate),
  so those names are null here (no zero-fill), a ~20% structural gap.
- No IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob or ppegt input.

## 2. Variables (predictor.py)
`m_aCompustat`: gvkey, permno, time_avail_m, `at`, `pstk`, `dltt`, `dlc`, `ivst`, `ivao` (annual FUNDA; `ivst`, `ivao` zero-filled upstream).

## 3. Formula
```
tempPSTK = pstk.fillna(0)
temp     = (ivst + ivao) - (dltt + dlc + tempPSTK)      # net financial assets
tempAvAT = 0.5 * (at + l12_at)                          # l12 = same permno, time_avail_m - 12 months
DelNetFin = (temp - l12_temp) / tempAvAT                # dropna
```
Change in net financial assets (financial assets minus debt and preferred) over average total assets.

## 4. Timing / lag
- OSAP: `time_avail_m = datadate + 6 months`, held 12 months (6-17 months stale); 12-month lag by date-merge.
- Sharadar: all inputs are LEVELS (stocks; ART == ARQ same-period, no TTM smear; no flow item, so `dimension` stays ART and
  nothing needs ARQ). Year-ago via `ctx.fundamentals_yoy([...], years=1)` (report-period aligned, tol 45 days), never `lag_months=12`.
  ART-as-of-filing makes the change a rolling 4-quarter difference refreshed quarterly, 0-3 months old, not an annual-FYE change.
- **Lease trap (in-window)**: `debtnc`/`debtc` (SF1 `debt` includes operating-lease obligations) absorb ASC 842 lease
  liabilities from FY2019 filings (FY2018 for early adopters). The 12-month change shows a one-off negative step for lessees in
  FY2019-20 filings, a cross-sectional lessee-vs-non-lessee artefact (not a financing decision). Measured on the universe: median
  DelNetFin -0.0106 (2015-12) -> -0.0338 (2019-12) -> -0.0122 (2020-12); `debtnc` exact-zero share 12.7% (2018-12) -> 3.9% (2019-12).
  About 24-36 decision months (2019-2020 filings) are affected; no alternative lease-free field exists in SF1.

## 5. Filters
SignalDoc Filter and Quantile Filter blank; predictor.py none. Harness universe applies. `avgAT > 0` guard here (OSAP has none).

## 6. Predicted sign
`Sign = +1.0` (Richardson et al. 2005, Table 8B DeltaFin, univariate reg t = 5.85): firms increasing net financial assets earn more;
long high, short low.

## 7. Mass-point question
Continuous ratio of differences of USD levels. Do-nothing firm (no change in any of the four legs) = exactly 0. Measured exact-zero
share of scored names 1.5% (1999-01), 2.2% (1999-12), 1.9% (2008-12), 1.9% (2015-12), 0.6% (2019-12, 2020-12): below the
5% warn line, no decile collapse. Ties: harness average rank.

## 8. History needed (snapshot starts 1998-01)
Latest filing plus the same fiscal period a year earlier. Universe coverage (scored / universe): 39.2% at 1999-01 (year-ago
assets only 49.8% available; SF1 starts 1997Q4), 70.3% 1999-03, 73.2% 1999-06, 70.3% 1999-12, 79.0% 2003-12, 80.0% 2008-12,
76.5% 2015-12, 76.7% 2019-12, 75.9% 2020-12. First decision month 1999-01 is thin (39%); later months clear the 40% bar
(no inherited pre-1999 data). No `history_months`.

## 9. OSAP metadata
Richardson et al. (2005), JAE; Cat.Data Accounting; Cat.Economic investment alt; continuous; sample 1962-2001; Acronym2 DelNetFin;
Portfolio Period 12, Start Month 6; EW; Key Table 8B DeltaFin, univariate reg; 1_clear / 1_good. Source
`Signals/pyCode/Predictors/DelNetFin.py`. SignalDoc: "sum of short-term investments (ivst) and investments and advances (ivao) minus
long-term debt (dltt), debt in current liabilities (dlc) and preferred stock capital, change scaled by average total assets."

## 10. Proposed Sharadar mappings
```
nf  = investmentsc + investmentsnc - debtnc - debtc        # all four non-null, else NaN (never zero-fill)
DelNetFin = (nf - nf_lag) / (0.5*(assets + assets_lag))    # fundamentals_yoy(years=1), avgAT > 0, fxusd == 1
```
Fields: `investmentsc`, `investmentsnc`, `debtnc`, `debtc`, `assets` (all in the field map). Deviations: `pstk` dropped; `investmentsc`
overstated for captive-finance filers; `investmentsnc` includes equity-method investments; `debtnc`/`debtc` include operating leases
from FY2019; ART quarterly refresh; ~20% structural null block where OSAP (zero-fill of ivst/ivao) would still score
financials. Alternatives `debt` (= debtc + debtnc, 99.99%) give nothing extra.
