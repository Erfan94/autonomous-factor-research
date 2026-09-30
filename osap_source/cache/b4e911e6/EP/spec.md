# EP — Earnings-to-price ratio (Basu 1977, JF, Table 1 average annual rate)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/EP.py` (cached `predictor.py`). DATA_SHA 198b281de1a0.
Written fresh from the source and `field_map_index.yaml`. Map statuses are mappings, not proofs (only notes marked verified_on 2026-09-30 are this snapshot).

## 1. Data availability (verdict: APPROX, feasible; no unavailable input)

| OSAP input | field_map key | Sharadar | map status | OSAP missing-item rule |
|---|---|---|---|---|
| `ib` (income before extraordinary items, annual) | `compustat.ib` (map points at `netinccmn`) | SF1 `netinc + netincdis` (see 10) | approx (remap: the map's `netinccmn` is IBCOM; proposed `netinc + netincdis`; `netincdis` NOT in the map) | not zero-filled (NaN) |
| `mve_permco` at t-6 (SMT) | `crsp.mve_permco` | SEP.close x SF1.sharesbas at the t-6 month-end (DAILY.marketcap analogue) | approx | row at t-6 required |

- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt. Nothing is zero-filled, nothing dropped.
- TRAP: the map's `compustat.ib -> netinccmn` is Compustat IBCOM (after preferred dividends, includes discontinued ops), NOT `ib`. Do not use it.
  Compustat `ib` is before preferred dividends and before extraordinary items AND discontinued operations. Nearest Sharadar concept is continuing income
  `netinc + netincdis`, where SF1.`netincdis` carries the OPPOSITE sign (known trap `sf1_netincdis_sign_inverted`: continuing = netinc + netincdis).
- FIELDS NOT IN THE MAP: `netincdis` (no `field_map_index` key, 0 hits), `sharesbas` is used as a level (map: `crsp.mve_permco` note). Checker: verify
  `netincdis` non-null share on ART/ARY universe rows, exact-zero share (~88% per the trap note), and that netinc + netincdis sits near the 10-K "income before extraordinary items" on a handful of names.
  Decision to log: use `netinc + netincdis` (fallback `netinc` alone if `netincdis` is unusable; differs on ~11.7% of rows by discontinued ops).
- The lagged cap needs SEP (from 1997-12-31) and SF1 `sharesbas`; both on the snapshot. Checker: `sharesbas` populated on ART rows known at each t-6 month-end.

## 2. Variables (exact source names)
`ib` (annual Compustat, $ millions; `m_aCompustat`), `mve_permco` (SignalMasterTable, $ millions), `permno, time_avail_m`. No SignalDoc `mve_c`: the code reads `mve_permco`.

## 3. Formula in words and key lines
EP is annual income before extraordinary items over company market value SIX MONTHS EARLIER (calendar `time_avail_m - 6 months`; a missing t-6 SMT row gives NaN). Negative EP is set missing.
```
df["time_lag6"] = df["time_avail_m"] - pd.DateOffset(months=6)        # self-merge -> mve_permco_lag6
df["EP"] = df["ib"] / df["mve_permco_lag6"]
df.loc[df["EP"] < 0, "EP"] = pd.NA ; df = df.dropna(subset=["EP"])
```
So losses (ib < 0) are NaN (construction, in `predictor.py`, NOT a portfolio filter); ib == 0 gives EP = 0 and is kept. A firm's lowest scored decile is the lowest POSITIVE EP, not losers.

## 4. Timing / lag convention
- OSAP: annual `ib` available at datadate + 6 months, held 12 months; market value is month t-6 (intended to mimic the Dec-31 market equity of Basu). `m_aCompustat` row must exist at t.
- Here (project default ART): TTM `netinc + netincdis` from the latest filing known at t, 0-3 months old (vs 6-17). ART flow = trailing-four-quarter SUM, a level, not a difference: no smear,
  no `dimension=ARQ`. ART flow nulls: universe ART coverage of netinccmn was 57% at 1999-01/02 (4-quarter sum needs 1998Q4), ~92% from 1999-03; expect the same thin start here.
  Faithful alternative: `dimension="ARY"` (annual, ~95% universe coverage in 1999), stale 0-12 months; ART chosen as the project convention, log the choice.
- Lagged cap: `ctx.at_month_end("SEP", ["close"], 6)` and `ctx.fundamentals_at_month_ends(["sharesbas"], [6])` give `ME_{t-6} = close_{t-6} x sharesbas(t-6 filing)`; use `ctx.fundamentals_at_month_ends(["sharesbas"], [6])` only, NO `sharefactor` (align with CompEquIss Route A, which matched DAILY.marketcap within 1% on 97.5-99.7% of the universe);
  ( sharesbas is split-restated to today's basis and SEP.close is on that basis, so the product is consistent; never pair with closeunadj).
  DAILY.marketcap is NOT used for the lag: it starts 1998-12-01, so a DAILY t-6 cap would first exist 1999-06 and lose five decision months (1999-01..05). The SEP route scores from 1999-01
  (t-6 = 1998-07, SEP from 1997-12-31), subject to a filing with `sharesbas` being known at 1998-07 (SF1 broad from 1997Q4). Checker to measure coverage 1999-01..06.
  If unsatisfactory, fallback is a constant-shares proxy M_t x closeadj(t-6)/closeadj(t) (wrong under issuance/buybacks; state if used).

## 5. Filters
- In the code: EP < 0 -> NaN (reproduce). SignalDoc `Filter` `exchcd==1` (NYSE only) is portfolio-stage and NOT in `predictor.py`: not reproduced (project universe spans NYSE/NASDAQ/NYSEMKT; `TICKERS.exchange` is the current exchange).
- Coverage: ib < 0 on roughly 30-45% of ART rows (map: 33% in 1999/2008, 45% in 2020), so after the loss exclusion coverage is about 55-70% of the universe before ART nulls. The 40% Stage-1 coverage bar is not automatic (thin early ART months may fall below); preflight to measure.

## 6. Predicted sign
SignalDoc `Sign = +1.0` (high EP -> high return); Stock Weight EW; LS Quantile 0.2; `Cat.Form` continuous; `Cat.Economic` valuation. Orientation: long HIGH EP. `FactorDef(ascending=True)`.

## 7. The mass-point question
- A do-nothing firm: `ib` fixed between filings, `ME_{t-6}` is a per-month historical value that changes every month; EP changes monthly: no stale-value default.
- Exact 0 needs ib = 0: measured 0.01% of non-null ART netinccmn rows (modal share 0.01%); expect the same order for `netinc + netincdis`. No mass point; ties: rank(method="average"), none expected.
- Scored cross-section excludes losers (about 30-45% of names), a coverage reduction, not a mass. Expected modal share well under 1%. A positive-EP name with ME_{t-6} tiny gives a huge EP; rank-based harness handles it, no winsorising.

## 8. History needed (snapshot starts 1998-01)
One filing (TTM needs four ART quarters: first full 1998Q4, filed early 1999) plus the price and share count at t-6 month-end. No `history_months` for returns; the price at t-6 is a level read
(if the translator wants the harness to gate on it, `history_months=6` would null names without a price 6 months back, which is the same as OSAP's "SMT row at t-6" requirement). Earliest decision 1999-01.

## 9. OSAP metadata (SignalDoc)
Acronym EP; Acronym2 EP; Basu; 1977; JF; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form continuous; Cat.Data Accounting; Cat.Economic valuation;
SampleStart 1957, End 1971; Key Table "1 average annual rate"; Test "port sort, no LS"; Sign +1.0; Return 0.58; T-Stat blank; Stock Weight EW; LS Quantile 0.2; Portfolio Period 1;
Start Month 6; Filter `exchcd==1`. Definition "ib / lag(market value of equity, 6 months). NYSE stocks only. Exclude if EP < 0. Lag simulates the Dec 31 market equity used in original paper".

## 10. Proposed Sharadar mappings and deviations
```
ib      -> SF1 netinc + netincdis (ART, latest filing)          [compustat.ib remap: NOT netinccmn; netincdis NOT in the map, sign inverted]
ME_t-6  -> SEP.close(t-6 bme) x SF1.sharesbas(known at t-6)                  [crsp.mve_permco at lag 6, approx]
EP      = ib / ME_t-6 ;  EP < 0 -> NaN ;  ME_t-6 <= 0 -> NaN ;  ascending=True
guard: fxusd == 1 (reporting-currency numerator over a USD cap; non-USD filers <= 0.06% of members)
```
Deviations: (a) ib is continuing income incl. any extraordinary items (Sharadar has no separate extraordinary line) and AFTER non-controlling interest; Compustat ib sits before NCI in some periods; (b) TTM at the latest
filing (0-3 months) instead of the fiscal-year value 6-17 months old; ARY is the faithful alternative; (c) lagged cap rebuilt from SEP x sharesbas (shares step at filing dates, not monthly as CRSP shrout;
company-level all-class cap at the primary's price, few-% level error on <=2% of names); (d) NYSE-only filter and the original Dec-31 annual sample not reproduced; (e) `TICKERS`-based exchange is current, unused here.
`FactorDef`: dimension ART (default), inputs `SF1.netinc, SF1.netincdis, SF1.sharesbas, SF1.fxusd, SEP.close`, `family=None` until Phase C. Units: SF1 monetary fields and sharesbas are raw; convert nothing if fxusd == 1 is gated.
