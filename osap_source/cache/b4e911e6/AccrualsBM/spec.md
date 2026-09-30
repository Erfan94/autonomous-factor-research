# AccrualsBM (Bartov & Kim 2004) — spec, Phase A fetch batch 01

Ref b4e911e69678a7424f318617a61d813f54183123. Source `Signals/pyCode/Predictors/AccrualsBM.py` (cached `predictor.py`);
SignalDoc row Acronym AccrualsBM, Cat.Signal Predictor (cached `signaldoc_row.csv`). DATA_SHA 198b281de1a0.
Upstream traced: `CompustatAnnual.py` (m_aCompustat), `SignalMasterTable.py` (mve_permco) via the cached Accruals/upstream_* files.
The spec is written fresh from that source and `field_map_index.yaml`; no prior outcome is cited.

## 1. Data availability — VERDICT: APPROX (constructible; two deviations, one structural risk)

| input | OSAP name | Sharadar | map key | index status |
|---|---|---|---|---|
| current assets | act | SF1.assetsc | compustat.act | mapped |
| cash + ST investments | che | SF1.cashneq + SF1.investmentsc.fillna(0) | compustat.che | approx (investmentsc includes financing receivables; cashneq incl. some restricted cash) |
| current liabilities | lct | SF1.liabilitiesc | compustat.lct | mapped |
| debt in current liabilities | dlc | SF1.debtc | compustat.dlc | mapped |
| income taxes payable | txp | NONE | compustat.txp | UNAVAILABLE (no SF1 field) |
| total assets | at | SF1.assets | compustat.at | mapped |
| common equity | ceq | SF1.equity | compustat.ceq | approx (incl. preferred; no pref split) |
| company market value | mve_permco | DAILY.marketcap (primary ticker, already company-level) | crsp.mve_permco | approx |
| share code / exchange (universe) | shrcd, exchcd | TICKERS.category / exchange | crsp.shrcd, crsp.exchcd | approx (harness universe; not in the factor) |

Deviations that make it `approx`, not `feasible`:
- **txp is unavailable and is NOT zero-filled by OSAP in this script.** `CompustatAnnual.py` zero_fill_vars lists act, che, lct,
  dp ... but NOT txp and NOT dlc; only `Accruals.py` does `txp.fillna(0)`. AccrualsBM uses raw txp, so in OSAP a missing txp
  (or dlc) makes the accrual missing. Sharadar cannot reproduce that sample condition. Closest construction: DROP the Δtxp term
  (equivalent to Δtxp = 0). Error = +Δtxp / avg(at), small against ΔWC, but a real construct change. Do not substitute
  taxliabilities/txditc (deferred taxes, a different item).
- **Financials / REITs drop out.** act, lct, dlc, che-inputs are null ~20% of ART rows, 71.5% Financial Services + 19.8% Real
  Estate (index notes for compustat.act/lct/dlc; coverage among US-common ART rows ~78-80%). OSAP zero-fills act/che/lct so banks
  carry a (degenerate) accrual there; here they are NaN. Do NOT zero-fill to imitate that. Leave NaN.
- No IBES/options/13F/patent/segment/rating/pension/xad/emp/ob/ppegt input. Nothing infeasible beyond txp.
Structural risk (section 7): a two-corner binary signal with ~90% missing will probably fail coverage >=40% / names-per-decile
>=30 / mass-point preflight in this relative universe. That is for preflight to measure; it is not a data-availability gap.

## 2. Variables by exact source name
m_aCompustat: ceq, act, che, lct, dlc, txp, at (annual, datadate + 6 months, held 12 months); SignalMasterTable: mve_permco;
temps: BM, lag_act/che/lct/dlc/txp/at (= value 12 panel rows earlier), tempacc, tempqBM, tempqAcc.

## 3. Formula
- BM = ln(ceq / mve_permco)   (NaN if ceq <= 0; ceq = 0 gives -inf, ~0.01% of rows)
- tempacc = [ (act - lag_act) - (che - lag_che) - ( (lct - lag_lct) - (dlc - lag_dlc) - (txp - lag_txp) ) ] / ((at + lag_at)/2)
  (working-capital accruals, NO depreciation term, unlike Accruals.py)
- tempqBM, tempqAcc = Stata-style fastxtile quintiles (n=5) of BM and tempacc, BY MONTH across the whole panel
- AccrualsBM = 1 if tempqBM == 5 (high BM) and tempqAcc == 1 (low accruals)
  AccrualsBM = 0 if tempqBM == 1 (low BM) and tempqAcc == 5 (high accruals)
  else NaN; then NaN if ceq < 0.
Key lines: `df.loc[(tempqBM==5)&(tempqAcc==1),"AccrualsBM"]=1`; `df.loc[(tempqBM==1)&(tempqAcc==5),"AccrualsBM"]=0`;
`df.loc[df["ceq"]<0,"AccrualsBM"]=np.nan`.
DISCREPANCY to record: the SignalDoc text ("1 if highest Accrual quintile and lowest BM quintile ... 0 if lowest Accrual and
highest BM") is the reverse of the code. The code is the authority: 1 = high BM + LOW accruals. The SignalDoc Sign (+1) agrees
with the code (value, low-accrual corner is the long side).

## 4. Timing / lag convention
- OSAP: annual data available at datadate month + 6, repeated 12 months, so a signal uses a fiscal year 6-17 months old. `lag_*`
  is a ROW shift(12) within permno on that monthly panel, i.e. the prior fiscal year when the panel has no gaps (a permno-panel
  gap would shift the window). BM is refreshed monthly: stale annual ceq over the current month's mve_permco.
- Sharadar/harness: PIT ART as of the signal date (datekey <= date), 1-4 months stale, updating each quarter, so the change
  window becomes a rolling 4-quarter change and the signal turns over more often than OSAP's annual one.
- All inputs are balance-sheet LEVELS (assetsc, cashneq, investmentsc, liabilitiesc, debtc, assets, equity). ART == ARQ for levels
  (index: ~99% exact-same-period match), so there is no TTM smearing; no flow item (no dp). No `dimension=ARQ` override needed.
- Recommended year-ago alignment: `ctx.fundamentals_yoy(fields, years=1)` (aligned by REPORT PERIOD, tol 45d) rather than
  `fundamentals(lag_months=12)`, which lands on the wrong quarter ~15% of the time. Current and lag balance sheets then span exactly
  4 quarters, the closest PIT analogue of OSAP's fiscal-year difference (and same-quarter seasonality cancels).
- mve: DAILY.marketcap at the signal date (USD millions; SF1 levels are raw USD). The unit gap is a constant shift inside ln()
  and does not move quintiles, but keep one scale explicit.

## 5. Filters
Exclude ceq < 0 (and BM undefined when ceq <= 0). OSAP's SignalMasterTable restricts to common stock (shrcd 10/11) on
NYSE/AMEX/NASDAQ; here the harness universe applies instead. Quintile breakpoints are therefore over the harness universe
(relative cap/dollar-volume screened, membership band), not OSAP's all-stock CRSP panel: a more large-cap cut, a mapping
deviation to state. The factor computes the quintile cuts on `ctx.universe` names only (a within-signal definition; no
sector ranking or dates in the factor).

## 6. Predicted sign
SignalDoc Sign = +1.0 (Return 0.206, T-Stat 5.5, LS Quantile 0.2, EW, Portfolio Period 12, Start Month 6, sample 1980-1998,
Cat.Economic = valuation, Cat.Form = discrete, Cat.Data = Accounting). `ascending=True` (high value = 1 = attractive).

## 7. The mass-point question
- A do-nothing firm (mid quintile on either variable, or a corner that does not match) gets NaN, not a value. Scored names only
  take values {0, 1}. Scored share: two independent quintile corners give 4% + 4% = 8% of names; BM and accruals are weakly
  correlated, so expect roughly 7-10% of the quintile-eligible names, then x ~0.8 (financials/REITs null) x ceq>0 (~0.9).
  Order of magnitude ~6-9% of the universe, i.e. ~100-200 scored names in a ~1,800-2,700-name universe. Preflight must measure it.
- Within the scored set the signal is a two-point mass (roughly half 1, half 0). A decile sort ties completely: D10 = all the
  1s, D1 = all the 0s, deciles 2-9 empty; ~50-100 names a side if the split is even, so the >=30 names per decile bar can only
  be met if the scored set is ~300+. Harness ties: rank(method="average") (analytics.py:182/187) gives all 1s one shared rank and all 0s another; the decile cut is pd.qcut(duplicates="drop") (analytics.py:264), which collapses to ~2 bins on a two-point mass (decile collapse / inconclusive territory).
- Sector ranking: a sector-month with < 10 scored names falls back to the cross-section rank. With ~150 scored names over ~11
  sectors, most sector-months fall back.
- Expected preflight interaction: coverage bar (40%) is likely missed by construction (~8% vs 40%); record as a measured
  `preflight_failed` reason if so, not as a data gap. Do not loosen a bar or substitute a continuous score (that is a different
  predictor).

## 8. History needed (snapshot starts 1998-01)
Needs one year-ago balance sheet plus the current one: >= 12 months of filings before the first decision month (1999-01), i.e.
year-ago reportperiod ~1997Q4-1998Q1. SF1 is in breadth from 1997Q4, so early-1999 lag coverage is thin (year-ago filings for
Sep-FYE names may fall before 1997Q4). The checker should measure level coverage of assetsc/debtc/liabilitiesc/cashneq/
investmentsc/assets at reportperiod 1997Q4-1998Q3 (the ~50% ART population quoted for 1998Q1-Q3 concerns TTM flows; these are
levels, but confirm). No SEP window, so no `history_months`; set `lookback_months=12` for the data-start check.

## 9. OSAP metadata
Acronym AccrualsBM; Authors Bartov and Kim; Year 2004; Journal RFQA; Cat.Signal Predictor; Predictability in OP 1_clear;
Signal Rep Quality 1_good; Cat.Economic valuation; Cat.Form discrete; Cat.Data Accounting; Sign +1; Return 0.206; T-Stat 5.5;
Evidence Summary "t=5.5 in long-short"; Key Table "3 mean diff 1-2"; Test "LS port"; Stock Weight EW; LS Quantile 0.2;
Portfolio Period 12; Start Month 6; Sample 1980-1998. Acronym2 AccrualsBM. Detailed Definition as above (text reversed vs code).

## 10. Proposed Sharadar mappings and deviations
```
inputs = SF1.assetsc, SF1.cashneq, SF1.investmentsc, SF1.liabilitiesc, SF1.debtc, SF1.assets, SF1.equity, DAILY.marketcap
act=assetsc; che=cashneq+investmentsc.fillna(0) (NaN if cashneq NaN); lct=liabilitiesc; dlc=debtc; at=assets; ceq=equity
acc = (d(act) - d(che) - (d(lct) - d(dlc))) / ((at + at_lag)/2)   # d = latest minus same-period year-ago via fundamentals_yoy
BM = ln(equity / (marketcap*1e6)); NaN where equity <= 0
qBM, qAcc = pd.qcut-style quintiles over ctx.universe; signal = 1 (qBM=5 & qAcc=1), 0 (qBM=1 & qAcc=5), else NaN
```
Deviations: (a) Δtxp omitted (txp unavailable; OSAP does not zero-fill it here); (b) financials/REITs NaN where OSAP
zero-fills act/che/lct; (c) che includes investmentsc financing receivables; (d) equity includes preferred; (e) marketcap =
primary close x total shares (other classes at primary price); (f) quarterly PIT ART replaces 6-month-lagged annual; year-ago by
report period, not row shift; (g) quintile breakpoints over the harness universe, not all CRSP; (h) signal text/code
reversal in SignalDoc resolved to the code.
Fields not in the map: none. txp (`compustat.txp`) is in the map, status unavailable. No new map keys needed.
