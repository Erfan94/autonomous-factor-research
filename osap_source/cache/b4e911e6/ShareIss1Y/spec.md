# ShareIss1Y — OSAP predictor spec (pinned ref b4e911e6, DATA_SHA 198b281de1a0)

## 1. Data availability verdict: APPROX (constructible; declared deviations)
Checked against `osap_source/field_map_index.yaml`. No IBES, options, 13F, patents, segments,
ratings, pensions, xad, emp, ob or ppegt. OSAP zero-fills nothing here.

| OSAP var | field_map key | Sharadar | status | note |
|---|---|---|---|---|
| shrout | crsp.shrout | SF1.sharesbas (route A) or DAILY.marketcap*1e6 / SEP.close (route B) | approx, verified-with-deviation 2026-09-30 | company-level (all classes) count on the primary ticker; filing-date cadence; both on TODAY's split basis |
| cfacshr | none | none | n/a | the split adjustment: Sharadar restates counts to today's basis, so not needed |

Why approx: (a) CRSP `shrout` is per PERMNO and monthly; Sharadar share counts are company-level
and step at filing dates (10-K/10-Q cover count); (b) OSAP's `shrout*cfacshr` split adjustment
is replaced by Sharadar's own restatement (checked below). Recommend: **approx** (feasible).

## 2. Variables by exact source name (predictor.py)
`SignalMasterTable`: permno, time_avail_m. `monthlyCRSP`: permno, time_avail_m, shrout
(thousands; upstream divides by 1000 so millions), cfacshr. Inner merge, validate 1:1.
Note: the file docstring says "shrout/cfacshr", the code MULTIPLIES (`shrout * cfacshr`); the
code is authoritative (and the note says the facshr construction of the paper gives
near-identical results).

## 3. Formula
Growth of split-adjusted shares outstanding between t-18 and t-6 months:

    temp      = shrout * cfacshr
    l6_temp   = temp at calendar month t-6 (exact DateOffset match; else NaN)
    l18_temp  = temp at calendar month t-18
    ShareIss1Y = (l6_temp - l18_temp) / l18_temp      ; dropna

Key line: `df["ShareIss1Y"] = (df["l6_temp"] - df["l18_temp"]) / df["l18_temp"]`. The most recent
six months are EXCLUDED (issuance over months t-18..t-6).
Sharadar (route A): `s6 = sharesbas as of business month-end t-6`, `s18` likewise at t-18, from
`ctx.fundamentals_at_month_ends(["sharesbas"], [6, 18])` (latest filing with datekey <= that
month-end, age <= 15 months); score `(s6 - s18) / s18.where(s18 > 0)`. Route B: `at_month_end`
on DAILY.marketcap and SEP.close at lags 6 and 18, shares = marketcap*1e6/close.
Gate: `history_months=18` (a listed name at t-18, as OSAP needs a CRSP row at t-18).

## 4. Timing / lag convention
Signal dated t; both readings are in the past (t-6, t-18), so no contemporaneous leakage;
portfolio held t+1. ART/SF1 as-of-filing: each reading is the latest filing known at its own
month-end, so cover counts lag the month-end by up to ~one quarter; the 12-month difference
is between two such counts (about four filings apart). Level field, not flow: no
`dimension=ARQ` flow concern; ART and ARQ carry the same sharesbas (null 0.07% both).
Split neutrality, VERIFIED on this snapshot: SF1 ART sharesbas is restated to today's basis and
continuous across splits: AAPL 2013-10-30 2.519e10 -> 2014-01-28 2.498e10 -> 2014-04-24 2.412e10
(the 7:1 split of 2014-06 lies inside, no step); NVDA (4:1 2021-07, 10:1 2024-06) 2.46e10 ..
2.51e10 through 2020-2022; TSLA (5:1 2020-08) 2.69e9 -> 3.01e9 over 2019-2021. A ratio of two
sharesbas readings is therefore split-neutral; never pair sharesbas with closeunadj.

## 5. Filters
predictor.py: none. SignalDoc `Filter` blank, `Quantile Filter` blank. Harness universe:
price >= $1, US common, relative cap/dollar-volume screens.

## 6. Predicted sign (SignalDoc)
`Sign = -1.0`: high share issuance -> low returns (Pontiff and Woodgate 2008, JF, Table 3A
ISSUE, univariate reg, t=7.08; Acronym2 ShareIs5). `ascending=False`. Cat.Economic external
financing; Cat.Form continuous; Cat.Data Accounting; sample 1970-2003; EW, Portfolio Period
12, Start Month 6; Signal Rep Quality 1_good; Predictability 1_clear.

## 7. The mass-point question
Do-nothing firm (no issuance, no buyback, no option exercise) has an unchanged share count and
produces exactly 0.0. Measured, route A on SF1 dimension ART (config default; sharesbas is a level, ART and ARQ carry the same count), 92 of 276 decision months (every third, 1998-12-31
.. 2021-09-30; universe 1,739-2,867; 90 months with >= 100 scored names):
- exact 0.0: 0.92% mean of scored names (max 1.54%); modal value 0.0 in all 90 months;
  10 qcut bins everywhere (distinct/n 97%); |change| < 0.1%: 4.5% mean (max 6.4%).
- same filing at both lags (stale count, identical datekey): 0.03% mean (max 0.7%).
- route B (DAILY): exact zero rate is not comparable (marketcap rounding noise breaks ties),
  route A vs B rank correlation 0.9987 mean (min 0.983).
OSAP's construction has no tie rule, no winsorisation and no floor, so no tie rule is
warranted by OSAP's own construction; 0.9% mass is far below the 10% cliff; average rank.
Buyback names are negative (not zeroed), as in OSAP.

## 8. History needed
Needs a price at t-18 and a filing known at t-18. SEP starts 1997-12-31 and SF1 filings begin
early 1998, so route A coverage is 0% at 1998-12-31 and 1999-03-31, 45.7% at 1999-06-30,
81.4% at 1999-09-30, 81.8% at 1999-12-31, 88%-98% from 2002 (median 95% over all months). Route B (DAILY from 1998-12-01):
first scorable month 2000-06-30 (82.2%). Recommend route A: about 5 decision months
(1999-01..1999-05) empty and 1999-06..1999-08 thin, of 276. `lookback_months` 33
(18 + the 15-month filing age cap).

## 9. OSAP metadata
Acronym ShareIss1Y (Acronym2 ShareIs5); Pontiff and Woodgate 2008, JF ("Share issuance and
cross-sectional returns"); Key Table "3A ISSUE"; Test "univariate reg"; T-Stat 7.08;
GScholarCites202509 874. Detailed Definition: growth in number of shares between t-18 and
t-6; shares calculated as shrout/cfacshr to adjust for splits. Source
`Signals/pyCode/Predictors/ShareIss1Y.py` (in tree.txt, not a Placebo).

## 10. Overlap with the v0 composite (factual, from factors/composite.py)
No leg reads share counts directly. Spearman of raw ShareIss1Y with raw legs (92 months):
Profitability mean -0.31 (range -0.46 to -0.18), Size (log mkt cap) -0.21, Value 0.01,
Momentum 0.01. Investment leg (asset growth, ART assets t vs t-12m) is a balance-sheet
growth measure, not measured here. Cat.Economic (external financing) has no v0 seed family.

## 11. Proposed Sharadar mappings and deviations
| item | mapping | deviation |
|---|---|---|
| shrout*cfacshr | SF1.sharesbas at month-ends t-6, t-18 (route A) | company-level; filing cadence; split-restated (no cfacshr) |
| calendar lag match | latest filing known at business month-end | up to a quarter stale, both ends |
| CRSP row at t-18 | `history_months=18` | approximates "a row exactly 18 months back" |
| universe/ranks | harness; within sector | OSAP EW cross-section |
Fields in `field_map_index.yaml`: crsp.shrout (approx, verified 2026-09-30), compustat.csho
(sharesbas, mapped, verified 2026-09-30). Nothing unmapped.
