# CF — Cash flow to market (Lakonishok, Shleifer, Vishny 1994, Table 6 panel 1)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/CF.py` (cached `predictor.py`,
`signaldoc_row.csv`; upstream files read from `../Accruals/`). DATA_SHA 198b281de1a0. Construction only.

## 1. Data availability (verdict: APPROX, constructible; two inputs, one OSAP zero-fill)
| input (OSAP) | field_map key | Sharadar | field_map status | note |
|---|---|---|---|---|
| `ib` (income before extraordinary items, `m_aCompustat`) | `compustat.ib` | SF1 `netinccmn` (ART TTM flow) | mapped, verified_on "" (prior-snapshot probe 2026-09-25) | needs the field-checker on THIS snapshot |
| `dp` (depreciation and amortisation, `m_aCompustat`) | `compustat.dp` | SF1 `depamor` (ART TTM flow) | mapped, verified_on 2026-09-30 | cash-flow add-back, not the income-statement line |
| `mve_permco` (SignalMasterTable, CRSP) | `crsp.mve_permco` | DAILY.marketcap x1e6 -> `ctx.universe["mkt_cap_usd"]` | approx, verified_on 2026-09-30 | company-level already |

- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt needed.
- OSAP ZERO-FILL: `dp` is in `zero_fill_vars` of upstream `CompustatAnnual.py` (line ~139-145),
  so a firm with `ib` but no `dp` still gets CF = ib/mve. `ib` is NOT zero-filled (missing ib -> NaN).
  This is the reason for `approx`, not `infeasible`: the translator must replicate dp NaN -> 0.
- Measured (field_map `compustat.dp`, 2026-09-30): ART depamor null 9.64% overall, exact-zero 3.79% of
  non-null (universe 1.6-2.6%). Early window: ART depamor null 58.1/54.7/53.7% at calendardate
  1998Q1/Q2/Q3, 3.1% 1998Q4, ~9% 1999Q1-Q2; universe PIT coverage of ART depamor 52.0% (1998-12-31),
  53.1% (1999-01), 58.6% (1999-02), 93.2% (1999-03), 96.7% (1999-04). ART netinccmn null 7.9% (1999),
  3.5% (2008), 6.6% (2020) on prior-snapshot probes; its early-1998 TTM pattern is not measured here.
  Because dp is zero-filled, the dp hole does not drop names; the ib hole does (see section 4).
- Fields for the field-checker on THIS snapshot: `compustat.ib` -> `netinccmn` (null/zero/units, early
  1998 TTM null share under ART vs ARY, netinc vs netinccmn differ 12.1% of ART rows, gap = prefdivis);
  `crsp.mve_permco` (already verified). `compustat.dp` already verified 2026-09-30.
  `fxusd` (`compustat.curcd`): numerator is reporting currency, denominator USD; if a material share of
  universe rows has `fxusd != 1`, divide both flows by `fxusd` (no `depamorusd` exists).

## 2. Variables (exact source names)
`ib` (Compustat annual, $ millions), `dp` (Compustat annual, $ millions, zero-filled),
`mve_permco` (company market equity, $ millions, month t), `permno`, `time_avail_m`.

## 3. Formula
CF = (ib + dp) / mve_permco; net income plus depreciation over market equity ("cash flow to price").
Raw ratio, high = cheap. Key lines:
```
df = m_aCompustat[["gvkey","permno","time_avail_m","ib","dp"]].drop_duplicates(["permno","time_avail_m"])
df = df.merge(SignalMasterTable[["permno","time_avail_m","mve_permco"]], how="right")
df["cash_flow"] = df["ib"] + df["dp"]
df["CF"] = np.where(df["mve_permco"] == 0, np.nan, df["cash_flow"] / df["mve_permco"])
```
Right merge keeps every SMT row; unmatched rows are NaN. `ib` NaN -> NaN; `dp` NaN was 0 upstream.
Negative cash flow is kept (~33% of ib negative; not trimmed).

## 4. Timing and lag
- OSAP: annual `ib`, `dp` (fiscal year ending `datadate`) available at `datadate + 6 months`, held 12
  months, latest wins: numerator 6-17 months stale; denominator month-t `mve_permco`, no lag.
- Here: `ctx.fundamentals(["netinccmn","depamor"])`, default ART, latest filing with
  `datekey <= signal_asof`, within `max_fundamental_age_months` = 15. No extra 6-month lag
  (field_map `yoy_by_report_period` ruling). Numerator is a TTM sum ending at the latest quarter,
  0-3 months old, against OSAP's fiscal-year figure 6-17 months old. The signal differs from OSAP by
  the last 1-3 quarters of earnings growth; rank correlation expected high, not exact.
- Both flows are TTM; CF needs no year-over-year difference, so no `dimension=ARQ`, no smearing. ib and dp
  MUST be read on the same dimension.
- Early-window thinness (measured, `compustat.dp`): ART needs four quarters of SF1 history and SF1
  starts 1998, so 1998Q1-Q3 TTM flows are ~50% null. ART-as-of 1999-01/02 is ~53-59% covered (universe),
  ~93%+ from 1999-03. Alternative: `dimension="ARY"` (fiscal-year flow, OSAP's own basis; `depamor`
  ARY null 1.16%, netinccmn ARY null 0.06%) restores 1999-01/02 coverage at the cost of staleness up to
  the 15-month cap. Translator decision (sanctioned deviation): default ART, ARY if preflight shows
  1999-01..02 coverage under the 40% bar; log which.
- Denominator: `ctx.universe["mkt_cap_usd"]` at the signal date (DAILY.marketcap month-end), NOT
  SF1.marketcap (filing date).

## 5. Filters
SignalDoc `Filter`: `exchcd%in%c(1,2)` (NYSE and AMEX only; Notes: "Exclude NASDAQ stocks"). Not
applied in `CF.py` itself (the filter is an OSAP portfolio-sort filter), and a factor file may not
filter. The harness universe (US common, NYSE/NASDAQ/NYSEMKT) includes NASDAQ names; deviation, not
reproduced. `Quantile Filter`/`LS Quantile` blank; EW portfolios, period 12, start month 6. No SIC exclusion.

## 6. Predicted sign
`Sign = 1.0` (SignalDoc, t = 3.379, port sort): high CF predicts high returns; long D10, short D1. No flip.

## 7. Mass-point question
A do-nothing firm (no new filing) keeps `ib+dp` fixed but `mkt_cap_usd` moves monthly, so CF moves
continuously. Mass at zero only if `ib+dp == 0`: `ib` exact zero 0.00-0.02% (prior probe), so ~none;
`dp` zero/NaN (1.6-2.6% zero in universe) gives CF = ib/mve, not zero. Share at any one value ~0%.
`mve_permco` == 0 -> NaN (OSAP); also guard `<= 0`. Ties: harness default (average).

## 8. History needed
One latest filing plus current market cap; no return window; `history_months` not needed. Under ART
the first decision months have ~53% TTM coverage (section 4); preflight should report 1999-01..03.
SF1 from 1997Q4 and DAILY from 1998-12-01 suffice for month-end cap at 1999-01.

## 9. OSAP metadata (SignalDoc)
Acronym CF; Acronym2 CF2Price; Cat.Signal Predictor; Cat.Form continuous; Cat.Data Accounting;
Cat.Economic valuation; Authors Lakonishok, Shleifer, Vishny; Year 1994; Journal JF; SampleStart
1968, End 1990; Key Table "6 panel 1"; Test port sort; Predictability 1_clear; Rep Quality 1_good;
Sign 1.0; T-Stat 3.379; EW; LS Quantile 0.1; Portfolio Period 12; Start Month 6; Filter `exchcd%in%c(1,2)`.
Definition: net income (ib) plus depreciation (dp) divided by market equity.

## 10. Proposed Sharadar mappings and deviations
```
ib         -> SF1 netinccmn (ART via ctx.fundamentals)       [compustat.ib, mapped; verify on this snapshot]
dp         -> SF1 depamor, NaN -> 0 (replicates OSAP zero-fill) [compustat.dp, mapped, verified 2026-09-30]
mve_permco -> ctx.universe["mkt_cap_usd"]                     [crsp.mve_permco, approx]
CF         =  (netinccmn + fillna(depamor, 0)) / mkt_cap_usd.where(mkt_cap_usd > 0); netinccmn NaN -> NaN
```
Deviations:
1. Numerator freshness: TTM to latest quarter (0-3 months) vs OSAP fiscal-year 6-17 months.
2. `netinccmn` is after preferred dividends; Compustat `ib` is before them (`netinc` would be nearer:
   parent net income, before preferred dividends; differs on 12.1% of ART rows, gap = prefdivis). The map says
   netinccmn; the translator should confirm with the field-checker whether to use `netinc` (not in the
   index; check the map) and log the choice.
3. `depamor` is the cash-flow add-back (may include operating-lease ROU amortisation from 2019, COST),
   not the income-statement dp; and Sharadar already 0-fills it when absent (3.8% exact-zero) so the
   OSAP zero-fill is reproduced automatically; explicit NaN->0 covers residual nulls.
4. Denominator: Sharadar prices all share classes at the primary ticker's price with all-class
   sharesbas; a few-% level error on <=2% of names.
5. OSAP's NYSE/AMEX-only filter not reproduced; NASDAQ names are in the harness universe.
6. Early 1999 coverage ~53-59% under ART; ARY fallback described in section 4.
7. Sector-relative ranks remove the across-sector level (financials' NI/cap).

Fields NOT in the map: none required; `netinc` alternative is in the map (`compustat.ni`).
`FactorDef`: dimension default ART (ARY only if preflight requires), no `history_months`,
`family=None` until Phase C.
