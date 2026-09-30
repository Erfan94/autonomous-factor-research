# CashProd — Cash productivity (Chandrashekar and Rao 2009, Table 4A)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/CashProd.py` (cached
`predictor.py`, `signaldoc_row.csv`; upstream read from `Accruals/upstream_*.py`). DATA_SHA
198b281de1a0; statuses from `field_map_index.yaml`.

## 1. Data availability (verdict: APPROX; constructible, no unavailable input)

| input (OSAP) | field_map key | Sharadar | status | note |
|---|---|---|---|---|
| `at` (m_aCompustat) | `compustat.at` | SF1 `assets` (ART level) | mapped, verified 2026-09-30 | null 0.05%, exact-zero 0.01% of non-null (data errors) |
| `che` (m_aCompustat) | `compustat.che` | SF1 `cashneq + investmentsc.fillna(0)` (ART level) | APPROX, verified 2026-09-30 | che null only where cashneq null (universe coverage 97.5% 1999, 99.8% 2008, 100% 2020-21); exact-zero 1.06%/0.88%/0.34%/0.24%/0.17% of non-null at 1998-12/1999/2008/2020/2021 |
| `mve_permco` (SignalMasterTable) | `crsp.mve_permco` | DAILY.marketcap on the Primary-Class ticker -> `ctx.universe["mkt_cap_usd"]` (raw USD) | approx, verified 2026-09-30 | company-level already; `>0` on 100% of members |
| `permno`/`time_avail_m` (SMT inner-merge row) | `crsp.smt_row` | SEP price presence at month-end | mapped | gate only |

No IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob, ppegt; no Compustat item
Sharadar lacks. Approximations: (a) `che` (Compustat che = cash + current securities, reproduced;
but investmentsc overshoots for vendor/captive-finance filers CSCO, F, GM, IBM, HPE, HOG and is null,
so che = cashneq, for the unclassified financial/REIT block); (b) `mve_permco` multi-class pricing
(section 10). Recommend: **approx** (constructible). Fields cashneq/investmentsc/assets already verified.

## 2. Variables (exact source names)

`at` (total assets, $M), `che` (cash and short-term investments, $M), `mve_permco` (company market
value of equity, $M, month t: `prc*shrout` summed over permco), `permno`, `time_avail_m`.
SignalDoc text says `mve_c`; the code uses `mve_permco` (company level) and is the authority.

## 3. Formula

CashProd = (mve_permco - at) / che. Raw ratio, no log, no scaling; units cancel. Key lines:
```
df = m_aCompustat[["permno","time_avail_m","at","che"]].drop_duplicates(["permno","time_avail_m"])
df = df.merge(SignalMasterTable[["permno","time_avail_m","mve_permco"]], how="inner")
df["CashProd"] = (df["mve_permco"] - df["at"]) / df["che"]
```
In words: market value of equity above book assets, per dollar of cash. Unbounded: negative when
mve < at, explodes as che -> 0.

## 4. Timing and lag

- OSAP: annual `at`, `che` at `datadate + 6 months` (`time_avail_m`), replicated 12 months, latest
  datadate wins: balance items 6-17 months stale; `mve_permco` at month t (no lag). Upstream also
  drops annual rows with missing `at`, `prcc_c` or `ni`; not reproduced (no `prcc_c` in Sharadar).
- Here: `ctx.fundamentals(["assets","cashneq","investmentsc"])`, default ART as-of (latest filing
  with datekey <= signal as-of, within `max_fundamental_age_months` = 15); no extra 6-month lag
  (`yoy_by_report_period` ruling). Balance items are 0-3 months old vs OSAP's 6-17, so the ratio
  tracks the latest quarter's cash and assets against the current cap; rank correlation with OSAP's
  CashProd expected high, not exact.
- Flow smearing: none. All three inputs are balance-sheet LEVELS (ART == ARQ same-period on 99.96%
  cashneq, 99.98% investmentsc, 99.10% assets). No `dimension=ARQ` needed; nothing differenced year
  over year.
- Denominator side: use `ctx.universe["mkt_cap_usd"]` at the signal date (DAILY.marketcap at the
  month-end), NOT SF1.marketcap (filing-date). Matches OSAP's month-t `mve_permco`.

## 5. Filters

SignalDoc `Filter`: blank; `Quantile Filter`: blank; `LS Quantile`: blank; `Stock Weight` EW.
No price, exchange or SIC filter in CashProd.py (financials retained). Harness universe applies
(US common, NYSE/NASDAQ/NYSEMKT, price >= $1, cap/dollar-volume band). Within-sector ranks here
neutralise the sector-level tilt (financials carry very low `che`, very different mve-at).

## 6. Predicted sign

SignalDoc `Sign = -1.0`: higher CashProd predicts LOWER returns (reported t = 3.6, regression of
returns on the characteristic, sample 1963-2003, "Stats are from WP version"). Orientation: long
LOW CashProd (D1 side), short HIGH CashProd; the translator flips the raw ratio (score = -CashProd
or equivalent). The flip is the published orientation, not a second hypothesis.

## 7. The mass-point question

A do-nothing firm (no new filing) keeps `at`, `che` fixed while `mve_permco` moves monthly, so
CashProd changes continuously; no default value. Mass points only at the `che` denominator:
- OSAP ZERO-FILLS `che` (`zero_fill_vars` in upstream CompustatAnnual.py), so missing che -> 0 and
  (mve-at)/0 = +/-inf in OSAP (no guard; `save_predictor` drops only nulls), i.e. those firms sit at
  the rank extremes.
- Here: `che` null (0.04%), `che <= 0` (exact-zero 0.17-1.06% of universe) -> NaN, not inf. Also
  `mkt_cap_usd > 0` (DAILY exact-zero 0.063%), `at > 0` guards. Emitted scores: no mass point;
  ~0.2-1% of names dropped. Ties: harness default (average); float ties negligible. Tiny-che
  names give extreme |CashProd|; the rank transform contains them.

## 8. History needed

One filing plus current cap; no return window, so no `history_months`. SF1 ART levels ~99.9% from
1997Q4, DAILY marketcap from 1998-12-01 (first month-end 1998-12-31), SEP from 1997-12-31; the
snapshot start 1998-01 and first decision month 1999-01 are covered. Coverage in 1998-12 che is
98.8% of universe, 1999 97.5%. The 15-month age cap drops stale filers (minor leak vs
OSAP's 18-month persistence).

## 9. OSAP metadata (SignalDoc)

Acronym CashProd; Cat.Signal Predictor; Cat.Form continuous; Cat.Data Accounting; Cat.Economic
`profitability alt`; Authors Chandrashekar and Rao; Year 2009; Journal WP; SampleStartYear 1963,
End 2003; Key Table `4A \eta`; Test `mv reg`; Predictability 1_clear; Rep Quality 1_good;
Sign -1.0; T-Stat 3.6; Stock Weight EW; Portfolio Period 1; Start Month 6. Definition: (mve - at) / che.

## 10. Proposed Sharadar mappings and deviations
```
at         -> SF1 assets (ART)                                         [compustat.at, mapped]
che        -> SF1 cashneq + investmentsc.fillna(0) (ART)               [compustat.che, approx]
mve_permco -> ctx.universe["mkt_cap_usd"] (DAILY.marketcap x1e6)       [crsp.mve_permco, approx]
CashProd   =  (mkt_cap_usd.where(>0) - assets.where(>0)) / che.where(>0);  score = -CashProd
```
Deviations:
1. Timing: latest filing (0-3 months old) vs OSAP annual + 6 months (6-17 months).
2. `che`: SF1 cashneq + investmentsc (Compustat definition reproduced for industrials) but
   investmentsc includes financing/loan receivables for CSCO, F, GM, IBM, HPE, HOG (che too high)
   and is null (-> che = cashneq, too low) for 85-92% of the unclassified financial/REIT block.
   Measured: Spearman(cashneq/assets, che/assets) 0.91-0.96 in non-financials, so using cashneq alone
   would move ~40-50% of names across deciles; cashneq-only is NOT used.
3. OSAP zero-fill of `che` (missing -> 0 -> +/-inf) is replaced by NaN (no inf scores); share
   affected ~0.2-1% exact-zero plus ~0.04% null.
4. `mve_permco`: DAILY.marketcap = primary close x SF1.sharesbas (all-class cover total) x
   sharefactor; other classes priced at the primary's price, unlisted classes included; OSAP sums
   P_i N_i over listed classes. Level error a few % on <= 2% of names.
5. Upstream `at/prcc_c/ni` non-null row filter not reproduced.
6. Non-USD reporters: `assets`, `cashneq`, `investmentsc` are in reporting currency, mkt_cap in
   USD. Field-checker measures the `fxusd != 1` share (expect ~0); if material, use `/ fxusd`.

Fields NOT in the map: none. `FactorDef`: dimension default ART (no override), no `history_months`,
`family=None` until Phase C, orientation lower-is-better.
