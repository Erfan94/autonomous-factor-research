# ShareVol — spec (fetched fresh; pinned OSAP ref b4e911e6; measured on DATA_SHA 198b281de1a0, 2026-09-30)

## 1. Data availability and verdict
VERDICT: **preflight_failed** (binary {0,1} signal, middle range missing: 2 distinct values, modal share 71-99.6% under
the plain-percent reading and 99.85-100% under the CRSP-units reading, qcut 1 bin; plus the OSAP drop rule is
unreproducible on Sharadar). No input is unavailable; mapping alone would be **approx**.
- Inputs: vol (CRSP monthly) -> SEP.volume (mapped, split-restated to today's basis, shares); shrout -> SF1.sharesbas ARQ
  (approx, split-restated, company-level, filing cadence; or DAILY.marketcap*1e6/SEP.close, same basis).
  Volume and shares are BOTH restated to the same basis, so volume/shares is split-neutral.
- OSAP zero-fills: none, but a missing tempShareVol is treated as HIGH (+inf) and scored 1 (see section 3); not a fill of an optional term.

The verdict is on OSAP's PUBLISHED construction (Cat.Form discrete; the {0,1} thresholds 5% / 10%). A continuous-turnover
reading (what OP regresses on) would be a different construction, not a translation of this predictor.

## 2. Variables
SignalMasterTable: permno, time_avail_m, sicCRSP, exchcd (the last two selected but unused by the formula).
monthlyCRSP: shrout, vol.

## 3. Formula
tempShareVol = (vol[t] + vol[t-1] + vol[t-2]) / (3 * shrout[t]) * 100   (3-month average monthly share volume / shares, %).
Drop observations with a shrout change in month t, t-1 or t-2 (dshrout = shrout != shrout[t-1], summed over 3 lags > 0;
the first two rows of a permno are not dropped).
ShareVol = 0 if tempShareVol < 5, = 1 if tempShareVol > 10, missing for 5 <= tempShareVol <= 10.
stata_ineq_pl (read at the pinned ref, utils/stata_replication.py) fills nulls with +inf for inequalities, so a NULL
tempShareVol (missing vol or shrout, or a first-row lag) satisfies `> 10` and becomes ShareVol = 1, as the code comment says.
A translation that leaves missing inputs as NaN differs only on the ~1-4% of names with a missing share count or volume month.
SignalDoc: "tempvol = sum of monthly share volume over the previous three months, scaled by 3 x shrout. ShareVol = 1 if
tempvol > 10%, 0 if tempvol < 5%." OP runs a linear regression; OSAP approximates with this long/short on the value
"rather than ranking" because the variable is extremely right skewed (mean ~5, sd 18, median 2 per SignalDoc note).

## 4. Timing
Monthly; uses months t, t-1, t-2 inclusive (harness signal date is the month-end, so month t is complete). Sharadar volume
is a daily flow summed over the calendar months (need all 3 months present; measured cov_T 0.96-1.00 of the universe).
UNIT AMBIGUITY: CRSP vol is in hundreds of shares and shrout in thousands, so OSAP's literal expression is 10 x the true
percent turnover (vol_hundreds/shrout_thousands*100 = 10 x V/S*100). Measured on the harness universe (true percent T = 3-month avg V / S x 100, sharesbas ARQ at t):
median T 17.6% (9.8-31.6), mean 24.4%. Reading A (thresholds on T): T<5 = 3.6% of scored names (0.4-20.6%), T>10 = 80.7%
(49.0-97.4%); 1-share among the binary names mean 95.3% (70.7-99.6%). Reading B (10 x T): <5 0.02%, >10 99.95%, 1-share 99.98%.
SignalDoc's mean 5 / median 2 does not match B in a consolidated-volume era; A is closer, but neither is verified.

## 5. Filters
SignalDoc Filter: **exchcd==1** (NYSE only, applied at the portfolio stage, not in the predictor script). The harness has
TICKERS.exchange as CURRENT exchange only (`crsp.exchcd`: approx, not point-in-time). Not reproducible point-in-time.
Portfolio Period 12, Start Month 6, Stock Weight EW, LS Quantile blank (binary groups).

## 6. Predicted sign
SignalDoc Sign = -1 (high share volume = low return): ascending=False. Datar, Naik, Radcliffe 1998, JFM, Table 2A Turnover;
t = 8.86 in a univariate regression; Predictability 1_clear; Rep Quality 1_good; Cat.Economic volume; sample 1962-1991.

## 7. Mass-point question
Do-nothing (no-volume) firm: tempShareVol ~ 0 -> 0. Nearly every firm lands in the 1 bucket or is missing. Measured over 276
months: ShareVol has 2 distinct values; modal share of the non-null cross-section = the 1-share; Reading A mean 95.3%
(1998-12 73.5%, 1999-12 83.7%, 2003-12 92.3%, 2008-12 99.4%, 2021-11 97.2%); qcut bins 1 every month (2 bins at best, none
reach 10); binary coverage A 0.84 of universe (0.66-0.98); Reading B qcut 0-1 bins, 1-share 99.85-100%. Tie handling in OSAP
is a two-group long/short, not deciles: a hard preflight fail under the 10% / 10-bin rule whichever unit is chosen.
The 3-month no-shares-change drop rule: with SF1 ARQ sharesbas stepping at each filing, only 9.9% (2.6-70.6%) of names
have t..t-3 readings all equal; applying it leaves ~8% of the universe (bin_cov_keep A mean 0.08, max 0.50). CRSP shrout
moves less often (corporate events), so the rule is a filter of modest size in OSAP and a near-total one here: a further
deviation, not a construction.

## 8. History
Needs 3 months of volume and sharesbas at t..t-3: available from the first decision month (1999-01, SEP from 1997-12).
Not binding. No 120-month issue (276 months), but the signal is unusable for deciles at any month.

## 9. OSAP metadata
Acronym ShareVol (Acronym2 VolumeShare); Predictor; Cat.Form discrete; Cat.Data Trading; Cat.Economic volume; 1_clear /
1_good; Datar, Naik and Radcliffe 1998, JFM; Sample 1962-1991; T-Stat 8.86; Stock Weight EW; Start Month 6; Filter exchcd==1.
Uses polars and utils.stata_replication.stata_ineq_pl (not cached here).

## 10. Proposed Sharadar mappings (for the record only; verdict is preflight_failed)
| OSAP | Sharadar | deviation |
|---|---|---|
| vol (hundreds of shares, CRSP) | SEP.volume summed over calendar months t, t-1, t-2 | unit and exchange-mix differences (NASDAQ double count pre-2004 in CRSP); split-restated |
| shrout (thousands) | SF1.sharesbas ARQ @ t | company-level, filing-date steps, split-restated; unit = shares |
| dropObs (shrout change in 3 months) | exact equality of ARQ sharesbas at t..t-3 | removes ~90% of names; not faithful |
| exchcd==1 filter | TICKERS.exchange (current) | not point-in-time |
Fields: crsp.vol mapped, crsp.shrout approx, crsp.exchcd approx, crsp.siccd approx; none outside the index.
