# Price — Log of the raw stock price (Blume and Husic 1973, JF, Table 2 column c)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Signals/pyCode/Predictors/Price.py` (cached `predictor.py`, `signaldoc_row.csv`,
`upstream_SignalMasterTable.py`, `upstream_CRSPMonthly.py`). Written fresh from source and `field_map_index.yaml`. DATA_SHA 198b281de1a0.
Measured on the harness universe (`build_universe`, recorded snapshot), all 276 decision months (signals 1998-12-31 .. 2021-11-30), scratch only, no factor file.

## 1. Data availability — VERDICT: FEASIBLE (one mapped input, no zero-fill, no unavailable item)

| input (OSAP) | field_map key | Sharadar | status |
|---|---|---|---|
| `prc` (CRSP monthly close, SignalMasterTable) | `crsp.prc` | `SEP.closeunadj` at the month's last trading day = the panel's `px_usd` (`ctx.universe["px_usd"]`) | mapped (verified 2026-09-30) |

- WHICH PRICE OSAP USES: raw as-traded `prc` from `crsp.msf` (`upstream_CRSPMonthly.py` selects `a.prc`; `cfacshr`/`cfacpr` are fetched but never applied in `Price.py`, nor in SignalMasterTable). So the level is NOT split-restated.
  Sharadar `closeunadj` is the as-traded price (jumps on split day: AAPL 2020-08-31 closeunadj 499.23 -> 129.04), `close` is split-restated and `closeadj` adds dividends. Use `closeunadj` only; `close` or `closeadj` would make the level depend on the snapshot date (today's split basis).
- `abs()` in OSAP is for CRSP's negative bid/ask-midpoint convention; SEP has no negative prices (close > 0 on every row), so it is a no-op.
- Not used: IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob, ppegt; no SF1 field at all.
- Missing-item rule: nothing to fill; a missing `prc` drops the row (`dropna` on `Price`). Panel `px_usd` is non-null for every universe name (coverage 100% in all 276 months).

## 2. Variables (exact source names)
`permno, time_avail_m, prc`; derived `Price`.

## 3. Formula in words and key lines
Natural log of the absolute month-end stock price; low-priced stocks vs high-priced stocks, price as a size/lottery-like trait.
```
df["Price"] = np.log(abs(df["prc"]))        # then dropna; yyyymm = time_avail_m
```
SignalDoc Detailed Definition agrees: "Log of absolute value of price (prc)." No scaling, no winsorising, no sample restriction.

## 4. Timing / lag convention
OSAP: `time_avail_m` = the CRSP month t of the row; the price is month t's last-trade close and predicts month t+1 (signal at month-end t). Harness: signal at the prior business month-end,
`px_usd` = `closeunadj` on the last trade date of that month (`build_monthly_panel`: `last.rename(closeunadj -> px_unadj)`), i.e. the same object; no extra lag. Price-only: no filing date, no ART/ARQ,
`dimension` default; nothing to smear. CRSP uses the bid/ask midpoint on a no-trade month-end; Sharadar carries the last close instead (immaterial).

## 5. Filters
Predictor: none. SignalDoc Filter blank (SignalDoc "Quantile Filter" blank). `upstream_SignalMasterTable.py` keeps common stocks `shrcd` in (10, 11, 12) on `exchcd` in (1, 2, 3). Here: the harness universe
(US common on NYSE/NASDAQ/NYSEMKT, price >= $1, relative size/dollar-volume screen). The $1 floor TRUNCATES the low-price tail that OSAP keeps (sub-$1 stocks, and for a log-price signal the extreme low decile): declared deviation,
not removable (harness owns the universe).

## 6. Predicted sign
SignalDoc `Sign = -1.0` (low price -> high returns); `ascending=False`. Cat.Economic other, Cat.Data Price, Cat.Form continuous, T-Stat 2.9, sample 1932-1971, Key Table 2 column c, test "mv reg", EW,
Portfolio Period 1, Start Month 12.

## 7. The mass-point question
A do-nothing firm (price never changes) just keeps its value; there is no zero. Prices sit on a cent grid, so pairwise ties are common but no single value is a mass point. Measured on all 276 months:
modal log-price share 0.13-0.67% of the universe (median 0.21%; the modal price is a round dollar level that changes by month, e.g. $20.00 at 0.67% in 1999-01), distinct values 1,227-2,141 (universe n 1,739-2,867);
qcut yields ten bins in every month. Ties: default average rank; no noise or secondary key.

## 8. History needed (snapshot starts 1998-01)
One month-end price. No window, no `history_months`. All 276 months scorable, coverage 100% of the universe. Overlap with the size characteristic (log price is correlated with log market cap) is a Phase C / Stage 2 question, not a construction one.

## 9. OSAP metadata
Price; Blume and Husic; 1973; JF; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Economic other; Sign -1.0; T-Stat 2.9; EW; Portfolio Period 1; Start Month 12; sample 1932-1971; Key Table "2 column c"; Test "mv reg"; cites 187.

## 10. Proposed Sharadar mappings with deviations
```
px = ctx.universe["px_usd"].astype(float)            # SEP.closeunadj at the month-end
score = np.log(px.where(px > 0))                      # ascending=False ; inputs ("SEP.closeunadj",)
```
Deviations: (a) `closeunadj` replaces CRSP `prc`; the two agree except CRSP's bid/ask midpoint on no-trade month-ends (and the abs() of negative quotes), (b) the harness price >= $1 floor truncates the low tail OSAP keeps,
(c) within-sector rank and harness winsorisation (1/99) replace OSAP's NYSE-breakpoint sort. No field missing from the map. Recommendation: translate (feasible) and preflight. A factor file reads data only through `MonthContext`
(`ctx.universe`), so if the translator prefers a daily read, `ctx.daily("SEP", ["closeunadj"], 10)` last row per ID at `signal_asof` is equivalent.
