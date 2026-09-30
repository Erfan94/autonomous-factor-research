# NetDebtFinance — Net debt financing: (long-term debt issued - reduced + change in current debt) / average total assets (Bradshaw, Richardson and Sloan 2006, JAE, Table 3)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/NetDebtFinance.py` (cached `predictor.py`, `NetDebtFinance.do`; upstream `upstream_CompustatAnnual.py`, `upstream_SignalMasterTable.py`). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml` (field_map.yaml detail for dltis, dltr, dlcch). Measurements: harness universe, schedule 1999-01 .. 2021-12 (276 decision months), recorded snapshot, SF1 ART with `fundamentals_yoy`.

## 1. Data availability (verdict: APPROX — the numerator maps exactly as a net flow; a tie rule is required)

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `dltis` (LT debt issuance) | `compustat.dltis` | `ncfdebt` (NET debt flow, issuance - repayment, incl. short-term/CP net change) | approx | not zero-filled; NaN -> NaN |
| `dltr` (LT debt reduction) | `compustat.dltr` | same column | approx | not zero-filled; NaN -> NaN |
| `dlcch` (current debt change) | `compustat.dlcch` | subsumed in `ncfdebt` (no standalone field) | unavailable alone | filled 0 by the predictor itself |
| `at` | `compustat.at` | `assets` | mapped | not zero-filled |
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt. What the construction needs is the SUM `dltis - dltr + dlcch` (the code adds dlcch; SignalDoc text says "minus current debt changes"; the code is the authority), which is exactly the net debt cash flow. field_map: "exact for OSAP's sum, not usable for one gross side". The gross items are not needed, so this is approx (not infeasible): OSAP zero-fills only dlcch, which the net sum already contains, and leaves dltis/dltr un-filled (missing -> NaN), matching `ncfdebt` null -> NaN here (never zero-filled).
- NO `debtc` gate on this predictor: OSAP has no dltt/dlc term. `ncfdebt` is populated for the unclassified block (95% of the ~370 debtc-null names scored before the tie rule; by sector at 1999-12 / 2008-12 / 2020-12 Financial Services 82% / 88% / 88%, Real Estate 95% / 95% / 97%, after the tie rule). `SF1.debt` is not an input under the recommended rule.

## 2. Variables (exact source names)
`gvkey, permno, time_avail_m, dlcch, dltis, dltr, at` (m_aCompustat); derived `l12_at`, `NetDebtFinance`.

## 3. Formula in words and key lines
Net long-term debt raised plus the change in current debt, scaled by the average of total assets this year and last year; set to missing if the absolute ratio exceeds 1.
```
df["dlcch"] = df["dlcch"].fillna(0)
df["NetDebtFinance"] = (dltis - dltr + dlcch) / (0.5 * (at + l12_at))
df.loc[df["NetDebtFinance"].abs() > 1, "NetDebtFinance"] = np.nan
```
Harness: `y = ctx.fundamentals_yoy(["ncfdebt","assets"])` (ART); `avg = (assets + assets_lag)/2`; `ratio = ncfdebt / avg.where(avg > 0)`; `abs(ratio) > 1 -> NaN` (measured: drops 0.00%-0.50% of the universe, median 0.09%); inf -> NaN.

## 4. Timing / lag convention
OSAP: annual flow and assets, available datadate + 6 months, held; `l12_at` prior fiscal year's assets. Here: ART `ncfdebt` is a TTM (rolling four-quarter) flow refreshed quarterly (field_map: ART == sum of 4 ARQ within 1% on 99.63% of rows; ARY == ART at fiscal year-end on 99.97%), so the numerator spans the same 12 months as the annual item at each fiscal year-end; the denominator averages the latest ART assets and the year-ago period aligned by reportperiod. It is a flow LEVEL, not a year-over-year difference of a flow, so nothing smears under TTM; do NOT set `dimension=ARQ` (one quarter's flow over a year's average assets). The 6-month availability lag is not reproduced.

## 5. Filters
None beyond the `abs > 1` exclusion (no SignalDoc Filter). Harness universe only.

## 6. Predicted sign
SignalDoc `Sign = -1.0` (LOW net debt financing is the long leg); Return 0.675; T-Stat 6.91. Orientation: `ascending=False`.

## 7. The mass-point question (measured over 276 months; this is the decisive section)
A do-nothing firm (no net debt flow) produces exactly 0.0; `ncfdebt == 0` is 15.4% of non-null ART rows pooled, rising over time, and 99.9% of zero rows have operating cash flow present (true no-activity and vendor 0-fill are not separable). Three tie options, all measured on the harness universe:
1. LITERAL (zeros kept): 0.0 is the modal value in all 276 months, share of the scored cross-section 7.9%-13.6% (median 10.5%); >= 10% in 201 of 276 months; qcut gives 9 bins in 15 of 276 months. Probe months: 1998-12-31 7.9%, 2010-06-30 13.2%, 2021-11-30 11.0%. HARD preflight failure (mass point). Not usable.
2. STANDING-RULE ANALOG (NaN where debt, `SF1.debt`, is exactly 0 at BOTH year-ends): removes 7.5% (median) of the scored names; remaining modal share 2.1%-10.3% (median 3.9%), >= 5% in 38 months (2006-07 3, 2019 9, 2020 12, 2021 11), >= 10% in 2 (2020-03 10.3%, 2020-04 10.0%), last probe 2021-11-30 9.5% (first probe 2.4%, middle 4.7%). The leftover zeros are firms with debt but zero net flow (median 3.5% of scored, up to 10.1%). A near-miss at the last probe and a cliff in two window months; debt-level users also need the debtc gate. Not recommended.
3. RECOMMENDED: NaN where `ncfdebt == 0` exactly (a zero flow is structural, not information; vendor 0-fill is inseparable). Modal share 0.05%-0.12% (median 0.06%), 10 bins in every month, no month near 5%; the tie rule leaves no residual mode. Loses 10.5% of the scored names (median).
Continuous otherwise (non-zero ratios are distinct; no other default).

## 8. History needed and coverage (snapshot starts 1998-01)
Needs a year-ago assets filing (SF1 from 1997Q4: 48% of the universe at 1998-12, ~89% from 1999-03). Coverage of the universe: raw (before tie rule) min 47.1% (1998-12), median 96.4%, mean 95.0%, 0 months < 40%; RECOMMENDED rule min 43.4% (1998-12), median 85.7%, mean 84.8%, max 89.1%, 74.5%-89.1% from 1999-03 (probes: 43.4% 1998-12-31, 84.6% 2010-06-30, 81.6% 2021-11-30), 0 months < 40%; scored n 990-2,176 (median 1,636). `ncfdebt` itself is null for 3.0% of the universe (median; >10% in 18 months, all 1998-12..2000-11, where the cash-flow statement is missing).

## 9. OSAP metadata
NetDebtFinance (Acronym2 NDebtFin); Bradshaw, Richardson, Sloan 2006 JAE; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form continuous; Cat.Data Accounting; Cat.Economic external financing; Sample 1971-2000; Key Table 3; Test port sort size adjusted; Evidence "t=6.9 in port sort"; Sign -1.0; Return 0.675; T-Stat 6.91; EW; LS Quantile 0.1; Portfolio Period 12.0; Start Month 6.0; GScholar cites 798. Definition: "Long-term debt issuance (dltis) minus long-term debt reduction (dltr) minus current debt changes (dlcch), scaled by average total assets (at) in years t-1 and t. Replace missing values of dlcch with 0. Exclude if ratio is greater than 1."

## 10. Proposed Sharadar mappings with deviations
```
y = ctx.fundamentals_yoy(["ncfdebt","assets"])        # ART
avg = (assets + assets_lag)/2 ; ratio = ncfdebt / avg.where(avg > 0)
score = ratio.where(ratio.abs() <= 1).where(ncfdebt != 0)    # tie rule: exact-zero net flow -> NaN
ascending=False ; lookback ~31 months ; dimension=None (ART)
```
Deviations: (a) gross `dltis`/`dltr` collapse onto net `ncfdebt` (exact for the sum; ncfdebt includes the short-term/CP leg that dlcch carries); (b) exact-zero net flow -> NaN (tie rule, option 3; drops 10.5% of the scored); (c) ART TTM rolling flow and year-ago assets by reportperiod, not annual values with a 6-month lag; (d) avg assets > 0 guard added; (e) the vendor may 0-fill an absent flow (inseparable, stated); (f) no fxusd gate (same-currency ratio). Fields not in the map: none.
Recommendation: **approx** — translate with tie option 3 and preflight; the literal construction fails the mass-point check.
