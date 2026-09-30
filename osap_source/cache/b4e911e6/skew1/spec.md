# skew1 — Volatility smirk near the money (Xing, Zhang and Zhao 2010, Table 3A; Acronym2 OSmirkNTM)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/skew1.py` (cached `predictor.py`; upstream `OptionMetricsXZZ.R`, `config.py` beside it). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`.

## 1. Data availability verdict: DATA_UNAVAILABLE (recommend infeasible)
| OSAP input | Sharadar | status |
|---|---|---|
| OptionMetrics `opprcd`/`secprd`/`vsurfd` (option-level implied vol, strike, cp_flag, expiry, best bid/offer, open interest, option volume) | none | UNAVAILABLE. The 13 held tables (ACTIONS, DAILY, DESCRIPTIONS, EVENTS, METRICS, SEP, SF1, SF2, SF3, SF3A, SF3B, SP500, TICKERS) contain no option-price or implied-vol data; `field_map_index.yaml` has no options entry |
| `SignalMasterTable.secid` (OptionMetrics security id) | none | unavailable |
Options is in the project's named-unavailable list. OSAP does not zero-fill it: `skew1` is NaN for any firm without an OptionMetrics match (`df_final.dropna`). The `PATCH_OPTIONM_IV` branch reads a 2023 vintage of the SAME OptionMetrics signal from `openassetpricing`: still options-derived, not a Sharadar-constructible path (and not this project's pinned construction).

## 2. Variables (OSAP)
`secid`, daily option rows: `cp_flag`, `strike_price`, `impl_volatility`, `best_bid`, `best_offer`, `open_interest`, option `volume`, `exdate`; underlying `close`, `volume`.

## 3. Formula in words
Daily, per secid, for options with 10-60 days to expiry, underlying volume > 0, 0.03 < impl vol < 2.0, mid price > 0.125, open interest > 0, observed on calendar day >= 23 of the month: take the call with moneyness (K/S) closest to 1 within 0.95-1.05 and the put with moneyness closest to 1 within 0.80-0.95; skew1 = IV(put) - IV(call); then the monthly value from the month's late-month days. Rows with no match are NaN.

## 4. Timing
Late-month (day >= 23) observations map to time_avail_m; signal available at that month end. No fundamentals; no ART/ARQ issue.

## 5. Filters
As above (volume, IV band, price, open interest, expiry window, moneyness bands).

## 6. Predicted sign
SignalDoc Sign = -1 (high put-minus-call smirk predicts low returns); Return 0.64, T-Stat 2.19; Test "port sort weekly"; LS Quantile 0.2; Predictability 2_likely, Rep Quality 2_fair. Would be `ascending=False`.

## 7. Mass-point question
Not measurable here: no input. A do-nothing firm produces no value (NaN, not a mass point); continuous when present. OptionMetrics coverage (~1996+) is a subset of optionable names, typically large/liquid.

## 8. History needed
OptionMetrics starts 1996; sample 1996-2005 in the paper. Irrelevant: data unavailable.

## 9. OSAP metadata
Xing, Zhang and Zhao (2010), JFQA; Cat.Data Options; Cat.Economic optionrisk; continuous; sample 1996-2005; Key Table 3A; EW; Portfolio Period 1; Start Month 12; 945 cites. Notes: "Tab3A shows weekly ret LS t-stat of 2.19. Screens in appendix are important."

## 10. Proposed Sharadar mappings
None. No Sharadar field carries option implied volatility; deriving one from prices would be a different signal, not OSAP's. Verdict: infeasible (data_unavailable: options).
