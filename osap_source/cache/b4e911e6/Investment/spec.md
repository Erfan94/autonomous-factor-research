# Investment (OSAP acronym `Investment`, Acronym2 InvToRev) — Capex-to-revenue divided by its own 36-month rolling mean (Titman, Wei and Xie 2004, JFQA, Table 1B Average)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/Investment.py` (cached `predictor.py`; upstream `upstream_CompustatAnnual.py`, `upstream_asrol.py` beside it).
DATA_SHA 198b281de1a0. Written fresh from source and `field_map_index.yaml`.
NAMING: this is the Titman-Wei-Xie capex-to-average-capex signal, translated as `factors/candidates/InvestmentTWX.py` with `osap_acronym="Investment"`. The v0 composite leg NAMED `Investment` is AssetGrowth (`osap_acronym="AssetGrowth"`, family `investment`); they are different signals.
Overlap with the v0 leg, measured (Spearman, harness universe, per month, then averaged over 276 months, ~1,600 names/month with both): rho(InvestmentTWX, total-assets YoY growth) mean 0.076, range -0.011 .. 0.200.
Inputs differ (this: capex and revenue; AssetGrowth: total assets). Both are OSAP Cat.Economic "investment" and both have SignalDoc Sign -1.

## 1. Data availability (verdict: APPROX, translatable; no unavailable input)

| OSAP input | field_map key | Sharadar | status | OSAP missing rule |
|---|---|---|---|---|
| `capx` | `compustat.capx` | `-SF1.capex` (SIGN FLIP: Sharadar capex is a cash outflow), dimension ARY | mapped (verified-with-deviation) | NOT zero-filled: missing capx -> NaN ratio |
| `revt` | `compustat.revt` | SF1 `revenue`, dimension ARY | mapped | not zero-filled; revt < 10 ($10m) -> Investment NaN |
- No IBES/options/13F/patents/segments/ratings/pensions/xad/emp/ob/ppegt. No zero-fill of an optional term, no SIC, no price input. Status is `approx` for the window/timing deviations in section 10, not for a missing item.
- capex measured on the ARY dimension: null 0.8% pooled (ART 9.2%, 46% in 1998) and ART is a TTM sum that equals ARY only at fiscal year-end. Sign mix of non-null ARY capex: negative (real capex) 90.9%, exactly 0 5.7%, positive (sign-inverted) 3.4%.

## 2. Variables (exact source names)
`gvkey, permno, time_avail_m, capx, revt` from `m_aCompustat`; derived `Investment` (ratio, then reused as the output), `tempMean`.

## 3. Formula in words and key lines
Annual capex / revenue, divided by the firm's mean of that ratio over a trailing 36-month window of the MONTHLY-REPLICATED annual panel (min 24 non-missing months); dropped when current revenue < $10m.
```
df["Investment"] = df["capx"] / df["revt"]
df = asrol(df, "permno", "time_avail_m", "1mo", 36, "Investment", "mean", "tempMean", min_samples=24)   # window INCLUDES the current month
df["Investment"] = df["Investment"] / df["tempMean"]
df.loc[df["revt"] < 10, "Investment"] = np.nan
```
As coded, the DENOMINATOR CONTAINS THE CURRENT YEAR'S OWN RATIO: a translator must not "correct" it to the prior three years. No winsorising, no positivity guard (OSAP divides by any tempMean, negative or zero).
What the window is: each annual record is replicated over 12 months, so a 36-month window ending in month t holds four vintages with month weights (n_cur, 12, 12, 12 - n_cur)/36 where n_cur = 1..12 is how long the newest record has been available.
Because every vintage has 12 months, `min_samples = 24` effectively needs THREE annual ratios (n_cur + 12 < 24 for two vintages unless n_cur = 12); two ratios suffice only in the last month of a vintage. The faithful minimum is therefore three fiscal years (current, -1, -2).

## 4. Timing / lag convention
OSAP: datadate + 6 months availability, held 12 months; asrol counts calendar months after `fill_date_gaps`. Here: ARY filing known at datekey (ARY datekey-reportperiod lag p1/50/99 = 37/76/304 days), 2-4 months fresher than OSAP's 6-month lag.
Both capex and revenue are FLOW items: under ART (TTM, refreshed quarterly) the year-over-year ratio would overlap and smear, and ART capex is 46% null in 1998; hence `FactorDef.dimension = "ARY"` (fiscal-year values, one refresh per year), aligned by reportperiod via `fundamentals_yoy(years=1)` and `(years=2)` as in ChInvIA.
ART-as-of-filing would change the signal into a quarterly-moving TTM ratio over 3 overlapping TTM values: not OSAP's object.

## 5. Filters
OSAP predictor: revt < 10 ($ millions) -> NaN. SignalDoc Filter blank ("Exclude if revenue less than $10m" is in the definition). Annual-data gate: at, prcc_c, ni non-null; curcd USD (not reproduced; fxusd != 1 on <= 0.06% of names). Threshold here: ARY revenue < 1e7 USD raw.

## 6. Predicted sign
SignalDoc `Sign = -1.0` (high investment relative to own history -> low return); Return 0.168 per month; T-Stat 2.86; Stock Weight VW; LS Quantile 0.2. Orientation: `ascending=False` (long LOW).

## 7. The mass-point question
Do-nothing firm: capex exactly 0 this year with positive history -> Investment exactly 0 (-0.0 after the sign flip); capex 0 in all window years -> 0/0 = NaN (the standing tie rule: level 0 at both ends -> NaN, here natural). Constant capex/revenue ratio across years -> exactly 1.0.
A second exact value: capex only in the current year and zero in both prior years gives cur/(cur/3) = 3.0 exactly.
Measured on the harness universe at all 276 signal months (1998-12-31 .. 2021-11-30), three-ratio form, revenue >= $10m:
- Modal share of the scored cross-section: max 0.49%, mean 0.20%; distinct values 552 (early) to ~1,800; `qcut(10)` has no collapse.
- Exact-zero Investment (capex fell to 0): mean 0.17%, max 0.49% of scored names. Sharadar positive capex (capx < 0 after flip): mean 1.94% (max 2.85%) of names with a value; tempMean <= 0: mean 3.9% of computable (nulled here; OSAP would keep the sign-flipped ratio).
- Revenue < $10m: 1.85% of the universe (mean), nulled.
Tie handling: none beyond nulls; harness average-rank default.

## 8. History needed (snapshot starts 1998-01): THE EARLY-WINDOW COVERAGE IS THIN
SF1 starts 1997Q4, so three consecutive ARY fiscal years exist only from about 2000. Measured coverage (share of the universe with a value, three-ratio form): 1998-12 24.2%, 1999-01 23.8%, 1999-06 38.2%, 1999-12 36.1%, 2000-01 36.0%, 2000-03 first month >= 40%, 2000-06 65.0%, 2000-12 71.6%, 2001-03 first >= 75%.
Months below 40%: 15 of 276 (1998-12 .. 2000-02); mean 82.6%, max 90.8%; 2001-2021 mean 86.2%, min 71.3%. With a two-ratio minimum (wider than OSAP's window rule, not recommended as the default) coverage is mean 88.8% and never below 40% (1998-12 43.8%, 1999-06 77.2%).
Scored names: 552 in 1998-12 (min) up to 1,815. `lookback_months` about 43 (24m of fiscal years + 15m filing age + ~4m report lag). No SEP price window: no `history_months`.

## 9. OSAP metadata
Investment (Acronym2 InvToRev); Titman, Wei and Xie 2004 JFQA; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form continuous; Cat.Data Accounting; Cat.Economic investment;
Sample 1973-1996; Key Table "1B Average"; Test "port sort, characteristic adjusted"; Sign -1.0; Return 0.168; T-Stat 2.86; VW; LS Quantile 0.2; Portfolio Period 12.0; Start Month 6.0; Filter blank; GScholar cites 2415.
Notes: "OP mean return is only 17 bps per month characteristic adjusted. We deviate somewhat from OP in the port sort by going LS 5-1 instead of (4+5) - (1+2) because OP value weights within each quintile which we can't do easily in our code."

## 10. Proposed Sharadar mappings with deviations
```
y1 = ctx.fundamentals_yoy(["capex","revenue"], years=1, dimension="ARY");  y2 = ctx.fundamentals_yoy([...], years=2, dimension="ARY")
x_k = (-capex_k) / revenue_k.where(revenue_k > 0)          for k = current, -1, -2
tempMean = mean(x_k) over the three ratios, required n == 3, tempMean > 0 else NaN
InvestmentTWX = x_cur / tempMean ; NaN where revenue_cur < 1e7 ;  ascending=False ; dimension="ARY"
```
Deviations: (a) equal-weight mean of three fiscal-year ratios, not OSAP's (n_cur, 12, 12, 12 - n_cur)/36 four-vintage monthly weights (the fourth vintage and the partial weights are not reproduced); (b) fiscal-year alignment by reportperiod, filing-date timing rather than datadate + 6 months;
(c) revenue > 0 guard on each ratio and tempMean > 0 guard (OSAP has neither; positive Sharadar capex is sign-inverted, 3.4% of ARY rows); (d) no curcd = USD gate (capex/revenue is currency-free; the $10m threshold is on raw reporting currency); (e) early coverage below 40% for the first 15 months (SF1 history, not a construction choice).
Fields not in the map: none (`compustat.capx`, `compustat.revt` both present). `-capex` sign flip is the load-bearing line.
