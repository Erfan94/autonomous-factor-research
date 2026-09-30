# PctTotAcc — Percent total accruals (Hafzalla, Lundholm, Van Winkle 2011, AR, Table 5A)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Signals/pyCode/Predictors/PctTotAcc.py` (cached `predictor.py`,
`signaldoc_row.csv`). Written fresh from source and `field_map_index.yaml`. DATA_SHA 198b281de1a0.
Measured on the harness universe (`build_universe`, recorded snapshot), all 276 decision months (signals 1998-12-31 .. 2021-11-30), scratch only, no factor file.

## 1. Data availability — VERDICT: APPROX (every input present; preferred-stock netting is lost; no unavailable item)

| OSAP input | field_map key | Sharadar (ART) | status | OSAP missing rule |
|---|---|---|---|---|
| `ni` | `compustat.ni` | `netinc` | mapped (verified 2026-09-30) | NOT zero-filled: missing -> NaN |
| `prstkcc` | `compustat.prstkcc` | `ncfcommon` (NET common flow, inflow-positive) | approx | ZERO-FILLED (`zero_fill_vars`) |
| `sstk` | `compustat.sstk` | same column `ncfcommon` | approx | ZERO-FILLED (`zero_fill_vars`) |
| `dvt` | `compustat.dvt` | `ncfdiv` (outflow-NEGATIVE, mostly common-only) | approx | ZERO-FILLED (`zero_fill_vars`) |
| `oancf` | `compustat.oancf` | `ncfo` | mapped | NOT zero-filled -> NaN |
| `fincf` | `compustat.fincf` | `ncff` | mapped | NOT zero-filled -> NaN |
| `ivncf` | `compustat.ivncf` | `ncfi` | mapped | NOT zero-filled -> NaN |

- Checked both places: upstream `CompustatAnnual.py` `zero_fill_vars` = [nopi, dvt, ob, dm, dc, aco, ap, intan, ao, lco, lo, rect, invt, drc, spi, gdwl, che, dp, act, lct, tstkp, dvpa, scstkc, sstk, mib, ivao, prstkc, prstkcc, txditc, ivst]; `PctTotAcc.py` has NO `fillna` of its own (only `dropna` on the result). So prstkcc, sstk, dvt are zero-filled, the other four inputs are not.
- Consequence for the translation: `ncfcommon` null -> 0 and `ncfdiv` null -> 0 are CONSISTENT with OSAP (zero-filled terms), while `netinc`, `ncfo`, `ncff`, `ncfi` null -> NaN (matches OSAP). In practice the four unfilled fields go null together (the cash-flow statement is absent as a block), so the fills seldom matter.
- Not used: IBES, options, 13F, patents, segments, ratings, pensions, xad, emp, ob, ppegt. `ib` is NOT used (ni, not ib), so the `ib = netinc + netincdis` sign trap does not apply; do not reach for `netincdis`.
- Why approx, not feasible: Compustat `sstk`/`prstkcc`/`dvt` include PREFERRED; Sharadar `ncfcommon`/`ncfdiv` exclude or only partly include it (see section 10).

## 2. Variables (exact source names)
`gvkey, permno, time_avail_m, ni, prstkcc, sstk, dvt, oancf, fincf, ivncf`; derived `PctTotAcc`.

## 3. Formula in words and key lines
Total accruals in the "cash-flow" sense: net income minus everything that the cash-flow statement and the equity flows
account for (operating, financing, investing cash flow, net stock repurchase, dividends), scaled by ABSOLUTE net income.
```
df = df.drop_duplicates(["permno", "time_avail_m"])
PctTotAcc = (ni - (prstkcc - sstk + dvt + oancf + fincf + ivncf)) / abs(ni)
```
Code vs SignalDoc text: they agree (Detailed Definition lists the same terms). Note the code ADDS dvt and net-repurchase on top of
`fincf`, which already contains them, so the published series is not the textbook accrual; it is replicated as coded.
`ni == 0` gives inf/NaN in the source; the translation sets it NaN (0.00-0.09% of the universe). No winsorising or sample restriction.

## 4. Timing / lag convention
OSAP: annual Compustat values stamped datadate + 6 months (m_aCompustat, each annual record copied to 12 months), held 12 months.
Sharadar: ART (TTM) as of `datekey` via `ctx.fundamentals([...])` (default dimension), so the signal refreshes each quarter and is
available ~1-3 months earlier than OSAP's +6-month stamp. All six inputs are TTM FLOWS of the same window in one ratio: there is no
year-over-year difference of a flow, so nothing smears under TTM and no `dimension=ARQ` flag is needed (ART == sum of 4 ARQ within 1%
on ~99% of rows for ncfo/ncff/ncfi/netinc). ART-as-of-filing vs OSAP: trailing-four-quarter vs fiscal-year window.

## 5. Filters
Predictor: none except the `dropna` of the ratio. SignalDoc Filter blank. Here: the harness universe only (price >= $1, relative
size/dollar-volume screen); financials and utilities are NOT dropped.

## 6. Predicted sign
SignalDoc `Sign = -1.0` (high accruals -> low returns); `ascending=False`. Cat.Economic accruals, Cat.Data Accounting,
Cat.Form continuous, T-Stat 3.29, Return 0.71 (EW, decile LS 0.1), Key Table 5A, sample 1989-2008.

## 7. The mass-point question
A continuous ratio of flows; a do-nothing firm (all flows zero) would give 0/|ni|, but `ni != 0` is required and cash-flow totals are
essentially never all zero. Measured on all 276 months: modal value share of scored names 0.04-0.17% (median 0.05%); distinct values
1,171-2,725 (scored n ~1,170-2,700); qcut yields ten bins everywhere. No tie handling needed beyond average rank.
Heavy tails: tiny |ni| denominators give |PctTotAcc| > 10 on 1.8-8.1% of scored names (median 3.7%); cross-sectional p1/p99 about
-15 / +19 (median month). Rank (and the harness winsorisation), never z-score. The sign of the denominator is removed by `abs()`, so a
loss-making firm is not sign-flipped (by design of the OSAP ratio).

## 8. History needed (snapshot starts 1998-01)
One ART filing; no lag, no price window, no `history_months`. Coverage of the universe (scored share): 51.3%, 52.4%, 57.1% at
1998-12 / 1999-01 / 1999-02 (SF1 ART needs four quarters of history, null 41-48% of the universe), 90.9-99.6% from 1999-03;
median 97.0%; 3 of 276 months below 80%. Null shares (median month): netinc 2.6%, ncfo/ncff/ncfi 2.9%, ncfcommon 3.0%, ncfdiv 3.0%. All 276 months scorable.

## 9. OSAP metadata
PctTotAcc (Acronym2 AccrPct); Hafzalla, Lundholm, Van Winkle; 2011; Accounting Review; Predictability in OP 1_clear; Signal Rep Quality 1_good;
Cat.Economic accruals; Sign -1.0; Return 0.71; T-Stat 3.29; EW; LS Quantile 0.1; Portfolio Period 12; Start Month 6. Notes: Table 5 Panel A size-adjusted
return hedges, t-stat approximate (p < .001). Cites 211.

## 10. Proposed Sharadar mappings with deviations
```
f = ctx.fundamentals(["netinc","ncfcommon","ncfdiv","ncfo","ncff","ncfi"])          # ART
dvt_like = -f["ncfdiv"].fillna(0).clip(upper=0)     # dvt >= 0; positive ncfdiv (0.0-0.6%/month) clipped to 0
net_rep  = -f["ncfcommon"].fillna(0)                # prstkcc - sstk; both zero-filled in OSAP
num = f["netinc"] - (net_rep + dvt_like + f["ncfo"] + f["ncff"] + f["ncfi"])
score = num / f["netinc"].abs().where(f["netinc"].abs() > 0)        # ascending=False; inputs SF1.{netinc,ncfcommon,ncfdiv,ncfo,ncff,ncfi}
```
Sign rearrangement: `prstkcc - sstk = -ncfcommon`; `dvt = -ncfdiv` (outflow-negative). Algebraically the Sharadar numerator is
`ni - (ncfo + ncfi + ncff - ncfcommon - ncfdiv)`: because `ncff` already contains `ncfcommon` and `ncfdiv`, those two net out. In Compustat, the
preferred-stock part of sstk and dvt is netted the same way inside fincf; in Sharadar preferred issuance/redemption and preferred dividends stay
un-netted inside `ncff` (material for financials 2008-11, TARP: e.g. C/JPM/BAC preferred flows of tens of $B, per the `sstk` note).
Deviations: (a) `ncfcommon` excludes preferred; `ncfdiv` mostly common-only (preferred dividends missing for separate-line filers); (b) net-share-settlement tax
and option-exercise flows sit inside `ncfcommon`; (c) ART (TTM) as filed rather than fiscal-year at datadate + 6 months; (d) `ni = 0` -> NaN (OSAP inf).
Fields not in the map: none. Recommendation: translate (approx) and preflight.
