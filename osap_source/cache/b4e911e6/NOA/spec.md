# NOA — Net operating assets: (operating assets - operating liabilities) / lagged total assets (Hirshleifer, Hou, Teoh and Zhang 2004, JAE, Table 4)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/NOA.py` (cached `predictor.py`; upstream `upstream_CompustatAnnual.py`, `upstream_SignalMasterTable.py`). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml` (field_map.yaml detail for che, dc, mib, dltt, ceq). Measurements: harness universe, schedule 1999-01 .. 2021-12 (276 decision months), recorded snapshot, SF1 ART with `fundamentals_yoy`.

## 1. Data availability (verdict: APPROX — feasible with declared deviations; no input is missing)

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `at` | `compustat.at` | `assets` | mapped | not zero-filled; NaN -> NOA NaN |
| `che` | `compustat.che` | `cashneq + investmentsc.fillna(0)` | approx | ZERO-FILLED in OSAP |
| `dltt` | `compustat.dltt` | `debtnc` (gated `debtc.notna()`) | approx | not zero-filled; NaN -> NOA NaN |
| `mib` | `compustat.mib` | residual `assets - liabilities - equity` | approx | ZERO-FILLED in OSAP |
| `dc` (convertible debt; NOT deferred charges) | `compustat.dc` | none (SF1 has no convertible-debt field) | unavailable -> 0 | ZERO-FILLED in OSAP, so 0 is OSAP's own missing-case value |
| `ceq` | `compustat.ceq` | `equity` | approx | not zero-filled |
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt. The one missing input (dc) is zero-filled by OSAP itself, so the rule gives approx, not infeasible. `lt`/`liabilities` (`compustat.lt`, mapped) enters through the mib residual.
- ALGEBRA. OA = at - che; OL = at - dltt - mib - dc - ceq; OA - OL = dltt + mib + dc + ceq - che. With mib := assets - liabilities - equity and ceq := equity, equity cancels (mib + ceq = assets - liabilities), so `NOA = (debtnc + assets - liabilities - che + 0) / assets_lag`; SF1.equity is NOT an input.
- Unclassified balance sheets (financials/REITs, ~20% of ART rows) have null `debtnc`/`debtc`/`investmentsc`: never zero-filled (field_map ruling); `debtc.notna()` gate kept. `debtnc` null IS that block: coverage with and without the gate is the same (mean 77.52% vs 77.53%, median 78.05% both).

## 2. Variables (exact source names)
`at, che, dltt, mib, dc, ceq` (m_aCompustat); derived `OA, OL, l12_at, NOA`.

## 3. Formula in words and key lines
Operating assets (total assets less cash and short-term investments) minus operating liabilities (total assets less long-term debt, minority interest, convertible debt and book equity), over the prior-year total assets.
```
df["OA"] = df["at"] - df["che"]
df["OL"] = df["at"] - df["dltt"] - df["mib"] - df["dc"] - df["ceq"]
df["l12_at"] = df.groupby("permno")["at"].shift(12)
df["NOA"] = (df["OA"] - df["OL"]) / df["l12_at"]
```
Harness: `y = ctx.fundamentals_yoy(["assets","liabilities","debtnc","debtc","cashneq","investmentsc"])` (ART); `noa = (debtnc + (assets - liabilities) - (cashneq + investmentsc.fillna(0))) / assets_lag`, NaN where `assets_lag <= 0`, `debtnc` or `debtc` null, or cashneq null; inf -> NaN. The same-currency ratio needs no fxusd gate. Universe-member year-ago assets available for 48.4% (1998-12), ~89% (1999-03), median 96.9% of months thereafter.

## 4. Timing / lag convention
OSAP: fiscal-year balance sheet available datadate + 6 months, held; `l12_at` the prior fiscal year's `at`. Here: latest ART filing known at the signal (datekey <= signal, at most 15 months old) against assets of the same fiscal period a year earlier aligned by reportperiod (45-day tolerance). All inputs are balance-sheet LEVELS (ART == ARQ on the same reportperiod): no flow, no TTM smear, no dimension override; the 6-month availability lag is not reproduced (ART refreshes quarterly). Not a change signal, so the standing change-in-level tie rule does not apply.

## 5. Filters
None in the predictor (no SignalDoc Filter). Harness universe only.

## 6. Predicted sign
SignalDoc `Sign = -1.0` (LOW NOA is the long leg); Return 1.48; T-Stat 8.45. Orientation: `ascending=False`.

## 7. The mass-point question
Continuous ratio; no default value and no signal zero-fill. A do-nothing firm has no natural value (a nonzero ratio). Measured over 276 months: modal share of the scored cross-section 0.05%-0.12% (median 0.07%); distinct values equal n scored in all 276 months; exact zeros at most 1 name per month; qcut yields 10 bins in every month. Quantiles of the score (p1/p50/p99): 1999-12 -0.21/0.63/4.58; 2008-12 -0.20/0.61/2.00; 2020-12 -0.65/0.58/1.64 (the harness winsorises 1/99). No tie handling needed.

## 8. History needed and coverage (snapshot starts 1998-01)
Needs a year-ago filing: SF1 starts 1997Q4, so the first months are thin. Measured coverage of the universe (scored names): min 38.1% (1998-12-31, 868 of 2,281), 1999-01 39.6% (944 of 2,386), 1999-02 45.9%; >= 40% from 1999-02-26 (first preflight probe 1998-12-31 warns at 38.1%, not a hard fail; 2 of 276 months < 40%); after 1999-03: min 70.8%, mean 77.9%, max 82.2% (median 78.1% overall; 80.4% at 2010-06-30, 75.4% at 2021-11-30). Scored n min 868, median 1,474, max 2,099. The ~20% gap is the unclassified block: by sector at 1999-12 / 2008-12 / 2020-12 Financial Services are scored 10% / 13% / 13% and Real Estate 11% / 15% / 12% (25-35 names, above the 10-name within-sector floor); other sectors 69%-98%.

## 9. OSAP metadata
NOA; Hirshleifer et al. 2004 JAE; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form continuous; Cat.Data Accounting; Cat.Economic asset composition; Sample 1964-2002; Key Table "4 H-L"; Test "LS port size+BM+Mom adjusted"; Evidence "t=8.5 in long-short"; Sign -1.0; Return 1.48; T-Stat 8.45; EW; LS Quantile 0.1; Portfolio Period 1.0; Start Month 6.0; GScholar cites 1138. Definition: "Difference between operating assets and operating liabilities, scaled by lagged total assets. Operating assets are total assets (at) minus cash- and short-term investments (che), operating liabilities are total assets minus long-term debt (dltt), minority interest (mib), deferred charges (dc) and book equity (ceq)." (The upstream `dc` is convertible debt, not deferred charges.)

## 10. Proposed Sharadar mappings with deviations
```
y = ctx.fundamentals_yoy(["assets","liabilities","debtnc","debtc","cashneq","investmentsc"])   # ART
che = cashneq + investmentsc.fillna(0) ; num = debtnc + (assets - liabilities) - che
NOA = num / assets_lag.where(assets_lag > 0) ; NaN where debtc or debtnc null ; ascending=False ; lookback ~31 months
```
Deviations: (a) `dc` = 0 (OSAP's own missing-case value; convertible issuers differ, NOA here LOWER by dc, size unmeasurable); (b) `mib + ceq` -> `assets - liabilities`: preferred stock, redeemable NCI and temporary/SPAC equity, which OSAP leaves inside OL, sit on the financing side here, so NOA is HIGHER by those amounts (material only for the 2019-23 SPAC cohort and preferred issuers); (c) `dltt` -> `debtnc`, which includes non-current OPERATING-lease liabilities from FY2019 (ASC 842): a level step up for lessees from 2019-2021 filings that OSAP's dltt excludes (declared, not adjusted); (d) `che` = cashneq + investmentsc.fillna(0): overstates for captive-finance/vendor-financing names, understates for unclassified banks; (e) ART as-of-filing and 6-month lag not reproduced; (f) financials/REITs mostly NaN (10%-15% scored), 20% coverage loss; (g) no fxusd gate. Fields not in the map: none beyond dc (handled above).
Recommendation: **approx** — translate and preflight (expect a coverage warning at the first probe only).
