# Recomm_ShortInterest — Analyst recommendations and short interest (Drake, Rees and Swanson 2011, Table 7b)

OSAP ref b4e911e69678a7424f318617a61d813f54183123 (config ref b4e911e6). Script `Signals/pyCode/Predictors/Recomm_ShortInterest.py`
(cached as `predictor.py`; present in the tree at that path). Authority: SignalDoc row with `Cat.Signal == Predictor`. Upstream read:
`upstream_IBESRecommendations.py` (ibes.recddet via WRDS), `upstream_CompustatShortInterest.py` (comp.sec_shortint and
sec_shortint_legacy via WRDS). DATA_SHA 198b281de1a0.

## 1. Data availability (verdict: `data_unavailable` — recommend `infeasible`; TWO independent missing inputs)

| input (OSAP) | Sharadar | status |
|---|---|---|
| `ireccd`, `amaskcd`, `anndats` (IBES `recddet` individual analyst recommendations) | NONE | unavailable (IBES) |
| `tickerIBES` (SignalMasterTable mapping to IBES) | NONE | unavailable |
| `shortint` (Compustat `sec_shortint`, exchange short interest, 1973+) | NONE | unavailable (not in any of the 13 tables) |
| `shrout` (monthlyCRSP) | `DAILY.marketcap*1e6/SEP.close` or SF1.sharesbas | `crsp.shrout` approx |
| `gvkey`, `permno` | TICKERS (no gvkey) | identifiers only |

- Checked on THIS snapshot (13 tables: ACTIONS, DAILY, DESCRIPTIONS, EVENTS, METRICS, SEP, SF1, SF2, SF3, SF3A, SF3B, SP500, TICKERS):
  no analyst-recommendation field, no short-interest field. The field_map index has no key for IBES recommendations or short interest.
  (SF2 insider trades, SF3 13F holdings and SF1 share counts are not substitutes: short interest is the exchange-reported short
  position, not any of them.) Both inputs are on the standing-unavailable list.
- Missing-item rule: OSAP does NOT zero-fill either: it INNER-joins short interest and recommendations (`how="inner"`), so a stock without
  both has no signal. Neither can be supplied, so there is no `approx` path: `infeasible`.

## 2. Variables (exact source names)

`ireccd` (-> `ireccd12`), `amaskcd`, `anndats`, `tickerIBES`, `gvkey`, `shortint`, `shrout`, `permno`, `time_avail_m`.

## 3. Formula in words and the key lines

Per tickerIBES-analyst, take the most recent recommendation issued on or before about the 17th of the month and carry it forward for
up to 5 months (`rec_extension = "5mo"`); average across analysts to get the stock-month consensus (`ireccd12`, 1 strong buy .. 5 sell).
```
ShortInterest = shortint / shrout
ConsRecomm    = 6 - ireccd12                      # 5 = strong buy .. 1 = sell (DRS coding)
QuintShortInterest, QuintConsRecomm = fastxtile(., n=5) by time_avail_m
Recomm_ShortInterest = 1 if (QuintShortInterest == 1 & QuintConsRecomm == 1)     # low short interest, lowest consensus
                     = 0 if (QuintShortInterest == 5 & QuintConsRecomm == 5)     # high short interest, highest consensus
                     = missing otherwise
```
Rows are restricted to names with all of gvkey, tickerIBES, short interest and recommendations (inner joins).

## 4. Timing / lag

Recommendations: the 17th-of-month consensus cut; carried 5 months; signal at `time_avail_m` t. Short interest: monthly (Compustat
monthly panel); no explicit publication lag applied in OSAP. Not reproducible without the data.

## 5. Filters

SignalDoc Filter blank. In-code: inner merges on gvkey, tickerIBES, shortint and recommendation; nothing else.

## 6. Predicted sign

SignalDoc `Sign = +1.0`: 1 (low short interest and lowest-quintile consensus code) earns more than 0 (high short interest, highest
quintile). `ascending=True`. Cat.Economic `recommendation`; Cat.Data `Analyst`; Cat.Form `discrete`; EW; Portfolio Period 1; Start
Month 1; sample 1994-2006; t = 4.09 (FF + Mom alpha, Table 7b); Signal Rep Quality `4_lack_data`.

## 7. The mass-point question

The output is binary {0, 1} and missing for the ~96%+ of names outside the two joint-extreme quintile cells. Whatever the data, scored
names sit on two values (modal share >= 50% of the scored set, above the 10% cliff), `qcut(q=10)` gives 2 bins, and the scored set is a
small share of the universe (a low/low or high/high corner of two quintile sorts: the corner is well under 20% and far under the 40%
Stage 1 coverage bar). So the signal would fail preflight (mass point, coverage) even if the inputs existed. Structural; not
measured (inputs absent).

## 8. History needed

IBES recommendations and Compustat short interest both begin pre-1999; the decision window would not be truncated if the data
existed. Scorable months on this snapshot: 0 of 276 (two missing inputs).

## 9. OSAP metadata

Acronym `Recomm_ShortInterest`; LongDescription "Analyst Recommendations and Short-Interest"; Authors Drake, Rees and Swanson; Year 2011;
Journal AR; Cat.Data Analyst; Cat.Economic recommendation; Cat.Form discrete; Sign 1.0; Return 1.11; T-Stat 4.09; Key Table 7b; Test
"port sort FF+Mom alpha"; Stock Weight EW; Portfolio Period 1; Start Month 1; Acronym2 Recomm_ShortInterest; Predictability 1_clear;
Signal Rep Quality 4_lack_data; GScholarCites 276. Detailed Definition: "Go long firms in lowest quintile of short interest
(shortint/shrout) and lowest quintile of analyst recommendations ... Go short firms in highest quintile of short interest and highest
quintile of analyst recommendations."

## 10. Proposed Sharadar mappings and deviations

- `ireccd`, `amaskcd`, `anndats`, `tickerIBES` -> NO mapping (IBES absent).
- `shortint` -> NO mapping (short interest absent).
- `shrout` -> `crsp.shrout` approx (irrelevant: the numerator is missing).
- Recommendation: `infeasible` (class `data_unavailable`: IBES recommendations AND short interest).
