# EarningsStreak — earnings surprise streak (Loh and Warachka 2012, Management Science, Table 3B)

OSAP ref b4e911e69678a7424f318617a61d813f54183123; source `Predictors/EarningsStreak.py` (cached `predictor.py`, `signaldoc_row.csv`).
Written fresh from the source and `field_map_index.yaml`.

## 1. Data availability — VERDICT: data_unavailable (recommend `infeasible`)

The surprise is (actual - consensus forecast) / price, and the consensus is IBES. IBES / analyst data is not in Sharadar; OSAP does not zero-fill any of these.

| OSAP input | origin | Sharadar | OSAP missing-item rule |
|---|---|---|---|
| `meanest` at `fpi == "6"` (mean analyst EPS forecast, the quarterly horizon) | IBES_EPS_Adj | none | `dropna(["actual","meanest","price"])` -> row dropped |
| `actual` (IBES-reported actual EPS) | IBES_EPS_Adj | none (SF1 `eps` is a different, Compustat-style figure) | row dropped |
| `price` (IBES price at statpers) | IBES_EPS_Adj | SEP.close exists but the row never forms without IBES | row dropped |
| `anndats_act` (announcement date), `statpers` | IBES_EPS_Adj | none (EVENTS code 22 is an 8-K proxy, not the IBES actual date) | row dropped |
| `tickerIBES` link | SignalMasterTable | none | NaN |

Near-match NOT proposed: a streak of same-sign changes in SF1 `eps` versus year-ago (a time-series surprise rather than an analyst-forecast surprise) is a different signal with a different
information content (the paper's measure is actual minus analyst consensus). Substituting it would be a near-match; the rule is infeasible.
No measurement: the verdict turns on absence of the source.

## 2. Variables (exact source names)
`tickerIBES, anndats_act, time_avail_m, fpi, actual, meanest, price, statpers` (IBES_EPS_Adj); `permno, time_avail_m, tickerIBES` (SignalMasterTable).

## 3. Formula in words and key lines
For each IBES ticker, take the quarterly (fpi 6) forecast record with the latest `statpers` per announcement month, compute the price-scaled surprise, keep only announcements whose surprise SIGN repeats the
previous announcement's sign (a streak of at least two), carry the streak surprise forward up to 6 months, and use its magnitude as the signal.
```
df = df[fpi == "6"].dropna(subset=["actual","meanest","price"]); time_avail_m = month(anndats_act); keep last per (tickerIBES, time_avail_m)
surp = (actual - meanest) / price ; surp_sign = sign(surp) ; streak = (surp_sign == lag(surp_sign)) ; keep streak==1
df = signal_master.merge(temp_ibes) ; anndats_act ffill within permno ; month_diff <= 6 ; EarningsStreak = surp (ffill)
```
Note `np.sign` = 0 when surp == 0, so two consecutive exact-meet quarters count as a "streak" with signal 0 (a potential mass point in the source construction).

## 4. Timing / lag convention
Availability is the announcement month (no extra lag); the signal is forward-filled within each permno and dropped once the announcement is more than 6 months old. No Sharadar analogue.

## 5. Filters
In code: missing actual / meanest / price -> dropped; non-streak announcements -> dropped; announcement older than 6 months -> dropped. SignalDoc Filter `abs(prc)>5` is portfolio-stage, not in the code.

## 6. Predicted sign
SignalDoc `Sign = +1.0` (large positive surprise streak -> high returns); Return 0.957, T-Stat 9.51; Stock Weight EW; LS Quantile 0.2; Portfolio Period 1; Start Month 12; Cat.Form continuous.

## 7. The mass-point question
Not measurable. By construction streak rows with `surp == 0` (two consecutive "meet" quarters) have signal exactly 0; in IBES a meaningful share of actuals equal consensus to the cent, so the source
signal itself may carry a mass at 0 and is thin-coverage (only firms with analyst coverage AND a same-sign repeat). Moot here.

## 8. History needed (snapshot starts 1998-01)
IBES from 1987 (SampleStart); two consecutive announcements needed; moot.

## 9. OSAP metadata (SignalDoc)
Acronym EarningsStreak; Acronym2 EarnStreak; Loh and Warachka; 2012; MS; Cat.Signal Predictor; Predictability in OP 1_clear; Signal Rep Quality 1_good; Cat.Form continuous; Cat.Data Accounting (as recorded;
the code is IBES); Cat.Economic earnings growth; SampleStart 1987, End 2009; Key Table "3B Spread FF3 Streaks"; Test "port sort FF3 alpha"; Sign +1.0; Return 0.957; T-Stat 9.51; EW; LS Quantile 0.2;
Filter `abs(prc)>5`. Notes: announcements more than 6 months old are not used (Table 3 footnote); portfolios reassigned monthly; updated Feb 2021.
Definition: "Use fpi == 6 and only the last statpers for each anndats_act. Define surp = (actual - meanest)/price. Define a firm-anndats as a streak if surp has the same sign as the most recent surp observation. Keep only streaks. Then define signal = surp."

## 10. Proposed Sharadar mappings
None. Recommend `infeasible` (frontier reason: IBES actual/consensus/price/announcement date not in Sharadar; not zero-filled by OSAP). SignalDoc lists Cat.Data "Accounting" but `predictor.py` reads IBES only.
