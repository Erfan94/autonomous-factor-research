# RIVolSpread — Realized minus implied volatility (Bali and Hovakimian 2009, Table 3 Panel A)

OSAP ref b4e911e69678a7424f318617a61d813f54183123 (config ref b4e911e6). Emitted by `Signals/pyCode/Predictors/ZZ1_RIVolSpread.py`
(cached as `predictor.py`). Authority: SignalDoc row with `Cat.Signal == Predictor` (`signaldoc_row.csv`). Upstream read:
`upstream_OptionMetricsCRSPLink.py`, `upstream_bali_hovak.R`. Runs after RealizedVol. DATA_SHA 198b281de1a0.

## 1. Data availability (verdict: `data_unavailable` — recommend `infeasible`)

| input (OSAP) | Sharadar | status |
|---|---|---|
| `mean_imp_vol` by `cp_flag` C/P (OptionMetrics IvyDB, WRDS, via `bali_hovak_imp_vol.csv`) | NONE | unavailable (options) |
| `secid` (OptionMetrics-CRSP link) | NONE | unavailable |
| `RealizedVol` (daily CRSP returns) | SEP closeadj | constructible (see RealizedVol spec; feasible) |
| `sicCRSP`, `permno`, `time_avail_m` | TICKERS.siccode (current), universe | approx |

- Checked on THIS snapshot (DATA_SHA 198b281de1a0): the 13 held tables are ACTIONS, DAILY, DESCRIPTIONS, EVENTS, METRICS, SEP, SF1, SF2,
  SF3, SF3A, SF3B, SP500, TICKERS. None holds option prices or implied volatility. The 386-row DESCRIPTIONS indicator list has no
  implied-vol, option or volatility-surface column (only SF3/SF3A call/put HOLDER counts of 13F filers, a different object, and
  METRICS beta/high-low columns). Options are on the standing-unavailable list.
- Missing-item rule: OSAP does NOT zero-fill `impvol`; it keeps only rows with `impvol.notna()` (`df = df[df["secid"].notna() &
  df["impvol"].notna()]`). Substituting 0 would make the signal equal annualised RealizedVol, a different (total-volatility)
  predictor, not a proxy for the spread. So `infeasible`; no `approx` path.

## 2. Variables (exact source names)

`impvolC`, `impvolP` (pivot of `mean_imp_vol` by `cp_flag`), `impvol`, `secid`, `RealizedVol`, `sicCRSP`, `permno`, `time_avail_m`.

## 3. Formula in words and the key lines

Implied vol = mean of call and put ATM implied volatility (falls back to whichever side exists). Realized vol = RealizedVol (std of the
month's daily excess returns, see its spec) x sqrt(252). The signal is realized minus implied.
```
impvol = (impvolC + impvolP)/2 ; if NaN use impvolC, else impvolP
RealizedVol = RealizedVol * sqrt(252)
RIVolSpread = RealizedVol - impvol        # only rows with secid and impvol and RealizedVol present
```
Filter: drop SIC 6720-6730 (closed-end funds) and SIC 6798 (REITs), applied BEFORE the merge with RealizedVol.

## 4. Timing / lag

OptionMetrics values are dated within month t (`date` -> `time_avail_m`); RealizedVol is month t's days; signal at t, return t+1, no extra
lag. Price leg is causal; the option leg needs a source that does not exist here. No SF1 item: no ART/ARQ issue.

## 5. Filters

SignalDoc `Filter = shrcd %in% c(10,11)` (common stock); note "OP says NYSE only but we find all stocks gets closer to their numbers".
In code: SIC 6720-6730 and 6798 removed; `secid` and `impvol` non-missing.

## 6. Predicted sign

SignalDoc `Sign = -1.0` (high realized-minus-implied spread predicts LOW returns). `ascending=False`. Cat.Economic `optionrisk`;
Cat.Data `Options`; Cat.Form `continuous`; VW; LS quantile 0.2; Portfolio Period 1; Start Month 6; sample 1996-2004; t = 2.9.

## 7. The mass-point question

Continuous difference of two volatilities; a do-nothing name has a zero realized-vol leg (-impvol, not a shared value). No mass
point expected in the spread itself. Not measured: the signal cannot be built. The real coverage limit is OptionMetrics' own
universe (optionable names with ATM quotes), which is not observable here.

## 8. History needed

OptionMetrics data begin 1996; decision window starts 1999-01, so history would not bind if the data existed. Price leg: 15 daily
returns in the month (RealizedVol covers 99.9% of the universe in all 276 months; measured for that spec). Scorable months on this
snapshot: 0 of 276 (no implied vol).

## 9. OSAP metadata

Acronym `RIVolSpread`; LongDescription "Realized minus Implied Vol"; Authors Bali and Hovakimian; Year 2009; Journal MS; Cat.Data
Options; Cat.Economic optionrisk; Cat.Form continuous; Sign -1.0; Return 0.732; T-Stat 2.9; Key Table "Table 3 Panel A"; Test "port
sort"; Stock Weight VW; LS Quantile 0.2; Portfolio Period 1; Start Month 6; Acronym2 VRPSpread; Predictability 1_clear; Signal Rep
Quality 1_good; GScholarCites 500. Detailed Definition: "Realized Vol (past 30 days) minus ATM Implied Vol". `config.PATCH_OPTIONM_IV`
makes OSAP download a 2023-vintage signal file instead of rebuilding; that file is OSAP's output, not a Sharadar input.

## 10. Proposed Sharadar mappings and deviations

- RealizedVol leg -> SEP closeadj daily returns (see `RealizedVol/spec.md`), x sqrt(252).
- Implied-vol leg -> NO mapping: no field in the map or on the snapshot.
- Recommendation: `infeasible` (class `data_unavailable`: options).
