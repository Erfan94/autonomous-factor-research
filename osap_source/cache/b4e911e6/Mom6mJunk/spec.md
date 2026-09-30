# Mom6mJunk — Junk-stock momentum: Mom6m for stocks with a credit rating of BBB+ or worse, S&P rating else CIQ (Avramov, Chordia, Jostova and Philipov 2007, JF, Table 3 NIG)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/Mom6mJunk.py` (cached `predictor.py`; upstream `upstream_SPCreditRatings.py`, `upstream_CIQCreditRatings.py`, `upstream_SignalMasterTable.py`, `upstream_CRSPMonthly.py`). DATA_SHA 198b281de1a0.
Written fresh from source and `field_map_index.yaml`.

## 1. Data availability (verdict: DATA_UNAVAILABLE -> INFEASIBLE. The gating input is a firm credit rating; no Sharadar table holds one, and OSAP does not zero-fill it)

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| S&P long-term issuer rating `splticrm` (`comp.adsprate`, mapped to a 1-22 numeric scale, `credrat` = `ratingsp`) | none (ratings are not in `field_map_index.yaml`) | none | unavailable | `credrat.fillna(inf)` then the junk test fails -> Mom6mJunk is NaN (the observation is DROPPED, not zero-filled) |
| CIQ rating (`currentratingnum`, `ciq.wrds_erating/irating/srating`) fallback | none | none | unavailable | as above |
| `gvkey` link (drop if gvkey missing) | `compustat.cusip`/`cik` approx only | TICKERS | - | not needed without a rating |
| `ret` (total return) | `crsp.ret` | SEP closeadj ratio | mapped | as Mom6m |
- Missing-item rule: a required input is unavailable and OSAP does not zero-fill it (missing rating = no signal), so infeasible.
- Checked on THIS snapshot: the 13 held tables (ACTIONS, DAILY, DESCRIPTIONS, EVENTS, METRICS, SEP, SF1, SF2, SF3, SF3A, SF3B, SP500, TICKERS). Column scan: no column name contains rating, credit or moody. SF1 carries only debt-quantity fields (debt, debtc, debtnc, debtusd, ncfdebt, currentratio) and no rating. TICKERS (28 columns: category, exchange, siccode, sector, scalemarketcap, scalerevenue, famaindustry, ...) carries none; `scalemarketcap` is a size bucket, not a credit grade. EVENTS has `eventcodes` only; the nearest code (DESCRIPTIONS EVENTCODES '63') is "Change in Credit Enhancement or Other External Support", a corporate-event code, not a rating. No proxy is proposed: a leverage, distance-to-default or size proxy is a different signal, not this predictor.
- Nothing was measured for coverage or mass points; there is no signal to measure. No preflight expected; route to `osap_frontier.yaml` with reason `data_unavailable: credit ratings (S&P adsprate / CIQ), no Sharadar source, not zero-filled by OSAP`.

## 2. Variables (exact source names)
`gvkey, permno, time_avail_m, ret` (SignalMasterTable); `ratingsp` from `m_SP_creditratings` (`credrat`, `sp` numeric), `ratingciq` from `m_CIQ_creditratings`; derived `ret_lag1..5`, `Mom6m`, `credrat`, `Mom6mJunk`.

## 3. Formula in words and key lines
Mom6m (compound of the five monthly returns t-5..t-1, `(1+ret_lag1)*...*(1+ret_lag5)-1`, see the Mom6m spec) kept only for stocks whose latest credit rating is junk-ish: numeric rating <= 14 and > 0 on OSAP's scale (higher = better; the Avramov cut is BBB or lower). Rating source: S&P by default, CIQ where S&P is missing, forward-filled within permno (`groupby("permno")["credrat"].ffill()`, no staleness limit).
```
df["credrat"] = df["ratingsp"].fillna(df["ratingciq"]) ; df["credrat"] = df.groupby("permno")["credrat"].ffill()
df["credrat"] = df["credrat"].fillna(np.inf)
df["Mom6mJunk"] = np.where((df["credrat"] <= 14) & (df["credrat"] > 0), df["Mom6m"], np.nan)
```
OSAP quirks (for completeness): `drop if gvkey missing` precedes the lags (comment in source: unsure it makes sense); returns NaN -> 0 after that drop, and the lags use row shifts on the gvkey-restricted panel.

## 4. Timing / lag convention
Signal dated t: returns t-5..t-1 and the rating as of (at most) month t, forward-filled. Holding t+1. The rating leg carries no publication lag in OSAP. Overlap with the v0 Momentum leg (return months t-11..t-1): the Mom6m return window (t-5..t-1) lies inside it (measured Spearman of Mom6m with that 12-1 value: median 0.64 over 276 months, see the Mom6m spec); the rating filter would restrict the cross-section to rated junk names (not measured, no rating data).

## 5. Filters
SignalDoc Filter `abs(prc)>5, me>me_nyse20`; Detailed Definition: "Mom6m. Include only stocks with a credit rating (splticrm) of BBB or lower. Drop if missing credit rating or non-standard credit rating." The harness universe already applies price >= $1 and a relative cap/dollar-volume screen.

## 6. Predicted sign
SignalDoc `Sign = +1.0`; Return 2.12; T-Stat 4.29. Orientation would be `ascending=True`.

## 7. The mass-point question
Not measurable (no rating). Structurally, the OSAP signal is NaN for every unrated or investment-grade name, so the scored set is a small junk-rated slice, well under the 40% coverage bar and possibly under the 30-names-per-decile bar (not measured); in any case infeasible on data.

## 8. History needed (snapshot starts 1998-01)
Returns window 6 month-ends; rating history from 1985 (paper sample 1985-2003). Moot.

## 9. OSAP metadata
Mom6mJunk (Acronym2 Mom6Jnk); Avramov et al 2007 JF; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form continuous; Cat.Data Price; Cat.Economic momentum; Sample 1985-2003; Key Table "3 NIG"; Test port sort; Sign +1.0; Return 2.12; T-Stat 4.29; EW; LS Quantile 0.1; Portfolio Period 1.0; Start Month 6.0; GScholar cites 593. LongDescription "Junk Stock Momentum".

## 10. Proposed Sharadar mappings with deviations
None. Fields not in the map: S&P issuer credit rating (`splticrm` / `comp.adsprate`) and CIQ credit ratings (`ciq.wrds_*rating`). If the field checker maps them it should record them as `unavailable`, with the note "no Sharadar table carries a credit rating; OSAP drops unrated names (no zero-fill)". Recommendation: infeasible.
