# AM — Assets-to-market (Fama and French 1992, Table 3 Ln(A/ME))

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/AM.py` (cached
`predictor.py`, `signaldoc_row.csv`). DATA_SHA 198b281de1a0. field_map statuses are mappings,
not proofs, until the field-checker verifies them on this snapshot.

## 1. Data availability (verdict: FEASIBLE; one approx input, small)

| input (OSAP) | field_map key | Sharadar | field_map status | note |
|---|---|---|---|---|
| `at` (Compustat annual, `m_aCompustat`) | `compustat.at` | SF1 `assets` (ART) | mapped | raw USD level; null 0.05%; ART==ARQ for a level |
| `mve_permco` (SignalMasterTable, from CRSP monthly) | `crsp.mve_permco` | DAILY.marketcap on Primary-Class ticker, x1e6 -> `ctx.universe["mkt_cap_usd"]` | approx | company-level already; see deviations |
| `permno`/`time_avail_m` (SMT row presence) | `crsp.smt_row` | SEP price presence at month-end | mapped | only the inner-merge gate |

- Harness-side only: `crsp.me` (DAILY.marketcap millions, scaled once -> `mkt_cap_usd`), `crsp.prc`,
  `crsp.shrcd`, `crsp.exchcd` (universe). No IBES/options/13F/patents/segments/ratings/pensions/
  xad/emp/ob/ppegt; no OSAP zero-fill term. The only approx is the market-cap denominator.
- Fields for the field-checker (verify on THIS snapshot): `compustat.at` -> `assets`;
  `crsp.mve_permco` -> `mkt_cap_usd`; `crsp.smt_row` (only if the translator uses has_price_at).
  Optional: `assets` has no `*usd` variant; `fxusd` (key `compustat.curcd`) is needed only
  for non-USD reporters; measure the share of universe rows with `fxusd != 1` (expect ~0).

## 2. Variables (exact source names)

`at` (total assets, Compustat $ millions), `mve_permco` (company market value of equity,
$ millions: `shrout/1000 * |prc|` summed over permco, month t), `time_avail_m`, `permno`.

## 3. Formula

AM = at / mve_permco. Raw ratio, no log (Fama-French use ln; the log is monotone, so ranks,
deciles and rank-IC are identical). Key lines:
```
df = m_aCompustat[["permno","time_avail_m","at"]].drop_duplicates(["permno","time_avail_m"])
df = df.merge(SignalMasterTable[["permno","time_avail_m","mve_permco"]], how="inner")
df["AM"] = df["at"] / df["mve_permco"]
df.dropna(subset=["AM"])
```
Units cancel (OSAP: both $ millions; here both raw USD). High AM = cheap relative to assets.
OSAP does NOT guard `mve_permco <= 0` (division gives inf/NaN); the translator must guard
the denominator (`mkt_cap_usd.where(> 0)`). `at` <= 0 is ~0.01% of rows (data errors); treat
`at <= 0` as missing (OSAP would emit 0 or a negative ratio).

## 4. Timing and lag

- OSAP numerator: annual `at` for fiscal year ending `datadate`, made available at
  `datadate + 6 months`, then replicated for 12 months (offsets 0..11), latest datadate wins
  per (permno, month). So at month t the numerator is 6 to 17 months stale, and year-end only.
- OSAP denominator: `mve_permco` at month t itself (current month-end market value, no lag).
- Convention here: `ctx.fundamentals(["assets"])` with default ART at the signal as-of uses
  the latest filing with `datekey <= signal_asof` (10-K or 10-Q, TTM-form), within
  `max_fundamental_age_months` = 15. No extra 6-month lag (field_map `yoy_by_report_period`
  ruling: OSAP's lag is not reproduced). Numerator is therefore 0-3 months old (latest
  quarter-end balance), against OSAP's 6-17. This changes the signal materially only via
  growth in assets between the annual and latest-quarter balance sheets; rank correlation
  with OSAP's AM is expected high but not exact. Note it in the docstring.
- Flow smearing: none. `assets` is a balance-sheet LEVEL, ART==ARQ same-period on 99.10% of
  rows with both; no `dimension=ARQ` needed; nothing to difference year over year.
- Denominator: use `ctx.universe["mkt_cap_usd"]` at the signal date (DAILY.marketcap, month-end),
  NOT SF1.marketcap (filing date). This matches OSAP's month-t `mve_permco`.

## 5. Filters

SignalDoc `Filter`: none (blank). `Quantile Filter`: blank; `LS Quantile`: blank; OSAP
portfolios are equal-weighted (`Stock Weight` EW). No price or exchange filter in AM.py; the
harness universe (US common, NYSE/NASDAQ/NYSEMKT, price >= $1, cap/dollar-volume band)
applies. The financials are retained in OSAP (no SIC exclusion); within-sector ranking here
absorbs the high-AM financial/utility cluster.

## 6. Predicted sign

`Sign = 1.0`: higher AM predicts higher returns (SignalDoc t = 5.69, univariate regression,
1963-1990). Orientation: long high AM (D10), short low AM.
No flip.

## 7. Mass-point question

A do-nothing firm (no new filing) keeps `at` fixed but `mve_permco` moves with price monthly,
so AM changes continuously. No zero-fill default: a firm has `at` and a market cap or is
dropped. Exact ties negligible (continuous float ratio). Only mass point: `at == 0` (~0.01%
of non-null), treated as missing. Expected share at any single value ~0%. Ties: harness
default (average). Preflight should still confirm coverage near the universe.

## 8. History needed

No return-window or multi-period requirement: one latest filing plus current market cap.
`history_months` is not needed (no return-window). Filing needs coverage from the first
decision month (1999-01); SF1 ART has `assets` in breadth from 1997Q4, SEP/DAILY from
1997-12-31 / 1998-12-01 (DAILY min date), so the snapshot start (1998-01) suffices. The 15-month
age cap drops stale filers, a minor coverage leak vs OSAP's 18-month persistence.

## 9. OSAP metadata (SignalDoc)

Acronym AM; Cat.Signal Predictor; Cat.Form continuous; Cat.Data Accounting; Cat.Economic
valuation; Authors Fama and French; Year 1992; Journal JF; SampleStartYear 1963, End 1990;
Key Table "3 Ln(A/ME)"; Test univariate reg; Predictability 1_clear; Rep Quality 1_good;
Sign 1.0; Stock Weight EW; Portfolio Period 12; Start Month 6 (annual-lag convention).
Definition: total assets (at) divided by market value of equity.

## 10. Proposed Sharadar mappings and deviations
```
at         -> SF1 assets (ART via ctx.fundamentals(["assets"]))   [compustat.at, mapped]
mve_permco -> ctx.universe["mkt_cap_usd"] (DAILY.marketcap x1e6)  [crsp.mve_permco, approx]
AM         =  assets / mkt_cap_usd.where(mkt_cap_usd > 0), assets <= 0 -> NaN
```

Deviations:
1. Numerator freshness: latest filing (<= 3 months) vs OSAP's annual-plus-6-months (6-17
   months stale).
2. Denominator multi-class: Sharadar prices every share (incl. unlisted classes) at the
   Primary ticker's price with sharesbas all-class total; OSAP sums P_i*N_i over listed
   classes. Level error a few % on <=2% of universe names (field_map `crsp.mve_permco`).
   No summation, no harness change.
3. Non-USD reporters (if any): `assets` is in reporting currency; divide by `fxusd` (reporting
   units per 1 USD) only if the checker finds a non-trivial share; else ignore.
4. Sector-relative ranks remove the across-sector level (financials carry AM of 10+);
   within-sector AM is what is scored.

Fields NOT in the map: none. `FactorDef`: dimension default ART (no override), no
`history_months`, `family=None` until Phase C.
