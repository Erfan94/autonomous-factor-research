# BrandInvest — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

Source: Signals/pyCode/Predictors/BrandInvest.py (cached `predictor.py`, `signaldoc_row.csv`,
`upstream_CompustatAnnual.py`). Construction only.

## 1. Data availability verdict: INFEASIBLE (xad is unavailable and OSAP does not zero-fill it where it matters)

- `xad` (Compustat annual advertising expense) has no Sharadar field. `field_map_index.yaml` line 175:
  `compustat.xad` sharadar "" status `unavailable`; `field_map.yaml` `xad: sf1: null, status: unavailable`.
  The snapshot's 112 SF1 columns were confirmed by the caller to contain no advertising item.
- The zero-fill exception does NOT rescue it. Upstream builds `xad0 = xad.fillna(0)` (CompustatAnnual.py
  line 136), and `xad` itself is NOT in `zero_fill_vars`. But the predictor needs the REAL `xad` for the
  denominator: `OK = xad.notna()`; BrandCapital is seeded only at the first non-missing xad
  (`xad/(0.5+0.1)`), `FirstNMyear` is NaN for a firm that never reports xad, and BrandCapital is set to NaN
  wherever `xad` is NaN or `fyear < FirstNMyear`. With xad absent for every firm, BrandCapital and its lag are
  all NaN, so `BrandInvest = xad0 / l_BrandCapital` is NaN for every firm-year. Zeroing the numerator alone
  yields no signal (0/NaN). There is no `approx` route; no Sharadar item (sgna, opex) isolates advertising.
- Recommend `infeasible`. Suggested frontier reason: "xad advertising expense not published by Sharadar SF1;
  BrandInvest's denominator (BrandCapital) needs real xad, xad0 zero-fill does not rescue it".
- Remaining inputs are available (see 10), so the failure is solely xad. Not a measured-on-data failure; the
  verdict follows from the absence of any SF1 column (field-checker may re-scan column names, none expected).

## 2. Variables (exact source names)

| source name | origin | field_map key | status |
|---|---|---|---|
| xad | funda.xad via a_aCompustat | compustat.xad | UNAVAILABLE |
| xad0 | upstream `xad.fillna(0)` | (derived from xad) | unavailable |
| at | funda.at | compustat.at | mapped (SF1.assets, verified 2026-09-30) |
| sic | CCM header (a_aCompustat `sic`) | compustat.sic | mapped (TICKERS.siccode, current, not point-in-time) |
| datadate | funda.datadate | compustat.datadate | mapped (calendardate) |
| fyear | funda.fyear | compustat.fyear | approx (calendardate year) |
| time_avail_m | upstream availability month (see 4) | -- | harness ART-as-of-filing |
| gvkey, permno | identifiers | -- | harness ticker/permaticker |

## 3. Formula

Brand capital by perpetual inventory (depreciation 0.5), per gvkey sorted by fyear:
- first fyear with non-missing xad: `BC = xad / (0.5 + 0.1)`
- every later row: `BC_t = (1 - 0.5) * BC_{t-1} + xad0_t` (`tempxad = xad.fillna(0)`, so a missing xad year still
  decays the stock)
- `BC` set to NaN if the firm never reported xad, if `fyear < FirstNMyear`, or if that row's own `xad` is NaN
- then scaled: `BC = BC / at` (same row's at)
- `l_BC = BC.shift(1)` within gvkey (prior ROW, not prior fiscal year; gaps in fyear are not checked)
- `BrandInvest = xad0 / l_BC`

Key lines: `df["BrandCapital"] = (1 - 0.5) * prev_brand_capital + curr_tempxad`;
`df["BrandCapital"] = df["BrandCapital"] / df["at"]`; `df["BrandInvest"] = df["xad0"] / df["l_BrandCapital"]`.
Quirk to preserve if ever built: the denominator `l_BC` is already divided by prior-year at, so BrandInvest is
xad_t over lagged-capital-per-asset, i.e. NOT a ratio scaled by current assets (units: dollars of xad per unit of
capital/assets). The SignalDoc text ("xad divided by BrandCapital") hides this.

## 4. Timing / lag

- Annual Compustat, expanded 12 months forward from upstream `time_avail_m` (`expand 12`), then the latest
  datadate wins per (gvkey, month). Upstream CompustatAnnual sets `time_avail_m` = datadate month + 6 (standard
  OSAP 6-month lag; consistent with SignalDoc Start Month 6). Under ART-as-of-filing the information date would
  move to the actual filing date (typically 2-3 months after FYE), so values would appear earlier than OSAP's.
- Dec fiscal year-end only (see 5); each value is held from June (Dec FYE + 6) through the following May, stale up to 17
  months after FYE. No flow item is differenced year over year by TTM: xad and the recursion are annual (ARY-like);
  `dimension=ARQ` smearing does not arise, but a Sharadar build would need ARY, not ART TTM, to reproduce the
  Dec-only annual stock. Moot given infeasibility.

## 5. Filters

- Drop SIC 4900-4999 (utilities) and 6000-6999 (financials). Sharadar siccode is the CURRENT classification
  (field_map note), a deviation from Compustat's header sic.
- Keep only `month(datadate) == 12`.
- Dedup by (gvkey, month), then (permno, month). Universe filters are harness-side.

## 6. Predicted sign

SignalDoc `Sign = -1` (higher brand investment predicts lower return). Cat.Economic `investment alt`; OP test:
port sort, LS quantile 0.2, EW; in-paper t=2.01 (SignalDoc T-Stat); Predictability "2_likely", quality "1_good".
Orientation for the harness would be negative (low BrandInvest long).

## 7. Mass-point question

A do-nothing firm (never reports xad, xad missing throughout) produces NaN, not a mass point: it drops out. The
signal exists only for firms that report advertising, a small share of the Compustat universe (order of one in
five or fewer firm-years, guess; not measured). Within those firms: a firm whose xad is missing in year t but
reported in t-1 gets `xad0 = 0` and a valid `l_BC`, hence BrandInvest = exactly 0 (a mass at zero of firms that
stopped reporting or report xad=0 after having reported). Ties at 0 need a within-sector average-rank tie
rule; count of exact zeros cannot be measured here. Sector-month breadth would also be thin (< 10 names in
many sectors, forcing the cross-section fallback). Moot given infeasibility.

## 8. History needed

The recursion is unbounded (seeded at the firm's first reported xad and decays at 0.5/yr, so effective memory
~3-5 years). The snapshot SF1 starts 1997Q4, so seeds would be left-truncated at 1998 (Compustat seeds from 1950s
onward), biasing early-window BC upward relative to OSAP. First usable year-end ~1999-2000 for lagged capital.
Needs at least 2 annual observations per firm.

## 9. OSAP metadata

- Acronym BrandInvest, Cat.Signal Predictor, authors Belo, Lin and Vitorino (2014), Review of Economic Dynamics.
- Cat.Form continuous, Cat.Data Accounting, Cat.Economic "investment alt". Sample 1975-2010.
- Sign -1, Return 0.435, T-stat 2.01, EW, LS quantile 0.2, portfolio period 12, start month 6. Related placebo:
  BrandCapital (same recursion, not the ratio).
- OSAP note: the paper is VW with a 10% single-stock cap; OSAP uses EW.

## 10. Proposed Sharadar mappings (for completeness; no factor to be written)

- at -> SF1.assets (ARY for the annual stock); sic -> TICKERS.siccode (current); datadate -> calendardate.
- xad -> NONE. No substitute proposed. Deviation: none to state, because the signal cannot be built.
- Fields not in the map index: none beyond xad (xad0 is derived from it).
- Recommendation: mark `infeasible` in `osap_source/osap_frontier.yaml`; do not translate or preflight.
