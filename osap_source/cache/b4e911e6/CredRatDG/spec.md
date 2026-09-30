# CredRatDG — Credit Rating Downgrade (Dichev and Piotroski 2001, JF, Table 4, 3-month BHAR)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/CredRatDG.py` (cached `predictor.py`,
`signaldoc_row.csv`). DATA_SHA 198b281de1a0.

## 1. Data availability — VERDICT: INFEASIBLE (credit ratings are not in Sharadar)

| input (OSAP) | source | Sharadar | status |
|---|---|---|---|
| `credrat` (S&P long-term issuer rating, numeric), `m_SP_creditratings` | Compustat `splticrm` via `comp.adsprate` | none | unavailable (no field_map key; ratings listed as unavailable class) |
| `anydowngrade`, `ratingdate`, `source` (`m_CIQ_creditratings`) | Capital IQ ratings | none | unavailable |
| `gvkey`, `permno`, `time_avail_m` (SignalMasterTable) | CCM link | TICKERS ticker/permaticker | mapped (irrelevant) |

- Searched `data/sharadar_llms.txt` and `osap_source/api_schema/*.sql`: no rating, downgrade, debt-rating or
  credit column in any held table. EVENTS holds 8-K item codes; rating actions are not an 8-K item (agencies, not
  the issuer, announce them) and no code is a rating proxy. No IBES/estimates.
- Zero-fill: the only `fillna(0)` in the predictor is `dg_cur = dg_cur.fillna(0)`, which fills months WITHOUT a
  recorded downgrade. It is an output default, not a zero-fill of an optional input term; the ratings themselves are
  not optional. Dropping both rating sources leaves `dg_cur = 0` for every firm-month and `CredRatDG = 0` everywhere:
  constant. Recommend `infeasible` under the standing rule.
- No proxy accepted (e.g. 8-K debt events, Altman-style distress, return-based distress): a different hypothesis,
  not a construction of this signal.

## 2. Variables (exact source names)
S&P: `credrat` (by gvkey, month), `l_credrat` = previous row's credrat; CIQ: `anydowngrade`, `ratingdate`; master
table: `gvkey`, `permno`, `time_avail_m`.

## 3. Formula (for the record)
```
downgrade_sp = 1 if credrat - l_credrat < 0          # rating fell >= 1 notch vs previous monthly row (numeric scale
                                                     #  where larger = better, per splticrm mapping upstream)
downgrade_ciq = 1 if any CIQ downgrade in the month
dg_cur  = downgrade_sp.fillna(downgrade_ciq).fillna(0)
CredRatDG = rolling_max(dg_cur, window=6 rows, min_periods=1) per permno
```
Binary: 1 if a downgrade happened in the current or previous 5 months. Note the file's docstring says "past 6 months",
SignalDoc text says "past 3 months"; the code is a 6-row window.

## 4. Timing / lag
Monthly ratings forward-filled by `time_avail_m`; a rating change in month t enters in month t (no extra lag);
the signal persists 6 months. No fundamentals, no ART/ARQ issue. Moot.

## 5. Filters
None in the file. SignalDoc Filter empty. Rated-firm-only coverage: firms without a rating get 0 (not NaN), so the
signal mixes "rated, no downgrade" with "unrated".

## 6. Predicted sign
SignalDoc `Sign = -1.0` (downgrade -> lower subsequent return); `ascending=False` if ever built. Cat.Economic `other`,
Cat.Data `Analyst`, Cat.Form discrete; Signal Rep Quality `4_lack_data`.

## 7. The mass-point question
Binary with a dominant do-nothing value 0: a firm with no downgrade in the last 6 months, i.e. well over 95% of
firm-months (downgrades are rare events; estimate, not measured). Two values, ties everywhere; decile formation
collapses. Would fail preflight even with data. Moot.

## 8. History needed
OSAP's ratings start 1978 (S&P) and the OSAP sample definition starts 1986; 1999-01 start would be fine had the
data existed. Moot.

## 9. OSAP metadata
Acronym CredRatDG; LongDescription "Credit Rating Downgrade"; Authors Dichev and Piotroski; Year 2001; Journal JF;
Sample 1986-1998; Predictability in OP 1_clear; Signal Rep Quality 4_lack_data; Cat.Form discrete; Cat.Data Analyst;
Cat.Economic other; Sign -1.0; Return 1.3167; T-Stat 11.04; Key Table "4 Downgrade BHAR 3-month"; Test "event study
3-month size+BM adjusted nonstandard data"; Stock Weight EW; Portfolio Period 1; Start Month 12. Notes: most of the
return is earned in the first 3 days of the announcement; OP uses Moody's data, OSAP has S&P back to 1978.

## 10. Proposed Sharadar mapping
None; no factor file. Fields not in the map: `splticrm`/`credrat`, CIQ `anydowngrade` (ratings class, unavailable).
Frontier row: reason "S&P/CIQ credit ratings not in Sharadar; dropping leaves constant 0; ~95%+ mass point".
