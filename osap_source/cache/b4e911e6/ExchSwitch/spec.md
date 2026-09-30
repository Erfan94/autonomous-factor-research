# ExchSwitch — listing upgrade in the past year (Dharan and Ikenberry 1995, Table 2 months -1 to 6)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/ExchSwitch.py` (cached `predictor.py`).
DATA_SHA 198b281de1a0. Measured on THIS snapshot with harness `build_universe` over the 276 decision months
(1999-01..2021-12) and ACTIONS exchange moves paired by `data_layer._exchange_moves` (scratch script, not committed).

## 1. Data availability (verdict: PREFLIGHT_FAILED — data constructible, signal is a ~99.5% mass point)

| OSAP input (`SignalMasterTable`) | field_map key | Sharadar | map status |
|---|---|---|---|
| `exchcd` and its 12 monthly lags | `crsp.exchcd` | point-in-time exchange from `ACTIONS` `exchangeto` / `exchangefrom` pairs (`contraname`) | approx |

- `TICKERS.exchange` is CURRENT only (ruling), so it cannot build lagged `exchcd`. The construction needs the
  ACTIONS exchange-move path named in the field_map `crsp.exchcd` note: 5,004 paired (ID, date) moves here, first
  dated 1998-01-07. Read through `ctx.actions(("exchangeto","exchangefrom"), 12, fields=("contraname",))` (rows dated
  <= signal), declaring `ACTIONS.contraname`.
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt. No SF1 input.
- Coverage of moves: about 15% of tickers have any recorded move (field_map). A firm that never moved has no row, so
  its flag is 0, equal to OSAP's 0 for a constant `exchcd`. OSAP output is binary for every SMT firm-month (no NaN).
- Field-checker: `ACTIONS.contraname` on `exchangeto`/`exchangefrom` on THIS snapshot (the map note quotes
  DATA_SHA 52402f7d1f9c, 3,895 pairs; this snapshot shows 5,004 paired moves, so the count moved) and the venue
  vocabulary (NYSE, NYSEMKT, NASDAQ, OTC, NYSEARCA, BATS).
- MEASURED (the reason for the verdict). Qualifying events in ACTIONS, all dates: 619 (NASDAQ->NYSE, NYSEMKT->NYSE,
  NASDAQ->NYSEMKT); 533 dated 1998-2021, by year 75 (1998), 62, 34, 34, 39, 24, then 4-29 a year (2015: 5, 2016: 4,
  2020: 5, 2021: 24). Across the 542,282 universe name-months of the 276 months, 2,701 (0.50%) carry the flag (an
  event dated in the prior 12 months, measured WITHOUT the
  current-venue condition, so an upper bound): monthly share mean 0.48%, range 0.04%-1.49%. Flagged names per month: median 7,
  p10 2, p90 24, max 34; fewer than 30 in 267 of 276 months, fewer than 10 in 177. Per-year share 1.25% (1999),
  0.70% (2000), 0.30-1.15% (2001-2009), 0.10-0.29% (2013-2021). The zero block is 98.5%-99.96% of the scored
  cross-section every month. SignalDoc's "approx 3,000 events" is the 1926-1990 CRSP history, not this universe.

## 2. Variables (exact source names)

`permno, time_avail_m, exchcd` (1 NYSE, 2 AMEX, 3 NASDAQ) and lags `exchcd_lag1..12` (monthly, per permno) from
`SignalMasterTable.parquet` (CRSP monthly header, restricted to shrcd 10/11/12 and exchcd 1/2/3).

## 3. Formula

```
any_amex_nasdaq = any(exchcd_lag_i in {2,3}, i=1..12)        any_nasdaq = any(exchcd_lag_i == 3, i=1..12)
ExchSwitch = 1 if (exchcd == 1 and any_amex_nasdaq) or (exchcd == 2 and any_nasdaq) else 0
```
Current exchange NYSE having been AMEX/NASDAQ in the prior 12 months, or current AMEX having been NASDAQ. A firm that
moves up and then moves on again is not flagged; a NaN lag is False. The output has no NaN.

## 4. Timing / lag convention

Monthly, 12 monthly lags (lag 1 = t-1): the flag is 1 for up to 12 consecutive months around a switch. Here: an
ACTIONS event dated in (t-12 months, t] with origin/destination as above and the destination still the current
venue. No fundamentals, so no ART-as-of-filing effect and no flow smearing; no `dimension` override.

## 5. Filters

SignalDoc `Filter` is empty. SignalMasterTable restricts to common stock on NYSE/AMEX/NASDAQ; the harness universe
(price >= $1, NYSE-20th-percentile cap, dollar volume) replaces it. The harness also screens on CURRENT
`TICKERS.exchange`, so a name that switched up and later left the three listed venues is not a member.

## 6. Predicted sign

SignalDoc `Sign = -1.0`: flagged firms earn LOW subsequent returns. Orientation: long flag = 0 (D1), short flag = 1
(`ascending=False`). `Cat.Form discrete`, `Cat.Economic other`, `Cat.Data Event`, `Stock Weight EW`,
`Portfolio Period 1`, `Start Month 12`.

## 7. The mass-point question

- A do-nothing firm (no exchange change in 12 months) produces exactly 0, as does a firm with no ACTIONS row. Measured
  share at 0: 98.5%-99.96% per month (mean 99.5%), about 10 flagged of about 1,965 universe names.
- Ties ARE the signal. A binary variable with a >= 98.5% zero block breaches the harness cliff (mode >= 10%, `qcut`
  < 10 bins) in every month: two values, D1..D9 one tie block. Fewer than 30 flagged names in 267/276 months also
  breaks the 30-names-per-decile bar. Average-rank ties and within-sector ranking do not rescue it (sector
  cells under 10 names fall back to the cross-section rank).
- Restricting to an event study (flagged only) is a different design, outside the decile screen. Verdict
  `preflight_failed` (measured: binary event, about 0.5% incidence).

## 8. History needed

ACTIONS exchange moves start 1998-01-07; a full 12-month window exists from 1999-01, the first decision month.
Pre-1998 switches are unobservable. Incidence decays from 1.25% (1999) to 0.10-0.29% (2013-2021); 2015 and 2016 carry
27 and 23 flagged name-months in the whole year.

## 9. OSAP metadata

`Cat.Signal Predictor`, `Cat.Form discrete`, `Cat.Data Event`, `Cat.Economic other`, Dharan and Ikenberry 1995 (JF),
sample 1962-1990, `Predictability 1_clear`, `Rep Quality 2_fair`, t = 3.61 (event study, months 1-6, size adjusted),
`Sign -1`, `Stock Weight EW`.

## 10. Proposed Sharadar mappings and deviations (only if it were built)

1. `exchcd` history -> ACTIONS `exchangeto`/`exchangefrom` `contraname` (NYSE 1, NYSEMKT 2, NASDAQ 3); observed moves
   only; `TICKERS.exchange` (current) is unusable for lags.
2. NYSEMKT == AMEX; OTC/NYSEARCA/BATS fall outside OSAP's 1/2/3.
3. About 15% of tickers carry any move; moves start 1998-01-07.
4. FIELD NOT IN THE INDEX as a factor input: `ACTIONS.contraname` (only the `crsp.exchcd` note mentions it).
Verdict: not a constructible decile predictor on this universe.
